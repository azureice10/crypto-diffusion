"""Verify frozen sources, retained sufficient records and all reanalysis rows."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.stats import binomtest

import size_statistics as S
from run_size_match import ROOT, P, load_calibration


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))


def verify(folder):
    commits=set();probes=0;full_checks=0;null_expected={}
    for N in P['sample_sizes']:
        for bank in range(P['calibration_banks']):
            path=folder/f'calibration_N{N}_bank{bank}.json'
            metadata=json.loads(path.read_text(encoding='utf-8'))
            assert metadata['draws']==P['training_draws_per_bank_and_design']
            assert metadata['seed_entropy']==[P['base_seed'],401,P['state_bits'],N,bank]
            commits.add(metadata['execution_commit'])
            for name,expected in metadata['source_sha256'].items():
                assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
            binary=path.with_suffix('.npz')
            assert hashlib.sha256(binary.read_bytes()).hexdigest()==metadata['archive_sha256']
            cal=load_calibration(folder,N,bank)
            for values in cal.values():
                assert values.shape==(P['retained_upper_tail'],)
                assert np.all(np.isfinite(values)) and np.all(values[1:]>=values[:-1])
            probes+=metadata['compression_probe_decisions_checked']
        record=json.loads((folder/f'validation_N{N}.json').read_text(encoding='utf-8'))
        assert record['seed_entropy']==[P['base_seed'],402,P['state_bits'],N]
        assert record['draws']==P['validation_draws_per_design']
        assert hashlib.sha256((folder/f'validation_N{N}.npz').read_bytes()).hexdigest()==record['archive_sha256']
        for name,expected in record['source_sha256'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
        commits.add(record['execution_commit']);full_checks+=record['compression_full_decisions_checked']
        with np.load(folder/f'validation_N{N}.npz',allow_pickle=False) as archive:
            data={key:archive[key] for key in archive.files}
        assert int(data['count_histogram'].sum())==P['validation_draws_per_design']
        assert np.all(data['count_values']>=record['count_candidates_minimum'])
        assert len(set(data['count_indices'].tolist()))==len(data['count_indices'])
        count_candidates_hist=np.bincount(data['count_values'],minlength=len(data['count_histogram']))
        minimum=record['count_candidates_minimum']
        np.testing.assert_array_equal(count_candidates_hist[minimum:],data['count_histogram'][minimum:])
        for j,method in enumerate(('count','basic','max_axis')):
            uniforms=S.rng(404,N,j).random(P['validation_draws_per_design'])
            assert S.array_sha256(uniforms)==record['uniform_array_sha256'][method]
            for bank in range(P['calibration_banks']):
                cal=load_calibration(folder,N,bank)
                for policy in S.POLICIES:
                    if method=='count':
                        v=data['count_values'];u=uniforms[data['count_indices']]
                        decision=S.count_reject(v,N,policy,None if policy==S.POLICIES[0] else u)
                        success=int(decision.sum())
                        if policy==S.POLICIES[0]:
                            assert success==int(data['count_histogram'][S.count_spec(N)['critical']:].sum())
                    else:
                        v=data[method];indices=data[method+'_indices'];u=uniforms[indices]
                        assert len(v)==P['retained_upper_tail'] and np.all(v[1:]>=v[:-1])
                        assert len(set(indices.tolist()))==len(indices)
                        assert indices.min()>=0 and indices.max()<P['validation_draws_per_design']
                        decision=S.hist_reject(cal[method],v,P['training_draws_per_bank_and_design'],S.target(N,policy),
                                               None if policy==S.POLICIES[0] else u)
                        success=int(decision.sum())
                    null_expected[N,bank,policy,method]=success
    assert len(commits)==1
    source=ROOT/P['source_data_folder']/'cipher_raw_rectangle.csv'
    retained=subprocess.run(['git','show',P['source_data_commit']+':'+source.relative_to(ROOT).as_posix()],
                            cwd=ROOT,check=True,capture_output=True).stdout
    assert hashlib.sha256(retained).digest()==hashlib.sha256(source.read_bytes()).digest()
    # Reconstruct binary decisions directly from raw sufficient statistics;
    # do not use the analyzer's decisions() or generated summary as an oracle.
    raw=read_csv(source);lookup={(int(r['N']),int(r['native_round']),int(r['replicate'])):r for r in raw}
    assert len(lookup)==7500
    expected={}
    for N in P['sample_sizes']:
        for native in P['native_rounds']:
            stats=np.array([[float(lookup[N,native,i]['stat_'+m]) for m in S.METHODS] for i in range(500)])
            for bank in range(P['calibration_banks']):
                cal=load_calibration(folder,N,bank)
                for policy in S.POLICIES:
                    columns=[]
                    for j,m in enumerate(S.METHODS):
                        u=None if policy==S.POLICIES[0] else S.rng(403,N,j).random(500)
                        if j==0: v=S.count_reject(stats[:,j],N,policy,u)
                        else: v=S.hist_reject(cal['basic' if j==1 else 'max_axis'],stats[:,j],
                                               P['training_draws_per_bank_and_design'],S.target(N,policy),u)
                        columns.append(v)
                    expected[N,native,bank,policy]=np.stack(columns,axis=1)
    rates=read_csv(folder/'detection_rates.csv');paired=read_csv(folder/'paired_comparisons.csv')
    assert len(rates)==360 and len(paired)==270
    for row in rates:
        key=int(row['N']),int(row['native_round']),int(row['bank']),row['policy']
        successes=int(expected[key][:,S.METHODS.index(row['method'])].sum())
        assert int(row['detections'])==successes and float(row['rate'])==successes/500
        np.testing.assert_allclose([float(row['wilson95_low']),float(row['wilson95_high'])],S.SAC.wilson(successes,500),rtol=1e-12,atol=1e-15)
    for row in paired:
        key=int(row['N']),int(row['native_round']),int(row['bank']),row['policy']
        d=expected[key];a=d[:,0];b=d[:,S.METHODS.index(row['comparator'])]
        cells=np.array([np.sum(~a&~b),np.sum(a&~b),np.sum(~a&b),np.sum(a&b)],dtype=int)
        assert [int(row[k]) for k in ('neither','count_only','comparator_only','both')]==cells.tolist()
        discord=int(cells[1]+cells[2]);p=1. if not discord else binomtest(int(cells[1]),discord,.5).pvalue
        np.testing.assert_allclose(float(row['mcnemar_exact_p']),p,rtol=1e-12,atol=1e-300)
        assert float(row['comparator_minus_count_rate'])==(cells[2]-cells[1])/500
        pi=S.POLICIES.index(row['policy']);j=S.METHODS.index(row['comparator'])
        seed=[P['base_seed'],405,int(row['bank']),pi,int(row['N']),int(row['native_round']),j]
        boot=np.random.default_rng(np.random.SeedSequence(seed)).multinomial(500,cells/500,size=10000)
        ci=np.quantile((boot[:,2]-boot[:,1])/500,[.025,.975])
        np.testing.assert_allclose([float(row['paired_bootstrap95_low']),float(row['paired_bootstrap95_high'])],ci,rtol=1e-12,atol=1e-15)
    for bank in range(3):
        for policy in S.POLICIES:
            family=[r for r in paired if int(r['bank'])==bank and r['policy']==policy]
            assert len(family)==45
            p=np.r_[[float(r['mcnemar_exact_p']) for r in family],np.ones(45)]
            order=np.argsort(p,kind='stable');adjusted=np.maximum.accumulate(np.minimum(1.,p[order]*(90-np.arange(90))))
            values=np.empty(90);values[order]=adjusted
            np.testing.assert_allclose(values[:45],[float(r['holm90_adjusted_p']) for r in family],rtol=1e-12,atol=1e-300)
    null=read_csv(folder/'null_validation.csv');assert len(null)==54
    for row in null:
        key=int(row['N']),int(row['bank']),row['policy'],row['method'];success=null_expected[key]
        assert int(row['rejections'])==success
        assert float(row['rate'])==success/P['validation_draws_per_design']
        assert float(row['target_iid_size'])==S.target(key[0],key[2])
        np.testing.assert_allclose([float(row['wilson95_low']),float(row['wilson95_high'])],S.SAC.wilson(success,P['validation_draws_per_design']),rtol=1e-12)
    summary=json.loads((folder/'analysis_summary.json').read_text(encoding='utf-8'))
    assert summary['new_cipher_evaluations']==0
    assert summary['rate_rows']==len(rates) and summary['paired_comparison_rows']==len(paired)
    primary=[r for r in paired if r['interpretation']=='primary_reanalysis']
    assert len(primary)==45
    assert summary['primary_significant_contrasts']==sum(float(r['holm90_adjusted_p'])<.05 for r in primary)
    assert summary['total_calibration_statistic_draws']==P['calibration_banks']*len(P['sample_sizes'])*P['training_draws_per_bank_and_design']
    assert summary['total_held_out_statistic_draws']==len(P['sample_sizes'])*P['validation_draws_per_design']
    for name,expected_hash in summary['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected_hash,name
    report={'schema':'sac-size-verification/1','status':'PASS','execution_commits':sorted(commits),
            'training_archives':P['calibration_banks']*len(P['sample_sizes']),
            'validation_archives':len(P['sample_sizes']),
            'calibration_draws':P['calibration_banks']*len(P['sample_sizes'])*P['training_draws_per_bank_and_design'],
            'held_out_draws':len(P['sample_sizes'])*P['validation_draws_per_design'],
            'training_compression_probe_decisions':probes,'validation_full_compression_decisions':full_checks,
            'raw_cipher_rows_verified_unchanged':len(raw),'rate_rows':len(rates),'paired_rows':len(paired),
            'null_rows':len(null),'source_sha256_records_checked':12,
            'verification_scope':'Integrity of frozen sources and sufficient records; all rate counts, paired outcomes, bootstrap intervals, exact McNemar tests, Holm90 and conditional null summaries recomputed. Full null replay is available through the frozen generator and seeds; not repeated by this fast verifier.'}
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(verify(args.input),indent=2))


if __name__=='__main__':main()
