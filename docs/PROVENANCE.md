# Provenance and packaging

The supplied research workspace was measured and audited on 10 November 2026
(Asia/Jakarta). This package is a separate local copy; the draft manuscript,
journal template, and original experiment folders remain outside it.

`provenance/source_inventory.json` records, for every copied source artifact:

- a relative path in the original workspace;
- a relative path in this repository;
- the original SHA-256 hash;
- the packaged SHA-256 hash;
- the packaging transformation, if any.

The Python measurement scripts are copied byte-for-byte. Numeric CSV files,
summary JSON, original measurement checkpoints, and figures retain their
measured bytes. Only `ambiente.json` output-directory fields were replaced by
portable repository paths. Text logs/reports were converted to UTF-8 LF and
machine-specific workspace paths were replaced with `<original-workspace>`.
CPU, OS, Python/NumPy, parameters, seeds, and historical source hashes remain.

Original source ZIP backups and the old workspace manifest are omitted to
avoid duplicate code and hashes referring to a different folder layout.
The official C files and license were moved to `third_party/` and `LICENSES/`.
The original compiled executable and debug symbols are not distributed.

Portable checkpoint pairs are additional representations, not new samples.
Each JSON points to its original pickle and records that pickle's hash.
Dictionary keys become JSON strings; numeric dtypes, shapes and values stay
the same. No object arrays are stored. Use `scripts/read_checkpoint.py` to
decode them without pickle.

`provenance/SHA256SUMS.json` covers the packaged code, documentation, data,
figures and portable exports. It excludes itself, Git internals and ignored
working outputs. Git newline conversion is disabled so checksums survive
Windows/Linux clones. The manifest is an integrity inventory, not a signed
authenticity statement. Update it deliberately if tracked content is changed.

Original environment manifests contain source hashes for the particular
measurement version used for each run. Early scalar and later batch versions
can differ; current source cannot simultaneously match every historical hash.
The scalar/batch equality record is in
`data/reference/validasi/kesetaraan_batch.json`.

The Linux C validation added on 10 November 2026 is new follow-up evidence,
stored under `data/validation/sparkle_c_2026-11-10/`. Reports are the exact JSON
bytes downloaded from workflow run 42790712675; the execution summary records
their hashes, artifact IDs and artifact archive hashes. The source inventory
continues to describe the original package, while the current checksum manifest
also covers this added evidence. None of `data/reference/` or the retained
official C sources was modified by the follow-up.

The directed SAC comparison is a second follow-up under
`data/followup/sac_directed_2026-11-10/`. Its protocol and generation code were
frozen in commit `b36f15ed785755be8068b898b59dc0aea8747b2a` before main
results were inspected. Execution metadata record the exact hashes of those
sources. Analysis and verification were added after generation and have their
own tracked source. Original `data/reference/`, production cipher/metric code
and the retained C reference remain unchanged. The new vector evaluators are
experiment-local scheduling implementations checked against scalar traces.

The size-matched SAC reanalysis on 11 November 2026 uses the unchanged archived
RECTANGLE sufficient statistics and new null simulations. Its plan, generator,
analysis, tests and verifier were frozen together in commit
`1e3b424da936cb148dc7b536c990cdfb36a36e4f` before the main null generation.
Selection was informed by the historical cipher findings, so this is a post
hoc reanalysis rather than independent confirmation. Evidence under
`data/followup/sac_size_matched_2026-11-11/` retains sufficient upper tails,
validation indices, count frequencies, seeds, source and complete-array hashes.
No cipher was evaluated again. Full-array versus compressed-record decisions
were checked at execution; fast verification recomputes all archived inference
from sufficient records. The historical data and experiment sources remain
unchanged. See [interpretation and scope](SAC_SIZE_MATCHING.md).

The fresh-input RECTANGLE confirmation on 11 November 2026 freezes its plan,
key list, explicit-key evaluator, inference, tests and verifier in commit
`71853e7dbf0a1dfccb4d80146f29a824ead217a4` before main input generation.
It uses the same default key plus eight seed-selected random keys, and new
input streams. The targets were selected from prior results; fresh samples
provide independent input confirmation conditional on the reused calibration.
Evidence under `data/followup/sac_fresh_keys_2026-11-11/` records raw statistics,
complete count-value/axis-bin histograms, input-prefix hashes, matrix aggregates,
snapshots and source/calibration hashes. The historic data, production code,
prior experiment code and trained null banks remain unchanged. See
[scope and per-key interpretation](SAC_FRESH_KEYS.md).

No author ORCID, GitHub account, article DOI, funding source, release date or
license choice was invented. Citation names and affiliation come from the
draft manuscript and should be reviewed by its authors before publication.
