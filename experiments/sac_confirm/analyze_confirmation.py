"""Prespecified per-key paired inference; never pool input replicates as keys."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

import confirmation as C


def analyze(folder):
    reps=C.P['replications_per_key'];rates=[];paired=[]
    for key in C.KEYS:
        raw=C.read_csv(folder/(key['key_id']+'_raw.csv'))
        assert len(raw)==reps*len(C.P['sample_sizes'])*len(C.P['analysis_rounds'])
        for N in C.P['sample_sizes']:
            for native in C.P['analysis_rounds']:
                selected=sorted((r for r in raw if int(r['N'])==N and int(r['native_round'])==native),key=lambda r:int(r['replicate']))
                assert [int(r['replicate']) for r in selected]==list(range(reps))
                stats=np.array([[float(r['stat_'+method]) for method in C.METHODS] for r in selected])
                for bank in C.P['calibration_banks']:
                    for pi,policy in enumerate(C.POLICIES):
                        d=C.decisions(stats,key['key_index'],N,bank,policy)
                        for j,method in enumerate(C.METHODS):
                            detected=int(d[:,j].sum());low,high=C.SAC.wilson(detected,reps)
                            rates.append({**key,'N':N,'native_round':native,'bank':bank,'policy':policy,
                                          'method':method,'replications':reps,'detections':detected,
                                          'rate':detected/reps,'wilson95_low':low,'wilson95_high':high,
                                          'target_iid_size':C.SIZE.target(N,policy),'query_budget':N*65})
                        for j,method in enumerate(C.METHODS[1:],1):
                            a,b=d[:,0],d[:,j]
                            cells=np.array([np.sum(~a&~b),np.sum(a&~b),np.sum(~a&b),np.sum(a&b)],dtype=int)
                            discordant=int(cells[1]+cells[2])
                            p=1. if not discordant else float(binomtest(int(cells[1]),discordant,.5).pvalue)
                            seed=[C.P['base_seed'],504,key['key_index'],pi,bank,N,native,j]
                            boot=np.random.default_rng(np.random.SeedSequence(seed)).multinomial(reps,cells/reps,size=10000)
                            ci=np.quantile((boot[:,2]-boot[:,1])/reps,[.025,.975])
                            selected_primary=C.planned(N,native,method)
                            role=('primary_confirmation' if bank==0 and policy==C.POLICIES[0] and selected_primary
                                  else 'secondary_grid' if bank==0 and policy==C.POLICIES[0] else 'sensitivity')
                            paired.append({**key,'N':N,'native_round':native,'bank':bank,'policy':policy,
                                           'comparator':method,'replications':reps,'count_only':int(cells[1]),
                                           'comparator_only':int(cells[2]),'both':int(cells[3]),'neither':int(cells[0]),
                                           'comparator_minus_count_rate':float((cells[2]-cells[1])/reps),
                                           'paired_bootstrap95_low':float(ci[0]),'paired_bootstrap95_high':float(ci[1]),
                                           'mcnemar_exact_p':p,'planned_contrast':selected_primary,
                                           'holm_primary18_p':None,'holm_grid162_p':None,'analysis_role':role})
    for bank in C.P['calibration_banks']:
        for policy in C.POLICIES:
            family=[r for r in paired if r['bank']==bank and r['policy']==policy]
            assert len(family)==162
            for r,p in zip(family,C.holm([r['mcnemar_exact_p'] for r in family])):r['holm_grid162_p']=float(p)
            selected=[r for r in family if r['planned_contrast']]
            assert len(selected)==18
            for r,p in zip(selected,C.holm([r['mcnemar_exact_p'] for r in selected])):r['holm_primary18_p']=float(p)
    C.write_csv(folder/'detection_rates.csv',rates)
    C.write_csv(folder/'paired_comparisons.csv',paired)
    C.write_csv(folder/'planned_comparisons.csv',[r for r in paired if r['planned_contrast']])
    descriptions=[]
    for bank in C.P['calibration_banks']:
        for policy in C.POLICIES:
            for focus in C.P['primary_contrasts_per_key']:
                N,r,method=focus['N'],focus['round'],focus['comparator']
                selected=[x for x in paired if x['key_type']=='random' and x['bank']==bank and x['policy']==policy and x['N']==N and x['native_round']==r and x['comparator']==method]
                assert len(selected)==8
                effect=np.array([x['comparator_minus_count_rate'] for x in selected])
                sign=1 if method=='basic' else -1
                def selected_rates(m):
                    return [x['rate'] for x in rates if x['key_type']=='random' and x['bank']==bank and x['policy']==policy and x['N']==N and x['native_round']==r and x['method']==m]
                description={'bank':bank,'policy':policy,'N':N,'native_round':r,'comparator':method,
                             'random_keys':8,'effect_mean':float(effect.mean()),
                             'effect_min':float(effect.min()),'effect_max':float(effect.max()),
                             'count_rate_mean':float(np.mean(selected_rates('count'))),
                             'comparator_rate_mean':float(np.mean(selected_rates(method))),
                             'keys_in_planned_direction':int(np.sum(sign*effect>0)),
                             'keys_significant_planned_holm18':sum(x['holm_primary18_p']<.05 and sign*x['comparator_minus_count_rate']>0 for x in selected),
                             'keys_significant_opposite_holm18':sum(x['holm_primary18_p']<.05 and sign*x['comparator_minus_count_rate']<0 for x in selected),
                             'keys_significant_planned_holm162':sum(x['holm_grid162_p']<.05 and sign*x['comparator_minus_count_rate']>0 for x in selected)}
                descriptions.append(description)
    C.write_csv(folder/'random_key_summary.csv',descriptions)
    metadata=[json.loads((folder/(key['key_id']+'_metadata.json')).read_text(encoding='utf-8')) for key in C.KEYS]
    defaults=[r for r in paired if r['key_id']=='default' and r['analysis_role']=='primary_confirmation']
    primary=[r for r in paired if r['analysis_role']=='primary_confirmation']
    summary={'schema':'sac-key-confirmation-summary/1','protocol':C.P,'keys':C.KEYS,
             'execution_commits':sorted({m['execution_commit'] for m in metadata}),
             'source_sha256':C.source_hashes(),'new_cipher_replications':len(C.KEYS)*reps,
             'new_keys_random':8,'default_controls':1,'new_null_draws':0,
             'raw_rows':sum(m['raw_rows'] for m in metadata),'input_prefix_rows':sum(m['input_prefix_rows'] for m in metadata),
             'rate_rows':len(rates),'paired_rows':len(paired),'primary_family_size':len(primary),
             'primary_significant':sum(r['holm_primary18_p']<.05 for r in primary),
             'duplicate_base_inputs_within_keys':sum(m['duplicate_input_bases'] for m in metadata),
             'base_intersections_with_discovery':sum(m['discovery_base_intersection'] for m in metadata),
             'fresh_default_control':defaults,
             'random_key_primary_descriptions':[r for r in descriptions if r['bank']==0 and r['policy']==C.POLICIES[0]],
             'random_key_all_descriptions':descriptions,
             'scope':'Independent fresh input streams conditional on reused frozen calibration. Eight randomly sampled key clusters, not 4000 independent keys. Per-key intervals condition on a key; cross-key means/ranges are descriptive. No all-key or mechanism claim.'}
    C.save_json(folder/'analysis_summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('new_cipher_replications','primary_significant','fresh_default_control','random_key_primary_descriptions')},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args();analyze(args.input)


if __name__=='__main__':main()
