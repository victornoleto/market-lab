"""
ctrader_oauth_bootstrap.py — one-time OAuth2 bootstrap for the cTrader Open API.

Run this on your LOCAL machine (needs a browser). The goal is to obtain the
first `refresh_token`, which the app will then use forever (rotating on each
refresh) on the VPS — no browser needed after this step.

Flow:
    1. Reads CTRADER_CLIENT_ID/SECRET/REDIRECT_URI/SCOPE from .env (or CLI).
    2. Starts http.server on the redirect host:port from REDIRECT_URI.
    3. Opens the browser at id.ctrader.com for user consent.
    4. Captures `authorization_code` from the redirect.
    5. POSTs to openapi.ctrader.com/apps/token to exchange code for tokens.
    6. Writes CTRADER_ACCESS_TOKEN and CTRADER_REFRESH_TOKEN back to .env.

Usage:
    python scripts/ctrader_oauth_bootstrap.py
    python scripts/ctrader_oauth_bootstrap.py --env-file .env.local

References:
    https://help.ctrader.com/open-api/account-authentication/
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

AUTH_URL = "https://id.ctrader.com/my/settings/openapi/grantingaccess/"
TOKEN_URL = "https://openapi.ctrader.com/apps/token"


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def update_env(path: Path, updates: dict[str, str]) -> None:
    """Replace or append keys in a .env file, preserving comments and order."""
    existing_lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    new_lines: list[str] = []
    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            new_lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            new_lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            new_lines.append(f"{key}={value}")
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


class _CallbackHandler(BaseHTTPRequestHandler):
    captured: dict[str, str] = {}

    def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler API)
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        _CallbackHandler.captured = params
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if "code" in params:
            body = "<h1>cTrader OAuth OK</h1><p>You can close this tab and return to the terminal.</p>"
        else:
            body = f"<h1>cTrader OAuth error</h1><pre>{json.dumps(params, indent=2)}</pre>"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *_args):  # noqa: N802 — silence default stderr logging
        return


def capture_code(redirect_uri: str) -> str:
    parsed = urllib.parse.urlparse(redirect_uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 80
    server = HTTPServer((host, port), _CallbackHandler)
    try:
        print(f"[bootstrap] listening on {host}:{port}{parsed.path or '/'} ...", flush=True)
        while "code" not in _CallbackHandler.captured and "error" not in _CallbackHandler.captured:
            server.handle_request()
    finally:
        server.server_close()
    if "error" in _CallbackHandler.captured:
        raise RuntimeError(f"OAuth error: {_CallbackHandler.captured}")
    return _CallbackHandler.captured["code"]


def exchange_code(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    data = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env", type=Path,
                        help="Path to .env file to read/update (default: .env)")
    parser.add_argument("--no-write", action="store_true",
                        help="Do not write tokens back to .env; just print them.")
    args = parser.parse_args()

    env_path: Path = args.env_file
    env = load_env(env_path)

    client_id = env.get("CTRADER_CLIENT_ID", "").strip()
    client_secret = env.get("CTRADER_CLIENT_SECRET", "").strip()
    redirect_uri = env.get("CTRADER_REDIRECT_URI", "http://localhost:8080/callback").strip()
    scope = env.get("CTRADER_SCOPE", "trading").strip()

    if not client_id or not client_secret:
        print(f"[error] CTRADER_CLIENT_ID / CTRADER_CLIENT_SECRET not set in {env_path}",
              file=sys.stderr)
        print("        Register the app at https://openapi.ctrader.com first.", file=sys.stderr)
        return 1

    auth_params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "product": "web",
    })
    auth_url = f"{AUTH_URL}?{auth_params}"

    print(f"[bootstrap] opening browser: {auth_url}", flush=True)
    webbrowser.open(auth_url)

    code = capture_code(redirect_uri)
    print("[bootstrap] authorization_code captured; exchanging for tokens ...", flush=True)

    tokens = exchange_code(code, client_id, client_secret, redirect_uri)

    access_token = tokens.get("accessToken") or tokens.get("access_token")
    refresh_token = tokens.get("refreshToken") or tokens.get("refresh_token")
    if not access_token or not refresh_token:
        print(f"[error] unexpected token response: {tokens}", file=sys.stderr)
        return 2

    print("\n=== Tokens received ===")
    print(f"access_token (preview): {access_token[:12]}...")
    print(f"refresh_token (preview): {refresh_token[:12]}...")
    print(f"expires_in: {tokens.get('expiresIn') or tokens.get('expires_in')}")
    print("=======================\n")

    if args.no_write:
        print("[bootstrap] --no-write set; not touching .env.")
        return 0

    update_env(env_path, {
        "CTRADER_ACCESS_TOKEN": access_token,
        "CTRADER_REFRESH_TOKEN": refresh_token,
    })
    print(f"[bootstrap] wrote tokens to {env_path}")
    print("[bootstrap] NEXT: fetch account IDs with ProtoOAGetAccountsByAccessTokenReq")
    print("           (will be automated in Phase 1 once the app client is built).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
