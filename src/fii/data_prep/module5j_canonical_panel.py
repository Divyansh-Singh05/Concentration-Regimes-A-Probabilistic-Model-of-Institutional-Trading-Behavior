# [migrated from Colab: paths now come from fii.paths; see
#  scripts/migrate_colab_modules.py — research logic unchanged]
from fii.paths import VALIDATION_DATA, ISIN_MAPPING  # noqa: E402
# ============================================================================
# MODULE 5J · v3 CANONICAL PANEL + DUAL-SIDE CLOSURE  (tape AND model)
#
# Closure map (built once, applied to BOTH bhavcopy and the model states so
# they share ONE company key):
#   ccanon(k) = isin_lookup[k]                     (CA-based, class-aware)
#               else issuer terminal (latest-trading ISIN of the issuer code)
#                    IF k does not co-exist with that terminal
#                    (overlap < 180d => chain/split -> collapse)
#               else k                              (co-existing DVR/partly-
#                                                    paid & singletons: keep)
# Terminal uses LATEST TRADE DATE, not the active-list flag (5K showed the
# list is incomplete). Overlap guard keeps Bharti partly-paid separate while
# merging Tata Steel / Bajaj / Alok / Ruchi / Vaibhav / Chola fragments.
#
# Outputs: returns_panel_v3.parquet (isin = canonical), states_v3.parquet
# (cisin merged). Supersedes v2 + calibrated states for CAR work.
# ============================================================================
import datetime as dt
from collections import defaultdict
import polars as pl
from pathlib import Path

DRIVE = VALIDATION_DATA
MODELD = ISIN_MAPPING
GUARD, OVERLAP_D = 0.50, 180

v2 = pl.read_parquet(DRIVE / "returns_panel_v2.parquet")
fac = pl.read_parquet(DRIVE / "ca_adjustment_factors.parquet")
lk = pl.read_parquet(MODELD / "isin_lookup.parquet")
lkmap = dict(zip(lk["old_isin"].to_list(), lk["canonical_isin"].to_list()))
states = pl.read_parquet(MODELD / "stockday_states_calibrated.parquet")

# ---- per-ISIN date span from the tape --------------------------------------
dts = v2.group_by("isin").agg(pl.col("date").min().alias("f"),
                              pl.col("date").max().alias("l"))
first = dict(zip(dts["isin"].to_list(), dts["f"].to_list()))
last = dict(zip(dts["isin"].to_list(), dts["l"].to_list()))
panel_isins = set(v2["isin"].unique().to_list())
model_cisins = set(states["cisin"].unique().to_list())

def iss(k):
    return k[3:7] if isinstance(k, str) and len(k) >= 7 else None

# terminal per issuer code = the priced ISIN with the latest last-trade
grp = defaultdict(list)
for k in panel_isins:
    grp[iss(k)].append(k)
terminal = {c: max(m, key=lambda x: last.get(x, dt.date(1900, 1, 1)))
            for c, m in grp.items()}

def overlap_days(a, b):
    if a not in first or b not in first:
        return -99999
    lo = max(first[a], first[b]); hi = min(last[a], last[b])
    return (hi - lo).days

def ccanon(k):
    if k in lkmap:
        return lkmap[k]
    c = iss(k)
    if c not in terminal:
        return k
    T = terminal[c]
    if k == T:
        return k
    return T if overlap_days(k, T) < OVERLAP_D else k   # collapse vs co-exist

cmap = {k: ccanon(k) for k in (panel_isins | model_cisins)}
mapdf = pl.DataFrame({"k": list(cmap), "ccanon": list(cmap.values())})

# report the model-side merges (fragments unified)
merged = [(k, v) for k, v in cmap.items() if k in model_cisins and v != k]
print("model cisins remapped (fragments merged):", len(merged))
for k, v in merged:
    print(f"    {k} -> {v}")
print("tape ISINs remapped:", sum(1 for k in panel_isins if cmap[k] != k))

# ---- TAPE: apply closure, dedup, returns, factors, Gate A ------------------
p = (v2.join(mapdf, left_on="isin", right_on="k", how="left")
       .with_columns(pl.coalesce("ccanon", "isin").alias("ccanon"))
       .rename({"isin": "isin_raw"}))
p = p.with_columns((pl.col("isin_raw") == pl.col("ccanon")).alias("_c"))
n0 = p.height
p = (p.sort(["ccanon", "date", "_c", "volume"],
            descending=[False, False, True, True])
       .unique(subset=["ccanon", "date"], keep="first").drop("_c"))
print("\ntape dedup removed", n0 - p.height, "overlap rows ->", p.height)
p = p.rename({"ccanon": "isin"}).sort(["isin", "date"])
p = p.with_columns(
    (pl.col("close") / pl.col("close").shift(1).over("isin") - 1).alias("ret_cc"))

apply_ev = fac.filter(pl.col("confirmed") | pl.col("obs_ratio").is_null())
excl_ev = fac.filter(pl.col("confirmed") == False)  # noqa: E712
rows = p.select("symbol", "date").unique().sort("date")
mapd = (apply_ev.select("symbol", "ex_date", "factor").sort("ex_date")
        .join_asof(rows, left_on="ex_date", right_on="date", by="symbol",
                   strategy="forward"))
per_day = (mapd.filter(pl.col("date").is_not_null())
               .group_by("symbol", "date")
               .agg(pl.col("factor").product().alias("adj_factor")))
p = p.join(per_day, on=["symbol", "date"], how="left")
p = p.with_columns(((1 + pl.col("ret_cc"))
                    * pl.col("adj_factor").fill_null(1.0) - 1).alias("ret_adj"))
nb = p.filter(pl.col("adj_factor").is_not_null()
              & (pl.col("ret_adj").abs() > GUARD)).height
p = p.with_columns(pl.when(pl.col("adj_factor").is_not_null()
                           & (pl.col("ret_adj").abs() > GUARD)).then(None)
                   .otherwise(pl.col("ret_adj")).alias("ret_adj"))
p = p.join(excl_ev.select("symbol", pl.col("ex_date").alias("date"),
                          pl.lit(True).alias("_k")), on=["symbol", "date"],
           how="left")
p = p.with_columns(pl.when(pl.col("_k")).then(None)
                   .otherwise(pl.col("ret_adj")).alias("ret_adj")).drop("_k")
p = p.with_columns((pl.col("ret_adj") - pl.col("nifty50_ret"))
                   .alias("ret_adj_mktadj"))
print("application guard nulled:", nb)

conf = fac.filter(pl.col("confirmed") == True)  # noqa: E712
gg = conf.join(p.select("symbol", "date", "ret_adj"),
               left_on=["symbol", "ex_date"], right_on=["symbol", "date"],
               how="inner").filter(pl.col("ret_adj").is_not_null())
med = float(gg["ret_adj"].abs().median())
print("\nGATE A: confirmed ex-days", gg.height, "| median |ret_adj|",
      round(med, 4), "->", "PASS" if med < 0.05 else "FAIL")

# ---- MODEL: apply the SAME closure to states -> states_v3 ------------------
sv3 = (states.join(mapdf, left_on="cisin", right_on="k", how="left")
             .with_columns(pl.coalesce("ccanon", "cisin").alias("cisin"))
             .drop("ccanon"))
d0 = sv3.height
sv3 = sv3.unique(subset=["cisin", "TR_DATE"], keep="first")
print("\nstates: merged fragments, dropped", d0 - sv3.height,
      "overlap-day dups -> cisins now:", sv3["cisin"].n_unique(), "(was 946)")

# ---- coverage on v3 --------------------------------------------------------
j = sv3.join(p.select("isin", "date", "ret_adj_mktadj"),
             left_on=["cisin", "TR_DATE"], right_on=["isin", "date"],
             how="left")
print("\nmodel match on v3:",
      round(100 * float(j["ret_adj_mktadj"].is_not_null().mean()), 2),
      "% (v2 90.4%)")
print(j.group_by("era").agg(
    (100 * pl.col("ret_adj_mktadj").is_not_null().mean()).round(2).alias("m%"),
    pl.len().alias("n")).sort("era"))
print(j.group_by("archetype").agg(
    (100 * pl.col("ret_adj_mktadj").is_not_null().mean()).round(2).alias("m%"))
    .sort("archetype"))
print("2011 coverage (backfill sanity):",
      round(100 * float(j.filter(pl.col("TR_DATE").dt.year() == 2011)
                        ["ret_adj_mktadj"].is_not_null().mean()), 2), "%")

p.write_parquet(DRIVE / "returns_panel_v3.parquet")
sv3.write_parquet(DRIVE / "states_v3.parquet")
print("\nwrote returns_panel_v3.parquet", p.shape,
      "and states_v3.parquet", sv3.shape)
print("NEXT: point 5B-4 at returns_panel_v3 + states_v3, run END-anchor test.")
