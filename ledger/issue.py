"""Issue one frozen, hashed NABD forecast round for the UAE (sentinel flu and RSV positivity).

Adapted from eval/ledger_issue.py (baseline-v0), now using the UAE track models (uae/models.py).

Usage (from repo root):
  python3 -m ledger.issue --cached --round R0     # from data/raw/flunet_are.csv
  python3 -m ledger.issue --fetch  --round R1     # pull fresh WHO FluNet first (run locally)

Writes, per model (NABD-UAE-v1 = frozen headline; NABD-UAE-v2 = locked challenger from R1 onwards
[docs/PROTOCOL-UAE-v2.md]; persistence baseline, so judges can compare):
  ledger/<UTC>_<model>.csv         interface-contract format (FluSight-style quantiles, percent)
  ledger/<UTC>_<model>.sha256      SHA-256 of the CSV
  ledger/<UTC>_<model>.meta.json   issue time, data-through week, issue-relative horizon labels
and appends one line per file to ledger/LEDGER.md.

A round is NOT public until it is committed and pushed to a public repository and the hash is posted.
The public commit time is the timestamp. Never edit a ledger file after issue; issue a new round instead.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adapters import flunet
from uae.models import NabdUAE, Persistence, QUANTILES, SERIES, H, prepare, expit
from uae.features_v2 import prepare_v2
from uae.models_v2 import NabdUAEv2

DESIGNATION = {"NABD-UAE-v1": "headline (frozen as-is, see docs/FREEZE.md)",
               "NABD-UAE-v2": "challenger (locked, docs/LOCK-UAE-v2.json)", "persistence": "baseline"}

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger"
COLS = ["reference_date", "target", "horizon", "target_end_date", "location", "output_type", "output_type_id",
        "value", "model"]


def issue(mode="cached", round_label="R0", now=None, with_v2=True):
    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%MZ")
    raw = flunet.load(mode)
    s = flunet.sentinel_series(raw)
    written = []
    data_through = {}
    frames = {}
    meta_rows = []
    for key, (_, target_name) in SERIES.items():
        d = prepare(s, key)
        i = int(d.dropna(subset=["y"]).index.max())          # last published week L
        L_end = d.week_end.iloc[i]
        cur = int(d.season.iloc[i])
        train = sorted(x for x in d.season.dropna().unique().astype(int) if x != cur)
        # extend the frame with the 4 future calendar weeks (no data) so models know target ISO weeks
        fut = pd.DataFrame({"week_end": [L_end + pd.Timedelta(weeks=h) for h in H]})
        iso = [t.isocalendar() for t in fut.week_end]
        fut["iso_year"] = [c[0] for c in iso]
        fut["iso_week"] = [c[1] for c in iso]
        fut["season"] = np.where(fut.iso_week >= 27, fut.iso_year, fut.iso_year - 1)
        dd = pd.concat([d.iloc[: i + 1], fut], ignore_index=True)
        ref = (L_end + pd.Timedelta(days=14)).date()
        cands = [(NabdUAE, dd), (Persistence, dd)]
        if with_v2:
            d2 = prepare_v2(raw, key, extend_weeks=len(H))
            assert d2.week_end.iloc[i] == L_end
            cands.append((NabdUAEv2, d2.iloc[: i + 1 + len(H)].reset_index(drop=True)))
        for M, frame in cands:
            m = M(frame, train)
            pq = m.predict(i)
            if M is NabdUAEv2:  # G11: exact per-signal explanation of the live v2 forecast
                ex_dir = ROOT / "results" / "uae" / "explain"
                ex_dir.mkdir(parents=True, exist_ok=True)
                slug = {"flu": "flu_pos_pct_sentinel", "rsv": "rsv_pos_pct_sentinel"}[key]
                parts = []
                for h, v in m.predict_detail(i).items():
                    if v is None:
                        continue
                    e = v["explain"].copy()
                    tot = e.contribution.sum()
                    e["pp_effect_loo"] = [np.nan if f == "last_observed_logit" else
                                          100 * expit(tot) - 100 * expit(tot - c)
                                          for f, c in zip(e.feature, e.contribution)]
                    e.insert(0, "horizon", h - 2)
                    e["unit"] = "logit"
                    e["series"] = key
                    e["target"] = target_name
                    e["submodel"] = v["sub"]
                    e["median_pct"] = 100 * expit(tot)
                    e["issue_date"] = str(now.date())
                    e["target_end_date"] = str((L_end + pd.Timedelta(weeks=h)).date())
                    e["design"] = f"live ledger {round_label}"
                    parts.append(e)
                if parts:
                    pd.concat(parts, ignore_index=True).to_csv(ex_dir / f"{now.date()}_{slug}.csv", index=False)
            rows = []
            for h in H:
                if pq.get(h) is None:
                    continue
                vals = 100 * expit(np.sort(pq[h]))
                tgt_end = (L_end + pd.Timedelta(weeks=h)).date()
                for q, v in zip(QUANTILES, vals):
                    rows.append([str(ref), target_name, h - 2, str(tgt_end), "ARE", "quantile", q,
                                 round(float(v), 4), m.name])
                meta_rows.append(dict(model=m.name, target=target_name, horizon=h - 2, target_end_date=str(tgt_end),
                                      weeks_ahead_of_issue=round((pd.Timestamp(tgt_end) - pd.Timestamp(now.date())).days / 7, 1)))
            frames.setdefault(m.name, []).extend(rows)
        data_through[target_name] = f"{int(d.iso_year.iloc[i])}-W{int(d.iso_week.iloc[i]):02d}"  # per series (audit m19)
    LEDGER.mkdir(exist_ok=True)
    for name, rows in frames.items():
        df = pd.DataFrame(rows, columns=COLS)
        base = LEDGER / f"{stamp}_{name}"
        csv = base.with_suffix(".csv")
        df.to_csv(csv, index=False)
        h = hashlib.sha256(csv.read_bytes()).hexdigest()
        base.with_suffix(".sha256").write_text(f"{h}  {csv.name}\n")
        mrows = [r for r in meta_rows if r["model"] == name]
        for r in mrows:
            r["horizon_label"] = "nowcast (target week already ended at issue)" if r["weeks_ahead_of_issue"] <= 0 \
                else f"+{r['weeks_ahead_of_issue']} wk after issue"
        meta = dict(round=round_label, issued_utc=now.isoformat(timespec="seconds"), model=name,
                    data_source="WHO FluNet xMart live" if mode == "fetch" else "data/raw/flunet_are.csv (cached)",
                    data_through_week=data_through, designation=DESIGNATION.get(name, ""), sha256=h, horizons=mrows,
                    public=False, note="Not public until committed, pushed to a public repo, and the hash is posted.")
        base.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
        with open(LEDGER / "LEDGER.md", "a") as f:
            f.write(f"| {round_label} | {now.isoformat(timespec='seconds')} | {csv.name} | {h} | data through "
                    f"{'; '.join(f'{k}: {v}' for k, v in data_through.items())} | {meta['data_source']} |\n")
        written.append((csv, h))
    # round manifest (vendor kit): SHA-256 per file + Merkle root; MANIFEST.sha256 is what gets anchored outside
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
    from nabd_kit.ledger import build_manifest, write_manifest
    files = [c for c, _ in written] + [c.with_suffix(".meta.json") for c, _ in written] + \
            [c.with_suffix(".sha256") for c, _ in written]
    man = build_manifest([str(f.relative_to(ROOT)) for f in files], base_dir=ROOT,
                         meta=dict(round=round_label, issued_utc=now.isoformat(timespec="seconds")))
    man["base_dir"] = "."
    mj, ms = write_manifest(man, LEDGER / "rounds" / f"{stamp}_{round_label}")
    with open(LEDGER / "LEDGER.md", "a") as f:
        f.write(f"| {round_label} | {now.isoformat(timespec='seconds')} | MANIFEST (Merkle root) | "
                f"{man['merkle_root']} | {len(files)} files | anchor: {ms.relative_to(ROOT)} |\n")
    written.append((ms, man["merkle_root"]))
    return written


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--round", default="R0")
    a = ap.parse_args()
    if not (LEDGER / "LEDGER.md").exists():
        (LEDGER / "LEDGER.md").write_text("# NABD forecast ledger\n\n| Round | Issued (UTC) | File | SHA-256 | Data | Source |\n|---|---|---|---|---|---|\n")
    for csv, h in issue("fetch" if a.fetch else "cached", a.round):
        print(f"{csv.relative_to(ROOT)}  sha256={h}")
    print("Next: git add ledger && git commit -m 'ledger round' && git push  (public commit time = timestamp); post the hash.")


if __name__ == "__main__":
    main()
