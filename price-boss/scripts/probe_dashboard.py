#!/usr/bin/env python3
"""Probe SmartGift Sales Dashboard endpoints (no credentials)."""
from __future__ import annotations

import re
import urllib.request

BASE = "https://smartgift-dashboard-pornpon.vercel.app"
PATHS = [
    "/api/health",
    "/api/auth/providers",
    "/api/auth/session",
    "/api/auth/csrf",
    "/api/sales",
    "/api/dashboard",
    "/api/reports",
    "/dash",
    "/login",
]


def fetch(path: str) -> tuple[int, str, dict]:
    req = urllib.request.Request(
        BASE + path,
        headers={"User-Agent": "price-boss-probe/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body, dict(e.headers)
    except Exception as e:  # noqa: BLE001
        return 0, str(e), {}


def main() -> None:
    for path in PATHS:
        code, body, headers = fetch(path)
        loc = headers.get("Location") or headers.get("location") or ""
        snippet = body.replace("\n", " ")[:120]
        print(f"{path:30} -> {code} loc={loc!r} body={snippet!r}")

    code, body, _ = fetch("/login")
    print("\n--- login assets ---")
    for m in re.findall(r"/_next/static/[^\"']+", body)[:25]:
        print(m)
    providers_code, providers_body, _ = fetch("/api/auth/providers")
    print(f"\nproviders ({providers_code}): {providers_body[:500]}")


if __name__ == "__main__":
    main()
