# When Do Foreign Institutions Move Prices?
## Trade Concentration and the Transitory–Permanent Decomposition of FII Flow

*Working paper draft v0.1 — prose against final validated numbers (Modules 1–11).
Exhibit placeholders marked [Exhibit N]. Numbers cite the validation log §3a–3n.*

---

## Abstract

Using fourteen years (2011–2025) of masked, daily, stock-level foreign
institutional investor (FII) trade records from India's NSDL depository, we ask
when foreign flow moves prices permanently and when its impact is transitory.
An unsupervised hidden-Markov regime model, fit only on within-day
cross-sectional flow features and frozen before any price data was examined,
partitions stock-days into flow archetypes that differ on two axes: direction
(buy/sell) and **concentration** (few versus many participating FII entities).
Concentration, not magnitude, separates the two kinds of impact. Episodes of
*concentrated* FII selling are followed by an out-of-sample reversal of +49 bp
over 20 days (+65 bp in-sample; concentrated buying mirrors at −48/−88 bp),
while *dispersed* selling of the same direction and comparable magnitude shows
no reversal at any horizon — the decline is permanent. The reversal is
accompanied by an event-day volume climax (1.12–1.13× the stock's own trailing
average) and survives stock and date fixed effects, two-way clustered errors,
past-return controls, characteristic demeaning, non-overlapping episode
selection, and a flow-surprise control. An independent Easley–O'Hara
informed-trading probability, estimated from FII order counts and blind to
returns, loads roughly three times more heavily on dispersed-selling exposure
than on concentrated-selling exposure — endorsing the interpretation that
dispersed flow is information and concentrated flow is liquidity demand.
Notably, this *inverts* our pre-registered hypothesis, which cast concentrated
flow as informed "sharks" and dispersed flow as forced "hostages." A second,
distinct regularity: the unexpected component of FII flow (AR(5) innovation)
reverts out of sample (forward IC −0.017 to −0.023). We document the full
gate-driven validation protocol, which caught two silent code corruptions, one
false data assumption, and two wrong economic narratives before any result was
accepted.

---

## 1. Introduction

Foreign institutional flow is the largest single marginal force in Indian
equities, and the question of whether it *informs* prices or merely *presses*
on them is as old as the emerging-market flow literature. The standard
approach measures flow magnitude — net purchases, in rupees or shares — and
asks whether returns continue or revert. We argue that magnitude is the wrong
axis. Two selling days of identical size can be opposite economic events: one
a single desk demanding immediacy, the other forty institutions independently
reducing a position. The first is a liquidity event and should revert; the
second aggregates dispersed information and should not.

The obstacle is that flow *composition* is rarely observable. Our data
resolves it partially: NSDL's masked FII transaction records preserve, within
each month, distinct (masked) entity identifiers, so for every stock-day we
observe not just how much FIIs traded but *how many* of them participated and
how skewed the participation was. We build ten leakage-disciplined,
cross-sectionally ranked flow features from these records, fit a three-state
hidden-Markov model on the directional axis, and overlay calibrated
concentration rules, yielding four archetypes: ROBOT (baseline two-sided
flow), SHARK_DIST (concentrated selling), SHARK_ACC (concentrated buying), and
HOSTAGE (dispersed, persistent selling). The taxonomy was frozen — training
sample ending April 2021, thresholds calibrated with built-in falsification
tests — before any price-based validation began.

Our headline result is a clean transitory–permanent decomposition along the
concentration axis. In a panel regression with stock and date fixed effects
and errors clustered two ways, the 20-day abnormal return following the end of
a concentrated-selling episode is +65.4 bp in the training era and +48.6 bp
out of sample (both p<0.01); concentrated buying mirrors at −87.9/−47.6 bp.
Dispersed selling — same direction, comparable flow — is statistically zero at
every horizon from 10 to 60 days: the price stays down. Concentration
separates liquidity from information.

We stress an unusual feature of the paper: **the result is the inverse of our
pre-registered hypothesis.** We named the concentrated archetype "Shark"
expecting informed trading, and the dispersed archetype "Hostage" expecting
forced, reverting fire-sales. The data refused both. We kept the archetype
names and report the refutation, because the validation protocol that produced
it — pre-registered predictions, one gated test per step, read-only
diagnostics before any fix — is itself a contribution: it caught two silent
code corruptions, one false assumption about exchange data, and two wrong
economic narratives before publication rather than after.

Related literature. [To expand: Coval–Stafford 2007 fire sales; Easley–O'Hara
PIN; Kyle 1985 impact; Campbell–Grossman–Wang volume/reversal;
Froot–O'Connell–Seasholes and the FII-flow EM literature; herding measures
(LSV) — our concentration axis is a daily, intra-institutional-class herding
measure tied directly to impact permanence.]

## 2. Data

**FII transactions.** NSDL masked stock-level FII trade records, April 2011 –
March 2025: date, masked entity code, ISIN, buy/sell flag, quantity, rate.
Entity codes are stable within a month only; all entity-based features are
therefore within-month by construction (a design constraint we verified in a
dedicated entity audit, and a stated limitation: no cross-month entity
tracking).

**Prices.** NSE daily bhavcopy for the full period, survivorship-free
(delisted names retained; event windows truncated at last trade rather than
dropped). Raw close-to-close returns are corporate-action adjusted by factors
we parse from NSE corporate-action files (splits, bonuses); each factor is
verified against the tape via the observed ex-day price ratio, with 99.1% of
applied factors tape-confirmed. The adjustment is gated: across 803 confirmed
ex-days the median |return| falls from 0.508 (raw) to 0.038 (adjusted).
A guard nulls any adjusted return exceeding ±50% where a factor was applied,
which caught 45 symbol-migration artifacts.

**Identity.** ISINs mutate. We resolve the 5,960 raw FII-side ISINs to 3,812
canonical identities using an issuer-bounded closure (ISIN characters 4–7
identify the issuer): value-preserving events (splits, bonuses, face-value
changes) map forward to the latest-trading ISIN of the same issuer, while
value-changing events (mergers, demergers, amalgamations) terminate identity.
A 180-day trading-overlap guard prevents collapsing genuinely distinct
listings (DVR/partly-paid lines). The closure is applied to *both* the price
tape and the model's state history. The model universe is 946 canonical ISINs
= 939 companies; the closure raised price-coverage of model stock-days from
90.4% to 98.49%, uniformly across archetypes. [Full construction, gates and
the NOISIN/degenerate-key audit: Appendix A / replication log.]

**Macro.** NIFTY50, S&P 500 (lagged one Indian trading day), USDINR, India
VIX. None enters the flow features; VIX appears only in state-dependence
tests (§8).

**Scope caveat, stated early.** The model universe is the liquid large/mid-cap
segment (~25% of FII-traded canonical names). Fire-sale dynamics may be
stronger in the excluded illiquid tail; our permanent-impact estimates are
therefore a conservative floor, and the reversal result speaks to liquid
names, where it is hardest to find.

## 3. The regime model

Ten within-day cross-sectional features are computed per stock-day from the
FII records — flow direction and magnitude scaled by trailing gross flow,
participation breadth, entity-concentration of selling and of buying,
persistence — each probit-ranked within the day (removing market-wide flow
level) and using strictly past information. May–June 2021 is masked as an
embargo buffer around the train/test boundary.

A three-state Gaussian HMM on the directional features yields a persistent
SELL / NEUTRAL / BUY backbone. Concentration states are *not* natively
recoverable by the HMM — persistence dominates the likelihood — so
concentration archetypes are defined by calibrated overlay rules on the
backbone: SHARK_DIST = SELL backbone with top-decile selling concentration,
SHARK_ACC symmetric on the buy side, HOSTAGE = SELL backbone with high breadth
and persistence but *low* concentration. Thresholds were calibrated with a
falsification-first protocol (a GMM-based rule failed its own stability test
and was replaced by a quantile rule confirmed by three-way convergence).

Everything is frozen at April 2021. Out of sample (July 2021 onward), the
archetype signatures, census shares, and transition structure replicate
near-exactly [Exhibit 1].

## 4. Empirical strategy

The unit of analysis is the archetype *episode* — a maximal run of consecutive
stock-days in one archetype. We measure market-adjusted, CA-adjusted,
clipped (±50%) cumulative abnormal returns from episode START (drift while
flow is active) and from episode END (the reversal test: flow has stopped, so
any systematic post-END return is price-pressure relaxation, not continued
flow). Test-era small-cap drift (+52 bp/20d on all labeled stock-days) makes
raw CARs uninterpretable, so all headline estimates are baseline-relative:
either difference-in-differences against the ALL_LABELED baseline or, in the
regression framework, absorbed by date fixed effects.

The regression framework is a PanelOLS with stock and date fixed effects,
standard errors clustered by stock and by calendar month, estimated separately
for the training and test eras. The dependent variable is the forward 20-day
abnormal return (bp) from stock-day t; regressors are archetype-END event
dummies (UNTAGGED omitted). Three specifications: R0 (FE only), R1 (+
characteristics: rolling 120-day beta, 126-to-21-day momentum, Amihud
illiquidity, log turnover, 20-day volatility, relative volume, log price, log
episode length), R2 (R1 + the pre-episode 20-day return, a *bad control* that
mechanically absorbs any generic loser-reversal channel — included
deliberately as a conservative lower bound). Language discipline throughout:
the model *predicts conditional on controls*; nothing here is causal, and
archetype labels are estimated regressors, which attenuates coefficients
toward zero.

## 5. Main result: the transitory–permanent decomposition

[Exhibit 2 — Table 1: R0/R1/R2, both eras. Headline column = R2, full
restored sample.]

| Post-episode 20d abnormal return (bp) | TRAIN | TEST (OOS) |
|---|---|---|
| SHARK_DIST end (concentrated sell) | **+65.4***\* | **+48.6***\* |
| SHARK_ACC end (concentrated buy) | **−87.9***\* | **−47.6***\* |
| HOSTAGE end (dispersed sell) | ≈0 (n.s.) | ≈0 (n.s.) |

Concentrated flow reverts; dispersed flow does not. The HOSTAGE null is the
economically important cell: it shares the SELL direction and the flow
magnitude range with SHARK_DIST and differs essentially only in participation
structure, making it the mechanism-relevant control. The generic
loser-reversal objection is closed inside the same table: pre-episode return
enters R2 significantly (a generic reversal channel exists in this market),
yet the SHARK_DIST dummy barely moves from R1 to R2 — the archetype carries
reversal information beyond "the stock just fell."

## 6. Mechanism: a liquidity shock, shown from internal data

[Exhibit 3 — event-arc figure: pre20 / event-day / episode / post20 CAR with
relative volume, per archetype.]

The full arc of a concentrated-selling episode reads as textbook price
pressure: a pre-episode decline (≈ −270 bp backdrop), a climax with volume at
1.12–1.13× the stock's own trailing 20-day average, then — once the
concentrated flow stops — a +80 bp (train) / +32 bp (test) recovery,
retracing roughly a third of the episode decline. SHARK_ACC mirrors on the
buy side. HOSTAGE shows the opposite volume signature: *below*-baseline
volume throughout — quiet, dispersed distribution that the market absorbs
without a liquidity premium, and without any subsequent recovery.

An honest methods note: we first sought external corroboration in exchange
block/bulk-deal disclosures and found essentially none. The reconciliation is
informative rather than embarrassing — disclosure regimes are
visibility-thresholded (0.5% of shares, all participants, single orders),
while FII episodes are worked orders spread across days; exchange volume is
the corroborating series that cannot be masked, and it delivers the climax
signature exactly where disclosures are blind.

## 7. Robustness

[Exhibit 4 — robustness panel.]

- **Overlap.** Restricting to non-overlapping episodes (≥28 calendar days
  apart, greedy selection) *strengthens* the reversal (+76/+108 bp).
- **Horizons.** CAR over 10/20/30/60 days builds and persists
  (+39 → +65 → +89 → +109 bp in-sample); a momentum artifact would decay.
  HOSTAGE is ≈0 at every horizon.
- **Dose–response.** Replacing dummies with the continuous episode-mean
  selling-concentration exposure (no thresholds) yields right-signed effects
  in all cells, cleanly significant in-sample (+27 bp per unit, p<0.01),
  weaker out of sample — the phenomenon lives in the concentration tail,
  which is exactly where the archetype thresholds sit.
- **Placebo.** ROBOT-end is contaminated as a placebo at the END anchor: a
  ROBOT episode ends by *transitioning into* a directional regime, so its
  "post" window contains the successor's flow (mechanically: +94 bp after
  BUY-transitions, −13 bp after SELL-transitions). HOSTAGE, which shares
  direction and magnitude with SHARK_DIST, is the valid null.

## 8. Alternative explanations, closed

- **Past-loser reversal** — pre20 control in R2 (§5).
- **Drift/size composition** — date FE, baseline-relative CARs, turnover /
  Amihud / beta controls.
- **Characteristics in disguise** (archetypes proxying for *kinds of stocks*
  rather than *moments in time*) — within-stock demeaning using train-era
  stock means leaves the predictive ICs essentially unchanged; the signal is
  dynamic, not compositional.
- **Flow-surprise magnitude** — the key confound: is "concentration" merely
  "big surprise"? We build NET_INNOV, a per-stock AR(5) innovation in scaled
  net flow, and add its episode mean to the regression: the SHARK_DIST
  coefficient is unchanged to the decimal (+65.4). Concentration is not
  surprise size. (NET_INNOV is estimated full-sample with deliberate
  look-ahead: it serves as a *yardstick*, and look-ahead makes it a stronger
  competitor than any real-time version — a conservative choice for the
  claim being defended. The archetypes themselves remain strictly real-time.)
- **State dependence** (VIX regimes, FII-flow Kyle λ) — tested and honestly
  mixed/null; not claimed. High-λ names show larger post-episode moves for
  *all* labels (a characteristic effect, not archetype-specific); the VIX
  interaction appears only in the test era and only marginally.

## 9. External validation: PIN endorses the reading

[Exhibit 5 — PIN ~ archetype-share regressions.]

The Easley–O'Hara probability of informed trading is estimated by MLE
(Lin–Ke stabilized) per stock-year from FII buy/sell *counts* — an input set
blind to prices, returns, and the archetype definitions. Estimates are sane
(levels in the literature band; negatively correlated with turnover). A
stock-year's PIN loads on its HOSTAGE share at +0.231 (train) / +0.149 (test),
roughly three times its loading on SHARK_DIST share (+0.077/+0.065): the
dispersed-selling archetype carries the informed-trading signature, the
concentrated one much less so — an independent construct arriving at the same
transitory/permanent assignment. Two nuances: the claim is relative
(concentrated selling carries *less* information, not none), and this is a
FII-slice PIN, not the classical all-market version (limitation, §12).
Consistent with the liquidity interpretation, the SHARK_DIST reversal is not
concentrated in high-PIN names — if anything it is larger where PIN is low.

## 10. A second regularity: flow-surprise reversion

The AR(5) flow innovation predicts *negative* forward returns in both eras
(daily IC −0.023 train / −0.017 test, t = −3.2/−2.6): the unexpected
component of FII flow reverts. We report this as a decomposition result, not
a tradable signal — the expectation model is estimated in-sample by design
(§8) — but it is a distinct, era-stable transitory channel: surprise flow,
like concentrated flow, is liquidity on average.

## 11. Is the regime model the right tool?

A gradient-boosted-tree challenger with access to all ten features beats the
frozen archetype baseline on overall predictive IC — but almost all of its
edge is *cross-sectional* (which stocks), not *dynamic* (which days). After
within-stock demeaning, the GBT's incremental dynamic performance fails the
pre-registered bar (quintile-spread t = 1.48 < 2). The features, not the HMM,
are the ceiling at current statistical power; sequence models (LSTMs) are not
justified by this data. The one identified lever for future work: within-stock
*changes* in participation breadth — the top dynamic SHAP feature — which the
current archetype rules do not use.

## 12. Limitations

Liquid-universe scope (the fire-sale tail is excluded); within-month-only
entity identity (no cross-month FII tracking); no fundamental controls beyond
what stock fixed effects absorb; FII-slice λ and PIN rather than all-market;
2024–25 entity-ID missingness (30–40%) confounding late-sample concentration
measurement; predictive-conditional claims only, never causal.

## 13. Conclusion

Two regularities in fourteen years of FII flow: (i) the concentration of
participation separates transitory from permanent price impact — concentrated
flow is liquidity demand that reverts, dispersed flow is information that
does not; (ii) the surprise component of flow reverts out of sample. Both
were found by an unsupervised taxonomy validated against a pre-registered,
gate-driven battery that refuted the authors' own starting hypothesis. The
"shark" was demanding liquidity; the "hostages," collectively, knew
something.

---

## Appendix stubs
- **A. Data construction and gates** — CA-factor parser + tape confirmation;
  ex-day gate; canonicalization closure; NOISIN audit; coverage accounting.
- **B. Threshold calibration and falsification protocol.**
- **C. Full failure log** — the two paste corruptions, the prev-close
  assumption, the parser bug, the migration guard, the inference fix
  (referee-facing summary; full detail in the replication log).
- **D. Estimator details** — PanelOLS/clustering; EHO likelihood with
  logsumexp stabilization; INNOV construction and look-ahead rationale.
- **E. Economic significance (Module 12 backtests, results in).** A gated
  long-short engine (execution-lag and cost-accounting correctness proven
  by pre-registered tests) ran four strategy pairs with and without the
  regime model. Three findings: (i) the model's information appears at the
  portfolio level exactly where [C1] predicts — excluding
  concentrated-regime days improves a flow-following book's gross Sharpe
  in *both* eras (ΔSharpe CI [+0.07,+0.49] test, [+0.03,+0.22] train), and
  the regime "arc" book (trend within concentrated episodes, reversion
  after they end, flat otherwise) is the only strategy with positive gross
  Sharpe in both eras (+1.00/+0.54) while its mechanical no-model twin is
  gross-negative; (ii) *nothing survives realistic costs* — best breakeven
  is ~2–8 bps one-way against a 15 bps assumption, because the reversal is
  ~50 bp/20d on ~7% of stock-days; (iii) this supports a
  limits-to-arbitrage reading: the transitory-impact regularity can
  persist precisely because harvesting it costs more than it pays net.
  Short legs additionally face India's SLB constraints. We report this as
  economic-significance evidence, not a trading claim.
