"""
The Holy Quran App - Qari Recitations (Hifz Made Easy)
Reads direct MP3 audio files from folder structure or cloud CDN fallback.
"""

import os
import re
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

# ---------------------------------------------------------------------------
# Path Configurations (Production & Render Friendly)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, "static")
CHAPTER_NAMES_ROOT = os.path.join(STATIC_ROOT, "Chapter Names")

# Local root folder (if running locally with unzipped folders)
QURAN_ROOT = r"D:\Web & AI\The Holy Quran App\QuranDownload"

PORT = int(os.environ.get("PORT", 8787))
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".ogg", ".aac"}

TAAWOOZ_FILE_STEM = "009000"
BISMILLAH_FILE_STEM = "001001"

TEST_SURAHS = {
    1: "Surah Al-Fatihah", 2: "Surah Al-Baqarah", 3: "Surah Aal-E-Imran", 4: "Surah An-Nisa",
    5: "Surah Al-Ma'idah", 6: "Surah Al-An'am", 7: "Surah Al-A'raf", 8: "Surah Al-Anfal",
    9: "Surah At-Tawbah", 10: "Surah Yunus", 11: "Surah Hud", 12: "Surah Yusuf",
    13: "Surah Ar-Ra'd", 14: "Surah Ibrahim", 15: "Surah Al-Hijr", 16: "Surah An-Nahl",
    17: "Surah Al-Isra", 18: "Surah Al-Kahf", 19: "Surah Maryam", 20: "Surah Ta-Ha",
    21: "Surah Al-Anbiya", 22: "Surah Al-Hajj", 23: "Surah Al-Mu'minun", 24: "Surah An-Nur",
    25: "Surah Al-Furqan", 26: "Surah Ash-Shu'ara", 27: "Surah An-Naml", 28: "Surah Al-Qasas",
    29: "Surah Al-Ankabut", 30: "Surah Ar-Rum", 31: "Surah Luqman", 32: "Surah As-Sajdah",
    33: "Surah Al-Ahzab", 34: "Surah Saba", 35: "Surah Fatir", 36: "Surah Ya-Sin",
    37: "Surah As-Saffat", 38: "Surah Sad", 39: "Surah Az-Zumar", 40: "Surah Ghafir",
    41: "Surah Fussilat", 42: "Surah Ash-Shura", 43: "Surah Az-Zukhruf", 44: "Surah Ad-Dukhan",
    45: "Surah Al-Jathiyah", 46: "Surah Al-Ahqaf", 47: "Surah Muhammad", 48: "Surah Al-Fath",
    49: "Surah Al-Hujurat", 50: "Surah Qaf", 51: "Surah Adh-Dhariyat", 52: "Surah At-Tur",
    53: "Surah An-Najm", 54: "Surah Al-Qamar", 55: "Surah Ar-Rahman", 56: "Surah Al-Waqi'ah",
    57: "Surah Al-Hadid", 58: "Surah Al-Mujadilah", 59: "Surah Al-Hashr", 60: "Surah Al-Mumtahanah",
    61: "Surah As-Saff", 62: "Surah Al-Jumu'ah", 63: "Surah Al-Munafiqun", 64: "Surah At-Taghabun",
    65: "Surah At-Talaq", 66: "Surah At-Tahrim", 67: "Surah Al-Mulk", 68: "Surah Al-Qalam",
    69: "Surah Al-Haqqah", 70: "Surah Al-Ma'arij", 71: "Surah Nuh", 72: "Surah Al-Jinn",
    73: "Surah Al-Muzzammil", 74: "Surah Al-Muddaththir", 75: "Surah Al-Qiyamah", 76: "Surah Al-Insan",
    77: "Surah Al-Mursalat", 78: "Surah An-Naba", 79: "Surah An-Nazi'at", 80: "Surah Abasa",
    81: "Surah At-Takwir", 82: "Surah Al-Infitar", 83: "Surah Al-Mutaffifin", 84: "Surah Al-Inshiqaq",
    85: "Surah Al-Buruj", 86: "Surah At-Tariq", 87: "Surah Al-A'la", 88: "Surah Al-Ghashiyah",
    89: "Surah Al-Fajr", 90: "Surah Al-Balad", 91: "Surah Ash-Shams", 92: "Surah Al-Layl",
    93: "Surah Ad-Duha", 94: "Surah Ash-Sharh", 95: "Surah At-Tin", 96: "Surah Al-Alaq",
    97: "Surah Al-Qadr", 98: "Surah Al-Bayyinah", 99: "Surah Az-Zalzalah", 100: "Surah Al-Adiyat",
    101: "Surah Al-Qari'ah", 102: "Surah At-Takathur", 103: "Surah Al-Asr", 104: "Surah Al-Humazah",
    105: "Surah Al-Fil", 106: "Surah Quraysh", 107: "Surah Al-Ma'un", 108: "Surah Al-Kawthar",
    109: "Surah Al-Kafirun", 110: "Surah An-Nasr", 111: "Surah Al-Masad", 112: "Surah Al-Ikhlas",
    113: "Surah Al-Falaq", 114: "Surah An-Nas",
}
JUZ_LABEL = "Juz 1 - 30"

SURAH_AYAH_COUNTS = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128,
    111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30,
    73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29,
    18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18,
    12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19,
    5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6
]

_BITRATE_SUFFIX_RE = re.compile(r"_\d+kbps$", re.IGNORECASE)

def display_qari_name(folder_name):
    name = _BITRATE_SUFFIX_RE.sub("", folder_name)
    cleaned = name.replace("_", " ").strip()
    return f"The Qari {cleaned}"

def list_qari_folders():
    if os.path.isdir(QURAN_ROOT):
        entries = [name for name in sorted(os.listdir(QURAN_ROOT)) if os.path.isdir(os.path.join(QURAN_ROOT, name))]
        if entries:
            return entries
    return ["Abdul_Basit_Murattal_192kbps", "Abdul_Basit_Mujawwad_128kbps", "Alafasy_128kbps", "Abu_Bakr_Shatri_128kbps"]

def get_audio_file_path(qari_folder, surah, ayah):
    surah_str = f"{int(surah):03d}"
    ayah_str = f"{int(ayah):03d}"
    filename = f"{surah_str}{ayah_str}.mp3"
    
    # 1. Local unzipped folder path: D:\...\QuranDownload\Qari_Folder\001001.mp3
    local_path = os.path.join(QURAN_ROOT, qari_folder, filename)
    if os.path.isfile(local_path):
        return local_path
        
    # 2. Local unzipped folder per surah: D:\...\QuranDownload\Qari_Folder\001\001001.mp3
    local_sub_path = os.path.join(QURAN_ROOT, qari_folder, surah_str, filename)
    if os.path.isfile(local_sub_path):
        return local_sub_path

    return None

def find_chapter_name_image(surah_number):
    try:
        n = int(surah_number)
    except (TypeError, ValueError):
        return None

    if not os.path.isdir(CHAPTER_NAMES_ROOT):
        return None

    exact_names = [f"{n}.png", f"{n:02d}.png", f"{n:03d}.png"]
    for name in exact_names:
        candidate = os.path.join(CHAPTER_NAMES_ROOT, name)
        if os.path.isfile(candidate):
            return candidate

    prefix_re = re.compile(rf"^0*{n}(?:\D|$)", re.IGNORECASE)
    try:
        for name in sorted(os.listdir(CHAPTER_NAMES_ROOT)):
            if not name.lower().endswith(".png"):
                continue
            stem = os.path.splitext(name)[0]
            if prefix_re.match(stem):
                candidate = os.path.join(CHAPTER_NAMES_ROOT, name)
                if os.path.isfile(candidate):
                    return candidate
    except OSError:
        return None

    return None

def safe_join(root, *parts):
    target = os.path.normpath(os.path.join(root, *parts))
    root_norm = os.path.normpath(root)
    if not target.startswith(root_norm):
        return None
    return target

# Front-end HTML defined in INDEX_HTML string (Keep original html code)
INDEX_HTML = """..."""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[server]", fmt % args)

    def send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path in ("/", "/index.html"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path.startswith("/static/"):
            filename = path[len("/static/"):]
            file_path = safe_join(STATIC_ROOT, filename)
            if file_path and os.path.isfile(file_path):
                ctype, _ = mimetypes.guess_type(file_path)
                try:
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", ctype or "image/jpeg")
                    self.send_header("Content-Length", str(len(file_data)))
                    self.end_headers()
                    self.wfile.write(file_data)
                    return
                except OSError:
                    self.send_error(500, "Error reading static file")
                    return
            else:
                self.send_error(404, "Static file not found")
                return

        if path == "/api/surahs":
            surahs = []
            for n in sorted(TEST_SURAHS):
                image_path = find_chapter_name_image(n)
                surahs.append({
                    "number": n,
                    "name": TEST_SURAHS[n],
                    "image_url": f"/chapter-name-image?surah={n}" if image_path else None,
                })
            self.send_json({"surahs": surahs, "juz": JUZ_LABEL})
            return

        if path == "/chapter-name-image":
            qs = parse_qs(parsed.query)
            surah = qs.get("surah", [""])[0]
            image_path = find_chapter_name_image(surah)
            if not image_path:
                self.send_error(404, "Chapter PNG not found")
                return
            try:
                with open(image_path, "rb") as f:
                    image_data = f.read()
            except OSError:
                self.send_error(404, "Chapter PNG unreadable")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(image_data)))
            self.end_headers()
            self.wfile.write(image_data)
            return

        if path == "/api/opening":
            self.send_json({
                "available": True,
                "taawooz_url": "https://everyayah.com/data/Abdul_Basit_Murattal_192kbps/001001.mp3",
                "bismillah_url": "https://everyayah.com/data/Abdul_Basit_Murattal_192kbps/001001.mp3",
            })
            return

        if path == "/api/ayah_count":
            qs = parse_qs(parsed.query)
            surah = int(qs.get("surah", ["1"])[0])
            s_idx = surah - 1
            max_cnt = SURAH_AYAH_COUNTS[s_idx] if 0 <= s_idx < len(SURAH_AYAH_COUNTS) else 7
            self.send_json({"max_ayah": max_cnt})
            return

        if path == "/api/sequence":
            qs = parse_qs(parsed.query)
            surah = qs.get("surah", [""])[0]
            ayah = int(qs.get("ayah", ["1"])[0])
            times = int(qs.get("times", ["21"])[0])

            qaris = list_qari_folders()
            seq = []
            
            for i in range(times):
                q_folder = qaris[i % len(qaris)]
                local_file = get_audio_file_path(q_folder, surah, ayah)
                
                if local_file:
                    audio_url = f"/audio?qari={q_folder}&surah={surah}&ayah={ayah}"
                else:
                    # Online production stream from CDN matching unzipped filenames
                    surah_formatted = f"{int(surah):03d}"
                    ayah_formatted = f"{int(ayah):03d}"
                    audio_url = f"https://everyayah.com/data/{q_folder}/{surah_formatted}{ayah_formatted}.mp3"

                seq.append({
                    "qari": display_qari_name(q_folder),
                    "url": audio_url
                })

            self.send_json({"sequence": seq})
            return

        if path == "/audio":
            qs = parse_qs(parsed.query)
            qari = qs.get("qari", [""])[0]
            surah = qs.get("surah", [""])[0]
            ayah = qs.get("ayah", [""])[0]

            audio_file = get_audio_file_path(qari, surah, ayah)
            if not audio_file or not os.path.isfile(audio_file):
                self.send_error(404, "Audio file not found")
                return

            try:
                with open(audio_file, "rb") as f:
                    data = f.read()
                ctype, _ = mimetypes.guess_type(audio_file)
                self.send_response(200)
                self.send_header("Content-Type", ctype or "audio/mpeg")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                self.send_error(500, f"Error reading audio file: {e}")
                return

        self.send_error(404, "Not Found")

def run():
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, Handler)
    print(f"Starting server on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
