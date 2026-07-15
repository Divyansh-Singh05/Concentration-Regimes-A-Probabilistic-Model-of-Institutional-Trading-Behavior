<div align="center">

# Concentration Regimes

### A Probabilistic Model of Institutional Trading Behavior

*Does foreign institutional flow move Indian equity prices permanently, or does it revert?*
*A regime-detection pipeline that answers with a pre-registered, gate-driven validation battery —*
*and reports the answer even where it contradicts the starting hypothesis.*

</div>

<br>

**Contents** · [What this is](#1--what-this-is) · [Results](#2--results) ·
[Methodology](#3--methodology-step-by-step) · [Quickstart](#4--quickstart) ·
[Repository layout](#5--repository-layout) · [Documentation](#6--documentation-map) ·
[Design decisions](#7--design-decisions-worth-knowing) · [Data note](#8--data-note) ·
[Requirements](#9--requirements)

<br>

---

## 1 · What this is

Fourteen years (2011–2025) of masked, daily, stock-level Foreign Institutional
Investor (FII) trade records from India's depository (NSDL) contain a question
every market-microstructure researcher cares about:

> **When foreign flow pushes a price, does that push contain information —
> or is it just temporary pressure that reverts?**

This repository is a fully reproducible research pipeline built to answer that
question, end to end.

<br>

**① A regime-detection model.** Unsupervised — a Hidden Markov Model, with a
challenger factorial-HMM and LightGBM — over ten leakage-safe,
cross-sectionally-ranked flow features. No price or macro data anywhere near
the model.

**② A validation battery.** 20+ stages, pre-registered, each with a PASS/FAIL
verdict declared *before* the result is computed. Event studies. Panel
regressions with fixed effects and two-way clustering. An independent
probability-of-informed-trading estimator. Walk-forward backtests with
transaction costs.

**③ Honest reporting.** Including the parts that inverted the project's own
starting hypothesis, and the parts that failed pre-registered bars. Negative
results aren't cut from the story — they're the evidence for why the
surviving claims can be trusted.

<br>

Every stage is the original, sequentially-verified research script, preserved
and executed as-is — not a rewritten summary. The full evidence trail (every
failure, every fix, every falsified prior) lives in
[`docs/research_log/`](docs/research_log/).

---

## 2 · Results

### 2.1 · The headline finding

> **Concentrated** FII selling (few institutions transacting a stock on a
> given day) is **liquidity-demanding**: prices fall alongside a volume
> climax, then **revert +49 to +109 bp over 10–60 days** once the flow
> stops. Concentrated buying mirrors it in reverse (a symmetric give-back).
> **Dispersed** FII selling (many institutions, quiet volume) is
> **information-consistent**: the decline is permanent at every horizon
> tested. An independent Easley–O'Hara PIN estimator — blind to prices and
> returns — loads **~3× more informed-trading probability onto dispersed
> selling than onto concentrated selling**, corroborating the split from a
> completely different angle.

This is the **opposite** of the project's pre-registered hypothesis
(concentrated = informed "Shark", dispersed = forced fire-sale "Hostage").
The inversion survived a full referee-style attack (§2.4) and is reported
as the finding, not hidden as a failure.

### 2.2 · Panel-regression evidence (Table 1: excess CAR, stock+date fixed effects, two-way clustered)

Coefficients in basis points, 20-day forward excess CAR, `linearmodels.PanelOLS`:

| Archetype | TRAIN coef (bp) | TRAIN t | TEST coef (bp) | TEST t |
|---|---:|---:|---:|---:|
| **SHARK_DIST** (concentrated sell) | **+65.4** | 5.35 *** | **+48.5** | 2.95 *** |
| **SHARK_ACC** (concentrated buy) | **−87.9** | −6.23 *** | **−47.6** | −2.84 *** |
| HOSTAGE (dispersed sell) | −3.6 | −0.38 ns | −8.1 | −0.48 ns |
| ROBOT (transient/index flow, placebo) | −7.7 | −0.65 ns | −38.4 †| −3.44 *** |

† ROBOT's TEST-era coefficient is a known artifact of the placebo's own
construction (post-episode = mechanical entry into the next regime), not a
sign of sell-skew — documented and superseded by HOSTAGE as the clean null.
See `docs/research_log/` §3i–3j.

The SHARK_DIST reversal / SHARK_ACC give-back holds across **all four
horizons tested (10/20/30/60 days)**, both eras, and survives: beta,
momentum, Amihud illiquidity, turnover, volatility, price-level and
episode-length controls; non-overlapping episode subsampling; a
flow-magnitude (INNOV) control; an index-reconstitution exclusion window;
and a LightGBM challenger with SHAP attribution. Full derivation:
[`docs/04_validation_framework.md`](docs/04_validation_framework.md).

### 2.3 · Regime census (out-of-sample, TEST era: Jul 2021 – Mar 2025)

| Archetype | Share of stock-days |
|---|---:|
| ROBOT (transient/index flow) | 43.6% |
| UNTAGGED_DIRECTIONAL | 35.9% |
| SHARK_DIST (concentrated sell) | 8.0% |
| SHARK_ACC (concentrated buy) | 7.0% |
| HOSTAGE (dispersed sell) | 5.6% |

### 2.4 · It survived an adversarial self-audit

Two rounds of hostile re-reading — an external-referee simulation (Module 13)
and a skeptic self-audit (Module 15) — attacked exactly the three weakest
joints in the argument:

| Objection | Test | Verdict |
|---|---|---|
| "The HMM is decoration" | Census-matched rule-based backbone reproduces Table 1 | **Confirmed** — HMM buys episode smoothness only; contribution re-ranked to (1) the identifier audit, (2) the comp[...] |
| "This is just index-reconstitution mechanics" | Exclude ±7 calendar days around 150 MSCI/FTSE/NIFTY review dates | **Passive mechanics excluded** — SHARK_DIST +61.5\*\*\*/+50.9\*\* survives |
| "It's just bid-ask bounce" | Re-run on bounce-free windows (t+3 … t+22) | Bounce = **11–24% of the headline** effect, not all of it — repriced and stated verbatim, not hidden |
| "Composition adds nothing beyond public/flow data" | LightGBM IC ladder: PUBLIC → +FLOW → +COMPOSITION | Composition adds ΔIC beyond both public data (t=5.2) and conventional flow (t=3.2) |

### 2.5 · What did *not* survive — reported honestly

- **Block/bulk-deal corroboration (Module 6): negative.** Concentrated
  selling does not coincide with visible block deals more than dispersed
  selling does — a "visibility threshold" lesson, kept in the record.
- **VIX / Kyle-λ state-dependence (Module 10): mixed/null**, not claimed.
- **Illiquid-tail extension (Module 14): no reversal effect** in the
  attributable illiquid tail — the reversal is a liquid-market phenomenon;
  the dislocation there stays permanent (a **stronger**, not weaker, form of
  limits-to-arbitrage).
- **Backtests: the signal does not clear realistic transaction costs.**
  Every strategy variant's breakeven is **2–8 bps one-way** — below what an
  institutional trader actually pays. Gross (pre-cost) diagnostics confirm
  the signal is real at the portfolio level; costs, not the model, are what
  block monetization. See [`docs/05_backtesting.md`](docs/05_backtesting.md).
- **Phase-II decision test (anticipation vs. confirmation): fails its
  pre-registered bar.** Episode-end timing is forecastable (hazard-model
  AUC 0.80 OOS vs. 0.57 for an age-only baseline) but a trivial "act once an
  episode is a few days old" rule beats the model paired. Forecastable ≠
  monetizable.

---

## 3 · Methodology, step by step

```mermaid
flowchart TD
    subgraph DP["1 · Data preparation"]
        A1[NSE bhavcopy tape] --> A2[repaired price panel]
        A3[Corporate-action records] --> A4[split/bonus adjustment factors<br/>tape-verified 99.1%]
        A2 --> A5[CA-adjusted returns panel v2<br/>gate: ex-day median |ret| 0.508 to 0.038]
        A4 --> A5
    end

    subgraph FE["2 · Feature engineering"]
        B1[Raw NSDL FII trades<br/>2011-2025] --> B2["10 probit-ranked stock-day<br/>flow features (backward-only windows)"]
    end

    subgraph ID["3 · Identity audit"]
        C1[Masked FII/sub-account/broker IDs] --> C2{"Stable across months?"}
        C2 -->|"No: re-minted ~monthly, proven by ID-persistence test"| C3["Redesign features as<br/>within-day / within-month only"]
    end

    subgraph MD["4 · Regime model"]
        B2 --> D1["3-state HMM backbone<br/>(SELL / NEUTRAL / BUY)"]
        C3 --> D1
        D1 --> D2["Concentration overlay thresholds<br/>(TRAIN-era quantile rule)"]
        D2 --> D3["Archetypes: ROBOT / SHARK_DIST /<br/>SHARK_ACC / HOSTAGE"]
    end

    subgraph CN["5 · Canonical identity"]
        A5 --> E1["Issuer-bounded ISIN closure<br/>(90.4% to 98.5% coverage)"]
        D3 --> E1
    end

    subgraph VAL["6 · Economic validation battery"]
        E1 --> F1[Event study: excess-CAR diff-in-diff]
        F1 --> F2[Liquidity-shock mechanism:<br/>pressure + volume + reversal arc]
        F2 --> F3["Panel regression<br/>(stock+date FE, 2-way cluster)"]
        F3 --> F4[Robustness: horizons, dose,<br/>non-overlap, placebo]
        F4 --> F5[LightGBM challenger + SHAP]
        F5 --> F6["Independent endorsement:<br/>Easley-O'Hara PIN estimator"]
    end

    subgraph ADV["7 · Adversarial self-audit"]
        F6 --> G1["Referee simulation:<br/>is the HMM necessary? index mechanics?"]
        G1 --> G2["Skeptic audit:<br/>bounce-free windows, SD-HO contrast"]
    end

    subgraph BT["8 · Backtests"]
        G2 --> H1[Engine correctness gates]
        H1 --> H2["No-model baselines<br/>(frozen, recorded first)"]
        H2 --> H3[Regime-conditioned strategies]
        H3 --> H4["Gross vs net verdict:<br/>signal real, costs bind (2-8bp breakeven)"]
    end
```

Each numbered stage above corresponds to a named pipeline stage with a
pre-registered PASS/FAIL gate — see [`docs/STAGES.md`](docs/STAGES.md) for
the complete manifest (inputs, outputs, and the exact verdict rule for
every one of the 55 registered stages).

### Why this order

| Step | What happens | Why it's here |
|---|---|---|
| **① Data preparation** | Repair the price tape | It has real defects — a four-digit year bug, null 2011 ISINs, un-restated ex-date closes. Fix these *before* touching returns so every later bp n[...] |
| **② Feature engineering** | Ten within-day, backward-only percentile-rank features | Cross-sectional ranking neutralizes 2011–2025 breadth growth and the 2021 structural break, without a single [...] |
| **③ Identity audit** | Test whether masked FII/broker IDs are stable | They are not — 0% cross-month persistence, proven formally. Every entity feature was redesigned to be within-day/within-mon[...] |
| **④ Regime model** | 3-state HMM backbone + concentration-overlay thresholds | Thresholds are frozen from the TRAIN era via a quantile rule — adopted *after* the original GMM approach failed its[...] |
| **⑤ Canonical identity** | Issuer-bounded ISIN closure | Corporate actions fragment one company across multiple ISINs; closure reconciles tape and model states, recovering 8 coverage points with z[...] |
| **⑥ Validation battery** | Six independent methods, one question | Does concentrated vs. dispersed selling actually behave differently in forward returns? Event study, mechanism decomposition, FE [...] |
| **⑦ Adversarial self-audit** | Attack the strongest claims, twice | Once as a simulated referee, once as a deliberately hostile self-review — with the resulting price corrections reported verbat[...] |
| **⑧ Backtests** | Does it survive transaction costs? | Answered honestly: the signal is real at the gross/portfolio level, but no variant clears realistic one-way costs. |

---

## 4 · Quickstart

```bash
# 1. environment (uv)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
# macOS + LightGBM: brew install libomp

# 2. data (extracts the research data export into data/)
./scripts/setup_data.sh          # or: SOURCE_DIR=/path/to/zips ./scripts/setup_data.sh

# 3. the whole research chain, one command
python pipeline.py --all
```

Useful invocations:

```bash
python pipeline.py --list                        # full stage manifest
python pipeline.py --phase validation             # one phase
python pipeline.py --stage panel_regression       # one stage
python pipeline.py --from-stage canonical_panel   # resume mid-chain
python pipeline.py --phase audit                  # read-only diagnostics
python pipeline.py --model hmm_regime             # train/evaluate a model
```

Every run writes a timestamped log per stage to `outputs/logs/`; seeds are
fixed from `config/config.yaml`. A failed gate halts the chain — this is by
design (see § 7, Design decisions).

---

## 5 · Repository layout

```
pipeline.py                  unified entrypoint
config/config.yaml           paths, frozen split dates, frozen thresholds, costs
src/fii/
  paths.py, config.py        config-driven paths (FII_DATA_ROOT overridable)
  runner.py                  stage executor: seeding, logging, halt-on-failure
  stages/registry.py         ordered stage manifest (the dependency graph)
  data_prep/                 tape repair -> CA adjustment -> canonical panel
  features/                  the 10-feature stock-day flow store
  models/                    BaseModel interface + auto-discovery registry
    hmm_stages/              HMM build/calibration stages (the main model)
    fhmm_stages/             factorial-HMM challenger (Module 17)
    hmm_regime.py            main model behind the common interface
    factorial_hmm.py         FHMM challenger behind the common interface
    lightgbm_gbt.py          GBT challenger
    _template.py             copy this to add a new model (one file, nothing else)
  phase2/                    causal filtering, calibration, hazard, decision
  validation/                the economic-validation battery (+ audits/)
  backtest/                  engine.py + gates + strategy pairs
  reporting/                 exhibit export + outputs/ population
legacy/colab_modules/        every original Colab script, byte-for-byte
docs/                        thesis-grade methodology docs (see map below)
outputs/                     logs, tables, figures, metrics... (generated)
data/                        research data (generated by setup, gitignored)
```

Stage scripts under `src/fii/` carry descriptive names
(`price_panel.py`, `flow_innovation.py`, `backbone_ablation.py`, ...) that
match their entry in `stages/registry.py` and `docs/STAGES.md`. The
original Colab-era names (`module5a_...`, `module9_...`) are preserved
verbatim only under `legacy/colab_modules/`, which exists specifically as
an unmodified historical record — see § 7, Design decisions.

---

## 6 · Documentation map

| | |
|---|---|
| [`docs/00_project_overview.md`](docs/00_project_overview.md) | findings, pipeline diagram, design philosophy |
| [`docs/01_data_preparation.md`](docs/01_data_preparation.md) | CA-adjustment math, ISIN canonicalization, the gates |
| [`docs/02_feature_engineering.md`](docs/02_feature_engineering.md) | feature definitions, probit ranking, leakage rules |
| [`docs/03_models.md`](docs/03_models.md) | HMM foundations (Baum–Welch, Viterbi), hybrid design, LightGBM, extension contract |
| [`docs/04_validation_framework.md`](docs/04_validation_framework.md) | event study, PanelOLS spec, INNOV, PIN likelihood |
| [`docs/05_backtesting.md`](docs/05_backtesting.md) | engine mechanics, metric definitions, honest results |
| [`docs/STAGES.md`](docs/STAGES.md) | per-stage purpose / inputs / outputs / gates |
| [`docs/paper/FII_thesis.md`](docs/paper/FII_thesis.md) | the long-form account (22 sections; also as PDF/DOCX) — every decision with its math, reality check, and file citation |
| [`docs/paper/identifier_audit_note.md`](docs/paper/identifier_audit_note.md) | standalone note: the masked-identifier audit protocol |
| [`docs/ADOPTION_RECIPE.md`](docs/ADOPTION_RECIPE.md) | one-page recipe: compute the composition measure on your own data |

---

## 7 · Design decisions worth knowing

#### Stages are the original research scripts, preserved

This research was built as sequentially-verified scripts, each with
pre-registered PASS/FAIL gates in its printed output; the validation log
cites those exact artifacts. Migration from the original Colab notebooks
applied exactly two mechanical substitutions (Colab paths → `fii.paths`;
backtest session-coupling → an explicit import), auditable in
`scripts/migrate_colab_modules.py`.

A later pass renamed the migrated files to descriptive names for
readability (logic untouched). Originals live byte-for-byte in `legacy/`.
Changing stage *logic* requires re-running the affected gates — that is
the contract.

<br>

#### The temporal protocol is frozen

Train ≤ 2021-04-30, test ≥ 2021-07-01, May–June 2021 masked everywhere.
These dates live in config for transparency, not for tuning.

<br>

#### Failures are part of the record

The battery caught two silent code corruptions, a false exchange-data
assumption, a CA-parser bug, and two wrong economic narratives — all
documented in the research log with their fixes. This is a feature of the
methodology, not an embarrassment.

<br>

#### Extending with a new model

Copy `src/fii/models/_template.py`, set a name, implement four methods.
The registry auto-discovers it; the frozen split, feature-store contract,
and validation battery apply unchanged.

---

## 8 · Data note

The pipeline expects two research data exports: NSDL FII trade parquets and
NSE price/CA/deal data. They are **not** redistributed in this repository —
`scripts/setup_data.sh` extracts them from local zips (override with
`SOURCE_DIR`). NSDL FII records are licensed data; see
[`docs/01_data_preparation.md`](docs/01_data_preparation.md) for schema.

---

## 9 · Requirements

Python ≥ 3.11 · `numpy` `pandas` `polars` `pyarrow` `scipy` `statsmodels`
`linearmodels` `hmmlearn` `lightgbm` `scikit-learn` `pyyaml` `matplotlib`
(see `requirements.txt` / `pyproject.toml`).

macOS + LightGBM needs `brew install libomp`.
