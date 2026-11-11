"""Verify key selection, fresh bases, auxiliary statistics and per-key inference."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.stats import binomtest

import confirmation as C


def verify(folder,regenerate_snapshots=False):
    records=[];decisions={};raw_total=0;input_checks=0;histogram_checks=0;snapshot_checks=0;regenerated=0
    reps=C.P['replications_per_key'];round_indices=np.array(C.P['analysis_rounds'])-1
    historical=C.read_csv(C.ROOT/C.KEY_RECORD['historical_keys_source'])
    excluded={int(r['kunci_hex'],16) for r in historical if r['primitif']=='RECTANGLE-80'}
    assert C.digest(C.ROOT/C.KEY_RECORD['historical_keys_source'])==C.KEY_RECORD['historical_keys_source_sha256']
    key_rng=np.random.default_rng(np.random.SeedSequence(C.KEY_RECORD['seed_entropy']))
    expected=[C.P['default_key_hex']];used=excluded|{int(expected[0],16)}
    while len(expected)<9:
        value=int.from_bytes(key_rng.bytes(10),'big')
        if value not in used:expected.append(f'{value:020x}');used.add(value)
    assert [k['key_hex'] for k in C.KEYS]==expected
    # Verify reused calibration bytes against the archived source commit.
    for N in C.P['sample_sizes']:
        for bank in C.P['calibration_banks']:
            name=f"{C.P['calibration_folder']}/calibration_N{N}_bank{bank}.npz"
            result=subprocess.run(['git','show',C.P['source_data_commit']+':'+name],cwd=C.ROOT,check=True,capture_output=True)
            import hashlib
            assert hashlib.sha256(result.stdout).hexdigest()==C.digest(C.ROOT/name)
    for key in C.KEYS:
        prefix=folder/key['key_id']
        record=json.loads(Path(str(prefix)+'_metadata.json').read_text(encoding='utf-8'));records.append(record)
        assert record['key']==key and record['replications']==reps
        for name,sha in record['source_sha256'].items():assert C.digest(C.ROOT/name)==sha,name
        for name,sha in record['output_sha256'].items():assert C.digest(folder/name)==sha,name
        raw=C.read_csv(Path(str(prefix)+'_raw.csv'));inputs=C.read_csv(Path(str(prefix)+'_inputs.csv'))
        lookup={(int(r['replicate']),int(r['N']),int(r['native_round'])):r for r in raw}
        assert len(raw)==len(lookup)==reps*6;raw_total+=len(raw)
        input_lookup={(int(r['replicate']),int(r['N'])):r for r in inputs}
        assert len(input_lookup)==len(inputs)==reps*2
        bases=[]
        for replicate in range(reps):
            seed=C.input_seed(key['key_index'],replicate);values=C.input_words(seed,max(C.P['sample_sizes']))
            bases.append(values.view('<u8').reshape(-1))
            for N in C.P['sample_sizes']:
                row=input_lookup[replicate,N]
                assert json.loads(row['seed_entropy'])==seed.entropy
                assert row['input_sha256']==C.array_digest(values[:N])
                assert int(row['query_budget'])==N*65;input_checks+=1
        bases=np.concatenate(bases);unique=np.unique(bases)
        assert record['input_bases']==len(bases) and record['unique_input_bases']==len(unique)
        assert record['duplicate_input_bases']==len(bases)-len(unique)
        assert record['sorted_unique_base_sha256']==C.array_digest(unique)
        assert record['discovery_base_intersection']==len(np.intersect1d(unique,C.discovery_bases(),assume_unique=True))
        with np.load(Path(str(prefix)+'_arrays.npz'),allow_pickle=False) as archive:
            arrays={k:archive[k] for k in archive.files}
        for N in C.P['sample_sizes']:
            vh=arrays[f'value_hist_N{N}'];rh=arrays[f'row_hist_N{N}'];ch=arrays[f'col_hist_N{N}']
            assert vh.shape==(reps,3,N+1) and rh.shape==ch.shape==(reps,3,64,8)
            assert np.all(vh.sum(axis=-1)==4096) and np.all(rh.sum(axis=-1)==64) and np.all(ch.sum(axis=-1)==64)
            _,probabilities,labels=C.SAC.bin_description(N)
            global_hist=np.stack([vh[...,labels==b].sum(axis=-1) for b in range(8)],axis=-1)
            np.testing.assert_array_equal(global_hist,rh.sum(axis=-2))
            np.testing.assert_array_equal(global_hist,ch.sum(axis=-2))
            rejected,_=C.SAC.count_description(N)
            count=vh[...,rejected].sum(axis=-1)
            basic=((global_hist-4096*probabilities)**2/(4096*probabilities)).sum(axis=-1)
            rowmax=(((rh-64*probabilities)**2/(64*probabilities)).sum(axis=-1)).max(axis=-1)
            colmax=(((ch-64*probabilities)**2/(64*probabilities)).sum(axis=-1)).max(axis=-1)
            independently_reconstructed=np.stack((count,basic,rowmax,colmax),axis=-1)
            all_stats=np.array([[[float(lookup[i,N,r]['stat_'+m]) for m in C.METHODS] for r in C.P['analysis_rounds']] for i in range(reps)])
            np.testing.assert_allclose(all_stats,independently_reconstructed,rtol=1e-12,atol=1e-10)
            histogram_checks+=reps*3
            sum_counts=arrays[f'sum_counts_N{N}'];sum_squared=arrays[f'sum_squared_counts_N{N}']
            support=np.arange(N+1,dtype=np.uint64)
            np.testing.assert_array_equal(sum_counts.sum(axis=(1,2)),(vh.astype(np.uint64)*support).sum(axis=(0,2)))
            np.testing.assert_array_equal(sum_squared.sum(axis=(1,2)),(vh.astype(np.uint64)*support**2).sum(axis=(0,2)))
            assert np.all(sum_counts<=reps*N) and np.all(sum_squared<=reps*N*N)
            for replicate in record['snapshot_replicates']:
                full=arrays[f'snapshot_rep{replicate}_N{N}'];selected=full[round_indices]
                assert full.shape==(8,64,64)
                for ri,native in enumerate(C.P['analysis_rounds']):
                    assert C.array_digest(selected[ri])==lookup[replicate,N,native]['count_matrix_sha256']
                    np.testing.assert_array_equal(np.bincount(selected[ri].ravel(),minlength=N+1),vh[replicate,ri])
                    snapshot_checks+=1
                np.testing.assert_allclose(C.SAC.statistics(selected,N),all_stats[replicate],rtol=1e-12,atol=1e-10)
            for ri,native in enumerate(C.P['analysis_rounds']):
                for bank in C.P['calibration_banks']:
                    for policy in C.POLICIES:
                        decisions[key['key_id'],N,native,bank,policy]=C.decisions(all_stats[:,ri],key['key_index'],N,bank,policy)
        if regenerate_snapshots:
            for replicate in record['snapshot_replicates']:
                matrices,_=C.keyed_counts(int(key['key_hex'],16),C.input_seed(key['key_index'],replicate))
                for N,matrix in matrices.items():
                    np.testing.assert_array_equal(matrix,arrays[f'snapshot_rep{replicate}_N{N}'])
                    regenerated+=1
    assert len({r['execution_commit'] for r in records})==1
    rates=C.read_csv(folder/'detection_rates.csv');paired=C.read_csv(folder/'paired_comparisons.csv')
    assert len(rates)==1296 and len(paired)==972
    for row in rates:
        k=(row['key_id'],int(row['N']),int(row['native_round']),int(row['bank']),row['policy'])
        successes=int(decisions[k][:,C.METHODS.index(row['method'])].sum())
        assert int(row['detections'])==successes and float(row['rate'])==successes/reps
        np.testing.assert_allclose([float(row['wilson95_low']),float(row['wilson95_high'])],C.SAC.wilson(successes,reps),rtol=1e-12,atol=1e-15)
    for row in paired:
        k=(row['key_id'],int(row['N']),int(row['native_round']),int(row['bank']),row['policy'])
        d=decisions[k];a,b=d[:,0],d[:,C.METHODS.index(row['comparator'])]
        cells=np.array([np.sum(~a&~b),np.sum(a&~b),np.sum(~a&b),np.sum(a&b)],dtype=int)
        assert [int(row[x]) for x in ('neither','count_only','comparator_only','both')]==cells.tolist()
        discordant=int(cells[1]+cells[2]);p=1. if not discordant else binomtest(int(cells[1]),discordant,.5).pvalue
        np.testing.assert_allclose(float(row['mcnemar_exact_p']),p,rtol=1e-12,atol=1e-300)
        assert float(row['comparator_minus_count_rate'])==(cells[2]-cells[1])/reps
        seed=[C.P['base_seed'],504,int(row['key_index']),C.POLICIES.index(row['policy']),int(row['bank']),int(row['N']),int(row['native_round']),C.METHODS.index(row['comparator'])]
        boot=np.random.default_rng(np.random.SeedSequence(seed)).multinomial(reps,cells/reps,size=10000)
        ci=np.quantile((boot[:,2]-boot[:,1])/reps,[.025,.975])
        np.testing.assert_allclose([float(row['paired_bootstrap95_low']),float(row['paired_bootstrap95_high'])],ci,rtol=1e-12,atol=1e-15)
    for bank in C.P['calibration_banks']:
        for policy in C.POLICIES:
            full=[r for r in paired if int(r['bank'])==bank and r['policy']==policy]
            selected=[r for r in full if r['planned_contrast']=='True']
            assert len(full)==162 and len(selected)==18
            for family,field in ((full,'holm_grid162_p'),(selected,'holm_primary18_p')):
                p=np.array([float(r['mcnemar_exact_p']) for r in family]);order=np.argsort(p,kind='stable')
                values=np.empty(len(p));values[order]=np.maximum.accumulate(np.minimum(1.,p[order]*(len(p)-np.arange(len(p)))))
                np.testing.assert_allclose(values,[float(r[field]) for r in family],rtol=1e-12,atol=1e-300)
    summary=json.loads((folder/'analysis_summary.json').read_text(encoding='utf-8'))
    assert summary['new_cipher_replications']==9*reps and summary['new_null_draws']==0
    assert summary['raw_rows']==raw_total and summary['primary_family_size']==18
    primary=[r for r in paired if r['analysis_role']=='primary_confirmation']
    assert len(primary)==18 and summary['primary_significant']==sum(float(r['holm_primary18_p'])<.05 for r in primary)
    assert summary['base_intersections_with_discovery']==sum(r['discovery_base_intersection'] for r in records)
    descriptions=C.read_csv(folder/'random_key_summary.csv');assert len(descriptions)==12
    for row in descriptions:
        selected=[r for r in paired if r['key_type']=='random' and int(r['N'])==int(row['N']) and int(r['native_round'])==int(row['native_round']) and r['comparator']==row['comparator'] and int(r['bank'])==int(row['bank']) and r['policy']==row['policy']]
        assert len(selected)==8
        effects=[float(r['comparator_minus_count_rate']) for r in selected]
        np.testing.assert_allclose([float(row['effect_mean']),float(row['effect_min']),float(row['effect_max'])],[np.mean(effects),min(effects),max(effects)],rtol=1e-12,atol=1e-15)
        sign=1 if row['comparator']=='basic' else -1
        assert int(row['keys_in_planned_direction'])==sum(sign*x>0 for x in effects)
        assert int(row['keys_significant_planned_holm18'])==sum(float(r['holm_primary18_p'])<.05 and sign*float(r['comparator_minus_count_rate'])>0 for r in selected)
    report={'schema':'sac-key-confirmation-verification/1','status':'PASS',
            'execution_commits':sorted({r['execution_commit'] for r in records}),
            'keys':9,'random_keys':8,'new_cipher_replications':9*reps,
            'raw_rows':raw_total,'input_prefix_hashes':input_checks,'histogram_reconstructed_conditions':histogram_checks,
            'snapshot_conditions':snapshot_checks,'regenerated_native_snapshot_matrices':regenerated,
            'rate_rows':len(rates),'paired_rows':len(paired),'primary_family':18,'full_grid_family':162,
            'source_records_checked':len(records),
            'scope':'Frozen source/key/calibration hashes, all fresh input prefixes and overlaps, raw statistics independently reconstructed from complete value/row/column histograms; all paired decisions, bootstrap intervals and both Holm families recomputed. Optional snapshot regeneration links retained matrices to new inputs.'}
    C.save_json(folder/'verification.json',report)
    print(json.dumps(report,indent=2));return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--regenerate-snapshots',action='store_true');args=parser.parse_args()
    verify(args.input,args.regenerate_snapshots)


if __name__=='__main__':main()
