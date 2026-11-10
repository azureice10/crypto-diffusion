"""Verify archived SAC data, snapshots, seeds and paired-analysis summaries."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

import sac_statistics as S

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def rows(path):
    with path.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args();folder=args.input
    source_hashes=[]
    for path in sorted(folder.glob('*_metadata_*.json')):
        metadata=json.loads(path.read_text(encoding='utf-8'))
        assert metadata['git_commit']=='b36f15ed785755be8068b898b59dc0aea8747b2a'
        for relative,expected in metadata['source_sha256'].items():
            assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected,relative
        source_hashes.append(metadata['source_sha256'])
    assert len(source_hashes)==4 and all(h==source_hashes[0] for h in source_hashes)
    snapshot_checks=0
    raw_total=0
    decisions={}
    for cipher,n,word_bits in (('rectangle',64,16),('clefia',128,32)):
        raw=rows(folder/f'cipher_raw_{cipher}.csv')
        assert len(raw)==7500
        raw_total+=len(raw)
        lookup={(int(r['replicate']),int(r['N']),int(r['native_round'])):r for r in raw}
        assert len(lookup)==7500
        for N in (64,256,1024):
            with np.load(folder/f'calibration_n{n}_N{N}.npz',allow_pickle=False) as arrays:
                calibration={key:arrays[key] for key in arrays.files}
            for r in (range(4,9) if n==64 else range(3,8)):
                stats=np.array([[float(lookup[i,N,r]['stat_'+m]) for m in S.METHODS] for i in range(500)])
                for policy,pvalues in (('nominal',S.nominal_pvalues(stats,n,N)),
                                       ('MC_calibrated',S.monte_carlo_pvalues(stats,n,N,calibration))):
                    for alpha in (.001,.01):
                        decisions[cipher,N,r,policy,alpha]=pvalues<alpha
        inputs=rows(folder/f'inputs_{cipher}.csv')
        assert len(inputs)==1500
        for r in inputs:
            replicate,N=int(r['replicate']),int(r['N'])
            rng=np.random.default_rng(np.random.SeedSequence([20261110,201,n,replicate]))
            data=rng.bytes(1024*n//8)[:N*n//8]
            assert hashlib.sha256(data).hexdigest()==r['input_sha256']
            assert int(r['query_budget'])==N*(n+1)
        with np.load(folder/f'count_snapshots_{cipher}.npz',allow_pickle=False) as archive:
            assert len(archive.files)==12
            for replicate in (0,1,2,499):
                previous=None
                for N in (64,256,1024):
                    counts=archive[f'rep{replicate}_N{N}']
                    assert counts.shape==(8 if n==64 else 7,n,n)
                    assert counts.min()>=0 and counts.max()<=N
                    if previous is not None:
                        oldN,old=previous
                        assert np.all(counts>=old) and np.all(counts-old<=N-oldN)
                    previous=(N,counts)
                    stats=S.statistics(counts,N)
                    for native_round in (range(4,9) if n==64 else range(3,8)):
                        row=lookup[replicate,N,native_round]
                        assert hashlib.sha256(counts[native_round-1].tobytes()).hexdigest()==row['count_matrix_sha256']
                        expected=np.array([float(row['stat_'+method]) for method in S.METHODS])
                        assert np.allclose(stats[native_round-1],expected,rtol=1e-12,atol=1e-12)
                        snapshot_checks+=1
    rates=rows(folder/'detection_rates.csv');paired=rows(folder/'paired_comparisons.csv')
    assert len(rates)==480 and len(paired)==360
    for r in rates:
        assert int(r['replications'])==500
        assert float(r['rate'])==int(r['detections'])/500
        low,high=S.wilson(int(r['detections']),500)
        assert np.allclose([low,high],[float(r['wilson95_low']),float(r['wilson95_high'])])
        key=(r['cipher'],int(r['N']),int(r['native_round']),r['policy'],float(r['alpha']))
        expected=int(decisions[key][:,S.METHODS.index(r['method'])].sum())
        assert int(r['detections'])==expected
    for r in paired:
        joint=sum(int(r[k]) for k in ('count_only','comparator_only','both','neither'))
        assert joint==500
        assert float(r['comparator_minus_count_rate'])==(int(r['comparator_only'])-int(r['count_only']))/500
        assert float(r['holm_adjusted_p'])+1e-15>=float(r['mcnemar_exact_p'])
        key=(r['cipher'],int(r['N']),int(r['native_round']),r['policy'],float(r['alpha']))
        d=decisions[key];a=d[:,0];b=d[:,S.METHODS.index(r['comparator'])]
        expected=[int(np.sum(a&~b)),int(np.sum(~a&b)),int(np.sum(a&b)),int(np.sum(~a&~b))]
        assert [int(r[k]) for k in ('count_only','comparator_only','both','neither')]==expected
        discordant=expected[0]+expected[1]
        p=1. if not discordant else binomtest(expected[0],discordant,.5).pvalue
        assert np.isclose(float(r['mcnemar_exact_p']),p,rtol=1e-12,atol=1e-300)
    for policy in ('nominal','MC_calibrated'):
        for alpha in (.001,.01):
            family=[r for r in paired if r['policy']==policy and float(r['alpha'])==alpha]
            p=np.array([float(r['mcnemar_exact_p']) for r in family]);order=np.argsort(p)
            adjusted=np.maximum.accumulate(np.minimum(1.,p[order]*(len(p)-np.arange(len(p)))))
            assert np.allclose(adjusted,[float(family[i]['holm_adjusted_p']) for i in order],rtol=1e-12,atol=1e-300)
    assert len(rows(folder/'null_validation.csv'))==96
    for n in (64,128):
        for N in (64,256,1024):
            with np.load(folder/f'calibration_n{n}_N{N}.npz',allow_pickle=False) as archive:
                assert set(archive.files)=={'basic','max_axis'}
                for key in archive.files:
                    values=archive[key]
                    assert values.shape==(100000,) and np.all(np.isfinite(values))
                    assert np.all(values[1:]>=values[:-1])
    report={'schema':'directed-sac-verification/1','status':'PASS','raw_cipher_condition_rows':raw_total,
            'cipher_replicates':1000,'input_prefix_hashes_checked':3000,
            'snapshot_condition_checks':snapshot_checks,'detection_rate_rows':len(rates),
            'paired_comparison_rows':len(paired),'null_validation_rows':96,
            'source_metadata_records':len(source_hashes),
            'source_commit':'b36f15ed785755be8068b898b59dc0aea8747b2a',
            'analysis_checks':'All rejection counts, paired outcomes, exact McNemar p-values and Holm adjustments recomputed from raw statistics'}
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
