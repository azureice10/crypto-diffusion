"""Verify descriptive identities, replayed data and synthetic diagnostic records."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binom

import mechanism as M


def close(a,b):np.testing.assert_allclose(a,b,rtol=1e-11,atol=1e-9)


def verify(folder):
    executions=[json.loads(p.read_text(encoding='utf-8')) for p in folder.glob('execution_*.json')]
    assert len(executions)==4 and len({r['execution_commit'] for r in executions})==1
    for record in executions:
        for name,expected in record['source_sha256'].items():assert M.C.digest(M.ROOT/name)==expected,name
    metrics=M.C.read_csv(folder/'condition_metrics.csv');bins=M.C.read_csv(folder/'bin_contributions.csv')
    assert len(metrics)==54 and len(bins)==432
    metric={(r['key_id'],int(r['N']),int(r['native_round'])):r for r in metrics}
    lookup={(r['key_id'],int(r['N']),int(r['native_round']),int(r['bin'])):r for r in bins}
    coordinate_tests=0
    with np.load(folder/'coordinate_maps.npz',allow_pickle=False) as maps:
        for key in M.C.KEYS:
            with np.load(M.SOURCE/(key['key_id']+'_arrays.npz'),allow_pickle=False) as source:
                for N in M.P['sample_sizes']:
                    _,probabilities,_=M.C.SAC.bin_description(N);e=4096*probabilities
                    for ri,native in enumerate(M.P['rounds']):
                        h=source[f'row_hist_N{N}'][:,ri].sum(axis=-2).astype(float)
                        mu=h.mean(axis=0);var=h.var(axis=0,ddof=0);parts=((h-e)**2/e).mean(axis=0)
                        row=metric[key['key_id'],N,native]
                        close(float(row['mean_basic']),parts.sum())
                        close(float(row['shape_component']),np.sum((mu-e)**2/e))
                        close(float(row['scatter_component']),np.sum(var/e))
                        for b in range(8):
                            r=lookup[key['key_id'],N,native,b+1]
                            close([float(r['mean_observed_cells']),float(r['mean_pearson_contribution']),float(r['shape_component']),float(r['scatter_component'])],
                                  [mu[b],parts[b],(mu[b]-e[b])**2/e[b],var[b]/e[b]])
                        total=source[f'sum_counts_N{N}'][ri];R=len(h);phat=total/(R*N)
                        prefix=f"{key['key_id']}_N{N}_r{native}"
                        close(maps[prefix+'_p_hat'],phat)
                        corrected=((total.astype(float)-R*N/2)**2-R*N/4)/((R*N)*(R*N-1))
                        close(maps[prefix+'_unbiased_b2'],corrected)
                        sig=np.minimum(1.,2*binom.cdf(np.minimum(total,R*N-total),R*N,.5)) < .05/221184
                        np.testing.assert_array_equal(maps[prefix+'_marginal_significant'],sig)
                        assert int(row['marginal_significant_cells'])==sig.sum();coordinate_tests+=4096
                        close(float(row['mean_flip_probability']),phat.mean())
                        close(float(row['unbiased_mean_squared_bias']),corrected.mean())
    counts=M.load_counts(folder);raw=M.C.read_csv(M.SOURCE/'default_raw.csv')
    hashes={(int(r['replicate']),int(r['N']),int(r['native_round'])):r['count_matrix_sha256'] for r in raw}
    hash_checks=0
    for case in M.P['default_cases']:
        data=counts[M.case_name(case)];assert data.shape==(500,64,64)
        for i,matrix in enumerate(data):assert M.C.array_digest(matrix)==hashes[i,case['N'],case['round']];hash_checks+=1
    summaries=M.C.read_csv(folder/'surrogate_summary.csv');assert len(summaries)==60
    covrows=M.C.read_csv(folder/'dependence_decomposition.csv');assert len(covrows)==24
    cov={(r['case'],int(r['bin'])):r for r in covrows}
    first_chunk_checks=0
    with np.load(folder/'surrogate_statistics.npz',allow_pickle=False) as surrogate:
        for ci,case in enumerate(M.P['default_cases']):
            name=M.case_name(case);N=case['N'];data=counts[name];train=data[:250];test=data[250:]
            _,probabilities,labels=M.C.SAC.bin_description(N);e=4096*probabilities
            categories=labels[data].reshape(500,4096)
            for b in range(8):
                indicator=categories==b;pi=indicator.mean(axis=0);observed=indicator.sum(axis=1)
                shape=(observed.mean()-e[b])**2/e[b];scatter=observed.var(ddof=0)/e[b]
                independent=np.sum(pi*(1-pi))/e[b]
                r=cov[name,b+1]
                close([float(r['shape']),float(r['observed_scatter']),float(r['product_marginal_scatter']),float(r['net_empirical_covariance'])],
                      [shape,scatter,independent,scatter-independent])
            groups={'actual_train':M.C.SAC.statistics(train,N),'actual_holdout':M.C.SAC.statistics(test,N)}
            for mi,model in enumerate(M.MODELS):
                stats=surrogate[name+'_'+model];assert stats.shape==(10000,4) and np.all(np.isfinite(stats))
                length=min(M.P['chunk'],10000)
                regenerated=M.draw_model(train,N,model,M.rng(601,ci,mi),length)
                close(M.C.SAC.statistics(regenerated,N),stats[:length]);first_chunk_checks+=length
                groups[model]=stats
            for group,stats in groups.items():
                d=M.decide(stats,N)
                for j,method in enumerate(M.C.METHODS):
                    r=next(x for x in summaries if x['case']==name and x['group']==group and x['method']==method)
                    success=int(d[:,j].sum());assert int(r['detections'])==success
                    close([float(r['rate']),float(r['mean_statistic'])],[success/len(stats),stats[:,j].mean()])
                    close([float(r['wilson95_low']),float(r['wilson95_high'])],M.C.SAC.wilson(success,len(stats)))
    layout_summary=M.C.read_csv(folder/'layout_summary.csv');parents=M.C.read_csv(folder/'layout_parent_rates.csv')
    assert len(layout_summary)==12 and len(parents)==750
    with np.load(folder/'layout_statistics.npz',allow_pickle=False) as layout:
        for ci,case in enumerate(M.P['default_cases']):
            name=M.case_name(case);N=case['N'];test=counts[name][250:];actual=M.C.SAC.statistics(test,N)
            stats=layout[name];assert stats.shape==(250,40,4)
            np.testing.assert_array_equal(stats[:,:,:2],np.broadcast_to(actual[:,None,:2],(250,40,2)))
            generator=M.rng(602,ci)
            first=np.array([generator.permutation(test[0].ravel()) for _ in range(40)]).reshape(40,64,64)
            close(M.C.SAC.statistics(first,N),stats[0])
            original=M.decide(actual,N);permuted=M.decide(stats.reshape(-1,4),N).reshape(250,40,4).mean(axis=1)
            delta=permuted-original;ci_bounds=M.parent_bootstrap(delta,ci)
            for i in range(250):
                r=next(x for x in parents if x['case']==name and int(x['parent_replicate'])==250+i)
                for j,method in enumerate(M.C.METHODS):
                    assert int(r[method+'_original'])==original[i,j]
                    close(float(r[method+'_permuted_rate']),permuted[i,j])
            for j,method in enumerate(M.C.METHODS):
                r=next(x for x in layout_summary if x['case']==name and x['method']==method)
                close([float(r['original_rate']),float(r['permuted_rate']),float(r['permuted_minus_original_rate']),float(r['parent_bootstrap95_low']),float(r['parent_bootstrap95_high'])],
                      [original[:,j].mean(),permuted[:,j].mean(),delta[:,j].mean(),ci_bounds[0,j],ci_bounds[1,j]])
    summary=json.loads((folder/'analysis_summary.json').read_text(encoding='utf-8'))
    assert summary['new_cipher_input_replications']==0 and summary['replayed_cipher_input_replications']==500
    assert summary['surrogate_matrix_draws']==90000 and summary['layout_matrix_draws']==30000
    report={'schema':'sac-mechanism-verification/1','status':'PASS',
            'execution_commits':sorted({r['execution_commit'] for r in executions}),
            'descriptive_conditions':54,'bin_rows':432,'coordinate_tests':coordinate_tests,
            'retained_original_matrix_hashes':hash_checks,'surrogate_first_chunk_replays':first_chunk_checks,
            'layout_parent_rows':750,'layout_draws_with_exact_basic_count_invariance':30000,
            'scope':'Source and raw-matrix hashes, independent bin identities/maps, signed covariance decomposition, all retained synthetic statistics and conditional rates, first surrogate chunks and first-parent permutations, clustered layout intervals. Full synthetic-count replay is reproducible from frozen seeds but is not repeated by this fast verifier.'}
    M.C.save_json(folder/'verification.json',report);print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    verify(parser.parse_args().input)
