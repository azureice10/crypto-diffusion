Exploratory Basic mechanism diagnostics. See `protocol.json` for the frozen
scope, identities, surrogate models and limits. The confirmation dataset is
reused; the default matrices are replayed with exact hash checks. No new
cipher input replications or calibration banks are introduced.

All-key analyses cover complete distributions, eight-bin contributions and
pooled marginal bias maps. Detailed product-marginal surrogates, covariance
identities and spatial permutations use the default key. These diagnose the
statistical source of detection without claiming a unique cryptographic cause.

From a full-history clone, install `requirements.txt`, then run:

```text
python -B experiments/sac_mechanism/test_mechanism.py
python -B experiments/sac_mechanism/run_mechanism.py all --output results/sac-mechanism
python -B experiments/sac_mechanism/verify_mechanism.py --input results/sac-mechanism
python -B experiments/plot_sac_mechanism.py --input results/sac-mechanism
python -B experiments/report_sac_mechanism.py --input results/sac-mechanism --report-root results/reports
```

Individual stages `descriptive`, `replay`, `surrogates`, `layouts`, `finalize`
allow resuming an unfinished analysis. Completed stage checkpoints are never
overwritten. Preflight uses synthetic data and an unrelated seed; ignored
`results/mechanism-smoke-<source-hash>` records are retained.

The default replay checks every original analysis-round matrix hash before
retaining three selected conditions. Fitted models use replicas 0–249; actual
holdout diagnostics use 250–499. Ten thousand draws per surrogate describe
conditional model behavior, not new cipher replications or an accurate
rare-event calibration. Forty spatial permutations per holdout parent are
clustered within that parent; paired intervals resample parents.

Exact bin identities and net empirical covariance are diagnostics. A product
surrogate removes all cross-cell dependence, not specifically shared-base
dependence. Pooled-coordinate tests target SAC marginals rather than the
original ideal-permutation null. Neither fitted models nor spatial shuffling
identify an S-box/ShiftRows cause without further cryptographic analysis.

The plot/report transformations are separate from frozen statistical code;
their hashes and inputs are recorded in plot/interpretation provenance.
The report command also refreshes `docs/SAC_MECHANISM.md` from the supplied
evidence. Archived evidence uses `data/followup/sac_mechanism_2026-11-11/`.
