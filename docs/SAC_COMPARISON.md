# Directed SAC comparison: results and interpretation

Executed on 10 November 2026. The design and measurement implementation were
frozen before the main results in commit
`b36f15ed785755be8068b898b59dc0aea8747b2a`.

## Question and scope

Does the existing corrected rejected-cell SAC count give the same conditional
detection behavior as sample-adapted SAC-Basic, SAC-Row and SAC-Column when
they receive exactly the same input/query budget and SAC matrix?

The histogram tests follow the statistical construction in
[Aslan et al., IEEE Access 2026](https://doi.org/10.1109/ACCESS.2026.3659273).
The authors' publicly supplied code was inspected at
[commit 1a2c4f4](https://github.com/srmnckn/SACtests/tree/1a2c4f4e3a81a4e8b019fb980817133304038746);
none of that code is copied here. Their 2^20-input experiments are not
numerically replicated: eight bin boundaries and exact probabilities are
recomputed for the smaller sample budgets, and the primary alpha is 0.001.
Conclusions therefore concern the documented adaptations and selected ciphers.

## Design

- RECTANGLE-80 and CLEFIA-128, one recorded default key per cipher.
- 500 independently seeded input replications per cipher; N=64, 256, 1,024
  are nested prefixes within a replication. Each condition requires N(n+1)
  trace inputs. All methods see the same full bit-pair count matrix.
- Analyze RECTANGLE native rounds 4-8 and CLEFIA rounds 3-7: 30 conditions.
- Corrected count: exact rejected-cell count tail with cell cutoff 0.001.
  Histogram tests: eight-bin Pearson statistics, global or maximum axis.
- Retain nominal chi-square/Sidak rules as sensitivity analyses. The primary
  histogram comparison uses plus-one Monte Carlo rank p-values, including ties,
  against 100,000 independent null calibration matrices per width/sample size.
- Validate marginal null sizes using another 200,000 simulations per design.
  Total: 600,000 training and 1,200,000 held-out null-statistic draws across
  six designs. Row/column share the same marginal max-axis null distribution;
  these simulations do not establish their joint behavior.
- Primary alpha=0.001; alpha=0.01 is a sensitivity analysis. All family p-values
  include the same finite-domain ideal-permutation coupling bound.
- Report Wilson pointwise 95% intervals and paired exact McNemar tests. Holm
  adjusts all 90 primary baseline-vs-comparator contrasts. Nested sample
  sizes and serial rounds are not treated as independent observations.

The new vector evaluators were checked against all native scalar rounds on
three keys and structured/random inputs: 24,870 state comparisons matched.
Independent scalar reconstruction of full two-input SAC matrices and scalar
histogram calculations also passed. No production cipher or metric source,
frozen original measurements, or official C reference was modified.

## Main results

Primary Monte Carlo calibrated histogram policy, alpha=0.001. Values below
are observed detection percentages in 500 replications; they are estimates,
not exact population powers. Count retains its exact discrete rule.

| Cipher / native round | N | Corrected count | Basic adapted | Row adapted | Column adapted |
|---|---:|---:|---:|---:|---:|
| RECTANGLE / 6 | 64 | 45.8% | 100.0% | 77.6% | 61.6% |
| RECTANGLE / 7 | 64 | 0.0% | 22.4% | 0.4% | 0.0% |
| RECTANGLE / 7 | 256 | 0.6% | 97.8% | 1.0% | 0.2% |
| RECTANGLE / 7 | 1,024 | 12.2% | 100.0% | 15.8% | 5.2% |
| CLEFIA / 4 | 64/256/1,024 | 100.0% | 100.0% | 100.0% | 100.0% |
| CLEFIA / 5-7 | all tested | 0.0-0.4% | 0.0-0.2% | 0.0% | 0.0-0.2% |

The sharpest contrast is RECTANGLE round 7, N=256: Basic detects 489/500
(Wilson 95% interval 96.10-98.77%) versus count 3/500 (0.20-1.75%). The paired
difference is 97.2 percentage points; its pointwise paired-bootstrap interval
is 95.6-98.6 points and Holm-adjusted McNemar p is 9.01e-145.
At N=1,024 the same round gives 500/500 versus 61/500.

Seven of the 90 primary contrasts remain significant after Holm correction:
six favor a histogram comparator, and one favors count. All occur in the
RECTANGLE cases. Count exceeds Column at round 7, N=1,024 (12.2% versus 5.2%,
Holm p=0.00425). There is no universal winner. Non-significant contrasts do
not establish equivalence, and 500/500 detections do not prove population
power exactly one.

No Holm-significant paired difference is observed on the selected CLEFIA
grid. All four SAC tests detect round 4 in all replications; detections at
rounds 5-7 are rare. This is a SAC-only comparison and does not replace the
original CLEFIA combined H=5, which is driven by a balance detector.

## Null calibration matters

At primary alpha=0.001, nominal max-axis chi-square/Sidak rejection rates
range from 0.00162 to 0.00219 across the six simulated designs. For the 64-bit,
N=64 case, the rate is 0.00219 (Wilson interval 0.001994-0.002405), compared
with 0.00093 (0.000806-0.001074) after Monte Carlo calibration.
The finding concerns this smaller-budget adaptation, not all settings in
the source paper.

Calibration does **not** make realized sizes identical. The calibrated
histogram rates range from 0.000725 to 0.00123, whereas count ranges from
0.00030 to 0.00075 because its count threshold is discrete. Some conditional
held-out intervals exceed 0.001; for example, Basic at 128 bits, N=256 has
0.00123 (0.001086-0.001393). Calibration-tail estimation with 100,000 draws
is finite. The plus-one rule is a valid marginal rank construction when
calibration and test samples are jointly repeated under the ideal-label
model; the reported held-out intervals condition on the particular learned
calibration and exclude retraining uncertainty. Results are therefore
query-matched comparisons at common nominal ceilings, not comparisons at
perfectly identical realized null size.

## Implications for the manuscript

The original H values remain results for the original detector family and
budgets. They cannot be described as detector-independent diffusion limits:
an added histogram observable detects RECTANGLE round 7 reliably at budgets
where the original tail-count detector usually does not. The result strengthens
the manuscript's argument that summary stability is conditional on how
evidence is aggregated and on which detectors are admitted.

Basic aggregates departures across the full count histogram; count retains
only cells with extreme individual p-values. Their divergent behavior is
consistent with departures that the extreme-cell tally discards. A histogram
rejection does not by itself identify biased Boolean coordinates: dependence
among cell statistics may also depart from an ideal-permutation reference.
The experiment does not demonstrate a new key-recovery attack or a security
break of full-round RECTANGLE.

The earlier statement that no direct SAC-method comparison exists should be
replaced with the bounded comparison above. Limits remain: one fixed key per
cipher, selected native-round windows, smaller-budget adaptations, finite
calibration and pointwise intervals, and no SAC-2, neural or exhaustive search
comparison. The nominal results should accompany the primary calibrated
results so that increased null rejection is not mistaken for increased power.

## Evidence and reproduction

Permanent data: [data/followup/sac_directed_2026-11-10](../data/followup/sac_directed_2026-11-10).
The archive contains 15,000 individual cipher condition records, 3,000 input
prefix hashes, selected count-matrix snapshots, all six calibration samples,
null summaries, 480 detection-rate rows, 360 paired contrasts (90 primary),
execution metadata, and PNG/SVG figures. Individual null-validation draws are
regenerated from the recorded seeds rather than retained as raw matrices.

The [verification record](../data/followup/sac_directed_2026-11-10/verification.json)
checks all input hashes, 120 snapshot conditions, source hashes, all rejection
counts, paired outcomes, McNemar p-values and Holm adjustments. The generation
stage used Python 3.12.13, NumPy 2.2.6, SciPy 1.15.3 on Windows 11. Runs took
about 172 s (RECTANGLE), 343 s (CLEFIA), 138 s (64-bit null) and 339 s
(128-bit null), executed concurrently; these are workload times, not cipher
performance benchmarks.

Reproduction commands and the frozen protocol are in
[experiments/sac](../experiments/sac). Run the analysis and verifier after the
four generation commands:

```bash
python experiments/sac/analyze_comparison.py --input results/sac-directed
python experiments/sac/verify_comparison.py --input results/sac-directed
```
