"""Search Pepperstone catalog (1889 symbols) for micro/mini variants
that would allow smaller notional sizing on $1k account.

Lists all symbols matching SPY/QQQ/Gold category with their minVolume
and lotSize so we can identify contracts trading < $1000 notional.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def load_env() -> dict[str, str]:
    env_file = Path(__file__).resolve().parent.parent / ".env.local"
    env: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def main() -> None:
    from ctrader_open_api import Client, EndPoints, Protobuf, TcpProtocol  # type: ignore
    from ctrader_open_api.messages import OpenApiMessages_pb2 as msgs  # type: ignore
    from twisted.internet import reactor  # type: ignore

    env = load_env()
    client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
    account_id = int(env["CTRADER_ACCOUNT_ID"])

    collected: list[dict] = []

    def on_app_auth(_):
        req = msgs.ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = account_id
        req.accessToken = env["CTRADER_ACCESS_TOKEN"]
        client.send(req).addCallback(on_account_auth)

    def on_account_auth(_):
        req = msgs.ProtoOASymbolsListReq()
        req.ctidTraderAccountId = account_id
        req.includeArchivedSymbols = False
        client.send(req).addCallback(on_list)

    def on_list(response):
        payload = Protobuf.extract(response)
        # Categories of interest: 3=Indices, 2=Metals, 32=(?)
        keywords = (
            "US500", "US.500", "SPX",
            "US100", "NAS", "NDX", "USTEC", "TECH100",
            "XAU", "GOLD", "GLD",
        )
        for s in payload.symbol:
            name = s.symbolName
            if any(k in name.upper() for k in keywords):
                collected.append({
                    "name": name,
                    "id": s.symbolId,
                    "categoryId": s.symbolCategoryId,
                    "description": s.description,
                    "enabled": s.enabled,
                })
        print(f"Found {len(collected)} matching symbols:")
        for c in sorted(collected, key=lambda x: x["name"]):
            print(f"  {c['name']:<20} id={c['id']:>6}  cat={c['categoryId']:>3}  "
                  f"en={c['enabled']}  {c['description']}")

        # Now fetch specs for each to see min volume
        ids = [c["id"] for c in collected]
        if ids:
            req = msgs.ProtoOASymbolByIdReq()
            req.ctidTraderAccountId = account_id
            req.symbolId.extend(ids)
            client.send(req).addCallback(on_details)
        else:
            reactor.stop()

    def on_details(response):
        payload = Protobuf.extract(response)
        details_by_id = {d.symbolId: d for d in payload.symbol}
        print("\n=== Detailed specs ===")
        print(f"{'name':<20} {'min_vol':>8} {'step':>6} {'lot_size':>10} "
              f"{'commission':>11} {'swap_L':>8} {'swap_S':>8}")
        for c in sorted(collected, key=lambda x: x["name"]):
            d = details_by_id.get(c["id"])
            if d is None:
                continue
            print(f"{c['name']:<20} {d.minVolume:>8} {d.stepVolume:>6} "
                  f"{d.lotSize:>10} {d.commission:>11} "
                  f"{d.swapLong:>8.2f} {d.swapShort:>8.2f}")
            c.update({
                "minVolume": d.minVolume,
                "stepVolume": d.stepVolume,
                "lotSize": d.lotSize,
                "commission": d.commission,
                "swapLong": d.swapLong,
                "swapShort": d.swapShort,
            })
        out = Path("reports/phase4_0/index_cfd_validation/pepperstone_catalog_variants.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(collected, indent=2, default=str))
        print(f"\nwrote {out}")
        reactor.stop()

    def on_connected(_):
        req = msgs.ProtoOAApplicationAuthReq()
        req.clientId = env["CTRADER_CLIENT_ID"]
        req.clientSecret = env["CTRADER_CLIENT_SECRET"]
        client.send(req).addCallback(on_app_auth)

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(lambda c, r: None)
    client.setMessageReceivedCallback(lambda c, m: None)
    client.startService()
    reactor.run()


if __name__ == "__main__":
    main()
