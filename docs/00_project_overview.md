# Project Overview

## What this research is

Using fourteen years (2011–2025) of masked, daily, stock-level foreign
institutional investor (FII) trade records from NSDL, this project asks: **when
does foreign flow move prices permanently, and when is its impact transitory?**

The answer, validated out of sample against every alternative we could
construct: **the concentration of participation — not the magnitude of flow —
separates the two.**

- **Concentrated** FII selling (few entities) is liquidity-demanding: prices
  fall with a volume climax, then revert **+49–65 bp over 20 days** after the
  flow stops. Concentrated buying mirrors (−48/−88 bp give-back).
- **Dispersed** FII selling (many entities, quiet volume) is
  information-consistent: the decline is **permanent** — no reversal at any
  horizon from 10 to 60 days.
- An independent Easley–O'Hara PIN estimator, blind to returns, loads ~3× more
  informed-trading probability on dispersed-selling exposure than on
  concentrated-selling exposure.

A second regularity: the **surprise component of FII flow reverts** out of
sample (decomposition evidence).

Notably, this **inverts the project's pre-registered hypothesis** (concentrated
"Shark" = informed, dispersed "Hostage" = forced fire-sale). The refutation is
reported, not hidden — the validation protocol that produced it is part of the
contribution.

## The pipeline at a glance

```
raw NSDL FII trades ──► feature store (10 probit flow features)
                              │
bhavcopy tape ──► CA-adjusted │
returns panel                 ▼
      │            hybrid HMM regime model
      │            (3-state backbone + concentration overlays)
      ▼                       │
issuer-bounded ISIN closure ◄─┘  (canonical v3 panel + states)
      │
      ▼
economic validation battery      backtests (Module 12)
(event study → mechanism →       (engine gates → baselines →
 panel regression → robustness →  HMM twins → diagnosis →
 GBT challenger → INNOV →         style-switch)
 VIX/λ → PIN)
```

Run it: `python pipeline.py --all`. Each stage prints pre-registered PASS/FAIL
gates; a failed gate halts the chain.

## Design philosophy (read before contributing)

1. **Stepwise, gated verification.** One verifiable claim per stage; the
   verdict rule is stated in the stage header *before* the result is computed.
2. **Frozen temporal protocol.** Train ≤ 2021-04-30, test ≥ 2021-07-01,
   May–June 2021 masked. Nothing downstream may move these.
3. **Falsification first.** The project killed two silent code corruptions,
   one false data assumption (NSE prev_close is *not* CA-restated), one
   parser bug, and two wrong economic narratives before accepting the result.
   The complete trail is in `research_log/FII_Module5_validation_log.md`.
4. **Preserved research code.** Stage scripts are the certified artifacts the
   validation log cites. They were migrated from Colab with exactly two
   mechanical substitutions (paths, engine import) — see
   `scripts/migrate_colab_modules.py`. Refactors that change stage *logic*
   require re-running the affected gates.
5. **Library estimators only.** Statistical models are visible library calls
   (`linearmodels.PanelOLS`, `statsmodels`, `hmmlearn`, `lightgbm`,
   `scipy.optimize`) — hand-rolled algebra is at most a cross-check.

## Document map

| Doc | Contents |
|---|---|
| `01_data_preparation.md` | tape repair, CA adjustment math, ISIN canonicalization |
| `02_feature_engineering.md` | the 10 flow features: definitions, intuition, leakage rules |
| `03_models.md` | HMM math (likelihood/Baum-Welch/Viterbi), overlay calibration, LightGBM, extension contract |
| `04_validation_framework.md` | event study, panel regression, INNOV, PIN — equations and verdicts |
| `05_backtesting.md` | engine mechanics, metrics definitions, strategy results |
| `STAGES.md` | per-stage manifest: purpose / inputs / outputs / gates |
| `FII_stockday_data_dictionary.md` | column-level dictionary of the feature store |
| `research_log/` | the unabridged evidence trail (every failure and fix) |
| `paper/` | working-paper outline and prose draft |
