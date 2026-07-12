"""Ordered manifest of every pipeline stage.

Phases run in the order given by PHASE_ORDER; stages run in the order
listed within each phase.  The ordering encodes real data dependencies:

  data_prep     bhavcopy tape -> repaired panel -> CA factors -> v2 panel
  features      raw FII trades -> stockday feature store
  model         features -> HMM backbone (frozen split) -> calibrated states
  canonical     states + v2 panel -> issuer-bounded closure -> v3 panel
  validation    the full economic-validation battery (Modules 5B4-11)
  backtest      engine gates -> baselines -> HMM twins -> diagnosis -> S4
  audit         read-only diagnostics; optional, safe to run any time
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fii.paths import REPO_ROOT

_PKG = REPO_ROOT / "src" / "fii"


@dataclass(frozen=True)
class Stage:
    name: str
    phase: str
    script: Path
    desc: str


PHASE_ORDER = ["data_prep", "features", "model", "canonical",
               "validation", "backtest", "exhibits", "audit"]

# fmt: off
STAGES: list[Stage] = [
    # ---- data preparation ---------------------------------------------------
    Stage("price_panel", "data_prep",
          _PKG / "data_prep/module5a_price_panel.py",
          "Bhavcopy -> repaired price panel (year-0020 fix, 2011 ISIN "
          "backfill, series dedupe, macro tz fix; gates G1/G2)"),
    Stage("ca_factors", "data_prep",
          _PKG / "data_prep/module5b1_ca_factors.py",
          "Parse split/bonus corporate actions -> adjustment factors, "
          "tape-verified (99.1% confirmed)"),
    Stage("apply_adjustment", "data_prep",
          _PKG / "data_prep/module5b2_apply_adjustment.py",
          "Apply CA factors -> returns_panel_v2 (ex-day gate A: median "
          "|ret| 0.508 -> 0.038; migration guard)"),
    # ---- feature engineering ------------------------------------------------
    Stage("feature_store", "features",
          _PKG / "features/module1_feature_store_v2.py",
          "Raw FII trades -> 10 probit-ranked stock-day flow features "
          "(strictly backward windows, May-Jun 2021 masked)"),
    # ---- model --------------------------------------------------------------
    # NOTE: module2_v4 (hybrid-overlay design exploration) is preserved in
    # models/hmm_stages/ and legacy/ but is NOT a runnable stage: it
    # continues the Module-2 notebook session (needs v1-v3 objects in
    # memory). The production chain is module3a -> module3b.
    Stage("hmm_train_oos", "model",
          _PKG / "models/hmm_stages/module3a_model_split_oos.py",
          "Frozen temporal split (train<=2021-04, test>=2021-07); "
          "fit backbone, decode both eras, OOS replication checks"),
    Stage("threshold_calibration", "model",
          _PKG / "models/hmm_stages/module3b_threshold_calibration.py",
          "Overlay thresholds via TRAIN-era quantile rule (GMM "
          "falsification documented) -> stockday_states_calibrated"),
    Stage("model_descriptives", "model",
          _PKG / "models/hmm_stages/module3c_descriptive_stats.py",
          "Archetype signatures, census, transitions, era replication"),
    # ---- canonical identity -------------------------------------------------
    Stage("canonical_panel", "canonical",
          _PKG / "data_prep/module5j_canonical_panel.py",
          "Issuer-bounded ISIN closure on tape AND states -> "
          "returns_panel_v3 + states_v3 (coverage 90.4% -> 98.5%)"),
    # ---- economic validation battery ----------------------------------------
    Stage("event_study", "validation",
          _PKG / "validation/module5b4_car_diff.py",
          "Excess-CAR difference-in-differences, START & END anchors"),
    Stage("deal_corroboration", "validation",
          _PKG / "validation/module6_deal_corroboration.py",
          "Block/bulk/short-deal coincidence test (negative result, "
          "kept: visibility-threshold lesson)"),
    Stage("liquidity_shock", "validation",
          _PKG / "validation/module6b_liquidity_shock_profile.py",
          "Event arc: pressure + volume climax + reversal (mechanism)"),
    Stage("panel_regression", "validation",
          _PKG / "validation/module7_panel_regression.py",
          "PanelOLS stock+date FE, two-way clustered; specs R0/R1/R2"),
    Stage("robustness", "validation",
          _PKG / "validation/module7b_robustness.py",
          "Non-overlap, horizons 10-60, dose-response, ROBOT placebo "
          "decomposition, beta-null fix"),
    Stage("gbt_challenger", "validation",
          _PKG / "validation/module8_gbt_shap.py",
          "LightGBM challenger vs regime baseline + SHAP attribution"),
    Stage("demeaning_check", "validation",
          _PKG / "validation/module8b_demeaning_check.py",
          "Characteristics-vs-dynamics decomposition (pre-registered "
          "LSTM gate: not met)"),
    Stage("flow_innovation", "validation",
          _PKG / "validation/module9_net_innov.py",
          "NET_INNOV AR(5) yardstick: concentration != flow surprise; "
          "surprise-reversion regularity"),
    Stage("vix_lambda", "validation",
          _PKG / "validation/module10_vix_lambda.py",
          "State-dependence: VIX interaction + FII-flow Kyle lambda "
          "(mixed/null, reported honestly)"),
    Stage("pin_model", "validation",
          _PKG / "validation/module11_pin.py",
          "Easley-O'Hara FII-PIN MLE per stock-year; independent "
          "endorsement of the transitory/permanent reading"),
    # ---- backtests -----------------------------------------------------------
    Stage("engine_gates", "backtest",
          _PKG / "backtest/engine_gates.py",
          "Backtest-engine correctness gates G1/G2/G3 (must PASS "
          "before any strategy runs)"),
    Stage("bt_baselines", "backtest",
          _PKG / "backtest/module12b_strategies_base.py",
          "Three no-model baselines (REV20, FLOW10, PROXY), frozen"),
    Stage("bt_hmm_twins", "backtest",
          _PKG / "backtest/module12c_strategies_hmm.py",
          "HMM-conditioned twins + pre-registered dSharpe verdicts"),
    Stage("bt_gross_diagnosis", "backtest",
          _PKG / "backtest/module12d_gross_diagnosis.py",
          "Signal-vs-implementation: gross dSharpe, breakeven costs"),
    Stage("bt_style_switch", "backtest",
          _PKG / "backtest/module12e_style_switch.py",
          "S4 style-switch (trend/reversion/hold by regime) pair"),
    # ---- paper exhibits --------------------------------------------------------
    Stage("paper_exhibits", "exhibits",
          _PKG / "reporting/make_exhibits.py",
          "Export every paper table (CSV+LaTeX) and figure (PNG) to "
          "outputs/tables and outputs/figures"),
    Stage("collect_outputs", "exhibits",
          _PKG / "reporting/collect_outputs.py",
          "Populate outputs/: predictions, trained_models, validation "
          "reports, descriptive stats, metrics, run summary"),
    # ---- read-only audits (optional) -----------------------------------------
    Stage("data_audit", "audit",
          _PKG / "validation/audits/module4c_data_audit.py",
          "Raw collected-data audit (dates, ISIN nulls, tz shifts)"),
    Stage("adjustment_diagnose", "audit",
          _PKG / "validation/audits/module5b2d_diagnose.py",
          "Read-only diagnosis of the stored v2 panel returns"),
    Stage("car_start_legacy", "audit",
          _PKG / "validation/audits/module5b3_car_start.py",
          "START-anchor CARs (inference superseded by event_study)"),
    Stage("data_lineage", "audit",
          _PKG / "validation/audits/module5c_data_lineage.py",
          "Table heads along the full derivation chain"),
    Stage("attrition", "audit",
          _PKG / "validation/audits/module5d_attrition_diagnostic.py",
          "Join-attrition decomposition (model vs tape)"),
    Stage("universe_audit", "audit",
          _PKG / "validation/audits/module5f_universe_audit.py",
          "Model-universe provenance and count integrity"),
    Stage("isin_provenance", "audit",
          _PKG / "validation/audits/module5g_isin_provenance.py",
          "5,960 -> 3,812 -> 946 ISIN funnel accounting"),
    Stage("cisin_validation", "audit",
          _PKG / "validation/audits/module5h_cisin_validation.py",
          "Canonical-ISIN validity checks"),
    Stage("tape_canonicalization", "audit",
          _PKG / "validation/audits/module5i_tape_canonicalization.py",
          "Coverage recovery measurement (90.4% -> 98.2%)"),
    Stage("isin_accounting", "audit",
          _PKG / "validation/audits/module5k_isin_accounting.py",
          "Active/inactive closure accounting; entity-boundary rule"),
    Stage("noisin_probe", "audit",
          _PKG / "validation/audits/module5l_noisin_probe.py",
          "Degenerate-key (NOISIN/null) audit: 0 model impact"),
    Stage("universe_integrity", "audit",
          _PKG / "validation/audits/module5m_universe_integrity.py",
          "Is 946 the right company count? (939 issuers, fragments)"),
]
# fmt: on


def by_name(name: str) -> Stage:
    for s in STAGES:
        if s.name == name:
            return s
    raise KeyError(f"unknown stage '{name}' — try: pipeline.py --list")


def phase_stages(phase: str) -> list[Stage]:
    return [s for s in STAGES if s.phase == phase]
