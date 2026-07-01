# Vocabulary Master

Aplikasi Streamlit untuk membantu belajar vocabulary bahasa Inggris melalui battle 2 pemain.

## Fitur MVP

- Battle 2 pemain secara bergiliran
- Level Beginner, Intermediate, Advanced, dan Mixed
- Mode soal: Meaning Match, Reverse Meaning, Synonym, Antonym, dan Fill the Blank
- Pemain pertama dipilih acak saat battle dimulai
- Total 20 soal dengan countdown 10 detik per soal
- Countdown berjalan otomatis dari 10 sampai 0 dan menampilkan status Waktu Habis
- Skor otomatis berdasarkan ketepatan, kecepatan, dan streak
- Enam soal terakhir menjadi bonus round dengan tingkat kesulitan dan nilai lebih tinggi
- Review jawaban setelah battle selesai
- Bank vocabulary awal dalam `data/vocabulary.csv`

## Menjalankan lokal

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
