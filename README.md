# Sentiment BBM — Analisis Sentimen Media Sosial Terkait BBM

Aplikasi Python siap pakai (*production-ready*) untuk melakukan analisis sentimen terhadap komentar media sosial berbahasa Indonesia mengenai kebijakan Bahan Bakar Minyak (BBM). Project ini menyediakan **dua pendekatan (versi)** analisis sentimen yang dapat digunakan sesuai kebutuhan.

---

## 🌟 Dua Pendekatan Analisis Sentimen

Project ini memiliki 2 versi implementasi analisis sentimen:

### 1. Versi Leksikon (Kamus Kata) — Versi 1
* **Metode:** Pencocokan berbasis kamus kata positif dan negatif secara manual (*lexicon-based*).
* **Kelebihan:** Sangat ringan, cepat, tanpa beban memori tinggi, dan tidak memerlukan GPU/model pembelajaran mesin.
* **Fitur:** Dilengkapi Command Line Interface (CLI) dan server API sederhana.

### 2. Versi Semantik AI (Embedding Vektor) — Versi 2
* **Metode:** Menggunakan model representasi bahasa *Sentence Transformers* (`paraphrase-multilingual-MiniLM-L12-v2`) untuk menghitung kesamaan kosinus (*cosine similarity*) antara teks input dan kalimat jangkar (*anchor sentences*).
* **Kelebihan:** Lebih cerdas mendeteksi konteks kalimat secara semantik tanpa bergantung pada pencocokan kata demi kata (*zero-shot learning*).

---

## 📁 Struktur Repositori

```
├── app/                        # [Versi 2] Analisis Sentimen Semantik AI
│   ├── main.py                 # FastAPI Entry Point (lifespan-managed engine)
│   ├── config.py               # Konfigurasi Pydantic settings dari .env
│   ├── schemas/
│   │   └── sentiment.py        # Model Pydantic Request/Response
│   └── services/
│       ├── verosight_client.py # Client HTTP Async untuk API Verosight
│       └── sentiment_engine.py # Logika embedding & Cosine Similarity
├── api/                        # [Versi 1] FastAPI Server untuk Leksikon
│   └── server.py               # Endpoint API versi Leksikon
├── data/                       # Penarikan data & Mock data
│   ├── fetch_data.py           # Script penarik data dari API Verosight
│   └── comments_cache.json     # Cache data komentar (diabaikan oleh git)
├── model/                      # [Versi 1] Logika Sentimen Leksikon
│   ├── analyzer.py             # Fungsi analisis batch & statistik
│   └── lexicon.py              # Definisi kamus kata positif/negatif
├── main.py                     # CLI Entry Point untuk Versi Leksikon
├── .env.example                # Template konfigurasi environment
├── .gitignore                  # File konfigurasi abaikan Git
├── requirements.txt            # Daftar dependensi Python
└── README.md                   # Dokumentasi project
```

---

## 🚀 Panduan Setup & Instalasi

### 1. Persiapan Virtual Environment
Buat dan aktifkan virtual environment Python:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instal Dependensi
Pasang semua pustaka yang diperlukan:
```bash
# Untuk Python 3.14+ di macOS, jalankan dengan flag kompabilitas PyO3 jika diperlukan:
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variable
Salin template `.env.example` menjadi `.env` lalu sesuaikan isinya:
```bash
cp .env.example .env
```
Isi variabel `VEROSIGHT_API_KEY` di dalam file `.env` dengan API Key Verosight Anda yang valid.

---

## 🛠️ Cara Menjalankan

### Menjalankan Versi 1 (Leksikon)

* **Melalui CLI (Command Line):**
  Untuk menganalisis satu kalimat teks langsung dari terminal:
  ```bash
  python3 main.py analyze "Kebijakan BBM sekarang sangat membantu rakyat kecil"
  ```
  Untuk menarik data komentar dari API Verosight dan menganalisisnya:
  ```bash
  python3 main.py comments --limit 5 --verbose
  ```

* **Melalui API Server (FastAPI):**
  Jalankan server API versi leksikon pada port 8001:
  ```bash
  python3 main.py serve --port 8001
  ```
  Akses dokumentasi interaktif API di: **http://localhost:8001/docs**

---

### Menjalankan Versi 2 (Semantik AI)

* **Melalui API Server (FastAPI):**
  Jalankan server API berbasis semantik/AI pada port 8003:
  ```bash
  uvicorn app.main:app --port 8003
  ```
  *(Catatan: Pada startup pertama, sistem akan mengunduh model embedding HuggingFace sebesar ~350MB)*

  Akses dokumentasi interaktif API di: **http://localhost:8003/docs**

---

## 🛡️ Keamanan Data (Penting!)
Jangan pernah melakukan push/commit file `.env` atau hardcode API Key langsung ke GitHub. Selalu gunakan mekanisme environment variable seperti yang sudah dikonfigurasi pada file `.gitignore`.
