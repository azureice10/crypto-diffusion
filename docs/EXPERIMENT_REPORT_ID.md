# Hasil eksperimen ulang dan klarifikasi makalah

**Pembaruan validasi:** laporan di bawah mempertahankan catatan eksekusi awal.
Validasi C SPARKLE yang semula terblokir di Windows telah berhasil dijalankan
di Linux pada 10 November 2026, tanpa perbedaan state. Lihat
[protokol dan bukti eksekusi lanjutan](SPARKLE_C_VALIDATION.md).

Tanggal: 10 November 2026 (Asia/Jakarta). Semua angka di bawah berasal dari eksekusi lokal yang disimpan, kecuali kolom draf yang disalin dari naskah awal.

## Desain

Lima seed 2026–2030 memakai sampel penuh: avalanche 64, linear/statistik keluaran 2048, diferensial 1024 pasangan per tiga pola, dan 16 koset untuk masing-masing himpunan 4/8 bit aktif. Seed 2026 juga menguji delapan kunci RECTANGLE dan CLEFIA serta 32 sampel avalanche kunci. Replikasi seed lain memakai kunci default tetap; ini bukan pengulangan penuh delapan kunci pada setiap seed.

Satu eksperimen sensitivitas pada seed 2026 memakai avalanche 256, linear 8192, diferensial 4096, dan 32 koset. Perubahan jumlah sampel juga mengubah posisi aliran RNG, sehingga sampel besar bukan perluasan tersarang dari sampel utama.

CLEFIA diukur pada 18 ronde asli. Tabel tambahan mengambil ronde 2,4,...,18 dari pengukuran yang sama; sembilan titik ini bukan eksperimen independen. SPARKLE dan Alzette tidak memakai pembungkus XOR kunci. Konstanta Alzette adalah b7e15162. Varian slim berasal dari awalan pengukuran big.

## Horizon utama dan sensitivitas

H adalah akhir deret deteksi bersambung dari ronde pertama. Angka ini bukan batas serangan. Tidak ada deteksi sejak awal direpresentasikan sebagai horizon individual kosong, sedangkan horizon gabungan menjadi 0. Deteksi setelah jeda tetap dicatat.

| Primitif | R | H draf | H aturan lama pada data baru | H terkoreksi | Rentang H lima seed | H sampel besar | H konservatif | H koreksi seluruh eksperimen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RECTANGLE-80 | 25 | 6 | 6 | 6 | 6–6 | 6 | 6 | 6 |
| CLEFIA-128 | 18 | 5 | 5 | 5 | 5–5 | 5 | 5 | 5 |
| Sparkle256 | 10 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Sparkle256-slim | 7 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Sparkle384 | 11 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Sparkle384-slim | 7 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Sparkle512 | 12 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Sparkle512-slim | 8 | 2 | 2 | 2 | 2–2 | 2 | 2 | 2 |
| Alzette | 4 | 4 | 4 | 4 | 4–4 | 4 | 4 | 4 |

### Horizon individual utama

| Primitif | SAC | Linear | Diferensial | ZS4 | ZS8 |
|---|---:|---:|---:|---:|---:|
| RECTANGLE-80 | 6 | 2 | 3 | 6 | 6 |
| CLEFIA-128 | 4 | 1 | 2 | 4 | 5 |
| Sparkle256 | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Sparkle256-slim | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Sparkle384 | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Sparkle384-slim | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Sparkle512 | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Sparkle512-slim | 2 | tidak terdeteksi sejak awal | tidak terdeteksi sejak awal | 1 | 1 |
| Alzette | 4 | tidak terdeteksi sejak awal | 3 | 3 | 2 |

Horizon gabungan yang sama tidak berarti seluruh metrik identik. Kelengkapan difusi teramati RECTANGLE pertama kali mencapai 1 pada ronde 5 untuk sampel avalanche 64, dan ronde 4 untuk sampel 256. Horizon diferensialnya berubah dari 3 menjadi 4, sedangkan SAC RECTANGLE pada kebijakan konservatif berakhir di ronde 5 dibanding ronde 6 pada agregat utama.

CLEFIA tampilan pasangan ronde: H=2/9 unit, titik terakhir setara ronde asli 4. Nilai ini dihitung dari titik genap dan tidak boleh dicampur dengan penyebut 18 ronde.

Kolom draf bukan reproduksi terverifikasi atas data lama: CSV/JSON dan versi kode pembentuk draf tidak tersedia. Perbedaan dapat berasal dari posisi bit aktif atau versi adapter selain dari perubahan aturan statistik.

## Koreksi statistik dan batas interpretasi

1. Spearman memakai peringkat rata-rata untuk nilai sama, dan hasil tidak terdefinisi untuk deret konstan. `audit/korelasi_audit.csv` membandingkan peringkat ordinal lama dengan koreksi pada titik data yang identik, menambahkan analisis tanpa slim dan per primitif. Koefisien deskriptif ini tidak disertai klaim inferensi populasi atau kausalitas.
2. SAC: peluang penolakan sel aktual untuk N=64 dan p<0,001 adalah 0,000617378264067, bukan 0,001. Agregat terkoreksi memakai Binomial(n²,q_actual) ditambah batas kopling. Di bawah label keluaran acak independen dan query berbeda, XOR terhadap keluaran dasar bersama menghasilkan indikator flip yang tetap independen. Jadi keberadaan keluaran dasar bersama saja tidak membatalkan model agregat. Ini mengklarifikasi keberatan awal pada telaah.
3. Batas kopling SAC Q²/2^n mencakup overlap antarbintang masukan dan perbedaan model fungsi acak/permutasi acak. Untuk zero-sum dipakai batas duplikasi koset ditambah birthday bound jumlah query. Zero-sum binomial sah pada model label acak dengan koset berbeda; bukan otomatis keliru hanya karena bit-bit berasal dari transformasi deterministik. Nilai-p merupakan probabilitas di bawah model ideal, bukan bukti keamanan.
4. Linear memakai nilai-p binomial eksak dua sisi untuk jumlah kesesuaian tanda dan Bonferroni atas n² pasangan per ronde, menggantikan aproksimasi normal. SAC konservatif memakai Bonferroni minimum nilai-p sel; zero-sum konservatif memakai batas Markov n·2^(-K)/m sehingga tidak memerlukan independensi antarindikator bit.
5. Diferensial tetap mensyaratkan TopCount>=3. Di bawah permutasi ideal, peluang tiga pasangan masukan berbeda dengan dx sama mempunyai dy sama dibatasi 1/((2^n-3)(2^n-5)). Union bound mencakup semua kombinasi tiga pasangan, tiga pola dx, serta kemungkinan pasangan masukan terulang. Ini menjelaskan kejadian maksimum, bukan memakai 2^-n sebagai peluang seluruh pengujian.
6. Aturan utama mengontrol ambang 0,001 per metrik per ronde, bukan seluruh penelitian. Kolom experimentwise memakai 0,001 dibagi lima kali jumlah ronde semua sembilan konfigurasi pada satu run; tidak mencakup seluruh seed, seluruh kunci, semua analisis tambahan, atau pemilihan hipotesis setelah melihat hasil.
7. Kalibrasi null memakai 1.000.000 pengambilan statistik Binomial per ukuran keadaan/aturan, disertai probabilitas tipe-I eksak dan interval Wilson 95%. Ini bukan sejuta eksperimen algoritma dan bukan pengukuran daya deteksi pada alternatif. Model ideal memiliki batas beda terhadap permutasi yang dicatat terpisah.

## Kunci, whitening, dan statistik keluaran

| Primitif | Rentang H delapan kunci, aturan terkoreksi |
|---|---:|
| RECTANGLE-80 | 6–6 |
| CLEFIA-128 | 5–5 |

Pada titik data baru yang identik, korelasi lin_sig_frac terhadap diff_top_frac adalah 0.838 dengan peringkat ordinal lama dan 0.583 dengan Spearman yang benar. Angka 0,838 pada draf perlu diganti. Perbandingan pada data identik ini mengisolasi dampak penanganan ties; perbandingan langsung dengan draf juga dapat melibatkan perubahan uji linear.


Analisis kunci utama mengubah kunci dan sampel masukan sekaligus; perbedaan antarkunci belum dapat diatribusikan murni kepada kunci. `audit/whitening_avalanche_kunci.csv` mengulang avalanche kunci dengan aliran RNG sama dan finalisasi ciphertext lengkap pada titik akhir. Kunci ronde serta input whitening selalu tetap digunakan; yang dihilangkan oleh trace utama hanya finalisasi keluaran.

`audit/whitening_statistik.csv` membandingkan trace dan ciphertext pada sampel identik. XOR konstan mempertahankan beda XOR, avalanche plaintext, besar korelasi linear, dan zero-sum himpunan genap, tetapi dapat mengubah statistik sampel bobot Hamming dan entropi byte. Final whitening bergantung kunci sehingga pengaruhnya pada avalanche kunci harus diperiksa terpisah.

Entropi byte gabungan memakai jumlah observasi berbeda menurut ukuran keadaan; kolom byte_observations mencatatnya. Entropi rata-rata per posisi byte memakai 2048 masukan pada setiap posisi sehingga lebih mudah dibandingkan. Bahkan permutasi identitas memetakan masukan seragam menjadi keluaran seragam: statistik keluaran tunggal adalah sanity check, bukan ukuran kekuatan pencampuran.

## Kurva dan performa

Kurva utama menggunakan 21 titik r/R termasuk nilai identitas pada ronde nol, interpolasi linear, dan enam metrik. `audit/kemiripan_sensitivitas.csv` mengulang kemiripan tanpa titik identitas pada interval yang sama-sama teramati. Kesamaan bentuk SPARKLE big/slim sebagian berasal dari pemakaian data yang sama. Normalisasi tidak menyetarakan biaya ronde atau kekuatan keamanan.

Benchmark mengukur seluruh trace Python, termasuk penyimpanan keadaan per ronde, tanpa ekspansi kunci di setiap evaluasi. Ini bukan throughput enkripsi produksi. `audit/benchmark_ulang.csv` memuat lima pengulangan bergilir dengan waktu CPU, dan ambiente.json mencatat CPU, OS, Python, NumPy, parameter, serta hash sumber. Pengulangan benchmark dijalankan setelah seluruh eksperimen selesai.

## Berkas dan reproduksi

- `utama_seed2026/`: keluaran penuh, analisis delapan kunci, checkpoint mentah, dan grafik PNG/PDF.
- `utama_seed2027/` sampai `utama_seed2030/`: replikasi seed pada kunci default.
- `sampel_besar_seed2026/`: sensitivitas jumlah sampel dan grafik PNG/PDF.
- `audit/horizon_semua_aturan.csv`: horizon, deteksi terakhir, dan deteksi setelah jeda untuk semua kebijakan dan tampilan pasangan ronde.
- `audit/deteksi_per_ronde.csv`: keputusan per metrik per ronde.
- `audit/kalibrasi_null.csv`: kalibrasi statistik dan batas pendekatan model.
- `kode_sebelum_perbaikan.zip`: salinan kode sebelum modifikasi.

Reproduksi dari folder proyek: `python MODEL2C/ulang_eksperimen.py`. Runner melewati folder yang sudah mempunyai ringkasan lengkap; untuk eksperimen baru gunakan `--output-dir` baru. Checkpoint pickle hanya boleh dibaca dari hasil lokal yang dipercaya.

Sumber metode: [RFC 6114 dan vektor CLEFIA](https://www.rfc-editor.org/rfc/rfc6114.html), [spesifikasi SPARKLE](https://sparkle-lwc.github.io/sparkle), [definisi peringkat rata-rata Spearman](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/rankcorr.htm). Uji adapter bukan validasi independen seluruh desain; vektor resmi RECTANGLE/CLEFIA dan pemeriksaan SPARKLE terhadap referensi resmi dicatat terpisah dalam validasi.

## Validasi dan keterbatasan pelaksanaan

Uji adapter, regresi Spearman/ties, ukuran diskret SAC, simetri nilai-p hingga N=8192, unit CLEFIA, lingkup kunci, serta vektor RECTANGLE/CLEFIA lulus. Finalisasi ciphertext diperiksa terhadap implementasi asli pada 20 masukan tambahan.

Kode C resmi SPARKLE diunduh bersama lisensi, dan berhasil dikompilasi memakai Zig 0.13.0. Windows Application Control memblokir eksekusi binary (WinError 4551). Karena itu validasi eksekusi C independen belum lulus dan tidak diklaim; hasilnya tercatat di validasi/hasil_referensi_c.json. Jangan menyebut seluruh implementasi sudah tervalidasi independen.

Audit juga mensimulasikan pembatasan permutasi acak langsung pada query berbeda: 500 pengulangan per ukuran keadaan. Interval tipe-I dari 500 ulangan lebar; gunakan perhitungan eksak dan kalibrasi satu juta statistik untuk menilai ambang 0,001, bukan mengartikan nol penolakan sebagai probabilitas nol.

Dokumen Word asli dipertahankan. Laporan ini menyediakan hasil dan klarifikasi untuk revisi naskah; belum merupakan naskah makalah yang sudah disunting.

## Konfirmasi deteksi linear setelah jeda

Konfigurasi sampel besar menghasilkan deteksi linear CLEFIA pada ronde 13 dan 14. Koordinat 2 pasangan bit dibekukan dalam hipotesis_linear_sebelum_konfirmasi.json sebelum pengambilan data uji independen. Konfirmasi memakai 65.536 masukan baru, seed 20261110, dan Bonferroni hanya atas hipotesis yang telah dipilih pada data penemuan. Sebanyak 0/2 pasangan terkonfirmasi pada ambang 0,001.

Hasil ini tidak mengubah definisi horizon bersambung. Tidak terkonfirmasi pada data baru belum merupakan bukti matematis bahwa deteksi awal palsu. Rincian korelasi dan nilai-p ada pada audit/linear_deteksi_terisolasi_konfirmasi.csv.

## Kesetaraan evaluator batch

Evaluator uint32 batch dipakai untuk SPARKLE/Alzette agar sensitivitas sampel besar dapat diselesaikan lebih cepat. Jadwal evaluasi berubah, sementara algoritma, urutan pengambilan RNG, dan definisi metrik tetap. Seluruh enam pengukuran dasar seed 2026 diulang dengan evaluator baru dan seluruh nilai tersimpan persis sama, termasuk matriks keluaran dan detail zero-sum; lihat validasi/kesetaraan_batch.json. Hash sumber setiap run tetap disimpan karena versi evaluator dapat berbeda. Benchmark selalu memakai trace Python skalar asli.
