# Cryptographic diffusion and statistical distinguisher experiments

Research supplement for **Empirical Comparison of Diffusion and Statistical
Distinguisher Horizons in RECTANGLE-80, CLEFIA-128, SPARKLE and Alzette**.

Authors listed in the draft: Hermawan Setiawan, Raden Budiarto Hadiprakoso,
and Sri Rosdiana, Politeknik Siber dan Sandi Negara, Indonesia.
This repository is a supplementary artifact, not a published journal article.
Repository: https://github.com/azureice10/crypto-diffusion.
An article DOI has not yet been assigned.

## What is included

- Five complete sample configurations using seeds 2026–2030.
- One larger-sample sensitivity run using seed 2026.
- Eight keys each for RECTANGLE and CLEFIA in the main seed-2026 run.
- Four detection policies, null calibration, and held-out confirmation.
- CSV/JSON results, original checkpoints, portable JSON/NPZ exports, and figures.
- Measurement source, regression tests, environment metadata, and SHA-256 checksums.
- Follow-up Linux validation of SPARKLE scalar/batch traces against official C.
- A directed, paired SAC detector comparison with 500 replications per cipher.

The combined horizons were unchanged across the five seeds and the larger
sample configuration: RECTANGLE 6/25 native rounds, CLEFIA 5/18 native rounds,
SPARKLE 2 steps, and Alzette 4/4 ARX rounds. These describe this protocol;
they are not security ratings or practical attack bounds.

The corrected Spearman coefficient between the significant single-bit linear
fraction and the top differential fraction is approximately 0.583, replacing
0.838 in the initial draft. Two late CLEFIA correlations found with 8,192
discovery inputs were not confirmed using 65,536 independent inputs.

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

A subsequent [paired SAC comparison](docs/SAC_COMPARISON.md) uses identical
query budgets for corrected-count and sample-adapted Basic/Row/Column tests
on RECTANGLE and CLEFIA. At RECTANGLE round 7, N=256, calibrated Basic detects
489/500 versus count 3/500. Seven of 90 primary contrasts remain significant
after Holm correction; six favor a histogram comparator and one favors count.
Null sizes, uncertainty and fixed-key/small-budget limitations are reported
separately. The comparison does not turn original horizons into universal
diffusion boundaries or demonstrate a new full-round attack.

The original `.pkl.gz` files are retained for the original audit scripts.
Prefer the JSON/NPZ exports for inspection. The portable reader uses
`allow_pickle=False`; the package verifier never loads pickle. See the
[limitations](docs/LIMITATIONS.md) and [provenance](docs/PROVENANCE.md).

## Citation and rights

Use [CITATION.cff](CITATION.cff) for the supplement metadata. Cite the final
article separately once its publication details exist.

Licenses are component-specific. The official SPARKLE material retains its GPL
notice. The supplied RECTANGLE/CLEFIA modules did not include verifiable license
grants, and no blanket MIT or other license has been invented for them or for
the research data. See [LICENSE.md](LICENSE.md) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before public redistribution.
The folder is prepared for local Git commit; unresolved publication/reuse rights
are explicitly recorded rather than silently assumed.
