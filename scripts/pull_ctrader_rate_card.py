"""Phase 4.0 T1 — Pull real Pepperstone cTrader rate card for Razor Index CFDs.

Connects to cTrader Open API (Protobuf over TLS) to fetch empirical
specs for US500, USTEC, XAUUSD on a Pepperstone demo account. Compares
observed values against the cost sensitivity matrix's viability envelope
(see ``reports/phase4_0/index_cfd_validation/cost_sensitivity.md``).

Flow
----
1. OAuth2 authorization code flow (interactive — user must complete in browser)
2. Exchange code → access_token + refresh_token
3. Fetch trading accounts via REST /connect/tradingaccounts
4. Connect to demo.ctraderapi.com:5035 (TLS+Protobuf)
5. App auth → Account auth → Symbols list → Symbol-by-id queries
6. Dump structured specs, compare against gates

Usage
-----

Two-phase run:

Phase A — OAuth bootstrap (first time, or token expired):
  .venv/bin/python scripts/pull_ctrader_rate_card.py --oauth

  Prints auth URL. Open in browser, authorize, copy code= value from the
  redirect URL, paste back into script stdin. Script saves access_token
  and refresh_token to .env.local.

Phase B — Actual rate card pull (after OAuth complete):
  .venv/bin/python scripts/pull_ctrader_rate_card.py

  Uses saved token, connects to trading API, prints rate card.

Output
------
  docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md (updated)
  reports/phase4_0/index_cfd_validation/ctrader_rate_card_raw.json

Citation
--------
cTrader Open API docs: https://help.ctrader.com/open-api/
[systematic_trading, Carver, p.185-188] — retail cost model scaling.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

ENV_LOCAL = Path(__file__).resolve().parent.parent / ".env.local"
OUT_RAW = Path("reports/phase4_0/index_cfd_validation/ctrader_rate_card_raw.json")
RATE_CARD_MD = Path("docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md")

SPOTWARE_AUTH_URL = "https://connect.spotware.com/apps/auth"
SPOTWARE_TOKEN_URL = "https://connect.spotware.com/apps/token"
SPOTWARE_ACCOUNTS_URL = "https://api.spotware.com/connect/tradingaccounts"

TARGET_SYMBOLS = ("US500", "USTEC", "XAUUSD")
# Fuzzy hints for Pepperstone naming variants (broker-specific)
NAS_HINTS = ("USTEC", "NAS100", "US.TECH", "USTECH", "TECH100", "NASDAQ")


# ---------------------------------------------------------------------------
# .env.local helpers (gitignored; persist OAuth tokens across runs)
# ---------------------------------------------------------------------------

def load_env() -> dict[str, str]:
    if not ENV_LOCAL.exists():
        return {}
    env: dict[str, str] = {}
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def save_env(env: dict[str, str]) -> None:
    """Persist env dict back to .env.local, preserving comment headers."""
    header = [
        "# Pepperstone cTrader Open API — credentials (gitignored)",
        "# Rotation: consider regenerating secret in app settings after Phase 4.0 T1",
        "",
    ]
    lines = header + [f"{k}={v}" for k, v in sorted(env.items())]
    ENV_LOCAL.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# OAuth2 authorization code flow
# ---------------------------------------------------------------------------

_code_arg: str | None = None  # set by main() from --code

def oauth_bootstrap(env: dict[str, str]) -> None:
    client_id = env["CTRADER_CLIENT_ID"]
    client_secret = env["CTRADER_CLIENT_SECRET"]
    redirect_uri = env.get("CTRADER_REDIRECT_URI")
    if not redirect_uri:
        print("ERROR: CTRADER_REDIRECT_URI not set in .env.local.", file=sys.stderr)
        print("Add the redirect URI registered in your Spotware app settings.", file=sys.stderr)
        sys.exit(1)

    scope = "trading"  # or 'accounts' for read-only; use 'trading' for specs+live
    auth_url = (
        f"{SPOTWARE_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"product=web"
    )
    print("=" * 72)
    print("STEP 1 — Open this URL in your browser:")
    print()
    print(f"  {auth_url}")
    print()
    print("STEP 2 — After authorizing, you will be redirected to:")
    print(f"  {redirect_uri}?code=XXXXXXXXX")
    print()
    print("STEP 3 — Copy the 'code=' value (without the 'code=' prefix).")
    print("=" * 72)
    if _code_arg:
        code = _code_arg.strip()
        print(f"\nUsing code from --code arg: {code[:10]}...")
    else:
        code = input("\nPaste auth code here: ").strip()
    if not code:
        print("ERROR: no code provided, aborting.", file=sys.stderr)
        sys.exit(1)

    print("\nExchanging code for access_token...")
    resp = requests.post(
        SPOTWARE_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    resp.raise_for_status()
    token_data = resp.json()
    if "accessToken" not in token_data and "access_token" not in token_data:
        print(f"ERROR: unexpected token response: {token_data}", file=sys.stderr)
        sys.exit(1)
    # Spotware uses camelCase; some OAuth libs rewrite it
    access_token = token_data.get("accessToken") or token_data.get("access_token")
    refresh_token = token_data.get("refreshToken") or token_data.get("refresh_token", "")
    expires_in = token_data.get("expiresIn") or token_data.get("expires_in", 0)

    print(f"  ✅ access_token received (expires in {expires_in}s)")
    if refresh_token:
        print(f"  ✅ refresh_token received")

    env["CTRADER_ACCESS_TOKEN"] = access_token
    if refresh_token:
        env["CTRADER_REFRESH_TOKEN"] = refresh_token
    save_env(env)
    print(f"\nTokens saved to {ENV_LOCAL}")

    print("\nSTEP 4 — Fetching trading accounts...")
    accounts_resp = requests.get(
        SPOTWARE_ACCOUNTS_URL,
        params={"access_token": access_token},
        timeout=30,
    )
    accounts_resp.raise_for_status()
    accounts = accounts_resp.json()
    print(f"\nFound {len(accounts)} trading account(s):")
    for acc in accounts:
        print(f"  - accountId={acc.get('accountId')}  "
              f"traderLogin={acc.get('traderLogin')}  "
              f"brokerName={acc.get('brokerName')}  "
              f"live={acc.get('live')}  "
              f"depositCurrency={acc.get('depositCurrency')}")

    if accounts:
        demo_accounts = [a for a in accounts if not a.get("live")]
        if demo_accounts:
            chosen = demo_accounts[0]
            acc_id = str(chosen.get("accountId"))
            env["CTRADER_ACCOUNT_ID"] = acc_id
            save_env(env)
            print(f"\n✅ Saved CTRADER_ACCOUNT_ID={acc_id} (demo, brokerName={chosen.get('brokerName')})")
        else:
            print("\n⚠️  No demo account found. All accounts appear to be LIVE.")
            print("   Specify CTRADER_ACCOUNT_ID manually in .env.local before running --pull.")
    print("\n✅ OAuth bootstrap complete. Run without --oauth to pull rate card.")


# ---------------------------------------------------------------------------
# Protobuf API pull (uses ctrader-open-api SDK)
# ---------------------------------------------------------------------------

def pull_rate_card(env: dict[str, str]) -> None:
    """Connect to demo.ctraderapi.com and pull specs for target symbols."""
    from ctrader_open_api import Client, EndPoints, Protobuf, TcpProtocol  # type: ignore
    from ctrader_open_api.messages import OpenApiMessages_pb2 as msgs  # type: ignore
    from twisted.internet import reactor  # type: ignore

    access_token = env.get("CTRADER_ACCESS_TOKEN")
    account_id = env.get("CTRADER_ACCOUNT_ID")
    client_id = env["CTRADER_CLIENT_ID"]
    client_secret = env["CTRADER_CLIENT_SECRET"]
    if not access_token or not account_id:
        print("ERROR: missing CTRADER_ACCESS_TOKEN or CTRADER_ACCOUNT_ID.", file=sys.stderr)
        print("Run with --oauth first to bootstrap.", file=sys.stderr)
        sys.exit(1)

    host = EndPoints.PROTOBUF_DEMO_HOST if env.get("CTRADER_ACCOUNT_TYPE", "demo") == "demo" else EndPoints.PROTOBUF_LIVE_HOST
    port = EndPoints.PROTOBUF_PORT

    print(f"Connecting to {host}:{port} ...")
    client = Client(host, port, TcpProtocol)

    collected: dict[str, Any] = {"symbols": {}}
    symbol_id_map: dict[int, str] = {}
    target_ids: list[int] = []

    def on_app_auth(response: Any) -> None:
        print("  ✅ App authenticated")
        req = msgs.ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = int(account_id)
        req.accessToken = access_token
        d = client.send(req)
        d.addCallback(on_account_auth)

    def on_account_auth(response: Any) -> None:
        print(f"  ✅ Account {account_id} authenticated")
        req = msgs.ProtoOASymbolsListReq()
        req.ctidTraderAccountId = int(account_id)
        req.includeArchivedSymbols = False
        d = client.send(req)
        d.addCallback(on_symbols_list)

    def on_symbols_list(response: Any) -> None:
        payload = Protobuf.extract(response)
        all_symbols = payload.symbol
        print(f"  ✅ Got {len(all_symbols)} symbols total")
        # Exact matches first
        for s in all_symbols:
            if s.symbolName in TARGET_SYMBOLS:
                symbol_id_map[s.symbolId] = s.symbolName
                target_ids.append(s.symbolId)
                collected["symbols"][s.symbolName] = {
                    "symbolId": s.symbolId,
                    "symbolName": s.symbolName,
                    "symbolCategoryId": s.symbolCategoryId,
                    "description": s.description,
                    "enabled": s.enabled,
                }
        # Fuzzy search for NAS/Tech 100 if USTEC not found
        if "USTEC" not in {symbol_id_map[i] for i in target_ids}:
            print("  ⚠️  USTEC not found by exact name. Fuzzy-searching NAS/Tech hints...")
            candidates = [
                s for s in all_symbols
                if any(h in s.symbolName.upper() for h in NAS_HINTS)
            ]
            print(f"     Candidates ({len(candidates)}): "
                  f"{sorted({c.symbolName for c in candidates})[:15]}")
            # Heuristic: prefer a symbol with "100" in it and "US"/"NAS"/"TECH" prefix
            best = None
            for c in candidates:
                name = c.symbolName.upper()
                if "100" in name and any(t in name for t in ("US", "NAS", "TECH")):
                    best = c
                    break
            if best is not None:
                print(f"     Selected: {best.symbolName} (id={best.symbolId})")
                symbol_id_map[best.symbolId] = best.symbolName
                target_ids.append(best.symbolId)
                collected["symbols"][best.symbolName] = {
                    "symbolId": best.symbolId,
                    "symbolName": best.symbolName,
                    "symbolCategoryId": best.symbolCategoryId,
                    "description": best.description,
                    "enabled": best.enabled,
                }
        print(f"  ✅ Matched {len(target_ids)} target symbols: "
              f"{[symbol_id_map[i] for i in target_ids]}")
        if not target_ids:
            print("  ⚠️  No target symbols found.")
            reactor.stop()
            return
        # Request detailed specs
        req = msgs.ProtoOASymbolByIdReq()
        req.ctidTraderAccountId = int(account_id)
        req.symbolId.extend(target_ids)
        d = client.send(req)
        d.addCallback(on_symbol_details)

    def on_symbol_details(response: Any) -> None:
        payload = Protobuf.extract(response)
        for detail in payload.symbol:
            name = symbol_id_map.get(detail.symbolId, f"sym_{detail.symbolId}")
            collected["symbols"][name].update({
                "digits": detail.digits,
                "pipPosition": detail.pipPosition,
                "enableShortSelling": detail.enableShortSelling,
                "minVolume": detail.minVolume,
                "maxVolume": detail.maxVolume,
                "stepVolume": detail.stepVolume,
                "lotSize": detail.lotSize,
                "commission": detail.commission,
                "commissionType": detail.commissionType,
                "slDistance": detail.slDistance,
                "tpDistance": detail.tpDistance,
                "gslDistance": detail.gslDistance,
                "gslCharge": detail.gslCharge,
                "distanceSetIn": detail.distanceSetIn,
                "minCommission": detail.minCommission,
                "minCommissionType": detail.minCommissionType,
                "minCommissionAsset": detail.minCommissionAsset,
                "rolloverCommission": detail.rolloverCommission,
                "skipRolloverDays": list(detail.skipRolloverDays) if hasattr(detail.skipRolloverDays, "__iter__") else int(detail.skipRolloverDays),
                "scheduleTimeZone": detail.scheduleTimeZone,
                "tradingMode": detail.tradingMode,
                "swapLong": detail.swapLong,
                "swapShort": detail.swapShort,
                "swapCalculationType": detail.swapCalculationType,
                "swapPeriod": detail.swapPeriod,
            })
            print(f"  ✅ {name}: lotSize={detail.lotSize}, minVol={detail.minVolume}, "
                  f"commission={detail.commission} ({detail.commissionType}), "
                  f"swapLong={detail.swapLong}, swapShort={detail.swapShort}")
        OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
        OUT_RAW.write_text(json.dumps(collected, indent=2, default=str))
        print(f"\n✅ Raw data saved to {OUT_RAW}")
        print(f"\nTODO next: compare values against sensitivity matrix envelope,")
        print(f"update {RATE_CARD_MD}, produce T1 verdict.")
        reactor.stop()

    def on_connected(_: Any) -> None:
        print("  ✅ TCP+TLS connected")
        req = msgs.ProtoOAApplicationAuthReq()
        req.clientId = client_id
        req.clientSecret = client_secret
        d = client.send(req)
        d.addCallback(on_app_auth)

    def on_error(failure: Any) -> None:
        print(f"  ❌ Error: {failure}", file=sys.stderr)
        reactor.stop()

    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(lambda c, r: print(f"  disconnected: {r}"))
    client.setMessageReceivedCallback(lambda c, m: None)
    client.startService()
    reactor.run()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--oauth", action="store_true",
                    help="Run OAuth2 bootstrap (prompts for auth code).")
    ap.add_argument("--code", type=str, default=None,
                    help="OAuth authorization code (skip stdin prompt).")
    ap.add_argument("--print-url-only", action="store_true",
                    help="Print OAuth URL and exit (no token exchange).")
    args = ap.parse_args()
    global _code_arg
    _code_arg = args.code

    if args.print_url_only:
        env = load_env()
        client_id = env["CTRADER_CLIENT_ID"]
        redirect_uri = env["CTRADER_REDIRECT_URI"]
        scope = "trading"
        url = (
            f"{SPOTWARE_AUTH_URL}?response_type=code&"
            f"client_id={client_id}&redirect_uri={redirect_uri}&"
            f"scope={scope}&product=web"
        )
        print(url)
        return

    env = load_env()
    if not env.get("CTRADER_CLIENT_ID") or not env.get("CTRADER_CLIENT_SECRET"):
        print("ERROR: .env.local missing CTRADER_CLIENT_ID/CTRADER_CLIENT_SECRET.", file=sys.stderr)
        sys.exit(1)

    if args.oauth:
        oauth_bootstrap(env)
    else:
        pull_rate_card(env)


if __name__ == "__main__":
    main()
