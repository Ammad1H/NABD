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
    ("00_start_here_en.png", "English", "Start here"),
    ("00_start_here_ar.png", "العربية", "ابدأ من هنا"),
    ("00b_season_replay_en.png", "English", "Season replay"),
    ("00b_season_replay_ar.png", "العربية", "إعادة عرض موسم"),
    ("01_weekly_card_en.png", "English", "Weekly card"),
    ("02_weekly_card_ar.png", "العربية", "البطاقة الأسبوعية"),
    ("03_season_shape.png", "English", "Season shape"),
    ("04_bed_days_scenario.png", "English", "Bed-days scenario"),
    ("04b_winter_planner.png", "English", "Hospital winter planner"),
    ("05_gcc.png", "English", "GCC out-of-sample"),
    ("06_ledger.png", "English", "Ledger receipt"),
    ("07_us_proof.png", "English", "US proof"),
    ("08_alerts.png", "English", "Alerts"),
    ("09_feed_removal.png", "English", "Feed removal"),
    ("10_workforce_simulated.png", "English", "Workforce (simulated)"),
    ("11_about.png", "English", "About & limitations"),
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
    render_bulletin()
    return 0


def render_bulletin() -> None:
    """PNG of each bulletin page (needs poppler's pdftoppm) -> app/screenshots/12_bulletin_p<n>.png."""
    import shutil
    pdfs = sorted((ROOT / "bulletin" / "out").glob("NABD-bulletin-*.pdf"))
    if not pdfs or not shutil.which("pdftoppm"):
        print("bulletin render skipped (no PDF or no pdftoppm)")
        return
    subprocess.run(["pdftoppm", "-r", "110", "-png", str(pdfs[-1]), str(OUT / "12_bulletin_p")], check=True)
    for f in sorted(OUT.glob("12_bulletin_p-*.png")):
        f.rename(OUT / f.name.replace("12_bulletin_p-", "12_bulletin_p"))
    print("wrote bulletin page PNGs")


if __name__ == "__main__":
    sys.exit(main())
