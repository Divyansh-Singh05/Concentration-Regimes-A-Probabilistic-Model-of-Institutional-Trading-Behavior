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
               "validation", "backtest", "exhibits", "phase2", "fhmm",
               "audit"]

# fmt: off
STAGES: list[Stage] = [
    # ---- data preparation ---------------------------------------------------
    Stage("price_panel", "data_prep",
          _PKG / "data_prep/price_panel.py",
          "Bhavcopy -> repaired price panel (year-0020 fix, 2011 ISIN "
          "backfill, series dedupe, macro tz fix; gates G1/G2)"),
    Stage("ca_factors", "data_prep",
          _PKG / "data_prep/ca_factors.py",
          "Parse split/bonus corporate actions -> adjustment factors, "
          "tape-verified (99.1% confirmed)"),
    Stage("apply_adjustment", "data_prep",
          _PKG / "data_prep/apply_adjustment.py",
          "Apply CA factors -> returns_panel_v2 (ex-day gate A: median "
          "|ret| 0.508 -> 0.038; migration guard)"),
    # ---- feature engineering ------------------------------------------------
    Stage("feature_store", "features",
          _PKG / "features/feature_store.py",
          "Raw FII trades -> 10 probit-ranked stock-day flow features "
          "(strictly backward windows, May-Jun 2021 masked)"),
    # ---- model --------------------------------------------------------------
    # NOTE: hybrid_overlay_design.py (hybrid-overlay design exploration) is preserved in
    # models/hmm_stages/ and legacy/ but is NOT a runnable stage: it
    # continues the Module-2 notebook session (needs v1-v3 objects in
    # memory). The production chain is train_oos.py -> threshold_calibration.py.
    Stage("hmm_train_oos", "model",
          _PKG / "models/hmm_stages/train_oos.py",
          "Frozen temporal split (train<=2021-04, test>=2021-07); "
          "fit backbone, decode both eras, OOS replication checks"),
    Stage("threshold_calibration", "model",
          _PKG / "models/hmm_stages/threshold_calibration.py",
          "Overlay thresholds via TRAIN-era quantile rule (GMM "
          "falsification documented) -> stockday_states_calibrated"),
    Stage("model_descriptives", "model",
          _PKG / "models/hmm_stages/descriptive_stats.py",
          "Archetype signatures, census, transitions, era replication"),
    # ---- canonical identity -------------------------------------------------
    Stage("canonical_panel", "canonical",
          _PKG / "data_prep/canonical_panel.py",
          "Issuer-bounded ISIN closure on tape AND states -> "
          "returns_panel_v3 + states_v3 (coverage 90.4% -> 98.5%)"),
    # ---- economic validation battery ----------------------------------------
    Stage("event_study", "validation",
          _PKG / "validation/event_study.py",
          "Excess-CAR difference-in-differences, START & END anchors"),
    Stage("deal_corroboration", "validation",
          _PKG / "validation/deal_corroboration.py",
          "Block/bulk/short-deal coincidence test (negative result, "
          "kept: visibility-threshold lesson)"),
    Stage("liquidity_shock", "validation",
          _PKG / "validation/liquidity_shock_profile.py",
          "Event arc: pressure + volume climax + reversal (mechanism)"),
    Stage("panel_regression", "validation",
          _PKG / "validation/panel_regression.py",
          "PanelOLS stock+date FE, two-way clustered; specs R0/R1/R2"),
    Stage("robustness", "validation",
          _PKG / "validation/robustness.py",
          "Non-overlap, horizons 10-60, dose-response, ROBOT placebo "
          "decomposition, beta-null fix"),
    Stage("gbt_challenger", "validation",
          _PKG / "validation/gbt_challenger.py",
          "LightGBM challenger vs regime baseline + SHAP attribution"),
    Stage("demeaning_check", "validation",
          _PKG / "validation/demeaning_check.py",
          "Characteristics-vs-dynamics decomposition (pre-registered "
          "LSTM gate: not met)"),
    Stage("flow_innovation", "validation",
          _PKG / "validation/flow_innovation.py",
          "NET_INNOV AR(5) yardstick: concentration != flow surprise; "
          "surprise-reversion regularity"),
    Stage("vix_lambda", "validation",
          _PKG / "validation/vix_lambda.py",
          "State-dependence: VIX interaction + FII-flow Kyle lambda "
          "(mixed/null, reported honestly)"),
    Stage("pin_model", "validation",
          _PKG / "validation/pin_model.py",
          "Easley-O'Hara FII-PIN MLE per stock-year; independent "
          "endorsement of the transitory/permanent reading"),
    Stage("backbone_ablation", "validation",
          _PKG / "validation/backbone_ablation.py",
          "Referee test: census-matched rule backbone reproduces Table 1 "
          "(V1: HMM not necessary — contribution is the measure)"),
    Stage("incremental_value", "validation",
          _PKG / "validation/incremental_value.py",
          "Referee test: composition vs flow-magnitude controls + "
          "GBT with/without composition block (+28% rel. IC, t=3.09)"),
    Stage("recon_exclusion", "validation",
          _PKG / "validation/recon_exclusion.py",
          "Referee test: index-reconstitution window exclusion "
          "(passive mechanics excluded)"),
    Stage("skeptic_tests", "validation",
          _PKG / "validation/skeptic_tests.py",
          "Self-audit: bounce-free windows (repriced -11/-24%), direct "
          "SD-HO contrast, public VCR head-to-head, PUBLIC->FLOW->COMP "
          "GBT ladder (all pre-registered; all pass)"),
    # ---- backtests -----------------------------------------------------------
    Stage("engine_gates", "backtest",
          _PKG / "backtest/engine_gates.py",
          "Backtest-engine correctness gates G1/G2/G3 (must PASS "
          "before any strategy runs)"),
    Stage("bt_baselines", "backtest",
          _PKG / "backtest/strategies_base.py",
          "Three no-model baselines (REV20, FLOW10, PROXY), frozen"),
    Stage("bt_hmm_twins", "backtest",
          _PKG / "backtest/strategies_hmm.py",
          "HMM-conditioned twins + pre-registered dSharpe verdicts"),
    Stage("bt_gross_diagnosis", "backtest",
          _PKG / "backtest/gross_diagnosis.py",
          "Signal-vs-implementation: gross dSharpe, breakeven costs"),
    Stage("bt_style_switch", "backtest",
          _PKG / "backtest/style_switch.py",
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
    # ---- Phase II (charter: docs/PHASE2_PLAN.md; run explicitly) -------------
    Stage("phase2_filtering", "phase2",
          _PKG / "phase2/causal_filtering.py",
          "16A: forward-filtered posteriors from frozen params; gate A2 "
          "= Table 1 survives on fully causal labels"),
    Stage("phase2_calibration", "phase2",
          _PKG / "phase2/calibration.py",
          "16B: nowcast calibration — Brier/log-loss/ECE vs census "
          "prior and label-Markov persistence baselines"),
    Stage("phase2_hazard", "phase2",
          _PKG / "phase2/hazard.py",
          "16C: episode-END hazard model, walk-forward yearly refits; "
          "bar = beat age-only KM baseline (k=1,3) at paired t>=2"),
    Stage("phase2_decision", "phase2",
          _PKG / "phase2/decision.py",
          "16D: anticipation vs confirmation, paired within episode, "
          "cost-neutral; theta walk-forward; bar = TEST gain CI>0 AND "
          "beats KM anticipator (t>=2)"),
    # ---- factorial HMM challenger (Module 17; separate code from the naive
    #      HMM chain by design — run explicitly, not part of --all) -----------
    Stage("fhmm_train_oos", "fhmm",
          _PKG / "models/fhmm_stages/train_oos.py",
          "17A: factorial HMM (direction x concentration chains), frozen "
          "split, end-to-end archetypes, gates G1-G4"),
    Stage("fhmm_descriptives", "fhmm",
          _PKG / "models/fhmm_stages/descriptives.py",
          "17B: chain census/dwell/transitions + agreement vs the "
          "calibrated naive-HMM archetypes (kappa, overlap)"),
    Stage("fhmm_table1", "fhmm",
          _PKG / "models/fhmm_stages/table1.py",
          "17C: Table-1 PanelOLS on FHMM labels vs naive-HMM labels, "
          "pre-registered verdicts V1/V2/V3"),
    Stage("fhmm_filtering", "fhmm",
          _PKG / "models/fhmm_stages/filtering.py",
          "17D: causal forward filtering on the product space (16A "
          "protocol); gate A2F = smoothed-FHMM economics survive"),
    Stage("fhmm_calibration", "fhmm",
          _PKG / "models/fhmm_stages/calibration.py",
          "17E: nowcast calibration for BOTH chains vs causal "
          "baselines (16B protocol, amended baseline inherited)"),
    Stage("fhmm_hazard", "fhmm",
          _PKG / "models/fhmm_stages/hazard.py",
          "17F: episode-END hazard, walk-forward yearly refits, AUC; "
          "bar = beat age-only KM at paired t>=2 (16C protocol)"),
    Stage("fhmm_decision", "fhmm",
          _PKG / "models/fhmm_stages/decision.py",
          "17G: anticipation vs confirmation, theta walk-forward, "
          "KM-anticipator control (16D protocol)"),
    # ---- tail-probe extension study (Module 14; run in order a->b->c) --------
    Stage("tail_census", "audit",
          _PKG / "validation/tail_census.py",
          "Tail probe 14A: feasibility census of the attributable "
          "illiquid tail (gates G1-G3)"),
    Stage("tail_labels", "audit",
          _PKG / "validation/tail_labels.py",
          "Tail probe 14B: method-frozen rule labels on the tail "
          "(census/clustering/power gates)"),
    Stage("tail_economics", "audit",
          _PKG / "validation/tail_economics.py",
          "Tail probe 14C: verdict NO TAIL EFFECT — dislocation "
          "transfers, reversal does not; friction bar ~100bp"),
    # ---- read-only audits (optional) -----------------------------------------
    Stage("data_audit", "audit",
          _PKG / "validation/audits/data_audit.py",
          "Raw collected-data audit (dates, ISIN nulls, tz shifts)"),
    Stage("adjustment_diagnose", "audit",
          _PKG / "validation/audits/adjustment_diagnose.py",
          "Read-only diagnosis of the stored v2 panel returns"),
    Stage("car_start_legacy", "audit",
          _PKG / "validation/audits/car_start_legacy.py",
          "START-anchor CARs (inference superseded by event_study)"),
    Stage("data_lineage", "audit",
          _PKG / "validation/audits/data_lineage.py",
          "Table heads along the full derivation chain"),
    Stage("attrition", "audit",
          _PKG / "validation/audits/attrition.py",
          "Join-attrition decomposition (model vs tape)"),
    Stage("universe_audit", "audit",
          _PKG / "validation/audits/universe_audit.py",
          "Model-universe provenance and count integrity"),
    Stage("isin_provenance", "audit",
          _PKG / "validation/audits/isin_provenance.py",
          "5,960 -> 3,812 -> 946 ISIN funnel accounting"),
    Stage("cisin_validation", "audit",
          _PKG / "validation/audits/cisin_validation.py",
          "Canonical-ISIN validity checks"),
    Stage("tape_canonicalization", "audit",
          _PKG / "validation/audits/tape_canonicalization.py",
          "Coverage recovery measurement (90.4% -> 98.2%)"),
    Stage("isin_accounting", "audit",
          _PKG / "validation/audits/isin_accounting.py",
          "Active/inactive closure accounting; entity-boundary rule"),
    Stage("noisin_probe", "audit",
          _PKG / "validation/audits/noisin_probe.py",
          "Degenerate-key (NOISIN/null) audit: 0 model impact"),
    Stage("universe_integrity", "audit",
          _PKG / "validation/audits/universe_integrity.py",
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
