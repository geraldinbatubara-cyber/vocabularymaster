# Vocabulary Master

Aplikasi Streamlit untuk membantu belajar vocabulary bahasa Inggris melalui battle 2 pemain.

## Fitur MVP

- Battle 2 pemain secara bergiliran
- Landing page ceria sebelum masuk lobi battle
- Level Beginner, Intermediate, Advanced, dan Mixed
- Mode soal: Meaning Match, Reverse Meaning, Synonym, Antonym, dan Fill the Blank
- Pilihan kategori vocabulary berdasarkan bank soal aktif
- Upload CSV untuk mengganti bank vocabulary sewaktu-waktu
- Download template CSV bank vocabulary
- Pemain pertama dipilih acak saat battle dimulai
- Pilihan jumlah soal 20, 30, 40, atau 50
- Countdown 10 detik per soal
- Countdown berjalan otomatis dari 10 sampai 0 dan menampilkan status Waktu Habis
- Skor otomatis berdasarkan ketepatan, kecepatan, dan streak
- 30% soal terakhir menjadi bonus round dengan tingkat kesulitan dan nilai lebih tinggi
- Review jawaban setelah battle selesai
- Bank vocabulary awal dalam `data/vocabulary.csv`

## Format CSV Bank Vocabulary

Kolom wajib: `word`, `meaning`, `level`, `synonym`, `antonym`, `example`.

Kolom opsional: `category`. Jika kosong atau tidak ada, aplikasi memakai kategori `general`.

## Menjalankan lokal

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
