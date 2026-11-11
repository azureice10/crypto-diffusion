"""Run the frozen size verifier with one platform-tolerant metadata assertion.

The experiment source and all archived records remain byte-identical. Only the
comparison of a recomputed SciPy binomial-tail target with its CSV decimal is
adapted: rtol=1e-12, atol=0 (the same relative tolerance as nearby tests).
Decision rules, integer counts, hashes, and all other assertions are unchanged.
"""
import hashlib
from pathlib import Path
import sys


FROZEN_SHA256 = '67fde6f3b53041aabd1321bec43fd86f88368a3c3cebf416517a458335635822'
ORIGINAL = "assert float(row['target_iid_size'])==S.target(key[0],key[2])"
PORTABLE = "np.testing.assert_allclose(float(row['target_iid_size']),S.target(key[0],key[2]),rtol=1e-12,atol=0)"


def adapted_source(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_SHA256:
        raise ValueError('Unexpected frozen verifier SHA256')
    source = raw.decode('utf-8')
    if source.count(ORIGINAL) != 1:
        raise ValueError('Expected exactly one target-size metadata assertion')
    return source.replace(ORIGINAL, PORTABLE)


def main():
    path = Path(__file__).resolve().parent / 'sac_size' / 'verify_size_match.py'
    source = adapted_source(path)
    sys.path.insert(0, str(path.parent))
    # Preserve the original command-line interface and file context.
    exec(compile(source, str(path), 'exec'), {'__name__': '__main__', '__file__': str(path)})


if __name__ == '__main__':
    main()
