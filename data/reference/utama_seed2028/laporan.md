# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette

Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.

Parameter: `{"primitif": ["rectangle", "clefia", "sparkle256", "sparkle256s", "sparkle384", "sparkle384s", "sparkle512", "sparkle512s", "alzette"], "sampel_avalanche": 64, "sampel_linear": 2048, "pasangan_diff": 1024, "koset": 16, "kunci": 0, "sampel_kunci_avalanche": 32, "seed": 2028, "cepat": false, "perbarui_kecepatan": false}`

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
| Sparkle256 | 3 | 2 | 1 | - | 1 | 1 | 2 | 0.200 | 8 | 0.800 |
| Sparkle256-slim | 3 | 2 | 1 | - | 1 | 1 | 2 | 0.286 | 5 | 0.714 |
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
| 1 | 0.040 | 0.042 | 0.062 | 0.963 | 0.296 | 32 | 278 | -1.881 | 64 | 64 |
| 2 | 0.080 | 0.112 | 0.250 | 0.858 | 0.093 | 0 | 68 | -3.913 | 64 | 64 |
| 3 | 0.120 | 0.197 | 0.562 | 0.670 | 0.094 | 0 | 7 | -7.193 | 64 | 64 |
| 4 | 0.160 | 0.314 | 0.999 | 0.452 | 0.094 | 0 | 2 | - | 56 | 63 |
| 5 | 0.200 | 0.423 | 1.000 | 0.106 | 0.077 | 0 | 1 | - | 31 | 55 |
| 6 | 0.240 | 0.481 | 1.000 | 0.003 | 0.080 | 0 | 1 | - | 4 | 10 |
| 7 | 0.280 | 0.495 | 1.000 | 0.001 | 0.081 | 0 | 1 | - | 0 | 0 |
| 8 | 0.320 | 0.498 | 1.000 | 0.001 | 0.095 | 0 | 1 | - | 0 | 0 |
| 9 | 0.360 | 0.500 | 1.000 | 0.001 | 0.079 | 0 | 1 | - | 0 | 0 |
| 10 | 0.400 | 0.502 | 1.000 | 0.000 | 0.079 | 0 | 1 | - | 0 | 0 |
| 11 | 0.440 | 0.500 | 1.000 | 0.001 | 0.080 | 0 | 1 | - | 0 | 0 |
| 12 | 0.480 | 0.498 | 1.000 | 0.000 | 0.093 | 0 | 1 | - | 0 | 0 |
| 13 | 0.520 | 0.500 | 1.000 | 0.000 | 0.079 | 0 | 1 | - | 0 | 0 |
| 14 | 0.560 | 0.501 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 15 | 0.600 | 0.500 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 16 | 0.640 | 0.501 | 1.000 | 0.000 | 0.093 | 0 | 1 | - | 0 | 0 |
| 17 | 0.680 | 0.500 | 1.000 | 0.000 | 0.083 | 0 | 1 | - | 0 | 0 |
| 18 | 0.720 | 0.501 | 1.000 | 0.000 | 0.093 | 0 | 1 | - | 0 | 0 |
| 19 | 0.760 | 0.499 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 20 | 0.800 | 0.499 | 1.000 | 0.001 | 0.076 | 0 | 1 | - | 0 | 0 |
| 21 | 0.840 | 0.500 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 22 | 0.880 | 0.500 | 1.000 | 0.000 | 0.090 | 0 | 1 | - | 0 | 0 |
| 23 | 0.920 | 0.498 | 1.000 | 0.001 | 0.083 | 0 | 1 | - | 0 | 0 |
| 24 | 0.960 | 0.499 | 1.000 | 0.000 | 0.088 | 0 | 1 | - | 0 | 0 |
| 25 | 1.000 | 0.500 | 1.000 | 0.000 | 0.077 | 0 | 1 | - | 0 | 0 |

### CLEFIA-128

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.056 | 0.071 | 0.133 | 0.876 | 1.000 | 64 | 1024 | 0.000 | 128 | 128 |
| 2 | 0.111 | 0.198 | 0.383 | 0.626 | 0.089 | 0 | 34 | -4.913 | 128 | 128 |
| 3 | 0.167 | 0.322 | 0.633 | 0.376 | 0.087 | 0 | 1 | - | 96 | 128 |
| 4 | 0.222 | 0.442 | 0.879 | 0.126 | 0.087 | 0 | 1 | - | 32 | 96 |
| 5 | 0.278 | 0.500 | 1.000 | 0.001 | 0.089 | 0 | 1 | - | 0 | 32 |
| 6 | 0.333 | 0.501 | 1.000 | 0.001 | 0.089 | 0 | 1 | - | 0 | 0 |
| 7 | 0.389 | 0.501 | 1.000 | 0.001 | 0.079 | 0 | 1 | - | 0 | 0 |
| 8 | 0.444 | 0.501 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 9 | 0.500 | 0.501 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 10 | 0.556 | 0.500 | 1.000 | 0.000 | 0.087 | 0 | 1 | - | 0 | 0 |
| 11 | 0.611 | 0.500 | 1.000 | 0.001 | 0.088 | 0 | 1 | - | 0 | 0 |
| 12 | 0.667 | 0.500 | 1.000 | 0.000 | 0.088 | 0 | 1 | - | 0 | 0 |
| 13 | 0.722 | 0.500 | 1.000 | 0.001 | 0.085 | 0 | 1 | - | 0 | 0 |
| 14 | 0.778 | 0.500 | 1.000 | 0.001 | 0.085 | 0 | 1 | - | 0 | 0 |
| 15 | 0.833 | 0.500 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 16 | 0.889 | 0.501 | 1.000 | 0.001 | 0.092 | 0 | 1 | - | 0 | 0 |
| 17 | 0.944 | 0.501 | 1.000 | 0.001 | 0.090 | 0 | 1 | - | 0 | 0 |
| 18 | 1.000 | 0.501 | 1.000 | 0.000 | 0.083 | 0 | 1 | - | 0 | 0 |

### Sparkle256

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.230 | 0.499 | 0.600 | 0.126 | 1 | 1 | - | 68 | 64 |
| 2 | 0.200 | 0.438 | 0.875 | 0.126 | 0.108 | 0 | 1 | - | 0 | 0 |
| 3 | 0.300 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 4 | 0.400 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 5 | 0.500 | 0.500 | 1.000 | 0.001 | 0.095 | 0 | 1 | - | 0 | 0 |
| 6 | 0.600 | 0.500 | 1.000 | 0.001 | 0.106 | 0 | 1 | - | 0 | 0 |
| 7 | 0.700 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 8 | 0.800 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 9 | 0.900 | 0.500 | 1.000 | 0.001 | 0.089 | 0 | 1 | - | 0 | 0 |
| 10 | 1.000 | 0.500 | 1.000 | 0.001 | 0.129 | 1 | 1 | - | 0 | 0 |

### Sparkle256-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.230 | 0.499 | 0.600 | 0.126 | 1 | 1 | - | 68 | 64 |
| 2 | 0.286 | 0.438 | 0.875 | 0.126 | 0.108 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.095 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.106 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |

### Sparkle384

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.091 | 0.194 | 0.416 | 0.656 | 0.117 | 0 | 1 | - | 132 | 128 |
| 2 | 0.182 | 0.416 | 0.833 | 0.167 | 0.102 | 0 | 1 | - | 0 | 0 |
| 3 | 0.273 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 4 | 0.364 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 5 | 0.455 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 6 | 0.545 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 7 | 0.636 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |
| 8 | 0.727 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 9 | 0.818 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 10 | 0.909 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 11 | 1.000 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |

### Sparkle384-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.143 | 0.194 | 0.416 | 0.656 | 0.117 | 0 | 1 | - | 132 | 128 |
| 2 | 0.286 | 0.416 | 0.833 | 0.167 | 0.102 | 0 | 1 | - | 0 | 0 |
| 3 | 0.429 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 4 | 0.571 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 5 | 0.714 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 0 |
| 6 | 0.857 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 7 | 1.000 | 0.500 | 1.000 | 0.001 | 0.100 | 0 | 1 | - | 0 | 0 |

### Sparkle512

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.083 | 0.175 | 0.374 | 0.688 | 0.103 | 0 | 1 | - | 195 | 192 |
| 2 | 0.167 | 0.407 | 0.812 | 0.188 | 0.101 | 0 | 1 | - | 0 | 0 |
| 3 | 0.250 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 1 |
| 4 | 0.333 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 5 | 0.417 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 6 | 0.500 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 7 | 0.583 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 8 | 0.667 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |
| 9 | 0.750 | 0.500 | 1.000 | 0.001 | 0.115 | 0 | 1 | - | 0 | 0 |
| 10 | 0.833 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 11 | 0.917 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 12 | 1.000 | 0.500 | 1.000 | 0.001 | 0.098 | 0 | 1 | - | 0 | 0 |

### Sparkle512-slim

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.125 | 0.175 | 0.374 | 0.688 | 0.103 | 0 | 1 | - | 195 | 192 |
| 2 | 0.250 | 0.407 | 0.812 | 0.188 | 0.101 | 0 | 1 | - | 0 | 0 |
| 3 | 0.375 | 0.500 | 1.000 | 0.001 | 0.101 | 0 | 1 | - | 0 | 1 |
| 4 | 0.500 | 0.500 | 1.000 | 0.001 | 0.102 | 0 | 1 | - | 0 | 0 |
| 5 | 0.625 | 0.500 | 1.000 | 0.001 | 0.097 | 0 | 1 | - | 0 | 0 |
| 6 | 0.750 | 0.500 | 1.000 | 0.001 | 0.099 | 0 | 1 | - | 0 | 0 |
| 7 | 0.875 | 0.500 | 1.000 | 0.001 | 0.104 | 0 | 1 | - | 0 | 0 |
| 8 | 1.000 | 0.500 | 1.000 | 0.001 | 0.108 | 0 | 1 | - | 0 | 0 |

### Alzette

| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.250 | 0.067 | 0.202 | 0.965 | 0.079 | 0 | 520 | -0.978 | 52 | 48 |
| 2 | 0.500 | 0.194 | 0.622 | 0.840 | 0.079 | 0 | 123 | -3.057 | 28 | 30 |
| 3 | 0.750 | 0.388 | 0.982 | 0.529 | 0.081 | 0 | 4 | -8.000 | 2 | 0 |
| 4 | 1.000 | 0.470 | 1.000 | 0.165 | 0.087 | 0 | 1 | - | 0 | 0 |

## 5. Keacakan pada ronde penuh dan kecepatan

| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |
|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 2.74 (4.32) | 0.077 (0.111) | 7.988/8.000 | 32.10 (32) | 3.99 (4.00) | 635 | 25.4 | 0.101 |
| CLEFIA-128 | 2.83 (4.47) | 0.086 (0.117) | 7.994/8.000 | 63.94 (64) | 5.55 (5.66) | 247 | 13.7 | 0.518 |
| Sparkle256 | 2.74 (4.62) | 0.092 (0.122) | 7.997/8.000 | 128.20 (128) | 8.09 (8.00) | 189 | 18.9 | 1.357 |
| Sparkle256-slim | 2.61 (4.62) | 0.097 (0.122) | 7.997/8.000 | 128.30 (128) | 7.96 (8.00) | 123 | 17.6 | 2.074 |
| Sparkle384 | 3.14 (4.70) | 0.100 (0.125) | 7.998/8.000 | 192.46 (192) | 9.54 (9.80) | 270 | 24.6 | 1.421 |
| Sparkle384-slim | 3.49 (4.70) | 0.084 (0.125) | 7.998/8.000 | 191.87 (192) | 9.54 (9.80) | 183 | 26.2 | 2.093 |
| Sparkle512 | 3.31 (4.76) | 0.093 (0.128) | 7.999/8.000 | 255.71 (256) | 11.47 (11.31) | 397 | 33.1 | 1.291 |
| Sparkle512-slim | 3.31 (4.76) | 0.098 (0.128) | 7.999/8.000 | 256.11 (256) | 11.11 (11.31) | 247 | 30.9 | 2.074 |
| Alzette | 2.78 (4.32) | 0.079 (0.111) | 7.988/8.000 | 32.05 (32) | 4.03 (4.00) | 4 | 1.1 | 14.662 |

## 6. Kombinasi antar-pasangan

Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.

| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |
|---|---|---|---|---|---|---|
| RECTANGLE-80 vs CLEFIA-128 | 0.240 vs 0.278 | 0.038 | 0.200 vs 0.278 | 0.957 | 0.0671 | 0.194 |
| RECTANGLE-80 vs Sparkle256 | 0.240 vs 0.200 | -0.040 | 0.200 vs 0.300 | 0.939 | 0.0892 | 0.074 |
| RECTANGLE-80 vs Sparkle256-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.927 | 0.1047 | 0.049 |
| RECTANGLE-80 vs Sparkle384 | 0.240 vs 0.182 | -0.058 | 0.200 vs 0.273 | 0.944 | 0.0855 | 0.071 |
| RECTANGLE-80 vs Sparkle384-slim | 0.240 vs 0.286 | 0.046 | 0.200 vs 0.429 | 0.925 | 0.1103 | 0.048 |
| RECTANGLE-80 vs Sparkle512 | 0.240 vs 0.167 | -0.073 | 0.200 vs 0.250 | 0.943 | 0.0853 | 0.078 |
| RECTANGLE-80 vs Sparkle512-slim | 0.240 vs 0.250 | 0.010 | 0.200 vs 0.375 | 0.939 | 0.0988 | 0.049 |
| RECTANGLE-80 vs Alzette | 0.240 vs 1.000 | 0.760 | 0.200 vs 1.000 | 0.641 | 0.3337 | 0.007 |
| CLEFIA-128 vs Sparkle256 | 0.278 vs 0.200 | -0.078 | 0.278 vs 0.300 | 0.933 | 0.0970 | 0.382 |
| CLEFIA-128 vs Sparkle256-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.955 | 0.0858 | 0.250 |
| CLEFIA-128 vs Sparkle384 | 0.278 vs 0.182 | -0.096 | 0.278 vs 0.273 | 0.932 | 0.0963 | 0.365 |
| CLEFIA-128 vs Sparkle384-slim | 0.278 vs 0.286 | 0.008 | 0.278 vs 0.429 | 0.956 | 0.0915 | 0.248 |
| CLEFIA-128 vs Sparkle512 | 0.278 vs 0.167 | -0.111 | 0.278 vs 0.250 | 0.924 | 0.1033 | 0.402 |
| CLEFIA-128 vs Sparkle512-slim | 0.278 vs 0.250 | -0.028 | 0.278 vs 0.375 | 0.959 | 0.0847 | 0.250 |
| CLEFIA-128 vs Alzette | 0.278 vs 1.000 | 0.722 | 0.278 vs 1.000 | 0.706 | 0.3086 | 0.035 |
| Sparkle256 vs Sparkle256-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.968 | 0.0614 | 0.654 |
| Sparkle256 vs Sparkle384 | 0.200 vs 0.182 | -0.018 | 0.300 vs 0.273 | 0.999 | 0.0077 | 0.955 |
| Sparkle256 vs Sparkle384-slim | 0.200 vs 0.286 | 0.086 | 0.300 vs 0.429 | 0.957 | 0.0766 | 0.648 |
| Sparkle256 vs Sparkle512 | 0.200 vs 0.167 | -0.033 | 0.300 vs 0.250 | 0.997 | 0.0147 | 1.051 |
| Sparkle256 vs Sparkle512-slim | 0.200 vs 0.250 | 0.050 | 0.300 vs 0.375 | 0.974 | 0.0602 | 0.654 |
| Sparkle256 vs Alzette | 0.200 vs 1.000 | 0.800 | 0.300 vs 1.000 | 0.634 | 0.3469 | 0.093 |
| Sparkle256-slim vs Sparkle384 | 0.286 vs 0.182 | -0.104 | 0.429 vs 0.273 | 0.966 | 0.0611 | 1.459 |
| Sparkle256-slim vs Sparkle384-slim | 0.286 vs 0.286 | 0.000 | 0.429 vs 0.429 | 0.999 | 0.0157 | 0.991 |
| Sparkle256-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.958 | 0.0682 | 1.606 |
| Sparkle256-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.998 | 0.0155 | 1.000 |
| Sparkle256-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.737 | 0.3090 | 0.141 |
| Sparkle384 vs Sparkle384-slim | 0.182 vs 0.286 | 0.104 | 0.273 vs 0.429 | 0.955 | 0.0763 | 0.679 |
| Sparkle384 vs Sparkle512 | 0.182 vs 0.167 | -0.015 | 0.273 vs 0.250 | 0.999 | 0.0094 | 1.101 |
| Sparkle384 vs Sparkle512-slim | 0.182 vs 0.250 | 0.068 | 0.273 vs 0.375 | 0.973 | 0.0594 | 0.685 |
| Sparkle384 vs Alzette | 0.182 vs 1.000 | 0.818 | 0.273 vs 1.000 | 0.631 | 0.3470 | 0.097 |
| Sparkle384-slim vs Sparkle512 | 0.286 vs 0.167 | -0.119 | 0.429 vs 0.250 | 0.945 | 0.0834 | 1.621 |
| Sparkle384-slim vs Sparkle512-slim | 0.286 vs 0.250 | -0.036 | 0.429 vs 0.375 | 0.997 | 0.0206 | 1.009 |
| Sparkle384-slim vs Alzette | 0.286 vs 1.000 | 0.714 | 0.429 vs 1.000 | 0.753 | 0.2998 | 0.143 |
| Sparkle512 vs Sparkle512-slim | 0.167 vs 0.250 | 0.083 | 0.250 vs 0.375 | 0.965 | 0.0667 | 0.623 |
| Sparkle512 vs Alzette | 0.167 vs 1.000 | 0.833 | 0.250 vs 1.000 | 0.617 | 0.3514 | 0.088 |
| Sparkle512-slim vs Alzette | 0.250 vs 1.000 | 0.750 | 0.375 vs 1.000 | 0.722 | 0.3125 | 0.141 |

### Kemiripan per kurva (Pearson)

**Avalanche rata-rata** (`avalanche_mean`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.999 | 0.992 | 0.976 | 0.994 | 0.963 | 0.990 | 0.980 | 0.610 |
| CLEFIA-128 | 0.999 | 1.000 | 0.993 | 0.983 | 0.995 | 0.972 | 0.990 | 0.986 | 0.623 |
| Sparkle256 | 0.992 | 0.993 | 1.000 | 0.971 | 1.000 | 0.954 | 0.998 | 0.970 | 0.597 |
| Sparkle256-slim | 0.976 | 0.983 | 0.971 | 1.000 | 0.970 | 0.998 | 0.959 | 0.999 | 0.711 |
| Sparkle384 | 0.994 | 0.995 | 1.000 | 0.970 | 1.000 | 0.953 | 0.999 | 0.970 | 0.595 |
| Sparkle384-slim | 0.963 | 0.972 | 0.954 | 0.998 | 0.953 | 1.000 | 0.940 | 0.997 | 0.735 |
| Sparkle512 | 0.990 | 0.990 | 0.998 | 0.959 | 0.999 | 0.940 | 1.000 | 0.960 | 0.575 |
| Sparkle512-slim | 0.980 | 0.986 | 0.970 | 0.999 | 0.970 | 0.997 | 0.960 | 1.000 | 0.698 |
| Alzette | 0.610 | 0.623 | 0.597 | 0.711 | 0.595 | 0.735 | 0.575 | 0.698 | 1.000 |

**Kelengkapan difusi** (`completeness`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.962 | 0.977 | 0.926 | 0.979 | 0.899 | 0.985 | 0.920 | 0.607 |
| CLEFIA-128 | 0.962 | 1.000 | 0.989 | 0.986 | 0.992 | 0.975 | 0.988 | 0.988 | 0.714 |
| Sparkle256 | 0.977 | 0.989 | 1.000 | 0.973 | 0.999 | 0.955 | 0.998 | 0.969 | 0.679 |
| Sparkle256-slim | 0.926 | 0.986 | 0.973 | 1.000 | 0.974 | 0.997 | 0.965 | 0.998 | 0.796 |
| Sparkle384 | 0.979 | 0.992 | 0.999 | 0.974 | 1.000 | 0.956 | 0.999 | 0.971 | 0.678 |
| Sparkle384-slim | 0.899 | 0.975 | 0.955 | 0.997 | 0.956 | 1.000 | 0.944 | 0.997 | 0.822 |
| Sparkle512 | 0.985 | 0.988 | 0.998 | 0.965 | 0.999 | 0.944 | 1.000 | 0.962 | 0.659 |
| Sparkle512-slim | 0.920 | 0.988 | 0.969 | 0.998 | 0.971 | 0.997 | 0.962 | 1.000 | 0.787 |
| Alzette | 0.607 | 0.714 | 0.679 | 0.796 | 0.678 | 0.822 | 0.659 | 0.787 | 1.000 |

**Pelanggaran SAC** (`sac_violation_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.994 | 0.991 | 0.963 | 0.990 | 0.952 | 0.987 | 0.973 | 0.487 |
| CLEFIA-128 | 0.994 | 1.000 | 0.995 | 0.981 | 0.995 | 0.970 | 0.990 | 0.986 | 0.510 |
| Sparkle256 | 0.991 | 0.995 | 1.000 | 0.966 | 1.000 | 0.952 | 0.997 | 0.971 | 0.488 |
| Sparkle256-slim | 0.963 | 0.981 | 0.966 | 1.000 | 0.964 | 0.999 | 0.952 | 0.999 | 0.594 |
| Sparkle384 | 0.990 | 0.995 | 1.000 | 0.964 | 1.000 | 0.949 | 0.999 | 0.969 | 0.484 |
| Sparkle384-slim | 0.952 | 0.970 | 0.952 | 0.999 | 0.949 | 1.000 | 0.935 | 0.996 | 0.613 |
| Sparkle512 | 0.987 | 0.990 | 0.997 | 0.952 | 0.999 | 0.935 | 1.000 | 0.958 | 0.467 |
| Sparkle512-slim | 0.973 | 0.986 | 0.971 | 0.999 | 0.969 | 0.996 | 0.958 | 1.000 | 0.577 |
| Alzette | 0.487 | 0.510 | 0.488 | 0.594 | 0.484 | 0.613 | 0.467 | 0.577 | 1.000 |

**Korelasi linear signifikan** (`lin_sig_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.985 | 0.994 | 0.943 | 0.998 | 0.944 | 1.000 | 0.968 | 0.809 |
| CLEFIA-128 | 0.985 | 1.000 | 0.996 | 0.983 | 0.993 | 0.984 | 0.988 | 0.996 | 0.873 |
| Sparkle256 | 0.994 | 0.996 | 1.000 | 0.962 | 0.999 | 0.962 | 0.996 | 0.982 | 0.835 |
| Sparkle256-slim | 0.943 | 0.983 | 0.962 | 1.000 | 0.955 | 1.000 | 0.948 | 0.996 | 0.927 |
| Sparkle384 | 0.998 | 0.993 | 0.999 | 0.955 | 1.000 | 0.956 | 0.999 | 0.978 | 0.825 |
| Sparkle384-slim | 0.944 | 0.984 | 0.962 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.926 |
| Sparkle512 | 1.000 | 0.988 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.815 |
| Sparkle512-slim | 0.968 | 0.996 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.904 |
| Alzette | 0.809 | 0.873 | 0.835 | 0.927 | 0.825 | 0.926 | 0.815 | 0.904 | 1.000 |

**Frekuensi dy teratas** (`diff_top_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.823 | 0.967 | 0.910 | 0.977 | 0.910 | 0.985 | 0.936 | 0.583 |
| CLEFIA-128 | 0.823 | 1.000 | 0.931 | 0.972 | 0.916 | 0.972 | 0.900 | 0.967 | 0.713 |
| Sparkle256 | 0.967 | 0.931 | 1.000 | 0.961 | 0.999 | 0.961 | 0.996 | 0.982 | 0.633 |
| Sparkle256-slim | 0.910 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.728 |
| Sparkle384 | 0.977 | 0.916 | 0.999 | 0.956 | 1.000 | 0.956 | 0.999 | 0.978 | 0.625 |
| Sparkle384-slim | 0.910 | 0.972 | 0.961 | 1.000 | 0.956 | 1.000 | 0.948 | 0.996 | 0.728 |
| Sparkle512 | 0.985 | 0.900 | 0.996 | 0.948 | 0.999 | 0.948 | 1.000 | 0.972 | 0.616 |
| Sparkle512-slim | 0.936 | 0.967 | 0.982 | 0.996 | 0.978 | 0.996 | 0.972 | 1.000 | 0.704 |
| Alzette | 0.583 | 0.713 | 0.633 | 0.728 | 0.625 | 0.728 | 0.616 | 0.704 | 1.000 |

**Bit zero-sum (8 bit aktif)** (`zs8_balanced_frac`)

| | RECTANGLE-80 | CLEFIA-128 | Sparkle256 | Sparkle256-slim | Sparkle384 | Sparkle384-slim | Sparkle512 | Sparkle512-slim | Alzette |
|---|---|---|---|---|---|---|---|---|---|
| RECTANGLE-80 | 1.000 | 0.978 | 0.716 | 0.842 | 0.726 | 0.879 | 0.711 | 0.860 | 0.750 |
| CLEFIA-128 | 0.978 | 1.000 | 0.693 | 0.824 | 0.703 | 0.862 | 0.688 | 0.832 | 0.802 |
| Sparkle256 | 0.716 | 0.693 | 1.000 | 0.974 | 0.999 | 0.956 | 0.998 | 0.968 | 0.572 |
| Sparkle256-slim | 0.842 | 0.824 | 0.974 | 1.000 | 0.980 | 0.997 | 0.976 | 0.997 | 0.666 |
| Sparkle384 | 0.726 | 0.703 | 0.999 | 0.980 | 1.000 | 0.963 | 0.999 | 0.973 | 0.579 |
| Sparkle384-slim | 0.879 | 0.862 | 0.956 | 0.997 | 0.963 | 1.000 | 0.958 | 0.997 | 0.693 |
| Sparkle512 | 0.711 | 0.688 | 0.998 | 0.976 | 0.999 | 0.958 | 1.000 | 0.968 | 0.570 |
| Sparkle512-slim | 0.860 | 0.832 | 0.968 | 0.997 | 0.973 | 0.997 | 0.968 | 1.000 | 0.666 |
| Alzette | 0.750 | 0.802 | 0.572 | 0.666 | 0.579 | 0.693 | 0.570 | 0.666 | 1.000 |

## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)

| | r_norm | avalanche_mean | completeness | sac_violation_frac | lin_sig_frac | lin_max_abs_corr | diff_top_frac | zs8_balanced_frac |
|---|---|---|---|---|---|---|---|---|
| r_norm | 1.000 | 0.444 | 0.663 | -0.548 | -0.219 | -0.117 | -0.343 | -0.654 |
| avalanche_mean | 0.444 | 1.000 | 0.728 | -0.613 | -0.280 | -0.242 | -0.466 | -0.548 |
| completeness | 0.663 | 0.728 | 1.000 | -0.728 | -0.363 | -0.229 | -0.608 | -0.725 |
| sac_violation_frac | -0.548 | -0.613 | -0.728 | 1.000 | 0.266 | 0.153 | 0.472 | 0.628 |
| lin_sig_frac | -0.219 | -0.280 | -0.363 | 0.266 | 1.000 | 0.374 | 0.278 | 0.341 |
| lin_max_abs_corr | -0.117 | -0.242 | -0.229 | 0.153 | 0.374 | 1.000 | -0.086 | 0.041 |
| diff_top_frac | -0.343 | -0.466 | -0.608 | 0.472 | 0.278 | -0.086 | 1.000 | 0.597 |
| zs8_balanced_frac | -0.654 | -0.548 | -0.725 | 0.628 | 0.341 | 0.041 | 0.597 | 1.000 |

## Catatan cara membaca

- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan juga kolom `/R`.
- "Tidak terdeteksi" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap tidak membuktikan tidak adanya distinguisher.
- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.
- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.
