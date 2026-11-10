# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette

Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.

Parameter: `{"primitif": ["rectangle", "clefia", "sparkle256", "sparkle256s", "sparkle384", "sparkle384s", "sparkle512", "sparkle512s", "alzette"], "sampel_avalanche": 64, "sampel_linear": 2048, "pasangan_diff": 1024, "koset": 16, "kunci": 0, "sampel_kunci_avalanche": 32, "seed": 2027, "cepat": false, "perbarui_kecepatan": false}`

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
| RECTANGLE-80 | 5 | 6 | 1 | 4 | 6 | 6 | 6 | 0.240 | 19 | 0.760 |
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
| 1 | 0.040 | 0.042 | 0.062 | 0.962 | 0.292 | 32 | 269 | -1.929 | 64 | 64 |
| 2 | 0.080 | 0.112 | 0.250 | 0.855 | 0.105 | 0 | 61 | -4.069 | 64 | 64 |
| 3 | 0.120 | 0.197 | 0.562 | 0.671 | 0.083 | 0 | 7 | -7.193 | 64 | 64 |
| 4 | 0.160 | 0.316 | 0.999 | 0.444 | 0.093 | 0 | 3 | -8.415 | 57 | 63 |
| 5 | 0.200 | 0.427 | 1.000 | 0.100 | 0.086 | 0 | 1 | - | 31 | 52 |
| 6 | 0.240 | 0.479 | 1.000 | 0.004 | 0.090 | 0 | 1 | - | 3 | 8 |
| 7 | 0.280 | 0.496 | 1.000 | 0.001 | 0.081 | 0 | 1 | - | 0 | 0 |
| 8 | 0.320 | 0.502 | 1.000 | 0.000 | 0.088 | 0 | 1 | - | 0 | 0 |
| 9 | 0.360 | 0.501 | 1.000 | 0.001 | 0.076 | 0 | 1 | - | 0 | 0 |
| 10 | 0.400 | 0.501 | 1.000 | 0.000 | 0.084 | 0 | 1 | - | 0 | 0 |
| 11 | 0.440 | 0.498 | 1.000 | 0.001 | 0.082 | 0 | 1 | - | 0 | 0 |
| 12 | 0.480 | 0.499 | 1.000 | 0.001 | 0.103 | 0 | 1 | - | 0 | 0 |
| 13 | 0.520 | 0.501 | 1.000 | 0.000 | 0.076 | 0 | 1 | - | 0 | 0 |
| 14 | 0.560 | 0.499 | 1.000 | 0.000 | 0.079 | 0 | 1 | - | 0 | 0 |
| 15 | 0.600 | 0.497 | 1.000 | 0.000 | 0.079 | 0 | 1 | - | 0 | 0 |
| 16 | 0.640 | 0.500 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 17 | 0.680 | 0.500 | 1.000 | 0.000 | 0.089 | 0 | 1 | - | 0 | 0 |
| 18 | 0.720 | 0.500 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 19 | 0.760 | 0.501 | 1.000 | 0.000 | 0.092 | 0 | 1 | - | 0 | 0 |
| 20 | 0.800 | 0.502 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 21 | 0.840 | 0.501 | 1.000 | 0.001 | 0.091 | 0 | 1 | - | 0 | 0 |
| 22 | 0.880 | 0.501 | 1.000 | 0.000 | 0.086 | 0 | 1 | - | 0 | 0 |
| 23 | 0.920 | 0.499 | 1.000 | 0.001 | 0.080 | 0 | 1 | - | 0 | 0 |
| 24 | 0.960 | 0.499 | 1.000 | 0.000 | 0.073 | 0 | 1 | - | 0 | 0 |
| 25 | 1.000 | 0.499 | 1.000 | 0.000 | 0.073 | 0 | 1 | - | 0 | 0 |

### CLEFIA-128

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.056 | 0.072 | 0.133 | 0.876 | 1.000 | 64 | 1024 | 0.000 | 128 | 128 |
| 2 | 0.111 | 0.197 | 0.383 | 0.628 | 0.086 | 0 | 32 | -5.000 | 128 | 128 |
| 3 | 0.167 | 0.321 | 0.633 | 0.377 | 0.096 | 0 | 1 | - | 96 | 128 |
| 4 | 0.222 | 0.442 | 0.879 | 0.126 | 0.096 | 0 | 1 | - | 32 | 96 |
| 5 | 0.278 | 0.500 | 1.000 | 0.001 | 0.082 | 0 | 1 | - | 0 | 32 |
| 6 | 0.333 | 0.500 | 1.000 | 0.001 | 0.082 | 0 | 1 | - | 0 | 0 |
| 7 | 0.389 | 0.500 | 1.000 | 0.000 | 0.085 | 0 | 1 | - | 0 | 0 |
| 8 | 0.444 | 0.500 | 1.000 | 0.000 | 0.090 | 0 | 1 | - | 0 | 0 |
| 9 | 0.500 | 0.499 | 1.000 | 0.000 | 0.102 | 0 | 1 | - | 0 | 0 |
| 10 | 0.556 | 0.499 | 1.000 | 0.000 | 0.104 | 0 | 1 | - | 0 | 0 |
| 11 | 0.611 | 0.500 | 1.000 | 0.000 | 0.104 | 0 | 1 | - | 0 | 0 |
| 12 | 0.667 | 0.500 | 1.000 | 0.000 | 0.088 | 0 | 1 | - | 0 | 0 |
| 13 | 0.722 | 0.500 | 1.000 | 0.000 | 0.097 | 0 | 1 | - | 0 | 0 |
| 14 | 0.778 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 15 | 0.833 | 0.501 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 16 | 0.889 | 0.500 | 1.000 | 0.001 | 0.082 | 0 | 1 | - | 0 | 0 |
| 17 | 0.944 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 18 | 1.000 | 0.500 | 1.000 | 0.001 | 0.093 | 0 | 1 | - | 0 | 0 |

### Sparkle256

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.230 | 0.499 | 0.602 | 0.106 | 0 | 1 | - | 71 | 64 |
| 2 | 0.200 | 0.437 | 0.875 | 0.126 | 0.103 | 0 | 1 | - | 0 | 0 |
| 3 | 0.300 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 4 | 0.400 | 0.501 | 1.000 | 0.001 | 0.093 | 0 | 1 | - | 0 | 0 |
| 5 | 0.500 | 0.500 | 1.000 | 0.001 | 0.096 | 0 | 1 | - | 0 | 0 |
| 6 | 0.600 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 7 | 0.700 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |
| 8 | 0.800 | 0.500 | 1.000 | 0.001 | 0.093 | 0 | 1 | - | 0 | 0 |
| 9 | 0.900 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 10 | 1.000 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |

### Sparkle256-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.230 | 0.499 | 0.602 | 0.106 | 0 | 1 | - | 71 | 64 |
| 2 | 0.286 | 0.437 | 0.875 | 0.126 | 0.103 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.501 | 1.000 | 0.001 | 0.093 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.096 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.094 | 0 | 1 | - | 0 | 0 |

### Sparkle384

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.091 | 0.194 | 0.416 | 0.656 | 0.117 | 0 | 1 | - | 133 | 128 |
| 2 | 0.182 | 0.417 | 0.833 | 0.167 | 0.105 | 0 | 1 | - | 0 | 0 |
| 3 | 0.273 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |
| 4 | 0.364 | 0.500 | 1.000 | 0.001 | 0.096 | 0 | 1 | - | 0 | 0 |
| 5 | 0.455 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 6 | 0.545 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 0.636 | 0.500 | 1.000 | 0.001 | 0.110 | 0 | 1 | - | 0 | 0 |
| 8 | 0.727 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 9 | 0.818 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 10 | 0.909 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 11 | 1.000 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |

### Sparkle384-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.194 | 0.416 | 0.656 | 0.117 | 0 | 1 | - | 133 | 128 |
| 2 | 0.286 | 0.417 | 0.833 | 0.167 | 0.105 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.107 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.096 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.110 | 0 | 1 | - | 0 | 0 |

### Sparkle512

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.083 | 0.176 | 0.374 | 0.688 | 0.101 | 0 | 1 | - | 196 | 192 |
| 2 | 0.167 | 0.406 | 0.812 | 0.188 | 0.104 | 0 | 1 | - | 0 | 0 |
| 3 | 0.250 | 0.500 | 1.000 | 0.001 | 0.109 | 0 | 1 | - | 0 | 0 |
| 4 | 0.333 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 5 | 0.417 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 6 | 0.500 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 7 | 0.583 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 8 | 0.667 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 9 | 0.750 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 10 | 0.833 | 0.500 | 1.000 | 0.001 | 0.105 | 0 | 1 | - | 0 | 0 |
| 11 | 0.917 | 0.500 | 1.000 | 0.001 | 0.109 | 0 | 1 | - | 0 | 0 |
| 12 | 1.000 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |

### Sparkle512-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.176 | 0.374 | 0.688 | 0.101 | 0 | 1 | - | 196 | 192 |
| 2 | 0.250 | 0.406 | 0.812 | 0.188 | 0.104 | 0 | 1 | - | 0 | 0 |
| 3 | 0.375 | 0.500 | 1.000 | 0.001 | 0.109 | 0 | 1 | - | 0 | 0 |
| 4 | 0.500 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 5 | 0.625 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 6 | 0.750 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 7 | 0.875 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 8 | 1.000 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |

### Alzette

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.250 | 0.067 | 0.217 | 0.965 | 0.079 | 0 | 474 | -1.111 | 54 | 56 |
| 2 | 0.500 | 0.193 | 0.613 | 0.842 | 0.089 | 0 | 107 | -3.259 | 34 | 34 |
| 3 | 0.750 | 0.389 | 0.980 | 0.527 | 0.079 | 0 | 4 | -8.000 | 8 | 0 |
| 4 | 1.000 | 0.468 | 1.000 | 0.178 | 0.079 | 0 | 1 | - | 0 | 0 |

## 5. Keacakan pada ronde penuh dan kecepatan

| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 2.39 (4.32) | 0.078 (0.111) | 7.988/8.000 | 32.04 (32) | 3.96 (4.00) | 752 | 30.1 | 0.085 |
| CLEFIA-128 | 2.70 (4.47) | 0.091 (0.117) | 7.993/8.000 | 63.76 (64) | 5.73 (5.66) | 283 | 15.7 | 0.453 |
| Sparkle256 | 2.78 (4.62) | 0.091 (0.122) | 7.997/8.000 | 128.30 (128) | 8.12 (8.00) | 225 | 22.5 | 1.139 |
| Sparkle256-slim | 3.40 (4.62) | 0.094 (0.122) | 7.997/8.000 | 128.26 (128) | 8.04 (8.00) | 156 | 22.3 | 1.638 |
| Sparkle384 | 3.36 (4.70) | 0.118 (0.125) | 7.998/8.000 | 191.91 (192) | 10.08 (9.80) | 322 | 29.3 | 1.191 |
| Sparkle384-slim | 3.01 (4.70) | 0.108 (0.125) | 7.998/8.000 | 191.96 (192) | 9.61 (9.80) | 243 | 34.7 | 1.583 |
| Sparkle512 | 3.54 (4.76) | 0.101 (0.128) | 7.999/8.000 | 256.18 (256) | 10.93 (11.31) | 526 | 43.8 | 0.974 |
| Sparkle512-slim | 2.92 (4.76) | 0.102 (0.128) | 7.999/8.000 | 255.86 (256) | 11.67 (11.31) | 349 | 43.6 | 1.467 |
| Alzette | 3.93 (4.32) | 0.075 (0.111) | 7.989/8.000 | 31.95 (32) | 3.92 (4.00) | 5 | 1.2 | 12.934 |

## 6. Kombinasi antar-pasangan

Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.

| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |
|---|---|---|---|---|---|---|
| RECTANGLE-80 vs CLEFIA-128 | 0.240 vs 0.278 | 0.038 | 0.200 vs 0.278 | 0.955 | 0.0684 | 0.188 |
| RECTANGLE-80 vs Sparkle256 | 0.240 vs 0.200 | -0.040 | 0.200 vs 0.300 | 0.940 | 0.0882 | 0.075 |
| RECTANGLE-80 vs Sparkle256-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.927 | 0.1044 | 0.052 |
| RECTANGLE-80 vs Sparkle384 | 0.240 vs 0.182 | -0.058 | 0.200 vs 0.273 | 0.945 | 0.0845 | 0.071 |
| RECTANGLE-80 vs Sparkle384-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.924 | 0.1099 | 0.054 |
| RECTANGLE-80 vs Sparkle512 | 0.240 vs 0.167 | -0.073 | 0.200 vs 0.250 | 0.944 | 0.0844 | 0.087 |
| RECTANGLE-80 vs Sparkle512-slim | 0.240 vs 0.250 | 0.010 | 0.200 vs 0.375 | 0.940 | 0.0983 | 0.058 |
| RECTANGLE-80 vs Alzette | 0.240 vs 1.000 | 0.760 | 0.200 vs 1.000 | 0.636 | 0.3398 | 0.007 |
| CLEFIA-128 vs Sparkle256 | 0.278 vs 0.200 | -0.078 | 0.278 vs 0.300 | 0.933 | 0.0970 | 0.398 |
| CLEFIA-128 vs Sparkle256-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.955 | 0.0858 | 0.277 |
| CLEFIA-128 vs Sparkle384 | 0.278 vs 0.182 | -0.096 | 0.278 vs 0.273 | 0.932 | 0.0964 | 0.380 |
| CLEFIA-128 vs Sparkle384-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.956 | 0.0914 | 0.286 |
| CLEFIA-128 vs Sparkle512 | 0.278 vs 0.167 | -0.111 | 0.278 vs 0.250 | 0.924 | 0.1034 | 0.465 |
| CLEFIA-128 vs Sparkle512-slim | 0.278 vs 0.250 | -0.028 | 0.278 vs 0.375 | 0.959 | 0.0846 | 0.309 |
| CLEFIA-128 vs Alzette | 0.278 vs 1.000 | 0.722 | 0.278 vs 1.000 | 0.704 | 0.3132 | 0.035 |
| Sparkle256 vs Sparkle256-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.968 | 0.0615 | 0.695 |
| Sparkle256 vs Sparkle384 | 0.200 vs 0.182 | -0.018 | 0.300 vs 0.273 | 0.999 | 0.0077 | 0.957 |
| Sparkle256 vs Sparkle384-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.957 | 0.0765 | 0.720 |
| Sparkle256 vs Sparkle512 | 0.200 vs 0.167 | -0.033 | 0.300 vs 0.250 | 0.997 | 0.0147 | 1.170 |
| Sparkle256 vs Sparkle512-slim | 0.200 vs 0.250 | 0.050 | 0.300 vs 0.375 | 0.974 | 0.0601 | 0.776 |
| Sparkle256 vs Alzette | 0.200 vs 1.000 | 0.800 | 0.300 vs 1.000 | 0.627 | 0.3536 | 0.088 |
| Sparkle256-slim vs Sparkle384 | 0.286 vs 0.182 | -0.104 | 0.429 vs 0.273 | 0.966 | 0.0612 | 1.376 |
| Sparkle256-slim vs Sparkle384-slim | 0.286 vs 0.286 | 0.000 | 0.429 vs 0.429 | 0.999 | 0.0156 | 1.035 |
| Sparkle256-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.958 | 0.0683 | 1.683 |
| Sparkle256-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.998 | 0.0154 | 1.117 |
| Sparkle256-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.731 | 0.3157 | 0.127 |
| Sparkle384 vs Sparkle384-slim | 0.182 vs 0.286 | 0.104 | 0.273 vs 0.429 | 0.955 | 0.0763 | 0.753 |
| Sparkle384 vs Sparkle512 | 0.182 vs 0.167 | -0.015 | 0.273 vs 0.250 | 0.999 | 0.0093 | 1.223 |
| Sparkle384 vs Sparkle512-slim | 0.182 vs 0.250 | 0.068 | 0.273 vs 0.375 | 0.973 | 0.0595 | 0.812 |
| Sparkle384 vs Alzette | 0.182 vs 1.000 | 0.818 | 0.273 vs 1.000 | 0.624 | 0.3538 | 0.092 |
| Sparkle384-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.946 | 0.0834 | 1.626 |
| Sparkle384-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.997 | 0.0205 | 1.079 |
| Sparkle384-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.747 | 0.3066 | 0.122 |
| Sparkle512 vs Sparkle512-slim | 0.167 vs 0.250 | 0.083 | 0.250 vs 0.375 | 0.965 | 0.0667 | 0.664 |
| Sparkle512 vs Alzette | 0.167 vs 1.000 | 0.833 | 0.250 vs 1.000 | 0.610 | 0.3582 | 0.075 |
| Sparkle512-slim vs Alzette | 0.250 vs 1.000 | 0.750 | 0.375 vs 1.000 | 0.716 | 0.3194 | 0.113 |

### Kemiripan per kurva (Pearson)

**Avalanche rata-rata** (`avalanche_mean`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.998 | 0.992 | 0.975 | 0.994 | 0.962 | 0.991 | 0.979 | 0.609 |
| CLEFIA-128 | 0.998 | 1.000 | 0.993 | 0.983 | 0.994 | 0.972 | 0.990 | 0.986 | 0.623 |
| Sparkle256 | 0.992 | 0.993 | 1.000 | 0.970 | 1.000 | 0.954 | 0.998 | 0.971 | 0.596 |
| Sparkle256-slim | 0.975 | 0.983 | 0.970 | 1.000 | 0.969 | 0.998 | 0.959 | 0.999 | 0.711 |
| Sparkle384 | 0.994 | 0.994 | 1.000 | 0.969 | 1.000 | 0.953 | 0.999 | 0.970 | 0.594 |
| Sparkle384-slim | 0.962 | 0.972 | 0.954 | 0.998 | 0.953 | 1.000 | 0.940 | 0.997 | 0.734 |
| Sparkle512 | 0.991 | 0.990 | 0.998 | 0.959 | 0.999 | 0.940 | 1.000 | 0.960 | 0.575 |
| Sparkle512-slim | 0.979 | 0.986 | 0.971 | 0.999 | 0.970 | 0.997 | 0.960 | 1.000 | 0.697 |
| Alzette | 0.609 | 0.623 | 0.596 | 0.711 | 0.594 | 0.734 | 0.575 | 0.697 | 1.000 |

**Kelengkapan difusi** (`completeness`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.962 | 0.977 | 0.926 | 0.979 | 0.899 | 0.985 | 0.920 | 0.612 |
| CLEFIA-128 | 0.962 | 1.000 | 0.989 | 0.986 | 0.992 | 0.975 | 0.988 | 0.988 | 0.717 |
| Sparkle256 | 0.977 | 0.989 | 1.000 | 0.973 | 0.999 | 0.955 | 0.998 | 0.969 | 0.683 |
| Sparkle256-slim | 0.926 | 0.986 | 0.973 | 1.000 | 0.974 | 0.997 | 0.965 | 0.998 | 0.797 |
| Sparkle384 | 0.979 | 0.992 | 0.999 | 0.974 | 1.000 | 0.956 | 0.999 | 0.971 | 0.682 |
| Sparkle384-slim | 0.899 | 0.975 | 0.955 | 0.997 | 0.956 | 1.000 | 0.944 | 0.997 | 0.823 |
| Sparkle512 | 0.985 | 0.988 | 0.998 | 0.965 | 0.999 | 0.944 | 1.000 | 0.962 | 0.664 |
| Sparkle512-slim | 0.920 | 0.988 | 0.969 | 0.998 | 0.971 | 0.997 | 0.962 | 1.000 | 0.789 |
| Alzette | 0.612 | 0.717 | 0.683 | 0.797 | 0.682 | 0.823 | 0.664 | 0.789 | 1.000 |

**Pelanggaran SAC** (`sac_violation_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.994 | 0.991 | 0.962 | 0.991 | 0.950 | 0.987 | 0.972 | 0.487 |
| CLEFIA-128 | 0.994 | 1.000 | 0.995 | 0.981 | 0.995 | 0.970 | 0.990 | 0.986 | 0.511 |
| Sparkle256 | 0.991 | 0.995 | 1.000 | 0.966 | 1.000 | 0.952 | 0.997 | 0.971 | 0.490 |
| Sparkle256-slim | 0.962 | 0.981 | 0.966 | 1.000 | 0.964 | 0.999 | 0.951 | 0.999 | 0.596 |
| Sparkle384 | 0.991 | 0.995 | 1.000 | 0.964 | 1.000 | 0.949 | 0.999 | 0.969 | 0.485 |
| Sparkle384-slim | 0.950 | 0.970 | 0.952 | 0.999 | 0.949 | 1.000 | 0.935 | 0.996 | 0.615 |
| Sparkle512 | 0.987 | 0.990 | 0.997 | 0.951 | 0.999 | 0.935 | 1.000 | 0.958 | 0.468 |
| Sparkle512-slim | 0.972 | 0.986 | 0.971 | 0.999 | 0.969 | 0.996 | 0.958 | 1.000 | 0.579 |
| Alzette | 0.487 | 0.511 | 0.490 | 0.596 | 0.485 | 0.615 | 0.468 | 0.579 | 1.000 |

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
| RECTANGLE-80 | 1.000 | 0.818 | 0.965 | 0.907 | 0.975 | 0.907 | 0.984 | 0.933 | 0.601 |
| CLEFIA-128 | 0.818 | 1.000 | 0.931 | 0.972 | 0.917 | 0.972 | 0.900 | 0.967 | 0.735 |
| Sparkle256 | 0.965 | 0.931 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.656 |
| Sparkle256-slim | 0.907 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.752 |
| Sparkle384 | 0.975 | 0.917 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.648 |
| Sparkle384-slim | 0.907 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.752 |
| Sparkle512 | 0.984 | 0.900 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.638 |
| Sparkle512-slim | 0.933 | 0.967 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.727 |
| Alzette | 0.601 | 0.735 | 0.656 | 0.752 | 0.648 | 0.752 | 0.638 | 0.727 | 1.000 |

**Bit zero-sum (8 bit aktif)** (`zs8_balanced_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.976 | 0.724 | 0.848 | 0.735 | 0.885 | 0.719 | 0.867 | 0.700 |
| CLEFIA-128 | 0.976 | 1.000 | 0.693 | 0.824 | 0.703 | 0.862 | 0.688 | 0.832 | 0.765 |
| Sparkle256 | 0.724 | 0.693 | 1.000 | 0.974 | 0.999 | 0.956 | 0.998 | 0.968 | 0.505 |
| Sparkle256-slim | 0.848 | 0.824 | 0.974 | 1.000 | 0.980 | 0.997 | 0.976 | 0.997 | 0.602 |
| Sparkle384 | 0.735 | 0.703 | 0.999 | 0.980 | 1.000 | 0.963 | 0.999 | 0.973 | 0.512 |
| Sparkle384-slim | 0.885 | 0.862 | 0.956 | 0.997 | 0.963 | 1.000 | 0.957 | 0.997 | 0.630 |
| Sparkle512 | 0.719 | 0.688 | 0.998 | 0.976 | 0.999 | 0.957 | 1.000 | 0.968 | 0.502 |
| Sparkle512-slim | 0.867 | 0.832 | 0.968 | 0.997 | 0.973 | 0.997 | 0.968 | 1.000 | 0.599 |
| Alzette | 0.700 | 0.765 | 0.505 | 0.602 | 0.512 | 0.630 | 0.502 | 0.599 | 1.000 |

## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)

| | r_norm | avalanche_mean | completeness | sac_violation_frac | lin_sig_frac | lin_max_abs_corr | diff_top_frac | zs8_balanced_frac |
|---|---|---|---|---|---|---|---|---|
| r_norm | 1.000 | 0.486 | 0.663 | -0.534 | -0.240 | -0.199 | -0.343 | -0.635 |
| avalanche_mean | 0.486 | 1.000 | 0.728 | -0.620 | -0.238 | -0.237 | -0.466 | -0.611 |
| completeness | 0.663 | 0.728 | 1.000 | -0.727 | -0.328 | -0.252 | -0.608 | -0.763 |
| sac_violation_frac | -0.534 | -0.620 | -0.727 | 1.000 | 0.236 | 0.201 | 0.472 | 0.647 |
| lin_sig_frac | -0.240 | -0.238 | -0.328 | 0.236 | 1.000 | 0.240 | 0.483 | 0.340 |
| lin_max_abs_corr | -0.199 | -0.237 | -0.252 | 0.201 | 0.240 | 1.000 | -0.051 | 0.076 |
| diff_top_frac | -0.343 | -0.466 | -0.608 | 0.472 | 0.483 | -0.051 | 1.000 | 0.625 |
| zs8_balanced_frac | -0.635 | -0.611 | -0.763 | 0.647 | 0.340 | 0.076 | 0.625 | 1.000 |

## Catatan cara membaca

- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan juga kolom `/R`.
- "Tidak terdeteksi" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap tidak membuktikan tidak adanya distinguisher.
- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.
- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.
