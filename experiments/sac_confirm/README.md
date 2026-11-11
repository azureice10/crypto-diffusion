Fresh-input RECTANGLE confirmation: one default key and eight new random keys.

The two targets were selected from earlier results. The protocol and complete
key list are frozen with the execution code before any main confirmation
inputs are evaluated. Default-key replication and random-key robustness have
different scopes and are reported separately. Three previously frozen null
banks are reused; these are not nine fresh calibration studies.

Primary inference comprises 18 preselected paired contrasts with Holm
correction. The full grid is also retained and corrected across 162 contrasts.
Per-key intervals condition on the key/calibration; descriptive averages over
eight random keys do not turn the number of input replicates into a larger
independent key sample.

Install the pinned requirements and use a full-history Git clone. From the
repository root:

```text
python -B experiments/sac_confirm/prepare_keys.py
python -B experiments/sac_confirm/test_confirmation.py
python -B experiments/sac_confirm/run_confirmation.py --key-indices 0 1 2 --output results/sac-key-confirmation
python -B experiments/sac_confirm/run_confirmation.py --key-indices 3 4 5 --output results/sac-key-confirmation
python -B experiments/sac_confirm/run_confirmation.py --key-indices 6 7 8 --output results/sac-key-confirmation
python -B experiments/sac_confirm/analyze_confirmation.py --input results/sac-key-confirmation
python -B experiments/sac_confirm/verify_confirmation.py --input results/sac-key-confirmation --regenerate-snapshots
python -B experiments/render_sac_confirmation.py --input results/sac-key-confirmation
```

The three generation commands are independent and may run concurrently. Each
key has fresh input streams. The key generator verifies the existing frozen
list without replacing it. Existing generation outputs are never overwritten;
specify only unfinished key indices to resume after an interruption.

Tests compare all nine keys with all 25 scalar native rounds (22,050 state
comparisons), reconstruct complete two-base count matrices from scalar calls
(294,912 matrix cells), and exercise the entire pipeline on unrelated small
smoke streams. Ignored `results/sac-key-smoke-<source-hash>` directories are
retained; an existing directory causes the end-to-end smoke test to skip.

Every analyzed matrix retains its full count-value histogram and row/column
bin histograms. The verifier independently reconstructs all four test statistics
from those records, re-creates input hashes, checks base overlaps and optional
native snapshots, and recomputes paired inference. Sums/squared sums of matrices
and selected full snapshots support later mechanism analysis, without asserting
that all full matrices are stored.

Historical measurements, cipher code, statistical decision implementations
and the three reused calibration banks remain unchanged. Conditional null
sizes from the size-matching study still apply. Full-key-space generalization,
mechanistic attribution and new contiguous horizons are outside this protocol.

The post-generation export wrapper sets `savefig.bbox=tight` so long axis
labels fit in the exported figure. Its hash and rendering configuration are
recorded separately in plot provenance; frozen statistical/plotting sources
and numeric figure data remain unchanged.
