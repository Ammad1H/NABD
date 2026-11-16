"""Fill the organisers' submission template with NABD's content.

  python pitch/submission/build_deck.py "<path to the official template .pptx>"

Writes pitch/submission/NABD-submission-deck.pptx. Numbers are read from results/ and ledger/, entrant facts
from pitch/submission/entrant.json. Needs python-pptx (not a project dependency: pip install python-pptx).
Export to PDF from PowerPoint (File > Export > PDF); the form accepts a PDF up to 5 MB.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "NABD-submission-deck.pptx"
E = json.loads((HERE / "entrant.json").read_text())

INK, TAUPE, MUTED = RGBColor(0x2E, 0x2A, 0x27), RGBColor(0x7B, 0x67, 0x5C), RGBColor(0x6B, 0x62, 0x5B)
SAND, LINE, WHITE = RGBColor(0xF3, 0xEE, 0xE6), RGBColor(0xD9, 0xD1, 0xC4), RGBColor(0xFF, 0xFF, 0xFF)
TEAL, ROSE, GREEN = RGBColor(0x0F, 0x6B, 0x78), RGBColor(0xB4, 0x50, 0x5B), RGBColor(0x2B, 0x7A, 0x57)
FONT = "Arial"
X0, W0 = 0.42, 9.16            # content column
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def j(p):
    return json.loads((ROOT / p).read_text())


POOL, FM, GCC, US = j("results/pool/summary.json"), j("results/fm/summary.json"), j("results/gcc/summary.json"), j("results/summary.json")
RP = j("results/replay/pool/summary.json")["results"]["country_q75|p30|h2"]
_T = RP["totals"]["NABD-Pool"]
SENS, PPV = (_T["surge_weeks"] - _T["missed"]) / _T["surge_weeks"], (_T["rostered"] - _T["wasted"]) / _T["rostered"]
P, SH = POOL["PRIMARY_flu_pool_vs_local_v1"], POOL["secondary"]["short_history_pool_vs_v1"]
PP = POOL["secondary"]["pool_vs_persistence"]
GP, GA = GCC["results"]["PRIMARY_flu_v1_vs_persistence"], GCC["results"]["flu_NABD-UAE-v1_vs_seasonal-analog"]
FMP = FM["results"]["Chronos-2 (zero-shot)"]["vs_NABD-Pool"]
UP = US["primary"]
N_ROUNDS = len({json.loads(m.read_text())["round"] for m in (ROOT / "ledger").glob("*.meta.json")})


def r3(d):
    return f"{d['rel_wis']:.3f} (95% CI {d['ci95'][0]:.3f}–{d['ci95'][1]:.3f})"


def pct(d):
    return f"{round((1 - d['rel_wis']) * 100)}%"


# ------------------------------------------------------------------ drawing helpers
def _run(par, text, size=10, bold=False, color=INK, italic=False):
    r = par.add_run()
    r.text = text
    f = r.font
    f.name, f.size, f.bold, f.italic = FONT, Pt(size), bold, italic
    f.color.rgb = color
    return r


def _bullet(par, indent_emu=150000):
    pPr = par._p.get_or_add_pPr()
    pPr.set("marL", str(indent_emu))
    pPr.set("indent", str(-indent_emu))
    bu = etree.SubElement(pPr, f"{{{A}}}buChar")
    bu.set("char", "•")


def text(slide, x, y, w, h, paras, size=10, anchor=MSO_ANCHOR.TOP, space=3):
    """paras: list of str | (str, opts) | [runs]; opts: bold, color, size, bullet, italic, align. A run is (text, opts)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, p in enumerate(paras):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.space_after = Pt(space)
        opts = {}
        if isinstance(p, tuple):
            p, opts = p
        runs = p if isinstance(p, list) else [(p, {})]
        if opts.get("bullet"):
            _bullet(par)
        if opts.get("align"):
            par.alignment = opts["align"]
        for rt, ro in runs:
            o = {**opts, **ro}
            _run(par, rt, o.get("size", size), o.get("bold", False), o.get("color", INK), o.get("italic", False))
    return tb


def _borders(cell, color="D9D1C4", w=6350):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("lnL", "lnR", "lnT", "lnB"):
        for old in tcPr.findall(qn(f"a:{tag}")):
            tcPr.remove(old)
        ln = etree.SubElement(tcPr, qn(f"a:{tag}"))
        ln.set("w", str(w))
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr")).set("val", color)
    # fills must come after the line elements in schema order
    for tag in ("solidFill", "noFill"):
        for el in tcPr.findall(qn(f"a:{tag}")):
            tcPr.remove(el)
            tcPr.append(el)


def table(slide, x, y, w, rows, widths, size=8.5, head_size=8.5, row_h=0.3):
    """rows[0] is the header. A cell is str or (str, opts)."""
    n, m = len(rows), len(rows[0])
    gf = slide.shapes.add_table(n, m, Inches(x), Inches(y), Inches(w), Inches(row_h * n))
    t = gf.table
    tot = sum(widths)
    for k, cw in enumerate(widths):
        t.columns[k].width = Inches(w * cw / tot)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for k, c in enumerate(row):
            opts = {}
            if isinstance(c, tuple):
                c, opts = c
            cell = t.cell(i, k)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.035)
            cell.vertical_anchor = MSO_ANCHOR.TOP if i else MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = TAUPE if i == 0 else (SAND if k == 0 else WHITE)
            tf = cell.text_frame
            tf.word_wrap = True
            par = tf.paragraphs[0]
            _run(par, c, head_size if i == 0 else opts.get("size", size), i == 0 or k == 0 or opts.get("bold", False),
                 WHITE if i == 0 else opts.get("color", INK))
            _borders(cell)
    return gf


def box(slide, x, y, w, h, title, body=None, fill=SAND, title_color=INK, size=8.5, title_size=9.5, line=LINE):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.color.rgb = line
    s.line.width = Pt(0.75)
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.06)
    par = tf.paragraphs[0]
    par.alignment = PP_ALIGN.LEFT
    par.space_after = Pt(2)
    _run(par, title, title_size, True, title_color)
    for b in body or []:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        p2.space_after = Pt(1.5)
        _run(p2, b, size, False, INK if fill != TAUPE else WHITE)
    return s


def arrow(slide, x, y, w=0.2, h=0.2):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = TAUPE
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def stat(slide, x, y, w, big, label, color=TEAL):
    text(slide, x, y, w, 0.5, [(big, {"size": 24, "bold": True, "color": color})])
    text(slide, x, y + 0.48, w, 0.7, [(label, {"size": 8.5, "color": MUTED})])


# ------------------------------------------------------------------ slides
def s1(s):
    tb = next(sh for sh in s.shapes if sh.has_text_frame and "Team Name" in sh.text_frame.text)
    vals = [E["team_name"], "1 (solo entrant)", "06 · Population and Workforce Health Early Warning"]
    for par, v in zip(tb.text_frame.paragraphs, vals):
        base = par.runs[-1]
        new = copy.deepcopy(base._r)
        par._p.append(new)
        par.runs[-1].text = v
        end = par._p.find(qn("a:endParaRPr"))
        if end is not None:                      # keep the paragraph-end marker last
            par._p.remove(end)
            par._p.append(end)


def s2(s):
    t = next(sh for sh in s.shapes if sh.has_table).table
    vals = ["1", E["name"], E["country"], "Sole entrant (all roles)", E["organization"], E["age_confirmation"]]
    for k, v in enumerate(vals):
        cell = t.cell(1, k)
        par = cell.text_frame.paragraphs[0]
        if par.runs:
            par.runs[0].text = v
        else:
            _run(par, v, 9)
    for tr in list(t._tbl.tr_lst)[2:]:           # one entrant: remove the four unused rows
        t._tbl.remove(tr)
    text(s, X0, 3.25, W0, 0.5, [("Team of one. There are no other members, advisers or contributors to declare.", {"color": MUTED, "size": 9})])


def s3(s):
    body = (f"NABD is a solo entry. {E['background']} During the challenge I designed, built and evaluated the whole system: "
            "data adapters for WHO FluNet and the CDC FluSight hub; four forecasting models; four evaluations whose plans were "
            "locked by hash before the test data were opened, plus a locked forward test; a hashed forecast ledger; a bilingual decision card with an audited "
            "approval log; two front-ends; 157 automated tests. The repository shows the skills this needs: probabilistic "
            "forecasting and scoring, pre-registration discipline, reproducible Python engineering, and Arabic/English interface "
            "work. Gaps, stated plainly: I am not a clinician, the playbook has not yet been reviewed by a clinician or a "
            "public-health officer, and I have no hospital data-sharing agreement. The pilot plan exists to close all three.")
    assert len(body) <= 1000, len(body)
    text(s, X0, 1.68, W0, 2.6, [(body, {"size": 11})], space=0)
    text(s, X0, 4.95, W0, 0.3, [(f"{len(body)} characters", {"size": 8, "color": MUTED})])


def s4(s):
    y, h, w, g = 1.42, 1.5, 1.34, 0.225
    steps = [("1  Data", ["WHO FluNet weekly lab surveillance: UAE, plus 46 countries' histories for the pooled model", "Aggregate counts only"]),
             ("2  Models", ["Own-record model (headline)", "Pooled model across countries (challenger)", "Repeat-last-week baseline"]),
             ("3  Forecast", ["RSV and influenza positivity", "1 to 4 weeks ahead", "23 quantiles: a range, not a line"]),
             ("4  Ledger", ["SHA-256 of every forecast file before WHO publishes the week", "Scored when WHO publishes"]),
             ("5  Card", ["Chance of crossing each pressure threshold", "One proposed action per role, Arabic and English"]),
             ("6  Decision", ["A named person approves, modifies or dismisses, with a reason", "Hash-chained audit log"])]
    for k, (ti, body) in enumerate(steps):
        x = X0 + k * (w + g)
        box(s, x, y, w, h, ti, body, fill=SAND if k < 5 else TAUPE, title_color=TEAL if k < 5 else WHITE, size=8.4, title_size=10,
            line=LINE if k < 5 else TAUPE)
        if k < 5:
            arrow(s, x + w + 0.02, y + h / 2 - 0.1, g - 0.04, 0.2)
    y2 = y + h + 0.22
    w3 = (W0 - 2 * 0.2) / 3
    box(s, X0, y2, w3, 1.45, "Evidence track (offline)",
        ["Plans and models locked by hash before test data are opened; deviations logged",
         "Held-out countries, Gulf, US benchmark, UAE forward test", "Every result reported, losses included"], fill=WHITE, title_color=TEAL, size=9)
    box(s, X0 + w3 + 0.2, y2, w3, 1.45, "Interfaces",
        ["Static web page (Arabic/English) built from the result files", "Analyst workbench (Streamlit): audited approvals, planner",
         "REST endpoint /forecast (FastAPI); weekly PDF bulletin"], fill=WHITE, title_color=TEAL, size=9)
    box(s, X0 + 2 * (w3 + 0.2), y2, w3, 1.45, "Guardrails",
        ["Card is blocked if band, direction and action disagree", "Person-level fields rejected by schema; small cells suppressed (k ≥ 10)",
         "Nothing is sent without a named approver"], fill=WHITE, title_color=TEAL, size=9)
    text(s, X0, 4.98, W0, 0.3, [("Weekly cycle: WHO publishes a week → forecast → hash → card → human decision → later scored against WHO's published value.",
                                 {"size": 8.5, "color": MUTED})])


def s5(s):
    rows = [["User", "Decision each week", "What NABD gives them", "Intended outcome"],
            ["Hospital bed and roster manager", "How much surge capacity to roster for the next two to three weeks",
             "The chance that RSV or influenza passes each pressure threshold, week by week, and one proposed roster action",
             "Fewer weeks staffed for a surge that does not come, and fewer weeks caught short"],
            ["ADPHC duty officer (public-health surveillance)", "Whether and when to advise facilities and the public",
             "A weekly Arabic/English card and bulletin, with the forecast shown beside 'repeat last week'",
             "Advisories matched to the size and length of the wave, with a record of who approved what"],
            ["Occupational-health officer (hospital or employer)", "How to plan for staff absence in the respiratory season",
             "A scenario of nurse shifts at risk, from the organisation's own absence rate (the feed is simulated today)",
             "Rosters that anticipate staff sickness as well as patient load"]]
    table(s, X0, 1.4, W0, rows, [1.5, 1.9, 2.9, 2.6], size=9, head_size=9, row_h=0.66)
    text(s, X0, 4.3, W0, 1.1, [
        [("Who benefits. ", {"bold": True}), ("Young children and their families: one Abu Dhabi hospital (Tawam) recorded 2,189 RSV admissions of "
                                            "children aged five or under in 2018–2022 (Alamiri et al., 2025).", {})],
        [("What it is not for. ", {"bold": True}), ("Individual diagnosis, patient-level prediction, or any decision about a named employee. "
                                                  "NABD forecasts how big and how long a wave will be; it does not claim to spot its start earlier than current surveillance.", {})]],
        size=9)


def s6(s):
    rows = [["What is measured", "Bar set in advance", "Where it stands"],
            ["Forecast error (WIS) of the pooled model vs each country's own-record model, 18 held-out countries",
             "Ratio below 1 with the 95% interval below 1 (plan locked before the data were opened)", (f"MET: {r3(P)}; better in {P['unit_wins']}", {"color": GREEN, "bold": True})],
            ["Forecast error vs 'repeat last week', Oman, Qatar, Saudi Arabia", "Ratio below 1 with the interval below 1 (locked)",
             (f"MET: {r3(GP)}", {"color": GREEN, "bold": True})],
            ["Forecast error vs the CDC FluSight ensemble, 53 US locations", f"Upper bound below {UP['margin']} (protocol frozen before scoring)",
             (f"NOT MET: {UP['rel_wis']:.2f} ({UP['ci95'][0]:.2f}–{UP['ci95'][1]:.2f}). Reported in full", {"color": ROSE, "bold": True})],
            ["UAE, forward in real time: pooled vs own-record model on the hashed ledger", "Ratio below 1 with the interval below 1; one assessment on or after 15 April 2027 (locked 14 Nov 2026)",
             "In progress: first round (R2) hashed on 14 Nov, 0 weeks scored yet. No UAE result is claimed"],
            ["Decision value: mis-rostered weeks per season under a fixed roster rule", "Fewer than the own-record model (post hoc replay)",
             f"{RP['NABD-Pool_minus_NABD-UAE-v1_mismatch']['mean_a']:.1f} vs {RP['NABD-Pool_minus_NABD-UAE-v1_mismatch']['mean_b']:.1f}; sensitivity {SENS:.0%}, predictive value {PPV:.0%}; not distinguishable from 'repeat last week' ({RP['NABD-Pool_minus_persistence_mismatch']['mean_b']:.1f})"],
            ["Hospital pilot (12 weeks, shadow mode)", "Error below 0.9 of the hospital's own census carried forward; 80% ranges cover 70–90% of weeks",
             "Not started: needs one hospital's aggregate weekly counts"],
            ["Process", "Every forecast hashed before WHO publishes its week; every action has a named approver and a reason",
             "Built and tested; outside timestamping still to do"]]
    table(s, X0, 1.38, W0, rows, [3.3, 3.3, 3.0], size=8.3, row_h=0.47)


def s7(s):
    s.shapes.add_picture(str(ROOT / "results" / "pool" / "fig_forest_pool_vs_local.png"), Inches(X0), Inches(1.6), height=Inches(3.12))
    x, w = 4.25, 5.35
    text(s, x, 1.6, w, 3.4, [
        ([("Held-out test, plan locked before download. ", {"bold": True}), (f"Pooled model vs own-record model, influenza, 18 countries: {r3(P)}, "
          f"better in {P['unit_wins']}. Where the record was short (≤ 2 seasons, the UAE's position): {SH['rel_wis']:.3f}. vs 'repeat last week': {PP['rel_wis']:.3f}.", {})], {"bullet": True}),
        ([("Gulf test, plan locked before download. ", {"bold": True}), (f"Own-record model vs 'repeat last week' in Oman, Qatar and Saudi Arabia: {r3(GP)}; "
          f"vs past-season patterns {GA['rel_wis']:.3f}.", {})], {"bullet": True}),
        ([("US benchmark, the result NABD lost. ", {"bold": True}), (f"vs the CDC FluSight ensemble {UP['rel_wis']:.2f} against a bar of {UP['margin']}: not met. "
          "7th of 21 single hub models in 2024/25, 19th of 25 in 2025/26.", {})], {"bullet": True}),
        ([("Foundation-model cross-check (post hoc). ", {"bold": True}), (f"Chronos-2 used off the shelf on the same forecasts is level with the pooled model: {r3(FMP)}. "
          "Both beat the own-record model, so the gain is not a quirk of one model.", {})], {"bullet": True}),
        ([("UAE's own four seasons. ", {"bold": True}), ("The own-record model only ties 'repeat last week' (1.00). That is why the pooled model exists, and why a forward UAE test is locked.", {})], {"bullet": True}),
    ], size=8.8, space=4)
    text(s, X0, 4.86, W0, 0.6, [(
        "Sources: WHO FluNet (GISRS); CDC FluSight Forecast Hub (github.com/cdcepi/FluSight-forecast-hub); Alamiri et al., J Infect Public Health 2025;18(12):103007 "
        "(Tawam RSV burden); Chronos (arXiv:2403.07815; amazon/chronos-2). Every number is reproducible from results/ in the repository; relative WIS below 1 = less error.",
        {"size": 7.5, "color": MUTED})])


def s8(s):
    rows = [["Source", "Type", "Owner", "Sensitivity", "Right to use", "Personal data"],
            ["WHO FluNet: the UAE and 81 other countries (46 development, 36 named test countries)", "Weekly aggregate laboratory surveillance counts", "WHO GISRS and national influenza centres",
             "Public, aggregate", "WHO terms: public-health, non-commercial use with attribution", "None"],
            ["CDC FluSight Forecast Hub", "US weekly state hospital-admission counts; ensemble and baseline forecasts", "US CDC and hub contributors",
             "Public, aggregate", "Hub MIT licence; US Government data", "None"],
            ["UAE academic calendar and public holidays", "Dates", "UAE Ministry of Education (public announcements)", "Public", "Public facts", "None"],
            ["Chronos-2 model weights (benchmark only, not an input)", "Pretrained model", "Amazon, via Hugging Face", "Public", "Apache-2.0", "None"],
            ["Synthetic employer-absence and pilot example files", "Simulated, labelled", "The entrant", "None (synthetic)", "Own work", "None"],
            ["Published burden figures (Tawam RSV study; Dubai claims study)", "Citations of published aggregates", "Journals and authors", "Public", "Citation", "None"]]
    table(s, X0, 1.62, W0, rows, [2.5, 2.0, 1.7, 1.0, 1.9, 0.8], size=8.2, head_size=8.2, row_h=0.42)
    text(s, X0, 4.72, W0, 0.6, [[("No personal or patient-level data is used anywhere. ", {"bold": True}),
                                ("The adapters reject person-level fields by schema. Pilot data would be weekly aggregates with small cells suppressed (k ≥ 10). "
                                 "WHO is not an endorser; WHO data are used for the public-health feed and evaluation only.", {})]], size=8.5)


def s9(s):
    rows = [["Risk", "Safeguard that is built", "What remains"],
            ["Privacy", "Aggregate counts only; schema rejects person-level fields; k ≥ 10 suppression designed for pilot data", "No person-level data is held, so exposure today is nil"],
            ["Security and integrity", "SHA-256 per forecast file and a Merkle manifest per round; hash-chained approval log; hashes can be recomputed in the browser",
             "Timestamping by an outside service is still to do"],
            ["Bias and fairness", "Population-level forecasts; tested in 21 countries across five WHO regions; testing volume shown beside positivity",
             "Positivity depends on who gets tested; the pilot reports children and adults separately"],
            ["Explainability", "The headline forecast decomposes exactly into its inputs; 'repeat last week' is always shown beside it", "The pooled challenger is less directly explainable"],
            ["Misuse and over-reliance", "The card is blocked when band, direction and action disagree; thresholds are labelled illustrative; no individual or employment use",
             "The playbook is not yet reviewed by a clinician"],
            ["Human oversight", "Every action needs a named approver and a reason; nothing is sent automatically", "None by design"],
            ["Failure modes", "Data-freshness badge and stale-data flag; labelled demo data, never silent fallback; losses published (US bar not met, UAE tie)",
             "No confirmatory UAE result until the locked forward test reports"]]
    table(s, X0, 1.62, W0, rows, [1.45, 5.0, 3.0], size=8.6, head_size=9, row_h=0.42)


def s10(s):
    text(s, X0, 1.75, W0, 1.6, [("Not applicable: NABD is software only.", {"bold": True, "size": 13}),
                               ("No wearable, sensor or connected device. It runs on an ordinary laptop CPU with no GPU: a weekly forecast round and the full "
                                "157-test suite each take under a minute. The web page is static files and can be hosted anywhere.", {"size": 10.5})], space=8)


def s11(s):
    text(s, X0, 1.85, W0, 2.4, [
        ("No login is required.", {"bold": True, "size": 13}),
        ([("Prototype: ", {"bold": True}), (E["prototype_url"], {"color": TEAL, "bold": True})], {"size": 11}),
        ([("Source code and evidence: ", {"bold": True}), (E["repo_url"], {"color": TEAL, "bold": True})], {"size": 11}),
        ("Every feature of the web page is open to any visitor: this week's card, the Arabic/English switch, the season replay, the ledger check and the "
         "approval demo (its log stays in the visitor's browser). The analyst workbench runs locally from the repository with one command and also has no login.", {"size": 10}),
    ], space=8)


def s12(s):
    y, h = 1.62, 1.12
    phases = [("Now · Nov 2026", ["Working prototype; ledger running weekly on WHO data", "Forward UAE test locked"]),
              ("Dec 2026 – Feb 2027", ["Data-sharing note with one hospital", "Clinician and ADPHC review of the playbook"]),
              ("12-week shadow pilot", ["Aggregate weekly paediatric respiratory counts", "No change to care; exit test set in advance"]),
              ("Apr 2027 decision", ["Pilot exit test and the locked UAE test both report", "Go or stop, on the record"]),
              ("Scale", ["More hospitals; a public-health feed for ADPHC", "Gulf: method already tested in Oman, Qatar, Saudi Arabia"])]
    w, g = 1.66, 0.215
    for k, (ti, body) in enumerate(phases):
        x = X0 + k * (w + g)
        box(s, x, y, w, h, ti, body, fill=SAND, title_color=TEAL, size=8.2, title_size=9.2)
        if k < 4:
            arrow(s, x + w + 0.015, y + h / 2 - 0.1, g - 0.03, 0.2)
    cw = (W0 - 0.3) / 2
    text(s, X0, 2.95, cw, 2.3, [
        ([("Stakeholders. ", {"bold": True}), ("Hospital operations (bed and roster managers), ADPHC surveillance, Department of Health, occupational-health teams.", {})], {"bullet": True}),
        ([("Integration. ", {"bold": True}), ("NABD is a forecast layer, not a new platform: a REST endpoint, a weekly bulletin and a static page that existing systems "
                                           "(Malaffi, Tableegh, Rasid) can host or link to.", {})], {"bullet": True}),
        ([("Regulatory. ", {"bold": True}), ("Aggregate, non-identifiable data only; DoH data-sharing approval and the hospital's research or quality-improvement sign-off before the pilot. "
                                          "NABD is planning support and makes no patient-level recommendation; any registration need would be confirmed with DoH.", {})], {"bullet": True}),
    ], size=8.6, space=4)
    text(s, X0 + cw + 0.3, 2.95, cw, 2.3, [
        ([("Timeline assumptions. ", {"bold": True}), ("WHO publishes each week 7–11 days after it ends; a data-sharing note takes four to eight weeks; the respiratory season runs to about March.", {})], {"bullet": True}),
        ([("Sustainability. ", {"bold": True}), ("Open code (MIT). A hypothesis, not a plan: a per-season forecast feed for public health and a per-facility seat running on the hospital's own data. "
                                              "WHO data stay in the non-commercial public-health feed.", {})], {"bullet": True}),
        ([("What would stop it. ", {"bold": True}), ("Missing the pilot exit test. In that case the record stays public and the hospital walks away at no cost.", {})], {"bullet": True}),
    ], size=8.6, space=4)


def s13(s):
    rows = [["Item", "Owner", "Licence or restriction"],
            ["NABD code, tests, documents and web page (written during the challenge window, from 5 Nov 2026)", "The entrant", "MIT. Per the challenge terms, IP stays with the entrant; the organiser has a 6-month right of first refusal on an exclusive licence"],
            ["Pre-existing IP", "None", "Nothing was brought in from before the challenge"],
            ["Open-source libraries: pandas, NumPy, SciPy, statsmodels, scikit-learn, pandera, Streamlit, FastAPI, Altair, ReportLab, Matplotlib", "Their authors", "BSD, MIT or Apache-2.0; used unmodified"],
            ["Chronos-2 weights and chronos-forecasting (benchmark only)", "Amazon", "Apache-2.0; not part of the product"],
            ["Fonts on the web page: IBM Plex, Newsreader, Noto Naskh Arabic", "IBM, Production Type, Google", "SIL Open Font Licence"],
            ["WHO FluNet and CDC FluSight data", "WHO; US CDC", "WHO: public-health, non-commercial use with attribution. A commercial hospital product would run on the hospital's own data"],
            [E["ai_row"][0], E["ai_row"][1], E["ai_row"][2]]]
    if not E["ai_row"][0]:
        rows = rows[:-1]
    table(s, X0, 1.62, W0, rows, [4.0, 1.6, 4.0], size=8.5, head_size=9, row_h=0.4)


def s14(s):
    text(s, X0, 1.75, W0, 3.4, [(p, o) for p, o in E["coi_paragraphs"]], size=10.5, space=8)


def s15(s):
    shot = HERE / "web-front-end.jpg"
    if shot.exists():
        pic = s.shapes.add_picture(str(shot), Inches(X0), Inches(0.95), width=Inches(4.75))
        pic.line.color.rgb = LINE
        pic.line.width = Pt(0.75)
    x = 5.42
    text(s, x, 0.92, 4.2, 0.35, [("The prototype, and what it showed", {"bold": True, "size": 13})])
    stat(s, x, 1.32, 1.3, pct(P), f"less influenza forecast error than a country's own-record model ({P['rel_wis']:.3f})")
    stat(s, x + 1.42, 1.32, 1.3, P["unit_wins"], "held-out countries better, none examined before the plan was locked")
    stat(s, x + 2.84, 1.32, 1.3, pct(SH), "less where the record is short, which is the UAE's position")
    text(s, x, 2.62, 4.2, 1.8, [
        ("Try it in two minutes", {"bold": True, "size": 10}),
        ("Open the prototype link: this week's RSV and influenza status for the UAE.", {"bullet": True}),
        ("Switch to العربية (top right): the whole page turns right-to-left.", {"bullet": True}),
        ("In 'The ledger', press Verify all: your browser recomputes each forecast file's SHA-256.", {"bullet": True}),
        ("In 'Decisions', press Play the season: watch a past season week by week.", {"bullet": True}),
        ("In 'This week's card', enter a name and record a decision.", {"bullet": True}),
    ], size=8.8, space=3)
    text(s, X0, 4.2, 4.75, 0.3, [("The web front-end: every number on it is generated from the repository's result files.", {"size": 8, "color": MUTED})])


FILL = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7, 8: s8, 9: s9, 10: s10, 11: s11, 12: s12, 13: s13, 14: s14, 15: s15}


def main(template: str):
    prs = Presentation(template)
    for i, slide in enumerate(prs.slides, 1):
        if i in FILL:
            FILL[i](slide)
    prs.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main(sys.argv[1])
