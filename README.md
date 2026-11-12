# Calibrated Strict Avalanche Criterion Comparisons Reveal Detector-Dependent Diffusion Endpoints

**[Supplement S1–S8 and complete evidence index](docs/MANUSCRIPT_SUPPLEMENT.md)**
· [Standalone supplementary PDF](docs/MANUSCRIPT_SUPPLEMENT.pdf)

Research artifacts by Hermawan Setiawan, Raden Budiarto Hadiprakoso and
Sri Rosdiana, Politeknik Siber dan Sandi Negara, Indonesia.
Repository: https://github.com/azureice10/crypto-diffusion.
Publication metadata will be added after an article DOI is assigned.

## What is included

- Stage A: five default-key seeds, a larger-sample sensitivity run, original
  eight-key analyses, component horizons and restricted five-family probes.
- Stage B: a query-matched SAC detector comparison on RECTANGLE and CLEFIA.
- Stage C: Count-size-matched calibration and randomized α = 0.001 sensitivity,
  with three independent calibration banks and held-out null validation.
- Stage D: 4,500 fresh RECTANGLE replications across a default control and eight
  new random keys, with paired and key-specific inference.
- Stage E: exploratory histogram, marginal-surrogate and layout diagnostics.
- Complete CSV/JSON/NPZ records, source hashes, frozen protocols, conformance
  reports, verification scripts and manuscript-figure reproduction.

Stage-A combined endpoints are RECTANGLE 6/25 native rounds, CLEFIA 5/18
native rounds and SPARKLE 2 steps. Alzette remains detected through its last
observed round: **≥4 (right-censored)**. These are protocol-specific endpoints.

Under Stage-C Count-size matching, Basic detects 480/500 versus Count 3/500
at RECTANGLE round 7, N = 256. The fresh default control gives 478/500 versus
1/500. Basic exceeds Count significantly on all eight new random keys; the
smaller Count–Column contrast is less consistent. Residual conditional size
mismatch and limited key sampling accompany these claims. Full outcomes,
including the lost Stage-B Column advantage and nonsignificant results, are
retained in the supplement. Ancillary correlation/output/timing audits are
indexed separately in S6.

## Repository layout

```text
MODEL2C/                       Measurement, analysis, plotting, and tests
data/reference/
  utama_seed2026/              Main measurements and eight-key analysis
  utama_seed2027/ ...2030/     Default-key seed replications
  sampel_besar_seed2026/       Larger-sample sensitivity
  audit/                      Detection policies, calibration, confirmation
  validasi/                   Recorded validation status and logs
docs/                         Methods, data dictionary, limitations, AI use
provenance/                   Source inventory and package checksums
scripts/                      Verification and portable checkpoint readers
third_party/sparkle/          Official C source and comparison driver
LICENSES/                     Retained upstream license text
```

`utama` means main; `sampel_besar` means larger sample; `primitif` means
primitive; `ronde` means round; `kunci` means key; `koset` means coset.
The existing field names are preserved to keep the measured data unchanged.

## Start here

Verify the frozen files without installing dependencies or loading pickle:

```bash
python scripts/verify_package.py
```

Use Python 3.12 or 3.13 for the executable workflows. The original run recorded
Python 3.13.14 and NumPy 2.2.6; plotting used Matplotlib 3.11.2.

```bash
python -m venv .venv
# Activate the environment using the command for your shell.
python -m pip install -r MODEL2C/requirements.txt
python -B MODEL2C/test_primitif.py
python -B scripts/read_checkpoint.py data/reference/utama_seed2026/medicoes_portable/clefia.json
```

Read [REPRODUCING.md](docs/REPRODUCING.md) for platform-specific environment
activation, the complete workflow, and the distinction between checking the
archive and running a new experiment.

## Run a new complete experiment

```bash
python -B MODEL2C/ulang_eksperimen.py --output-dir results/reproduced
```

This runs the six configurations, audit, confirmation, and figures. It can take
several minutes or longer, depending on the computer. Benchmark results are
machine-dependent. Keep the output in `results/`; the frozen reference data
should not be overwritten. The runner skips completed run directories, so use
a new output directory for a genuinely new execution.

The measurement scripts retain their original folder name and byte contents.
Their standalone default output is `eksperimen_ulang/`; the commands above
explicitly select the ignored `results/` directory instead.

## Read the evidence

- [Full experimental report (Indonesian)](docs/EXPERIMENT_REPORT_ID.md)
- [Mathematical methodology (Indonesian)](docs/METHODOLOGY_ID.md)
- [English methods and interpretation](docs/METHODS.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Main horizon table](data/reference/utama_seed2026/horizon.csv)
- [Detection policies and seed sensitivity](data/reference/audit/horizon_semua_aturan.csv)
- [Spearman comparison](data/reference/audit/korelasi_audit.csv)
- [Held-out CLEFIA confirmation](data/reference/audit/linear_deteksi_terisolasi_konfirmasi.csv)
- [Main figures](data/reference/utama_seed2026/grafik)
- [Validation status](data/reference/validasi/verifikasi_hasil.json)
- [Successful Linux SPARKLE C validation and execution evidence](docs/SPARKLE_C_VALIDATION.md)
- [Directed SAC comparison: results, calibration and interpretation](docs/SAC_COMPARISON.md)
- [Size-matched SAC reanalysis and calibration-bank sensitivity](docs/SAC_SIZE_MATCHING.md)
- [Fresh-input SAC confirmation and eight random keys](docs/SAC_FRESH_KEYS.md)
- [Basic mechanism: marginal shape, covariance and layout diagnostics](docs/SAC_MECHANISM.md)

The Indonesian report describes the original workspace layout. Its
`eksperimen_ulang/` paths correspond to `data/reference/` in this repository;
its top-level methods/report files are under `docs/` here. Historical source
ZIP backups are intentionally omitted because the executable source is already
provided, with source hashes and a packaging inventory.

## Validation and limits

Adapter tests, official RECTANGLE/CLEFIA vectors, rank/tie handling, and batch
equivalence checks passed in the recorded execution. The initial official
SPARKLE C execution was blocked by Windows Application Control; the historical
status is retained unchanged. A Linux follow-up on 10 November 2026 **passed**
on Python 3.12/3.13 and GCC -O0/-O2: 59,846 C states per build and 199,316
scalar/batch comparisons including slim prefixes, with zero mismatches.
The four builds use the same 5,394 input cases; their counts are not independent
statistical replications. See the [protocol and archived JSON evidence](docs/SPARKLE_C_VALIDATION.md).

The [Stage-B paired comparison](docs/SAC_COMPARISON.md) supplies the initial
RECTANGLE/CLEFIA grid at shared query budgets. Its full results remain archived
with their initial calibration. The revised manuscript emphasizes the
subsequent recalibration and independent-input confirmation below.

A [size-matched reanalysis](docs/SAC_SIZE_MATCHING.md) dated 11 November 2026
addresses unequal null sizes on the archived RECTANGLE grid. It preserves
Count and matches histogram targets to its exact discrete size, with a
separately labeled randomized α = 0.001 sensitivity. Nine million calibration
and three million held-out null-statistic draws assess actual sizes and
retraining variation. Existing cipher inputs are reused; this is not an
independent cipher replication or a multiple-key study.

The [fresh-input key confirmation](docs/SAC_FRESH_KEYS.md) subsequently tests
the default key and eight new random RECTANGLE keys using 500 new input
replications per key. It reuses frozen calibration and reports the default
control separately from per-key results and descriptive random-key summaries.
Two preselected contrasts per key receive Holm correction over 18 tests;
the full 162-contrast grid is also retained and corrected separately.

An [exploratory mechanism analysis](docs/SAC_MECHANISM.md) reuses this archive
to study complete histograms, pooled marginal maps, independent-marginal
surrogates and spatial permutations. It explains the statistical source of
Basic's detection and distinguishes that evidence from unique cryptographic
causation. No new cipher input replications or calibration banks are claimed.

The original `.pkl.gz` files are retained for the original audit scripts.
Prefer the JSON/NPZ exports for inspection. The portable reader uses
`allow_pickle=False`; the package verifier never loads pickle. See the
[limitations](docs/LIMITATIONS.md) and [provenance](docs/PROVENANCE.md).

## Citation and rights

Use [CITATION.cff](CITATION.cff) for the supplement metadata. Cite the final
article separately once its publication details exist.

Author-owned code is MIT-licensed; author-owned data, figures and documents
are CC BY 4.0. Third-party components retain their own terms. In particular,
the new grants exclude the historical RECTANGLE/CLEFIA modules whose upstream
permissions remain unresolved. See [LICENSE.md](LICENSE.md) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for exact scope.
