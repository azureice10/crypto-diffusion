"""Reproduce the four revised-manuscript figures from archived measurements."""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REPO=ROOT
FOLLOW=REPO/'data/followup'
SIZE=FOLLOW/'sac_size_matched_2026-11-11'
KEYS=FOLLOW/'sac_fresh_keys_2026-11-11'
MECH=FOLLOW/'sac_mechanism_2026-11-11'
POLICY='match_count_nonrandom'
FIG=REPO/'results/manuscript-figures'

def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def selected(source,**fields):
    return [r for r in source if all(str(r[k])==str(v) for k,v in fields.items())]

def one(source,**fields):
    out=selected(source,**fields)
    assert len(out)==1,(fields,len(out))
    return out[0]

def save(fig,name,inputs):
    FIG.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIG/(name+'.png'),dpi=400)
    plt.close(fig)
    import hashlib
    return {'figure':name,'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            'png_sha256':hashlib.sha256((FIG/(name+'.png')).read_bytes()).hexdigest()}

def figures():
    plt.rcParams.update({'font.family':'Times New Roman','font.size':9,'axes.labelsize':9,
        'axes.titlesize':9.5,'legend.fontsize':8.2,'xtick.labelsize':8.2,'ytick.labelsize':8.2,
        'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6,'savefig.facecolor':'white'})
    prov=[]
    source=REPO/'data/reference/utama_seed2026/ringkasan.json'
    s=json.loads(source.read_text(encoding='utf-8'))
    fig,axes=plt.subplots(1,2,figsize=(5.0,2.65))
    pats=[('RECTANGLE-80','-','o','0'),('CLEFIA-128','--','s','.15'),('Sparkle256',':','^','0'),
          ('Sparkle384','-.','D','.3'),('Sparkle512',(0,(5,2,1,2)),'x','.45'),('Alzette','-','v','.6')]
    for name,ls,m,c in pats:
        rr=s['per_ronde'][name][:8]
        for ax,field in zip(axes,['avalanche_mean','completeness']):
            ax.plot([r['round'] for r in rr],[r[field] for r in rr],linestyle=ls,marker=m,color=c,markersize=3,markerfacecolor='white',lw=.9,label=name.replace('Sparkle','SPARKLE'))
    for ax in axes:
        ax.set_xlabel('Native round / step');ax.set_xticks([1,2,4,6,8]);ax.grid(axis='y',color='.9',lw=.4)
    axes[0].set(ylabel='Mean flip frequency',ylim=(0,.55),title='(a) Avalanche');axes[0].axhline(.5,color='.5',ls=':',lw=.6)
    axes[1].set(ylabel='Observed coverage',ylim=(0,1.04),title='(b) Bit-pair coverage')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,handlelength=1.9,columnspacing=1)
    fig.subplots_adjust(left=.11,right=.99,top=.87,bottom=.34,wspace=.5)
    prov.append(save(fig,'diffusion',[source]))

    rate=rows(SIZE/'detection_rates.csv');null=rows(SIZE/'null_validation.csv')
    fig,axes=plt.subplots(1,2,figsize=(5,2.8),gridspec_kw={'width_ratios':[1.05,1]})
    for n,ls,m,c in [(64,':','^','.5'),(256,'-','s','0'),(1024,'--','o','.25')]:
        rr=sorted(selected(rate,N=n,bank=0,policy=POLICY,method='basic'),key=lambda r:int(r['native_round']))
        y=np.array([float(r['rate']) for r in rr]);lo=np.array([float(r['wilson95_low']) for r in rr]);hi=np.array([float(r['wilson95_high']) for r in rr])
        axes[0].errorbar([int(r['native_round']) for r in rr],y,yerr=[np.maximum(0,y-lo),np.maximum(0,hi-y)],linestyle=ls,marker=m,color=c,markersize=3,markerfacecolor='white',lw=.8,capsize=1.5,label=f'Basic N={n:,}')
    rr=sorted(selected(rate,N=256,bank=0,policy=POLICY,method='count'),key=lambda r:int(r['native_round']))
    axes[0].plot([int(r['native_round']) for r in rr],[float(r['rate']) for r in rr],'-D',color='.6',markerfacecolor='white',ms=3,lw=.8,label='Count N=256')
    for method,offset,m,c,label in [('basic',-.08,'s','0','Basic'),('max_axis',.08,'^','.45','Maximum-axis')]:
        rr=sorted(selected(null,bank=0,policy=POLICY,method=method),key=lambda r:int(r['N']))
        x=np.arange(3)+offset;y=np.array([float(r['rate_to_target']) for r in rr]);t=np.array([float(r['target_iid_size']) for r in rr])
        lo=np.array([float(r['wilson95_low']) for r in rr])/t;hi=np.array([float(r['wilson95_high']) for r in rr])/t
        axes[1].errorbar(x,y,yerr=[y-lo,hi-y],fmt=m,color=c,ms=4,capsize=2,label=label)
    axes[0].set(xlabel='RECTANGLE native round',ylabel='Detection frequency',xticks=[4,5,6,7,8],ylim=(-.04,1.04),title='(a) Transition and round 8')
    axes[1].set(xlabel='Base inputs N',ylabel='Null size / target',xticks=[0,1,2],xticklabels=['64','256','1,024'],ylim=(.65,1.3),title='(b) Residual size mismatch')
    axes[1].axhline(1,color='.5',ls='--',lw=.7)
    for ax in axes:
        ax.grid(axis='y',color='.9',lw=.4)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.3),frameon=False,ncol=1 if ax==axes[1] else 2,fontsize=8.2,handlelength=1.3,columnspacing=.6)
    fig.subplots_adjust(left=.12,right=.99,top=.86,bottom=.35,wspace=.7)
    prov.append(save(fig,'size_control',[SIZE/'detection_rates.csv',SIZE/'null_validation.csv']))

    paired=rows(KEYS/'paired_comparisons.csv')
    fig,axes=plt.subplots(1,2,figsize=(5,3.1))
    for ax,n,method,label in zip(axes,[256,1024],['basic','column'],['(a) Basic − Count','(b) Column − Count']):
        rr=sorted(selected(paired,N=n,native_round=7,bank=0,policy=POLICY,comparator=method),key=lambda r:int(r['key_index']))
        for i,r in enumerate(rr):
            x=100*float(r['comparator_minus_count_rate']);lo=100*float(r['paired_bootstrap95_low']);hi=100*float(r['paired_bootstrap95_high'])
            ax.errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt='o',color='black',markerfacecolor='black' if float(r['holm_primary18_p'])<.05 else 'white',ms=3.5,capsize=2,lw=.8)
        ax.set_yticks(range(9),['Default']+[f'K{i}' for i in range(1,9)]);ax.invert_yaxis();ax.set_xlabel('Paired difference (pp)');ax.set_title(label);ax.grid(axis='x',color='.9',lw=.4)
    axes[0].set_xlim(91,100);axes[1].set_xlim(-19,2);axes[1].axvline(0,color='.6',ls=':',lw=.6)
    fig.subplots_adjust(left=.13,right=.98,top=.87,bottom=.19,wspace=.65)
    prov.append(save(fig,'key_confirmation',[KEYS/'paired_comparisons.csv']))

    bins=selected(rows(MECH/'bin_contributions.csv'),key_id='default',N=256,native_round=7)
    fig,axes=plt.subplots(1,2,figsize=(5,2.65));x=np.arange(1,9)
    axes[0].bar(x-.18,[float(r['ideal_expected_cells']) for r in bins],width=.36,color='white',edgecolor='black',lw=.6,label='Ideal')
    axes[0].bar(x+.18,[float(r['mean_observed_cells']) for r in bins],width=.36,color='.5',label='Observed')
    shape=np.array([float(r['shape_component']) for r in bins]);scatter=np.array([float(r['scatter_component']) for r in bins])
    axes[1].bar(x,shape,width=.72,color='.3',label='Shape')
    axes[1].bar(x,scatter,bottom=shape,width=.72,color='white',edgecolor='black',hatch='///',lw=.5,label='Scatter')
    axes[0].set(ylabel='Mean cell occupancy',title='(a) Count histogram');axes[1].set(ylabel='Mean Pearson contribution',title='(b) Basic decomposition')
    for ax in axes:
        ax.set_xlabel('Count bin');ax.set_xticks(x);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.25),ncol=2,frameon=False,fontsize=8.2,handlelength=1.2,columnspacing=.8)
    fig.subplots_adjust(left=.115,right=.99,top=.86,bottom=.32,wspace=.65)
    prov.append(save(fig,'mechanism',[MECH/'bin_contributions.csv']))
    import hashlib
    (FIG/'figure_provenance.json').write_text(json.dumps({'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figures':prov},indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=FIG)
    args=parser.parse_args()
    FIG=args.output
    figures()
    print('Four manuscript figures and source/input/output hashes written to', FIG)
