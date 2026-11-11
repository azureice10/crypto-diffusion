"""Show the two preselected effects per key without pooling key clusters."""
import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import confirmation as C


def plot(folder):
    rows=C.read_csv(folder/'planned_comparisons.csv')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,focus in zip(axes,C.P['primary_contrasts_per_key']):
        N,native,method=focus['N'],focus['round'],focus['comparator']
        for offset,(policy,marker,label) in enumerate(zip(C.POLICIES,('o','s'),('Matched Count size','Randomized alpha 0.001'))):
            selected=[next(r for r in rows if r['key_id']==key['key_id'] and int(r['N'])==N and int(r['native_round'])==native and r['comparator']==method and int(r['bank'])==0 and r['policy']==policy) for key in C.KEYS]
            values=100*np.array([float(r['comparator_minus_count_rate']) for r in selected])
            low=100*np.array([float(r['paired_bootstrap95_low']) for r in selected]);high=100*np.array([float(r['paired_bootstrap95_high']) for r in selected])
            extents=np.array([values-low,high-values]);assert extents.min()>-1e-10
            ax.errorbar(np.arange(9)+(offset-.5)*.14,values,yerr=np.maximum(0.,extents),marker=marker,
                        linestyle='none',color='black' if offset==0 else '.55',capsize=2,label=label,markersize=4)
        ax.axhline(0,color='black',lw=.7,linestyle='--');ax.axvspan(-.45,.45,color='.93',zorder=-1)
        ax.set_xticks(range(9),['Default']+[f'K{i}' for i in range(1,9)],rotation=35)
        ax.set_title(f'Round {native}, N={N:,}: {method.title()} minus Count')
        ax.set_ylabel('Detection-rate difference (percentage points)');ax.grid(axis='y',alpha=.2)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.12,1,1))
    for ext in ('png','svg'):fig.savefig(folder/f'key_confirmation.{ext}',dpi=220)
    plt.close(fig)
    C.save_json(folder/'plot_provenance.json',{'schema':'sac-key-plot-provenance/1',
                'source_sha256':C.digest(Path(__file__)),
                'input_sha256':C.digest(folder/'planned_comparisons.csv'),
                'output_sha256':{f'key_confirmation.{ext}':C.digest(folder/f'key_confirmation.{ext}') for ext in ('png','svg')},
                'intervals':'Pointwise paired bootstrap, conditional on bank/key; key order fixed before outcomes.'})
    print('Rendered per-key planned effects with conditional paired intervals.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    plot(parser.parse_args().input)
