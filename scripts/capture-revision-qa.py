#!/usr/bin/env python3
"""Capture the revised homepage at the three acceptance-criteria widths."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "revision-2026-07-28"
EVIDENCE = ROOT / "evidence" / "TICKET-20260727-pickle-advisors-redesign-release-revision-qa.txt"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SERVER_PORT = 8765
DEBUG_PORT = 9224


def wait_for(url: str, timeout: float = 15) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for {url}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    chrome_profile = tempfile.TemporaryDirectory(prefix="pickle-revision-chrome-")
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(SERVER_PORT), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    chrome = subprocess.Popen(
        [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={chrome_profile.name}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    records: list[dict[str, object]] = []
    try:
        wait_for(f"http://127.0.0.1:{SERVER_PORT}/")
        wait_for(f"http://127.0.0.1:{DEBUG_PORT}/json/version")
        for width, height in ((1440, 1000), (390, 844), (430, 932)):
            first = OUT / f"revised-{width}-first.png"
            full = OUT / f"revised-{width}-full.png"
            url = f"http://127.0.0.1:{SERVER_PORT}/"
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
            records.append(
                {
                    "width": width,
                    "first_view": json.loads(first_run.stdout),
                    "full_page": json.loads(full_run.stdout),
                }
            )
        EVIDENCE.write_text(json.dumps({"status": "PASS", "captures": records}, indent=2) + "\n")
        print(EVIDENCE.read_text(), end="")
        return 0
    finally:
        chrome.terminate()
        server.terminate()
        chrome.wait(timeout=10)
        server.wait(timeout=10)
        chrome_profile.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
