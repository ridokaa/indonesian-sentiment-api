# 💬 indonesian-sentiment-api

**Layanan analisis sentimen komentar media sosial Bahasa Indonesia.**
Kirim sebuah kalimat → dapat label **positif / negatif / netral**. Bisa dipakai lewat **terminal (CLI)** atau **REST API (FastAPI)**.

> 🔀 Mencari klasifikasi **topik** postingan trending (bukan sentimen)? Lihat project saudaranya: [**trending-topic-mapper**](https://github.com/ridokaa/trending-topic-mapper).

---

## 🧭 Gambaran Singkat

```
Komentar      ──►  V1 Leksikon (kamus kata)      ──►  positif / negatif / netral + skor
 (input / API      atau
  Verosight)       V2 Semantik (SBERT embedding)  ──►  POSITIVE / NEGATIVE / NEUTRAL + confidence
```

Ada **dua versi** mesin sentimen dalam satu repo. Keduanya berdiri sendiri, pilih sesuai kebutuhan:

| | **V1 — Leksikon** | **V2 — Semantik (AI)** |
|---|---|---|
| **Cara kerja** | Menghitung kata positif/negatif dari kamus, memperhitungkan **negasi** (`tidak`, `gak`, …) dan **penguat** (`sangat`, `makin`, …) | Mengubah teks jadi vektor (SBERT `paraphrase-multilingual-MiniLM-L12-v2`), lalu dibandingkan dengan **kalimat jangkar** tiap label pakai *cosine similarity* |
| **Kelebihan** | Sangat ringan, instan, hasilnya bisa dijelaskan (kata apa yang memicu) | Paham konteks kalimat walau kata kuncinya tidak ada di kamus (*zero-shot*) |
| **Kekurangan** | Hanya tahu kata yang ada di kamus | Perlu download model ~460 MB, lebih lambat |
| **Akses** | CLI + API (port 8001) | API (port 8003) |
| **Kode** | `main.py`, `api/`, `model/`, `data/` | `app/` |

---

## 🚀 Quick Start

```bash
git clone https://github.com/ridokaa/indonesian-sentiment-api.git
cd indonesian-sentiment-api

python3 -m venv venv
source venv/bin/activate
# Python 3.14+ di macOS butuh flag PyO3 di bawah; di versi lain boleh dihapus
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install -r requirements.txt

cp .env.example .env      # lalu isi VEROSIGHT_API_KEY
```

> Tanpa API key, **V1 tetap jalan** memakai 50 komentar contoh bawaan. **V2** butuh key untuk endpoint ambil-data, tapi endpoint analisis teks tetap jalan.

---

## 1️⃣ V1 — Leksikon

### Lewat terminal

```bash
# Analisis satu kalimat
python3 main.py analyze "Kebijakan BBM sekarang sangat membantu rakyat kecil"

# Ambil komentar (Verosight, fallback ke data contoh) lalu analisis semuanya
python3 main.py comments --keyword BBM --limit 5 --verbose
```

Contoh output:

```
Teks    : BBM naik lagi, rakyat makin sengsara
Sentimen: negatif
Skor    : -1.0
Kata negatif: naik, sengsara
```

### Lewat API

```bash
python3 main.py serve --port 8001      # dokumentasi interaktif: http://localhost:8001/docs
```

| Method | Endpoint | Fungsi |
|---|---|---|
| `GET` | `/analyze?text=...` | Analisis satu teks |
| `POST` | `/analyze` | Sama, body `{"text": "..."}` |
| `POST` | `/batch` | Banyak teks sekaligus, body `{"comments": ["...", "..."]}` + ringkasan jumlah per label |
| `GET` | `/comments?keyword=BBM&days=20&limit=50` | Lihat komentar mentah dari sumber data |
| `GET` | `/comments/sentiment?keyword=BBM` | Ambil komentar + langsung dianalisis |

```bash
curl "http://localhost:8001/analyze?text=Terima%20kasih%20pemerintah%20BBM%20tidak%20jadi%20naik"
```

---

## 2️⃣ V2 — Semantik (SBERT)

```bash
uvicorn app.main:app --port 8003       # dokumentasi interaktif: http://localhost:8003/docs
```

*Startup pertama mengunduh model embedding dari HuggingFace.*

| Method | Endpoint | Fungsi |
|---|---|---|
| `GET` | `/health` | Cek service hidup |
| `POST` | `/api/v1/analyze` | Analisis satu teks, body `{"text": "..."}` |
| `GET` | `/api/v1/fetch-and-analyze?keyword=BBM&days=30&limit=50` | Ambil komentar dari Verosight lalu dianalisis (default `keyword` di kode adalah `Asing`, jadi set `keyword=BBM` secara eksplisit) |

```bash
curl -X POST http://localhost:8003/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "BBM naik terus, rakyat kecil jangan dibebani"}'
```

```json
{"text": "BBM naik terus, rakyat kecil jangan dibebani", "label": "NEGATIVE", "confidence": 0.3662,
 "scores": {"POSITIVE": 0.2199, "NEGATIVE": 0.2506, "NEUTRAL": 0.2139}}
```

`scores` = kemiripan tertinggi teks ke kalimat jangkar tiap label; `confidence` = skor label terpilih dibagi total ketiga skor.

---

## ⚙️ Konfigurasi (`.env`)

| Variabel | Default | Keterangan |
|---|---|---|
| `VEROSIGHT_API_KEY` | – | API key Verosight (wajib untuk data asli) |
| `VEROSIGHT_BASE_URL` | `https://api.verosight.com` | Base URL API |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Model embedding untuk V2 |

---

## 📁 Struktur

```
├── main.py                     # V1: CLI (analyze / comments / serve)
├── api/server.py               # V1: FastAPI
├── model/
│   ├── lexicon.py              # V1: kamus kata positif/negatif, negasi, penguat
│   └── analyzer.py             # V1: preprocessing teks + analisis batch + ringkasan
├── data/fetch_data.py          # V1: ambil data Verosight, fallback 50 komentar contoh
├── app/                        # V2
│   ├── main.py                 #   FastAPI (model dimuat sekali saat startup)
│   ├── config.py               #   baca .env (pydantic-settings)
│   ├── schemas/sentiment.py    #   model request/response
│   └── services/
│       ├── sentiment_engine.py #   SBERT + kalimat jangkar + cosine similarity
│       └── verosight_client.py #   client async Verosight
├── .env.example
└── requirements.txt
```

---

## 🛡️ Keamanan

`.env` sudah masuk `.gitignore`. Jangan pernah commit API key atau menuliskannya langsung di kode.
