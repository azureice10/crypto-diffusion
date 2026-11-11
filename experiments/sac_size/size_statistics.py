"""Explicit deterministic and randomized size-matching decision rules."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np
from scipy.stats import binom

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'sac'))
import sac_statistics as SAC

PROTOCOL = json.loads((HERE / 'protocol.json').read_text(encoding='utf-8'))
POLICIES = ('match_count_nonrandom', 'equal_alpha_randomized')
METHODS = SAC.METHODS


def rng(stage, samples, *suffix):
    return np.random.default_rng(np.random.SeedSequence(
        [PROTOCOL['base_seed'], stage, PROTOCOL['state_bits'], samples, *suffix]))


def array_sha256(values):
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


@lru_cache(maxsize=None)
def count_spec(samples):
    n = PROTOCOL['state_bits']
    _, q = SAC.count_description(samples)
    values = np.arange(n*n+1)
    greater = binom.sf(values, n*n, q)
    mass = binom.pmf(values, n*n, q)
    inclusive = binom.sf(values-1, n*n, q)
    delta = SAC.coupling(n, samples)
    accepted = inclusive+delta < PROTOCOL['nominal_alpha']
    critical = int(values[accepted][0])
    size = float(inclusive[critical])
    alpha = PROTOCOL['nominal_alpha']-delta
    boundary = np.flatnonzero((greater < alpha) & (inclusive >= alpha))
    assert len(boundary) == 1
    boundary = int(boundary[0])
    return {'critical': critical, 'iid_size': size, 'delta': delta,
            'randomized_label_target': alpha,
            'randomized_boundary': boundary,
            'randomized_boundary_probability': float((alpha-greater[boundary])/mass[boundary]),
            'greater': greater, 'mass': mass, 'inclusive': inclusive}


def target(samples, policy):
    s = count_spec(samples)
    return s['iid_size'] if policy == POLICIES[0] else s['randomized_label_target']


def count_reject(values, samples, policy, uniforms=None):
    values = np.asarray(values)
    assert np.all(values == np.floor(values))
    values = values.astype(np.int64)
    spec = count_spec(samples)
    if policy == POLICIES[0]:
        return values >= spec['critical']
    assert policy == POLICIES[1] and uniforms is not None
    u = np.asarray(uniforms)
    return spec['greater'][values]+u*spec['mass'][values] < target(samples, policy)


def hist_reject(reference, observations, total_draws, level, uniforms=None):
    """Return exact decisions, including when only an adequate upper tail is kept.

    Values below a retained tail have only a lower bound on their rank p-value;
    that bound exceeds every allowed level. No truncated rank is reported as a
    full p-value. Including a partly truncated tie at the lowest tail value also
    cannot cause rejection under this coverage requirement.
    """
    ref = np.asarray(reference)
    assert ref.ndim == 1 and np.all(ref[1:] >= ref[:-1])
    assert len(ref) == total_draws or len(ref) > (total_draws+1)*level+2
    if len(ref) < total_draws:
        assert np.count_nonzero(ref > ref[0]) > (total_draws+1)*level+2, 'Retained tail cuts an eligible randomized tie group'
    obs = np.asarray(observations)
    left = np.searchsorted(ref, obs, side='left')
    right = np.searchsorted(ref, obs, side='right')
    greater = len(ref)-right
    equal = right-left
    if uniforms is None:
        score = (1+greater+equal)/(total_draws+1)
    else:
        score = (greater+np.asarray(uniforms)*(equal+1))/(total_draws+1)
    result = score < level
    # The discarded body, including any partially retained boundary tie, is
    # unconditionally known not to reject. This matters for randomized ties.
    if len(ref) < total_draws:
        result = result & (obs > ref[0])
    return result


def upper_tail(values, keep):
    """Sorted upper values and original validation indices."""
    order = np.argsort(values, kind='stable')[-keep:]
    return np.asarray(values)[order], order.astype(np.int64)


def holm90(pvalues):
    """Holm across original 90 slots; untested hypotheses receive p=1."""
    p = np.asarray(pvalues, dtype=float)
    assert len(p) <= 90
    padded = np.r_[p, np.ones(90-len(p))]
    order = np.argsort(padded, kind='stable')
    corrected = np.maximum.accumulate(np.minimum(1., padded[order]*(90-np.arange(90))))
    result = np.empty(90)
    result[order] = corrected
    return result[:len(p)]
