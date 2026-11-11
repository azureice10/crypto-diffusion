"""Exploratory SAC histogram, marginal, dependence and layout diagnostics."""
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.stats import binom

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'sac_confirm'))
import confirmation as C

P=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
SOURCE=ROOT/P['source_folder']
MODELS=P['surrogate_models']


def case_name(case):return f"N{case['N']}_r{case['round']}"
def rng(stage,*indices):return np.random.default_rng(np.random.SeedSequence([P['base_seed'],stage,*indices]))


def source_hashes():
    record=C.source_hashes()
    paths=list(HERE.glob('*.py'))+[HERE/'protocol.json',HERE/'requirements.txt']
    paths += [SOURCE/(key['key_id']+suffix) for key in C.KEYS for suffix in ('_arrays.npz','_raw.csv')]
    paths += [SOURCE/'verification.json']
    record.update({p.relative_to(ROOT).as_posix():C.digest(p) for p in paths})
    return record


def finish(folder,stage,started,**extra):
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    outputs=[p for p in folder.iterdir() if p.is_file() and not p.name.startswith('execution_')]
    record={'schema':'sac-mechanism-execution/1','stage':stage,'execution_commit':commit,
            'parameters':P,'source_sha256':source_hashes(),'python':sys.version,
            'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
            'elapsed_seconds':time.perf_counter()-started,**extra}
    C.save_json(folder/f'execution_{stage}.json',record)
    print(json.dumps({'stage':stage,'status':'complete','elapsed_seconds':record['elapsed_seconds']}),flush=True)


def parts(histograms,expected):
    h=np.asarray(histograms,dtype=float);e=np.asarray(expected,dtype=float)
    mean=h.mean(axis=0)
    shape=(mean-e)**2/e
    scatter=((h-mean)**2).mean(axis=0)/e
    contribution=((h-e)**2/e).mean(axis=0)
    np.testing.assert_allclose(shape+scatter,contribution,rtol=1e-12,atol=1e-10)
    return mean,shape,scatter,contribution


def squared_bias_unbiased(total,observations):
    return ((np.asarray(total,dtype=float)-observations/2)**2-observations/4)/(observations*(observations-1))


def effective_size(weights):
    weights=np.asarray(weights,dtype=float)
    return 0. if not np.any(weights) else float(weights.sum()**2/np.sum(weights**2))


def decide(stats,N):
    cal=C.calibration(N,0);level=C.SIZE.target(N,C.POLICIES[0])
    return np.stack([C.SIZE.count_reject(stats[:,0],N,C.POLICIES[0])]+[
        C.SIZE.hist_reject(cal['basic' if j==1 else 'max_axis'],stats[:,j],1000000,level)
        for j in (1,2,3)],axis=1)


def descriptive(folder):
    started=time.perf_counter();metrics=[];bins=[];pmfs=[];maps={}
    family=9*2*3*4096;cutoff=.05/family
    for key in C.KEYS:
        raw=C.read_csv(SOURCE/(key['key_id']+'_raw.csv'))
        lookup={(int(r['replicate']),int(r['N']),int(r['native_round'])):r for r in raw}
        with np.load(SOURCE/(key['key_id']+'_arrays.npz'),allow_pickle=False) as archive:
            for N in P['sample_sizes']:
                cuts,probabilities,_=C.SAC.bin_description(N);expected=4096*probabilities
                for ri,native in enumerate(P['rounds']):
                    prefix=f"{key['key_id']}_N{N}_r{native}"
                    vh=archive[f'value_hist_N{N}'][:,ri]
                    global_hist=archive[f'row_hist_N{N}'][:,ri].sum(axis=-2)
                    stats=np.array([[float(lookup[i,N,native]['stat_'+m]) for m in C.METHODS] for i in range(P['replications'])])
                    mean,shape,scatter,contribution=parts(global_hist,expected)
                    np.testing.assert_allclose(contribution.sum(),stats[:,1].mean(),rtol=1e-12,atol=1e-10)
                    totals=archive[f'sum_counts_N{N}'][ri];M=P['replications']*N
                    phat=totals/M;bias=phat-.5;bias2=squared_bias_unbiased(totals,M)
                    pvalues=np.minimum(1.,2*binom.cdf(np.minimum(totals,M-totals),M,.5))
                    significant=pvalues<cutoff;w=bias**2
                    maps[prefix+'_p_hat']=phat;maps[prefix+'_unbiased_b2']=bias2
                    maps[prefix+'_marginal_significant']=significant
                    detected=decide(stats,N)
                    record={'key_id':key['key_id'],'key_type':key['key_type'],'N':N,'native_round':native,
                            'replications':P['replications'],'mean_basic':float(stats[:,1].mean()),
                            'basic_q05':float(np.quantile(stats[:,1],.05)),'basic_median':float(np.median(stats[:,1])),
                            'basic_q95':float(np.quantile(stats[:,1],.95)),
                            'shape_component':float(shape.sum()),'scatter_component':float(scatter.sum()),
                            'shape_fraction_of_mean_basic':float(shape.sum()/contribution.sum()),
                            'mean_flip_probability':float(phat.mean()),'signed_mean_bias':float(bias.mean()),
                            'raw_rms_pooled_bias':float(np.sqrt(w.mean())),
                            'unbiased_mean_squared_bias':float(bias2.mean()),
                            'noise_corrected_rms_display':float(np.sqrt(max(0.,bias2.mean()))),
                            'max_abs_pooled_bias':float(np.abs(bias).max()),
                            'effective_cells_raw_squared_bias':effective_size(w),
                            'effective_input_rows_raw_squared_bias':effective_size(w.sum(axis=1)),
                            'effective_output_columns_raw_squared_bias':effective_size(w.sum(axis=0)),
                            'marginal_significant_cells':int(significant.sum()),
                            'marginal_family_size':family,'marginal_bonferroni_cutoff':cutoff,
                            'underflowed_marginal_pvalues_not_reported_as_zero':int((pvalues==0).sum())}
                    record.update({m+'_detections':int(detected[:,j].sum()) for j,m in enumerate(C.METHODS)})
                    metrics.append(record)
                    boundaries=np.r_[-1,cuts,N]
                    for b in range(8):
                        bins.append({'key_id':key['key_id'],'N':N,'native_round':native,'bin':b+1,
                                     'count_low_inclusive':int(boundaries[b]+1),'count_high_inclusive':int(boundaries[b+1]),
                                     'ideal_probability':float(probabilities[b]),'ideal_expected_cells':float(expected[b]),
                                     'mean_observed_cells':float(mean[b]),'mean_frequency_difference':float(mean[b]/4096-probabilities[b]),
                                     'mean_pearson_contribution':float(contribution[b]),
                                     'shape_component':float(shape[b]),'scatter_component':float(scatter[b]),
                                     'fraction_of_mean_basic':float(contribution[b]/contribution.sum())})
                    frequency=vh.mean(axis=0)/4096
                    ideal=binom.pmf(np.arange(N+1),N,.5)
                    for k in range(N+1):
                        pmfs.append({'key_id':key['key_id'],'N':N,'native_round':native,'count':k,
                                     'mean_cell_frequency':float(frequency[k]),'ideal_binomial_probability':float(ideal[k])})
    C.write_csv(folder/'condition_metrics.csv',metrics);C.write_csv(folder/'bin_contributions.csv',bins)
    C.write_csv(folder/'count_distributions.csv',pmfs);np.savez_compressed(folder/'coordinate_maps.npz',**maps)
    finish(folder,'descriptive',started,condition_rows=len(metrics),bin_rows=len(bins),pmf_rows=len(pmfs),
           coordinate_tests=family,coordinate_null='Fixed-key SAC marginal probability 1/2; exact binomial across independent base draws; Bonferroni does not assume cell independence')


def replay(folder):
    started=time.perf_counter();raw=C.read_csv(SOURCE/'default_raw.csv')
    lookup={(int(r['replicate']),int(r['N']),int(r['native_round'])):r for r in raw}
    retained={case_name(c):np.empty((P['replications'],64,64),dtype=np.uint16) for c in P['default_cases']}
    checks=0
    for replicate in range(P['replications']):
        matrices,_=C.keyed_counts(int(C.KEYS[0]['key_hex'],16),C.input_seed(0,replicate))
        for N,matrix in matrices.items():
            for native in P['rounds']:
                assert C.array_digest(matrix[native-1])==lookup[replicate,N,native]['count_matrix_sha256'];checks+=1
        for case in P['default_cases']:retained[case_name(case)][replicate]=matrices[case['N']][case['round']-1]
        if (replicate+1)%100==0:print(json.dumps({'stage':'replay','replications':replicate+1}),flush=True)
    np.savez_compressed(folder/'default_replayed_counts.npz',**retained)
    finish(folder,'replay',started,matrix_hashes_checked=checks,new_cipher_input_replications=0,
           replayed_cipher_input_replications=P['replications'],archive_sha256=C.digest(folder/'default_replayed_counts.npz'))


def load_counts(folder):
    with np.load(folder/'default_replayed_counts.npz',allow_pickle=False) as archive:return {k:archive[k] for k in archive.files}


def draw_model(train,N,model,generator,length):
    if model=='iid_fair_binomial':return generator.binomial(N,.5,size=(length,64,64)).astype(np.uint16)
    if model=='independent_fitted_binomial':
        return generator.binomial(N,train.mean(axis=0)/N,size=(length,64,64)).astype(np.uint16)
    assert model=='independent_empirical_cells'
    flat=train.reshape(len(train),4096)
    index=generator.integers(len(train),size=(length,4096))
    return flat[index,np.arange(4096)].reshape(length,64,64)


def summarize_stats(stats,N,case,group):
    decisions=decide(stats,N);rows=[]
    for j,method in enumerate(C.METHODS):
        hits=int(decisions[:,j].sum());low,high=C.SAC.wilson(hits,len(stats))
        rows.append({'case':case,'N':N,'group':group,'method':method,'draws':len(stats),'detections':hits,
                     'rate':hits/len(stats),'wilson95_low':low,'wilson95_high':high,
                     'mean_statistic':float(stats[:,j].mean()),'median_statistic':float(np.median(stats[:,j])),
                     'q05_statistic':float(np.quantile(stats[:,j],.05)),'q95_statistic':float(np.quantile(stats[:,j],.95))})
    return rows


def dependence_parts(counts,N):
    _,probabilities,labels=C.SAC.bin_description(N);e=4096*probabilities
    categories=labels[counts].reshape(len(counts),4096)
    per_cell=np.stack([(categories==b).mean(axis=0) for b in range(8)],axis=-1)
    hist=np.stack([(categories==b).sum(axis=1) for b in range(8)],axis=-1)
    mean,shape,scatter,contribution=parts(hist,e)
    independent=(per_cell*(1-per_cell)).sum(axis=0)/e
    return mean,shape,scatter,independent,scatter-independent,contribution


def surrogates(folder):
    started=time.perf_counter();real=load_counts(folder);saved={};summaries=[];covariance=[];fingerprints={}
    T=P['training_replicates'];H=P['holdout_replicates'];B=P['surrogate_draws']
    for ci,case in enumerate(P['default_cases']):
        name=case_name(case);N=case['N'];counts=real[name];train=counts[:T];test=counts[T:T+H]
        for group,data in (('actual_train',train),('actual_holdout',test)):
            summaries+=summarize_stats(C.SAC.statistics(data,N),N,name,group)
        mean,shape,scatter,independent,cov,contribution=dependence_parts(counts,N)
        for b in range(8):covariance.append({'case':name,'bin':b+1,'shape':float(shape[b]),
                                            'observed_scatter':float(scatter[b]),'product_marginal_scatter':float(independent[b]),
                                            'net_empirical_covariance':float(cov[b]),'mean_contribution':float(contribution[b])})
        for mi,model in enumerate(MODELS):
            generator=rng(601,ci,mi);stats=np.empty((B,4));hasher=hashlib.sha256()
            for start in range(0,B,P['chunk']):
                length=min(P['chunk'],B-start);sim=draw_model(train,N,model,generator,length)
                hasher.update(np.ascontiguousarray(sim).tobytes())
                stats[start:start+length]=C.SAC.statistics(sim,N)
            saved[name+'_'+model]=stats;fingerprints[name+'_'+model]=hasher.hexdigest()
            summaries+=summarize_stats(stats,N,name,model)
            print(json.dumps({'stage':'surrogates','case':name,'model':model,'draws':B}),flush=True)
    np.savez_compressed(folder/'surrogate_statistics.npz',**saved)
    C.write_csv(folder/'surrogate_summary.csv',summaries);C.write_csv(folder/'dependence_decomposition.csv',covariance)
    finish(folder,'surrogates',started,synthetic_matrix_draws=B*len(MODELS)*len(P['default_cases']),
           complete_synthetic_counts_sha256=fingerprints,stats_archive_sha256=C.digest(folder/'surrogate_statistics.npz'),
           caveat='Conditional fitted-model intervals exclude parameter-estimation uncertainty; no fresh cipher confirmation or rare-tail recalibration')


def parent_bootstrap(delta,case_index):
    generator=rng(603,case_index);R=len(delta);B=P['bootstrap_draws'];sample=np.empty((B,delta.shape[1]))
    for start in range(0,B,500):
        length=min(500,B-start);indices=generator.integers(R,size=(length,R))
        sample[start:start+length]=delta[indices].mean(axis=1)
    return np.quantile(sample,[.025,.975],axis=0)


def layouts(folder):
    started=time.perf_counter();real=load_counts(folder);saved={};parent_rows=[];summary=[]
    T=P['training_replicates'];H=P['holdout_replicates'];L=P['layout_permutations_per_parent'];invariance=0
    for ci,case in enumerate(P['default_cases']):
        name=case_name(case);N=case['N'];test=real[name][T:T+H];generator=rng(602,ci)
        actual=C.SAC.statistics(test,N);stats=np.empty((H,L,4))
        for i,matrix in enumerate(test):
            shuffled=np.array([generator.permutation(matrix.ravel()) for _ in range(L)]).reshape(L,64,64)
            stats[i]=C.SAC.statistics(shuffled,N)
            np.testing.assert_array_equal(stats[i,:,:2],np.broadcast_to(actual[i,:2],(L,2)))
            invariance+=L
        saved[name]=stats;original=decide(actual,N)
        permuted=decide(stats.reshape(-1,4),N).reshape(H,L,4).mean(axis=1)
        delta=permuted-original;ci_bounds=parent_bootstrap(delta,ci)
        for i in range(H):
            row={'case':name,'parent_replicate':T+i,'permutations':L}
            for j,m in enumerate(C.METHODS):row[m+'_original']=int(original[i,j]);row[m+'_permuted_rate']=float(permuted[i,j])
            parent_rows.append(row)
        for j,m in enumerate(C.METHODS):
            summary.append({'case':name,'method':m,'genuine_holdout_parents':H,'permutations_per_parent':L,
                            'original_rate':float(original[:,j].mean()),'permuted_rate':float(permuted[:,j].mean()),
                            'permuted_minus_original_rate':float(delta[:,j].mean()),
                            'parent_bootstrap95_low':float(ci_bounds[0,j]),'parent_bootstrap95_high':float(ci_bounds[1,j])})
        print(json.dumps({'stage':'layouts','case':name,'parents':H,'permutations_per_parent':L}),flush=True)
    np.savez_compressed(folder/'layout_statistics.npz',**saved)
    C.write_csv(folder/'layout_parent_rates.csv',parent_rows);C.write_csv(folder/'layout_summary.csv',summary)
    finish(folder,'layouts',started,basic_count_exact_invariance_checks=invariance,
           archive_sha256=C.digest(folder/'layout_statistics.npz'),
           caveat='Repeated layout permutations are clustered within real parents; no iid interval over synthetic permutations')


def finalize(folder):
    execution=[json.loads(p.read_text(encoding='utf-8')) for p in folder.glob('execution_*.json')]
    assert {r['stage'] for r in execution}=={'descriptive','replay','surrogates','layouts'}
    C.save_json(folder/'analysis_summary.json',{'schema':'sac-mechanism-summary/1','protocol':P,
        'execution_commits':sorted({r['execution_commit'] for r in execution}),
        'source_sha256':source_hashes(),'descriptive_conditions':54,'coordinate_tests':221184,
        'new_cipher_input_replications':0,'replayed_cipher_input_replications':P['replications'],
        'surrogate_matrix_draws':P['surrogate_draws']*3*3,
        'layout_matrix_draws':P['holdout_replicates']*P['layout_permutations_per_parent']*3,
        'methodological_scope':'Post hoc exploratory diagnosis with exact bin identities, marginal maps, fitted-product surrogates and layout ablations; not unique cryptographic causal identification.'})
