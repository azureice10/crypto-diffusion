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

The Indonesian report describes the original workspace layout. Its
`eksperimen_ulang/` paths correspond to `data/reference/` in this repository;
its top-level methods/report files are under `docs/` here. Historical source
ZIP backups are intentionally omitted because the executable source is already
provided, with source hashes and a packaging inventory.

## Validation and limits

Adapter tests, official RECTANGLE/CLEFIA vectors, rank/tie handling, and batch
equivalence checks passed in the recorded execution. Independently compiled
official SPARKLE C validation was **not completed**: Windows Application Control
blocked its executable. The C sources and recorded status are included; no
successful independent C comparison is claimed.

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
