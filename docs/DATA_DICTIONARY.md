# Data dictionary

All experimental plaintexts and keys were synthetic. Bit indices use the
integer representation consumed by the adapters: bit 0 is the least
significant integer bit. Primitive-specific word/byte layouts are documented
in `MODEL2C/primitif.py`.

## Run folders

| Folder | Meaning |
|---|---|
| `utama_seed2026` | Main full-sample study; eight additional-key measurements for each block cipher |
| `utama_seed2027` … `utama_seed2030` | Four full-sample default-key seed replications |
| `sampel_besar_seed2026` | Larger samples and 32 cosets; no additional-key measurements |
| `audit` | Cross-run, cross-policy, correlation, null, and held-out analyses |
| `validasi` | Validation logs and status, including an explicitly unsuccessful C execution attempt |

The phrase "eight keys" means the default, zero, all-one, and five random keys
for RECTANGLE and CLEFIA. It does not mean eight keys for SPARKLE/Alzette or
eight-key replication on every seed.

## Core files

| File | Unit of observation / purpose |
|---|---|
| `ringkasan.json` | Run parameters, primitive profiles, per-round results, horizons, correlations, key summaries |
| `ambiente.json` | Recorded execution environment and original source hashes; output path was made portable during packaging |
| `per_ronde.csv` | One row per primitive and native round/step; 102 rows per complete nine-configuration run |
| `horizon.csv` | One row per primitive with individual and combined contiguous horizons |
| `diferensial_detail.csv` | Primitive × predefined input-difference pattern × round, multiplicities and distinct output differences |
| `zero_sum_detail.csv` | Primitive × active-set size × round, balanced positions and probabilities |
| `keacakan_dan_kecepatan.csv` | Full trace-output statistics and original CPU trace benchmark |
| `sbox.csv` | Nonlinear-component properties; ARX properties are not equated to small S-box table metrics |
| `kombinasi_pasangan.csv` | Pairwise curve and speed summaries |
| `korelasi_metrik.csv` | Corrected Spearman matrix on pooled primitive × round observations |
| `kemiripan_kurva.csv` | Per-metric pairwise Pearson/RMS values |
| `kurva_ternormalisasi.csv` | Values interpolated onto the normalized round axis |
| `kunci_*.csv`, `avalanche_kunci*.csv` | Eight-key summaries and key-bit avalanche for the main run only |
| `medicoes/*.pkl.gz` | Original full measurements used by the audit |
| `medicoes_portable/*.json`, `*.npz` | The same measurement structure and numeric arrays in a non-pickle format |

## Important columns

| Field | Interpretation |
|---|---|
| `primitif` | Primitive/configuration name |
| `round` | One-based native round, SPARKLE step, or Alzette ARX round |
| `r_norm` | `round / total_rounds` |
| `avalanche_mean` | Mean observed output-flip proportion; reference 0.5 |
| `completeness` | Fraction of input/output bit pairs observed to flip at least once; sample-dependent |
| `sac_violation_frac` | Fraction of cells rejected at the nominal cell threshold, before aggregate decision |
| `sac_effective_alpha` | Actual discrete cell rejection probability under the ideal null |
| `sac_p_value_legacy` | Old aggregate rule using nominal alpha as binomial probability |
| `sac_p_value` | Corrected aggregate rule with actual cell probability and coupling correction |
| `sac_bonferroni_p` | Conservative adjusted minimum cell p-value |
| `lin_sig_pairs`, `lin_sig_frac` | Counts/fractions from the exact binomial/Bonferroni linear test |
| `lin_sig_pairs_legacy` | Old normal-approximation count retained for comparison |
| `lin_bonferroni_p` | Minimum adjusted exact linear p-value |
| `lin_noise_level` | Historical normal-approximation reference line; not the corrected decision rule |
| `diff_top_count`, `diff_top_frac` | Maximum multiplicity/fraction of a full-state output difference over three fixed input patterns |
| `diff_null_p_bound` | Union-bound probability for the triple-repetition decision under the ideal permutation model |
| `zs4_*`, `zs8_*` | Zero-sum measurements for 4/8 active input bits |
| `*_markov_p_bound` | Alternative conservative bound for the count of balanced output bits |
| `deteksi_terisolasi` / `*_after_gap` | Detections after the contiguous horizon; not automatically false positives |
| `distinguisher_horizon` / `H` | Maximum of the five individual contiguous detection horizons |
| `margin_frac` / `sisa_frac` | `1 - H/R`, a descriptive remaining trace fraction |
| `byte_observations` | Number of pooled output bytes; varies with state width |
| `byte_entropy_by_position_mean` | Mean entropy across byte positions, each using the same number of input samples |
| `us_per_eval` | CPU microseconds to evaluate and materialize a complete trace |

Blank individual horizons mean detection was absent at the first sampled
round, so the contiguous horizon is undefined. The combined horizon is zero
if no individual horizon is defined. Do not convert blank individual values
into a claim that the test was not run. Extremely small probabilities can
underflow numerically; a stored zero is not a proof of a mathematically zero
probability.

## Audit files

- `horizon_semua_aturan.csv`: all runs, policies, paired CLEFIA views,
  contiguous horizons, last detections, and detections after gaps.
- `deteksi_per_ronde.csv`: boolean decisions by metric and round.
- `horizon_kunci_semua_aturan.csv`: policy sensitivity for the eight keys.
- `korelasi_audit.csv`: old ordinal ranks versus average-rank Spearman on
  identical points, without slim variants, and within primitives.
- `kemiripan_sensitivitas.csv`: curve comparison with/without the identity point.
- `kalibrasi_null.csv`: one million binomial-statistic samples per case,
  exact ideal-model type-I rates, and Wilson intervals.
- `null_permutasi_langsung.csv`: 500 sampled ideal-permutation restrictions per
  state width; these provide a separate direct sanity check.
- `hipotesis_linear_sebelum_konfirmasi.json`: selected coordinates frozen
  before held-out sampling.
- `linear_deteksi_terisolasi_konfirmasi.csv`: two selected CLEFIA coordinate
  pairs and their independent 65,536-input confirmation results.
- `whitening_statistik.csv`: trace versus completed ciphertext on identical samples.
- `whitening_avalanche_kunci.csv`: trace versus completed-ciphertext endpoint
  for key avalanche on matched samples.
- `benchmark_ulang.csv`: five repeated CPU-time trace benchmarks.

## Portable checkpoint schema

Schema identifier: `measurement-checkpoint/1`. Each metadata JSON holds
`measurement`, an `arrays` inventory, and a paired `arrays_file`. Each
`{"$array":"array_0000"}` value references a numeric array in the NPZ archive.
The inventory stores shape and NumPy dtype; no object arrays are allowed.
Dictionary keys are strings, including the retained-round keys in `ys`.
The JSON records hashes of both the original pickle and the NPZ.

Checkpoint fields are `ava` (avalanche/SAC rows), `lin` (linear rows), `ys`
(retained ±1 output matrices), `diff_rows`, `diff_best`, `zs4`, and `zs8`.
In `ys`, rows index input samples and columns index least-significant-first
integer bits. In each zero-sum row, `zero_rates` is an output-bit vector and
`balanced_positions` lists zero-based bit indices.
