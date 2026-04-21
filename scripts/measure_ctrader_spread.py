"""Phase 4.0 T1.2 — Measure live bid/ask spread for target Index CFDs.

Subscribes to spot quotes via ProtoOASubscribeSpotsReq and captures
~60 seconds of bid/ask ticks per symbol. Computes median spread in
bps of mid-price, compares vs sensibility envelope threshold (15 bps half).

Usage:
  .venv/bin/python scripts/measure_ctrader_spread.py [--seconds 60]

Output:
  reports/phase4_0/index_cfd_validation/spread_measurements.json
  Appends spread row to
  docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md §5.1

Citation: [systematic_trading, p.185-188] — spread is 2nd dominant cost
after commission at retail CFD scale.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

OUT_PATH = Path("reports/phase4_0/index_cfd_validation/spread_measurements.json")

TARGET_SYMBOLS = ("US500", "NAS100", "XAUUSD")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (Path(__file__).resolve().parent.parent / ".env.local").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seconds", type=int, default=60,
                    help="Observation window in seconds (default 60)")
    args = ap.parse_args()

    from ctrader_open_api import Client, EndPoints, Protobuf, TcpProtocol  # type: ignore
    from ctrader_open_api.messages import OpenApiMessages_pb2 as msgs  # type: ignore
    from twisted.internet import reactor  # type: ignore

    env = load_env()
    client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
    account_id = int(env["CTRADER_ACCOUNT_ID"])

    # Known symbol ids from prior pull
    symbol_ids: dict[str, int] = {"US500": 10013, "NAS100": 10014, "XAUUSD": 41}
    id_to_name: dict[int, str] = {v: k for k, v in symbol_ids.items()}

    # Collected ticks: {symbol_name: [(timestamp, bid, ask), ...]}
    ticks: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    # Per-symbol last observed bid/ask (spot events report deltas)
    last_bid: dict[int, float | None] = {sid: None for sid in symbol_ids.values()}
    last_ask: dict[int, float | None] = {sid: None for sid in symbol_ids.values()}
    digits: dict[int, int] = {10013: 1, 10014: 1, 41: 2}

    start_time: float | None = None
    stop_scheduled = False

    def stop_later():
        nonlocal stop_scheduled
        if stop_scheduled:
            return
        stop_scheduled = True
        print(f"\nObserving for {args.seconds} seconds...")
        reactor.callLater(args.seconds, finalize)

    def on_app_auth(_):
        req = msgs.ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = account_id
        req.accessToken = env["CTRADER_ACCESS_TOKEN"]
        client.send(req).addCallback(on_account_auth)

    def on_account_auth(_):
        print(f"  ✅ Account {account_id} authenticated")
        sub = msgs.ProtoOASubscribeSpotsReq()
        sub.ctidTraderAccountId = account_id
        sub.symbolId.extend(list(symbol_ids.values()))
        client.send(sub).addCallback(on_subscribed)

    def on_subscribed(_):
        print(f"  ✅ Subscribed to {list(symbol_ids.keys())}")
        nonlocal start_time
        start_time = time.time()
        stop_later()

    def handle_message(_, message):
        # We get ProtoOASpotEvent messages asynchronously.
        try:
            payload_class_name = message.payloadType
        except Exception:
            return
        # ProtoOASpotEvent payloadType = 2131
        if payload_class_name != 2131:
            return
        event = msgs.ProtoOASpotEvent()
        event.ParseFromString(message.payload)
        sid = event.symbolId
        if sid not in id_to_name:
            return
        d = digits.get(sid, 2)
        scale = 10 ** d
        # cTrader sends prices as ints; divide by 10^digits to get real
        if event.HasField("bid"):
            last_bid[sid] = event.bid / scale
        if event.HasField("ask"):
            last_ask[sid] = event.ask / scale
        # Record only when both bid and ask known and event carries either
        if last_bid[sid] is not None and last_ask[sid] is not None:
            if start_time is not None:
                ticks[id_to_name[sid]].append(
                    (time.time() - start_time, last_bid[sid], last_ask[sid])
                )

    def finalize():
        print("\n=== Spread observations ===")
        result: dict[str, Any] = {
            "window_seconds": args.seconds,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "market_hours_note": "Note: captured after NYSE close (21:00 UTC). "
                                 "Index CFDs continue quoting via futures basis.",
            "symbols": {},
        }
        for name, data in ticks.items():
            if not data:
                print(f"  {name}: NO TICKS RECEIVED")
                result["symbols"][name] = {"n_ticks": 0}
                continue
            mids = [(b + a) / 2.0 for (_t, b, a) in data]
            spreads_abs = [a - b for (_t, b, a) in data]
            spreads_bps = [((a - b) / ((a + b) / 2.0)) * 10000.0 for (_t, b, a) in data]
            print(f"  {name}:")
            print(f"    ticks: {len(data)}")
            print(f"    mid range: [{min(mids):.4f}, {max(mids):.4f}]")
            print(f"    spread abs (min/median/max): "
                  f"{min(spreads_abs):.4f} / {median(spreads_abs):.4f} / {max(spreads_abs):.4f}")
            print(f"    spread bps (min/median/max): "
                  f"{min(spreads_bps):.2f} / {median(spreads_bps):.2f} / {max(spreads_bps):.2f}")
            print(f"    spread half bps (median / 2): "
                  f"{median(spreads_bps) / 2:.2f}")
            result["symbols"][name] = {
                "n_ticks": len(data),
                "mid_min": min(mids),
                "mid_max": max(mids),
                "spread_abs_min": min(spreads_abs),
                "spread_abs_median": median(spreads_abs),
                "spread_abs_max": max(spreads_abs),
                "spread_bps_min": min(spreads_bps),
                "spread_bps_median": median(spreads_bps),
                "spread_bps_max": max(spreads_bps),
                "spread_half_bps_median": median(spreads_bps) / 2,
            }

        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(result, indent=2, default=float))
        print(f"\nwrote {OUT_PATH}")

        # Gate check
        print("\n=== T1.2 Gate (spread_half ≤ 15 bps) ===")
        for name, data in result["symbols"].items():
            if "spread_half_bps_median" not in data:
                print(f"  {name}: NO DATA (skipped)")
                continue
            half = data["spread_half_bps_median"]
            ok = half <= 15.0
            print(f"  {name}: half={half:.2f} bps  {'✅' if ok else '❌'}")

        reactor.stop()

    def on_connected(_):
        req = msgs.ProtoOAApplicationAuthReq()
        req.clientId = env["CTRADER_CLIENT_ID"]
        req.clientSecret = env["CTRADER_CLIENT_SECRET"]
        client.send(req).addCallback(on_app_auth)

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(lambda c, r: None)
    client.setMessageReceivedCallback(handle_message)
    client.startService()
    reactor.run()


if __name__ == "__main__":
    main()
