"""NABD Streamlit app. Run:  streamlit run app/streamlit_app.py

Reads only interface-contract paths (docs/BUILD-SPEC.md v1.1); shows a DEMO DATA banner
whenever any panel falls back to app/demo_data.py.
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

from app import audit, data_io  # noqa: E402
from app.i18n import t  # noqa: E402
from app.workforce import secure_aggregate, synthetic_employers  # noqa: E402
from playbook.validate import load_playbook, match_band  # noqa: E402

TEAL, SLATE, SAND, ROSE = "#1f7a8c", "#334155", "#e2d4b7", "#b4505b"

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
  {"section.main .block-container, .stMarkdown, .stRadio, .stSelectbox, .stTextInput {direction: rtl; text-align: right;}" if rtl else ""}
</style>""", unsafe_allow_html=True)

PAGES = ["nav_card", "nav_us", "nav_ledger", "nav_ablation", "nav_workforce", "nav_about"]
page = st.sidebar.radio("Page", PAGES, format_func=lambda k: t(k, lang))
st.sidebar.caption("NABD prototype · Future Health Digital Innovation Challenge 2026 · Statement 06")

st.title(t("title", lang))
st.caption(t("subtitle", lang))


def demo_banner():
    st.markdown(f'<div class="nabd-banner"><b>⚠ {t("demo_banner", lang)}</b></div>', unsafe_allow_html=True)


def sim_watermark():
    st.markdown(f'<div class="nabd-sim">{t("simulated", lang)} · {t("simulated", "en" if rtl else "ar")}</div>',
                unsafe_allow_html=True)


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


def fan_chart(col: str, target: str, fc: pd.DataFrame, pers: pd.DataFrame, issue: dt.date):
    hist = observed[["week_end", col]].dropna().tail(26).rename(columns={col: "value"})
    hist["week_end"] = pd.to_datetime(hist.week_end)
    f = fan_frame(fc, target)
    f["target_end_date"] = pd.to_datetime(f.target_end_date)
    f["horizon"] = [data_io.horizon_label(d.date(), issue) for d in f.target_end_date]
    p = fan_frame(pers, target)
    p["target_end_date"] = pd.to_datetime(p.target_end_date)
    base = alt.Chart(f).encode(x=alt.X("target_end_date:T", title="Week ending"))
    band95 = base.mark_area(opacity=0.18, color=TEAL).encode(y=alt.Y("0.025:Q", title="%"), y2="0.975:Q")
    band80 = base.mark_area(opacity=0.35, color=TEAL).encode(y="0.1:Q", y2="0.9:Q")
    med = base.mark_line(color=TEAL, strokeWidth=3, point=True).encode(
        y="0.5:Q", tooltip=[alt.Tooltip("target_end_date:T", title="week end"), "horizon:N",
                            alt.Tooltip("0.1:Q", format=".1f"), alt.Tooltip("0.5:Q", format=".1f"),
                            alt.Tooltip("0.9:Q", format=".1f")])
    pers_line = alt.Chart(p).mark_line(color=SLATE, strokeDash=[6, 4]).encode(x="target_end_date:T", y="0.5:Q")
    h = alt.Chart(hist).mark_line(color=SLATE, point=alt.OverlayMarkDef(size=18)).encode(
        x="week_end:T", y="value:Q", tooltip=[alt.Tooltip("week_end:T"), alt.Tooltip("value:Q", format=".1f")])
    issue_rule = alt.Chart(pd.DataFrame({"d": [pd.Timestamp(issue)]})).mark_rule(color=ROSE, strokeDash=[2, 2]).encode(x="d:T")
    return (band95 + band80 + h + pers_line + med + issue_rule).properties(height=300)


def drivers(col: str) -> list[str]:
    s = observed.dropna(subset=[col])
    last3 = s[col].tail(3).round(1).tolist()
    spec = s.specimens.tail(2).tolist()
    spec_chg = 100 * (spec[-1] - spec[0]) / spec[0] if spec[0] else 0
    hist_peak = (observed.assign(season=np.where(observed.ISO_WEEK >= 27, observed.ISO_YEAR, observed.ISO_YEAR - 1))
                 .dropna(subset=[col]).groupby("season").apply(lambda g: int(g.loc[g[col].idxmax(), "ISO_WEEK"]),
                                                              include_groups=False))
    out = [f"Last 3 weeks: {' → '.join(map(str, last3))}%",
           f"Testing volume change (last week): {spec_chg:+.0f}%" + (" ⚠ >30%: interpret positivity with care" if abs(spec_chg) > 30 else ""),
           f"Past seasonal peak weeks (ISO): {', '.join(map(str, hist_peak.tolist()[-4:]))}",
           "School term in session since 31 Aug 2026 (UAE MoE calendar)"]
    return out


# ------------------------------------------------------------------ pages
if page == "nav_card":
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    fr = data_io.freshness(observed)
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    c1, c2, c3 = st.columns([2, 2, 3])
    c1.metric(t("last_week", lang), fr["last_week"])
    c2.metric(t("lag", lang), f'{fr["lag_days"]} {t("days", lang)}', f'{t("expected", lang)} ~{fr["expected_lag_days"]}', delta_color="off")
    badge = "nabd-badge-warn" if fr["stale"] else "nabd-badge-ok"
    c3.markdown(f'<br><span class="{badge}">{t("freshness", lang)}: {t("stale" if fr["stale"] else "fresh", lang)}</span>'
                f'<br><small>Issued {issue.isoformat()} · model: <b>{meta.get("model")}</b> · source: {meta.get("source")}'
                + (f'<br>round <code>{meta["round_file"]}</code> · SHA-256 <code>{meta["sha256"][:16]}…</code>' if meta.get("round_file") else "")
                + '</small>', unsafe_allow_html=True)

    pb = load_playbook()
    for col in ("rsv", "flu"):
        target = data_io.UAE_TARGETS[col]
        st.subheader(t(col, lang))
        left, right = st.columns([3, 2])
        with left:
            st.altair_chart(fan_chart(col, target, fc, pers, issue), width="stretch")
            st.caption(f"Teal: forecast median with 80% / 95% bands · dashed slate: {t('persistence', lang)} · red rule: issue date")
            f = fan_frame(fc, target)
            pe = fan_frame(pers, target)
            tbl = pd.DataFrame({
                t("horizon", lang): [data_io.horizon_label(d, issue) for d in f.target_end_date],
                "week end": f.target_end_date.astype(str),
                t("median", lang): f[0.5].round(1),
                t("band80", lang): [f"{a:.1f}–{b:.1f}" for a, b in zip(f[0.1], f[0.9])],
                t("persistence", lang): pe[0.5].round(1).values[:len(f)],
            })
            st.dataframe(tbl, hide_index=True, width="stretch")
        with right:
            st.markdown(f"**{t('drivers', lang)}** <small>(descriptive context, not model attributions)</small>", unsafe_allow_html=True)
            for d in drivers(col):
                st.markdown(f"- {d}")
            # Band rule on the forecast median whose horizon is closest to +1.5 wk after issue.
            f["h_wk"] = [(d - issue).days / 7 for d in f.target_end_date]
            row = f.iloc[(f.h_wk - 1.5).abs().argsort().iloc[0]]
            band = match_band(pb, target, "ARE", float(row[0.5]))
            st.markdown(f"**{t('action', lang)}**")
            st.caption(f"⚠ {t('illustrative', lang)} · playbook v{pb['version']}")
            if band:
                st.markdown(f'<div class="nabd-card">Tier {band["tier"]} · band <code>{band["id"]}</code> '
                            f'(median {row[0.5]:.1f}% at {data_io.horizon_label(row.target_end_date, issue)})<br><br>'
                            f'<b>{pb["roles"]["hospital_ops"][lang]}:</b> {band["actions"]["hospital_ops"][lang]}<br>'
                            f'<b>{pb["roles"]["adphc_duty"][lang]}:</b> {band["actions"]["adphc_duty"][lang]}</div>',
                            unsafe_allow_html=True)
                with st.form(f"decide_{col}"):
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
                                              "target": target, "target_end_date": str(row.target_end_date),
                                              "median": round(float(row[0.5]), 2), "demo": is_demo},
                                playbook_version=pb["version"], valid_reason_codes=set(codes))
                            st.success(f"{t('recorded', lang)} · #{rec['seq']} · {rec['hash'][:16]}…")
                        except audit.AuditError as e:
                            st.error(str(e))
            else:
                st.info("No playbook band matches this forecast.")
    with st.expander(t("audit", lang)):
        ok, msg = audit.verify_chain()
        (st.success if ok else st.error)(msg)
        recs = audit.read_records()
        if recs:
            st.dataframe(pd.DataFrame(recs)[["seq", "ts_utc", "approver", "role", "decision", "reason_code",
                                             "band_id", "hash"]], hide_index=True, width="stretch")

elif page == "nav_us":
    summary, s_demo = data_io.load_us_summary()
    tables, t_demo = data_io.load_us_tables()
    if s_demo or t_demo:
        demo_banner()
    st.subheader(t("verdict", lang))
    st.markdown("NABD-ensemble vs CDC FluSight-ensemble on US state weekly flu admissions, vintage-correct inputs, "
                "same truth for all models; relative WIS with block-bootstrap 95% CI; non-inferiority margin 1.15. "
                "The verdict below is shown **verbatim** from `results/summary.json`.")
    verdict_key = next((k for k in summary if "verdict" in k.lower()), None)
    if verdict_key:
        st.markdown(f'<div class="nabd-card" style="font-size:1.2rem"><b>{verdict_key}:</b> {summary[verdict_key]}</div>',
                    unsafe_allow_html=True)
    st.json(summary, expanded=False)
    for name, df in tables.items():
        st.markdown(f"**{name}**")
        st.dataframe(df, hide_index=True, width="stretch")
        rel_cols = [c for c in df.columns if "rel" in c.lower() and pd.api.types.is_numeric_dtype(df[c])]
        if "horizon" in df.columns and rel_cols:
            colour = "season:N" if "season" in df.columns else alt.value(TEAL)
            ch = alt.Chart(df).mark_line(point=True).encode(x="horizon:O", y=alt.Y(f"{rel_cols[0]}:Q", scale=alt.Scale(zero=False)),
                                                           color=colour)
            ref = alt.Chart(pd.DataFrame({"y": [1.0, 1.15]})).mark_rule(strokeDash=[4, 4], color=ROSE).encode(y="y:Q")
            st.altair_chart((ch + ref).properties(height=240), width="stretch")
    for fig in data_io.list_figures():
        st.image(str(fig), caption=fig.name)

    st.divider()
    st.subheader("UAE retrospective (leave-one-season-out, n = 4 seasons)")
    uae = data_io.load_uae_summary()
    if uae is None:
        demo_banner()
        st.info("results/uae/summary.json not found yet.")
    else:
        st.caption("Shown verbatim from results/uae/summary.json. Only 4 seasons: treat as indicative, not definitive.")
        rel = uae.get("rel_wis_nabd", {})
        if rel:
            st.dataframe(pd.DataFrame([{"comparison": k, "rel_wis": v.get("rel_wis"),
                                        "ci95_low": (v.get("ci95") or [None, None])[0],
                                        "ci95_high": (v.get("ci95") or [None, None])[1],
                                        "n_reference_dates": v.get("n_reference_dates")} for k, v in rel.items()]),
                         hide_index=True, width="stretch")
        st.json(uae, expanded=False)
        for name, df in data_io.load_uae_tables().items():
            with st.expander(f"Table: {name}"):
                st.dataframe(df, hide_index=True, width="stretch")
        for fig in data_io.list_figures("uae"):
            st.image(str(fig), caption=fig.name)

elif page == "nav_ledger":
    rounds, scored, l_demo = data_io.load_ledger(observed)
    if l_demo:
        demo_banner()
    st.subheader(t("nav_ledger", lang))
    st.markdown("Every forecast round is committed publicly **before** its target weeks are published. "
                "The hash below is recomputed from the file now; it must match the recorded hash and the public commit.")
    st.dataframe(rounds, hide_index=True, width="stretch")
    if not scored.empty:
        sc = scored.copy()
        sc["status"] = sc.inside_80pct_band.map({True: "inside 80% band", False: "outside 80% band", None: "awaiting data"})
        st.dataframe(sc, hide_index=True, width="stretch")
        n = sc.inside_80pct_band.notna().sum()
        if n:
            st.metric("Scored points inside 80% band", f"{int(sc.inside_80pct_band.sum())}/{int(n)}")
        st.caption("The ledger is an integrity device, not statistical evidence: counts at submission are small.")

elif page == "nav_ablation":
    abl, a_demo = data_io.load_ablation()
    if a_demo:
        demo_banner()
    st.subheader(t("nav_ablation", lang))
    feed_col = abl.columns[0]
    feeds = abl[feed_col].tolist()
    choice = st.radio("Remove feed", feeds, horizontal=True)
    row = abl[abl[feed_col] == choice].iloc[0]
    cols = st.columns(max(1, len(abl.columns) - 1))
    for c, name in zip(cols, abl.columns[1:]):
        val = row[name]
        c.metric(name, f"{val:.3f}" if isinstance(val, (int, float, np.floating)) else str(val))
    st.dataframe(abl, hide_index=True, width="stretch")
    st.caption("Shows how much each signal family contributes: removing a useful feed should worsen WIS and widen intervals.")

elif page == "nav_workforce":
    sim_watermark()
    st.subheader(t("nav_workforce", lang))
    st.markdown("Synthetic employers report weekly respiratory sickness-absence counts. Each count is split into "
                "additive secret shares across three non-colluding servers, so **no server sees any employer's number**. "
                "A district total is released only if at least *k* employers contributed.")
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
**What NABD is.** A respiratory-season forecasting feed for Abu Dhabi: calibrated RSV and influenza forecasts with
horizons stated relative to the issue date, and playbook actions that a named human must approve.

**What NABD does not claim.**
- It does not claim to detect surge *onset* earlier than a hospital's own census. Our US tests found no onset advantage.
  It forecasts *how big and how long*.
- No Abu Dhabi hospital, district or daily data are used. Every Abu Dhabi operational claim is a pilot hypothesis.

**Honest limitations.**
1. UAE retrospective evaluation covers only 4 seasons (2022/23 is low-volume); skill estimates are uncertain.
2. Non-inferiority to the CDC FluSight-ensemble may fail; the result is pre-registered and reported either way.
3. The time-series foundation model (Chronos-2) is run off this server; its gain may be null.
4. The live ledger has few scored points at submission: it is an integrity device, not statistical evidence.
5. The occupational (workforce) signal is simulated.
6. The playbook is illustrative and has not been reviewed by a clinician or public-health official.
7. WHO FluNet data are used for public-health evaluation only (non-commercial terms); the hospital product would run on
   the hospital's own data.
8. Publication lags (FluNet ~10–11 days; NHSN weekly) are estimates.

**Governance.** Aggregate data only; adapters reject person-level fields. Every decision is written to an
append-only, hash-chained audit log. Simulated layers carry a permanent watermark.
""")
