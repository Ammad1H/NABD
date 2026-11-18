import asyncio
from playwright.async_api import async_playwright
OUT = "shots"
NAV = 64
async def top(pg, loc, pad=24):
    await loc.first.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
    await pg.evaluate("([el, nav, pad]) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - nav - pad)", [await loc.first.element_handle(), NAV, pad])
    await pg.wait_for_timeout(900)
async def center(pg, loc):
    await loc.first.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
    await pg.evaluate("(el) => { const r = el.getBoundingClientRect(); window.scrollTo(0, r.top + scrollY - (innerHeight - r.height) / 2 + 20); }", await loc.first.element_handle())
    await pg.wait_for_timeout(900)
async def shot(pg, name):
    await pg.screenshot(path=f"{OUT}/{name}.jpg", type="jpeg", quality=92)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1440, "height": 810}, device_scale_factor=4/3)
        pg = await ctx.new_page()
        await pg.goto("http://localhost:8600/", wait_until="networkidle")
        await pg.wait_for_timeout(2000)
        # let every section render once
        h = await pg.evaluate("document.body.scrollHeight")
        for y in range(0, h, 600):
            await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(60)
        await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(800)
        await shot(pg, "s01_hero")
        await top(pg, pg.locator("#problem .sec-head")); await shot(pg, "s02_problem")
        await top(pg, pg.locator("#how .sec-head")); await shot(pg, "s03_how")
        await center(pg, pg.get_by_text("Forecast error of the pooled model relative to each country", exact=False)); await shot(pg, "s04_forest")
        await center(pg, pg.get_by_text("The UAE's own seasons, pooled model (development check)")); await shot(pg, "s05_uae")
        await center(pg, pg.get_by_text("Cross-check: a general foundation model", exact=False)); await shot(pg, "s06_fm")
        await center(pg, pg.get_by_text("Proposed action", exact=True)); await shot(pg, "s07_card")
        await pg.fill("#ap-name", "Duty officer (demo)")
        await center(pg, pg.locator("#ap-name"))
        await pg.click("[data-act=decision]:has-text('Approve')"); await pg.wait_for_timeout(300)
        await pg.click("[data-act=record]"); await pg.wait_for_timeout(900)
        await center(pg, pg.get_by_text("Session log", exact=True)); await shot(pg, "s07_approved")
        await pg.click("[data-act=lang]"); await pg.wait_for_timeout(1200)
        await center(pg, pg.locator("#week .sec-head")); await shot(pg, "s07_arabic")
        await pg.click("[data-act=lang]"); await pg.wait_for_timeout(1200)
        await center(pg, pg.get_by_text("Mis-rostered weeks per season", exact=False)); await shot(pg, "s08_replay")
        await center(pg, pg.get_by_text("United States, against the CDC's combined forecast")); await shot(pg, "s08_us")
        await top(pg, pg.locator("#ledger .sec-head")); await shot(pg, "s09_ledger")
        await pg.click("[data-act=verify-all]"); await pg.wait_for_timeout(2500); await shot(pg, "s09_verified")
        await center(pg, pg.get_by_text("One hospital. Twelve weeks.", exact=False)); await shot(pg, "s10_pilot")
        await b.close()
asyncio.run(main())
