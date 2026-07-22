import json
import os
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.verosight.com"
API_KEY = os.getenv("VEROSIGHT_API_KEY", "YOUR_VEROSIGHT_API_KEY_HERE")
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(DATA_DIR, "comments_cache.json")

SAMPLE_COMMENTS = [
    {"text": "BBM naik lagi, rakyat makin sengsara", "platform": "twitter", "date": "2026-07-15"},
    {"text": "Kenaikan BBM kali ini cukup wajar mengingat harga minyak dunia", "platform": "facebook", "date": "2026-07-15"},
    {"text": "Pemerintah harusnya turunkan harga BBM bukan naikin", "platform": "twitter", "date": "2026-07-14"},
    {"text": "Alhamdulillah harga BBM stabil tahun ini, semoga terus begini", "platform": "instagram", "date": "2026-07-14"},
    {"text": "Bensin mahal gini gowes aja ah", "platform": "twitter", "date": "2026-07-13"},
    {"text": "Ekonomi susah BBM naik terus, rakyat kecil yang rugi", "platform": "facebook", "date": "2026-07-13"},
    {"text": "Kebijakan BBM sekarang sudah tepat sasaran", "platform": "twitter", "date": "2026-07-12"},
    {"text": "Mogok massal karena BBM naik, pemerintah tidak becus", "platform": "twitter", "date": "2026-07-12"},
    {"text": "BBM bersubsidi tepat sasaran, orang kaya gak usah ikut nikmatin", "platform": "instagram", "date": "2026-07-11"},
    {"text": "Antrian BBM dimana-mana, panic buying lagi", "platform": "facebook", "date": "2026-07-11"},
    {"text": "Saya setuju BBM naik asal subsidi tepat sasaran", "platform": "twitter", "date": "2026-07-10"},
    {"text": "Harga BBM turun dikit aja langsung disambut gembira", "platform": "instagram", "date": "2026-07-10"},
    {"text": "BBM semakin tidak terjangkau, gaji UMR mana cukup", "platform": "facebook", "date": "2026-07-09"},
    {"text": "Kendaraan listrik solusi hindari mahalnya BBM", "platform": "twitter", "date": "2026-07-09"},
    {"text": "Kebijakan energi pemerintah patut diapresiasi, BBM terkendali", "platform": "instagram", "date": "2026-07-08"},
    {"text": "BBM naik terus, ongkos angkutan ikut naik, semua pada naik", "platform": "facebook", "date": "2026-07-08"},
    {"text": "Pertamina tolong perbaiki kualitas BBM jangan cuma naikin harga", "platform": "twitter", "date": "2026-07-07"},
    {"text": "Syukur BBM masih bisa dijangkau, semoga tidak naik lagi", "platform": "instagram", "date": "2026-07-07"},
    {"text": "Demo BBM dimana-mana, pemerintah dengar suara rakyat", "platform": "facebook", "date": "2026-07-06"},
    {"text": "Pemerintah janji BBM tidak naik, ternyata naik juga", "platform": "twitter", "date": "2026-07-06"},
    {"text": "BBM naik itu menyakitkan tapi mau gimana lagi", "platform": "twitter", "date": "2026-07-05"},
    {"text": "Konversi BBM ke gas solusi cerdas buat transportasi", "platform": "instagram", "date": "2026-07-05"},
    {"text": "Harga minyak dunia turun tapi BBM kok gak turun", "platform": "facebook", "date": "2026-07-04"},
    {"text": "Terima kasih pemerintah BBM tidak jadi naik", "platform": "twitter", "date": "2026-07-04"},
    {"text": "Biarin aja BBM naik, yang penting bisa beli", "platform": "instagram", "date": "2026-07-03"},
    {"text": "BBM naik bikin inflasi makin parah", "platform": "facebook", "date": "2026-07-03"},
    {"text": "Yang kaya tambah kaya, yang miskin tambah menderita karena BBM", "platform": "twitter", "date": "2026-07-02"},
    {"text": "BBM tidak naik itu kabar baik buat rakyat", "platform": "instagram", "date": "2026-07-02"},
    {"text": "Pemerintah harus berani menaikkan BBM demi masa depan energi", "platform": "twitter", "date": "2026-07-01"},
    {"text": "Subsidi BBM dinikmati orang kaya, perlu evaluasi", "platform": "facebook", "date": "2026-07-01"},
    {"text": "BBM berkualitas harga terjangkau, Pertamina hebat", "platform": "instagram", "date": "2026-06-30"},
    {"text": "Bensin premium sudah hilang, sekarang harus beli pertalite", "platform": "twitter", "date": "2026-06-30"},
    {"text": "Harga BBM per hari ini masih stabil, semoga awet", "platform": "facebook", "date": "2026-06-29"},
    {"text": "Saya dukung penuh kebijakan BBM pemerintah demi kemandirian energi", "platform": "instagram", "date": "2026-06-29"},
    {"text": "Rakyat butuh harga BBM yang adil, bukan yang murah", "platform": "twitter", "date": "2026-06-28"},
    {"text": "BBM naik terus, rakyat kecil jangan dibebani", "platform": "facebook", "date": "2026-06-28"},
    {"text": "Tolak kenaikan BBM, rakyat sudah cukup menderita", "platform": "twitter", "date": "2026-06-27"},
    {"text": "Minyak goreng mahal, BBM naik, apa lagi yang naik?", "platform": "facebook", "date": "2026-06-27"},
    {"text": "BBM pilihan tepat buat mobilitas sehari-hari", "platform": "instagram", "date": "2026-06-26"},
    {"text": "Harga BBM dunia naik, wajar kalau di Indonesia ikut naik", "platform": "twitter", "date": "2026-06-26"},
    {"text": "Yang penting BBM lancar dan gak antri", "platform": "facebook", "date": "2026-06-25"},
    {"text": "BBM naik belum pernah ada solusi nyata buat rakyat", "platform": "twitter", "date": "2026-06-25"},
    {"text": "Indonesia kaya minyak tapi BBM mahal, aneh", "platform": "instagram", "date": "2026-06-24"},
    {"text": "Pemerintah perlu kaji ulang harga BBM setiap bulan", "platform": "facebook", "date": "2026-06-24"},
    {"text": "BBM naik dikit aja udah pada protes, gak pernah bersyukur", "platform": "twitter", "date": "2026-06-23"},
    {"text": "Kualitas BBM Pertamina bagus, harganya aja yang kurang bersahabat", "platform": "instagram", "date": "2026-06-23"},
    {"text": "BBM naik tanda ekonomi sedang tidak baik-baik saja", "platform": "facebook", "date": "2026-06-22"},
    {"text": "Bangga pake BBM dalam negeri, Pertamina jaya", "platform": "twitter", "date": "2026-06-22"},
    {"text": "BBM tidak naik itu hoax? tolong klarifikasi pemerintah", "platform": "facebook", "date": "2026-06-21"},
    {"text": "Harga BBM sekarang masuk akal, jangan dibandingkan dengan negara tetangga", "platform": "instagram", "date": "2026-06-21"},
]

def fetch_from_api(days=20, limit=50, keyword="BBM"):
    url = f"{API_BASE}/v1/analytics/trending?days={days}&limit={limit}&keyword={keyword}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "X-API-Key": API_KEY,
    })
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read()).get("data",{}).get("top_posts",[])
            return data, "api"
    except (HTTPError, URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[fetch_data] API error: {e}. Falling back to sample data.")
        return SAMPLE_COMMENTS, "sample"

def load_comments(days=20, limit=50, keyword="BBM", use_cache=True):
    # if use_cache and os.path.exists(CACHE_FILE):
    #     with open(CACHE_FILE, "r") as f:
    #         return json.load(f), "cache"
    comments, source = fetch_from_api(days, limit, keyword)
    if comments and source == "api":
        with open(CACHE_FILE, "w") as f:
            json.dump(comments, f, indent=2)
    elif not comments or source == "sample":
        comments = SAMPLE_COMMENTS
    return comments, source
