#!/usr/bin/env python3
"""Capture homepage and audit release routes at desktop and mobile widths."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DEBUG_PORT = 9227


def wait_for(url: str, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: capture-release-qa.py <base-url> <label>", file=sys.stderr)
        return 2
    base_url = sys.argv[1].rstrip("/") + "/"
    label = sys.argv[2]
    out = ROOT / "qa" / f"release-{label}"
    evidence = ROOT / "evidence" / f"release-{label}.json"
    out.mkdir(parents=True, exist_ok=True)
    evidence.parent.mkdir(parents=True, exist_ok=True)

    profile = tempfile.TemporaryDirectory(prefix="pickle-release-chrome-")
    chrome = subprocess.Popen(
        [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={profile.name}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for(f"http://127.0.0.1:{DEBUG_PORT}/json/version")
        for route_name, route in (("home", ""), ("audit", "audit/")):
            url = urljoin(base_url, route)
            wait_for(url)
            for width, height in ((1440, 1000), (390, 844), (430, 932)):
                first = out / f"{route_name}-{width}-first.png"
                full = out / f"{route_name}-{width}-full.png"
                first_run = subprocess.run(
                    ["node", "qa-capture.mjs", url, str(width), str(height), str(first), str(DEBUG_PORT)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                full_run = subprocess.run(
                    ["node", "qa-fullpage.mjs", url, str(width), str(height), str(full), str(DEBUG_PORT)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                first_data = json.loads(first_run.stdout)
                full_data = json.loads(full_run.stdout)
                if first_data["scrollWidth"] != first_data["clientWidth"]:
                    raise RuntimeError(f"Horizontal overflow on {route_name} at {width}px")
                records.append({"route": route_name, "width": width, "first": first_data, "full": full_data})
        result = {"status": "PASS", "base_url": base_url, "label": label, "records": records}
        evidence.write_text(json.dumps(result, indent=2) + "\n")
        print(evidence.read_text(), end="")
        return 0
    finally:
        chrome.terminate()
        chrome.wait(timeout=10)
        profile.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
