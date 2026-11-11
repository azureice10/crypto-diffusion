"""Render verified size-matching CSVs; handle Wilson endpoint roundoff only."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PRIMARY='match_count_nonrandom'
RANDOM='equal_alpha_randomized'
METHODS=('count','basic','row','column')


def rows(path):
    with path.open(encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def errors(values,lower,upper):
    result=np.array([values-lower,upper-values])
    assert result.min()>-1e-12, 'Interval does not contain estimate'
    # The frozen Wilson routine can return +4e-19 as the lower endpoint of
    # a zero rate. Preserve CSV intervals; clamp only negative plot extents.
    return np.maximum(0.,result)


def plot(folder):
    folder=folder.resolve()
    data=rows(folder/'detection_rates.csv');null=rows(folder/'null_validation.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.7),sharey=True)
    for ax,N in zip(axes,(256,1024)):
        for k,(policy,label,color) in enumerate((('historical','Historical alpha 0.001','.8'),
                     (PRIMARY,'Matched to Count size','.45'),(RANDOM,'Randomized alpha 0.001','.1'))):
            selected=[next(r for r in data if int(r['N'])==N and int(r['native_round'])==7 and
                           int(r['bank'])==0 and r['method']==m and r['policy']==(PRIMARY if policy=='historical' else policy)) for m in METHODS]
            values=np.array([float(r['historical_rate'] if policy=='historical' else r['rate']) for r in selected])
            x=np.arange(4)+(k-1)*.24
            ax.bar(x,values,width=.23,color=color,label=label)
            if policy!='historical':
                low=np.array([float(r['wilson95_low']) for r in selected]);high=np.array([float(r['wilson95_high']) for r in selected])
                ax.errorbar(x,values,yerr=errors(values,low,high),fmt='none',ecolor='black',capsize=2,lw=.7)
        ax.set_xticks(range(4),['Count','Basic','Row','Column']);ax.set_title(f'RECTANGLE round 7, N={N:,}')
        ax.set_ylim(0,1.07);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_ylabel('Conditional detection frequency')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=8,frameon=False)
    fig.tight_layout(rect=(0,.1,1,1))
    for extension in ('png','svg'):fig.savefig(folder/f'size_matched_detection.{extension}',dpi=220)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.7),sharey=True)
    for ax,policy in zip(axes,(PRIMARY,RANDOM)):
        for j,(method,label,marker,color) in enumerate((('count','Count','o','black'),('basic','Basic','s','.35'),('max_axis','Row/Column marginal','^','.65'))):
            selected=sorted((r for r in null if int(r['bank'])==0 and r['policy']==policy and r['method']==method),key=lambda r:int(r['N']))
            y=np.array([float(r['rate_to_target']) for r in selected])
            low=np.array([float(r['wilson95_low'])/float(r['target_iid_size']) for r in selected])
            high=np.array([float(r['wilson95_high'])/float(r['target_iid_size']) for r in selected])
            ax.errorbar(np.arange(3)+(j-1)*.08,y,yerr=errors(y,low,high),marker=marker,color=color,capsize=3,label=label)
        ax.axhline(1,color='black',linestyle='--',lw=.7);ax.set_xticks(range(3),['64','256','1,024'])
        ax.set_xlabel('Base inputs N');ax.grid(alpha=.2)
        ax.set_title('Match exact Count size' if policy==PRIMARY else 'Randomized alpha 0.001')
    axes[0].set_ylabel('Held-out null rate / target')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.1,1,1))
    for extension in ('png','svg'):fig.savefig(folder/f'size_matched_null.{extension}',dpi=220)
    plt.close(fig)
    root=Path(__file__).resolve().parents[1]
    paths=[Path(__file__),folder/'detection_rates.csv',folder/'null_validation.csv']
    paths += [folder/f'{stem}.{ext}' for stem in ('size_matched_detection','size_matched_null') for ext in ('png','svg')]
    record={'schema':'sac-size-plot-provenance/1',
            'note':'Post-generation renderer. Frozen analyzer numeric output is unchanged. Only microscopic negative Wilson errorbar extents at endpoints are clamped to zero for plotting; recorded intervals are preserved.',
            'sha256':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (folder/'plot_provenance.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('Rendered two figures as PNG and SVG; CSV intervals unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    plot(parser.parse_args().input)
