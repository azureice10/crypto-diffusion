#!/usr/bin/env python3
"""Audit saved measurements; never re-label old samples as new replication."""
import argparse
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import pickle
import random
import statistics

import numpy as np
import bandingkan as B
import metrik as M
import primitif as P

METRICS = ("sac", "linear", "diferensial", "zero_sum4", "zero_sum8")
POLICIES = ("legacy", "corrected", "conservative", "experimentwise")


def read_measurement(path):
    # Only open locally generated trusted checkpoints from this rerun.
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


def decisions(rows, policy, alpha):
    if policy == "legacy":
        return [{"sac": r["sac_p_value_legacy"] < alpha,
                 "linear": r["lin_sig_pairs_legacy"] > 0,
                 "diferensial": r["diff_top_count"] >= 3,
                 "zero_sum4": r["zs4_p_value_legacy"] < alpha,
                 "zero_sum8": r["zs8_p_value_legacy"] < alpha} for r in rows]
    conservative = policy == "conservative"
    return [{"sac": r["sac_bonferroni_p" if conservative else "sac_p_value"] < alpha,
             "linear": r["lin_bonferroni_p"] < alpha,
             "diferensial": r["diff_top_count"] >= 3 and r["diff_null_p_bound"] < alpha,
             "zero_sum4": r["zs4_markov_p_bound" if conservative else "zs4_p_value"] < alpha,
             "zero_sum8": r["zs8_markov_p_bound" if conservative else "zs8_p_value"] < alpha}
            for r in rows]


def horizon_record(rows, policy, alpha, label, name, native_factor=1):
    hits = decisions(rows, policy, alpha)
    result = {"run": label, "primitif": name, "aturan": policy, "alpha_per_test": alpha,
              "R": len(rows), "native_factor": native_factor}
    for metric in METRICS:
        marked = [{"round": i + 1, "hit": hit[metric]} for i, hit in enumerate(hits)]
        result[metric] = M.horizon(marked, lambda r: r["hit"])
        found = [r["round"] for r in marked if r["hit"]]
        result[metric + "_last_detection"] = max(found) if found else None
        result[metric + "_after_gap"] = " ".join(map(str, M.isolated(marked, lambda r: r["hit"])))
    combined = max((result[k] or 0 for k in METRICS), default=0)
    result.update(H=combined, H_native=combined * native_factor,
                  H_frac=combined / len(rows), sisa_frac=1 - combined / len(rows))
    return result, hits


def add_zero_legacy(rows, m):
    for i, row in enumerate(rows):
        row["zs4_p_value_legacy"] = m["zs4"][i]["p_value_legacy"]
        row["zs8_p_value_legacy"] = m["zs8"][i]["p_value_legacy"]


def wilson(hits, total):
    p, z = hits / total, 1.959963984540054
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z / denominator * math.sqrt(p * (1-p) / total + z * z / (4 * total * total))
    return max(0, center-radius), min(1, center+radius)


def null_calibration(output, replicates=1_000_000):
    """Exact iid-label null plus MC sanity check, not 1e6 primitive runs.

    Under distinct avalanche stars all flip indicators are independent fair
    bits: shared base output cancels in XOR. Thus the exact discrete cell size
    q, not nominal alpha, determines V~Binomial(n^2,q). Switching to a random
    permutation changes event probabilities by at most the recorded bound.
    """
    rng = np.random.default_rng(9102026)
    rows = []
    for n in (64, 128, 256, 384, 512):
        mass, pv = M.binomial_mass(64), M.binomial_pvalues(64)
        q = float(mass[pv < .001].sum())
        coupling = M.null_coupling_bound(n, 64 * (n + 1))
        counts = rng.binomial(n*n, q, size=replicates)
        for policy, assumed in (("legacy", .001), ("corrected", q)):
            cutoff = 0
            while M.binom_tail(n*n, assumed, cutoff) + (coupling if policy == "corrected" else 0) >= .001:
                cutoff += 1
            found = int((counts >= cutoff).sum())
            lo, hi = wilson(found, replicates)
            rows.append({"n_bits": n, "test": "SAC", "aturan": policy,
                         "q_cell_actual": q, "critical_count": cutoff,
                         "exact_iid_type1": M.binom_tail(n*n, q, cutoff),
                         "permutation_coupling_bound": coupling,
                         "mc_replicates": replicates, "mc_rejections": found,
                         "mc_rate": found/replicates, "wilson95_low": lo, "wilson95_high": hi})
        q_bonf = float(mass[n*n*pv + coupling < .001].sum())
        count = rng.binomial(n*n, q_bonf, size=replicates)
        found = int((count > 0).sum())
        lo, hi = wilson(found, replicates)
        rows.append({"n_bits": n, "test": "SAC", "aturan": "conservative",
                     "q_cell_actual": q_bonf, "critical_count": 1,
                     "exact_iid_type1": -math.expm1(n*n * math.log1p(-q_bonf)),
                     "permutation_coupling_bound": coupling, "mc_replicates": replicates,
                     "mc_rejections": found, "mc_rate": found/replicates,
                     "wilson95_low": lo, "wilson95_high": hi})
        for policy in ("corrected", "conservative"):
            q_zs = 2 ** -16
            count = rng.binomial(n, q_zs, size=replicates)
            bound = math.comb(16,2) / 2 ** (n-8) + math.comb(16*256,2) / 2**n
            cutoff = 1
            def pvalue(k):
                return (M.binom_tail(n,q_zs,k) if policy == "corrected" else n*q_zs/k) + bound
            while pvalue(cutoff) >= .001:
                cutoff += 1
            found = int((count >= cutoff).sum())
            lo, hi = wilson(found,replicates)
            rows.append({"n_bits":n,"test":"ZS8","aturan":policy,"q_cell_actual":q_zs,
                         "critical_count":cutoff,"exact_iid_type1":M.binom_tail(n,q_zs,cutoff),
                         "permutation_coupling_bound":bound,"mc_replicates":replicates,
                         "mc_rejections":found,"mc_rate":found/replicates,
                         "wilson95_low":lo,"wilson95_high":hi})
    B.write_csv(output / "kalibrasi_null.csv", rows)
    return rows


def direct_permutation_sanity(output, repetitions=500):
    """Evaluate avalanche stars under fresh sampled random permutations.

    An injective list of Q uniform output labels is exactly the restriction
    of a uniformly sampled permutation to Q distinct inputs. Rejection of a
    whole batch with duplicate labels preserves that distribution.
    """
    rng = np.random.default_rng(5012026)
    result=[]
    pvalues=M.binomial_pvalues(64)
    q=float(M.binomial_mass(64)[pvalues<.001].sum())
    for n in (64,128,256,384,512):
        counts=[]
        for _ in range(repetitions):
            size=64*(n+1)
            while True:
                labels=rng.integers(0,256,size=(size,n//8),dtype=np.uint8)
                if len(np.unique(labels.view(np.dtype((np.void,n//8)))))==size:
                    break
            bits=np.unpackbits(labels,axis=1,bitorder="little").reshape(64,n+1,n)
            flips=np.bitwise_xor(bits[:,1:,:],bits[:,:1,:]).sum(axis=0)
            counts.append(int((pvalues[flips]<.001).sum()))
        for policy,assumed in (("legacy",.001),("corrected",q)):
            coupling=M.null_coupling_bound(n,64*(n+1)) if policy=="corrected" else 0
            critical=0
            while M.binom_tail(n*n,assumed,critical)+coupling>=.001:
                critical+=1
            hits=sum(v>=critical for v in counts)
            lo,hi=wilson(hits,repetitions)
            result.append(dict(n_bits=n,aturan=policy,repetitions=repetitions,
                observed_mean_violations=float(np.mean(counts)),iid_expected_mean=n*n*q,
                observed_variance=float(np.var(counts,ddof=1)),iid_expected_variance=n*n*q*(1-q),
                rejections=hits,rate=hits/repetitions,wilson95_low=lo,wilson95_high=hi))
        print(f"Null permutasi langsung {n} bit: {repetitions} ulangan",flush=True)
    B.write_csv(output / "null_permutasi_langsung.csv",result)


def whitened_output(p, key):
    if p.key == "rectangle":
        keys = P.R.key_extend_80(P.R.key_from_hex(f"{key:020x}"))
        mask = P.R.state_to_int(keys[-1])
        return lambda v: v ^ mask
    wk, _ = P.C.key_schedule_128(key.to_bytes(16,"big"))
    def finish(v):
        w = [(v >> s) & 0xffffffff for s in (96,64,32,0)]
        return P._words_to_int([w[3], w[0]^wk[2], w[1], w[2]^wk[3]])
    return finish


def audit_whitening(run, output):
    rows, keyrows = [], []
    for name in ("rectangle", "clefia"):
        p = P.PRIMITIVES[name]
        m = read_measurement(run / "medicoes" / f"{name}.pkl.gz")
        y = m["ys"][p.rounds]
        # Reconstruct integer states from saved bit matrices and apply exactly
        # the omitted final XOR (and CLEFIA's final word order).
        packed = np.packbits((y > 0).astype(np.uint8),axis=1,bitorder="little")
        ints = [int.from_bytes(bytes(row),"little") for row in packed]
        finish = whitened_output(p,p.default_key)
        final = M.to_bits([finish(v) for v in ints],p.n).astype(float)*2-1
        for label, values in (("trace",y),("ciphertext",final)):
            rows.append(dict(primitif=p.name, representation=label, **M.full_round_randomness(values)))
        # Check finalization independently against native encryption.
        rng = random.Random(123)
        for _ in range(10):
            x = rng.getrandbits(p.n)
            if name == "rectangle":
                expected = P.R.state_to_int(P.R.encrypt_block_with_master(P.R.int_to_state(x),P.R.key_from_hex(P.RECT_KEY)))
            else:
                expected = int.from_bytes(P.C.encrypt_block(x.to_bytes(16,"big"),P.CLEFIA_KEY),"big")
            assert finish(p.trace(x)[-1]) == expected
        other = copy.copy(p)
        def factory(key, original=p):
            tr, fn = original.with_key(key), whitened_output(original,key)
            def full(x):
                result = tr(x)
                result[-1] = fn(result[-1])
                return result
            return full
        other.with_key = factory
        for label, primitive in (("trace",p),("ciphertext_endpoint",other)):
            ka = M.key_avalanche(primitive,32,random.Random(2026+500+p.seed_id))
            keyrows.extend(dict(primitif=p.name,representation=label,**r) for r in ka)
    B.write_csv(output / "whitening_statistik.csv",rows)
    B.write_csv(output / "whitening_avalanche_kunci.csv",keyrows)


def correlation_audit(summaries, output):
    summary = summaries["utama_seed2026"]
    fields = ["r_norm","avalanche_mean","completeness","sac_violation_frac",
              "lin_sig_frac","lin_max_abs_corr","diff_top_frac","zs8_balanced_frac"]
    rows = []
    for group in ("all", "without_slim", *summary["per_ronde"]):
        points = [r for name, data in summary["per_ronde"].items() for r in data
                  if group == "all" or (group == "without_slim" and "slim" not in name) or group == name]
        for a in fields:
            for b in fields:
                x,y = [r[a] for r in points],[r[b] for r in points]
                old = float(np.corrcoef(np.argsort(np.argsort(x)),np.argsort(np.argsort(y)))[0,1])
                rows.append({"group":group,"a":a,"b":b,"points":len(points),
                             "old_ordinal_ranks":old,"spearman_average_ranks":M.spearman(x,y)})
    B.write_csv(output / "korelasi_audit.csv", rows)
    pairs = []
    names = list(summary["per_ronde"])
    from itertools import combinations
    for a,b in combinations(names,2):
        for field, (_,start) in B.CURVES.items():
            ca = [r[field] for r in summary["per_ronde"][a]]
            cb = [r[field] for r in summary["per_ronde"][b]]
            ns = {p["name"]:p["n_bits"] for p in summary["primitif"]}
            for zero in (True,False):
                grid = np.linspace(0 if zero else max(1/len(ca),1/len(cb)),1,21)
                def interp(curve,n):
                    xs = np.arange(0 if zero else 1,len(curve)+1)/len(curve)
                    ys = [start(n)]+curve if zero else curve
                    return np.interp(grid,xs,ys)
                va,vb = interp(ca,ns[a]),interp(cb,ns[b])
                corr = float(np.corrcoef(va,vb)[0,1]) if va.std() and vb.std() else None
                pairs.append(dict(a=a,b=b,metric=field,include_identity=zero,
                                  pearson=corr,rmse=float(np.sqrt(np.mean((va-vb)**2)))))
    B.write_csv(output / "kemiripan_sensitivitas.csv",pairs)


def audit_figures(output,records):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names=[p.name for p in P.PRIMITIVES.values()]
    matrix=np.array([[next(r["H"] for r in records if r["run"]=="utama_seed2026"
                         and r["primitif"]==name and r["aturan"]==policy)
                      for policy in POLICIES] for name in names])
    fig,ax=plt.subplots(figsize=(9,6))
    im=ax.imshow(matrix,cmap="YlGnBu",vmin=0)
    ax.set_xticks(range(4),["Lama","Terkoreksi","Konservatif","Seluruh run"],rotation=15)
    ax.set_yticks(range(len(names)),names)
    ax.set_title("Horizon gabungan pada data identik (seed 2026)")
    for i in range(len(names)):
        for j in range(4):
            ax.text(j,i,str(matrix[i,j]),ha="center",va="center",
                    color="white" if matrix[i,j]>matrix.max()*.6 else "black")
    fig.colorbar(im,ax=ax,label="Ronde asli / step / ronde ARX")
    fig.tight_layout()
    for ext in ("png","pdf"):
        fig.savefig(output/f"horizon_sensitivitas.{ext}",dpi=220,bbox_inches="tight")
    plt.close(fig)


def confirm_isolated_linear(root,output):
    """Independent held-out check of selected late CLEFIA correlations."""
    run=root/"sampel_besar_seed2026"
    summary=json.loads((run/"ringkasan.json").read_text(encoding="utf-8"))
    p=P.PRIMITIVES["clefia"]
    m=read_measurement(run/"medicoes"/"clefia.pkl.gz")
    rounds=M.isolated(m["lin"],lambda r:r["lin_sig_pairs"]>0)
    if not rounds:
        return
    params=summary["parameter"]
    rng=random.Random(params["seed"]+p.seed_id)
    for _ in range(params["sampel_avalanche"]):
        rng.getrandbits(p.n)
    size=params["sampel_linear"]
    xs=[rng.getrandbits(p.n) for _ in range(size)]
    traces=p.trace_many(xs)
    xbits=M.to_bits(xs,p.n).astype(float)*2-1
    pv=M.binomial_pvalues(size)
    selected=[]
    for r in rounds:
        y=M.to_bits([t[r-1] for t in traces],p.n).astype(float)*2-1
        corr=xbits.T@y/size
        counts=np.rint((corr+1)*size/2).astype(int)
        adjusted=np.minimum(1,p.n*p.n*pv[counts]+M.null_coupling_bound(p.n,size))
        for i,j in np.argwhere(adjusted<.001):
            selected.append(dict(round=r,input_bit=int(i),output_bit=int(j),
                                 discovery_n=size,discovery_corr=float(corr[i,j]),
                                 discovery_bonferroni_p=float(adjusted[i,j])))
    # Freeze selected coordinates before drawing any hold-out input.
    (output/"hipotesis_linear_sebelum_konfirmasi.json").write_text(
        json.dumps({"holdout_seed":20261110,"holdout_n":65536,"selected":selected},indent=2),encoding="utf-8")
    heldout_n=65536
    rng=random.Random(20261110)
    matches=np.zeros(len(selected),dtype=np.int64)
    for start in range(0,heldout_n,2048):
        inputs=[rng.getrandbits(p.n) for _ in range(min(2048,heldout_n-start))]
        states=p.trace_many(inputs)
        for index,h in enumerate(selected):
            matches[index]+=sum(((x>>h["input_bit"])&1)==((t[h["round"]-1]>>h["output_bit"])&1)
                                for x,t in zip(inputs,states))
    pvalues=M.binomial_pvalues(heldout_n)
    for h,count in zip(selected,matches):
        adjusted=min(1,len(selected)*float(pvalues[count])+M.null_coupling_bound(p.n,heldout_n))
        h.update(holdout_seed=20261110,holdout_n=heldout_n,holdout_corr=2*int(count)/heldout_n-1,
                 holdout_bonferroni_p=adjusted,confirmed_at_001=adjusted<.001)
    B.write_csv(output/"linear_deteksi_terisolasi_konfirmasi.csv",selected)
    print(f"Konfirmasi independen linear: {sum(h['confirmed_at_001'] for h in selected)}/{len(selected)} pasangan lolos",flush=True)


def correlation_figures(output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with (output/"korelasi_audit.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    rows=[r for r in rows if r["group"]=="all"]
    fields=list(dict.fromkeys(r["a"] for r in rows))
    fig,axes=plt.subplots(1,2,figsize=(14,6))
    for ax,field,title in zip(axes,("old_ordinal_ranks","spearman_average_ranks"),
                               ("Peringkat ordinal lama","Peringkat rata-rata (Spearman)")):
        values=np.array([[float(next(r[field] for r in rows if r["a"]==a and r["b"]==b))
                          for b in fields] for a in fields])
        im=ax.imshow(values,cmap="RdBu_r",vmin=-1,vmax=1)
        ax.set_xticks(range(len(fields)),fields,rotation=60,ha="right",fontsize=8)
        ax.set_yticks(range(len(fields)),fields,fontsize=8)
        ax.set_title(title)
    fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.03)
    fig.subplots_adjust(bottom=.31,wspace=.4,right=.87)
    for ext in ("png","pdf"):
        fig.savefig(output/f"korelasi_sebelum_sesudah.{ext}",dpi=220,bbox_inches="tight")
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",type=Path,required=True)
    args=parser.parse_args()
    root=args.data_dir
    output=root / "audit"
    output.mkdir(exist_ok=True)
    summaries={p.parent.name:json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*/ringkasan.json"))}
    records, detections, keyrecords = [],[],[]
    for label,summary in summaries.items():
        params=summary["parameter"]
        total=sum(p["rounds"] for p in summary["primitif"])*len(METRICS)
        for info in summary["primitif"]:
            p=next(p for p in P.PRIMITIVES.values() if p.name==info["name"])
            m=read_measurement(root / label / "medicoes" / f"{p.derived_from or p.key}.pkl.gz")
            rows=B.per_round_rows(p,m,params["pasangan_diff"])
            add_zero_legacy(rows,m)
            for policy in POLICIES:
                alpha=.001/total if policy=="experimentwise" else .001
                record,hits=horizon_record(rows,policy,alpha,label,p.name)
                records.append(record)
                detections.extend(dict(run=label,primitif=p.name,aturan=policy,round=i+1,**hit)
                                  for i,hit in enumerate(hits))
                if p.key=="clefia":
                    paired=[dict(r,round=i+1) for i,r in enumerate(rows[1::2])]
                    record,_=horizon_record(paired,policy,alpha,label,"CLEFIA-128 paired",2)
                    records.append(record)
            if label=="utama_seed2026" and p.with_key:
                for i in range(params["kunci"]):
                    km=read_measurement(root / label / "medicoes" / f"{p.key}_kunci_{i}.pkl.gz")
                    kr=B.per_round_rows(p,km,params["pasangan_diff"])
                    add_zero_legacy(kr,km)
                    for policy in POLICIES:
                        alpha=.001/total if policy=="experimentwise" else .001
                        rec,_=horizon_record(kr,policy,alpha,label,p.name)
                        keyrecords.append(dict(rec,key_index=i))
    B.write_csv(output / "horizon_semua_aturan.csv",records)
    B.write_csv(output / "deteksi_per_ronde.csv",detections)
    B.write_csv(output / "horizon_kunci_semua_aturan.csv",keyrecords)
    null_calibration(output)
    direct_permutation_sanity(output)
    correlation_audit(summaries,output)
    audit_figures(output,records)
    correlation_figures(output)
    confirm_isolated_linear(root,output)
    audit_whitening(root / "utama_seed2026",output)
    speeds=[]
    for i in range(5):
        for name,speed in B.measure_speed(list(P.PRIMITIVES.values()),2026+i,cpu_seconds=.25).items():
            speeds.append(dict(repetition=i+1,primitif=name,**speed))
    B.write_csv(output / "benchmark_ulang.csv",speeds)
    write_report(root,summaries,records,keyrecords)
    print(f"Audit selesai: {output}")


def write_report(root,summaries,records,keyrecords):
    old={"RECTANGLE-80":6,"CLEFIA-128":5,"Sparkle256":2,"Sparkle256-slim":2,
         "Sparkle384":2,"Sparkle384-slim":2,"Sparkle512":2,"Sparkle512-slim":2,"Alzette":4}
    L=["# Hasil eksperimen ulang dan klarifikasi makalah", "",
       "Tanggal: 10 November 2026 (Asia/Jakarta). Semua angka di bawah berasal dari eksekusi lokal yang disimpan, kecuali kolom draf yang disalin dari naskah awal.","",
       "## Desain", "",
       "Lima seed 2026–2030 memakai sampel penuh: avalanche 64, linear/statistik keluaran 2048, diferensial 1024 pasangan per tiga pola, dan 16 koset untuk masing-masing himpunan 4/8 bit aktif. Seed 2026 juga menguji delapan kunci RECTANGLE dan CLEFIA serta 32 sampel avalanche kunci. Replikasi seed lain memakai kunci default tetap; ini bukan pengulangan penuh delapan kunci pada setiap seed.","",
       "Satu eksperimen sensitivitas pada seed 2026 memakai avalanche 256, linear 8192, diferensial 4096, dan 32 koset. Perubahan jumlah sampel juga mengubah posisi aliran RNG, sehingga sampel besar bukan perluasan tersarang dari sampel utama.","",
       "CLEFIA diukur pada 18 ronde asli. Tabel tambahan mengambil ronde 2,4,...,18 dari pengukuran yang sama; sembilan titik ini bukan eksperimen independen. SPARKLE dan Alzette tidak memakai pembungkus XOR kunci. Konstanta Alzette adalah b7e15162. Varian slim berasal dari awalan pengukuran big.","",
       "## Horizon utama dan sensitivitas", "",
       "H adalah akhir deret deteksi bersambung dari ronde pertama. Angka ini bukan batas serangan. Tidak ada deteksi sejak awal direpresentasikan sebagai horizon individual kosong, sedangkan horizon gabungan menjadi 0. Deteksi setelah jeda tetap dicatat.","",
       "| Primitif | R | H draf | H aturan lama pada data baru | H terkoreksi | Rentang H lima seed | H sampel besar | H konservatif | H koreksi seluruh eksperimen |",
       "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    def find(run,name,policy):
        return next(r for r in records if r["run"]==run and r["primitif"]==name and r["aturan"]==policy)
    for name in old:
        main=find("utama_seed2026",name,"corrected")
        vals=[find(f"utama_seed{s}",name,"corrected")["H"] for s in range(2026,2031)]
        L.append(f"| {name} | {main['R']} | {old[name]} | {find('utama_seed2026',name,'legacy')['H']} | {main['H']} | {min(vals)}–{max(vals)} | {find('sampel_besar_seed2026',name,'corrected')['H']} | {find('utama_seed2026',name,'conservative')['H']} | {find('utama_seed2026',name,'experimentwise')['H']} |")
    L += ["","### Horizon individual utama","",
          "| Primitif | SAC | Linear | Diferensial | ZS4 | ZS8 |",
          "|---|---:|---:|---:|---:|---:|"]
    for name in old:
        r=find("utama_seed2026",name,"corrected")
        L.append("| "+name+" | "+" | ".join(str(r[k]) if r[k] is not None else "tidak terdeteksi sejak awal" for k in METRICS)+" |")
    paired=find("utama_seed2026","CLEFIA-128 paired","corrected")
    main_rect=summaries["utama_seed2026"]["per_ronde"]["RECTANGLE-80"]
    large_rect=summaries["sampel_besar_seed2026"]["per_ronde"]["RECTANGLE-80"]
    L += ["",f"Horizon gabungan yang sama tidak berarti seluruh metrik identik. Kelengkapan difusi teramati RECTANGLE pertama kali mencapai 1 pada ronde {M.first_round(main_rect,lambda r:r['completeness']==1)} untuk sampel avalanche 64, dan ronde {M.first_round(large_rect,lambda r:r['completeness']==1)} untuk sampel 256. Horizon diferensialnya berubah dari 3 menjadi 4, sedangkan SAC RECTANGLE pada kebijakan konservatif berakhir di ronde 5 dibanding ronde 6 pada agregat utama."]
    L += ["",f"CLEFIA tampilan pasangan ronde: H={paired['H']}/{paired['R']} unit, titik terakhir setara ronde asli {paired['H_native']}. Nilai ini dihitung dari titik genap dan tidak boleh dicampur dengan penyebut 18 ronde.","",
          "Kolom draf bukan reproduksi terverifikasi atas data lama: CSV/JSON dan versi kode pembentuk draf tidak tersedia. Perbedaan dapat berasal dari posisi bit aktif atau versi adapter selain dari perubahan aturan statistik.","",
          "## Koreksi statistik dan batas interpretasi", "",
          "1. Spearman memakai peringkat rata-rata untuk nilai sama, dan hasil tidak terdefinisi untuk deret konstan. `audit/korelasi_audit.csv` membandingkan peringkat ordinal lama dengan koreksi pada titik data yang identik, menambahkan analisis tanpa slim dan per primitif. Koefisien deskriptif ini tidak disertai klaim inferensi populasi atau kausalitas.",
          "2. SAC: peluang penolakan sel aktual untuk N=64 dan p<0,001 adalah 0,000617378264067, bukan 0,001. Agregat terkoreksi memakai Binomial(n²,q_actual) ditambah batas kopling. Di bawah label keluaran acak independen dan query berbeda, XOR terhadap keluaran dasar bersama menghasilkan indikator flip yang tetap independen. Jadi keberadaan keluaran dasar bersama saja tidak membatalkan model agregat. Ini mengklarifikasi keberatan awal pada telaah.",
          "3. Batas kopling SAC Q²/2^n mencakup overlap antarbintang masukan dan perbedaan model fungsi acak/permutasi acak. Untuk zero-sum dipakai batas duplikasi koset ditambah birthday bound jumlah query. Zero-sum binomial sah pada model label acak dengan koset berbeda; bukan otomatis keliru hanya karena bit-bit berasal dari transformasi deterministik. Nilai-p merupakan probabilitas di bawah model ideal, bukan bukti keamanan.",
          "4. Linear memakai nilai-p binomial eksak dua sisi untuk jumlah kesesuaian tanda dan Bonferroni atas n² pasangan per ronde, menggantikan aproksimasi normal. SAC konservatif memakai Bonferroni minimum nilai-p sel; zero-sum konservatif memakai batas Markov n·2^(-K)/m sehingga tidak memerlukan independensi antarindikator bit.",
          "5. Diferensial tetap mensyaratkan TopCount>=3. Di bawah permutasi ideal, peluang tiga pasangan masukan berbeda dengan dx sama mempunyai dy sama dibatasi 1/((2^n-3)(2^n-5)). Union bound mencakup semua kombinasi tiga pasangan, tiga pola dx, serta kemungkinan pasangan masukan terulang. Ini menjelaskan kejadian maksimum, bukan memakai 2^-n sebagai peluang seluruh pengujian.",
          "6. Aturan utama mengontrol ambang 0,001 per metrik per ronde, bukan seluruh penelitian. Kolom experimentwise memakai 0,001 dibagi lima kali jumlah ronde semua sembilan konfigurasi pada satu run; tidak mencakup seluruh seed, seluruh kunci, semua analisis tambahan, atau pemilihan hipotesis setelah melihat hasil.",
          "7. Kalibrasi null memakai 1.000.000 pengambilan statistik Binomial per ukuran keadaan/aturan, disertai probabilitas tipe-I eksak dan interval Wilson 95%. Ini bukan sejuta eksperimen algoritma dan bukan pengukuran daya deteksi pada alternatif. Model ideal memiliki batas beda terhadap permutasi yang dicatat terpisah.","",
          "## Kunci, whitening, dan statistik keluaran", "",
          "| Primitif | Rentang H delapan kunci, aturan terkoreksi |", "|---|---:|"]
    for name in ("RECTANGLE-80","CLEFIA-128"):
        vals=[r["H"] for r in keyrecords if r["primitif"]==name and r["aturan"]=="corrected"]
        L.append(f"| {name} | {min(vals)}–{max(vals)} |")
    corr=summaries["utama_seed2026"]["korelasi_metrik"]
    value=next(r["diff_top_frac"] for r in corr if r["metrik"]=="lin_sig_frac")
    with (root/"audit"/"korelasi_audit.csv").open(encoding="utf-8",newline="") as f:
        cr=list(csv.DictReader(f))
    ordinal=next(float(r["old_ordinal_ranks"]) for r in cr
                 if r["group"]=="all" and r["a"]=="lin_sig_frac" and r["b"]=="diff_top_frac")
    L += ["",f"Pada titik data baru yang identik, korelasi lin_sig_frac terhadap diff_top_frac adalah {ordinal:.3f} dengan peringkat ordinal lama dan {value:.3f} dengan Spearman yang benar. Angka 0,838 pada draf perlu diganti. Perbandingan pada data identik ini mengisolasi dampak penanganan ties; perbandingan langsung dengan draf juga dapat melibatkan perubahan uji linear.",""]
    L += ["", "Analisis kunci utama mengubah kunci dan sampel masukan sekaligus; perbedaan antarkunci belum dapat diatribusikan murni kepada kunci. `audit/whitening_avalanche_kunci.csv` mengulang avalanche kunci dengan aliran RNG sama dan finalisasi ciphertext lengkap pada titik akhir. Kunci ronde serta input whitening selalu tetap digunakan; yang dihilangkan oleh trace utama hanya finalisasi keluaran.","",
          "`audit/whitening_statistik.csv` membandingkan trace dan ciphertext pada sampel identik. XOR konstan mempertahankan beda XOR, avalanche plaintext, besar korelasi linear, dan zero-sum himpunan genap, tetapi dapat mengubah statistik sampel bobot Hamming dan entropi byte. Final whitening bergantung kunci sehingga pengaruhnya pada avalanche kunci harus diperiksa terpisah.","",
          "Entropi byte gabungan memakai jumlah observasi berbeda menurut ukuran keadaan; kolom byte_observations mencatatnya. Entropi rata-rata per posisi byte memakai 2048 masukan pada setiap posisi sehingga lebih mudah dibandingkan. Bahkan permutasi identitas memetakan masukan seragam menjadi keluaran seragam: statistik keluaran tunggal adalah sanity check, bukan ukuran kekuatan pencampuran.","",
          "## Kurva dan performa", "",
          "Kurva utama menggunakan 21 titik r/R termasuk nilai identitas pada ronde nol, interpolasi linear, dan enam metrik. `audit/kemiripan_sensitivitas.csv` mengulang kemiripan tanpa titik identitas pada interval yang sama-sama teramati. Kesamaan bentuk SPARKLE big/slim sebagian berasal dari pemakaian data yang sama. Normalisasi tidak menyetarakan biaya ronde atau kekuatan keamanan.","",
          "Benchmark mengukur seluruh trace Python, termasuk penyimpanan keadaan per ronde, tanpa ekspansi kunci di setiap evaluasi. Ini bukan throughput enkripsi produksi. `audit/benchmark_ulang.csv` memuat lima pengulangan bergilir dengan waktu CPU, dan ambiente.json mencatat CPU, OS, Python, NumPy, parameter, serta hash sumber. Pengulangan benchmark dijalankan setelah seluruh eksperimen selesai.","",
          "## Berkas dan reproduksi", "",
          "- `utama_seed2026/`: keluaran penuh, analisis delapan kunci, checkpoint mentah, dan grafik PNG/PDF.",
          "- `utama_seed2027/` sampai `utama_seed2030/`: replikasi seed pada kunci default.",
          "- `sampel_besar_seed2026/`: sensitivitas jumlah sampel dan grafik PNG/PDF.",
          "- `audit/horizon_semua_aturan.csv`: horizon, deteksi terakhir, dan deteksi setelah jeda untuk semua kebijakan dan tampilan pasangan ronde.",
          "- `audit/deteksi_per_ronde.csv`: keputusan per metrik per ronde.",
          "- `audit/kalibrasi_null.csv`: kalibrasi statistik dan batas pendekatan model.",
          "- `kode_sebelum_perbaikan.zip`: salinan kode sebelum modifikasi.","",
          "Reproduksi dari folder proyek: `python MODEL2C/ulang_eksperimen.py`. Runner melewati folder yang sudah mempunyai ringkasan lengkap; untuk eksperimen baru gunakan `--output-dir` baru. Checkpoint pickle hanya boleh dibaca dari hasil lokal yang dipercaya.","",
          "Sumber metode: [RFC 6114 dan vektor CLEFIA](https://www.rfc-editor.org/rfc/rfc6114.html), [spesifikasi SPARKLE](https://sparkle-lwc.github.io/sparkle), [definisi peringkat rata-rata Spearman](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/rankcorr.htm). Uji adapter bukan validasi independen seluruh desain; vektor resmi RECTANGLE/CLEFIA dan pemeriksaan SPARKLE terhadap referensi resmi dicatat terpisah dalam validasi."]
    reference_note=("Kode C resmi SPARKLE diunduh bersama lisensi, dan berhasil dikompilasi memakai Zig 0.13.0. Windows Application Control memblokir eksekusi binary (WinError 4551). Karena itu validasi eksekusi C independen belum lulus dan tidak diklaim; hasilnya tercatat di validasi/hasil_referensi_c.json. Jangan menyebut seluruh implementasi sudah tervalidasi independen."
                    if (root/"validasi"/"hasil_referensi_c.json").exists() else
                    "Validasi eksekusi C independen SPARKLE tidak dijalankan dalam folder hasil ini dan tidak diklaim lulus.")
    L += ["", "## Validasi dan keterbatasan pelaksanaan", "",
          "Uji adapter, regresi Spearman/ties, ukuran diskret SAC, simetri nilai-p hingga N=8192, unit CLEFIA, lingkup kunci, serta vektor RECTANGLE/CLEFIA lulus. Finalisasi ciphertext diperiksa terhadap implementasi asli pada 20 masukan tambahan.","",
          reference_note,"",
          "Audit juga mensimulasikan pembatasan permutasi acak langsung pada query berbeda: 500 pengulangan per ukuran keadaan. Interval tipe-I dari 500 ulangan lebar; gunakan perhitungan eksak dan kalibrasi satu juta statistik untuk menilai ambang 0,001, bukan mengartikan nol penolakan sebagai probabilitas nol.","",
          "Dokumen Word asli dipertahankan. Laporan ini menyediakan hasil dan klarifikasi untuk revisi naskah; belum merupakan naskah makalah yang sudah disunting."]
    confirmation=root/"audit"/"linear_deteksi_terisolasi_konfirmasi.csv"
    if confirmation.exists():
        with confirmation.open(encoding="utf-8",newline="") as f:
            checks=list(csv.DictReader(f))
        passed=sum(r["confirmed_at_001"]=="True" for r in checks)
        L += ["", "## Konfirmasi deteksi linear setelah jeda", "",
              f"Konfigurasi sampel besar menghasilkan deteksi linear CLEFIA pada ronde 13 dan 14. Koordinat {len(checks)} pasangan bit dibekukan dalam hipotesis_linear_sebelum_konfirmasi.json sebelum pengambilan data uji independen. Konfirmasi memakai 65.536 masukan baru, seed 20261110, dan Bonferroni hanya atas hipotesis yang telah dipilih pada data penemuan. Sebanyak {passed}/{len(checks)} pasangan terkonfirmasi pada ambang 0,001.","",
              "Hasil ini tidak mengubah definisi horizon bersambung. Tidak terkonfirmasi pada data baru belum merupakan bukti matematis bahwa deteksi awal palsu. Rincian korelasi dan nilai-p ada pada audit/linear_deteksi_terisolasi_konfirmasi.csv."]
    batch_note=("Seluruh enam pengukuran dasar seed 2026 diulang dengan evaluator baru dan seluruh nilai tersimpan persis sama, termasuk matriks keluaran dan detail zero-sum; lihat validasi/kesetaraan_batch.json."
                if (root/"validasi"/"kesetaraan_batch.json").exists() else
                "Uji regresi membandingkan trace batch dan skalar per ronde; bukti seluruh checkpoint dari paket eksperimen asli tidak disalin otomatis ke folder baru.")
    L += ["", "## Kesetaraan evaluator batch", "",
          "Evaluator uint32 batch dipakai untuk SPARKLE/Alzette agar sensitivitas sampel besar dapat diselesaikan lebih cepat. Jadwal evaluasi berubah, sementara algoritma, urutan pengambilan RNG, dan definisi metrik tetap. "+batch_note+" Hash sumber setiap run tetap disimpan karena versi evaluator dapat berbeda. Benchmark selalu memakai trace Python skalar asli."]
    (root / "HASIL_EKSPERIMEN_ULANG.md").write_text("\n".join(L)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
