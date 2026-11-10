"""Frozen design constants for the 'borrowed strength' test (docs/PREREG-POOL.md, lock #1).

Country lists were written from general knowledge and public WHO-region membership BEFORE any FluNet data
beyond ARE, USA, OMN, QAT, SAU, BHR, KWT were downloaded or examined. Do not edit after lock #1.
"""
# Development countries: long-running national influenza surveillance programmes named from general knowledge
# (AMR, EUR, WPR, SEAR, AFR) plus the seven countries the project had already seen.
DEV = ["USA", "CAN", "MEX", "BRA", "ARG", "CHL", "COL", "CUB",
       "GBR", "IRL", "FRA", "DEU", "ESP", "ITA", "PRT", "NLD", "BEL", "CHE", "AUT", "NOR", "SWE", "DNK", "FIN",
       "POL", "CZE", "GRC", "TUR", "RUS", "UKR", "ROU",
       "CHN", "JPN", "KOR", "AUS", "NZL", "SGP", "MNG", "IND", "THA", "ZAF",
       "ARE", "OMN", "QAT", "SAU", "BHR", "KWT"]
ALREADY_SEEN = ["ARE", "USA", "OMN", "QAT", "SAU", "BHR", "KWT"]

# Confirmatory held-out countries (never downloaded or examined at lock #1).
HELD_EMRO = ["AFG", "DJI", "EGY", "IRN", "IRQ", "JOR", "LBN", "LBY", "MAR", "PAK", "PSE", "SOM", "SDN", "SYR",
             "TUN", "YEM"]          # every WHO-EMRO member not in DEV
HELD_OTHER = ["ISR", "GEO", "ARM", "KAZ", "UZB", "BGD", "LKA", "NPL", "IDN", "VNM", "PHL", "MYS",
              "KEN", "GHA", "SEN", "ETH", "PER", "ECU", "CRI", "PRY"]   # pre-named, other regions
HELD = HELD_EMRO + HELD_OTHER
assert not set(DEV) & set(HELD)

# Approximate capital latitude (degrees, public geography), used only as a model feature.
LAT = dict(USA=38.9, CAN=45.4, MEX=19.4, BRA=-15.8, ARG=-34.6, CHL=-33.4, COL=4.7, CUB=23.1, GBR=51.5, IRL=53.3,
           FRA=48.9, DEU=52.5, ESP=40.4, ITA=41.9, PRT=38.7, NLD=52.4, BEL=50.8, CHE=46.9, AUT=48.2, NOR=59.9,
           SWE=59.3, DNK=55.7, FIN=60.2, POL=52.2, CZE=50.1, GRC=38.0, TUR=39.9, RUS=55.8, UKR=50.5, ROU=44.4,
           CHN=39.9, JPN=35.7, KOR=37.6, AUS=-35.3, NZL=-41.3, SGP=1.3, MNG=47.9, IND=28.6, THA=13.8, ZAF=-25.7,
           ARE=24.5, OMN=23.6, QAT=25.3, SAU=24.7, BHR=26.2, KWT=29.4,
           AFG=34.5, DJI=11.6, EGY=30.0, IRN=35.7, IRQ=33.3, JOR=31.9, LBN=33.9, LBY=32.9, MAR=34.0, PAK=33.7,
           PSE=31.9, SOM=2.0, SDN=15.5, SYR=33.5, TUN=36.8, YEM=15.4,
           ISR=31.8, GEO=41.7, ARM=40.2, KAZ=51.2, UZB=41.3, BGD=23.8, LKA=6.9, NPL=27.7, IDN=-6.2, VNM=21.0,
           PHL=14.6, MYS=3.1, KEN=-1.3, GHA=5.6, SEN=14.7, ETH=9.0, PER=-12.0, ECU=-0.2, CRI=9.9, PRY=-25.3)
assert all(c in LAT for c in DEV + HELD)

EVAL_SEASONS = [2022, 2023, 2024, 2025]
EXCLUDE_TRAINING_SEASONS = [2020]
MIN_YEAR = 2015
QUALIFY = dict(min_reported_frac=0.8, min_median_specimens=20)   # same rule as the GCC test
SENTINEL_MIN_QUALIFYING_EVAL_SEASONS = 3                          # same series-choice rule as the GCC test
MIN_TRAINING_SEASONS = 2          # the local v1 method cannot be fitted on fewer own seasons
MIN_SCORED_EVAL_SEASONS = 1       # a held-out country is included if >= 1 flu evaluation season is scored
SHORT_HISTORY_MAX_OWN_SEASONS = 2
TRUNCATE_TO_SEASONS = 2           # 'simulated short record' secondary
BOOTSTRAP = dict(unit="country", B=2000, seed=0)

# Data source: WHO FluNet full export as mirrored on GitHub (the route used for the GCC test, pinned).
MIRROR_URL = ("https://raw.githubusercontent.com/sergezaugg/10_flunet_dashboard/"
              "88ff8df/{path}")
EXPORT_SHA256_PREFIX = "2ad479fa2ef50ef8"   # VIW_FNT_20261003.csv, as recorded in data/raw/PROVENANCE.md
COLUMNS = ["COUNTRY_CODE", "ISO_YEAR", "ISO_WEEK", "ORIGIN_SOURCE", "SPEC_PROCESSED_NB", "INF_ALL", "RSV"]
