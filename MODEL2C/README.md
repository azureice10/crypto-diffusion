# Eksperimen difusi dan distinguisher empiris

Python >=3.12. Dependensi pengukuran: NumPy dan Matplotlib (versi eksekusi
dicatat dalam `ambiente.json`). Jalankan dari folder induk:

```powershell
python -m pip install -r MODEL2C/requirements.txt
python -B MODEL2C/test_primitif.py
python -B MODEL2C/ulang_eksperimen.py
```

Runner menjalankan lima seed dengan ukuran sampel penuh, delapan kunci
RECTANGLE/CLEFIA pada seed 2026, satu sensitivitas sampel besar, audit statistik,
dan grafik. Hasil ditulis ke `eksperimen_ulang/`. Folder run yang sudah memiliki
`ringkasan.json` dilewati; gunakan `--output-dir` baru untuk pengukuran baru.

Pengukuran tunggal:

```powershell
python -B MODEL2C/bandingkan.py --seed 2026 --output-dir hasil_baru
python -B MODEL2C/buat_grafik.py --data-dir hasil_baru --output-dir hasil_baru/grafik
```

CLEFIA memakai 18 ronde asli. SPARKLE dan Alzette tidak mempunyai pembungkus
kunci tambahan. Trace mempertahankan kunci ronde dan input whitening, tetapi
belum menjalankan finalisasi ciphertext; audit membandingkan statistik trace
dengan ciphertext lengkap dan avalanche kunci pada titik akhir.

Aturan utama: peluang diskret aktual SAC dan koreksi kopling terhadap model
permutasi, nilai-p binomial eksak/Bonferroni untuk linear, binomial/kopling
untuk zero-sum, serta batas union tiga tabrakan untuk diferensial. Audit
menyajikan pula aturan lama, Bonferroni/Markov, dan koreksi lintas ronde/metrik.
Perbedaan daya deteksi antarukuran keadaan tetap harus dipertimbangkan.

Checkpoint `.pkl.gz` hanya boleh dibuka dari hasil lokal yang dipercaya.
Lihat `eksperimen_ulang/HASIL_EKSPERIMEN_ULANG.md` untuk hasil dan batasan.
