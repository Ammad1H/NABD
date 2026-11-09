"""NABD weekly bilingual bulletin: a 2-page PDF (page 1 English, page 2 Arabic) built from ONE ledger round.

    python -m bulletin.make_bulletin                 # latest ledger round -> bulletin/out/
    python -m bulletin.make_bulletin --round 2026-11-08T1212Z
    python -m bulletin.make_bulletin --round latest --out /tmp/x.pdf

This is NABD's own bulletin layout (modelled loosely on public weekly respiratory summaries). It is NOT an
ADPHC or DoH format and not an official product.

Determinism: the PDF depends only on (a) the ledger round files, (b) the WHO FluNet data truncated to the round's
own `data_through_week`, (c) the playbook, (d) any audit-log decisions that reference this round, and (e) ledger
scores for this round. The only date printed is the round's own `issued_utc`. ReportLab runs in invariant mode
(fixed creation date and document ID) and matplotlib PNGs carry no software/date metadata, so the same inputs give
the same bytes (tests/test_bulletin.py).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "nabd_v2_kit"
for _p in (ROOT, VENDOR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from reportlab import rl_config  # noqa: E402

rl_config.invariant = 1  # fixed creation date + document ID -> reproducible bytes
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT, TA_RIGHT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,  # noqa: E402
                                Table, TableStyle)

import arabic_reshaper  # noqa: E402
from bidi.algorithm import get_display  # noqa: E402

from app import audit, cardcheck, data_io  # noqa: E402
from playbook.validate import load_playbook  # noqa: E402

OUT_DIR = ROOT / "bulletin" / "out"
LEDGER = ROOT / "ledger"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
TEAL, SLATE, ROSE, SAND = "#1f7a8c", "#334155", "#b4505b", "#f3efe6"

_FONTS_OK = False


def _fonts() -> None:
    global _FONTS_OK
    if _FONTS_OK:
        return
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    _FONTS_OK = True


def ar(s: str) -> str:
    """Shape + reorder Arabic for a left-to-right PDF engine."""
    return get_display(arabic_reshaper.reshape(s))


# --------------------------------------------------------------------------------------------- text
TXT = {
    "title": {"en": "NABD weekly respiratory forecast bulletin: United Arab Emirates",
              "ar": "نشرة نبض الأسبوعية لتوقعات أمراض الجهاز التنفسي: الإمارات العربية المتحدة"},
    "sub": {"en": "RSV and influenza sentinel positivity (WHO FluNet). NABD's own layout; not an official DoH or ADPHC product.",
            "ar": "نسبة إيجابية الفيروس المخلوي التنفسي والإنفلونزا في مواقع الرصد (منظمة الصحة العالمية FluNet). تنسيق خاص بنبض، وليس منتجاً رسمياً لدائرة الصحة أو مركز أبوظبي للصحة العامة."},
    "issued": {"en": "Issued", "ar": "تاريخ الإصدار"},
    "through": {"en": "Data through", "ar": "البيانات حتى"},
    "lag": {"en": "Lag at issue", "ar": "التأخير عند الإصدار"},
    "days": {"en": "days", "ar": "أيام"},
    "round": {"en": "Ledger round", "ar": "جولة السجل"},
    "model": {"en": "Model", "ar": "النموذج"},
    "anchor": {"en": "Anchor status", "ar": "حالة التوثيق الخارجي"},
    "anchor_no": {"en": "hashed locally; not yet published or externally timestamped",
                  "ar": "مُجزّأ محلياً؛ لم يُنشر أو يُختم زمنياً من جهة خارجية بعد"},
    "anchor_yes": {"en": "published", "ar": "منشور"},
    "rsv": {"en": "RSV (sentinel positivity, %)", "ar": "الفيروس المخلوي التنفسي (نسبة الإيجابية في الرصد، %)"},
    "flu": {"en": "Influenza (sentinel positivity, %)", "ar": "الإنفلونزا (نسبة الإيجابية في الرصد، %)"},
    "last": {"en": "Last published week", "ar": "آخر أسبوع منشور"},
    "trend3": {"en": "3-week observed trend", "ar": "الاتجاه المرصود لثلاثة أسابيع"},
    "direction": {"en": "Forecast", "ar": "التوقع"},
    "path": {"en": "forecast path to +3 weeks", "ar": "مسار التوقع حتى 3 أسابيع"},
    "tier": {"en": "tier", "ar": "المستوى"},
    "rise": {"en": "rise", "ar": "ارتفاع"},
    "fall": {"en": "fall", "ar": "انخفاض"},
    "horizon": {"en": "Horizon", "ar": "الأفق"},
    "week_end": {"en": "Week ending", "ar": "نهاية الأسبوع"},
    "median": {"en": "Median", "ar": "الوسيط"},
    "range80": {"en": "80% range", "ar": "نطاق 80%"},
    "band": {"en": "Playbook band", "ar": "نطاق دليل العمل"},
    "proposed": {"en": "PROPOSED, NOT APPROVED", "ar": "مقترح، غير معتمد"},
    "decided": {"en": "Decision recorded", "ar": "قرار مسجّل"},
    "blocked": {"en": "Card blocked by the consistency check; no action proposed.",
                "ar": "حُجبت البطاقة بواسطة فحص الاتساق؛ لا إجراء مقترح."},
    "shape": {"en": "Season shape: this season (thick) vs the last four complete seasons",
              "ar": "شكل الموسم: الموسم الحالي (خط سميك) مقارنة بالمواسم الأربعة الكاملة السابقة"},
    "track": {"en": "Track record of this ledger", "ar": "سجل الأداء لهذا السجل"},
    "track_none": {"en": "No target week of any issued round has been published yet, so nothing is scored. Evidence so far comes from retrospective tests (technical documentation).",
                   "ar": "لم يُنشر بعد أي أسبوع مستهدف من الجولات الصادرة، لذا لا يوجد تقييم. الأدلة حتى الآن من اختبارات بأثر رجعي (الوثائق الفنية)."},
    "not_title": {"en": "What this bulletin is not", "ar": "ما ليست عليه هذه النشرة"},
    "not": {"en": ["Not a forecast of hospital admissions or bed occupancy: it forecasts national sentinel test positivity.",
                   "Not an early warning of season onset: in tests, onset alerts came no earlier than a threshold on the latest counts.",
                   "Not an official DoH, ADPHC or SEHA product, and not reviewed by them.",
                   "Never for decisions about individuals or employment. All data are aggregate."],
            "ar": ["ليست توقعاً لحالات دخول المستشفيات أو إشغال الأسرّة: إنها تتوقع نسبة إيجابية الفحوص في مواقع الرصد الوطنية.",
                   "ليست إنذاراً مبكراً ببدء الموسم: في الاختبارات لم تسبق التنبيهات عتبةً بسيطة على أحدث الأعداد.",
                   "ليست منتجاً رسمياً لدائرة الصحة أو مركز أبوظبي للصحة العامة أو صحة، ولم تُراجع من قبلهم.",
                   "لا تُستخدم أبداً في قرارات تخص أفراداً أو التوظيف. جميع البيانات مجمّعة."]},
    "playbook_note": {"en": "ILLUSTRATIVE playbook (version {v}): actions are proposals pending clinical and public-health review. Nothing is released without a named human approver.",
                      "ar": "دليل عمل توضيحي (الإصدار {v}): الإجراءات مقترحات بانتظار المراجعة السريرية ومراجعة الصحة العامة. لا يُنفَّذ أي إجراء دون معتمِد مسمّى."},
    "footer": {"en": "Source: WHO FluNet (public-health, non-commercial use, with citation). Forecasts are probabilistic; coverage is checked and reported in the technical documentation. SHA-256 of the forecast file: {sha}",
               "ar": "المصدر: منظمة الصحة العالمية FluNet (للاستخدام في الصحة العامة وغير التجاري مع الإشارة إلى المصدر). التوقعات احتمالية، ويُفحص مدى تغطيتها ويُنشر في الوثائق الفنية. بصمة SHA-256 لملف التوقع: {sha}"},
    "nowcast": {"en": "nowcast", "ar": "تقدير آني"},
    "wk": {"en": "wk", "ar": "أسبوع"},
}
TREND_WORD = {"rising": {"en": "rising", "ar": "صاعد"}, "plateau": {"en": "plateau", "ar": "مستقر"},
              "falling": {"en": "falling", "ar": "هابط"}, "flat": {"en": "flat", "ar": "ثابت"},
              "unknown": {"en": "unknown", "ar": "غير معروف"}}


def tx(key: str, lang: str, **kw) -> str:
    s = TXT[key][lang]
    if isinstance(s, str) and kw:
        s = s.format(**kw)
    return s


# --------------------------------------------------------------------------------------------- data
def round_stamps() -> list[str]:
    return sorted({data_io.ROUND_RE.match(f.name).group(1) for f in data_io.ledger_round_files()})


def load_round(stamp: str) -> dict:
    files = {data_io.ROUND_RE.match(f.name).group(2): f for f in data_io.ledger_round_files()
             if f.name.startswith(stamp + "_")}
    if not files:
        raise FileNotFoundError(f"no ledger round {stamp}")
    metas = {}
    for m, f in files.items():
        mp = f.with_name(f.name[:-4] + ".meta.json")
        metas[m] = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    head = next((m for m, me in metas.items() if str(me.get("designation", "")).startswith("headline")), None)
    if head is None:
        head = next((m for m in sorted(files) if m not in data_io.PERSISTENCE_NAMES), None)
    if head is None:
        raise ValueError(f"round {stamp} has no forecast model file")
    pers = next((m for m in data_io.PERSISTENCE_NAMES if m in files), None)
    return {"stamp": stamp, "model": head, "file": files[head], "meta": metas[head],
            "fc": data_io._normalise_quantiles(pd.read_csv(files[head])),
            "pers": data_io._normalise_quantiles(pd.read_csv(files[pers])) if pers else None,
            "sha256": metas[head].get("sha256") or __import__("hashlib").sha256(files[head].read_bytes()).hexdigest()}


def observed_as_of(meta: dict) -> pd.DataFrame:
    """WHO FluNet observed series truncated to the round's own data_through_week (later data never leaks in)."""
    o = data_io.load_uae_observed()
    weeks = list((meta.get("data_through_week") or {}).values())
    if weeks:
        y, w = str(min(weeks)).split("-W")
        o = o[(o.ISO_YEAR < int(y)) | ((o.ISO_YEAR == int(y)) & (o.ISO_WEEK <= int(w)))]
    return o.reset_index(drop=True)


def round_decisions(round_file: str, issue: dt.date) -> dict:
    """Latest audit decision per (target, role) that references this round (or its issue date and model)."""
    out = {}
    for r in audit.read_records():
        ref = r.get("forecast_ref") or {}
        if ref.get("round_file") == round_file or (not ref.get("round_file") and ref.get("reference_date") == issue.isoformat()):
            out[(ref.get("target"), r.get("role"))] = r
    return out


def round_scores(model: str, stamp: str) -> pd.DataFrame | None:
    p = LEDGER / "scores.csv"
    if not p.exists() or p.stat().st_size == 0:
        return None
    try:
        s = pd.read_csv(p)
    except (pd.errors.EmptyDataError, ValueError):
        return None
    return s if not s.empty else None


# --------------------------------------------------------------------------------------------- charts
def _png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    return buf.getvalue()


def fan_png(obs: pd.DataFrame, col: str, fc: pd.DataFrame, pers: pd.DataFrame | None, target: str,
            issue: dt.date, title: str) -> bytes:
    h = obs[["week_end", col]].dropna().tail(14)
    w = fc[fc.target == target].pivot_table(index="target_end_date", columns="q", values="value").sort_index()
    w.columns = [round(float(c), 3) for c in w.columns]
    x = pd.to_datetime(pd.Series(w.index))
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    ax.fill_between(x, w[0.025], w[0.975], color=TEAL, alpha=0.18, lw=0)
    ax.fill_between(x, w[0.1], w[0.9], color=TEAL, alpha=0.35, lw=0)
    ax.plot(x, w[0.5], color=TEAL, lw=2, marker="o", ms=3)
    ax.plot(pd.to_datetime(h.week_end), h[col], color=SLATE, lw=1.4, marker="o", ms=2.5)
    if pers is not None:
        pw = pers[pers.target == target].pivot_table(index="target_end_date", columns="q", values="value").sort_index()
        pw.columns = [round(float(c), 3) for c in pw.columns]
        ax.plot(pd.to_datetime(pd.Series(pw.index)), pw[0.5], color=SLATE, lw=1, ls="--")
    ax.axvline(pd.Timestamp(issue), color=ROSE, lw=0.8, ls=":")
    ax.set_title(title, fontsize=7.5, loc="left", color=SLATE)
    ax.tick_params(labelsize=6)
    ax.set_ylabel("%", fontsize=6.5)
    ax.grid(alpha=0.25, lw=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.autofmt_xdate(rotation=0, ha="center")
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=6, interval=4))
    return _png(fig)


def shape_png(obs: pd.DataFrame) -> bytes:
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 1.7), sharex=True)
    for ax, col, name in zip(axes, ("rsv", "flu"), ("RSV", "Influenza")):
        sf = data_io.season_frame(obs, col)
        cur = sf.season.max()
        prev = [s for s in sorted(sf.season.unique()) if s != cur][-4:]
        greys = ["#cbd5e1", "#94a3b8", "#64748b", "#475569"][-len(prev):] if prev else []
        for s, c in zip(prev, greys):
            g = sf[sf.season == s]
            ax.plot(g.x, g.value, color=c, lw=1, label=str(g.label.iloc[0]))
        g = sf[sf.season == cur]
        ax.plot(g.x, g.value, color=TEAL, lw=2.4, label="this season")
        ax.set_title(name, fontsize=7.5, loc="left", color=SLATE)
        ax.set_xlim(0, 52)
        ax.tick_params(labelsize=6)
        ax.grid(alpha=0.25, lw=0.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("weeks since ISO week 27", fontsize=6)
    axes[0].set_ylabel("%", fontsize=6.5)
    axes[1].legend(fontsize=5.5, frameon=False, loc="upper right", ncol=1)
    return _png(fig)


# --------------------------------------------------------------------------------------------- PDF
def _styles(lang: str) -> dict:
    _fonts()
    al = TA_RIGHT if lang == "ar" else TA_LEFT
    return {
        "title": ParagraphStyle("t", fontName="DejaVu-Bold", fontSize=12.5, leading=15, textColor=colors.HexColor(SLATE), alignment=al),
        "sub": ParagraphStyle("s", fontName="DejaVu", fontSize=7, leading=9, textColor=colors.HexColor("#64748b"), alignment=al),
        "h": ParagraphStyle("h", fontName="DejaVu-Bold", fontSize=9, leading=11, textColor=colors.HexColor(TEAL), alignment=al, spaceBefore=4),
        "b": ParagraphStyle("b", fontName="DejaVu", fontSize=7.3, leading=9.4, alignment=al),
        "small": ParagraphStyle("sm", fontName="DejaVu", fontSize=6.3, leading=8, textColor=colors.HexColor("#475569"), alignment=al),
        "cell": ParagraphStyle("c", fontName="DejaVu", fontSize=6.8, leading=8.2, alignment=al),
        "cellb": ParagraphStyle("cb", fontName="DejaVu-Bold", fontSize=6.8, leading=8.2, alignment=al),
    }


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _wrap_rtl(text: str, style, width: float) -> list[str]:
    """Greedy word-wrap of Arabic in LOGICAL order (measured on the reshaped glyphs), so each visual line can be
    reordered on its own. Reordering a whole paragraph first and letting the engine wrap it would put the end of
    the sentence on the first line."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if cur and pdfmetrics.stringWidth(arabic_reshaper.reshape(cand), style.fontName, style.fontSize) > width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def _p(text: str, style, lang: str, width: float | None = 180 * mm) -> Paragraph:
    text = text or ""
    if lang == "ar":
        lines = _wrap_rtl(text, style, width) if width else [text]
        return Paragraph("<br/>".join(_esc(ar(ln)) for ln in lines), style)
    return Paragraph(_esc(text), style)


def _hlab(d, issue, labels, lang) -> str:
    lab = labels.get(pd.Timestamp(d).date().isoformat()) or data_io.horizon_label(pd.Timestamp(d).date(), issue)
    if lang == "ar":
        return lab.replace("nowcast", TXT["nowcast"]["ar"]).replace(" wk", " " + TXT["wk"]["ar"])
    return lab


def _tile(lang: str, st: dict, rd: dict, pb: dict, col: str, obs: pd.DataFrame, issue: dt.date,
          labels: dict, decisions: dict) -> list:
    target = data_io.UAE_TARGETS[col]
    fc = rd["fc"]
    res = cardcheck.build_card(pb, target, "ARE", fc[fc.target == target], obs[col], issue)
    out = [_p(tx(col, lang), st["h"], lang)]
    lvl = _hlab(res.level_row.target_end_date, issue, labels, lang)
    sep = "، " if lang == "ar" else ", "
    facts = (f"{tx('last', lang)}: {res.last_value:.1f}% ({res.prev_value:.1f}% → {res.last_value:.1f}%) · "
             f"{tx('trend3', lang)}: {TREND_WORD[res.observed_trend][lang]} · "
             f"{tx('direction', lang)} ({lvl}): {cardcheck.FC_TXT[res.kit.forecast_key][lang]} "
             f"({tx('rise', lang)} {cardcheck.fmt_p(res.kit.p_up)}{sep}{tx('fall', lang)} {cardcheck.fmt_p(res.kit.p_down)}) · "
             f"{tx('path', lang)}: {TREND_WORD.get(res.trend, TREND_WORD['unknown'])[lang]}")
    out.append(_p(facts, st["b"], lang))
    w = fc[fc.target == target].pivot_table(index="target_end_date", columns="q", values="value").sort_index()
    w.columns = [round(float(c), 3) for c in w.columns]
    thr = list(res.exceed.columns) if res.exceed is not None else []
    pmap = {}
    if res.exceed is not None:
        for d, (_, row) in zip(res.exceed_dates, res.exceed.iterrows()):
            pmap[pd.Timestamp(d).date()] = row
    head = [tx("horizon", lang), tx("week_end", lang), tx("median", lang), tx("range80", lang)] + [f"P(> {T:g}%)" for T in thr]
    rows = [head]
    for d, r in w.iterrows():
        dd = pd.Timestamp(d).date()
        pr = pmap.get(dd)
        rows.append([_hlab(d, issue, labels, lang), dd.isoformat(), f"{r[0.5]:.1f}", f"{r[0.1]:.1f}–{r[0.9]:.1f}"]
                    + [cardcheck.fmt_p(pr[T]) if pr is not None else "–" for T in thr])
    if lang == "ar":
        rows = [list(reversed(r)) for r in rows]
    cells = [[_p(str(c), st["cellb"] if i == 0 else st["cell"], lang, width=None) for c in r] for i, r in enumerate(rows)]
    tb = Table(cells, hAlign="RIGHT" if lang == "ar" else "LEFT")
    tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f4f1")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    out.append(tb)
    if not res.renderable:
        out.append(_p(tx("blocked", lang), st["b"], lang))
        return [KeepTogether(out)], res
    band = res.band
    out.append(_p(f"{tx('band', lang)}: {cardcheck.band_label(band, lang)} ({tx('tier', lang)} {band['tier']})", st["cellb"], lang))
    for role in pb["roles"]:
        if role not in band["actions"]:
            continue
        dec = decisions.get((target, role))
        status = (f"{tx('decided', lang)}: {dec['decision']} · {dec['approver']} · {dec['hash'][:10]}" if dec
                  else tx("proposed", lang))
        out.append(_p(f"• {pb['roles'][role][lang]}: {band['actions'][role][lang]} [{status}]", st["cell"], lang))
    return [KeepTogether(out)], res


def _page(lang: str, rd: dict, pb: dict, obs: pd.DataFrame, issue: dt.date, charts: dict, scores) -> list:
    st = _styles(lang)
    meta = rd["meta"]
    labels = data_io.round_horizon_labels(rd["file"])
    decisions = round_decisions(rd["file"].name, issue)
    last_end = obs.week_end.iloc[-1]
    lag = (issue - last_end).days
    through = f"{int(obs.ISO_YEAR.iloc[-1])}-W{int(obs.ISO_WEEK.iloc[-1]):02d} ({last_end.isoformat()})"
    _iss = str(meta.get("issued_utc") or "")
    issued = (f"{_iss[:10]} {_iss[11:16]} UTC" if len(_iss) >= 16 else rd["stamp"])
    anchored = bool(meta.get("public")) and bool(meta.get("anchored"))
    flow = [_p(tx("title", lang), st["title"], lang), _p(tx("sub", lang), st["sub"], lang), Spacer(1, 3)]
    hdr = (f"{tx('issued', lang)}: {issued} · {tx('through', lang)}: {through} · {tx('lag', lang)}: {lag} {tx('days', lang)} · "
           f"{tx('model', lang)}: {rd['model']} · {tx('round', lang)}: {meta.get('round', '')} {rd['stamp']} · "
           f"{tx('anchor', lang)}: {tx('anchor_yes' if anchored else 'anchor_no', lang)}")
    flow.append(_p(hdr, st["small"], lang))
    flow.append(Spacer(1, 4))
    for col in ("rsv", "flu"):
        tile, _ = _tile(lang, st, rd, pb, col, obs, issue, labels, decisions)
        flow += tile
        flow.append(Spacer(1, 3))
    imgs = [Image(io.BytesIO(charts["rsv"]), width=88 * mm, height=46 * mm),
            Image(io.BytesIO(charts["flu"]), width=88 * mm, height=46 * mm)]
    if lang == "ar":
        imgs = imgs[::-1]
    flow.append(Table([imgs], colWidths=[90 * mm, 90 * mm]))
    flow.append(_p(tx("shape", lang), st["h"], lang))
    flow.append(Image(io.BytesIO(charts["shape"]), width=180 * mm, height=41 * mm))
    flow.append(_p(tx("track", lang), st["h"], lang))
    if scores is None:
        flow.append(_p(tx("track_none", lang), st["b"], lang))
    else:
        flow.append(_p(f"{len(scores)} scored rows (ledger/scores.csv).", st["b"], lang))
    box = [_p(tx("not_title", lang), st["cellb"], lang)] + [_p("• " + s, st["cell"], lang) for s in TXT["not"][lang]]
    bt = Table([[box]], colWidths=[180 * mm])
    bt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SAND)),
                            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e0a100")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    flow += [Spacer(1, 4), bt, Spacer(1, 3),
             _p(tx("playbook_note", lang, v=pb["version"]), st["small"], lang),
             _p(tx("footer", lang, sha=rd["sha256"]), st["small"], lang)]
    return flow


def build_pdf_bytes(stamp: str | None = None) -> bytes:
    stamps = round_stamps()
    if not stamps:
        raise FileNotFoundError("no ledger rounds")
    stamp = stamps[-1] if stamp in (None, "latest") else stamp
    rd = load_round(stamp)
    pb = load_playbook()
    obs = observed_as_of(rd["meta"])
    issue = dt.date.fromisoformat(stamp[:10])
    charts = {
        "rsv": fan_png(obs, "rsv", rd["fc"], rd["pers"], data_io.UAE_TARGETS["rsv"], issue, "RSV %"),
        "flu": fan_png(obs, "flu", rd["fc"], rd["pers"], data_io.UAE_TARGETS["flu"], issue, "Influenza %"),
        "shape": shape_png(obs),
    }
    scores = round_scores(rd["model"], stamp)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=11 * mm,
                            bottomMargin=10 * mm, title=f"NABD weekly bulletin {stamp}", author="NABD prototype",
                            subject="RSV and influenza forecast bulletin (UAE)", creator="NABD bulletin/make_bulletin.py")
    story = _page("en", rd, pb, obs, issue, charts, scores) + [PageBreak()] + _page("ar", rd, pb, obs, issue, charts, scores)
    doc.build(story)
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", default="latest", help="ledger round stamp, e.g. 2026-11-08T1212Z, or 'latest'")
    ap.add_argument("--out", default=None, help="output PDF path (default bulletin/out/NABD-bulletin-<stamp>.pdf)")
    a = ap.parse_args(argv)
    stamps = round_stamps()
    stamp = stamps[-1] if a.round == "latest" else a.round
    pdf = build_pdf_bytes(stamp)
    out = Path(a.out) if a.out else OUT_DIR / f"NABD-bulletin-{stamp}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf)
    import hashlib
    print(f"wrote {out} ({len(pdf):,} bytes, sha256 {hashlib.sha256(pdf).hexdigest()[:16]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
