"""SIMULATED occupational signal: employer sickness-absence counts via secure aggregation.

All data here are synthetic. The protocol demonstrated:
  1. Each employer splits its weekly respiratory-absence count into n additive secret shares
     modulo a large prime and sends one share to each of n non-colluding aggregation servers.
     A single server learns nothing about any employer's count.
  2. A district total is only released if at least k distinct employers contributed (k-anonymity
     at the employer level). Otherwise the cell is suppressed.
  3. Servers publish only their per-district share sums; adding them reconstructs the total.
"""
from __future__ import annotations

import secrets

import numpy as np
import pandas as pd

PRIME = 2_147_483_647  # 2^31 - 1
DISTRICTS = ["Abu Dhabi Island", "Mussafah", "Khalifa City", "Al Ain", "Al Dhafra"]


def synthetic_employers(n_employers: int = 60, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    district = rng.choice(DISTRICTS, size=n_employers, p=[0.32, 0.30, 0.18, 0.14, 0.06])
    staff = rng.integers(40, 2500, size=n_employers)
    rate = rng.gamma(2.0, 0.006, size=n_employers)  # weekly respiratory absence rate
    absent = rng.binomial(staff, np.clip(rate, 0, 0.2))
    return pd.DataFrame({"employer_id": [f"E{i:03d}" for i in range(n_employers)],
                         "district": district, "staff": staff, "resp_absent": absent})


def share(value: int, n_servers: int) -> list[int]:
    shares = [secrets.randbelow(PRIME) for _ in range(n_servers - 1)]
    shares.append((value - sum(shares)) % PRIME)
    return shares


def secure_aggregate(emp: pd.DataFrame, k: int = 10, n_servers: int = 3) -> tuple[pd.DataFrame, list[dict]]:
    """Return (district_table, one_server_view). The table shows released totals or SUPPRESSED."""
    if k < 1:
        raise ValueError("k must be >= 1")
    server_sums = [dict() for _ in range(n_servers)]
    staff_sums = [dict() for _ in range(n_servers)]
    counts: dict[str, int] = {}
    for _, row in emp.iterrows():
        for s, sh in enumerate(share(int(row.resp_absent), n_servers)):
            server_sums[s][row.district] = (server_sums[s].get(row.district, 0) + sh) % PRIME
        for s, sh in enumerate(share(int(row.staff), n_servers)):
            staff_sums[s][row.district] = (staff_sums[s].get(row.district, 0) + sh) % PRIME
        counts[row.district] = counts.get(row.district, 0) + 1
    rows = []
    for d in DISTRICTS:
        n = counts.get(d, 0)
        if n >= k:
            total = sum(srv.get(d, 0) for srv in server_sums) % PRIME
            staff = sum(srv.get(d, 0) for srv in staff_sums) % PRIME
            rows.append({"district": d, "employers": n, "released": True,
                         "resp_absent_total": int(total), "staff_total": int(staff),
                         "rate_per_1000": round(1000 * total / staff, 1) if staff else None})
        else:
            rows.append({"district": d, "employers": n, "released": False,
                         "resp_absent_total": None, "staff_total": None, "rate_per_1000": None})
    one_server = [{"district": d, "server_1_share_sum": server_sums[0].get(d)} for d in DISTRICTS]
    return pd.DataFrame(rows), one_server
