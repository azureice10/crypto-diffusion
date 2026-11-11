"""Analyze archived RECTANGLE statistics under the frozen size-matching rules."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

import size_statistics as S
from run_size_match import ROOT, P, hashes, load_calibration


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))


def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def raw_statistics():
    path=ROOT/P['source_data_folder']/'cipher_raw_rectangle.csv'
    rows=read_csv(path)
    assert len(rows)==7500 and set(r['key_hex'] for r in rows)=={P['key_hex']}
    grouped={}
    for N in P['sample_sizes']:
        for native in P['native_rounds']:
            group=sorted((r for r in rows if int(r['N'])==N and int(r['native_round'])==native),
                         key=lambda r:int(r['replicate']))
            assert [int(r['replicate']) for r in group]==list(range(P['cipher_replications']))
            grouped[N,native]=np.array([[float(r['stat_'+method]) for method in S.METHODS] for r in group])
    return grouped


def decisions(stats,N,cal,policy):
    size=P['cipher_replications'];columns=[]
    for j,method in enumerate(S.METHODS):
        uniform=None if policy==S.POLICIES[0] else S.rng(403,N,j).random(size)
        if j==0: decision=S.count_reject(stats[:,j],N,policy,uniform)
        else: decision=S.hist_reject(cal['basic' if j==1 else 'max_axis'],stats[:,j],
                                      P['training_draws_per_bank_and_design'],S.target(N,policy),uniform)
        columns.append(decision)
    return np.stack(columns,axis=-1)


def analyze(folder):
    data=raw_statistics();rates=[];paired=[]
    historical=read_csv(ROOT/P['source_data_folder']/'detection_rates.csv')
    old={(int(r['N']),int(r['native_round']),r['method']):float(r['rate']) for r in historical
         if r['cipher']=='rectangle' and r['policy']=='MC_calibrated' and float(r['alpha'])==.001}
    for bank in range(P['calibration_banks']):
        for pi,policy in enumerate(S.POLICIES):
            family=[]
            for N in P['sample_sizes']:
                cal=load_calibration(folder,N,bank)
                for native in P['native_rounds']:
                    stats=data[N,native];d=decisions(stats,N,cal,policy);size=len(d)
                    for j,method in enumerate(S.METHODS):
                        successes=int(d[:,j].sum());low,high=S.SAC.wilson(successes,size)
                        rates.append({'cipher':'rectangle','N':N,'native_round':native,
                                      'bank':bank,'policy':policy,'method':method,
                                      'replications':size,'detections':successes,'rate':successes/size,
                                      'wilson95_low':low,'wilson95_high':high,
                                      'target_iid_size':S.target(N,policy),'historical_rate':old[N,native,method],
                                      'query_budget':N*(P['state_bits']+1)})
                    for j,method in enumerate(S.METHODS[1:],1):
                        base,other=d[:,0],d[:,j]
                        cells=np.array([np.sum(~base&~other),np.sum(base&~other),
                                        np.sum(~base&other),np.sum(base&other)],dtype=int)
                        discordant=int(cells[1]+cells[2])
                        p=1. if discordant==0 else float(binomtest(int(cells[1]),discordant,.5).pvalue)
                        # Explicit seed construction follows the protocol's
                        # bootstrap order, rather than the common n,N helper.
                        boot_rng=np.random.default_rng(np.random.SeedSequence(
                            [P['base_seed'],405,bank,pi,N,native,j]))
                        boot=boot_rng.multinomial(size,cells/size,size=10000)
                        ci=np.quantile((boot[:,2]-boot[:,1])/size,[.025,.975])
                        family.append({'cipher':'rectangle','N':N,'native_round':native,
                                       'bank':bank,'policy':policy,'comparator':method,
                                       'replications':size,'count_only':int(cells[1]),
                                       'comparator_only':int(cells[2]),'both':int(cells[3]),'neither':int(cells[0]),
                                       'comparator_minus_count_rate':float((cells[2]-cells[1])/size),
                                       'paired_bootstrap95_low':float(ci[0]),'paired_bootstrap95_high':float(ci[1]),
                                       'mcnemar_exact_p':p,'holm90_adjusted_p':None,
                                       'interpretation':'primary_reanalysis' if bank==P['primary_bank'] and policy==S.POLICIES[0] else 'sensitivity'})
            assert len(family)==45
            for row,p in zip(family,S.holm90([r['mcnemar_exact_p'] for r in family])):
                row['holm90_adjusted_p']=float(p)
            paired.extend(family)
    null=[]
    for N in P['sample_sizes']:
        record=json.loads((folder/f'validation_N{N}.json').read_text(encoding='utf-8'))
        null.extend(record['held_out_results'])
    write_csv(folder/'detection_rates.csv',rates)
    write_csv(folder/'paired_comparisons.csv',paired)
    write_csv(folder/'null_validation.csv',null)
    focus={(r['N'],r['round']) for r in P['focus_conditions']}
    selected=[r for r in paired if (r['N'],r['native_round']) in focus]
    write_csv(folder/'focus_comparisons.csv',selected)
    primary=[r for r in paired if r['interpretation']=='primary_reanalysis']
    bank_effects=[]
    for policy in S.POLICIES:
        for N,native in sorted(focus):
            for method in S.METHODS[1:]:
                rows=[r for r in paired if r['policy']==policy and r['N']==N and r['native_round']==native and r['comparator']==method]
                values=[r['comparator_minus_count_rate'] for r in rows]
                bank_effects.append({'policy':policy,'N':N,'native_round':native,'comparator':method,
                                    'difference_min':min(values),'difference_max':max(values),
                                    'significant_banks':sum(r['holm90_adjusted_p']<.05 for r in rows)})
    write_csv(folder/'calibration_sensitivity.csv',bank_effects)
    executions=[json.loads(p.read_text(encoding='utf-8')) for p in folder.glob('calibration_*.json')]
    summary={'schema':'sac-size-summary/1','protocol':P,'source_sha256':hashes(),
             'execution_commits':sorted(set(r['execution_commit'] for r in executions)),
             'total_calibration_statistic_draws':P['calibration_banks']*len(P['sample_sizes'])*P['training_draws_per_bank_and_design'],
             'total_held_out_statistic_draws':len(P['sample_sizes'])*P['validation_draws_per_design'],
             'new_cipher_evaluations':0,'reused_cipher_replications':500,
             'rate_rows':len(rates),'paired_comparison_rows':len(paired),'null_validation_rows':len(null),
             'primary_tested_contrasts':len(primary),'holm_family_slots':90,
             'primary_significant_contrasts':sum(r['holm90_adjusted_p']<.05 for r in primary),
             'focus_primary':[r for r in selected if r['interpretation']=='primary_reanalysis'],
             'bank_sensitivity':bank_effects,
             'scope':'Post hoc reanalysis of one key and reused cipher samples; no independent confirmation. Primary and randomized policies are distinct. Sizes are held-out conditional rates, not asserted exactly equal; retraining banks are sensitivity analyses.'}
    (folder/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return rates,null


def plots(folder,rates,null):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    methods=S.METHODS;labels=['Count','Basic','Row','Column']
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.7),sharey=True)
    for ax,N in zip(axes,(256,1024)):
        base=[r for r in rates if r['N']==N and r['native_round']==7 and r['bank']==0]
        for offset,(policy,label,color) in enumerate((('historical','Historical alpha 0.001','.8'),
                     (S.POLICIES[0],'Matched to exact Count size','.45'),
                     (S.POLICIES[1],'Randomized alpha 0.001','.1'))):
            chosen=[next(r for r in base if r['method']==m and r['policy']==S.POLICIES[0 if policy=='historical' else S.POLICIES.index(policy)]) for m in methods]
            y=[r['historical_rate'] if policy=='historical' else r['rate'] for r in chosen]
            ax.bar(np.arange(4)+(offset-1)*.24,y,width=.23,color=color,label=label)
            if policy!='historical':
                low=np.array([r['wilson95_low'] for r in chosen]);hi=np.array([r['wilson95_high'] for r in chosen]);v=np.array(y)
                ax.errorbar(np.arange(4)+(offset-1)*.24,v,yerr=[v-low,hi-v],fmt='none',ecolor='black',capsize=2,lw=.7)
        ax.set_xticks(range(4),labels);ax.set_title(f'RECTANGLE round 7, N={N:,}');ax.set_ylim(0,1.07)
        ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_ylabel('Conditional detection frequency')
    handles,legend=axes[0].get_legend_handles_labels();fig.legend(handles,legend,loc='lower center',ncol=3,fontsize=8,frameon=False)
    fig.tight_layout(rect=(0,.1,1,1));fig.savefig(folder/'size_matched_detection.png',dpi=220);fig.savefig(folder/'size_matched_detection.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.7),sharey=True)
    for ax,policy in zip(axes,S.POLICIES):
        for j,(method,label,marker,color) in enumerate((('count','Count','o','black'),('basic','Basic','s','.35'),('max_axis','Row/Column marginal','^','.65'))):
            chosen=sorted((r for r in null if r['bank']==0 and r['policy']==policy and r['method']==method),key=lambda r:r['N'])
            y=np.array([r['rate_to_target'] for r in chosen]);low=np.array([r['wilson95_low']/r['target_iid_size'] for r in chosen]);hi=np.array([r['wilson95_high']/r['target_iid_size'] for r in chosen])
            x=np.arange(3)+(j-1)*.08
            ax.errorbar(x,y,yerr=[y-low,hi-y],marker=marker,color=color,capsize=3,label=label)
        ax.axhline(1,color='black',linestyle='--',lw=.7);ax.set_xticks(range(3),['64','256','1,024'])
        ax.set_xlabel('Base inputs N');ax.grid(alpha=.2)
        ax.set_title('Match exact Count size' if policy==S.POLICIES[0] else 'Randomized alpha 0.001')
    axes[0].set_ylabel('Held-out null rate / target')
    handles,legend=axes[0].get_legend_handles_labels();fig.legend(handles,legend,loc='lower center',ncol=3,frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.1,1,1));fig.savefig(folder/'size_matched_null.png',dpi=220);fig.savefig(folder/'size_matched_null.svg');plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--plots',action='store_true');args=parser.parse_args()
    rates,null=analyze(args.input)
    if args.plots:plots(args.input,rates,null)
    summary=json.loads((args.input/'analysis_summary.json').read_text(encoding='utf-8'))
    print(json.dumps({k:summary[k] for k in ('total_calibration_statistic_draws','total_held_out_statistic_draws','new_cipher_evaluations','primary_significant_contrasts','focus_primary')},indent=2))


if __name__=='__main__':main()
