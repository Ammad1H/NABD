"""NABD Streamlit app. Run:  streamlit run app/streamlit_app.py

Reads only interface-contract paths (docs/BUILD-SPEC.md v1.1–v1.4). Rules:
- Results panels (US proof, alerts, GCC, feed removal, explanations) show "not yet computed" when
  their file is missing. They never show demo numbers.
- Only the weekly card can fall back to DEMO forecasts (when no ledger round or retrospective file
  exists), and then a DEMO DATA banner is shown.
- Every weekly card passes the consistency gate in app/cardcheck.py (G14) before its action renders.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import altair as alt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app import audit, cardcheck, data_io, planner  # noqa: E402
from app.i18n import t  # noqa: E402
from app.workforce import secure_aggregate, synthetic_employers  # noqa: E402
from playbook.validate import load_playbook  # noqa: E402

TEAL, SLATE, SAND, ROSE, GREEN = "#1f7a8c", "#334155", "#e2d4b7", "#b4505b", "#2e7d5b"

st.set_page_config(page_title="NABD", page_icon="🫀", layout="wide")

lang = st.sidebar.radio("Language / اللغة", ["en", "ar"], format_func=lambda x: "English" if x == "en" else "العربية")
rtl = lang == "ar"
st.markdown(f"""
<style>
  .stApp {{ background: #f7f9fb; }}
  h1, h2, h3 {{ color: {SLATE}; }}
  .nabd-banner {{ background:#fff4e5; border-left:6px solid #e0a100; padding:.6rem 1rem; border-radius:4px; margin-bottom:.8rem; }}
  .nabd-sim {{ background:#fde8ea; border:2px dashed {ROSE}; color:{ROSE}; font-weight:700; text-align:center;
               padding:.4rem; letter-spacing:.3em; border-radius:4px; }}
  .nabd-badge-ok {{ background:#e6f4f1; color:{TEAL}; padding:.25rem .6rem; border-radius:12px; font-weight:600; }}
  .nabd-badge-warn {{ background:#fde8ea; color:{ROSE}; padding:.25rem .6rem; border-radius:12px; font-weight:600; }}
  .nabd-card {{ background:white; border:1px solid #e5e7eb; border-radius:8px; padding:1rem; }}
  .nabd-verdict-bad {{ background:#fde8ea; border:2px solid {ROSE}; color:#7a1f2b; border-radius:8px; padding:1rem; }}
  .nabd-verdict-good {{ background:#e6f4f1; border:2px solid {GREEN}; color:#1d4d39; border-radius:8px; padding:1rem; }}
  .nabd-pill {{ display:inline-block; background:{ROSE}; color:white; font-weight:800; padding:.2rem .7rem;
                border-radius:6px; letter-spacing:.08em; margin-right:.5rem; }}
  .nabd-pill-good {{ background:{GREEN}; }}
  .nabd-explore {{ background:#f1f5f9; border-left:6px solid #64748b; padding:.5rem 1rem; border-radius:4px; }}
  {"section.main .block-container, .stMarkdown, .stRadio, .stSelectbox, .stTextInput {direction: rtl; text-align: right;}" if rtl else ""}
</style>""", unsafe_allow_html=True)

PAGES = ["nav_card", "nav_shape", "nav_scenario", "nav_planner", "nav_gcc", "nav_ledger", "nav_us", "nav_alerts", "nav_ablation",
         "nav_workforce", "nav_about"]
page = st.sidebar.radio("Page", PAGES, format_func=lambda k: t(k, lang))
st.sidebar.caption("NABD prototype · Future Health Digital Innovation Challenge 2026 · Statement 06")


@st.cache_data(ttl=300)
def _evidence_lines() -> list[str]:
    """BUILD-SPEC v1.7 evidence order, read from results files (never hard-coded numbers)."""
    lines = []
    gcc, _, _ = data_io.load_gcc()
    res = (gcc or {}).get("results", {}) if isinstance(gcc, dict) else {}
    pf, pa = res.get("PRIMARY_flu_v1_vs_persistence"), res.get("flu_NABD-UAE-v1_vs_seasonal-analog")
    if pf:
        inc = ", ".join((gcc or {}).get("included_countries") or [])
        txt = (f"**1. Out-of-sample Gulf test** ({inc}; plan locked in our git history before their data were "
               f"downloaded; self-attested until externally timestamped). Influenza forecast error vs "
               f"past-season patterns: **{(1 - pa['rel_wis']) * 100:.0f}% lower** "
               f"(relative WIS {pa['rel_wis']:.2f}, {pa['ci95'][0]:.2f}–{pa['ci95'][1]:.2f}; pre-registered secondary)."
               if pa else f"**1. Out-of-sample Gulf test** ({inc}).")
        txt += (f" Vs last-week persistence: **{(1 - pf['rel_wis']) * 100:.0f}% lower** ({pf['rel_wis']:.3f}, "
                f"{pf['ci95'][0]:.2f}–{pf['ci95'][1]:.2f}; primary, {res.get('PRIMARY_verdict', '?')}).")
        lines.append(txt)
    else:
        lines.append("**1. Out-of-sample Gulf test:** not yet computed.")
    v, _ = data_io.us_verdict(data_io.load_us_summary())
    league, _ = data_io.load_league()
    lt = league.get("league_table")
    rank = ""
    if lt is not None:
        nab = lt[lt.model.astype(str).str.startswith("NABD") & (lt.variant == "excluding ensembles")]
        rank = "; among single hub models: " + ", ".join(f"{int(r.rank)} of {int(r.n_models)} in {r.season}"
                                                          for r in nab.itertuples())
    lines.append(f"**2. US vs the CDC FluSight ensemble:** missed our pre-set bar ({v or 'not yet computed'}){rank}.")
    fit = data_io.load_uae_forward_in_time()
    if fit:
        lines.append("**3. UAE's own short record (forward-in-time, v1 vs persistence):** "
                     + ", ".join(f"{k} {d['rel_wis']:.3f}" for k, d in fit.items()) + ": parity.")
    rounds = data_io.ledger_round_files()
    n_rounds = len({r.name.split("_")[0] for r in rounds})
    lines.append(f"**4. Live forecast ledger:** {n_rounds} issued round(s), {len(rounds)} hashed file(s) (R0 and R1 "
                 "carry the same v1 forecast; R1 adds the v2 challenger); 0 weeks scored so far; local only until "
                 "pushed and externally timestamped. The pilot ask.")
    return lines


def _gcc_label(key: str) -> str:
    """Plain-language label for a results/gcc/summary.json key (the raw key stays in the JSON)."""
    names = {"NABD-UAE-v1": "NABD v1 (frozen UAE method)", "NABD-UAE-v2-GCC": "NABD v2 challenger",
             "persistence": "last week carried forward", "seasonal-analog": "past-season pattern"}
    primary = key.startswith("PRIMARY_")
    k = key.replace("PRIMARY_", "")
    series, rest = k.split("_", 1)
    a, b = rest.split("_vs_")
    lab = f"{'Influenza' if series == 'flu' else 'RSV'}: {names.get(a, a)} vs {names.get(b, b)}"
    if primary:
        lab += " (PRIMARY, pre-registered)"
    elif series == "flu" and b == "seasonal-analog":
        lab += " (pre-registered secondary)"
    else:
        lab += " (secondary)"
    return lab


with st.sidebar.expander("📊 " + ("Evidence, in order" if lang == "en" else "الأدلة بالترتيب"), expanded=True):
    for _ln in _evidence_lines():
        st.markdown(_ln)

st.title(t("title", lang))
st.caption(t("subtitle", lang))


def demo_banner():
    st.markdown(f'<div class="nabd-banner"><b>⚠ {t("demo_banner", lang)}</b></div>', unsafe_allow_html=True)


def not_computed(what: str, path: str):
    st.info(f"**{t('not_computed', lang)}:** {what}  \nExpected file: `{path}`")


def sim_watermark():
    st.markdown(f'<div class="nabd-sim">{t("simulated", lang)} · {t("simulated", "en" if rtl else "ar")}</div>',
                unsafe_allow_html=True)


def exploratory_note():
    st.markdown(f'<div class="nabd-explore"><b>{t("exploratory", lang)}</b></div>', unsafe_allow_html=True)


@st.cache_data(ttl=300)
def _observed():
    return data_io.load_uae_observed()


observed = _observed()


# ------------------------------------------------------------------ helpers
def fan_frame(fc: pd.DataFrame, target: str) -> pd.DataFrame:
    g = fc[fc.target == target]
    piv = g.pivot_table(index="target_end_date", columns="q", values="value").reset_index()
    piv.columns = [c if isinstance(c, str) else round(float(c), 3) for c in piv.columns]
    return piv


def _qcols(df: pd.DataFrame) -> pd.DataFrame:
    """Vega-Lite treats dots in field names as nested access, so rename 0.025 -> q025 etc."""
    return df.rename(columns={c: f"q{int(round(c * 1000)):03d}" for c in df.columns if isinstance(c, float)})


def fan_chart(col: str, target: str, fc: pd.DataFrame, pers: pd.DataFrame, issue: dt.date, meta: dict | None = None):
    hist = observed[["week_end", col]].dropna().tail(16).rename(columns={col: "value"})
    hist["week_end"] = pd.to_datetime(hist.week_end)
    f = _qcols(fan_frame(fc, target))
    f["target_end_date"] = pd.to_datetime(f.target_end_date)
    f["horizon"] = [data_io.display_horizon(d.date(), issue, meta) for d in f.target_end_date]
    p = _qcols(fan_frame(pers, target))
    p["target_end_date"] = pd.to_datetime(p.target_end_date)
    base = alt.Chart(f).encode(x=alt.X("target_end_date:T", title="Week ending"))
    band95 = base.mark_area(opacity=0.18, color=TEAL).encode(y=alt.Y("q025:Q", title="%"), y2="q975:Q")
    band80 = base.mark_area(opacity=0.35, color=TEAL).encode(y="q100:Q", y2="q900:Q")
    med = base.mark_line(color=TEAL, strokeWidth=3, point=True).encode(
        y="q500:Q", tooltip=[alt.Tooltip("target_end_date:T", title="week end"), "horizon:N",
                             alt.Tooltip("q100:Q", format=".1f", title="10%"), alt.Tooltip("q500:Q", format=".1f", title="median"),
                             alt.Tooltip("q900:Q", format=".1f", title="90%")])
    pers_line = alt.Chart(p).mark_line(color=SLATE, strokeDash=[6, 4], point=True).encode(
        x="target_end_date:T", y="q500:Q", tooltip=[alt.Tooltip("q500:Q", format=".1f", title="persistence median")])
    h = alt.Chart(hist).mark_line(color=SLATE, point=alt.OverlayMarkDef(size=18)).encode(
        x="week_end:T", y="value:Q", tooltip=[alt.Tooltip("week_end:T"), alt.Tooltip("value:Q", format=".1f")])
    issue_rule = alt.Chart(pd.DataFrame({"d": [pd.Timestamp(issue)]})).mark_rule(color=ROSE, strokeDash=[2, 2]).encode(x="d:T")
    return (band95 + band80 + h + pers_line + med + issue_rule).properties(height=300)


def context_lines(col: str) -> list[str]:
    s = observed.dropna(subset=[col])
    last3 = s[col].tail(3).round(1).tolist()
    spec = s.specimens.tail(2).tolist()
    spec_chg = 100 * (spec[-1] - spec[0]) / spec[0] if spec[0] else 0
    hist_peak = (observed.assign(season=np.where(observed.ISO_WEEK >= 27, observed.ISO_YEAR, observed.ISO_YEAR - 1))
                 .dropna(subset=[col]).groupby("season").apply(lambda g: int(g.loc[g[col].idxmax(), "ISO_WEEK"]),
                                                              include_groups=False))
    hist_peak = hist_peak.iloc[:-1]  # drop the current, incomplete season
    return [f"Last 3 published weeks: {' → '.join(map(str, last3))}%",
            f"Testing volume change (last week): {spec_chg:+.0f}%" + (" ⚠ >30%: interpret positivity with care" if abs(spec_chg) > 30 else ""),
            f"Peak week (ISO) in previous seasons: {', '.join(map(str, hist_peak.tolist()[-4:]))}"]


FEATURE_TXT = {
    "last_observed_logit": {"en": "Starting point: last published positivity", "ar": "نقطة البداية: آخر نسبة إيجابية منشورة"},
    "intercept": {"en": "Model constant", "ar": "ثابت النموذج"},
    "dy1": {"en": "Change over the last published week", "ar": "التغير خلال آخر أسبوع منشور"},
    "anom": {"en": "Above/below the usual level for this week of the season", "ar": "أعلى/أدنى من المستوى المعتاد لهذا الأسبوع من الموسم"},
    "dclim": {"en": "Usual seasonal change from now to the target week", "ar": "التغير الموسمي المعتاد من الآن حتى الأسبوع المستهدف"},
    "dlogspec": {"en": "Change in testing volume", "ar": "التغير في حجم الفحوصات"},
    "ns_dy1": {"en": "Change in non-sentinel (hospital lab) positivity", "ar": "التغير في إيجابية المختبرات غير الرصدية (المستشفيات)"},
    "ns_gap": {"en": "Gap: non-sentinel vs sentinel positivity", "ar": "الفجوة بين الإيجابية غير الرصدية والرصدية"},
    "school_win": {"en": "School break in the target window", "ar": "عطلة مدرسية ضمن الفترة المستهدفة"},
    "ram_win": {"en": "Ramadan in the target window", "ar": "رمضان ضمن الفترة المستهدفة"},
    "residual_median_offset": {"en": "Calibration offset (median of past errors)", "ar": "إزاحة المعايرة (وسيط الأخطاء السابقة)"},
}
BASE_TERMS = {"last_observed_logit", "intercept", "residual_median_offset"}


def _wrap(s: str, width: int = 30) -> str:
    """Break a long axis label into lines (joined by '|', split by the Vega labelExpr)."""
    words, lines, cur = str(s).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "|".join(lines)


@st.cache_data(ttl=600)
def bulletin_bytes(meta: dict) -> bytes | None:
    """PDF bulletin for this ledger round: the committed file in bulletin/out/ if present, else built on the fly."""
    try:
        from bulletin import make_bulletin
        stamp = meta.get("round_stamp")
        out = ROOT / "bulletin" / "out" / f"NABD-bulletin-{stamp}.pdf"
        if out.exists():
            return out.read_bytes()
        return make_bulletin.build_pdf_bytes(stamp)
    except Exception:  # noqa: BLE001 - the card must still render if the bulletin cannot be built
        return None


def feature_name(f: str) -> str:
    return FEATURE_TXT.get(str(f), {}).get(lang, str(f))


def explain_panel(col: str, ex: pd.DataFrame | None, ex_date: str | None, issue: dt.date, default_wk: float):
    st.markdown(f"**{t('why', lang)}**")
    if ex is None or ex.empty:
        not_computed("per-signal contributions for this forecast (UAE v2, linear on the logit scale)",
                     "results/uae/explain/<issue_date>_<target>.csv")
        return
    if ex_date != issue.isoformat():
        st.caption(f"No explanation file exists yet for this card's issue date ({issue.isoformat()}). Showing the latest "
                   f"available example, issue date {ex_date}"
                   + (f" ({ex['design'].iloc[0]})" if "design" in ex.columns else "") + ", to illustrate the method.")
    ex = ex.copy()
    if "target_end_date" in ex.columns:
        ex_issue = dt.date.fromisoformat(str(ex["issue_date"].iloc[0])) if "issue_date" in ex.columns else issue
        weeks = sorted(pd.unique(ex["target_end_date"].astype(str)))
        wk_of = {w: data_io.horizon_weeks(w, ex_issue) for w in weeks}
        default = next((i for i, w in enumerate(weeks) if wk_of[w] == int(default_wk)), 0)
        sel = st.selectbox(t("week_end", lang), weeks, index=default, key=f"exh_{col}",
                           format_func=lambda w: data_io.display_horizon(w, ex_issue, None, lang))
        g = ex[ex["target_end_date"].astype(str) == sel].copy()
    else:  # older explain files without dates: fall back to the model step
        horizons = list(pd.unique(ex["horizon"]))
        h = st.selectbox("Model step", horizons, index=horizons.index(0) if 0 in horizons else 0, key=f"exh_{col}")
        g = ex[ex["horizon"] == h].copy()
    g["contribution"] = pd.to_numeric(g["contribution"], errors="coerce")
    g = g.dropna(subset=["contribution"])
    unit = str(g["unit"].iloc[0]) if "unit" in g.columns and len(g) else ""
    sig = g[~g.feature.isin(BASE_TERMS)].copy()
    sig["abs"] = sig.contribution.abs()
    sig = sig.sort_values("abs", ascending=False)
    sig["label"] = [_wrap(x) for x in sig.feature.map(feature_name)]
    sig["direction"] = np.where(sig.contribution >= 0, "pushes up", "pushes down")
    if "median_pct" in g.columns and len(g):
        st.caption(f"Model median for this step: {float(g['median_pct'].iloc[0]):.1f}%"
                   + (f" (target week ending {g['target_end_date'].iloc[0]})" if "target_end_date" in g.columns else ""))
    if not sig.empty:
        ch = alt.Chart(sig).mark_bar().encode(
            y=alt.Y("label:N", sort=list(sig.label), title=None,
                    axis=alt.Axis(labelLimit=0, labelFontSize=11, labelOverlap=False, labelPadding=6,
                                  labelExpr="split(datum.label, '|')")),
            x=alt.X("contribution:Q", title=f"contribution ({unit})" if unit else "contribution"),
            color=alt.Color("direction:N", scale=alt.Scale(domain=["pushes up", "pushes down"], range=[ROSE, TEAL]), legend=None),
            tooltip=["feature", "value", alt.Tooltip("contribution:Q", format="+.3f")]).properties(height=64 * max(len(sig), 3))
        st.altair_chart(ch, width="stretch")
    for r in list(sig.itertuples()):
        r = r._replace(label=str(r.label).replace("|", " "))
        pp = getattr(r, "pp_effect_loo", np.nan)
        verb = "pushed the forecast up" if r.contribution >= 0 else "pushed the forecast down"
        extra = f"; without it the median would move by {-float(pp):+.1f} percentage points" if pd.notna(pp) else ""
        gloss = ""
        val = getattr(r, "value", np.nan)
        try:
            val = float(val)
        except (TypeError, ValueError):
            val = np.nan
        if str(getattr(r, "feature", "")).startswith("dy1") and pd.notna(val) and val < 0 <= r.contribution:
            gloss = (" The last week fell, and the model expects part of a one-week drop to reverse "
                     "(week-to-week noise), so this term nudges the forecast back up")
        st.markdown(f"- **{r.label}** {verb} ({r.contribution:+.2f} {unit}{extra}).{gloss}")
    model_name = str(ex["model"].iloc[0]) if "model" in ex.columns and len(ex) else "the UAE linear model"
    st.caption(f"Exact additive terms of {model_name} (linear on the logit scale): starting point + constant + signal "
               "terms + calibration offset = forecast median on the logit scale. They describe the model, not causes.")


# ------------------------------------------------------------------ pages
if page == "nav_card":
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    fr = data_io.freshness(observed)
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    hl = lambda d: data_io.display_horizon(d, issue, meta, lang)  # noqa: E731  (one convention everywhere)
    c1, c2, c3 = st.columns([2, 2, 3])
    c1.metric(t("last_week", lang), fr["last_week"])
    c2.metric(t("lag", lang), f'{fr["lag_days"]} {t("days", lang)}', f'{t("expected", lang)} ~{fr["expected_lag_days"]}', delta_color="off")
    badge = "nabd-badge-warn" if fr["stale"] else "nabd-badge-ok"
    c3.markdown(f'<br><span class="{badge}">{t("freshness", lang)}: {t("stale" if fr["stale"] else "fresh", lang)}</span>'
                f'<br><small>Issued {issue.isoformat()} · model: <b>{meta.get("model")}</b> · source: {meta.get("source")}'
                + (f'<br>round <code>{meta["round_file"]}</code> · SHA-256 <code>{meta["sha256"][:16]}…</code>' if meta.get("round_file") else "")
                + '</small>', unsafe_allow_html=True)
    bpdf = bulletin_bytes(meta) if meta.get("round_stamp") else None
    if bpdf:
        st.download_button(t("bulletin_dl", lang), data=bpdf, file_name=f"NABD-bulletin-{meta['round_stamp']}.pdf",
                           mime="application/pdf")

    pb = load_playbook()
    explain, ex_date = data_io.load_uae_explain(issue.isoformat())
    for col in ("rsv", "flu"):
        target = data_io.UAE_TARGETS[col]
        st.subheader(t(col, lang))
        res = cardcheck.build_card(pb, target, "ARE", fc[fc.target == target], observed[col], issue)
        # ---- 1. Key numbers and the proposed action first
        top_l, top_r = st.columns([3, 2])
        with top_l:
            st.markdown(f'<div class="nabd-card">{cardcheck.card_sentence(res, lang, hl(res.level_row.target_end_date))}'
                        f'<br><small>{t("obs_trend", lang)}: <b>{cardcheck.TREND_TXT[res.observed_trend][lang]}</b> '
                        f'(log-slope {res.observed_slope:+.2f}/wk over the last 3 published weeks; context only)</small>'
                        '</div>', unsafe_allow_html=True)
            if res.exceed is not None:
                st.markdown(f"**{t('exceed_title', lang)}**")
                ex_tbl = pd.DataFrame({
                    t("week_end", lang): [data_io.week_ending_label(d, lang) for d in res.exceed_dates],
                    t("horizon", lang): [data_io.horizon_label(d, issue, lang) for d in res.exceed_dates],
                    **{f"P(> {T:g}%)": [cardcheck.fmt_p(v) for v in res.exceed[T]] for T in res.exceed.columns}})
                st.dataframe(ex_tbl, hide_index=True, width="stretch")
                lvl_txt = (f"{res.level:g}%" if res.level > 0 else t("below_tiers", lang))
                st.caption(f"{t('decision_rule', lang)} {res.p_act:.0%}. "
                           f"{t('effective_level', lang)}: {lvl_txt}. "
                           + t("edge_note", lang))
        with top_r:
            st.markdown(f"**{t('action', lang)}**")
            st.caption(f"⚠ {t('illustrative', lang)} · playbook v{pb['version']}")
            if not res.renderable:
                st.error(t("blocked", lang) + "\n\n" + "\n".join(f"- {p}" for p in res.problems))
            else:
                band = res.band
                role_lines = "".join(f'<b>{pb["roles"][r][lang]}:</b> {band["actions"][r][lang]}<br>'
                                     for r in pb["roles"] if r in band["actions"])
                st.markdown(f'<div class="nabd-card"><b style="font-size:1.05rem">{cardcheck.band_label(band, lang)}</b> '
                            f'<small>(tier {band["tier"]})</small><br>'
                            f'<small>{t("chosen_from", lang)} {res.level:g}% · {t("fc_path", lang)} '
                            f'{cardcheck.TREND_TXT[res.trend][lang]} ({res.trend_ratio:.2f}×)</small><br><br>'
                            f'{role_lines}</div>', unsafe_allow_html=True)
                st.caption(t("passed_check", lang))
        # ---- 2. Evidence: fan chart, horizon table, explanation; approval form and context
        left, right = st.columns([3, 2])
        with left:
            st.altair_chart(fan_chart(col, target, fc, pers, issue, meta), width="stretch")
            st.caption(f"Teal: forecast median with 80% / 95% bands · dashed slate: {t('persistence', lang)} · red rule: issue date")
            f = fan_frame(fc, target)
            pe = fan_frame(pers, target)
            tbl = pd.DataFrame({
                t("week_end", lang): [data_io.week_ending_label(d, lang) for d in f.target_end_date],
                t("horizon", lang): [data_io.horizon_label(d, issue, lang) for d in f.target_end_date],
                t("median", lang): f[0.5].round(1),
                t("band80", lang): [f"{a:.1f}–{b:.1f}" for a, b in zip(f[0.1], f[0.9])],
                t("persistence_short", lang): f.target_end_date.map(dict(zip(pe.target_end_date, pe[0.5].round(1)))).values,
            })
            st.dataframe(tbl, hide_index=True, width="stretch")
            st.caption(t("horizon_note", lang))
            explain_panel(col, explain.get(col), ex_date, issue, res.level_horizon_wk)
        with right:
            if res.renderable:
                band = res.band
                with st.form(f"decide_{col}"):
                    st.markdown(f"**{t('record_title', lang)}**")
                    role = st.selectbox(t("role", lang), list(pb["roles"]), format_func=lambda r: pb["roles"][r][lang])
                    approver = st.text_input(t("approver", lang))
                    decision = st.radio(t("decision", lang), ["APPROVE", "MODIFY", "DISMISS"], horizontal=True,
                                        format_func=lambda d: t(d.lower(), lang))
                    codes = {rc["code"]: rc[lang] for rc in pb["reason_codes"]}
                    reason = st.selectbox(t("reason", lang), list(codes), format_func=lambda c: codes[c])
                    modified = st.text_input(t("modified", lang))
                    note = st.text_area(t("note", lang), height=60)
                    if st.form_submit_button(t("submit", lang)):
                        try:
                            rec = audit.append_decision(
                                approver=approver, role=role, decision=decision, reason_code=reason, note=note,
                                band_id=band["id"], proposed_action=band["actions"][role]["en"],
                                modified_action=modified if decision == "MODIFY" else None,
                                forecast_ref={"model": meta.get("model"), "reference_date": issue.isoformat(),
                                              "target": target, "target_end_date": str(res.level_row.target_end_date),
                                              "median": round(float(res.level_row[0.5]), 2), "trend": res.trend,
                                              "effective_level": res.level,
                                              "max_p_exceed": {f"{k:g}": round(v, 3) for k, v in res.max_p.items()},
                                              "forecast_key": res.kit.forecast_key, "demo": is_demo,
                                              "round_file": meta.get("round_file")},
                                playbook_version=pb["version"], valid_reason_codes=set(codes))
                            st.success(f"{t('recorded', lang)} · #{rec['seq']} · {rec['hash'][:16]}…")
                        except audit.AuditError as e:
                            st.error(str(e))
            st.markdown(f"**{t('context', lang)}**")
            for d in context_lines(col):
                st.markdown(f"- {d}")
        st.divider()
    with st.expander(t("audit", lang)):
        ok, msg = audit.verify_chain()
        (st.success if ok else st.error)(msg)
        recs = audit.read_records()
        if recs:
            _labels = {b["id"]: cardcheck.band_label(b, lang) for b in pb.get("bands", [])}
            _df = pd.DataFrame(recs)
            _df["band"] = _df["band_id"].map(lambda i: _labels.get(i, i))
            st.dataframe(_df[["seq", "ts_utc", "approver", "role", "decision", "reason_code", "band", "hash"]],
                         hide_index=True, width="stretch")

elif page == "nav_alerts":
    st.subheader(t("nav_alerts", lang))
    st.markdown("Statement 06 asks for alert lead time, sensitivity, PPV, false alarms, data latency and behaviour "
                "when a feed is missing. The honest headline: **no forecast here, NABD's or the CDC's, warns of surge "
                "onset earlier than a simple threshold on the latest counts** (median lead about 0 weeks). At the primary "
                "US threshold every rule had **zero** false alarms; NABD's higher PPV comes from fewer *late* first "
                "alerts. The value NABD adds is the size and duration of the coming weeks.")
    alerts = data_io.load_alerts()
    us = alerts.get("US alerts_us")
    if us is None:
        not_computed("US alert metrics", "results/tables/alerts_us.csv")
    else:
        st.markdown("#### US state flu admissions (2024/25, 2025/26)")
        thr = sorted(us["T_per_100k"].unique())
        T = st.radio("Onset threshold (per 100k)", thr, index=thr.index(3.0) if 3.0 in thr else 0, horizontal=True)
        g = us[us.T_per_100k == T].copy()
        show = g[["season", "rule", "eligible_loc_seasons", "sensitivity_lead0to4", "median_lead_weeks_timely",
                  "ppv", "false_alarms_per_loc_season", "premature_gt4"]].rename(columns={
                      "eligible_loc_seasons": "eligible", "sensitivity_lead0to4": "sensitivity (lead 0–4 wk)",
                      "median_lead_weeks_timely": "median lead (wk)", "false_alarms_per_loc_season": "false alarms / loc-season",
                      "premature_gt4": "premature (>4 wk)"})
        st.dataframe(show.round(3), hide_index=True, width="stretch")
        ch = alt.Chart(g).mark_bar().encode(x=alt.X("rule:N", title=None), y=alt.Y("ppv:Q", title="PPV", scale=alt.Scale(domain=[0, 1])),
                                            color=alt.Color("rule:N", legend=None), column=alt.Column("season:N", title=None))
        st.altair_chart(ch.properties(width=180, height=200))
        st.caption("Rule D3 (docs/DEVIATIONS.md). Its thresholds were informed by probes that touched the test seasons "
                   "before the freeze (DEVIATIONS D5), so these metrics are **diagnostic**, not confirmatory.")
        for key, label in (("US latency_us", "Data latency (input-to-issue lag, stale rounds)"),
                           ("US dropout_us", "Missing-feed behaviour: WIS when inputs are truncated by 1–2 extra weeks")):
            if key in alerts:
                with st.expander(label):
                    st.dataframe(alerts[key], hide_index=True, width="stretch")
    st.markdown("#### UAE sentinel positivity (n = 4 seasons, descriptive; RETIRED design)")
    st.warning("These UAE alert counts come from the **leave-one-season-out (LOSO)** design, in which the model is "
               "trained on later seasons. That design is **retired as evidence** (DEVIATIONS U1, claims-ledger D4/F18). "
               "Shown for transparency only; do not cite them.")
    uae_keys = [k for k in alerts if k.startswith("UAE ")]
    if not uae_keys:
        not_computed("UAE alert metrics under the pre-declared UAE alert rule", "results/uae/tables/alert*.csv")
    for k in uae_keys:
        st.markdown(f"**{k[4:]}**")
        st.dataframe(alerts[k], hide_index=True, width="stretch")
    if uae_keys:
        st.caption("Four seasons only: these are descriptive counts, not estimates with useful confidence intervals.")

elif page == "nav_us":
    summary = data_io.load_us_summary()
    tables = data_io.load_us_tables()
    st.subheader(t("verdict", lang))
    st.markdown("NABD-ensemble vs the CDC FluSight-ensemble on US state weekly flu admissions. Vintage-correct inputs, "
                "same truth for every model, relative WIS with bootstrap 95% CI, non-inferiority margin 1.15. The protocol "
                "was frozen before any test-season score (docs/FREEZE.md).")
    verdict, vtext = data_io.us_verdict(summary)
    if verdict is None:
        not_computed("pre-registered US primary endpoint", "results/summary.json")
    else:
        good = str(verdict).strip().upper() == "MET"
        st.markdown(f'<div class="{"nabd-verdict-good" if good else "nabd-verdict-bad"}" style="font-size:1.15rem">'
                    f'<span class="nabd-pill {"nabd-pill-good" if good else ""}">{verdict}</span>'
                    f'{vtext or ""}</div>', unsafe_allow_html=True)
        st.caption("Shown verbatim from results/summary.json. We set the bar at the CDC's best; v1 missed it.")
        s1 = (summary or {}).get("S1_vs_baseline")
        if isinstance(s1, dict) and s1.get("rel_wis") is not None:
            ci = s1.get("ci95") or [np.nan, np.nan]
            st.markdown(f"Secondary (S1), NABD vs FluSight-baseline (persistence): relative WIS **{s1['rel_wis']:.3f}** "
                        f"(95% CI {ci[0]:.3f}–{ci[1]:.3f}). The CI includes 1, so NABD is not shown to beat persistence.")
        ch2 = (summary or {}).get("chronos2")
        if ch2:
            st.caption(f"Chronos-2 foundation model: {ch2}")
    ep = tables.get("endpoints")
    if ep is not None:
        st.markdown("#### All pre-registered endpoints")
        cols = [c for c in ["analysis", "A", "B", "n_cells", "rel_wis", "ci_lo", "ci_hi", "cov50_A", "cov95_A"] if c in ep.columns]
        st.dataframe(ep[cols].round(3), hide_index=True, width="stretch")
    figs = [f for f in data_io.list_figures() if "league" not in f.name]
    for fig in figs:
        st.image(str(fig), caption=fig.name)

    st.markdown("#### Where NABD v1 ranks among individual CDC FluSight hub models")
    league, _ = data_io.load_league()
    lt = league.get("league_table")
    if lt is None:
        not_computed("league table (method declared before computing: docs/DEVIATIONS.md D7)", "results/tables/league_table.csv")
    else:
        nab = lt[lt.model.astype(str).str.startswith("NABD")]
        nab = nab.assign(_o=(nab.variant != "excluding ensembles")).sort_values(["_o", "season"])
        for r in nab.itertuples():
            who = "single hub models (ensembles excluded)" if r.variant == "excluding ensembles" else "all hub models incl. ensembles"
            st.markdown(f"- **{r.season}, {who}:** NABD v1 ranks **{int(r.rank)} of {int(r.n_models)}** "
                        f"(relative WIS vs FluSight-baseline {r.rel_wis:.2f}; lower is better).")
        st.caption("Pairwise relative WIS (Cramer et al. 2022) on common cells; inclusion rule declared before any hub "
                   "model was downloaded (DEVIATIONS D7). Context, not an endpoint.")
        seasons = list(pd.unique(lt.season))
        ss = st.radio("Season", seasons, horizontal=True, key="league_season")
        variants = sorted(pd.unique(lt[lt.season == ss].variant), key=lambda v: v != "excluding ensembles")
        vv = st.radio("Models included", variants, horizontal=True, key="league_variant",
                      help="'excluding ensembles' = single models only: the comparison quoted in the pitch.")
        g = lt[(lt.season == ss) & (lt.variant == vv)].sort_values("rel_wis").copy()
        g["who"] = np.where(g.model.astype(str).str.startswith("NABD"), "NABD v1",
                            np.where(g.model.astype(str).isin(["FluSight-ensemble", "FluSight-baseline"]), g.model.astype(str), "other hub model"))
        ch = alt.Chart(g).mark_bar().encode(
            y=alt.Y("model:N", sort=list(g.model), title=None, axis=alt.Axis(labelLimit=260)),
            x=alt.X("rel_wis:Q", title="relative WIS vs FluSight-baseline (lower is better)"),
            color=alt.Color("who:N", scale=alt.Scale(domain=["NABD v1", "FluSight-ensemble", "FluSight-baseline", "other hub model"],
                                                   range=[ROSE, TEAL, SLATE, "#cbd5e1"])),
            tooltip=["model", alt.Tooltip("rel_wis:Q", format=".3f"), "rank", "coverage"]).properties(height=14 * len(g))
        rule = alt.Chart(pd.DataFrame({"x": [1.0]})).mark_rule(strokeDash=[4, 4], color=SLATE).encode(x="x:Q")
        st.altair_chart(ch + rule, width="stretch")
    league_figs = [f for f in data_io.list_figures() if "league" in f.name]
    if league_figs:
        with st.expander("Hub league figure from results/ (ranks among ALL hub models, ensembles included)"):
            for fig in league_figs:
                st.image(str(fig), caption=f"{fig.name}: all-model ranks (e.g. 13 of 41) differ from the single-model "
                                           "ranks quoted in the pitch (7 of 21); both come from the same table.")

    r2 = (summary or {}).get("round2")
    sens = {k: v for k, v in tables.items() if any(x in k for x in ("sensitivity", "block", "per_location", "national"))}
    if sens or r2:
        with st.expander("Sensitivity analyses (declared in docs/DEVIATIONS.md D6/D11; they do not change the verdict)"):
            if isinstance(r2, dict):
                b4 = (r2.get("sensitivity_block_bootstrap_L4") or {}).get("PRIMARY pooled")
                if b4:
                    st.markdown(f"- Moving-block bootstrap (L = 4): primary relative WIS {b4[0]:.3f}, 95% CI {b4[1]:.3f}–{b4[2]:.3f}.")
                ns = r2.get("national_share_of_WIS") or {}
                if ns:
                    st.markdown("- Share of total WIS from the national US series: "
                                + ", ".join(f"{k} {v:.0%}" for k, v in ns.items()) + ".")
                ex = (r2.get("excl_US_national") or {}).get("PRIMARY excl. US national")
                if ex:
                    st.markdown(f"- Excluding the national series: relative WIS {ex['rel_wis']:.3f} "
                                f"(cluster CI {ex['cluster_ci_lo']:.3f}–{ex['cluster_ci_hi']:.3f}).")
                for w in r2.get("per_location_wins") or []:
                    st.markdown(f"- vs {w['comparator']}, {w['season']}: NABD better in {w['nabd_wins']} of {w['locations']} locations.")
            for name, df in sens.items():
                st.markdown(f"**{name}**")
                st.dataframe(df, hide_index=True, width="stretch")
    diag = {k: v for k, v in tables.items() if k.startswith(("phase_decomposition", "rev_curves", "scorer_crosscheck", "league_cells"))}
    if diag:
        with st.expander("Diagnostics (G13: where the error comes from; decision value; scorer cross-check)"):
            st.markdown("Phases here are **as-of** phases (computed only from data available at forecast time), "
                        "declared in DEVIATIONS D10 before computing. Descriptive, not an endpoint.")
            for name, df in diag.items():
                st.markdown(f"**{name}**")
                st.dataframe(df, hide_index=True, width="stretch")
    expl = {k: v for k, v in tables.items() if "exploratory" in k}
    expl_summary = (summary or {}).get("exploratory")
    if expl or expl_summary:
        with st.expander("EXPLORATORY analyses (post hoc; not pre-registered; never a claim)"):
            exploratory_note()
            st.markdown("Phases in E1 are defined from realised truth, so the split favours wider intervals in rising cells. "
                        "It is **not** evidence that NABD 'does better in surges' (docs/DEVIATIONS.md E1).")
            for name, df in expl.items():
                st.dataframe(df, hide_index=True, width="stretch")
            if expl_summary:
                st.json(expl_summary, expanded=False)
    skip = set(sens) | set(expl) | set(league) | set(diag) | {"endpoints"} | {k for k in tables if k.startswith(("alerts_us", "latency_us", "dropout_us"))}
    tech = {k: v for k, v in tables.items() if k not in skip}
    if tech:
        with st.expander("Technical tables (cell coverage, vintage flags, tuning)"):
            for name, df in tech.items():
                st.markdown(f"**{name}**")
                st.dataframe(df, hide_index=True, width="stretch")

    st.divider()
    st.subheader("UAE's own record (n = 4 seasons)")
    fit = data_io.load_uae_forward_in_time()
    if fit:
        st.markdown("**Forward-in-time (each season forecast using only earlier seasons), NABD-UAE-v1 vs persistence:** "
                    + "; ".join(f"{k} **{d['rel_wis']:.3f}** (block 95% CI {d['ci95_moving_block_L4'][0]:.2f}–"
                                f"{d['ci95_moving_block_L4'][1]:.2f})" for k, d in fit.items())
                    + ". **Parity with persistence:** the UAE record is too short to show skill on its own. That is why "
                    "the out-of-sample Gulf test (GCC page) and the live ledger carry the evidence.")
        st.caption("The multi-signal UAE v2 challenger did not improve on v1 (results/uae/SUMMARY-v2.md); it is reported, "
                   "not promoted.")
    uae = data_io.load_uae_summary()
    if uae is None:
        not_computed("UAE retrospective", "results/uae/summary.json")
    else:
        st.caption("Leave-one-season-out results below (verbatim from results/uae/summary.json) let each forecast learn "
                   "from LATER seasons too, so they flatter the model. Context only, not a headline.")
        for key in [k for k in uae if k.startswith("rel_wis")]:
            block = uae[key]
            if not isinstance(block, dict):
                continue
            rows = [{"comparison": k, "rel_wis": v.get("rel_wis"), "ci95_low": (v.get("ci95") or [None, None])[0],
                     "ci95_high": (v.get("ci95") or [None, None])[1], "n_reference_dates": v.get("n_reference_dates")}
                    for k, v in block.items() if isinstance(v, dict)]
            if rows:
                st.markdown(f"**{key}**")
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.json(uae, expanded=False)
        for name, df in data_io.load_uae_tables().items():
            if name == "ablation" or name.startswith("alert"):
                continue
            with st.expander(f"Table: {name}"):
                st.dataframe(df, hide_index=True, width="stretch")
        for fig in data_io.list_figures("uae"):
            st.image(str(fig), caption=fig.name)

elif page == "nav_gcc":
    st.subheader(t("nav_gcc", lang))
    st.markdown("Does the UAE method work on Gulf countries it was never tuned on? The frozen UAE method is run on "
                "other GCC countries' WHO FluNet data (other EMRO countries are not part of this test). The plan and "
                "inclusion rules were committed and locked in our git history **before** that data was downloaded "
                "(self-attested until externally timestamped), and every included country is reported, losses "
                "included (BUILD-SPEC G12, docs/PREREG-GCC.md). Influenza is the pre-registered primary; RSV is "
                "secondary (its country-clustered interval crosses 1).")
    summary, tabs, figs = data_io.load_gcc()
    if summary is None and not tabs:
        not_computed("GCC out-of-sample test", "results/gcc/summary.json")
    else:
        summary = summary if isinstance(summary, dict) else {}
        res = summary.get("results") if isinstance(summary.get("results"), dict) else summary
        v = res.get("PRIMARY_verdict") or summary.get("primary_verdict") or summary.get("verdict")
        prim_key = next((k for k in res if k.upper().startswith("PRIMARY") and isinstance(res[k], dict)), None)
        txt = summary.get("primary_text")
        if txt is None and prim_key:
            p_ = res[prim_key]
            ci = p_.get("ci95") or [np.nan, np.nan]
            txt = (f"Primary ({prim_key.replace('PRIMARY_', '').replace('_', ' ')}): relative WIS {p_['rel_wis']:.3f} "
                   f"(95% CI {ci[0]:.3f}–{ci[1]:.3f}), {p_.get('n_country_seasons', '?')} country-seasons, "
                   f"{p_.get('n_cells', '?')} forecasts. Below 1 = better than persistence.")
        if v or txt:
            good = str(v).strip().upper() in {"MET", "PASS", "SUCCESS"}
            st.markdown(f'<div class="{"nabd-verdict-good" if good else "nabd-verdict-bad"}" style="font-size:1.1rem">'
                        + (f'<span class="nabd-pill {"nabd-pill-good" if good else ""}">{v}</span>' if v else "")
                        + f'{txt or ""}</div>', unsafe_allow_html=True)
        inc = summary.get("included_countries")
        if inc:
            st.markdown(f"**Included countries (by the pre-declared rule):** {', '.join(inc)}. Countries that failed the "
                        "inclusion rule are listed in the inclusion table below.")
        wins = summary.get("season_wins_v1_vs_persistence")
        if isinstance(wins, dict):
            st.markdown("**Seasons where the frozen UAE method beat persistence:** "
                        + "; ".join(f"{k} {v_}" for k, v_ in wins.items()) + ".")
        rows = [{"comparison": _gcc_label(k), "rel_wis": d.get("rel_wis"), "ci95_low": (d.get("ci95") or [None, None])[0],
                 "ci95_high": (d.get("ci95") or [None, None])[1], "country_seasons": d.get("n_country_seasons"),
                 "forecasts": d.get("n_cells")} for k, d in res.items() if isinstance(d, dict) and "rel_wis" in d]
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Shown verbatim from results/gcc/summary.json. WHO FluNet values are final, revised data "
                   "(no vintages exist), so this is retrospective, but the method, rules and inclusion criteria were "
                   "locked before the data was downloaded (docs/PREREG-GCC.md).")
        for fig in figs:
            st.image(str(fig), caption=fig.name)
        if "per_country" in tabs:
            st.markdown("**Per country (mean WIS; ratio below 1 = better than the comparator)**")
            st.dataframe(tabs["per_country"], hide_index=True, width="stretch")
        for name, df in tabs.items():
            if name == "per_country":
                continue
            with st.expander(f"Table: {name}"):
                st.dataframe(df, hide_index=True, width="stretch")
        with st.expander("summary.json"):
            st.json(summary, expanded=False)

elif page == "nav_ledger":
    rounds, scored, l_demo = data_io.load_ledger(observed)
    if l_demo:
        demo_banner()
    st.subheader(t("nav_ledger", lang))
    st.markdown("Every forecast round is committed **before** its target weeks are published. The hash below is "
                "recomputed from the file now and must match the recorded hash. Timestamps are self-attested until "
                "the repository is pushed publicly and the manifest is anchored outside the team (see ledger/README.md).")
    st.dataframe(rounds[[c for c in ["model", "issued_utc", "hash_matches", "git_commit_time", "sha256", "round_file"]
                         if c in rounds.columns]], hide_index=True, width="stretch")
    st.caption("hash_matches = recomputed SHA-256 equals the hash recorded at issue.")
    if not scored.empty:
        sc = scored.copy()
        for c in ("q10", "median", "q90"):
            sc[c] = pd.to_numeric(sc[c], errors="coerce").round(1)
        sc.insert(0, "model", sc.round_file.str.extract(r"Z_(.+)\.csv$")[0])
        sc = sc.drop(columns=["round_file"])
        sc["status"] = sc.inside_80pct_band.map({True: "inside 80% band", False: "outside 80% band", None: "awaiting data"})
        st.dataframe(sc, hide_index=True, width="stretch")
        n = sc.inside_80pct_band.notna().sum()
        if n:
            st.metric("Scored points inside 80% band", f"{int(sc.inside_80pct_band.sum())}/{int(n)}")
        st.caption("The ledger is an integrity device, not statistical evidence: counts at submission are small.")

elif page == "nav_ablation":
    st.subheader(t("nav_ablation", lang))
    st.markdown("What does each signal family add, and what happens when a feed is missing? The UAE model is re-run "
                "without one feed at a time (same leave-one-season-out protocol), and the change in score is shown.")
    abl = data_io.load_uae_ablation()
    if abl is None or abl.empty:
        not_computed("UAE feed-removal ablation", "results/uae/tables/ablation.csv")
    else:
        FEED_TXT = {"CORE": "recent change", "CLIM": "seasonal climatology", "TV": "testing volume",
                    "NS": "non-sentinel (hospital lab) positivity", "CAL": "school calendar and Ramadan"}
        a = abl.copy()
        a["delta"] = pd.to_numeric(a["delta"], errors="coerce")
        a["full"] = pd.to_numeric(a.get("full"), errors="coerce")
        a["pct_change"] = 100 * a["delta"] / a["full"]
        a["feed_label"] = a.feed.map(lambda f: f"{f}: {FEED_TXT[f]}" if f in FEED_TXT else str(f))
        series = list(pd.unique(a["series"])) if "series" in a.columns else [None]
        sel = st.radio("Series", series, horizontal=True) if series != [None] else None
        g = a[a.series == sel] if sel is not None else a
        metric = str(g["metric"].iloc[0]) if "metric" in g.columns else "score"
        g = g.assign(effect=np.where(g.delta > 0, "worse without (feed helped)", "better or equal without (feed did not help)"))
        ch = alt.Chart(g).mark_bar().encode(
            y=alt.Y("feed_label:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320)),
            x=alt.X("delta:Q", title=f"change in {metric} without the feed"),
            color=alt.Color("effect:N", scale=alt.Scale(domain=["worse without (feed helped)", "better or equal without (feed did not help)"],
                                                     range=[TEAL, "#94a3b8"])),
            tooltip=["feed", "kind", "full", "without", alt.Tooltip("delta:Q", format="+.3f"),
                     alt.Tooltip("pct_change:Q", format="+.1f")]).properties(height=40 * max(len(g), 3))
        st.altair_chart(ch, width="stretch")
        for r in g.itertuples():
            if pd.isna(r.delta):
                continue
            verdict = "the forecast gets worse, so the feed helps" if r.delta > 0 else "the forecast does not get worse, so the feed adds nothing measurable here"
            st.markdown(f"- **{r.feed_label}** ({getattr(r, 'kind', '')}): {metric} {r.full:.3f} → {r.without:.3f} "
                        f"({r.delta:+.3f}, {r.pct_change:+.1f}%): {verdict}.")
        st.caption("For WIS, lower is better: a positive change means the forecast is worse without that feed. "
                   "Four seasons only; small differences are within noise. Feeds that do not help are reported, not hidden.")
        with st.expander("Full table"):
            st.dataframe(abl, hide_index=True, width="stretch")

elif page == "nav_shape":
    st.subheader(t("nav_shape", lang))
    st.markdown("**Season timing and shape change from year to year.** WHO FluNet UAE sentinel positivity for every "
                "complete season in our data, aligned on the season start (ISO week 27), with this season and NABD's "
                "latest issued forecast overlaid. Some seasons look alike (this season's flu peak is close to last "
                "season's); the point is that you cannot know in advance which shape you will get.")
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    pb = load_playbook()
    which = st.radio("Series", ["rsv", "flu"], horizontal=True, format_func=lambda c: t(c, lang))
    target = data_io.UAE_TARGETS[which]
    seasons = data_io.season_frame(observed, which)
    thr = (cardcheck.tier_thresholds(pb, target, "ARE") or [None])[0]
    cur = seasons.season.max()
    seasons["this season"] = np.where(seasons.season == cur, "this season", "earlier seasons")
    f = fan_frame(fc, target)
    f = _qcols(f)
    f["x"] = [data_io.season_week_index(pd.Timestamp(d).date()) for d in f.target_end_date]
    base = alt.Chart(seasons).encode(x=alt.X("x:Q", title="Weeks since season start (ISO week 27)",
                                             scale=alt.Scale(domain=[0, 52])))
    lines = base.mark_line(point=alt.OverlayMarkDef(size=12)).encode(
        y=alt.Y("value:Q", title="sentinel positivity (%)"),
        color=alt.Color("label:N", title="season", scale=alt.Scale(scheme="tableau10")),
        strokeWidth=alt.condition(alt.datum.season == int(cur), alt.value(4), alt.value(1.6)),
        tooltip=["label:N", "ISO_WEEK:Q", alt.Tooltip("value:Q", format=".1f")])
    band = alt.Chart(f).mark_area(opacity=0.25, color=TEAL).encode(x="x:Q", y="q100:Q", y2="q900:Q")
    med = alt.Chart(f).mark_line(color=TEAL, strokeDash=[5, 3], strokeWidth=3).encode(x="x:Q", y="q500:Q")
    layers = lines + band + med
    if thr is not None:
        layers += alt.Chart(pd.DataFrame({"y": [thr]})).mark_rule(color=ROSE, strokeDash=[3, 3]).encode(y="y:Q")
    st.altair_chart(layers.properties(height=380), width="stretch")
    st.caption(f"Thick line: this season. Teal dashed line and band: NABD forecast median and 80% band issued "
               f"{issue.isoformat()} (model {meta.get('model')}). Red rule: first playbook threshold"
               + (f" ({thr:g}%)" if thr is not None else "") + ". Sentinel positivity is share of tests positive, not admissions.")
    st.markdown("#### Season by season")
    st.dataframe(data_io.season_stats(seasons, thr), hide_index=True, width="stretch")
    st.caption("Peak and onset weeks are ISO weeks. 'First week ≥ threshold' uses the playbook's first tier threshold. "
               "The current season is incomplete. Context only: NABD does not claim to predict onset earlier than a "
               "threshold on the latest counts (Alerts page).")

elif page == "nav_scenario":
    st.markdown('<div class="nabd-sim">SCENARIO · NOT A FORECAST OF ADMISSIONS · سيناريو</div>', unsafe_allow_html=True)
    st.subheader(t("nav_scenario", lang))
    st.markdown("What could the RSV forecast mean in paediatric bed-days for **one hospital**? This page translates "
                "NABD's sentinel RSV positivity forecast into an **illustrative** range, under an assumption you can "
                "see and change. It is **not validated**: no Abu Dhabi hospital data are used. A pilot would replace "
                "the assumption with the hospital's own census.")
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    c1, c2, c3 = st.columns(3)
    annual = c1.number_input("Baseline RSV admissions per year (children ≤5)", 50, 3000, 438, step=10,
                             help="Default 438 = 2,189 RSV admissions over 2018–2022 at Tawam Hospital, Al Ain "
                                  "(research/burden.md §1), divided by 5 years. Years were very uneven.")
    los = c2.slider("Mean length of stay (days)", 3.0, 7.0, 4.0, 0.1,
                    help="Sourced range 4–6 days (research/positioning.md [S1][S3]); Tawam infants under 6 months "
                         "averaged 5.8 days. Default is the conservative 4.0.")
    cost = c3.number_input("Cost per admission (US$)", 0, 20000, 2241, step=50,
                           help="Default US$2,241 = median RSV hospitalisation cost, Dubai insurance claims 2014–23 "
                                "(research/positioning.md [S3]). Optional.")
    sc = data_io.rsv_scenario(observed, fc[fc.target == data_io.UAE_TARGETS["rsv"]], issue, annual, los, cost, meta=meta)
    st.markdown(f"**Assumption (unvalidated):** weekly admissions = annual baseline × this week's sentinel RSV "
                f"positivity ÷ the average seasonal sum of weekly positivity ({sc.attrs['season_sum']:.0f} "
                f"percentage-point-weeks over {sc.attrs['n_seasons']} complete seasons). Bed-days = admissions × length of stay.")
    st.dataframe(sc.drop(columns=["target_end_date"]), hide_index=True, width="stretch")
    st.caption("Ranges are the forecast's 10%–90% band carried through the same arithmetic. Positivity is national "
               "sentinel data, not one hospital's catchment, so the scale is illustrative only. Nothing on this page is a "
               "claim about any real hospital's occupancy.")

elif page == "nav_planner":
    st.markdown('<div class="nabd-sim">SCENARIO / SIMULATED · NOT A FORECAST OF ADMISSIONS OR ABSENCE · سيناريو</div>',
                unsafe_allow_html=True)
    st.subheader(t("nav_planner", lang))
    st.markdown("**Population forecast → workforce consequence.** What could this week's RSV forecast mean for one "
                "hospital's paediatric beds **and** its own nursing roster over the next three weeks? Every number below "
                "is a **SCENARIO** built from NABD's sentinel RSV positivity forecast and inputs **you** set. No Abu Dhabi "
                "hospital or HR data are used. A pilot would replace each input with the hospital's own aggregates "
                "(docs/PILOT-DATA-SPEC.md).")
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    st.markdown("##### Demand inputs")
    d1, d2, d3, d4 = st.columns(4)
    annual = d1.number_input("RSV admissions per year (children ≤5)", 10, 3000, planner.SOURCED_DEFAULTS["annual_admissions"],
                             step=10, help="Sourced default 438 = 2,189 RSV admissions over 2018–2022 at Tawam Hospital, "
                                           "Al Ain (research/burden.md), ÷ 5 years. Replace with your own.")
    los = d2.slider("Mean length of stay (days)", 3.0, 7.0, planner.SOURCED_DEFAULTS["los_days"], 0.1,
                    help="Sourced range 4–6 days (research/positioning.md [S1][S3]). Default is the conservative 4.0.")
    beds = d3.number_input("Paediatric respiratory beds (ILLUSTRATIVE default)", 1, 500, 40, step=1,
                           help="Illustrative placeholder. Set to your ward's real capacity.")
    cost = d4.number_input("Cost per admission (US$)", 0, 20000, planner.SOURCED_DEFAULTS["cost_usd"], step=50,
                           help="Sourced default US$2,241 = median RSV hospitalisation cost, Dubai insurance claims "
                                "(research/positioning.md [S3]). Shown in AED at the fixed peg 3.6725.")
    st.markdown("##### Workforce inputs (the hospital's own)")
    w1, w2, w3, w4 = st.columns(4)
    nurses = w1.number_input("Paediatric nursing headcount (ILLUSTRATIVE default)", 0, 2000, 80, step=5)
    shifts = w2.number_input("Shifts per nurse per week", 1.0, 7.0, 4.0, 0.5,
                             help="Illustrative placeholder; use your roster pattern.")
    spare = w3.number_input("Bank/float shifts available per week", 0, 500, 10, step=1,
                            help="Illustrative placeholder; your cover capacity.")
    src = w4.radio("Absence-rate source", ["Enter my HR figure", "SIMULATED module"], index=1,
                   help="No UAE sickness-absence statistic is cited as fact. Either type your own HR average or use "
                        "the clearly SIMULATED secure-aggregation module.")
    rate = None
    if src == "Enter my HR figure":
        pct = st.number_input("Average weekly respiratory sickness-absence rate across the year, % of staff "
                              "(set by partner HR; no default figure)", 0.0, 20.0, 0.0, 0.1)
        rate = pct / 100 if pct > 0 else None
        if rate is None:
            st.info("Enter your HR figure to see the workforce columns. NABD supplies no absence statistic.")
    else:
        sim_watermark()
        tbl, _ = secure_aggregate(synthetic_employers(n_employers=60), k=10)
        rate = planner.simulated_absence_rate(tbl)
        st.caption(f"SIMULATED: weekly respiratory absence rate {rate:.2%} from synthetic employers released through "
                   "k ≥ 10 secure aggregation (Workforce page). Not a real statistic." if rate is not None else
                   "SIMULATED module released no cell at k = 10.")
    driver = st.radio("Staff absence follows", list(planner.DRIVERS), index=0, horizontal=True,
                      format_func=lambda k: planner.DRIVER_LABEL[k],
                      help="Which forecast drives the staff-absence scenario. Default: flu and RSV with equal weight. "
                           "Adult staff absence plausibly follows influenza more than paediatric RSV; RSV alone is "
                           "offered for comparison. An assumption, not a validated model.")
    plan = planner.winter_plan(observed, fc[fc.target == data_io.UAE_TARGETS["rsv"]], issue, annual_admissions=annual,
                               los_days=los, beds=int(beds), nurses=int(nurses), absence_rate_avg=rate,
                               shifts_per_nurse_week=float(shifts), spare_shifts_week=float(spare), cost_usd=float(cost),
                               meta=meta, fc_flu=fc[fc.target == data_io.UAE_TARGETS["flu"]], absence_driver=driver)
    st.markdown("##### Weekly plan (SCENARIO: 10% – median – 90% of the forecast carried through the same arithmetic)")
    st.markdown("**Demand: beds and cost** (SCENARIO)")
    st.dataframe(plan[[c for c in planner.DEMAND_COLS if c in plan.columns]], hide_index=True, width="stretch")
    st.markdown("**Workforce: nursing roster** (SCENARIO; absence rate " + ("from your HR figure" if src == "Enter my HR figure" else "SIMULATED") + ")")
    if all(c in plan.columns for c in planner.WF_COLS):
        st.dataframe(plan[["week", "weeks after issue"] + planner.WF_COLS], hide_index=True, width="stretch")
    else:
        st.info("Workforce columns need an absence rate: enter your HR figure, or choose the SIMULATED module.")
    st.markdown(f"**Assumptions (unvalidated, shown so you can challenge them).** Weekly admissions = annual admissions × "
                f"this week's sentinel RSV positivity ÷ {plan.attrs['season_sum']:.0f} (the average seasonal sum of weekly "
                f"positivity over {plan.attrs['n_seasons']} complete UAE seasons). Beds occupied = admissions × length of stay "
                f"÷ 7. Staff absence = the hospital's own average rate × a driver index ({planner.DRIVER_LABEL[driver]}): "
                f"each pathogen's forecast positivity ÷ its own seasonal average (1 = an average week); for 'both', the two "
                f"indices are averaged level by level, which assumes they move together. Shifts at risk = absent nurses × shifts per nurse. Net roster gap = shifts "
                f"at risk − bank/float shifts, floored at 0. P(gap > 0) is read from the forecast quantiles. AED at 3.6725 per US$.")
    pb = load_playbook()
    res = cardcheck.build_card(pb, data_io.UAE_TARGETS["rsv"], "ARE", fc[fc.target == data_io.UAE_TARGETS["rsv"]],
                               observed["rsv"], issue)
    if res.renderable and "occupational_health" in res.band["actions"]:
        st.markdown(f"##### {pb['roles']['occupational_health'][lang]}: proposed action (ILLUSTRATIVE playbook)")
        st.markdown(f'<div class="nabd-card"><b>{cardcheck.band_label(res.band, lang)}</b><br>'
                    f'{res.band["actions"]["occupational_health"][lang]}</div>', unsafe_allow_html=True)
        st.caption("Same band as the weekly card (G14-checked). Approve, modify or dismiss it on the weekly card "
                   "(choose the occupational-health role).")
    st.caption("How real absence counts would arrive in a pilot: employers' weekly counts via k-anonymous secure "
               "aggregation (Workforce page, SIMULATED today). Nothing on this page is a claim about any real hospital.")

elif page == "nav_workforce":
    sim_watermark()
    st.subheader(t("nav_workforce", lang))
    st.markdown("Synthetic employers report weekly respiratory sickness-absence counts. Each count is split into "
                "additive secret shares across three non-colluding servers, so **no server sees any employer's number**. "
                "A district total is released only if at least *k* employers contributed. **This module uses synthetic "
                "data only and feeds no forecast.**")
    k = st.slider("k (minimum employers per released cell)", 3, 25, 10)
    n = st.slider("Synthetic employers", 20, 200, 60, step=10)
    emp = synthetic_employers(n_employers=n)
    table, one_server = secure_aggregate(emp, k=k)
    table["status"] = table.released.map({True: "released", False: f"SUPPRESSED (<{k} employers)"})
    st.dataframe(table.drop(columns=["released"]), hide_index=True, width="stretch")
    with st.expander("What one aggregation server sees (random-looking share sums)"):
        st.dataframe(pd.DataFrame(one_server), hide_index=True)
    sim_watermark()

else:
    st.subheader(t("nav_about", lang))
    st.markdown("""
**What NABD is.** Every winter RSV and influenza drive paediatric admissions in Abu Dhabi (one hospital, Tawam,
recorded 2,189 RSV admissions of children aged 5 and under in 2018–22), and their timing and shape change from year
to year. To our knowledge, no public forecast of how big or how long exists for the UAE. NABD is an open forecasting hub:
probabilistic RSV and influenza forecasts from WHO FluNet surveillance (coverage checked and reported), the chance of
crossing each pressure threshold, and playbook actions that a named person must approve. It is the forecast layer that Abu Dhabi's existing detection systems
(Tableegh/Malaffi notifications, UMOC early warning, Rasid) could host. It does not replace them.

**Evidence, in order.** (1) An out-of-sample test on Oman, Qatar and Saudi Arabia, with the plan locked in our git
history before their data were downloaded (self-attested until externally timestamped): influenza forecast error 46%
lower than past-season patterns and 9% lower than last-week persistence (GCC page). (2) The US benchmark: NABD missed
our pre-set bar against the CDC FluSight ensemble; among single hub models it ranked 7th of 21 in 2024/25 and 19th of
25 in 2025/26 (US proof page). (3) The UAE's own four-season record: parity with persistence forward-in-time.
(4) The live, hashed forecast ledger (Ledger page), local until pushed and externally timestamped: the pilot ask.

**What NABD does not claim.**
- It does not warn of surge *onset* earlier than a simple threshold on the latest counts (median lead about 0 weeks).
- It did **not** meet its pre-registered US bar (non-inferiority to the CDC FluSight ensemble).
- The 21–36% error reduction seen in the CDC archive is the **CDC ensemble's**, not NABD's.
- No ED, weather or geospatial signal is used by any scored model. No online calibration (ACI) is used. The
  foundation model was not run.
- The multi-signal UAE v2 did **not** improve on v1, and the leave-one-season-out UAE results are context only.
- No SEHA operational numbers, ED volumes or bed occupancy. The bed-days page is a labelled scenario.
- No workforce-absence figures: that module is SIMULATED.
- No crisis framing: DoH has described this season as similar to the previous two.
- NABD does not predict the nirsevimab immunisation window. Season-shape context is context only.
- Tableegh, UMOC and Rasid are not inadequate: NABD adds a forecast layer they can host.
""")
    uae = data_io.load_uae_summary() or {}
    has = lambda p: (ROOT / p).exists()  # noqa: E731
    explain_built = has("results/uae/explain") and any((ROOT / "results/uae/explain").glob("*.csv"))
    rows = [
        ("WHO FluNet UAE sentinel flu and RSV positivity", "REAL", "data/raw (cached WHO FluNet)"),
        ("NABD-UAE v1 forecasts: forward-in-time parity with persistence (n = 4 seasons); LOSO as context", "REAL", "results/uae/"),
        ("NABD-UAE v2 multi-signal challenger (did not improve on v1)", "REAL, reported not promoted", "results/uae/SUMMARY-v2.md"),
        ("Exceedance probabilities on the card (chance of crossing each threshold)", "REAL", "app/cardcheck.py"),
        ("Season-shape view (this season vs the last 4)", "REAL", "Season shape page"),
        ("Paediatric bed-days translator", "SCENARIO (unvalidated assumption, sourced inputs)", "Bed-days scenario page"),
        ("US back-test vs the CDC FluSight ensemble (verdict NOT MET)", "REAL", "results/summary.json"),
        ("Live forecast ledger round with SHA-256", "REAL (local until pushed and anchored)", "ledger/"),
        ("Hash-chained audit log of approve/modify/dismiss decisions", "REAL", "app/audit/audit.jsonl"),
        ("Card consistency gate (band, direction and action must agree)", "REAL", "app/cardcheck.py"),
        ("Per-signal explanations (UAE)", "REAL" if explain_built else "NOT YET COMPUTED", "results/uae/explain/"),
        ("Feed-removal ablation (UAE)", "REAL" if has("results/uae/tables/ablation.csv") else "NOT YET COMPUTED",
         "results/uae/tables/ablation.csv"),
        ("GCC out-of-sample test", "REAL" if has("results/gcc/summary.json") else "NOT YET COMPUTED", "results/gcc/"),
        ("League table among CDC hub models", "REAL" if list((ROOT / "results/tables").glob("league*.csv")) else "NOT YET COMPUTED",
         "results/tables/league*.csv"),
        ("Weather inputs (Abu Dhabi)", "USED" if any("weather" in str(x).lower() for x in (uae.get("signals") or []))
         else "NOT USED (not obtainable in the build environment)", "adapters/weather"),
        ("Playbook thresholds and actions", "ILLUSTRATIVE (not reviewed by a clinician or official)", "playbook/playbook.yaml"),
        ("Employer sickness-absence feed (secure aggregation)", "SIMULATED (synthetic data, feeds no forecast)", "app/workforce.py"),
        ("Abu Dhabi hospital, district or daily data", "NOT BUILT (pilot only)", "n/a"),
        ("Chronos-2 foundation model", "NOT RUN (weights unavailable here; reported only if run)", "models/chronos2.py"),
        ("Online calibration (ACI)", "NOT USED in v1", "models/config.yaml"),
        ("ED syndromic / geospatial inputs for NABD", "NOT BUILT", "n/a"),
    ]
    st.markdown("#### What's real / simulated / not built")
    st.dataframe(pd.DataFrame(rows, columns=["component", "status", "where"]), hide_index=True, width="stretch")
    st.markdown("""
**Other limitations.** UAE evaluation covers only 4 seasons (2022/23 is low-volume). WHO FluNet data are used for
public-health evaluation only (non-commercial terms); a hospital product would run on the hospital's own data.
Publication lags are estimates (FluNet: 7 days measured on 8 Nov; skill is measured at a conservative 11-day lag; NHSN weekly). The ledger has few scored points at submission:
it is an integrity device, not statistical evidence.

**Card rules (playbook v0.4, illustrative).** For every future target week, the card computes the chance of exceeding each
playbook threshold from the issued forecast quantiles. The action uses the highest threshold with at least a 30%
chance in any of the next three target weeks, plus the forecast path (furthest median vs the last value: rising ≥ 1.15×,
falling ≤ 0.87×). Probabilities at the edge of the forecast are shown as <1% / >99%. Direction labels need at least 60%
probability (otherwise "uncertain"). "Stable" means within ±10% (minimum 1 percentage point) of the last published value.
The observed 3-week trend is shown as context only. Every card is re-checked; a contradictory card cannot render an
action.

**Governance.** Aggregate data only; adapters reject person-level fields. Every decision is written to an append-only,
hash-chained audit log. Simulated layers carry a permanent watermark.
""")
