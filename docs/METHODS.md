# Methods and interpretation

The study observes per-round traces of RECTANGLE-80, CLEFIA-128, six SPARKLE
big/slim configurations, and Alzette with constant `b7e15162`. CLEFIA uses
18 native rounds. The paired-round audit samples rounds 2,4,…,18 from the
same measurements; it is not an independent experiment. SPARKLE and Alzette
have no extra keyed wrapper. Slim data are prefixes of the corresponding
big measurements and therefore share observations.

The main default-key seeds are 2026–2030, with stable primitive-specific
offsets. The main sizes are 64 avalanche inputs, 2,048 linear/output inputs,
1,024 pairs per each of three input-difference patterns, and 16 cosets per
4/8-active-bit zero-sum test. The larger run uses 256, 8,192, 4,096, and 32.
Larger samples advance the RNG differently; they are not nested extensions
of the smaller samples.

## Detection rules

1. **SAC:** the corrected count test uses the actual discrete probability of
   a cell rejection, not the nominal 0.001 threshold as that probability.
   For 64 samples, that actual probability is about 0.000617378264067.
   The ideal-label model has independent flip indicators on distinct input
   stars despite a shared base output. A conservative finite-domain coupling
   term bounds input overlaps and switching to a random permutation.
2. **Linear:** exact two-sided binomial p-values for sign agreement, followed
   by Bonferroni over the `n²` single-bit pairs per round, plus coupling.
3. **Differential:** retain `TopCount >= 3`; additionally require the union
   bound over triples, the three preselected input differences, and input-pair
   reuse to pass the threshold. This is not a search over all differences.
4. **Zero-sum:** use balanced positions across every sampled coset, with a
   binomial ideal-label model and a bound for duplicated cosets/permutation
   switching. A Markov alternative tests sensitivity to the bit-count model.

The audit policies are `legacy`, `corrected`, `conservative` (SAC Bonferroni
and zero-sum Markov), and `experimentwise`. The last divides 0.001 by five
times the sum of round counts across the nine configurations within one run.
It does not control multiplicity across all seeds, keys, and later analyses.

The contiguous horizon ends at the first failed detection starting from round
one. Later detections are retained separately. Their presence neither extends
that operational horizon nor proves that the later detections are false.

## Correlations and calibration

Spearman uses average ranks for ties; constant inputs have undefined
correlation. Old ordinal-rank results are retained for an identical-data
comparison. Pooled primitive × round coefficients are descriptive and do
not represent independent observations or causal effects.

Null calibration combines exact ideal-model probabilities, one million draws
of binomial statistics per case, and a separate 500 sampled-permutation
restrictions per width. These are not one million full cipher experiments,
nor an estimate of power against every possible distinguisher.

Two CLEFIA coordinates selected at rounds 13/14 in the larger run were frozen
before a held-out test with seed 20261110 and 65,536 new inputs. Neither
passed the selected-family Bonferroni threshold of 0.001.

## Finalization and speed

Traces retain round keys and input whitening but omit final ciphertext
finalization. Constant output XOR preserves plaintext avalanche, XOR
differences, absolute linear correlations, and zero-sum on even sets.
It can change sample Hamming-weight and pooled-byte statistics. Key avalanche
requires separate treatment because final whitening changes with the key.
Matched trace/ciphertext audits are supplied.

Benchmarks measure the scalar Python trace including intermediate-state
materialization, not optimized production encryption. The batch evaluator
accelerates ARX measurement without changing benchmark evaluation. In the
recorded environment all six base seed-2026 measurements were compared with
the original scalar checkpoints and all saved values were exactly equal.

See [METHODOLOGY_ID.md](METHODOLOGY_ID.md) for the mathematical bounds and
[EXPERIMENT_REPORT_ID.md](EXPERIMENT_REPORT_ID.md) for detailed results.
