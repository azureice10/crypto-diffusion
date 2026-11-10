# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette

Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.

Parameter: `{"primitif": ["rectangle", "clefia", "sparkle256", "sparkle256s", "sparkle384", "sparkle384s", "sparkle512", "sparkle512s", "alzette"], "sampel_avalanche": 256, "sampel_linear": 8192, "pasangan_diff": 4096, "koset": 32, "kunci": 0, "sampel_kunci_avalanche": 32, "seed": 2026, "cepat": false, "perbarui_kecepatan": false}`

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
| RECTANGLE-80 | 4 | 6 | 2 | 4 | 5 | 6 | 6 | 0.240 | 19 | 0.760 |
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
| 1 | 0.040 | 0.042 | 0.062 | 0.965 | 0.277 | 32 | 1041 | -1.976 | 64 | 64 |
| 2 | 0.080 | 0.113 | 0.250 | 0.923 | 0.091 | 9 | 280 | -3.871 | 64 | 64 |
| 3 | 0.120 | 0.197 | 0.562 | 0.801 | 0.040 | 0 | 21 | -7.608 | 64 | 64 |
| 4 | 0.160 | 0.315 | 1.000 | 0.619 | 0.047 | 0 | 7 | -9.193 | 56 | 63 |
| 5 | 0.200 | 0.424 | 1.000 | 0.336 | 0.040 | 0 | 2 | - | 28 | 50 |
| 6 | 0.240 | 0.479 | 1.000 | 0.023 | 0.047 | 0 | 1 | - | 0 | 4 |
| 7 | 0.280 | 0.496 | 1.000 | 0.002 | 0.038 | 0 | 1 | - | 0 | 0 |
| 8 | 0.320 | 0.500 | 1.000 | 0.000 | 0.041 | 0 | 1 | - | 0 | 0 |
| 9 | 0.360 | 0.500 | 1.000 | 0.001 | 0.039 | 0 | 1 | - | 0 | 0 |
| 10 | 0.400 | 0.501 | 1.000 | 0.001 | 0.047 | 0 | 1 | - | 0 | 0 |
| 11 | 0.440 | 0.500 | 1.000 | 0.000 | 0.042 | 0 | 1 | - | 0 | 0 |
| 12 | 0.480 | 0.500 | 1.000 | 0.001 | 0.043 | 0 | 1 | - | 0 | 0 |
| 13 | 0.520 | 0.500 | 1.000 | 0.001 | 0.048 | 0 | 1 | - | 0 | 0 |
| 14 | 0.560 | 0.500 | 1.000 | 0.001 | 0.035 | 0 | 1 | - | 0 | 0 |
| 15 | 0.600 | 0.498 | 1.000 | 0.001 | 0.047 | 0 | 1 | - | 0 | 0 |
| 16 | 0.640 | 0.499 | 1.000 | 0.001 | 0.039 | 0 | 1 | - | 0 | 0 |
| 17 | 0.680 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 18 | 0.720 | 0.499 | 1.000 | 0.001 | 0.037 | 0 | 1 | - | 0 | 0 |
| 19 | 0.760 | 0.500 | 1.000 | 0.000 | 0.043 | 0 | 1 | - | 0 | 0 |
| 20 | 0.800 | 0.499 | 1.000 | 0.001 | 0.043 | 0 | 1 | - | 0 | 0 |
| 21 | 0.840 | 0.501 | 1.000 | 0.001 | 0.041 | 0 | 1 | - | 0 | 0 |
| 22 | 0.880 | 0.500 | 1.000 | 0.001 | 0.042 | 0 | 1 | - | 0 | 0 |
| 23 | 0.920 | 0.500 | 1.000 | 0.000 | 0.042 | 0 | 1 | - | 0 | 0 |
| 24 | 0.960 | 0.500 | 1.000 | 0.001 | 0.040 | 0 | 1 | - | 0 | 0 |
| 25 | 1.000 | 0.500 | 1.000 | 0.000 | 0.039 | 0 | 1 | - | 0 | 0 |

### CLEFIA-128

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.056 | 0.071 | 0.133 | 0.882 | 1.000 | 64 | 4096 | 0.000 | 128 | 128 |
| 2 | 0.111 | 0.197 | 0.383 | 0.639 | 0.043 | 0 | 131 | -4.967 | 128 | 128 |
| 3 | 0.167 | 0.321 | 0.633 | 0.383 | 0.050 | 0 | 1 | - | 96 | 128 |
| 4 | 0.222 | 0.442 | 0.879 | 0.126 | 0.050 | 0 | 1 | - | 32 | 96 |
| 5 | 0.278 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 32 |
| 6 | 0.333 | 0.500 | 1.000 | 0.001 | 0.043 | 0 | 1 | - | 0 | 0 |
| 7 | 0.389 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 8 | 0.444 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 9 | 0.500 | 0.500 | 1.000 | 0.001 | 0.047 | 0 | 1 | - | 0 | 0 |
| 10 | 0.556 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 11 | 0.611 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 12 | 0.667 | 0.500 | 1.000 | 0.001 | 0.044 | 0 | 1 | - | 0 | 0 |
| 13 | 0.722 | 0.500 | 1.000 | 0.001 | 0.062 | 1 | 1 | - | 0 | 0 |
| 14 | 0.778 | 0.500 | 1.000 | 0.001 | 0.062 | 1 | 1 | - | 0 | 0 |
| 15 | 0.833 | 0.500 | 1.000 | 0.001 | 0.043 | 0 | 1 | - | 0 | 0 |
| 16 | 0.889 | 0.500 | 1.000 | 0.001 | 0.046 | 0 | 1 | - | 0 | 0 |
| 17 | 0.944 | 0.500 | 1.000 | 0.001 | 0.046 | 0 | 1 | - | 0 | 0 |
| 18 | 1.000 | 0.500 | 1.000 | 0.001 | 0.048 | 0 | 1 | - | 0 | 0 |

### Sparkle256

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.230 | 0.500 | 0.670 | 0.046 | 0 | 1 | - | 67 | 64 |
| 2 | 0.200 | 0.437 | 0.875 | 0.126 | 0.049 | 0 | 1 | - | 0 | 0 |
| 3 | 0.300 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |
| 4 | 0.400 | 0.500 | 1.000 | 0.001 | 0.047 | 0 | 1 | - | 0 | 0 |
| 5 | 0.500 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 6 | 0.600 | 0.500 | 1.000 | 0.001 | 0.051 | 0 | 1 | - | 0 | 0 |
| 7 | 0.700 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |
| 8 | 0.800 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 9 | 0.900 | 0.500 | 1.000 | 0.001 | 0.051 | 0 | 1 | - | 0 | 0 |
| 10 | 1.000 | 0.500 | 1.000 | 0.001 | 0.049 | 0 | 1 | - | 0 | 0 |

### Sparkle256-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.230 | 0.500 | 0.670 | 0.046 | 0 | 1 | - | 67 | 64 |
| 2 | 0.286 | 0.437 | 0.875 | 0.126 | 0.049 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.047 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.045 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.051 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |

### Sparkle384

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.091 | 0.194 | 0.416 | 0.715 | 0.049 | 0 | 2 | - | 129 | 128 |
| 2 | 0.182 | 0.417 | 0.833 | 0.167 | 0.046 | 0 | 1 | - | 0 | 0 |
| 3 | 0.273 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 4 | 0.364 | 0.500 | 1.000 | 0.001 | 0.048 | 0 | 1 | - | 0 | 0 |
| 5 | 0.455 | 0.500 | 1.000 | 0.001 | 0.054 | 0 | 1 | - | 0 | 0 |
| 6 | 0.545 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 7 | 0.636 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |
| 8 | 0.727 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 9 | 0.818 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 10 | 0.909 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 11 | 1.000 | 0.500 | 1.000 | 0.001 | 0.051 | 0 | 1 | - | 0 | 0 |

### Sparkle384-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.194 | 0.416 | 0.715 | 0.049 | 0 | 2 | - | 129 | 128 |
| 2 | 0.286 | 0.417 | 0.833 | 0.167 | 0.046 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.048 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.054 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |

### Sparkle512

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.083 | 0.175 | 0.375 | 0.739 | 0.049 | 0 | 1 | - | 196 | 192 |
| 2 | 0.167 | 0.406 | 0.812 | 0.188 | 0.051 | 0 | 1 | - | 0 | 0 |
| 3 | 0.250 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 4 | 0.333 | 0.500 | 1.000 | 0.001 | 0.057 | 0 | 1 | - | 0 | 0 |
| 5 | 0.417 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 6 | 0.500 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 7 | 0.583 | 0.500 | 1.000 | 0.001 | 0.060 | 0 | 1 | - | 0 | 0 |
| 8 | 0.667 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |
| 9 | 0.750 | 0.500 | 1.000 | 0.001 | 0.056 | 0 | 1 | - | 0 | 0 |
| 10 | 0.833 | 0.500 | 1.000 | 0.001 | 0.051 | 0 | 1 | - | 0 | 0 |
| 11 | 0.917 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 12 | 1.000 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |

### Sparkle512-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.175 | 0.375 | 0.739 | 0.049 | 0 | 1 | - | 196 | 192 |
| 2 | 0.250 | 0.406 | 0.812 | 0.188 | 0.051 | 0 | 1 | - | 0 | 0 |
| 3 | 0.375 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 4 | 0.500 | 0.500 | 1.000 | 0.001 | 0.057 | 0 | 1 | - | 0 | 0 |
| 5 | 0.625 | 0.500 | 1.000 | 0.001 | 0.052 | 0 | 1 | - | 0 | 0 |
| 6 | 0.750 | 0.500 | 1.000 | 0.001 | 0.050 | 0 | 1 | - | 0 | 0 |
| 7 | 0.875 | 0.500 | 1.000 | 0.001 | 0.060 | 0 | 1 | - | 0 | 0 |
| 8 | 1.000 | 0.500 | 1.000 | 0.001 | 0.053 | 0 | 1 | - | 0 | 0 |

### Alzette

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.250 | 0.068 | 0.266 | 0.970 | 0.040 | 0 | 2033 | -1.011 | 56 | 56 |
| 2 | 0.500 | 0.192 | 0.724 | 0.894 | 0.046 | 0 | 526 | -2.961 | 41 | 32 |
| 3 | 0.750 | 0.388 | 0.992 | 0.655 | 0.050 | 0 | 22 | -7.541 | 8 | 0 |
| 4 | 1.000 | 0.469 | 1.000 | 0.323 | 0.038 | 0 | 1 | - | 0 | 0 |

## 5. Keacakan pada ronde penuh dan kecepatan

| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 2.98 (4.32) | 0.038 (0.056) | 7.998/8.000 | 32.00 (32) | 4.00 (4.00) | 635 | 25.4 | 0.101 |
| CLEFIA-128 | 2.85 (4.47) | 0.040 (0.058) | 7.999/8.000 | 64.11 (64) | 5.59 (5.66) | 241 | 13.4 | 0.531 |
| Sparkle256 | 3.36 (4.62) | 0.043 (0.061) | 7.999/8.000 | 128.03 (128) | 7.94 (8.00) | 187 | 18.7 | 1.370 |
| Sparkle256-slim | 2.85 (4.62) | 0.048 (0.061) | 7.999/8.000 | 127.98 (128) | 7.96 (8.00) | 130 | 18.6 | 1.971 |
| Sparkle384 | 3.09 (4.70) | 0.051 (0.063) | 8.000/8.000 | 192.06 (192) | 9.77 (9.80) | 263 | 23.9 | 1.459 |
| Sparkle384-slim | 3.12 (4.70) | 0.050 (0.063) | 8.000/8.000 | 192.08 (192) | 9.74 (9.80) | 190 | 27.2 | 2.016 |
| Sparkle512 | 3.03 (4.76) | 0.051 (0.064) | 8.000/8.000 | 255.93 (256) | 11.40 (11.31) | 386 | 32.2 | 1.325 |
| Sparkle512-slim | 3.67 (4.76) | 0.053 (0.064) | 8.000/8.000 | 255.89 (256) | 11.52 (11.31) | 256 | 32.1 | 1.997 |
| Alzette | 2.47 (4.32) | 0.048 (0.056) | 7.997/8.000 | 32.00 (32) | 4.02 (4.00) | 4 | 1.0 | 16.054 |

## 6. Kombinasi antar-pasangan

Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.

| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |
|---|---|---|---|---|---|---|
| RECTANGLE-80 vs CLEFIA-128 | 0.240 vs 0.278 | 0.038 | 0.160 vs 0.278 | 0.955 | 0.0747 | 0.190 |
| RECTANGLE-80 vs Sparkle256 | 0.240 vs 0.200 | -0.040 | 0.160 vs 0.300 | 0.939 | 0.0932 | 0.074 |
| RECTANGLE-80 vs Sparkle256-slim | 0.240 vs 0.286 | 0.046 | 0.160 vs 0.429 | 0.934 | 0.0998 | 0.051 |
| RECTANGLE-80 vs Sparkle384 | 0.240 vs 0.182 | -0.058 | 0.160 vs 0.273 | 0.943 | 0.0902 | 0.069 |
| RECTANGLE-80 vs Sparkle384-slim | 0.240 vs 0.286 | 0.046 | 0.160 vs 0.429 | 0.932 | 0.1045 | 0.050 |
| RECTANGLE-80 vs Sparkle512 | 0.240 vs 0.167 | -0.073 | 0.160 vs 0.250 | 0.941 | 0.0911 | 0.076 |
| RECTANGLE-80 vs Sparkle512-slim | 0.240 vs 0.250 | 0.010 | 0.160 vs 0.375 | 0.946 | 0.0926 | 0.050 |
| RECTANGLE-80 vs Alzette | 0.240 vs 1.000 | 0.760 | 0.160 vs 1.000 | 0.649 | 0.3402 | 0.006 |
| CLEFIA-128 vs Sparkle256 | 0.278 vs 0.200 | -0.078 | 0.278 vs 0.300 | 0.933 | 0.0955 | 0.388 |
| CLEFIA-128 vs Sparkle256-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.954 | 0.0881 | 0.269 |
| CLEFIA-128 vs Sparkle384 | 0.278 vs 0.182 | -0.096 | 0.278 vs 0.273 | 0.932 | 0.0953 | 0.364 |
| CLEFIA-128 vs Sparkle384-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.955 | 0.0934 | 0.263 |
| CLEFIA-128 vs Sparkle512 | 0.278 vs 0.167 | -0.111 | 0.278 vs 0.250 | 0.924 | 0.1028 | 0.401 |
| CLEFIA-128 vs Sparkle512-slim | 0.278 vs 0.250 | -0.028 | 0.278 vs 0.375 | 0.959 | 0.0859 | 0.266 |
| CLEFIA-128 vs Alzette | 0.278 vs 1.000 | 0.722 | 0.278 vs 1.000 | 0.707 | 0.3154 | 0.033 |
| Sparkle256 vs Sparkle256-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.967 | 0.0630 | 0.695 |
| Sparkle256 vs Sparkle384 | 0.200 vs 0.182 | -0.018 | 0.300 vs 0.273 | 0.999 | 0.0081 | 0.939 |
| Sparkle256 vs Sparkle384-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.956 | 0.0776 | 0.679 |
| Sparkle256 vs Sparkle512 | 0.200 vs 0.167 | -0.033 | 0.300 vs 0.250 | 0.997 | 0.0156 | 1.034 |
| Sparkle256 vs Sparkle512-slim | 0.200 vs 0.250 | 0.050 | 0.300 vs 0.375 | 0.974 | 0.0603 | 0.686 |
| Sparkle256 vs Alzette | 0.200 vs 1.000 | 0.800 | 0.300 vs 1.000 | 0.630 | 0.3559 | 0.085 |
| Sparkle256-slim vs Sparkle384 | 0.286 vs 0.182 | -0.104 | 0.429 vs 0.273 | 0.965 | 0.0631 | 1.351 |
| Sparkle256-slim vs Sparkle384-slim | 0.286 vs 0.286 | 0.000 | 0.429 vs 0.429 | 0.999 | 0.0152 | 0.978 |
| Sparkle256-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.956 | 0.0706 | 1.488 |
| Sparkle256-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.997 | 0.0161 | 0.987 |
| Sparkle256-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.732 | 0.3178 | 0.123 |
| Sparkle384 vs Sparkle384-slim | 0.182 vs 0.286 | 0.104 | 0.273 vs 0.429 | 0.954 | 0.0778 | 0.724 |
| Sparkle384 vs Sparkle512 | 0.182 vs 0.167 | -0.015 | 0.273 vs 0.250 | 0.999 | 0.0098 | 1.101 |
| Sparkle384 vs Sparkle512-slim | 0.182 vs 0.250 | 0.068 | 0.273 vs 0.375 | 0.973 | 0.0601 | 0.731 |
| Sparkle384 vs Alzette | 0.182 vs 1.000 | 0.818 | 0.273 vs 1.000 | 0.627 | 0.3562 | 0.091 |
| Sparkle384-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.944 | 0.0853 | 1.521 |
| Sparkle384-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.996 | 0.0213 | 1.010 |
| Sparkle384-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.748 | 0.3088 | 0.126 |
| Sparkle512 vs Sparkle512-slim | 0.167 vs 0.250 | 0.083 | 0.250 vs 0.375 | 0.965 | 0.0678 | 0.664 |
| Sparkle512 vs Alzette | 0.167 vs 1.000 | 0.833 | 0.250 vs 1.000 | 0.613 | 0.3607 | 0.083 |
| Sparkle512-slim vs Alzette | 0.250 vs 1.000 | 0.750 | 0.375 vs 1.000 | 0.717 | 0.3218 | 0.124 |

### Kemiripan per kurva (Pearson)

**Avalanche rata-rata** (`avalanche_mean`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.998 | 0.992 | 0.975 | 0.994 | 0.963 | 0.991 | 0.980 | 0.609 |
| CLEFIA-128 | 0.998 | 1.000 | 0.993 | 0.983 | 0.994 | 0.972 | 0.990 | 0.986 | 0.622 |
| Sparkle256 | 0.992 | 0.993 | 1.000 | 0.971 | 1.000 | 0.954 | 0.998 | 0.971 | 0.597 |
| Sparkle256-slim | 0.975 | 0.983 | 0.971 | 1.000 | 0.970 | 0.998 | 0.959 | 0.999 | 0.710 |
| Sparkle384 | 0.994 | 0.994 | 1.000 | 0.970 | 1.000 | 0.953 | 0.999 | 0.970 | 0.594 |
| Sparkle384-slim | 0.963 | 0.972 | 0.954 | 0.998 | 0.953 | 1.000 | 0.940 | 0.997 | 0.733 |
| Sparkle512 | 0.991 | 0.990 | 0.998 | 0.959 | 0.999 | 0.940 | 1.000 | 0.960 | 0.575 |
| Sparkle512-slim | 0.980 | 0.986 | 0.971 | 0.999 | 0.970 | 0.997 | 0.960 | 1.000 | 0.697 |
| Alzette | 0.609 | 0.622 | 0.597 | 0.710 | 0.594 | 0.733 | 0.575 | 0.697 | 1.000 |

**Kelengkapan difusi** (`completeness`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.962 | 0.976 | 0.926 | 0.979 | 0.899 | 0.985 | 0.920 | 0.656 |
| CLEFIA-128 | 0.962 | 1.000 | 0.989 | 0.986 | 0.992 | 0.975 | 0.988 | 0.988 | 0.763 |
| Sparkle256 | 0.976 | 0.989 | 1.000 | 0.973 | 0.999 | 0.955 | 0.998 | 0.969 | 0.729 |
| Sparkle256-slim | 0.926 | 0.986 | 0.973 | 1.000 | 0.974 | 0.997 | 0.965 | 0.998 | 0.841 |
| Sparkle384 | 0.979 | 0.992 | 0.999 | 0.974 | 1.000 | 0.956 | 0.999 | 0.971 | 0.728 |
| Sparkle384-slim | 0.899 | 0.975 | 0.955 | 0.997 | 0.956 | 1.000 | 0.944 | 0.997 | 0.866 |
| Sparkle512 | 0.985 | 0.988 | 0.998 | 0.965 | 0.999 | 0.944 | 1.000 | 0.962 | 0.709 |
| Sparkle512-slim | 0.920 | 0.988 | 0.969 | 0.998 | 0.971 | 0.997 | 0.962 | 1.000 | 0.834 |
| Alzette | 0.656 | 0.763 | 0.729 | 0.841 | 0.728 | 0.866 | 0.709 | 0.834 | 1.000 |

**Pelanggaran SAC** (`sac_violation_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.989 | 0.978 | 0.981 | 0.975 | 0.974 | 0.964 | 0.990 | 0.500 |
| CLEFIA-128 | 0.989 | 1.000 | 0.997 | 0.975 | 0.996 | 0.965 | 0.991 | 0.984 | 0.487 |
| Sparkle256 | 0.978 | 0.997 | 1.000 | 0.961 | 0.999 | 0.948 | 0.996 | 0.971 | 0.470 |
| Sparkle256-slim | 0.981 | 0.975 | 0.961 | 1.000 | 0.956 | 0.999 | 0.942 | 0.998 | 0.572 |
| Sparkle384 | 0.975 | 0.996 | 0.999 | 0.956 | 1.000 | 0.943 | 0.999 | 0.967 | 0.464 |
| Sparkle384-slim | 0.974 | 0.965 | 0.948 | 0.999 | 0.943 | 1.000 | 0.927 | 0.995 | 0.588 |
| Sparkle512 | 0.964 | 0.991 | 0.996 | 0.942 | 0.999 | 0.927 | 1.000 | 0.954 | 0.447 |
| Sparkle512-slim | 0.990 | 0.984 | 0.971 | 0.998 | 0.967 | 0.995 | 0.954 | 1.000 | 0.551 |
| Alzette | 0.500 | 0.487 | 0.470 | 0.572 | 0.464 | 0.588 | 0.447 | 0.551 | 1.000 |

**Korelasi linear signifikan** (`lin_sig_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.993 | 0.995 | 0.964 | 0.997 | 0.964 | 0.998 | 0.982 | 0.842 |
| CLEFIA-128 | 0.993 | 1.000 | 0.995 | 0.983 | 0.993 | 0.983 | 0.988 | 0.996 | 0.873 |
| Sparkle256 | 0.995 | 0.995 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.833 |
| Sparkle256-slim | 0.964 | 0.983 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle384 | 0.997 | 0.993 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.825 |
| Sparkle384-slim | 0.964 | 0.983 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle512 | 0.998 | 0.988 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.815 |
| Sparkle512-slim | 0.982 | 0.996 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.904 |
| Alzette | 0.842 | 0.873 | 0.833 | 0.926 | 0.825 | 0.926 | 0.815 | 0.904 | 1.000 |

**Frekuensi dy teratas** (`diff_top_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.817 | 0.964 | 0.906 | 0.974 | 0.906 | 0.983 | 0.932 | 0.585 |
| CLEFIA-128 | 0.817 | 1.000 | 0.931 | 0.972 | 0.917 | 0.972 | 0.900 | 0.967 | 0.718 |
| Sparkle256 | 0.964 | 0.931 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.639 |
| Sparkle256-slim | 0.906 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.734 |
| Sparkle384 | 0.974 | 0.917 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.631 |
| Sparkle384-slim | 0.906 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.734 |
| Sparkle512 | 0.983 | 0.900 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.621 |
| Sparkle512-slim | 0.932 | 0.967 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.710 |
| Alzette | 0.585 | 0.718 | 0.639 | 0.734 | 0.631 | 0.734 | 0.621 | 0.710 | 1.000 |

**Bit zero-sum (8 bit aktif)** (`zs8_balanced_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.970 | 0.730 | 0.852 | 0.740 | 0.888 | 0.725 | 0.872 | 0.704 |
| CLEFIA-128 | 0.970 | 1.000 | 0.693 | 0.824 | 0.703 | 0.862 | 0.688 | 0.832 | 0.778 |
| Sparkle256 | 0.730 | 0.693 | 1.000 | 0.974 | 0.999 | 0.956 | 0.998 | 0.968 | 0.513 |
| Sparkle256-slim | 0.852 | 0.824 | 0.974 | 1.000 | 0.980 | 0.997 | 0.976 | 0.997 | 0.612 |
| Sparkle384 | 0.740 | 0.703 | 0.999 | 0.980 | 1.000 | 0.963 | 0.999 | 0.973 | 0.520 |
| Sparkle384-slim | 0.888 | 0.862 | 0.956 | 0.997 | 0.963 | 1.000 | 0.957 | 0.997 | 0.640 |
| Sparkle512 | 0.725 | 0.688 | 0.998 | 0.976 | 0.999 | 0.957 | 1.000 | 0.968 | 0.510 |
| Sparkle512-slim | 0.872 | 0.832 | 0.968 | 0.997 | 0.973 | 0.997 | 0.968 | 1.000 | 0.609 |
| Alzette | 0.704 | 0.778 | 0.513 | 0.612 | 0.520 | 0.640 | 0.510 | 0.609 | 1.000 |

## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)

| | r_norm | avalanche_mean | completeness | sac_violation_frac | lin_sig_frac | lin_max_abs_corr | diff_top_frac | zs8_balanced_frac |
|---|---|---|---|---|---|---|---|---|
| r_norm | 1.000 | 0.539 | 0.644 | -0.563 | -0.169 | 0.047 | -0.425 | -0.635 |
| avalanche_mean | 0.539 | 1.000 | 0.710 | -0.622 | -0.254 | 0.076 | -0.531 | -0.600 |
| completeness | 0.644 | 0.710 | 1.000 | -0.702 | -0.279 | -0.021 | -0.602 | -0.729 |
| sac_violation_frac | -0.563 | -0.622 | -0.702 | 1.000 | 0.203 | -0.207 | 0.538 | 0.652 |
| lin_sig_frac | -0.169 | -0.254 | -0.279 | 0.203 | 1.000 | 0.374 | 0.377 | 0.291 |
| lin_max_abs_corr | 0.047 | 0.076 | -0.021 | -0.207 | 0.374 | 1.000 | -0.008 | -0.064 |
| diff_top_frac | -0.425 | -0.531 | -0.602 | 0.538 | 0.377 | -0.008 | 1.000 | 0.726 |
| zs8_balanced_frac | -0.635 | -0.600 | -0.729 | 0.652 | 0.291 | -0.064 | 0.726 | 1.000 |

## Catatan cara membaca

- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan juga kolom `/R`.
- "Tidak terdeteksi" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap tidak membuktikan tidak adanya distinguisher.
- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.
- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.
