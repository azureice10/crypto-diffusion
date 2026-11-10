# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette

Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.

Parameter: `{"primitif": ["rectangle", "clefia", "sparkle256", "sparkle256s", "sparkle384", "sparkle384s", "sparkle512", "sparkle512s", "alzette"], "sampel_avalanche": 64, "sampel_linear": 2048, "pasangan_diff": 1024, "koset": 16, "kunci": 8, "sampel_kunci_avalanche": 32, "seed": 2026, "cepat": false, "perbarui_kecepatan": false}`

## 1. Profil primitif

| Primitif | Struktur | Bit | Ronde (R) | Satuan | Catatan |
|---|---|---|---|---|---|
| RECTANGLE-80 | SPN (bitslice) | 64 | 25 | ronde | kunci 00010203040506070809; S-box 4-bit per kolom |
| CLEFIA-128 | GFN 4-cabang | 128 | 18 | ronde asli CLEFIA | kunci uji resmi ffeedd..00; S-box 8-bit S0/S1 |
| Sparkle256 | ARX-SPN (permutasi) | 256 | 10 | step | permutasi Sparkle big (10 step), tanpa kunci |
| Sparkle256-slim | ARX-SPN (permutasi) | 256 | 7 | step | permutasi Sparkle slim (7 step), tanpa kunci; step-nya sama persis dengan awal varian big |
| Sparkle384 | ARX-SPN (permutasi) | 384 | 11 | step | permutasi Sparkle big (11 step), tanpa kunci |
| Sparkle384-slim | ARX-SPN (permutasi) | 384 | 7 | step | permutasi Sparkle slim (7 step), tanpa kunci; step-nya sama persis dengan awal varian big |
| Sparkle512 | ARX-SPN (permutasi) | 512 | 12 | step | permutasi Sparkle big (12 step), tanpa kunci |
| Sparkle512-slim | ARX-SPN (permutasi) | 512 | 8 | step | permutasi Sparkle slim (8 step), tanpa kunci; step-nya sama persis dengan awal varian big |
| Alzette | ARX-box | 64 | 4 | ronde ARX | Alzette dengan konstanta tetap c=b7e15162, tanpa kunci tambahan |

## 2. Unit nonlinear (S-box)

| S-box | Bit | Bijektif | Uniformitas diff. | log2 DP maks | Linearitas | Nonlinearitas | log2 korelasi maks | Derajat aljabar | Titik tetap |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE S | 4 | True | 4 | -2.000 | 8 | 4 | -1.000 | 3 | 0 |
| CLEFIA S0 | 8 | True | 10 | -4.678 | 56 | 100 | -2.193 | 6 | 0 |
| CLEFIA S1 | 8 | True | 4 | -6.000 | 32 | 112 | -3.000 | 7 | 0 |
| Alzette (ARX, bukan tabel) | 64 | True | - | - | - | - | - | - | - |

## 3. Horizon distinguisher (ronde terakhir sifat masih terdeteksi)

Horizon gabungan = maksimum dari semua horizon. Margin = R − horizon gabungan. Pecahan (`/R`) membuat primitif dengan definisi ronde berbeda bisa dibandingkan.

| Primitif | Difusi lengkap | SAC | Linear | Diferensial | Zero-sum 4 bit | Zero-sum 8 bit | Gabungan | Gabungan/R | Margin | Margin/R |
|---|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 5 | 6 | 2 | 3 | 6 | 6 | 6 | 0.240 | 19 | 0.760 |
| CLEFIA-128 | 5 | 4 | 1 | 2 | 4 | 5 | 5 | 0.278 | 13 | 0.722 |
| Sparkle256 | 3 | 2 | - | - | 1 | 1 | 2 | 0.200 | 8 | 0.800 |
| Sparkle256-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.286 | 5 | 0.714 |
| Sparkle384 | 3 | 2 | - | - | 1 | 1 | 2 | 0.182 | 9 | 0.818 |
| Sparkle384-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.286 | 5 | 0.714 |
| Sparkle512 | 3 | 2 | - | - | 1 | 1 | 2 | 0.167 | 10 | 0.833 |
| Sparkle512-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.250 | 6 | 0.750 |
| Alzette | 4 | 4 | - | 3 | 3 | 2 | 4 | 1.000 | 0 | 0.000 |

Horizon adalah akhir deretan deteksi yang bersambung dari ronde 1. Deteksi setelah jeda tidak menaikkan horizon menurut definisi operasional ini; deteksi itu bukan otomatis positif palsu dan dicatat di kolom `deteksi_terisolasi` pada `horizon.csv`. Ini horizon eksperimen, bukan batas serangan atau klaim keamanan. Angka serangan literatur harus dibaca terpisah karena model, data, kompleksitas, dan jenis serangannya berbeda.

Varian slim Sparkle memakai pengukuran varian big-nya, karena step-nya sama persis. Selisih margin big dan slim karena itu murni datang dari jumlah step.

## 4. Kurva per ronde

### RECTANGLE-80

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.040 | 0.042 | 0.062 | 0.961 | 0.293 | 32 | 257 | -1.994 | 64 | 64 |
| 2 | 0.080 | 0.113 | 0.250 | 0.855 | 0.115 | 1 | 59 | -4.117 | 64 | 64 |
| 3 | 0.120 | 0.196 | 0.562 | 0.669 | 0.083 | 0 | 9 | -6.830 | 64 | 64 |
| 4 | 0.160 | 0.314 | 0.998 | 0.455 | 0.077 | 0 | 2 | - | 57 | 63 |
| 5 | 0.200 | 0.424 | 1.000 | 0.104 | 0.091 | 0 | 1 | - | 33 | 52 |
| 6 | 0.240 | 0.478 | 1.000 | 0.003 | 0.085 | 0 | 1 | - | 2 | 9 |
| 7 | 0.280 | 0.498 | 1.000 | 0.001 | 0.090 | 0 | 1 | - | 0 | 0 |
| 8 | 0.320 | 0.501 | 1.000 | 0.000 | 0.093 | 0 | 1 | - | 0 | 0 |
| 9 | 0.360 | 0.500 | 1.000 | 0.000 | 0.084 | 0 | 1 | - | 0 | 0 |
| 10 | 0.400 | 0.502 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 11 | 0.440 | 0.500 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 12 | 0.480 | 0.500 | 1.000 | 0.001 | 0.089 | 0 | 1 | - | 0 | 0 |
| 13 | 0.520 | 0.500 | 1.000 | 0.001 | 0.077 | 0 | 1 | - | 0 | 0 |
| 14 | 0.560 | 0.501 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |
| 15 | 0.600 | 0.497 | 1.000 | 0.001 | 0.087 | 0 | 1 | - | 0 | 0 |
| 16 | 0.640 | 0.498 | 1.000 | 0.000 | 0.089 | 0 | 1 | - | 0 | 0 |
| 17 | 0.680 | 0.501 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |
| 18 | 0.720 | 0.500 | 1.000 | 0.001 | 0.076 | 0 | 1 | - | 0 | 0 |
| 19 | 0.760 | 0.500 | 1.000 | 0.001 | 0.079 | 0 | 1 | - | 0 | 0 |
| 20 | 0.800 | 0.500 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 21 | 0.840 | 0.499 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |
| 22 | 0.880 | 0.501 | 1.000 | 0.000 | 0.077 | 0 | 1 | - | 0 | 0 |
| 23 | 0.920 | 0.499 | 1.000 | 0.000 | 0.081 | 0 | 1 | - | 0 | 0 |
| 24 | 0.960 | 0.500 | 1.000 | 0.000 | 0.083 | 0 | 1 | - | 0 | 0 |
| 25 | 1.000 | 0.501 | 1.000 | 0.000 | 0.082 | 0 | 1 | - | 0 | 0 |

### CLEFIA-128

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.056 | 0.071 | 0.133 | 0.876 | 1.000 | 64 | 1024 | 0.000 | 128 | 128 |
| 2 | 0.111 | 0.197 | 0.383 | 0.626 | 0.100 | 0 | 32 | -5.000 | 128 | 128 |
| 3 | 0.167 | 0.321 | 0.633 | 0.376 | 0.084 | 0 | 1 | - | 96 | 128 |
| 4 | 0.222 | 0.442 | 0.879 | 0.125 | 0.081 | 0 | 1 | - | 32 | 96 |
| 5 | 0.278 | 0.500 | 1.000 | 0.000 | 0.083 | 0 | 1 | - | 0 | 32 |
| 6 | 0.333 | 0.499 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 7 | 0.389 | 0.500 | 1.000 | 0.001 | 0.087 | 0 | 1 | - | 0 | 0 |
| 8 | 0.444 | 0.500 | 1.000 | 0.001 | 0.085 | 0 | 1 | - | 0 | 0 |
| 9 | 0.500 | 0.500 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 10 | 0.556 | 0.499 | 1.000 | 0.000 | 0.091 | 0 | 1 | - | 0 | 0 |
| 11 | 0.611 | 0.500 | 1.000 | 0.000 | 0.092 | 0 | 1 | - | 0 | 0 |
| 12 | 0.667 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 13 | 0.722 | 0.500 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |
| 14 | 0.778 | 0.500 | 1.000 | 0.000 | 0.085 | 0 | 1 | - | 0 | 0 |
| 15 | 0.833 | 0.500 | 1.000 | 0.000 | 0.092 | 0 | 1 | - | 0 | 0 |
| 16 | 0.889 | 0.501 | 1.000 | 0.000 | 0.092 | 0 | 1 | - | 0 | 0 |
| 17 | 0.944 | 0.500 | 1.000 | 0.001 | 0.087 | 0 | 1 | - | 0 | 0 |
| 18 | 1.000 | 0.500 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |

### Sparkle256

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.230 | 0.499 | 0.599 | 0.104 | 0 | 1 | - | 75 | 64 |
| 2 | 0.200 | 0.438 | 0.875 | 0.126 | 0.093 | 0 | 1 | - | 0 | 0 |
| 3 | 0.300 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |
| 4 | 0.400 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 5 | 0.500 | 0.500 | 1.000 | 0.000 | 0.096 | 0 | 1 | - | 0 | 0 |
| 6 | 0.600 | 0.500 | 1.000 | 0.000 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 0.700 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 8 | 0.800 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 9 | 0.900 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 10 | 1.000 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |

### Sparkle256-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.230 | 0.499 | 0.599 | 0.104 | 0 | 1 | - | 75 | 64 |
| 2 | 0.286 | 0.438 | 0.875 | 0.126 | 0.093 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.000 | 0.096 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.000 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |

### Sparkle384

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.091 | 0.194 | 0.416 | 0.658 | 0.100 | 0 | 1 | - | 132 | 129 |
| 2 | 0.182 | 0.417 | 0.833 | 0.167 | 0.106 | 0 | 1 | - | 0 | 0 |
| 3 | 0.273 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 4 | 0.364 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 5 | 0.455 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 6 | 0.545 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 0.636 | 0.500 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |
| 8 | 0.727 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 9 | 0.818 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |
| 10 | 0.909 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 11 | 1.000 | 0.500 | 1.000 | 0.001 | 0.106 | 0 | 1 | - | 0 | 0 |

### Sparkle384-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.194 | 0.416 | 0.658 | 0.100 | 0 | 1 | - | 132 | 129 |
| 2 | 0.286 | 0.417 | 0.833 | 0.167 | 0.106 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |

### Sparkle512

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.083 | 0.175 | 0.375 | 0.688 | 0.104 | 0 | 1 | - | 201 | 192 |
| 2 | 0.167 | 0.406 | 0.812 | 0.188 | 0.103 | 0 | 1 | - | 0 | 0 |
| 3 | 0.250 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 4 | 0.333 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 5 | 0.417 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 6 | 0.500 | 0.500 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |
| 7 | 0.583 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 8 | 0.667 | 0.500 | 1.000 | 0.001 | 0.109 | 0 | 1 | - | 0 | 0 |
| 9 | 0.750 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |
| 10 | 0.833 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |
| 11 | 0.917 | 0.500 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |
| 12 | 1.000 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |

### Sparkle512-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.175 | 0.375 | 0.688 | 0.104 | 0 | 1 | - | 201 | 192 |
| 2 | 0.250 | 0.406 | 0.812 | 0.188 | 0.103 | 0 | 1 | - | 0 | 0 |
| 3 | 0.375 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 4 | 0.500 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 5 | 0.625 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 6 | 0.750 | 0.500 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |
| 7 | 0.875 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 8 | 1.000 | 0.500 | 1.000 | 0.001 | 0.109 | 0 | 1 | - | 0 | 0 |

### Alzette

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.250 | 0.068 | 0.209 | 0.965 | 0.081 | 0 | 521 | -0.975 | 54 | 52 |
| 2 | 0.500 | 0.194 | 0.646 | 0.844 | 0.080 | 0 | 131 | -2.967 | 37 | 32 |
| 3 | 0.750 | 0.390 | 0.985 | 0.527 | 0.089 | 0 | 4 | -8.000 | 6 | 0 |
| 4 | 1.000 | 0.468 | 1.000 | 0.178 | 0.091 | 0 | 1 | - | 0 | 0 |

## 5. Keacakan pada ronde penuh dan kecepatan

| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 3.01 (4.32) | 0.091 (0.111) | 7.988/8.000 | 31.92 (32) | 3.98 (4.00) | 2090 | 83.6 | 0.031 |
| CLEFIA-128 | 2.87 (4.47) | 0.086 (0.117) | 7.994/8.000 | 64.04 (64) | 5.53 (5.66) | 850 | 47.2 | 0.151 |
| Sparkle256 | 2.87 (4.62) | 0.100 (0.122) | 7.997/8.000 | 128.25 (128) | 7.86 (8.00) | 616 | 61.6 | 0.415 |
| Sparkle256-slim | 3.31 (4.62) | 0.095 (0.122) | 7.997/8.000 | 128.23 (128) | 7.97 (8.00) | 438 | 62.5 | 0.585 |
| Sparkle384 | 3.93 (4.70) | 0.098 (0.125) | 7.998/8.000 | 192.19 (192) | 9.54 (9.80) | 851 | 77.4 | 0.451 |
| Sparkle384-slim | 3.14 (4.70) | 0.101 (0.125) | 7.998/8.000 | 191.87 (192) | 9.85 (9.80) | 625 | 89.3 | 0.614 |
| Sparkle512 | 3.01 (4.76) | 0.106 (0.128) | 7.999/8.000 | 255.67 (256) | 11.54 (11.31) | 1379 | 114.9 | 0.371 |
| Sparkle512-slim | 2.87 (4.76) | 0.103 (0.128) | 7.999/8.000 | 255.73 (256) | 11.46 (11.31) | 915 | 114.4 | 0.559 |
| Alzette | 1.55 (4.32) | 0.090 (0.111) | 7.989/8.000 | 32.07 (32) | 4.00 (4.00) | 12 | 3.0 | 5.258 |

## 6. Kombinasi antar-pasangan

Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.

| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |
|---|---|---|---|---|---|---|
| RECTANGLE-80 vs CLEFIA-128 | 0.240 vs 0.278 | 0.038 | 0.200 vs 0.278 | 0.955 | 0.0682 | 0.203 |
| RECTANGLE-80 vs Sparkle256 | 0.240 vs 0.200 | -0.040 | 0.200 vs 0.300 | 0.940 | 0.0888 | 0.074 |
| RECTANGLE-80 vs Sparkle256-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.927 | 0.1044 | 0.052 |
| RECTANGLE-80 vs Sparkle384 | 0.240 vs 0.182 | -0.058 | 0.200 vs 0.273 | 0.945 | 0.0849 | 0.068 |
| RECTANGLE-80 vs Sparkle384-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.925 | 0.1098 | 0.050 |
| RECTANGLE-80 vs Sparkle512 | 0.240 vs 0.167 | -0.073 | 0.200 vs 0.250 | 0.944 | 0.0850 | 0.082 |
| RECTANGLE-80 vs Sparkle512-slim | 0.240 vs 0.250 | 0.010 | 0.200 vs 0.375 | 0.940 | 0.0984 | 0.055 |
| RECTANGLE-80 vs Alzette | 0.240 vs 1.000 | 0.760 | 0.200 vs 1.000 | 0.638 | 0.3375 | 0.006 |
| CLEFIA-128 vs Sparkle256 | 0.278 vs 0.200 | -0.078 | 0.278 vs 0.300 | 0.933 | 0.0970 | 0.363 |
| CLEFIA-128 vs Sparkle256-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.955 | 0.0858 | 0.257 |
| CLEFIA-128 vs Sparkle384 | 0.278 vs 0.182 | -0.096 | 0.278 vs 0.273 | 0.932 | 0.0962 | 0.334 |
| CLEFIA-128 vs Sparkle384-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.956 | 0.0914 | 0.245 |
| CLEFIA-128 vs Sparkle512 | 0.278 vs 0.167 | -0.111 | 0.278 vs 0.250 | 0.924 | 0.1033 | 0.406 |
| CLEFIA-128 vs Sparkle512-slim | 0.278 vs 0.250 | -0.028 | 0.278 vs 0.375 | 0.959 | 0.0847 | 0.269 |
| CLEFIA-128 vs Alzette | 0.278 vs 1.000 | 0.722 | 0.278 vs 1.000 | 0.705 | 0.3115 | 0.029 |
| Sparkle256 vs Sparkle256-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.968 | 0.0614 | 0.710 |
| Sparkle256 vs Sparkle384 | 0.200 vs 0.182 | -0.018 | 0.300 vs 0.273 | 0.999 | 0.0078 | 0.921 |
| Sparkle256 vs Sparkle384-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.956 | 0.0768 | 0.676 |
| Sparkle256 vs Sparkle512 | 0.200 vs 0.167 | -0.033 | 0.300 vs 0.250 | 0.997 | 0.0146 | 1.118 |
| Sparkle256 vs Sparkle512-slim | 0.200 vs 0.250 | 0.050 | 0.300 vs 0.375 | 0.974 | 0.0602 | 0.742 |
| Sparkle256 vs Alzette | 0.200 vs 1.000 | 0.800 | 0.300 vs 1.000 | 0.630 | 0.3509 | 0.079 |
| Sparkle256-slim vs Sparkle384 | 0.286 vs 0.182 | -0.104 | 0.429 vs 0.273 | 0.966 | 0.0610 | 1.297 |
| Sparkle256-slim vs Sparkle384-slim | 0.286 vs 0.286 | 0.000 | 0.429 vs 0.429 | 0.998 | 0.0159 | 0.952 |
| Sparkle256-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.958 | 0.0682 | 1.576 |
| Sparkle256-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.998 | 0.0155 | 1.046 |
| Sparkle256-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.733 | 0.3129 | 0.111 |
| Sparkle384 vs Sparkle384-slim | 0.182 vs 0.286 | 0.104 | 0.273 vs 0.429 | 0.955 | 0.0764 | 0.734 |
| Sparkle384 vs Sparkle512 | 0.182 vs 0.167 | -0.015 | 0.273 vs 0.250 | 0.999 | 0.0094 | 1.215 |
| Sparkle384 vs Sparkle512-slim | 0.182 vs 0.250 | 0.068 | 0.273 vs 0.375 | 0.973 | 0.0594 | 0.806 |
| Sparkle384 vs Alzette | 0.182 vs 1.000 | 0.818 | 0.273 vs 1.000 | 0.627 | 0.3510 | 0.086 |
| Sparkle384-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.945 | 0.0836 | 1.654 |
| Sparkle384-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.997 | 0.0207 | 1.098 |
| Sparkle384-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.749 | 0.3036 | 0.117 |
| Sparkle512 vs Sparkle512-slim | 0.167 vs 0.250 | 0.083 | 0.250 vs 0.375 | 0.965 | 0.0667 | 0.664 |
| Sparkle512 vs Alzette | 0.167 vs 1.000 | 0.833 | 0.250 vs 1.000 | 0.613 | 0.3554 | 0.071 |
| Sparkle512-slim vs Alzette | 0.250 vs 1.000 | 0.750 | 0.375 vs 1.000 | 0.719 | 0.3165 | 0.106 |

### Kemiripan per kurva (Pearson)

**Avalanche rata-rata** (`avalanche_mean`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.999 | 0.992 | 0.976 | 0.994 | 0.963 | 0.990 | 0.980 | 0.611 |
| CLEFIA-128 | 0.999 | 1.000 | 0.993 | 0.983 | 0.995 | 0.972 | 0.990 | 0.986 | 0.625 |
| Sparkle256 | 0.992 | 0.993 | 1.000 | 0.971 | 1.000 | 0.954 | 0.998 | 0.970 | 0.599 |
| Sparkle256-slim | 0.976 | 0.983 | 0.971 | 1.000 | 0.970 | 0.998 | 0.959 | 0.999 | 0.713 |
| Sparkle384 | 0.994 | 0.995 | 1.000 | 0.970 | 1.000 | 0.953 | 0.999 | 0.970 | 0.595 |
| Sparkle384-slim | 0.963 | 0.972 | 0.954 | 0.998 | 0.953 | 1.000 | 0.940 | 0.997 | 0.736 |
| Sparkle512 | 0.990 | 0.990 | 0.998 | 0.959 | 0.999 | 0.940 | 1.000 | 0.960 | 0.577 |
| Sparkle512-slim | 0.980 | 0.986 | 0.970 | 0.999 | 0.970 | 0.997 | 0.960 | 1.000 | 0.699 |
| Alzette | 0.611 | 0.625 | 0.599 | 0.713 | 0.595 | 0.736 | 0.577 | 0.699 | 1.000 |

**Kelengkapan difusi** (`completeness`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.962 | 0.977 | 0.926 | 0.979 | 0.900 | 0.985 | 0.920 | 0.616 |
| CLEFIA-128 | 0.962 | 1.000 | 0.989 | 0.986 | 0.992 | 0.975 | 0.988 | 0.988 | 0.723 |
| Sparkle256 | 0.977 | 0.989 | 1.000 | 0.973 | 0.999 | 0.955 | 0.998 | 0.969 | 0.688 |
| Sparkle256-slim | 0.926 | 0.986 | 0.973 | 1.000 | 0.974 | 0.997 | 0.965 | 0.998 | 0.805 |
| Sparkle384 | 0.979 | 0.992 | 0.999 | 0.974 | 1.000 | 0.956 | 0.999 | 0.971 | 0.687 |
| Sparkle384-slim | 0.900 | 0.975 | 0.955 | 0.997 | 0.956 | 1.000 | 0.944 | 0.997 | 0.831 |
| Sparkle512 | 0.985 | 0.988 | 0.998 | 0.965 | 0.999 | 0.944 | 1.000 | 0.962 | 0.668 |
| Sparkle512-slim | 0.920 | 0.988 | 0.969 | 0.998 | 0.971 | 0.997 | 0.962 | 1.000 | 0.796 |
| Alzette | 0.616 | 0.723 | 0.688 | 0.805 | 0.687 | 0.831 | 0.668 | 0.796 | 1.000 |

**Pelanggaran SAC** (`sac_violation_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.994 | 0.991 | 0.963 | 0.990 | 0.951 | 0.986 | 0.972 | 0.487 |
| CLEFIA-128 | 0.994 | 1.000 | 0.995 | 0.981 | 0.995 | 0.970 | 0.990 | 0.986 | 0.510 |
| Sparkle256 | 0.991 | 0.995 | 1.000 | 0.967 | 1.000 | 0.952 | 0.997 | 0.971 | 0.489 |
| Sparkle256-slim | 0.963 | 0.981 | 0.967 | 1.000 | 0.964 | 0.999 | 0.952 | 0.999 | 0.595 |
| Sparkle384 | 0.990 | 0.995 | 1.000 | 0.964 | 1.000 | 0.949 | 0.999 | 0.969 | 0.484 |
| Sparkle384-slim | 0.951 | 0.970 | 0.952 | 0.999 | 0.949 | 1.000 | 0.935 | 0.996 | 0.614 |
| Sparkle512 | 0.986 | 0.990 | 0.997 | 0.952 | 0.999 | 0.935 | 1.000 | 0.958 | 0.467 |
| Sparkle512-slim | 0.972 | 0.986 | 0.971 | 0.999 | 0.969 | 0.996 | 0.958 | 1.000 | 0.577 |
| Alzette | 0.487 | 0.510 | 0.489 | 0.595 | 0.484 | 0.614 | 0.467 | 0.577 | 1.000 |

**Korelasi linear signifikan** (`lin_sig_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.986 | 0.994 | 0.946 | 0.998 | 0.946 | 1.000 | 0.970 | 0.813 |
| CLEFIA-128 | 0.986 | 1.000 | 0.995 | 0.984 | 0.993 | 0.984 | 0.988 | 0.996 | 0.873 |
| Sparkle256 | 0.994 | 0.995 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.833 |
| Sparkle256-slim | 0.946 | 0.984 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle384 | 0.998 | 0.993 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.825 |
| Sparkle384-slim | 0.946 | 0.984 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle512 | 1.000 | 0.988 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.815 |
| Sparkle512-slim | 0.970 | 0.996 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.904 |
| Alzette | 0.813 | 0.873 | 0.833 | 0.926 | 0.825 | 0.926 | 0.815 | 0.904 | 1.000 |

**Frekuensi dy teratas** (`diff_top_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.813 | 0.962 | 0.903 | 0.973 | 0.903 | 0.982 | 0.930 | 0.576 |
| CLEFIA-128 | 0.813 | 1.000 | 0.931 | 0.972 | 0.917 | 0.972 | 0.900 | 0.967 | 0.712 |
| Sparkle256 | 0.962 | 0.931 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.632 |
| Sparkle256-slim | 0.903 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.727 |
| Sparkle384 | 0.973 | 0.917 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.625 |
| Sparkle384-slim | 0.903 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.727 |
| Sparkle512 | 0.982 | 0.900 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.615 |
| Sparkle512-slim | 0.930 | 0.967 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.703 |
| Alzette | 0.576 | 0.712 | 0.632 | 0.727 | 0.625 | 0.727 | 0.615 | 0.703 | 1.000 |

**Bit zero-sum (8 bit aktif)** (`zs8_balanced_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.977 | 0.724 | 0.848 | 0.735 | 0.886 | 0.719 | 0.867 | 0.725 |
| CLEFIA-128 | 0.977 | 1.000 | 0.693 | 0.824 | 0.704 | 0.863 | 0.688 | 0.832 | 0.784 |
| Sparkle256 | 0.724 | 0.693 | 1.000 | 0.974 | 0.999 | 0.956 | 0.998 | 0.968 | 0.537 |
| Sparkle256-slim | 0.848 | 0.824 | 0.974 | 1.000 | 0.980 | 0.997 | 0.976 | 0.997 | 0.634 |
| Sparkle384 | 0.735 | 0.704 | 0.999 | 0.980 | 1.000 | 0.963 | 0.999 | 0.974 | 0.545 |
| Sparkle384-slim | 0.886 | 0.863 | 0.956 | 0.997 | 0.963 | 1.000 | 0.957 | 0.997 | 0.662 |
| Sparkle512 | 0.719 | 0.688 | 0.998 | 0.976 | 0.999 | 0.957 | 1.000 | 0.968 | 0.535 |
| Sparkle512-slim | 0.867 | 0.832 | 0.968 | 0.997 | 0.974 | 0.997 | 0.968 | 1.000 | 0.632 |
| Alzette | 0.725 | 0.784 | 0.537 | 0.634 | 0.545 | 0.662 | 0.535 | 0.632 | 1.000 |

## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)

| | r_norm | avalanche_mean | completeness | sac_violation_frac | lin_sig_frac | lin_max_abs_corr | diff_top_frac | zs8_balanced_frac |
|---|---|---|---|---|---|---|---|---|
| r_norm | 1.000 | 0.580 | 0.664 | -0.527 | -0.293 | -0.066 | -0.343 | -0.635 |
| avalanche_mean | 0.580 | 1.000 | 0.728 | -0.594 | -0.289 | -0.058 | -0.464 | -0.606 |
| completeness | 0.664 | 0.728 | 1.000 | -0.726 | -0.397 | -0.125 | -0.607 | -0.763 |
| sac_violation_frac | -0.527 | -0.594 | -0.726 | 1.000 | 0.287 | 0.159 | 0.472 | 0.598 |
| lin_sig_frac | -0.293 | -0.289 | -0.397 | 0.287 | 1.000 | 0.293 | 0.583 | 0.418 |
| lin_max_abs_corr | -0.066 | -0.058 | -0.125 | 0.159 | 0.293 | 1.000 | -0.039 | -0.040 |
| diff_top_frac | -0.343 | -0.464 | -0.607 | 0.472 | 0.583 | -0.039 | 1.000 | 0.625 |
| zs8_balanced_frac | -0.635 | -0.606 | -0.763 | 0.598 | 0.418 | -0.040 | 0.625 | 1.000 |

## 8. Perbandingan antar-kunci

Metrik yang sama diulang untuk kunci default, kunci semua 0, kunci semua 1, dan kunci acak. Metrik "stabil" jika horizonnya sama untuk semua kunci. Selisih satu ronde di tepi horizon biasanya efek sampel, bukan bukti ketergantungan pada kunci.

| Primitif | Metrik | Min | Maks | Kunci tanpa deteksi | Stabil | Nilai per kunci |
|---|---|---|---|---|---|---|
| RECTANGLE-80 | difusi_lengkap_ronde | 5 | 5 | 0 | ya | 5 5 5 5 5 5 5 5 |
| RECTANGLE-80 | sac_horizon | 5 | 6 | 0 | tidak | 5 6 5 6 6 5 5 5 |
| RECTANGLE-80 | linear_horizon | 1 | 1 | 0 | ya | 1 1 1 1 1 1 1 1 |
| RECTANGLE-80 | diferensial_horizon | 3 | 4 | 0 | tidak | 3 3 3 3 3 3 4 4 |
| RECTANGLE-80 | zero_sum4_horizon | 5 | 6 | 0 | tidak | 5 6 6 6 6 6 6 6 |
| RECTANGLE-80 | zero_sum8_horizon | 6 | 6 | 0 | ya | 6 6 6 6 6 6 6 6 |
| RECTANGLE-80 | distinguisher_horizon | 6 | 6 | 0 | ya | 6 6 6 6 6 6 6 6 |
| CLEFIA-128 | difusi_lengkap_ronde | 5 | 5 | 0 | ya | 5 5 5 5 5 5 5 5 |
| CLEFIA-128 | sac_horizon | 4 | 4 | 0 | ya | 4 4 4 4 4 4 4 4 |
| CLEFIA-128 | linear_horizon | 1 | 1 | 0 | ya | 1 1 1 1 1 1 1 1 |
| CLEFIA-128 | diferensial_horizon | 2 | 2 | 0 | ya | 2 2 2 2 2 2 2 2 |
| CLEFIA-128 | zero_sum4_horizon | 4 | 4 | 0 | ya | 4 4 4 4 4 4 4 4 |
| CLEFIA-128 | zero_sum8_horizon | 5 | 5 | 0 | ya | 5 5 5 5 5 5 5 5 |
| CLEFIA-128 | distinguisher_horizon | 5 | 5 | 0 | ya | 5 5 5 5 5 5 5 5 |

### Bit zero-sum antar-kunci

"Seimbang" di sini berarti jumlah XOR-nya nol di **setiap** koset yang diuji. Bit yang seimbang di semua kunci belum tentu sifat pasti, dan bit yang seimbang hanya di sebagian kunci belum tentu bergantung pada kunci: bit dengan laju nol tinggi tetapi di bawah 100% bisa lolos di satu kunci dan gagal di kunci lain hanya karena sampel. Karena itu lihat juga laju nol per koset (rata-rata semua kunci) dan kemiripan laju antar-kunci: mendekati 1 berarti semua kunci sepakat bit mana yang bias, jadi biasnya tidak bergantung pada kunci; mendekati 0 berarti noise.

Baris ditampilkan bila sebagian bit sudah hilang dan masih ada bit seimbang di semua kunci, atau bila bit di sebagian kunci terlalu banyak untuk disebut kebetulan (p < 0,001). Semua baris ada di `kunci_zero_sum.csv`.

| Primitif | Bit aktif | Ronde | Bit seimbang per kunci | Semua kunci | Sebagian kunci | Posisi di semua kunci | Laju nol tertinggi (bit=laju) | Kemiripan laju antar-kunci |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 4 bit | 4 | 56 56 58 57 58 56 56 57 | 56 | 3 | 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 … (+32) | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 0.817 |
| RECTANGLE-80 | 4 bit | 5 | 26 31 30 30 27 28 32 29 | 23 | 11 | 0 1 2 3 4 8 12 13 16 17 18 20 21 25 29 30 32 47 48 49 57 60 61 | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 0.833 |
| RECTANGLE-80 | 4 bit | 6 | 0 2 1 1 1 1 3 1 | 0 | 4 |  | 17=0.961 0=0.938 30=0.930 21=0.891 61=0.844 | 0.583 |
| RECTANGLE-80 | 8 bit | 4 | 63 63 64 63 64 63 63 63 | 63 | 1 | 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 … (+39) | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 1.000 |
| RECTANGLE-80 | 8 bit | 5 | 50 51 55 50 54 52 51 53 | 49 | 9 | 0 1 2 3 4 5 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 25 26 … (+25) | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 0.805 |
| RECTANGLE-80 | 8 bit | 6 | 5 4 11 6 10 10 8 7 | 3 | 14 | 0 1 5 | 0=1.000 1=1.000 5=1.000 18=0.984 22=0.977 | 0.670 |
| CLEFIA-128 | 4 bit | 3 | 96 96 96 96 96 96 96 96 | 96 | 0 | 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 … (+72) | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 0.920 |
| CLEFIA-128 | 4 bit | 4 | 32 32 32 32 32 32 32 32 | 32 | 0 | 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 … (+8) | 95=1.000 94=1.000 93=1.000 92=1.000 91=1.000 | 0.819 |
| CLEFIA-128 | 8 bit | 4 | 96 96 96 96 96 96 96 96 | 96 | 0 | 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 … (+72) | 0=1.000 1=1.000 2=1.000 3=1.000 4=1.000 | 0.927 |
| CLEFIA-128 | 8 bit | 5 | 32 32 32 32 32 32 32 32 | 32 | 0 | 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 … (+8) | 95=1.000 94=1.000 93=1.000 92=1.000 91=1.000 | 0.795 |

### Avalanche kunci

Satu bit kunci dibalik, dengan kunci dan plaintext acak di tiap sampel. Avalanche ideal = ronde pertama rata-ratanya dalam 0,01 dari 0,5.

| Primitif | Bit kunci | R | Kelengkapan penuh | Avalanche ideal | Horizon SAC kunci |
|---|---|---|---|---|---|
| RECTANGLE-80 | 80 | 25 | 6 | 6 | 6 |
| CLEFIA-128 | 128 | 18 | 2 | 2 | 1 |

## Catatan cara membaca

- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan juga kolom `/R`.
- "Tidak terdeteksi" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap tidak membuktikan tidak adanya distinguisher.
- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.
- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.
