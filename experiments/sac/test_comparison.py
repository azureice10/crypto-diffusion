"""Conformance and statistical invariants for the directed SAC follow-up."""
import json
from pathlib import Path
import random
import time

import numpy as np
from scipy.stats import binom, chi2

import batch_ciphers as B
import sac_statistics as S


def main():
    rng=random.Random(20261110)
    comparisons=0
    for name,cfg in B.CONFIG.items():
        n,wb=cfg['bits'],cfg['word_bits']
        inputs=[0,(1<<n)-1]+[1<<bit for bit in range(n)]+[rng.getrandbits(n) for _ in range(100)]
        words=np.array([[(x>>(wb*i))&((1<<wb)-1) for i in range(4)] for x in inputs],dtype='<u2' if wb==16 else '<u4')
        for key in (None,0,(1<<(80 if n==64 else 128))-1):
            trace=B.P.PRIMITIVES[cfg['source_key']].trace if key is None else B.P.PRIMITIVES[cfg['source_key']].with_key(key)
            expected=[trace(x) for x in inputs]
            for r,state in enumerate(cfg['function'](words,25 if n==64 else 18,key)):
                integers=[sum(int(w)<<(wb*i) for i,w in enumerate(row)) for row in state]
                assert integers==[t[r] for t in expected],(name,key,r)
                comparisons+=len(inputs)
        # Reconstruct all bit-pair counts from independent scalar calls.
        counts,values=B.avalanche_counts(name,12345,(2,),batch_size=2)
        slow=np.zeros((cfg['rounds'],n,n),dtype=np.uint16)
        for row in values:
            x=sum(int(w)<<(i*wb) for i,w in enumerate(row))
            base=B.P.PRIMITIVES[cfg['source_key']].trace(x)
            for i in range(n):
                trace=B.P.PRIMITIVES[cfg['source_key']].trace(x^(1<<i))
                for r in range(cfg['rounds']):
                    slow[r,i]+=np.array([((base[r]^trace[r])>>j)&1 for j in range(n)],dtype=np.uint16)
        assert np.array_equal(counts[2],slow)
    for samples in (64,256,1024):
        cuts,probabilities,_=S.bin_description(samples)
        assert np.isclose(probabilities.sum(),1) and 64*probabilities.min()>5
        for n in (64,128):
            counts=np.random.default_rng(134).binomial(samples,.5,(3,n,n))
            actual=S.statistics(counts,samples)
            transposed=S.statistics(counts.transpose(0,2,1),samples)
            assert np.allclose(actual[:,1],transposed[:,1])
            assert np.allclose(actual[:,2],transposed[:,3])
            # Scalar histogram/Pearson construction independent of vector axes.
            expected=[]
            for matrix in counts:
                hist=np.histogram(matrix,bins=np.r_[-.5,cuts+.5,samples+.5])[0]
                basic=float(sum((o-n*n*p)**2/(n*n*p) for o,p in zip(hist,probabilities)))
                row=[];col=[]
                for index in range(n):
                    rh=np.histogram(matrix[index],bins=np.r_[-.5,cuts+.5,samples+.5])[0]
                    ch=np.histogram(matrix[:,index],bins=np.r_[-.5,cuts+.5,samples+.5])[0]
                    row.append(sum((o-n*p)**2/(n*p) for o,p in zip(rh,probabilities)))
                    col.append(sum((o-n*p)**2/(n*p) for o,p in zip(ch,probabilities)))
                cell=2*binom.cdf(np.minimum(matrix,samples-matrix),samples,.5)
                expected.append([(cell<.001).sum(),basic,max(row),max(col)])
            assert np.allclose(actual,expected)
            p=S.nominal_pvalues(actual,n,samples)
            assert np.all((p>=0)&(p<=1))
    # Strict tails, ties and plus-one finite calibration correction.
    cal={'basic':np.array([1.,2.,2.,4.]),'max_axis':np.array([1.,2.,2.,4.])}
    p=S.monte_carlo_pvalues(np.array([[0.,2.,2.,5.]]),64,64,cal)[0]
    assert abs(p[1]-(4/5+S.coupling(64,64)))<1e-12
    assert abs(p[3]-(1/5+S.coupling(64,64)))<1e-12
    print(json.dumps({'status':'PASS','full_trace_state_comparisons':comparisons,
                      'checks':'three keys, full native traces, independent scalar count matrices, scalar histogram statistics, transpose symmetry, bin expectations, ties and MC correction'},indent=2))


if __name__=='__main__':main()
