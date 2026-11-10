# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette

Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.

Parameter: `{"primitif": ["rectangle", "clefia", "sparkle256", "sparkle256s", "sparkle384", "sparkle384s", "sparkle512", "sparkle512s", "alzette"], "sampel_avalanche": 64, "sampel_linear": 2048, "pasangan_diff": 1024, "koset": 16, "kunci": 0, "sampel_kunci_avalanche": 32, "seed": 2029, "cepat": false, "perbarui_kecepatan": false}`

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
| RECTANGLE-80 | 5 | 6 | 1 | 3 | 6 | 6 | 6 | 0.240 | 19 | 0.760 |
| CLEFIA-128 | 5 | 4 | 1 | 2 | 4 | 5 | 5 | 0.278 | 13 | 0.722 |
| Sparkle256 | 3 | 2 | - | - | 1 | 1 | 2 | 0.200 | 8 | 0.800 |
| Sparkle256-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.286 | 5 | 0.714 |
| Sparkle384 | 3 | 2 | - | - | 1 | 1 | 2 | 0.182 | 9 | 0.818 |
| Sparkle384-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.286 | 5 | 0.714 |
| Sparkle512 | 3 | 2 | - | - | 1 | 1 | 2 | 0.167 | 10 | 0.833 |
| Sparkle512-slim | 3 | 2 | - | - | 1 | 1 | 2 | 0.250 | 6 | 0.750 |
| Alzette | - | 4 | - | 3 | 3 | 2 | 4 | 1.000 | 0 | 0.000 |

Horizon adalah akhir deretan deteksi yang bersambung dari ronde 1. Deteksi setelah jeda tidak menaikkan horizon menurut definisi operasional ini; deteksi itu bukan otomatis positif palsu dan dicatat di kolom `deteksi_terisolasi` pada `horizon.csv`. Ini horizon eksperimen, bukan batas serangan atau klaim keamanan. Angka serangan literatur harus dibaca terpisah karena model, data, kompleksitas, dan jenis serangannya berbeda.

Varian slim Sparkle memakai pengukuran varian big-nya, karena step-nya sama persis. Selisih margin big dan slim karena itu murni datang dari jumlah step.

## 4. Kurva per ronde

### RECTANGLE-80

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.040 | 0.042 | 0.062 | 0.963 | 0.294 | 32 | 253 | -2.017 | 64 | 64 |
| 2 | 0.080 | 0.114 | 0.250 | 0.858 | 0.101 | 0 | 74 | -3.791 | 64 | 64 |
| 3 | 0.120 | 0.197 | 0.562 | 0.673 | 0.082 | 0 | 6 | -7.415 | 64 | 64 |
| 4 | 0.160 | 0.316 | 0.998 | 0.450 | 0.075 | 0 | 2 | - | 56 | 63 |
| 5 | 0.200 | 0.423 | 1.000 | 0.111 | 0.088 | 0 | 1 | - | 28 | 50 |
| 6 | 0.240 | 0.480 | 1.000 | 0.002 | 0.082 | 0 | 1 | - | 3 | 6 |
| 7 | 0.280 | 0.497 | 1.000 | 0.001 | 0.074 | 0 | 1 | - | 0 | 0 |
| 8 | 0.320 | 0.501 | 1.000 | 0.000 | 0.079 | 0 | 1 | - | 0 | 0 |
| 9 | 0.360 | 0.501 | 1.000 | 0.000 | 0.081 | 0 | 1 | - | 0 | 0 |
| 10 | 0.400 | 0.500 | 1.000 | 0.000 | 0.080 | 0 | 1 | - | 0 | 0 |
| 11 | 0.440 | 0.498 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 12 | 0.480 | 0.500 | 1.000 | 0.001 | 0.078 | 0 | 1 | - | 0 | 0 |
| 13 | 0.520 | 0.500 | 1.000 | 0.000 | 0.080 | 0 | 1 | - | 0 | 0 |
| 14 | 0.560 | 0.499 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |
| 15 | 0.600 | 0.501 | 1.000 | 0.000 | 0.077 | 0 | 1 | - | 0 | 0 |
| 16 | 0.640 | 0.499 | 1.000 | 0.001 | 0.082 | 0 | 1 | - | 0 | 0 |
| 17 | 0.680 | 0.501 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 18 | 0.720 | 0.500 | 1.000 | 0.000 | 0.082 | 0 | 1 | - | 0 | 0 |
| 19 | 0.760 | 0.500 | 1.000 | 0.001 | 0.078 | 0 | 1 | - | 0 | 0 |
| 20 | 0.800 | 0.500 | 1.000 | 0.001 | 0.095 | 0 | 1 | - | 0 | 0 |
| 21 | 0.840 | 0.499 | 1.000 | 0.001 | 0.075 | 0 | 1 | - | 0 | 0 |
| 22 | 0.880 | 0.499 | 1.000 | 0.001 | 0.073 | 0 | 1 | - | 0 | 0 |
| 23 | 0.920 | 0.501 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 24 | 0.960 | 0.500 | 1.000 | 0.001 | 0.076 | 0 | 1 | - | 0 | 0 |
| 25 | 1.000 | 0.502 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |

### CLEFIA-128

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.056 | 0.072 | 0.133 | 0.876 | 1.000 | 64 | 1024 | 0.000 | 128 | 128 |
| 2 | 0.111 | 0.198 | 0.383 | 0.627 | 0.094 | 0 | 36 | -4.830 | 128 | 128 |
| 3 | 0.167 | 0.322 | 0.633 | 0.376 | 0.094 | 0 | 1 | - | 96 | 128 |
| 4 | 0.222 | 0.441 | 0.879 | 0.125 | 0.091 | 0 | 1 | - | 32 | 96 |
| 5 | 0.278 | 0.499 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 32 |
| 6 | 0.333 | 0.500 | 1.000 | 0.000 | 0.092 | 0 | 1 | - | 0 | 0 |
| 7 | 0.389 | 0.501 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 8 | 0.444 | 0.500 | 1.000 | 0.001 | 0.087 | 0 | 1 | - | 0 | 0 |
| 9 | 0.500 | 0.500 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 10 | 0.556 | 0.501 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 11 | 0.611 | 0.500 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 12 | 0.667 | 0.500 | 1.000 | 0.000 | 0.083 | 0 | 1 | - | 0 | 0 |
| 13 | 0.722 | 0.500 | 1.000 | 0.001 | 0.090 | 0 | 1 | - | 0 | 0 |
| 14 | 0.778 | 0.500 | 1.000 | 0.000 | 0.090 | 0 | 1 | - | 0 | 0 |
| 15 | 0.833 | 0.500 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 16 | 0.889 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 17 | 0.944 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 18 | 1.000 | 0.501 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |

### Sparkle256

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.231 | 0.499 | 0.598 | 0.088 | 0 | 1 | - | 64 | 64 |
| 2 | 0.200 | 0.438 | 0.875 | 0.126 | 0.101 | 0 | 1 | - | 0 | 0 |
| 3 | 0.300 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 4 | 0.400 | 0.500 | 1.000 | 0.000 | 0.100 | 0 | 1 | - | 0 | 0 |
| 5 | 0.500 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 6 | 0.600 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 7 | 0.700 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 8 | 0.800 | 0.500 | 1.000 | 0.001 | 0.116 | 0 | 1 | - | 0 | 0 |
| 9 | 0.900 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 1 | 0 |
| 10 | 1.000 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |

### Sparkle256-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.231 | 0.499 | 0.598 | 0.088 | 0 | 1 | - | 64 | 64 |
| 2 | 0.286 | 0.438 | 0.875 | 0.126 | 0.101 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.000 | 0.100 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |

### Sparkle384

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.091 | 0.194 | 0.416 | 0.657 | 0.100 | 0 | 1 | - | 133 | 128 |
| 2 | 0.182 | 0.416 | 0.833 | 0.167 | 0.102 | 0 | 1 | - | 0 | 0 |
| 3 | 0.273 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 4 | 0.364 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 5 | 0.455 | 0.500 | 1.000 | 0.001 | 0.119 | 0 | 1 | - | 0 | 0 |
| 6 | 0.545 | 0.500 | 1.000 | 0.001 | 0.110 | 0 | 1 | - | 0 | 0 |
| 7 | 0.636 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |
| 8 | 0.727 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 9 | 0.818 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 10 | 0.909 | 0.500 | 1.000 | 0.001 | 0.106 | 0 | 1 | - | 0 | 0 |
| 11 | 1.000 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |

### Sparkle384-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.194 | 0.416 | 0.657 | 0.100 | 0 | 1 | - | 133 | 128 |
| 2 | 0.286 | 0.416 | 0.833 | 0.167 | 0.102 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.119 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.110 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |

### Sparkle512

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.083 | 0.175 | 0.374 | 0.689 | 0.109 | 0 | 1 | - | 196 | 192 |
| 2 | 0.167 | 0.406 | 0.812 | 0.188 | 0.106 | 0 | 1 | - | 0 | 0 |
| 3 | 0.250 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 4 | 0.333 | 0.500 | 1.000 | 0.001 | 0.115 | 0 | 1 | - | 0 | 0 |
| 5 | 0.417 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 6 | 0.500 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 7 | 0.583 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 8 | 0.667 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 9 | 0.750 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 10 | 0.833 | 0.500 | 1.000 | 0.001 | 0.106 | 0 | 1 | - | 0 | 0 |
| 11 | 0.917 | 0.500 | 1.000 | 0.001 | 0.110 | 0 | 1 | - | 0 | 0 |
| 12 | 1.000 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |

### Sparkle512-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.175 | 0.374 | 0.689 | 0.109 | 0 | 1 | - | 196 | 192 |
| 2 | 0.250 | 0.406 | 0.812 | 0.188 | 0.106 | 0 | 1 | - | 0 | 0 |
| 3 | 0.375 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 4 | 0.500 | 0.500 | 1.000 | 0.001 | 0.115 | 0 | 1 | - | 0 | 0 |
| 5 | 0.625 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 6 | 0.750 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 7 | 0.875 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 8 | 1.000 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |

### Alzette

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.250 | 0.068 | 0.217 | 0.963 | 0.083 | 0 | 511 | -1.003 | 58 | 56 |
| 2 | 0.500 | 0.190 | 0.594 | 0.845 | 0.081 | 0 | 117 | -3.130 | 46 | 28 |
| 3 | 0.750 | 0.387 | 0.981 | 0.535 | 0.080 | 0 | 4 | -8.000 | 8 | 0 |
| 4 | 1.000 | 0.469 | 0.999 | 0.176 | 0.078 | 0 | 1 | - | 0 | 0 |

## 5. Keacakan pada ronde penuh dan kecepatan

| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 2.87 (4.32) | 0.076 (0.111) | 7.988/8.000 | 32.04 (32) | 3.94 (4.00) | 684 | 27.3 | 0.094 |
| CLEFIA-128 | 2.39 (4.47) | 0.080 (0.117) | 7.995/8.000 | 64.08 (64) | 5.62 (5.66) | 275 | 15.3 | 0.465 |
| Sparkle256 | 2.92 (4.62) | 0.097 (0.122) | 7.997/8.000 | 128.13 (128) | 8.12 (8.00) | 194 | 19.4 | 1.318 |
| Sparkle256-slim | 2.74 (4.62) | 0.093 (0.122) | 7.997/8.000 | 127.90 (128) | 8.17 (8.00) | 144 | 20.6 | 1.779 |
| Sparkle384 | 2.70 (4.70) | 0.095 (0.125) | 7.998/8.000 | 191.79 (192) | 9.69 (9.80) | 286 | 26.0 | 1.344 |
| Sparkle384-slim | 2.92 (4.70) | 0.103 (0.125) | 7.998/8.000 | 191.84 (192) | 9.79 (9.80) | 202 | 28.9 | 1.901 |
| Sparkle512 | 3.09 (4.76) | 0.100 (0.128) | 7.999/8.000 | 255.63 (256) | 11.60 (11.31) | 404 | 33.7 | 1.266 |
| Sparkle512-slim | 3.18 (4.76) | 0.105 (0.128) | 7.998/8.000 | 255.74 (256) | 11.65 (11.31) | 317 | 39.7 | 1.614 |
| Alzette | 2.96 (4.32) | 0.087 (0.111) | 7.991/8.000 | 32.09 (32) | 3.98 (4.00) | 4 | 1.0 | 15.510 |

## 6. Kombinasi antar-pasangan

Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.

| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |
|---|---|---|---|---|---|---|
| RECTANGLE-80 vs CLEFIA-128 | 0.240 vs 0.278 | 0.038 | 0.200 vs 0.278 | 0.954 | 0.0694 | 0.202 |
| RECTANGLE-80 vs Sparkle256 | 0.240 vs 0.200 | -0.040 | 0.200 vs 0.300 | 0.941 | 0.0881 | 0.071 |
| RECTANGLE-80 vs Sparkle256-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.928 | 0.1034 | 0.053 |
| RECTANGLE-80 vs Sparkle384 | 0.240 vs 0.182 | -0.058 | 0.200 vs 0.273 | 0.946 | 0.0843 | 0.070 |
| RECTANGLE-80 vs Sparkle384-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.925 | 0.1090 | 0.049 |
| RECTANGLE-80 vs Sparkle512 | 0.240 vs 0.167 | -0.073 | 0.200 vs 0.250 | 0.945 | 0.0842 | 0.074 |
| RECTANGLE-80 vs Sparkle512-slim | 0.240 vs 0.250 | 0.010 | 0.200 vs 0.375 | 0.941 | 0.0974 | 0.058 |
| RECTANGLE-80 vs Alzette | 0.240 vs 1.000 | 0.760 | 0.200 vs - | 0.637 | 0.3389 | 0.006 |
| CLEFIA-128 vs Sparkle256 | 0.278 vs 0.200 | -0.078 | 0.278 vs 0.300 | 0.933 | 0.0971 | 0.352 |
| CLEFIA-128 vs Sparkle256-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.955 | 0.0857 | 0.261 |
| CLEFIA-128 vs Sparkle384 | 0.278 vs 0.182 | -0.096 | 0.278 vs 0.273 | 0.932 | 0.0963 | 0.346 |
| CLEFIA-128 vs Sparkle384-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.956 | 0.0914 | 0.244 |
| CLEFIA-128 vs Sparkle512 | 0.278 vs 0.167 | -0.111 | 0.278 vs 0.250 | 0.924 | 0.1034 | 0.367 |
| CLEFIA-128 vs Sparkle512-slim | 0.278 vs 0.250 | -0.028 | 0.278 vs 0.375 | 0.959 | 0.0847 | 0.288 |
| CLEFIA-128 vs Alzette | 0.278 vs 1.000 | 0.722 | 0.278 vs - | 0.706 | 0.3116 | 0.030 |
| Sparkle256 vs Sparkle256-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.968 | 0.0614 | 0.741 |
| Sparkle256 vs Sparkle384 | 0.200 vs 0.182 | -0.018 | 0.300 vs 0.273 | 0.999 | 0.0077 | 0.981 |
| Sparkle256 vs Sparkle384-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.957 | 0.0767 | 0.694 |
| Sparkle256 vs Sparkle512 | 0.200 vs 0.167 | -0.033 | 0.300 vs 0.250 | 0.997 | 0.0146 | 1.041 |
| Sparkle256 vs Sparkle512-slim | 0.200 vs 0.250 | 0.050 | 0.300 vs 0.375 | 0.974 | 0.0603 | 0.817 |
| Sparkle256 vs Alzette | 0.200 vs 1.000 | 0.800 | 0.300 vs - | 0.626 | 0.3536 | 0.085 |
| Sparkle256-slim vs Sparkle384 | 0.286 vs 0.182 | -0.104 | 0.429 vs 0.273 | 0.966 | 0.0610 | 1.324 |
| Sparkle256-slim vs Sparkle384-slim | 0.286 vs 0.286 | 0.000 | 0.429 vs 0.429 | 0.999 | 0.0158 | 0.936 |
| Sparkle256-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.958 | 0.0681 | 1.405 |
| Sparkle256-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.998 | 0.0155 | 1.103 |
| Sparkle256-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs - | 0.730 | 0.3158 | 0.115 |
| Sparkle384 vs Sparkle384-slim | 0.182 vs 0.286 | 0.104 | 0.273 vs 0.429 | 0.955 | 0.0763 | 0.707 |
| Sparkle384 vs Sparkle512 | 0.182 vs 0.167 | -0.015 | 0.273 vs 0.250 | 0.999 | 0.0093 | 1.062 |
| Sparkle384 vs Sparkle512-slim | 0.182 vs 0.250 | 0.068 | 0.273 vs 0.375 | 0.973 | 0.0595 | 0.833 |
| Sparkle384 vs Alzette | 0.182 vs 1.000 | 0.818 | 0.273 vs - | 0.624 | 0.3537 | 0.087 |
| Sparkle384-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.945 | 0.0834 | 1.501 |
| Sparkle384-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.997 | 0.0206 | 1.178 |
| Sparkle384-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs - | 0.746 | 0.3065 | 0.123 |
| Sparkle512 vs Sparkle512-slim | 0.167 vs 0.250 | 0.083 | 0.250 vs 0.375 | 0.965 | 0.0668 | 0.785 |
| Sparkle512 vs Alzette | 0.167 vs 1.000 | 0.833 | 0.250 vs - | 0.610 | 0.3581 | 0.082 |
| Sparkle512-slim vs Alzette | 0.250 vs 1.000 | 0.750 | 0.375 vs - | 0.715 | 0.3193 | 0.104 |

### Kemiripan per kurva (Pearson)

**Avalanche rata-rata** (`avalanche_mean`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.999 | 0.992 | 0.976 | 0.994 | 0.963 | 0.991 | 0.980 | 0.609 |
| CLEFIA-128 | 0.999 | 1.000 | 0.993 | 0.984 | 0.995 | 0.972 | 0.990 | 0.986 | 0.622 |
| Sparkle256 | 0.992 | 0.993 | 1.000 | 0.971 | 1.000 | 0.954 | 0.998 | 0.970 | 0.595 |
| Sparkle256-slim | 0.976 | 0.984 | 0.971 | 1.000 | 0.970 | 0.998 | 0.959 | 0.999 | 0.709 |
| Sparkle384 | 0.994 | 0.995 | 1.000 | 0.970 | 1.000 | 0.953 | 0.999 | 0.970 | 0.593 |
| Sparkle384-slim | 0.963 | 0.972 | 0.954 | 0.998 | 0.953 | 1.000 | 0.940 | 0.997 | 0.732 |
| Sparkle512 | 0.991 | 0.990 | 0.998 | 0.959 | 0.999 | 0.940 | 1.000 | 0.960 | 0.574 |
| Sparkle512-slim | 0.980 | 0.986 | 0.970 | 0.999 | 0.970 | 0.997 | 0.960 | 1.000 | 0.695 |
| Alzette | 0.609 | 0.622 | 0.595 | 0.709 | 0.593 | 0.732 | 0.574 | 0.695 | 1.000 |

**Kelengkapan difusi** (`completeness`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.962 | 0.977 | 0.926 | 0.979 | 0.900 | 0.985 | 0.920 | 0.607 |
| CLEFIA-128 | 0.962 | 1.000 | 0.989 | 0.986 | 0.992 | 0.975 | 0.988 | 0.988 | 0.711 |
| Sparkle256 | 0.977 | 0.989 | 1.000 | 0.973 | 0.999 | 0.955 | 0.998 | 0.969 | 0.677 |
| Sparkle256-slim | 0.926 | 0.986 | 0.973 | 1.000 | 0.974 | 0.997 | 0.965 | 0.998 | 0.791 |
| Sparkle384 | 0.979 | 0.992 | 0.999 | 0.974 | 1.000 | 0.956 | 0.999 | 0.971 | 0.677 |
| Sparkle384-slim | 0.900 | 0.975 | 0.955 | 0.997 | 0.956 | 1.000 | 0.944 | 0.997 | 0.816 |
| Sparkle512 | 0.985 | 0.988 | 0.998 | 0.965 | 0.999 | 0.944 | 1.000 | 0.962 | 0.658 |
| Sparkle512-slim | 0.920 | 0.988 | 0.969 | 0.998 | 0.971 | 0.997 | 0.962 | 1.000 | 0.782 |
| Alzette | 0.607 | 0.711 | 0.677 | 0.791 | 0.677 | 0.816 | 0.658 | 0.782 | 1.000 |

**Pelanggaran SAC** (`sac_violation_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.994 | 0.991 | 0.964 | 0.991 | 0.952 | 0.987 | 0.973 | 0.486 |
| CLEFIA-128 | 0.994 | 1.000 | 0.995 | 0.981 | 0.995 | 0.970 | 0.990 | 0.986 | 0.509 |
| Sparkle256 | 0.991 | 0.995 | 1.000 | 0.967 | 1.000 | 0.952 | 0.997 | 0.971 | 0.487 |
| Sparkle256-slim | 0.964 | 0.981 | 0.967 | 1.000 | 0.964 | 0.999 | 0.952 | 0.999 | 0.593 |
| Sparkle384 | 0.991 | 0.995 | 1.000 | 0.964 | 1.000 | 0.949 | 0.999 | 0.969 | 0.483 |
| Sparkle384-slim | 0.952 | 0.970 | 0.952 | 0.999 | 0.949 | 1.000 | 0.935 | 0.996 | 0.612 |
| Sparkle512 | 0.987 | 0.990 | 0.997 | 0.952 | 0.999 | 0.935 | 1.000 | 0.958 | 0.466 |
| Sparkle512-slim | 0.973 | 0.986 | 0.971 | 0.999 | 0.969 | 0.996 | 0.958 | 1.000 | 0.575 |
| Alzette | 0.486 | 0.509 | 0.487 | 0.593 | 0.483 | 0.612 | 0.466 | 0.575 | 1.000 |

**Korelasi linear signifikan** (`lin_sig_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.985 | 0.994 | 0.944 | 0.998 | 0.944 | 1.000 | 0.968 | 0.809 |
| CLEFIA-128 | 0.985 | 1.000 | 0.995 | 0.984 | 0.993 | 0.984 | 0.988 | 0.996 | 0.873 |
| Sparkle256 | 0.994 | 0.995 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.833 |
| Sparkle256-slim | 0.944 | 0.984 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle384 | 0.998 | 0.993 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.825 |
| Sparkle384-slim | 0.944 | 0.984 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle512 | 1.000 | 0.988 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.815 |
| Sparkle512-slim | 0.968 | 0.996 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.904 |
| Alzette | 0.809 | 0.873 | 0.833 | 0.926 | 0.825 | 0.926 | 0.815 | 0.904 | 1.000 |

**Frekuensi dy teratas** (`diff_top_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.814 | 0.962 | 0.905 | 0.973 | 0.905 | 0.982 | 0.931 | 0.583 |
| CLEFIA-128 | 0.814 | 1.000 | 0.931 | 0.972 | 0.916 | 0.972 | 0.899 | 0.967 | 0.718 |
| Sparkle256 | 0.962 | 0.931 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.638 |
| Sparkle256-slim | 0.905 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.733 |
| Sparkle384 | 0.973 | 0.916 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.630 |
| Sparkle384-slim | 0.905 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.733 |
| Sparkle512 | 0.982 | 0.899 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.620 |
| Sparkle512-slim | 0.931 | 0.967 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.709 |
| Alzette | 0.583 | 0.718 | 0.638 | 0.733 | 0.630 | 0.733 | 0.620 | 0.709 | 1.000 |

**Bit zero-sum (8 bit aktif)** (`zs8_balanced_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.973 | 0.729 | 0.852 | 0.740 | 0.888 | 0.725 | 0.872 | 0.730 |
| CLEFIA-128 | 0.973 | 1.000 | 0.693 | 0.824 | 0.703 | 0.862 | 0.688 | 0.832 | 0.802 |
| Sparkle256 | 0.729 | 0.693 | 1.000 | 0.974 | 0.999 | 0.956 | 0.998 | 0.968 | 0.527 |
| Sparkle256-slim | 0.852 | 0.824 | 0.974 | 1.000 | 0.980 | 0.997 | 0.976 | 0.997 | 0.630 |
| Sparkle384 | 0.740 | 0.703 | 0.999 | 0.980 | 1.000 | 0.963 | 0.999 | 0.973 | 0.534 |
| Sparkle384-slim | 0.888 | 0.862 | 0.956 | 0.997 | 0.963 | 1.000 | 0.957 | 0.997 | 0.659 |
| Sparkle512 | 0.725 | 0.688 | 0.998 | 0.976 | 0.999 | 0.957 | 1.000 | 0.968 | 0.524 |
| Sparkle512-slim | 0.872 | 0.832 | 0.968 | 0.997 | 0.973 | 0.997 | 0.968 | 1.000 | 0.627 |
| Alzette | 0.730 | 0.802 | 0.527 | 0.630 | 0.534 | 0.659 | 0.524 | 0.627 | 1.000 |

## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)

| | r_norm | avalanche_mean | completeness | sac_violation_frac | lin_sig_frac | lin_max_abs_corr | diff_top_frac | zs8_balanced_frac |
|---|---|---|---|---|---|---|---|---|
| r_norm | 1.000 | 0.463 | 0.631 | -0.386 | -0.240 | -0.005 | -0.343 | -0.635 |
| avalanche_mean | 0.463 | 1.000 | 0.739 | -0.670 | -0.238 | -0.097 | -0.466 | -0.649 |
| completeness | 0.631 | 0.739 | 1.000 | -0.742 | -0.323 | -0.056 | -0.598 | -0.750 |
| sac_violation_frac | -0.386 | -0.670 | -0.742 | 1.000 | 0.236 | 0.010 | 0.472 | 0.608 |
| lin_sig_frac | -0.240 | -0.238 | -0.323 | 0.236 | 1.000 | 0.240 | 0.483 | 0.340 |
| lin_max_abs_corr | -0.005 | -0.097 | -0.056 | 0.010 | 0.240 | 1.000 | -0.087 | -0.065 |
| diff_top_frac | -0.343 | -0.466 | -0.598 | 0.472 | 0.483 | -0.087 | 1.000 | 0.625 |
| zs8_balanced_frac | -0.635 | -0.649 | -0.750 | 0.608 | 0.340 | -0.065 | 0.625 | 1.000 |

## Catatan cara membaca

- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan juga kolom `/R`.
- "Tidak terdeteksi" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap tidak membuktikan tidak adanya distinguisher.
- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.
- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.
