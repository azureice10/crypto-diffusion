"""Generate explanatory reports from verified, frozen mechanism outputs."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent/'sac_mechanism'))
import mechanism as M


def main(folder,report_root):
    metrics=M.C.read_csv(folder/'condition_metrics.csv');bins=M.C.read_csv(folder/'bin_contributions.csv')
    covariance=M.C.read_csv(folder/'dependence_decomposition.csv');models=M.C.read_csv(folder/'surrogate_summary.csv')
    layouts=M.C.read_csv(folder/'layout_summary.csv')
    verification=json.loads((folder/'verification.json').read_text(encoding='utf-8'));assert verification['status']=='PASS'
    def condition(key,N,r):return next(x for x in metrics if x['key_id']==key and int(x['N'])==N and int(x['native_round'])==r)
    def model(case,group,method='basic'):return next(x for x in models if x['case']==case and x['group']==group and x['method']==method)
    selected=condition('default',256,7);r8=condition('default',256,8);r8large=condition('default',1024,8)
    b7=[x for x in bins if x['key_id']=='default' and x['N']=='256' and x['native_round']=='7']
    cov=sum(float(x['net_empirical_covariance']) for x in covariance if x['case']=='N256_r7')
    independent=sum(float(x['product_marginal_scatter']) for x in covariance if x['case']=='N256_r7')
    tail_fraction=sum(float(x['fraction_of_mean_basic']) for x in b7 if x['bin'] in ('1','8'))
    with np.load(folder/'coordinate_maps.npz',allow_pickle=False) as maps:
        p=maps['default_N256_r7_p_hat'];mask=maps['default_N256_r7_marginal_significant'];energy=(p-.5)**2
    input_energy=energy.sum(axis=1).reshape(4,16).sum(axis=1)/energy.sum()
    output_energy=energy.sum(axis=0).reshape(4,16).sum(axis=1)/energy.sum()
    key_conditions=[condition(k['key_id'],256,7) for k in M.C.KEYS]
    interpretations={'schema':'sac-mechanism-interpretation/1','report_source_sha256':M.C.digest(Path(__file__)),
        'scientific_source_commit':'6d60cfb6c84a4cc02717e1896ec0d19671f08693',
        'default_N256_r7':{'mean_basic':float(selected['mean_basic']),
             'shape':float(selected['shape_component']),'scatter':float(selected['scatter_component']),
             'shape_fraction':float(selected['shape_fraction_of_mean_basic']),
             'independent_empirical_scatter':independent,'net_empirical_covariance':cov,
             'net_covariance_fraction_of_mean':cov/float(selected['mean_basic']),
             'mean_flip_probability':float(selected['mean_flip_probability']),
             'count_statistic_mean':float(model('N256_r7','actual_train','count')['mean_statistic'])/2+float(model('N256_r7','actual_holdout','count')['mean_statistic'])/2,
             'count_critical_cells':M.C.SIZE.count_spec(256)['critical'],
             'marginal_significant_negative':int(np.sum(mask&(p<.5))),
             'marginal_significant_positive':int(np.sum(mask&(p>.5))),
             'outer_histogram_bins_mean_contribution_fraction':tail_fraction,
             'input_word_squared_bias_energy_fractions':input_energy.tolist(),
             'output_word_squared_bias_energy_fractions':output_energy.tolist()},
        'source_input_sha256':{name:M.C.digest(folder/name) for name in ('condition_metrics.csv','bin_contributions.csv','dependence_decomposition.csv','surrogate_summary.csv','layout_summary.csv','coordinate_maps.npz','verification.json')},
        'scope':'Interpretation of an exploratory statistical diagnostic; covariance is a signed net contribution to mean Basic, not a measure of all dependence or a percent of power explained.'}
    M.C.save_json(folder/'interpretation.json',interpretations)
    def pct(x,d=1):return f'{100*float(x):.{d}f}'
    def fmt(x,d=3):return f'{float(x):.{d}f}'
    table=['| Bin / rentang hitungan K | Ekspektasi sel | Rata-rata aktual | Kontribusi Pearson | Bagian rata-rata Basic |',
           '|---|---:|---:|---:|---:|']
    for row in b7:table.append(f"| {row['bin']}: {row['count_low_inclusive']}–{row['count_high_inclusive']} | {fmt(row['ideal_expected_cells'],1)} | {fmt(row['mean_observed_cells'],1)} | {fmt(row['mean_pearson_contribution'],2)} | {pct(row['fraction_of_mean_basic'])}% |")
    bin_table='\n'.join(table)
    table=['| Kunci | Mean flip (%) | Bagian bentuk rata-rata (%) | Koordinat signifikan r7,N=256 | Koordinat signifikan r8,N=1.024 |',
           '|---|---:|---:|---:|---:|']
    for key,row in zip(M.C.KEYS,key_conditions):
        label='Default' if key['key_id']=='default' else 'K'+str(key['key_index'])
        table.append(f"| {label} | {pct(row['mean_flip_probability'],4)} | {pct(row['shape_fraction_of_mean_basic'])} | {row['marginal_significant_cells']} | {condition(key['key_id'],1024,8)['marginal_significant_cells']} |")
    key_table='\n'.join(table)
    table=['| Kondisi | Kelompok / jumlah matriks | Count | Basic | Row | Column |',
           '|---|---|---:|---:|---:|---:|']
    names={'actual_holdout':'Holdout aktual (250)','iid_fair_binomial':'Binomial fair independen (10.000)',
           'independent_fitted_binomial':'Binomial marginal terpasang (10.000)',
           'independent_empirical_cells':'Marginal empiris independen (10.000)'}
    for case in M.P['default_cases']:
        name=M.case_name(case)
        for group,label in names.items():
            table.append(f"| r={case['round']}, N={case['N']} | {label} | "+' | '.join(pct(model(name,group,m)['rate'],2)+'%' for m in M.C.METHODS)+' |')
    model_table='\n'.join(table)
    table=['| Metode | Holdout asli | Posisi diacak | Δ (pp) | CI bootstrap per-parent 95% untuk Δ |',
           '|---|---:|---:|---:|---|']
    for method in M.C.METHODS:
        row=next(x for x in layouts if x['case']=='N1024_r7' and x['method']==method)
        table.append(f"| {method.title()} | {pct(row['original_rate'],2)}% | {pct(row['permuted_rate'],2)}% | {pct(row['permuted_minus_original_rate'],2)} | [{pct(row['parent_bootstrap95_low'],2)}; {pct(row['parent_bootstrap95_high'],2)}] |")
    layout_table='\n'.join(table)
    mean_range=[float(x['mean_flip_probability']) for x in key_conditions]
    shape_range=[float(x['shape_fraction_of_mean_basic']) for x in key_conditions]
    text=f'''Analisis mekanisme statistik SAC-Basic — 11 November 2026

**Hasil utama: Basic menangkap pergeseran kecil yang konsisten pada distribusi hitungan SAC.** Pada RECTANGLE ronde 7,N=256, rata-rata peluang flip default key adalah {pct(selected['mean_flip_probability'],4)}%, dibanding referensi 50%. Selisih sekitar 0,324 poin persentase tampak kecil, tetapi pola itu terakumulasi dalam histogram 4.096 pasangan bit. Count mempertahankan hanya sel yang lolos ambang ekstrem.

Rata-rata statistik Basic adalah {fmt(selected['mean_basic'])}: komponen bentuk histogram rata-rata {fmt(selected['shape_component'])} ({pct(selected['shape_fraction_of_mean_basic'])}%), dan komponen variasi antarreplikasi {fmt(selected['scatter_component'])}. Term kovarians net empiris adalah {cov:.3f}, sekitar {100*cov/float(selected['mean_basic']):.2f}% dari rata-rata Basic. Persentase ini merupakan dekomposisi rata-rata statistik, bukan persentase daya deteksi atau ukuran seluruh ketergantungan.

Pada model pembanding yang menghapus ketergantungan antarsel, frekuensi penolakan Basic tetap {pct(model('N256_r7','independent_fitted_binomial')['rate'],2)}% untuk marginal binomial terpasang dan {pct(model('N256_r7','independent_empirical_cells')['rate'],2)}% untuk marginal empiris. Data holdout memberi {pct(model('N256_r7','actual_holdout')['rate'])}%. Jadi penyimpangan marginal cukup untuk mereproduksi sebagian besar perilaku Basic pada kondisi ini; ketergantungan tidak perlu menjadi penjelasan dominan. Ini belum mengidentifikasi penyebab aljabarnya pada cipher.

**Desain dan keterlacakan.** Analisis eksploratif ini diinformasikan hasil deteksi sebelumnya. Protokol dan kode statistik dibekukan pada commit `6d60cfb6c84a4cc02717e1896ec0d19671f08693`; pengujian pendahuluan memakai data sintetis. Arsip konfirmasi sembilan kunci dipakai kembali untuk 54 kondisi (dua N, tiga ronde). Matriks default key diregenerasi dari 500 seed lama, dan seluruh 3.000 hash matriks ronde analisis cocok; 1.500 matriks pada tiga kondisi disimpan untuk diagnosis rinci. Tidak ada replikasi input cipher baru.

Model marginal dipasang pada replikasi 0–249; replikasi 250–499 dipakai sebagai holdout internal. Ada 90.000 matriks pembanding sintetis dan 30.000 pengacakan posisi. Holdout ini berasal dari arsip yang sudah diketahui, sehingga bukan konfirmasi baru yang dikumpulkan secara independen. Bank kalibrasi dan aturan ukuran nol yang didekatkan ke Count tetap sama.

**1. Apa yang bergeser pada histogram?** Bin pertama (K≤119) memiliki rata-rata {fmt(b7[0]['mean_observed_cells'],1)} sel, dibanding ekspektasi {fmt(b7[0]['ideal_expected_cells'],1)}. Bin terakhir (K≥138) memiliki {fmt(b7[-1]['mean_observed_cells'],1)} sel, dibanding {fmt(b7[-1]['ideal_expected_cells'],1)}. Ada surplus hitungan relatif rendah dan defisit hitungan tinggi. Kedua bin menyumbang {pct(tail_fraction)}% rata-rata statistik Basic.

{bin_table}

Bin kuantil tidak mempunyai probabilitas tepat 1/8 karena hitungan diskret; ekspektasi di atas memakai probabilitas eksak yang sama dengan eksperimen sebelumnya. Rata-rata jumlah sel ekstrem yang digunakan Count hanya {interpretations['default_N256_r7']['count_statistic_mean']:.3f}; keputusan Count memerlukan sedikitnya {interpretations['default_N256_r7']['count_critical_cells']} sel ekstrem. Kenaikan sekitar 110 sel pada bin pertama terutama merupakan perubahan histogram luas, bukan 110 sel yang semuanya melampaui cutoff Count. Inilah perbedaan informasi yang dimanfaatkan kedua statistik.

Histogram tiap replikasi tetap mempunyai 4.096 sel dengan count K dari N=256. Menggabungkan 500 replikasi untuk menghitung rata-rata histogram tidak mengganti referensinya menjadi Binomial(500N,½).

**2. Apa yang tampak pada peta koordinat?** Dengan menggabungkan 500 replikasi untuk estimasi marginal, {selected['marginal_significant_cells']} koordinat pada default r7,N=256 menolak peluang flip ½ setelah Bonferroni atas 221.184 uji dalam grid ini. Seluruh {interpretations['default_N256_r7']['marginal_significant_negative']} koordinat tersebut memiliki bias negatif; tidak ada koordinat signifikan positif. Keluarga ini adalah audit SAC marginal pada map berkunci tetap, berbeda dari referensi ideal-permutation pada detektor utama. Koreksinya tidak mencakup semua pilihan analisis adaptif di seluruh proyek.

Pola tidak seragam pada seluruh matriks. Energi kuadrat bias terestimasi pada input indeks 16–31 dan 48–63 masing-masing sekitar {pct(input_energy[1])}% dan {pct(input_energy[3])}%. Jumlah efektif baris input berdasarkan kuadrat bias mentah adalah {fmt(selected['effective_input_rows_raw_squared_bias'],1)}, dibanding {fmt(selected['effective_output_columns_raw_squared_bias'],1)} untuk kolom output. Besaran ini deskriptif dan masih memuat noise estimasi. Pola blok/diagonal yang terlihat belum merupakan penurunan matematis bahwa ShiftRows atau S-box tertentu menyebabkan efeknya.

RMS bias marginal setelah koreksi noise sekitar {100*float(selected['noise_corrected_rms_display']):.3f} poin persentase. Koreksi menggunakan estimator tak-bias untuk kuadrat bias; nilai negatif tetap disimpan, dan hanya akar untuk tampilan yang dicap nonnegatif setelah perataan.

**Konsistensi deskriptif pada sembilan kunci.**

{key_table}

Rata-rata flip r7,N=256 berada pada {100*min(mean_range):.4f}–{100*max(mean_range):.4f}% dan bagian bentuk histogram pada {100*min(shape_range):.1f}–{100*max(shape_range):.1f}%. Diagnosis rinci pembanding/kovarians di bawah dilakukan pada default key; delapan kunci lainnya memberikan bukti deskriptif, bukan replikasi diagnosis lengkap.

**3. Apa peran ketergantungan antarsel?** Identitas empiris pada 500 matriks default adalah:

`mean Basic = bentuk rata-rata + variasi marginal independen + kovarians net`

`{float(selected['mean_basic']):.3f} = {float(selected['shape_component']):.3f} + {independent:.3f} + {cov:.3f}`.

Kovarians net merupakan jumlah bertanda dan dapat menyembunyikan pembatalan ketergantungan positif/negatif. Nilainya yang kecil tidak membuktikan sel independen, dan tidak membatasi pengaruh ketergantungan pada semua ekor distribusi atau semua detektor. Simulasi pembanding berikut melengkapi identitas tersebut.

{model_table}

Model binomial terpasang mempertahankan estimasi peluang tiap koordinat, lalu menggambar sel secara independen. Model empiris menggambar ulang setiap sel secara independen dari count sel yang sama pada 250 matriks training. Keduanya menghapus seluruh ketergantungan antarsel; tidak hanya ketergantungan akibat basis X bersama. Matriks sintetis ini tidak diasumsikan dapat direalisasikan oleh cipher yang sah. Interval Wilson model bersifat kondisional pada distribusi yang dipasang dan tidak memasukkan ketidakpastian estimasi parameter.

Kesesuaian model paling jelas untuk Basic. Pada N=1.024, prediksi Count 13,44% dan 11,17% lebih rendah daripada 19,60% pada holdout aktual. Jadi model marginal belum merupakan model generatif lengkap untuk seluruh statistik cipher. Ketidakpastian pemasangan, sampling, dan ketergantungan pada kejadian ekstrem tetap relevan. Sepuluh ribu draw fair juga terlalu sedikit untuk mengganti validasi rare-event satu juta draw sebelumnya.

**4. Mengapa Row dan Column dapat berbeda?** Pada default r7,N=1.024, posisi 4.096 sel dari setiap matriks holdout diacak 40 kali. Multiset nilai tidak berubah. Basic dan Count persis invarian pada seluruh 30.000 pengacakan di tiga kondisi. Hasil Row dan Column berubah karena penempatan nilai pada baris/kolom berubah.

{layout_table}

Row turun dari 14,8% ke 3,10%, sedangkan Column berada di 3,15% setelah pengacakan. Kedekatan Row–Column sesudah pengacakan sesuai simetri posisi acak. Ini mendukung peran susunan spasial penyimpangan dalam asimetri statistik sumbu. Pengacakan observasi bukan transformasi cipher yang sah dan tidak membuktikan lapisan kriptografis mana penyebabnya.

Count tetap 19,6% setelah pengacakan, sehingga celah relatif Count–Column tidak hilang. Data mendukung peran lokasi dalam kelebihan Row atas Column; lokasi saja belum menjelaskan seluruh perbedaan Count–Column. Perbedaan agregasi global Count dan maksimum-sumbu Column tetap relevan.

Empat puluh pengacakan pada satu matriks tetap satu parent data. CI resample 250 parent holdout, bukan memperlakukan 10.000 pengacakan per kondisi sebagai input cipher independen. CI ini eksploratif, pointwise dan kondisional pada sampel; kasus penolakan yang sangat jarang atau nol parent tidak boleh dipakai untuk klaim signifikansi kuat dari bootstrap saja.

**5. Apa arti kontrol ronde 8?** Pada N=256, mean Basic turun ke {fmt(r8['mean_basic'])}, dekat referensi iid delapan-bin sebesar 7; bentuk rata-rata hanya {fmt(r8['shape_component'])}. Tidak ada koordinat yang signifikan pada budget pooled tersebut. Namun pada r8,N=1.024, audit pooled menemukan {r8large['marginal_significant_cells']} koordinat signifikan, sementara Basic per-replikasi hanya {r8large['basic_detections']}/500. Ini memakai 500N=512.000 basis per koordinat, jauh lebih banyak daripada satu uji N=1.024. Temuan tersebut memperkuat perlunya menyebut budget; non-detection bukan bukti SAC sempurna. Horizon kontinu baru tidak ditetapkan dari diagnosis ini.

**Revisi yang didukung.** Diskusi dapat menjelaskan bahwa Basic mengakumulasi perubahan distribusi marginal yang moderat dan searah, sementara Count membuang sel yang belum ekstrem. Asimetri Row–Column mendapat bukti dari pola koordinat dan ablation lokasi. Ganti dugaan bahwa ketergantungan adalah penjelasan utama dengan bukti kuantitatif yang lebih terbatas: term kovarians net Basic kecil dan marginal independen sudah mereproduksi deteksinya pada default key. Jangan menggeneralisasikan kesimpulan itu ke semua detektor atau semua kunci.

Hasil ini juga tidak menunjukkan Basic unik atau optimal; statistik agregat lain mungkin memanfaatkan pergeseran mean yang sama. Mekanisme statistik telah diperjelas, sedangkan atribusi ke S-box/ShiftRows atau pemisahan shared-base dari ketergantungan intrinsik masih memerlukan eksperimen/analisis lain. Naskah Word belum diubah pada pekerjaan ini.

**Artefak dan QA.**

- [Histogram dan kontribusi bin](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/bin_distribution.png), [peta bias](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/marginal_bias_maps.png), [pembanding marginal](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/surrogate_diagnostics.png), dan [ablation posisi](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/layout_ablation.png).
- [Ringkasan interpretasi numerik](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/interpretation.json), [metrik seluruh kondisi](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/condition_metrics.csv), [kontribusi seluruh bin](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/bin_contributions.csv), [dekomposisi kovarians](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/dependence_decomposition.csv), dan [verifikasi](jictra-crypto-diffusion-supplement/data/followup/sac_mechanism_2026-11-11/verification.json).
- [Kode, protokol dan reproduksi](jictra-crypto-diffusion-supplement/experiments/sac_mechanism/README.md). Lima tes awal lolos. Verifikasi mencakup 54 kondisi, 432 baris bin, 221.184 uji koordinat, 1.500 hash matriks yang disimpan, 1.152 matriks probe pembanding, dan seluruh 30.000 pengacakan dengan invariansi Basic/Count. Seluruh data dan sumber eksperimen terdahulu tetap identik.
'''
    report_root.mkdir(parents=True,exist_ok=True)
    (report_root/'HASIL_ANALISIS_MEKANISME_SAC_BASIC.md').write_text(text,encoding='utf-8',newline='\n')
    english=f'''# Statistical mechanism of SAC-Basic detection

Exploratory analysis dated 11 November 2026. Statistical code/plan were frozen
in `6d60cfb6c84a4cc02717e1896ec0d19671f08693` before main mechanism outputs;
preflight used synthetic data. The existing nine-key confirmation archive is
reused across 54 conditions. Default matrices are replayed with all 3000
original matrix hashes checked; no new cipher input replications are added.

At RECTANGLE round 7,N=256, default-key mean flip probability is
{float(selected['mean_flip_probability']):.8f}. Mean Basic is {float(selected['mean_basic']):.3f}, comprising
{float(selected['shape_component']):.3f} mean-shape and {float(selected['scatter_component']):.3f} scatter contributions.
The net empirical cross-cell covariance contributes {cov:.3f}; this is a signed
contribution to the statistic's mean, not a measure of all dependence or a
fraction of power explained. Bins 1/8 contribute {100*tail_fraction:.1f}% of mean Basic.
Count averages {interpretations['default_N256_r7']['count_statistic_mean']:.3f} extreme cells, below its 12-cell threshold.

Pooled marginal SAC tests find 588 significant coordinates, all negative,
under a 0.05/221184 Bonferroni cutoff for this exploratory grid. These are
fixed-map marginal tests, distinct from the original ideal-permutation null;
they do not control all adaptive analyses across the project. Raw squared
bias is concentrated in input bits 16–31 and 48–63. Observed patterns do not
identify a particular cipher layer. Across nine keys, mean flip probability
ranges {min(mean_range):.8f}–{max(mean_range):.8f} and mean-shape fractions
{100*min(shape_range):.1f}–{100*max(shape_range):.1f}%.

Models fit on replicas 0–249 are compared with the existing holdout 250–499.
With cross-cell dependence removed, fitted-binomial and empirical-marginal
Basic rejection rates are 96.47% and 96.77%, versus 95.6% observed holdout.
This supports a marginal-distribution explanation at the default key; it is
not unique causal identification or independent new data confirmation.
Fitted-model intervals omit estimation uncertainty. Count is less well
predicted at N=1024 (13.44%/11.17% versus 19.60% observed), so the models
do not explain the complete joint behavior of every detector.
Synthetic count matrices need not correspond to any valid cipher.

Uniformly permuting cell positions preserves Basic and Count exactly.
For round 7,N=1024, Row falls from 14.8% to 3.10% and permuted Column is
3.15%, supporting an effect of spatial assignment on axis statistics.
Count remains 19.6%, so spatial rearrangement does not remove the entire
Count–Column difference; global-count versus maximum-axis aggregation remains
relevant.
Forty permutations per holdout matrix are clustered within 250 parent
replications. Intervals resample parents and are exploratory; rare parent
outcomes limit bootstrap interpretation. No ShiftRows/S-box cause follows.

Round 8,N=256 has mean Basic {float(r8['mean_basic']):.3f} near the iid reference 7.
At N=1024, pooled 500N marginal tests nevertheless detect {r8large['marginal_significant_cells']} coordinates,
while per-replica Basic rejects {r8large['basic_detections']}/500. The pooled budget is 500 times larger;
non-detection is not perfect SAC, and no new contiguous horizon is defined.

There are 90000 synthetic surrogate matrices and 30000 layout permutations,
not 120000 new cipher replications. Fair-model tail counts at 10000 draws
do not replace the previous million-draw null validation. Product-marginal
models remove all cross-cell dependence without isolating shared-base effects.
Mean-shape departures may also be exploitable by other aggregate tests;
the analysis does not establish Basic as unique or optimal.

See [protocol/reproduction](../experiments/sac_mechanism/README.md),
[numeric interpretation](../data/followup/sac_mechanism_2026-11-11/interpretation.json),
[all condition metrics](../data/followup/sac_mechanism_2026-11-11/condition_metrics.csv),
[bin contributions](../data/followup/sac_mechanism_2026-11-11/bin_contributions.csv),
[surrogate results](../data/followup/sac_mechanism_2026-11-11/surrogate_summary.csv),
[layout results](../data/followup/sac_mechanism_2026-11-11/layout_summary.csv),
and [verification](../data/followup/sac_mechanism_2026-11-11/verification.json).

![Count distribution and contributions](../data/followup/sac_mechanism_2026-11-11/bin_distribution.png)
![Default marginal maps, pooled N=256](../data/followup/sac_mechanism_2026-11-11/marginal_bias_maps.png)
![Marginal surrogates](../data/followup/sac_mechanism_2026-11-11/surrogate_diagnostics.png)
![Position permutation](../data/followup/sac_mechanism_2026-11-11/layout_ablation.png)
'''
    (M.ROOT/'docs/SAC_MECHANISM.md').write_text(english,encoding='utf-8',newline='\n')
    print(json.dumps(interpretations['default_N256_r7'],indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--report-root',type=Path,required=True);args=parser.parse_args();main(args.input,args.report_root)
