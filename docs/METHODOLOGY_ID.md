# Dasar koreksi dan model null

Semua uji menilai transformasi per ronde terhadap model ideal yang dinyatakan
di sini. Tidak ada klaim bahwa uji memiliki daya yang sama untuk seluruh
ukuran keadaan. Analisis algoritma berkunci memakai kunci tetap kecuali saat
secara eksplisit menguji avalanche kunci atau variasi kunci.

## 1. SAC: ukuran uji diskret dan struktur dependensi

Dengan N masukan, hitungan flip satu sel mempunyai model Binomial(N, 1/2)
di bawah keluaran acak independen. Definisikan p_N(k) sebagai nilai-p eksak
dua sisi (maksimum 1) untuk hitungan k. Peluang penolakan sel yang sebenarnya:

q_N = sum_{k: p_N(k) < alpha_cell} C(N,k) / 2^N.

Untuk N=64 dan alpha_cell=0,001, q_N=0,0006173782640671298.
Mengganti q_N dengan alpha_cell pada distribusi agregat tidak tepat; pada
konfigurasi ini aturan lama lebih konservatif terhadap model ideal.

Pada satu bintang masukan, sebuah masukan dasar X dan seluruh X xor e_i
berbeda. Jika label keluaran pada query-query itu independen dan seragam,
vektor (Y_i xor Y_0) tetap independen dan seragam setelah dikondisikan pada
Y_0. Distribusi tersebut tidak bergantung pada Y_0. Jadi keluaran dasar yang
dipakai bersama tidak dengan sendirinya menimbulkan dependensi pada indikator
flip di model null ini. Bila seluruh bintang masukan tidak beririsan, sel-sel
matriks hitungan juga independen dan V ~ Binomial(n²,q_N).

Untuk N bintang acak, peluang overlap antarbintang dibatasi
C(N,2)(n+1)²/2^n. Pergantian model label independen menjadi permutasi seragam
pada Q=N(n+1) query menambah paling banyak C(Q,2)/2^n. Jumlah kedua batas
tersebut tidak melebihi Q²/2^n. Nilai-p yang dilaporkan dibatasi maksimum 1:

p_SAC = min(1, P[Binomial(n²,q_N) >= V_observed] + Q²/2^n).

Ini membahas null ideal pada setiap ronde. Ia tidak mengasumsikan keadaan
berbagai ronde dalam satu algoritma saling independen. Pemeriksaan tambahan
memakai Bonferroni minimum nilai-p sel; uji tambahan tersebut tidak bergantung
pada independensi antarsel, setelah koreksi pendekatan null yang sama.
Agregat ini adalah uji terhadap model acak ideal dengan statistik SAC; ia
bukan uji universal atas seluruh transformasi yang hanya memenuhi frekuensi
marginal SAC tanpa asumsi distribusi gabungan yang sama.

## 2. Linear satu bit

Untuk sampel berukuran N, jumlah kesesuaian tanda bit masukan dan keluaran
mempunyai null Binomial(N,1/2) pada label keluaran acak independen, bersyarat
pada masukan yang berbeda. Setiap pasangan bit diuji dengan nilai-p eksak dua
sisi; minimum nilai-p dikalikan n² lalu ditambah batas kopling yang konservatif.
Bonferroni tidak memerlukan independensi antarpasangan. Kolom lin_noise_level
lama tetap merupakan garis referensi aproksimasi normal; keputusan terkoreksi
memakai lin_bonferroni_p, bukan garis tersebut.

## 3. Zero-sum

Pada koset-koset berbeda, setiap bit XOR keluaran di model label acak adalah
bit seragam. Peluang suatu posisi seimbang pada K koset adalah q=2^-K,
sehingga jumlah posisi seimbang M ~ Binomial(n,q) pada model ideal tersebut.
Adapter memilih koset dengan mengacak bit di luar himpunan aktif berukuran k.
Peluang duplikasi koset dibatasi C(K,2)/2^(n-k); jumlah query Q=K*2^k.
Peluang collision label keluaran dibatasi C(Q,2)/2^n. Tambahkan kedua batas ini
pada ekor binomial, lalu batasi nilai maksimum 1.

Analisis konservatif alternatif memakai batas Markov:
P[M >= m] <= n*2^-K/m, untuk m>0, ditambah batas kopling di atas.
Ini merupakan pemeriksaan sensitivitas yang tidak memerlukan independensi
antarindikator posisi bit.

## 4. Diferensial: kejadian maksimum

Aturan tetap TopCount>=3. Untuk satu dx, pasangan-pasangan masukan tak berurut
{X,X xor dx} berbeda adalah disjoint. Pada permutasi ideal, setelah pasangan
keluaran pertama menentukan dy, peluang pasangan kedua mempunyai dy sama
dibatasi 1/(2^n-3), dan pasangan ketiga 1/(2^n-5).

Untuk N pasangan dan D pola dx yang ditetapkan sebelum pengukuran:

p_bound <= D * [C(N,3)/((2^n-3)(2^n-5)) + C(N,2)*2/2^n].

Suku kedua mencakup pengambilan ulang pasangan masukan tak berurut. Union
bound mencakup semua tiga pasangan dan semua D=3 pola. Kejadian maksimum atas
semua dy sudah tercakup karena dy pertama tidak ditentukan lebih dahulu.
Deteksi memerlukan TopCount>=3 dan p_bound<alpha. Ini masih bukan pencarian
seluruh dx, bukan estimasi probabilitas trail terbaik, dan bukan serangan.

## 5. Multiplicity, seed, dan horizon

Aturan utama memakai alpha=0,001 per metrik per ronde. Lima keluarga metrik
adalah SAC, linear, diferensial, ZS4, ZS8. Audit experimentwise membagi alpha
dengan lima kali jumlah ronde sembilan konfigurasi pada satu run. Union bound
tidak memerlukan independensi antar-ronde/varian. Ia tidak mencakup semua run,
semua kunci, atau pemilihan hipotesis berdasarkan hasil setelah eksperimen.

Horizon individual adalah panjang deret deteksi bersambung dari ronde pertama.
Deteksi setelah jeda tetap dilaporkan sebagai deteksi setelah jeda; status itu
bukan bukti positif palsu. Rentang dari lima seed merupakan rentang observasi,
bukan interval kepercayaan atas horizon atau seluruh ruang kunci.

## 6. Whitening dan entropi

XOR keluaran yang tetap untuk satu kunci mempertahankan beda XOR, avalanche
plaintext, besar korelasi linear, serta zero-sum himpunan genap. Pada sampel
tertentu, bobot Hamming dan entropi byte gabungan dapat berubah. Entropi tiap
posisi byte invariant terhadap XOR byte konstan dan permutasi posisi byte,
karena hanya mengganti label kategori. Sampel utama memperlihatkan hal ini.

Pada avalanche kunci, konstanta whitening berubah saat kunci berubah; karena
itu finalisasi harus ditangani terpisah. Audit menggunakan sampel/kunci acak
identik sebelum dan setelah finalisasi pada titik akhir, serta memeriksa
finalisasi terhadap enkripsi asli RECTANGLE/CLEFIA.

Entropi byte gabungan dari 2048 keadaan memakai 2048*n/8 byte. Ini memberi
jumlah observasi lebih besar untuk keadaan yang lebih besar. Rata-rata entropi
per posisi byte selalu memakai 2048 observasi per posisi pada konfigurasi
utama dan disediakan sebagai pembanding. Permutasi identitas pun mempertahankan
keseragaman masukan: statistik keluaran tunggal tidak mengukur kekuatan difusi.
