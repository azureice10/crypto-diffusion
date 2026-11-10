"""Sample-adapted SAC histogram tests and independent Monte Carlo calibration."""
from functools import lru_cache
import math

import numpy as np
from scipy.stats import binom, chi2

METHODS = ('count', 'basic', 'row', 'column')


@lru_cache(maxsize=None)
def bin_description(samples):
    # First integer reaching each 1/8-quantile; exact, unequal discrete masses.
    cuts = binom.ppf(np.arange(1,8)/8, samples, .5).astype(int)
    if len(set(cuts)) != 7:
        raise ValueError('Eight distinct bins unavailable')
    cumulative = binom.cdf(cuts,samples,.5)
    probabilities = np.diff(np.r_[0.,cumulative,1.])
    labels = np.searchsorted(cuts,np.arange(samples+1),side='left')
    return cuts, probabilities, labels


@lru_cache(maxsize=None)
def count_description(samples):
    k = np.arange(samples+1)
    cell_p = np.minimum(1.,2*binom.cdf(np.minimum(k,samples-k),samples,.5))
    reject = cell_p < .001
    q = float(binom.pmf(k[reject],samples,.5).sum())
    return reject,q


def statistics(counts,samples):
    counts = np.asarray(counts)
    n = counts.shape[-1]
    _, probabilities, labels = bin_description(samples)
    categories = labels[counts]
    row_hist = np.stack([(categories==i).sum(axis=-1) for i in range(8)],axis=-1)
    col_hist = np.stack([(categories==i).sum(axis=-2) for i in range(8)],axis=-1)
    row_chi = ((row_hist-n*probabilities)**2/(n*probabilities)).sum(axis=-1)
    col_chi = ((col_hist-n*probabilities)**2/(n*probabilities)).sum(axis=-1)
    global_hist = row_hist.sum(axis=-2)
    basic = ((global_hist-n*n*probabilities)**2/(n*n*probabilities)).sum(axis=-1)
    reject,_ = count_description(samples)
    return np.stack((reject[counts].sum(axis=(-1,-2)), basic,
                     row_chi.max(axis=-1),col_chi.max(axis=-1)),axis=-1)


def coupling(n,samples):
    return min(1.,math.ldexp(float((samples*(n+1))**2),-n))


def nominal_pvalues(stats,n,samples):
    _,q = count_description(samples)
    cell_min = chi2.sf(np.asarray(stats)[...,2:],7)
    # Sidak aggregation reproduces the paper's row/column decision rule.
    # The independent-label null makes rows (and separately columns) disjoint.
    family = -np.expm1(n*np.log1p(-np.minimum(cell_min,1.)))
    result = np.concatenate((binom.sf(np.asarray(stats)[...,0:1]-1,n*n,q),
                             chi2.sf(np.asarray(stats)[...,1:2],7), family),axis=-1)
    return np.minimum(1.,result+coupling(n,samples))


def monte_carlo_pvalues(stats,n,samples,calibration):
    stats = np.asarray(stats)
    values = nominal_pvalues(stats,n,samples)
    for j,key in ((1,'basic'),(2,'max_axis'),(3,'max_axis')):
        reference = calibration[key]
        # Include ties, plus-one finite-MC rank p-value. Calibration independent
        # of all validation and cipher inputs. Row/column share a null law.
        tails = len(reference)-np.searchsorted(reference,stats[...,j],side='left')
        values[...,j] = np.minimum(1.,(1+tails)/(len(reference)+1)+coupling(n,samples))
    return values


def sample_null_statistics(n,samples,repetitions,rng,chunk=1000):
    """Independent labels yield independent Bin(N,1/2) cells.

    Generate row histograms directly: their sum is the global histogram and
    their maximum Pearson statistic has both the row and column max-null law.
    This is a sufficient-statistic simulation, not a full cipher execution.
    """
    _, probabilities,_ = bin_description(samples)
    _,q = count_description(samples)
    result = np.empty((repetitions,3))
    for start in range(0,repetitions,chunk):
        length = min(chunk,repetitions-start)
        rows = rng.multinomial(n,probabilities,size=(length,n))
        global_hist = rows.sum(axis=1)
        result[start:start+length,0] = rng.binomial(n*n,q,size=length)
        result[start:start+length,1] = ((global_hist-n*n*probabilities)**2/(n*n*probabilities)).sum(axis=1)
        result[start:start+length,2] = (((rows-n*probabilities)**2/(n*probabilities)).sum(axis=-1)).max(axis=-1)
    return result


def wilson(successes,total,z=1.959963984540054):
    p = successes/total
    denominator=1+z*z/total
    center=(p+z*z/(2*total))/denominator
    half=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/denominator
    return max(0.,center-half),min(1.,center+half)
