"""Take screenshots of every NABD app page (EN, plus AR for the weekly card).

Usage:  python app/take_screenshots.py   (needs `pip install playwright` and `playwright install chromium`)
Starts a headless Streamlit server on port 8599 and writes PNGs to app/screenshots/.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "screenshots"
PORT = 8599
SHOTS = [  # (file, language label, page label)
    ("01_weekly_card_en.png", "English", "Weekly card"),
    ("02_weekly_card_ar.png", "العربية", "البطاقة الأسبوعية"),
    ("03_alerts.png", "English", "Alerts"),
    ("04_us_proof.png", "English", "US proof"),
    ("05_gcc.png", "English", "GCC out-of-sample"),
    ("06_ledger.png", "English", "Ledger receipt"),
    ("07_feed_removal.png", "English", "Feed removal"),
    ("08_workforce_simulated.png", "English", "Workforce (simulated)"),
    ("09_about.png", "English", "About & limitations"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "streamlit_app.py"),
                             "--server.headless", "true", "--server.port", str(PORT),
                             "--browser.gatherUsageStats", "false"], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(6)
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1440, "height": 2400})
            for fname, lang_label, page_label in SHOTS:
                pg.goto(f"http://localhost:{PORT}", wait_until="networkidle")
                pg.wait_for_selector("section[data-testid='stSidebar']", timeout=60000)
                pg.get_by_text(lang_label, exact=True).first.click()
                time.sleep(2)
                pg.locator("section[data-testid='stSidebar']").get_by_text(page_label, exact=True).first.click()
                time.sleep(5)
                pg.wait_for_load_state("networkidle")
                pg.screenshot(path=str(OUT / fname), full_page=True)
                print("wrote", fname)
            b.close()
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
