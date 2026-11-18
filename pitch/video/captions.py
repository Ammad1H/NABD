"""Burn captions onto the captured frames. Segments: (frame, seconds, caption)."""
import json
from PIL import Image, ImageDraw, ImageFont
SEG = [
 ("s01_hero", 7.5, "Every winter, RSV and influenza reach Abu Dhabi's children's wards together."),
 ("s01_hero", 7.5, "One hospital, Tawam, admitted 2,189 young children with RSV in five years. Every Monday, someone decides how much to prepare."),
 ("s02_problem", 10, "They plan from last week and last year. But UAE seasons change shape: flu peaked in October one year, in February the year before."),
 ("s02_problem", 8, "And a model built only on the UAE's four seasons just ties repeating last week."),
 ("s03_how", 15, "So NABD learns from more seasons than one country has: one model learns how respiratory seasons rise, peak and fade across 46 countries' WHO data."),
 ("s04_forest", 11, "The plan was locked, then the model. Only then were 18 unseen countries opened."),
 ("s04_forest", 13, "23% less forecast error than each country's own-record model. Better in 18 of 18."),
 ("s05_uae", 11, "Back to the UAE: forecasting its last two seasons forward in time, with the UAE left out of training, the pooled model beat repeating last week in both."),
 ("s05_uae", 9, "That is a development check, not proof, so the real UAE test runs live."),
 ("s06_fm", 9, "An off-the-shelf foundation model lands level with ours on the same test. Learning across countries works, whichever model does it."),
 ("s07_card", 8, "Each week NABD turns that into one card: the chance of crossing each pressure threshold, and one proposed action."),
 ("s07_approved", 8, "A named person approves it, and the decision is logged. Nothing is sent without a human."),
 ("s07_arabic", 7, "In Arabic and in English."),
 ("s08_replay", 9, "NABD shows what it does not do. In a roster replay it beats the own-record model, but not simply repeating last week."),
 ("s08_us", 8, "Against the CDC's combined forecast in the US, it missed its own bar."),
 ("s09_ledger", 10, "So the UAE test runs forward. Every forecast is fingerprinted before WHO publishes the week it covers."),
 ("s09_verified", 10, "\"Verify all\" recomputes every fingerprint in your browser, and the test that will judge NABD is already locked."),
 ("s10_pilot", 12, "Give NABD one hospital's aggregate counts for twelve weeks, in shadow mode. If it does not beat the hospital's own census, the hospital walks away."),
 ("s11_end", 5, None),
]
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 40)
W, H = 1920, 1080
def wrap(d, text, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=FONT) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
meta = []
for k, (f, sec, cap) in enumerate(SEG):
    im = Image.open(f"shots/{f}.jpg").convert("RGB")
    assert im.size == (W, H), (f, im.size)
    if cap:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        lines = wrap(d, cap, 1560)
        assert len(lines) <= 3, (f, lines)
        lh, pad = 54, 30
        bh = len(lines) * lh + 2 * pad
        y0 = H - bh - 40
        d.rounded_rectangle([140, y0, W - 140, y0 + bh], 18, fill=(16, 40, 44, 228))
        for i, ln in enumerate(lines):
            tw = d.textlength(ln, font=FONT)
            d.text(((W - tw) / 2, y0 + pad + i * lh), ln, font=FONT, fill=(255, 255, 255, 255))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    out = f"frames/{k:02d}.jpg"
    im.save(out, quality=92)
    meta.append((out, sec))
json.dump(meta, open("frames/meta.json", "w"))
print("total seconds", sum(s for _, s in meta))
