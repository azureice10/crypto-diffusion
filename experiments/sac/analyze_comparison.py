"""Summarize paired SAC experiments and independent held-out null checks."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

import sac_statistics as S

HERE=Path(__file__).resolve().parent
PROTOCOL=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
METHOD_LABELS={'count':'Corrected count','basic':'SAC-Basic adapted',
               'row':'SAC-Row adapted','column':'SAC-Column adapted'}


def load_csv(path):
    with path.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def holm(rows,field='mcnemar_exact_p'):
    pvalues=np.array([r[field] for r in rows])
    order=np.argsort(pvalues)
    adjusted=np.maximum.accumulate(np.minimum(1.,pvalues[order]*(len(rows)-np.arange(len(rows)))))
    for index,value in zip(order,adjusted):rows[index]['holm_adjusted_p']=float(value)


def summarize(folder):
    rates=[];comparisons=[];all_decisions={}
    paired_rng=np.random.default_rng(20261110303)
    for cipher in ('rectangle','clefia'):
        rows=load_csv(folder/f'cipher_raw_{cipher}.csv')
        assert len(rows)==500*3*5
        n=64 if cipher=='rectangle' else 128
        for samples in PROTOCOL['sample_sizes']:
            with np.load(folder/f'calibration_n{n}_N{samples}.npz',allow_pickle=False) as arrays:
                calibration={key:arrays[key] for key in arrays.files}
            for native_round in PROTOCOL['ciphers'][cipher]['analysis_rounds']:
                selected=sorted((r for r in rows if int(r['N'])==samples and int(r['native_round'])==native_round),key=lambda r:int(r['replicate']))
                assert [int(r['replicate']) for r in selected]==list(range(500))
                stats=np.array([[float(r['stat_'+method]) for method in S.METHODS] for r in selected])
                nominal=S.nominal_pvalues(stats,n,samples)
                retained=np.array([[float(r['nominal_p_'+method]) for method in S.METHODS] for r in selected])
                assert np.allclose(nominal,retained,rtol=1e-12,atol=1e-300)
                policies={'nominal':nominal,'MC_calibrated':S.monte_carlo_pvalues(stats,n,samples,calibration)}
                for policy,pvalues in policies.items():
                    for alpha in (PROTOCOL['primary_alpha'],PROTOCOL['sensitivity_alpha']):
                        decisions=pvalues<alpha
                        key=(cipher,samples,native_round,policy,alpha)
                        all_decisions[key]=decisions
                        for index,method in enumerate(S.METHODS):
                            successes=int(decisions[:,index].sum());low,high=S.wilson(successes,len(selected))
                            rates.append({'cipher':cipher,'state_bits':n,'N':samples,'native_round':native_round,
                                          'policy':policy,'alpha':alpha,'method':method,'replications':len(selected),
                                          'detections':successes,'rate':successes/len(selected),
                                          'wilson95_low':low,'wilson95_high':high,'query_budget':samples*(n+1)})
                        base=decisions[:,0]
                        for index,method in enumerate(S.METHODS[1:],1):
                            other=decisions[:,index]
                            cells=np.array([np.sum(~base&~other),np.sum(base&~other),np.sum(~base&other),np.sum(base&other)],dtype=int)
                            discordant=int(cells[1]+cells[2])
                            p=1. if discordant==0 else float(binomtest(int(cells[1]),discordant,.5).pvalue)
                            # Paired bootstrap over the four joint binary outcomes.
                            boot=paired_rng.multinomial(len(base),cells/len(base),size=10000)
                            delta=(boot[:,2]-boot[:,1])/len(base)
                            low,high=np.quantile(delta,[.025,.975])
                            comparisons.append({'cipher':cipher,'N':samples,'native_round':native_round,
                                                'policy':policy,'alpha':alpha,'comparator':method,
                                                'replications':len(base),'count_only':int(cells[1]),
                                                'comparator_only':int(cells[2]),'both':int(cells[3]),'neither':int(cells[0]),
                                                'comparator_minus_count_rate':float((cells[2]-cells[1])/len(base)),
                                                'paired_bootstrap95_low':float(low),'paired_bootstrap95_high':float(high),
                                                'mcnemar_exact_p':p,'holm_adjusted_p':None,
                                                'interpretation':'primary' if policy=='MC_calibrated' and alpha==.001 else 'sensitivity'})
    for policy in ('nominal','MC_calibrated'):
        for alpha in (.001,.01):
            family=[r for r in comparisons if r['policy']==policy and r['alpha']==alpha]
            assert len(family)==90;holm(family)
    write_csv(folder/'detection_rates.csv',rates)
    write_csv(folder/'paired_comparisons.csv',comparisons)
    null=[]
    for n in (64,128):
        null.extend(load_csv(folder/f'null_validation_n{n}.csv'))
    write_csv(folder/'null_validation.csv',null)
    primary=[r for r in comparisons if r['interpretation']=='primary']
    significant=[r for r in primary if r['holm_adjusted_p']<.05]
    summary={'schema':'directed-sac-summary/1','protocol':PROTOCOL,
             'analysis_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'replicates_per_cipher':500,'cipher_condition_count':30,'primary_paired_contrasts':90,
             'primary_holm_significant_contrasts':len(significant),
             'primary_comparator_better_contrasts':sum(r['comparator_minus_count_rate']>0 for r in significant),
             'primary_count_better_contrasts':sum(r['comparator_minus_count_rate']<0 for r in significant),
             'largest_primary_differences':sorted(primary,key=lambda r:abs(r['comparator_minus_count_rate']),reverse=True)[:15],
             'scope':'Fixed-key conditional detection probabilities on the selected round/sample grid; not a universal detector ranking. Wilson intervals and paired bootstrap intervals are pointwise; Holm p-values correct the 90 primary contrasts. Degenerate bootstrap intervals do not establish exact population equivalence.',
             'calibration_note':'MC-calibrated p-values include ties and the plus-one correction. Held-out null intervals condition on the learned calibration sample and do not include variation from retraining that calibration.'}
    (folder/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return rates,comparisons,null


def plots(folder,rates,null):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig,axes=plt.subplots(2,3,figsize=(10,5.4),sharey=True)
    for i,cipher in enumerate(('rectangle','clefia')):
        for j,samples in enumerate((64,256,1024)):
            ax=axes[i,j]
            for method,marker,style,color in zip(S.METHODS,('o','s','^','D'),('-','--',':','-.'),('black','.3','.5','.7')):
                chosen=sorted((r for r in rates if r['cipher']==cipher and r['N']==samples and r['method']==method and r['policy']=='MC_calibrated' and r['alpha']==.001),key=lambda r:r['native_round'])
                ax.plot([r['native_round'] for r in chosen],[r['rate'] for r in chosen],marker=marker,linestyle=style,color=color,label=METHOD_LABELS[method],markersize=4)
            ax.set_title(f'{cipher.upper()}, N={samples:,}')
            ax.set_xticks(PROTOCOL['ciphers'][cipher]['analysis_rounds']);ax.set_ylim(-.04,1.04);ax.grid(alpha=.2)
            if j==0:ax.set_ylabel('Detection frequency')
            if i==1:ax.set_xlabel('Native round')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=4,frameon=False)
    fig.tight_layout(rect=(0,.06,1,1))
    fig.savefig(folder/'detection_curves.png',dpi=220);fig.savefig(folder/'detection_curves.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.2),sharey=True)
    for ax,n in zip(axes,(64,128)):
        for method,marker,color in zip(('count','basic','row'),('o','s','^'),('black','.35','.65')):
            for policy,style in (('nominal','--'),('MC_calibrated','-')):
                if method=='count' and policy=='MC_calibrated':continue
                chosen=sorted((r for r in null if int(r['state_bits'])==n and r['method']==method and r['policy']==policy and float(r['alpha'])==.001),key=lambda r:int(r['N']))
                values=np.array([float(r['rate']) for r in chosen])
                intervals=np.array([[float(r['wilson95_low']),float(r['wilson95_high'])] for r in chosen])
                label='Corrected count (both policies)' if method=='count' else ('Row/Column adapted' if method=='row' else METHOD_LABELS[method])+(' nominal' if policy=='nominal' else ' calibrated')
                ax.errorbar([int(r['N']) for r in chosen],values,yerr=[values-intervals[:,0],intervals[:,1]-values],marker=marker,linestyle=style,color=color,capsize=2,label=label)
        ax.axhline(.001,color='black',linewidth=.7);ax.set_title(f'{n}-bit state');ax.set_xscale('log',base=4)
        ax.set_ylim(bottom=0)
        ax.set_xticks([64,256,1024],['64','256','1,024']);ax.set_xlabel('Base inputs N');ax.grid(alpha=.2)
    axes[0].set_ylabel('Held-out null rejection frequency')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=7)
    fig.tight_layout(rect=(0,.22,1,1));fig.savefig(folder/'null_calibration.png',dpi=220);fig.savefig(folder/'null_calibration.svg');plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args();rates,comparisons,null=summarize(args.input);plots(args.input,rates,null)
    summary=json.loads((args.input/'analysis_summary.json').read_text(encoding='utf-8'))
    print(json.dumps({key:summary[key] for key in ('cipher_condition_count','primary_paired_contrasts','primary_holm_significant_contrasts','primary_comparator_better_contrasts','primary_count_better_contrasts')},indent=2))


if __name__=='__main__':main()
