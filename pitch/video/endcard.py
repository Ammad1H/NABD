import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1440, "height": 810}, device_scale_factor=4/3)
        pg = await ctx.new_page()
        await pg.goto("file://" + str(Path("endcard.html").resolve()), wait_until="networkidle")
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path="shots/s11_end.jpg", type="jpeg", quality=92)
        await b.close()
asyncio.run(main())
