"""Shared schema guards for NABD adapters.

Privacy-by-construction: any column whose name looks like a person-level identifier is rejected
before data enters the pipeline. All NABD inputs are weekly/daily population aggregates.
"""
import re
import pandas as pd
import pandera.pandas as pa

# Tokens that indicate person-level data. Matched against lower-cased column names split on non-alphanumerics.
FORBIDDEN_TOKENS = {
    "id", "uid", "name", "firstname", "lastname", "patient", "patientid", "person", "emiratesid", "emirates",
    "dob", "birth", "birthdate", "mrn", "nationalid", "passport", "phone", "mobile", "email", "address",
    "employee", "employeeid", "ssn", "insurance", "gender_identity",
}
# Exact column names that are allowed even though they contain a forbidden token (aggregate keys).
ALLOWED_EXACT = {"location_id", "station_id", "country_id"}


class PersonLevelFieldError(ValueError):
    """Raised when an input frame carries a column that looks like a person-level identifier."""


def reject_person_level(df: pd.DataFrame, source: str = "input") -> pd.DataFrame:
    bad = []
    for c in df.columns:
        lc = str(c).lower()
        if lc in ALLOWED_EXACT:
            continue
        tokens = set(t for t in re.split(r"[^a-z0-9]+", lc) if t)
        squashed = re.sub(r"[^a-z0-9]", "", lc)
        if tokens & FORBIDDEN_TOKENS or squashed in FORBIDDEN_TOKENS:
            bad.append(c)
    if bad:
        raise PersonLevelFieldError(f"{source}: person-level field(s) rejected: {bad}")
    return df


FLUNET_WEEKLY = pa.DataFrameSchema(
    {
        "iso_year": pa.Column(int, pa.Check.in_range(2000, 2100)),
        "iso_week": pa.Column(int, pa.Check.in_range(1, 53)),
        "origin": pa.Column(str, pa.Check.isin(["SENTINEL", "NONSENTINEL"])),
        "specimens": pa.Column(float, pa.Check.ge(0), nullable=True),
        "flu_pos": pa.Column(float, pa.Check.ge(0), nullable=True),
        "rsv_pos": pa.Column(float, pa.Check.ge(0), nullable=True),
        "week_end": pa.Column("datetime64[ns]"),
        "season": pa.Column(int),
    },
    checks=[
        pa.Check(lambda d: (d.flu_pos.fillna(0) <= d.specimens.fillna(float("inf"))).all(),
                 error="flu positives exceed specimens"),
        pa.Check(lambda d: (d.rsv_pos.fillna(0) <= d.specimens.fillna(float("inf"))).all(),
                 error="RSV positives exceed specimens"),
    ],
    strict=True,
    unique=["iso_year", "iso_week", "origin"],
)

WEATHER_WEEKLY = pa.DataFrameSchema(
    {
        "week_end": pa.Column("datetime64[ns]"),
        "tavg_c": pa.Column(float, nullable=True),
        "tmax_c": pa.Column(float, nullable=True),
        "real": pa.Column(bool),
    },
    strict=True,
)

CALENDAR = pa.DataFrameSchema(
    {
        "start": pa.Column("datetime64[ns]"),
        "end": pa.Column("datetime64[ns]"),
        "event": pa.Column(str),
        "school_closed": pa.Column(bool),
        "verified": pa.Column(bool),
        "source": pa.Column(str),
    },
    strict=True,
)
