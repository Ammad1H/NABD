"""Build the draft technical documentation PDF for the organisers' early review.
Run: .venv/bin/python pitch/submission/draft-review/build_techdoc.py   (numbers are from results/, see docs/TECHNICAL.md)"""
from pathlib import Path
import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

OUT = Path(__file__).with_name("NABD-technical-documentation-draft.pdf")
fd = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("S", fd / "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("SB", fd / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("M", fd / "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("S", normal="S", bold="SB", italic="S", boldItalic="SB")
TEAL, INK, MUTE = colors.HexColor("#0f6b78"), colors.HexColor("#1b2428"), colors.HexColor("#5c6b70")
st = lambda n, **k: ParagraphStyle(n, fontName=k.pop("fontName", "S"), fontSize=k.pop("fontSize", 8.6), leading=k.pop("leading", 12), textColor=k.pop("textColor", INK), alignment=TA_LEFT, **k)
B, SM = st("b"), st("sm", fontSize=7.6, leading=10.5, textColor=MUTE)
H1, H2 = st("h1", fontName="SB", fontSize=19, leading=23, spaceAfter=2), st("h2", fontName="SB", fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=11, spaceAfter=4)
BL = st("bl", leftIndent=10, bulletIndent=0, spaceAfter=1.5)
P = lambda t, s=B: Paragraph(t, s)
def bl(items): return [Paragraph(i, BL, bulletText="•") for i in items]
def tbl(rows, widths, head=True):
    t = Table([[Paragraph(str(c), st("c", fontSize=7.8, leading=10.2, fontName="SB" if (head and r == 0) else "S")) for c in row] for r, row in enumerate(rows)], colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#d6dcde")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f4") if head else colors.white),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    return t

def diagram():
    W, Hh = 178 * mm, 62 * mm; d = Drawing(W, Hh)
    cols = [("Public data", ["WHO FluNet:", "UAE + 45 countries", "CDC FluSight hub", "UAE calendar"]),
            ("Adapters", ["schema checks", "reject person-", "level fields", "weekly totals only"]),
            ("Models", ["NABD-UAE-v1", "NABD-Pool", "v2, US ensemble", "baselines"]),
            ("Locked tests", ["plan locked first", "scored once", "held-out, Gulf,", "US, live UAE"]),
            ("Ledger", ["SHA-256 per file", "Merkle manifest", "sealed before WHO", "publishes the week"]),
            ("Decision layer", ["exceedance chances", "action per role", "named approver", "hash-chained log"])]
    bw, gap = 26.5 * mm, 3.8 * mm
    for i, (h, ls) in enumerate(cols):
        x = i * (bw + gap); y = 6 * mm
        d.add(Rect(x, y, bw, 50 * mm, strokeColor=TEAL, fillColor=colors.HexColor("#f3f8f8" if i % 2 == 0 else "#ffffff"), strokeWidth=.8))
        d.add(String(x + 2 * mm, y + 43 * mm, h, fontName="SB", fontSize=6.9, fillColor=TEAL))
        for j, l in enumerate(ls): d.add(String(x + 2 * mm, y + (35 - j * 6.2) * mm, l, fontName="S", fontSize=5.7, fillColor=INK))
        if i < len(cols) - 1:
            ax = x + bw; d.add(Line(ax, y + 25 * mm, ax + gap, y + 25 * mm, strokeColor=TEAL, strokeWidth=1)); d.add(Polygon([ax + gap, y + 25 * mm, ax + gap - 1.4 * mm, y + 26.2 * mm, ax + gap - 1.4 * mm, y + 23.8 * mm], fillColor=TEAL, strokeColor=TEAL))
    d.add(String(0, 0.5 * mm, "Interfaces: static bilingual web page (web/), Streamlit workbench (app/), FastAPI /forecast (app/api.py), weekly PDF bulletin.", fontName="S", fontSize=6.2, fillColor=MUTE))
    return d

S = []
S += [P("NABD: technical documentation (draft)", H1), P("Future Health Digital Innovation Challenge 2026 · Statement 06, Population and Workforce Health Early Warning · Entrant: Ammad Hassan (solo), MBZUAI · Draft of 15 Nov 2026", SM), Spacer(1, 4)]
S += [P("1. Purpose and status", H2), P("NABD forecasts RSV and influenza positivity for the UAE for the next three weeks as probabilistic ranges, converts each forecast into the chance of crossing pressure thresholds, and proposes one action per role. A named person approves, modifies or dismisses it. <b>Status: working prototype on public data.</b> No hospital has used it; no Abu Dhabi hospital data have been used. Every statement of result below carries its status: pre-registered, post hoc, retrospective or live.")]
S += [P("2. Architecture", H2), diagram(), Spacer(1, 3),
      P("<b>Interface contract.</b> Every forecast file uses the CDC FluSight hub quantile format (23 quantile levels), so any model, front-end or scorer can read any round. Front-ends read results and ledger files through one loader (<font name='M'>app/data_io.py</font>), so the web page and the workbench cannot disagree on a number. <b>Privacy by construction:</b> every adapter validates against a schema that rejects person-level fields; all data are weekly aggregates; the pilot spec adds k ≥ 10 cell suppression.")]
S += [P("3. Models", H2), tbl([["Model", "What it is", "Role"],
      ["NABD-UAE-v1", "Pooled linear growth model on the logit scale with a seasonal-climatology term; intervals from nested out-of-season residuals. Inputs: UAE sentinel positivity and testing volume.", "Frozen headline model of the live ledger"],
      ["NABD-Pool", "Borrowed strength. Average of (G) gradient-boosted quantile models trained on 46 development countries' WHO histories and (L) v1's linear form with coefficients fitted on pooled rows and shrunk toward the country's own fit by weight n/(n+8). Own lags, growth, season phase, latitude, volume, number of earlier seasons.", "Challenger on the ledger since round R2; runs on a laptop CPU in seconds"],
      ["NABD-UAE-v2", "v1 plus non-sentinel positivity, school breaks and Ramadan.", "Challenger; did not beat v1 (1.059), reported"],
      ["US ensemble", "Equal-weight quantile average of a damped log-linear negative-binomial GLM and an empirical error model, on NHSN admissions.", "Stress test against the CDC FluSight ensemble"],
      ["Baselines", "Repeat last week; past-season pattern. Chronos-2 (zero-shot, off the shelf) as an external benchmark only.", "Comparators; Chronos-2 is never an input to NABD"]], [26, 112, 40])]
S += [P("4. Evidence, with status", H2), tbl([["Test", "Result", "Status"],
      ["Borrowed strength: 18 held-out countries, influenza", "Pool vs each country's own-record model 0.767 (95% CI 0.681–0.832); better in 18/18; 0.624 where the record is short; vs repeat-last-week 0.879", "Pre-registered; primary met"],
      ["Gulf: Oman, Qatar, Saudi Arabia", "v1 vs last week 0.914 (0.843–0.983); vs past-season pattern 0.536", "Pre-registered; primary met"],
      ["US vs CDC FluSight ensemble", "1.22 (1.01–1.52) against a bar of 1.15; 7th of 21 and 19th of 25 single models", "Pre-registered; NOT met"],
      ["UAE own record, forward in time", "v1 vs last week 1.002 (tie) on four seasons", "Retrospective"],
      ["Chronos-2 zero-shot on the same forecasts", "vs Pool 1.026 (0.993–1.055); vs own-record model 0.787", "Post hoc"],
      ["Decision replay of a fixed roster rule", "Mis-rostered weeks a season: Pool 10.5, own-record 12.3, last week 11.1, past pattern 16.6; Pool vs last week not distinguishable", "Post hoc"],
      ["Prospective UAE test (live ledger)", "Pool vs own-record model, season 2026/27; locked before its first data point; 0 weeks scored so far", "Pre-registered; no result until after 15 Apr 2027"]], [46, 98, 34]),
      P("Retrospective tests use WHO's revised values; no real-time vintages of FluNet exist. Forecasts are of laboratory positivity, not hospital load.", SM)]
S += [P("5. Integrity mechanisms", H2)] + bl([
      "<b>Locks.</b> Each protocol is committed with a hash manifest before its data are opened; code refuses to score if a locked file has changed (<font name='M'>assert_locked</font>). Any later analysis is declared in <font name='M'>docs/DEVIATIONS.md</font> before it is run and labelled post hoc.",
      "<b>Ledger.</b> Each weekly round is hashed (SHA-256, Merkle manifest) before WHO publishes its target week, then scored once; tampered files are excluded. The web page recomputes the hashes in the browser.",
      "<b>Human in the loop.</b> A card consistency gate blocks cards whose band, trend and action disagree. Decisions are appended to a hash-chained log. Nothing is communicated without a named approver.",
      "<b>Tests.</b> 157 automated project tests (adapters, leakage and future-perturbation checks, locks, card gate, audit chain, ledger, web build) and a vendored scorer cross-checked against an independent implementation."])
S += [P("6. Assumptions and dependencies", H2)] + bl([
      "<b>A1.</b> WHO FluNet sentinel positivity indicates community activity; testing practice can change. <b>A2.</b> Publication lag is about 7–11 days and horizons are defined from the issue date. <b>A3.</b> First-release values may be revised; retrospectives use revised data, which flatters them versus live use. <b>A4.</b> Hospital load follows community positivity closely enough to matter: <i>untested</i>, and the pilot's question. <b>A5.</b> The playbook thresholds and wording are placeholders until a clinician and a public-health officer review them.",
      "<b>Data:</b> WHO FluNet (public-health, non-commercial terms), CDC FluSight hub, UAE school calendars. <b>Software:</b> Python 3.12, pandas, scikit-learn, statsmodels, Streamlit, FastAPI; CPU only. <b>Optional:</b> Chronos-2 benchmark needs torch and Hugging Face access. <b>Pilot:</b> one hospital's aggregate weekly paediatric respiratory counts under a data-sharing agreement (<font name='M'>docs/PILOT-DATA-SPEC.md</font>)."])
S += [P("7. Limitations", H2)] + bl([
      "The pooled model's evidence is from other countries. A confirmatory UAE result can only come forward in time; that test is locked and reports after 15 April 2027.",
      "In the US NABD missed its pre-registered bar against the CDC's combined forecast.",
      "NABD does not warn earlier that a surge is starting; it forecasts size and duration. In the roster replay it is not clearly better than repeating last week.",
      "The UAE's own four-season record shows no edge for a model trained on it alone. Seasonal peaks, not onsets, drive the value.",
      "Locks and ledger times are self-attested git commits until the repository is public and the fingerprints are stamped by an outside service. The employer-absence feed is simulated on synthetic data and watermarked as such."])
S += [P("8. Run it", H2), tbl([["Command", "What it does"],
      ["pip install -r requirements-dev.txt && pytest -q", "Installs and runs the test suite (157 tests)"],
      ["python -m web.build && python -m http.server 8600 --directory web/dist", "Builds and serves the presentation page at http://localhost:8600"],
      ["streamlit run app/streamlit_app.py", "Analyst workbench: audited approvals, hospital planner, every table"],
      ["python -m ledger.weekly --fetch --with-pool", "Pulls WHO data, scores past rounds, issues a round if new data exist"]], [92, 86])]
S += [P("9. Where architectural feedback would help most", H2)] + bl([
      "Is a positivity forecast the right interface for hospital operations, or should the pilot target admissions directly once a hospital's counts exist?",
      "How should a pooled model be governed in production: retraining cadence, drift checks, and when a challenger may replace the headline model?",
      "What would the integration path into existing Abu Dhabi systems look like for a read-only forecast feed with a human approval step?",
      "Is the evidence plan (locked live test, then a 12-week shadow pilot with a pre-set exit criterion) the right shape for a first deployment?"])
S += [Spacer(1, 6), P("Repository: https://github.com/Ammad1H/NABD · Full documentation: docs/TECHNICAL.md · Claims ledger: research/claims-ledger.md · Deviations log: docs/DEVIATIONS.md", SM)]
def foot(c, d):
    c.saveState(); c.setFont("S", 6.8); c.setFillColor(MUTE); c.drawString(16 * mm, 9 * mm, "NABD · technical documentation (draft for review) · Ammad Hassan"); c.drawRightString(194 * mm, 9 * mm, f"{d.page}"); c.restoreState()
SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=16 * mm, title="NABD technical documentation (draft)", author="Ammad Hassan").build(S, onFirstPage=foot, onLaterPages=foot)
print("wrote", OUT, OUT.stat().st_size // 1024, "kB")
