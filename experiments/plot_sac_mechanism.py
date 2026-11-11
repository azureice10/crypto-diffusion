"""Visualize frozen mechanism diagnostics; no statistical decisions are changed."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0,str(Path(__file__).resolve().parent/'sac_mechanism'))
import mechanism as M


def save(fig,folder,name):
    for ext in ('png','svg'):fig.savefig(folder/f'{name}.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)


def main(folder):
    bins=M.C.read_csv(folder/'bin_contributions.csv');pmfs=M.C.read_csv(folder/'count_distributions.csv')
    conditions=M.C.read_csv(folder/'condition_metrics.csv');models=M.C.read_csv(folder/'surrogate_summary.csv')
    layouts=M.C.read_csv(folder/'layout_summary.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig,axes=plt.subplots(1,3,figsize=(11.5,3.6))
    for r,style,color in ((7,'-','black'),(8,'--','.55')):
        selected=[x for x in pmfs if x['key_id']=='default' and int(x['N'])==256 and int(x['native_round'])==r]
        k=np.array([int(x['count']) for x in selected]);frequency=np.array([float(x['mean_cell_frequency']) for x in selected])
        axes[0].plot(k,frequency,style,color=color,label=f'Round {r}')
        if r==7:axes[0].plot(k,[float(x['ideal_binomial_probability']) for x in selected],':',color='.25',label='Ideal binomial')
        chosen=[x for x in bins if x['key_id']=='default' and int(x['N'])==256 and int(x['native_round'])==r]
        e=np.array([float(x['ideal_expected_cells']) for x in chosen]);mean=np.array([float(x['mean_observed_cells']) for x in chosen])
        sd=np.sqrt(np.array([float(x['scatter_component']) for x in chosen]))
        axes[1].errorbar(np.arange(1,9)+(r-7.5)*.08,(mean-e)/np.sqrt(e),yerr=sd,
                         linestyle=style,marker='o' if r==7 else 's',color=color,label=f'Round {r}',capsize=2,markersize=3)
    axes[0].set(xlim=(88,168),xlabel='Cell count K (N=256)',ylabel='Mean cell frequency',title='(a) Actual versus ideal count distribution')
    reject,_=M.C.SAC.count_description(256);support=np.arange(257)
    for cut in (support[reject & (support<128)].max()+.5,support[reject & (support>128)].min()-.5):axes[0].axvline(cut,color='.6',lw=.6,linestyle='-.')
    axes[0].legend(frameon=False,fontsize=7);axes[0].grid(alpha=.15)
    axes[1].axhline(0,color='black',lw=.6);axes[1].set(xticks=range(1,9),xlabel='Fixed histogram bin',ylabel='Mean residual / sqrt(expected)',title='(b) Mean residual +/- replicate SD')
    axes[1].legend(frameon=False,fontsize=7);axes[1].grid(alpha=.15)
    selected=[x for x in bins if x['key_id']=='default' and int(x['N'])==256 and int(x['native_round'])==7]
    shape=np.array([float(x['shape_component']) for x in selected]);scatter=np.array([float(x['scatter_component']) for x in selected])
    axes[2].bar(range(1,9),shape,color='.25',label='Mean shape')
    axes[2].bar(range(1,9),scatter,bottom=shape,color='.75',label='Between-replica scatter')
    axes[2].set(xticks=range(1,9),xlabel='Fixed histogram bin',ylabel='Mean Pearson contribution',title='(c) Round-seven bin contributions')
    axes[2].legend(frameon=False,fontsize=7);axes[2].grid(axis='y',alpha=.15);axes[2].set_axisbelow(True)
    fig.tight_layout();save(fig,folder,'bin_distribution')

    fig,axes=plt.subplots(1,2,figsize=(9,4))
    fig.subplots_adjust(left=.08,right=.80,wspace=.35,bottom=.16,top=.88)
    with np.load(folder/'coordinate_maps.npz',allow_pickle=False) as archive:
        values=[archive[f'default_N256_r{r}_p_hat']-.5 for r in (7,8)]
    maximum=max(float(np.max(np.abs(x))) for x in values)
    for ax,r,data in zip(axes,(7,8),values):
        image=ax.imshow(data,cmap='gray',vmin=-maximum,vmax=maximum,origin='lower',interpolation='nearest')
        row=next(x for x in conditions if x['key_id']=='default' and int(x['N'])==256 and int(x['native_round'])==r)
        ax.set(title=f"Round {r}, N=256: {row['marginal_significant_cells']} cells",xlabel='Output bit j (LSB first)',ylabel='Input bit i (LSB first)',xticks=[0,16,32,48,63],yticks=[0,16,32,48,63])
        for x in (15.5,31.5,47.5):ax.axvline(x,color='.6',lw=.4);ax.axhline(x,color='.6',lw=.4)
    color_axis=fig.add_axes([.86,.19,.025,.66])
    fig.colorbar(image,cax=color_axis,label='Pooled flip bias: p_hat - 0.5')
    fig.suptitle('Pooled marginal bias, default key (500 replications)',fontsize=10,y=.99)
    save(fig,folder,'marginal_bias_maps')

    groups=('actual_holdout','iid_fair_binomial','independent_fitted_binomial','independent_empirical_cells')
    labels=('Actual holdout','Independent fair','Independent fitted binomial','Independent empirical cells')
    fig,axes=plt.subplots(1,3,figsize=(11.5,3.8),sharey=True)
    for ax,case in zip(axes,M.P['default_cases']):
        name=M.case_name(case)
        for gi,(group,label,color) in enumerate(zip(groups,labels,('.1','.8','.45','.65'))):
            chosen=[next(r for r in models if r['case']==name and r['group']==group and r['method']==m) for m in M.C.METHODS]
            y=np.array([float(r['rate']) for r in chosen]);lo=np.array([float(r['wilson95_low']) for r in chosen]);hi=np.array([float(r['wilson95_high']) for r in chosen])
            errors=np.maximum(0.,np.array([y-lo,hi-y]))
            ax.bar(np.arange(4)+(gi-1.5)*.19,y,width=.18,color=color,label=label)
            ax.errorbar(np.arange(4)+(gi-1.5)*.19,y,yerr=errors,fmt='none',color='black',capsize=1,lw=.5)
        ax.set(xticks=range(4),xticklabels=['Count','Basic','Row','Column'],ylim=(0,1.08),title=f"Round {case['round']}, N={case['N']:,}")
        ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[0].set_ylabel('Conditional rejection frequency')
    handles,legend=axes[0].get_legend_handles_labels();fig.legend(handles,legend,loc='lower center',ncol=4,frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.1,1,1));save(fig,folder,'surrogate_diagnostics')

    fig,ax=plt.subplots(figsize=(7.5,3.8))
    for ci,(case,marker,color) in enumerate(zip(M.P['default_cases'],('o','s','^'),('black','.45','.7'))):
        chosen=[next(r for r in layouts if r['case']==M.case_name(case) and r['method']==m) for m in M.C.METHODS]
        y=100*np.array([float(r['permuted_minus_original_rate']) for r in chosen]);lo=100*np.array([float(r['parent_bootstrap95_low']) for r in chosen]);hi=100*np.array([float(r['parent_bootstrap95_high']) for r in chosen])
        ax.errorbar(np.arange(4)+(ci-1)*.12,y,yerr=np.maximum(0.,np.array([y-lo,hi-y])),
                    marker=marker,color=color,linestyle='none',capsize=3,label=f"r={case['round']}, N={case['N']:,}")
    ax.axhline(0,color='black',lw=.7,linestyle='--');ax.set(xticks=range(4),xticklabels=['Count','Basic','Row','Column'],ylabel='Permuted minus original rate (pp)',title='Spatial-layout ablation: parent-level paired intervals')
    ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,fontsize=8)
    fig.tight_layout();save(fig,folder,'layout_ablation')
    names=('bin_distribution','marginal_bias_maps','surrogate_diagnostics','layout_ablation')
    M.C.save_json(folder/'plot_provenance.json',{'schema':'sac-mechanism-plot-provenance/1',
        'source_sha256':M.C.digest(Path(__file__)),
        'input_sha256':{name:M.C.digest(folder/name) for name in ('bin_contributions.csv','count_distributions.csv','condition_metrics.csv','coordinate_maps.npz','surrogate_summary.csv','layout_summary.csv')},
        'output_sha256':{f'{name}.{ext}':M.C.digest(folder/f'{name}.{ext}') for name in names for ext in ('png','svg')},
        'notes':'PMF window is 88-168 counts at N=256. Bin residual bars show replicate SD, not confidence intervals. Surrogate Wilson intervals omit fit uncertainty. Layout intervals resample genuine parents. Gray-map scale is symmetric and shared across rounds.'})
    print('Rendered four mechanism figures as PNG/SVG.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    main(parser.parse_args().input)
