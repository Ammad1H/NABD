"""The page's ledger text follows the files: scored weeks, the own-record receipt, outside timestamps."""
import pandas as pd

from web import build


def _scores(tmp_path):
    rows = []
    for f, model in [("2026-11-08T0651Z_NABD-UAE-v1.csv", "NABD-UAE-v1"), ("2026-11-14T1947Z_NABD-UAE-v1.csv", "NABD-UAE-v1"),
                     ("2026-11-14T1947Z_NABD-Pool.csv", "NABD-Pool")]:
        for tgt, obs, med, in50 in [("wk rsv pos pct sentinel", 23.02, 12.36, False), ("wk flu pos pct sentinel", 20.32, 26.91, False)]:
            rows.append(dict(file=f, model=model, target=tgt, horizon=-1, target_end_date="2026-11-08",
                             observed=obs, median=med, wis=1.0, in50=in50, in95=True))
    pd.DataFrame(rows).to_csv(tmp_path / "scores.csv", index=False)


def test_receipt_is_the_earliest_own_record_forecast_and_never_the_pooled_model(tmp_path, monkeypatch):
    _scores(tmp_path)
    monkeypatch.setattr(build, "LEDGER", tmp_path)
    monkeypatch.setattr(build, "ROOT", tmp_path)
    lg = build.ledger_block()
    assert lg["n_scored"] == 1
    r = lg["receipt"]
    assert r["week"] == "2026-W45" and r["issued"] == "2026-11-08"
    assert r["rows"]["rsv"] == dict(observed=23.0, median=12.4, in50=False, in95=True)
    assert "Pool" not in str(r)
    assert lg["anchors"] == []


def test_anchor_status_read_from_the_anchors_folder(tmp_path, monkeypatch):
    d = tmp_path / "anchors" / "2026-11-19T1700Z_all"
    d.mkdir(parents=True)
    (d / "MANIFEST.sha256.ots").write_bytes(b"x")
    (d / "manifest.tsr").write_bytes(b"x")
    monkeypatch.setattr(build, "LEDGER", tmp_path)
    monkeypatch.setattr(build, "ROOT", tmp_path)
    assert build.ledger_block()["anchors"] == [dict(stamp="2026-11-19T1700Z", ots=True, tsr=True)]


def test_no_scores_keeps_the_old_wording_path(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "LEDGER", tmp_path)
    monkeypatch.setattr(build, "ROOT", tmp_path)
    lg = build.ledger_block()
    assert lg["n_scored"] == 0 and lg["receipt"] is None
