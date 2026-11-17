"""Lapisan RAG/chatbot di atas ontologi Notaris Triage.

Satu cara kerja:
1. Deteksi kasus dari kata kunci A-Box (bukan dari LLM).
2. Tempel fakta ground-truth dari A-Box (instansi, akta, dokumen, dll).
3. Ambil baris penjelasan bahasa awam yang relevan dari verbalized.jsonl.
4. LLM hanya merangkum fakta itu ke bahasa awam; LLM tidak boleh menambah fakta.
   Kalau LLM gagal atau iseng, jawaban turun ke format terstruktur dari A-Box.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
DEMO = AKAR / "demo"
if str(DEMO) not in sys.path:
    sys.path.insert(0, str(DEMO))

import app as demo  # demo/app.py: deteksi, ground_case, slot_untuk, selaras, kandidat_kasus

VERBALIZED = AKAR / "data" / "verbalized.jsonl"


def _baca_korpus() -> list[dict]:
    if not VERBALIZED.exists():
        return []
    keluar = []
    with open(VERBALIZED, encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if baris:
                keluar.append(json.loads(baris))
    return keluar


_korpus = None


def korpus() -> list[dict]:
    global _korpus
    if _korpus is None:
        _korpus = _baca_korpus()
    return _korpus


def konteks(iri: str, info: dict, maks: int = 14) -> list[str]:
    """Baris penjelasan yang relevan: cocokkan label kasus, akta, lembaga, status,
    dan dokumen yang disebut di fakta. Diurutkan agar relevan dulu."""
    korpus_ = korpus()
    if not korpus_:
        return []

    kata = set()
    for nilai in [info.get("label"), info.get("lembaga"), info.get("akta"), info.get("status")]:
        if nilai:
            kata |= {w for w in re.findall(r"[a-zA-Z]{4,}", str(nilai).lower())}
    for d in info.get("kurang", []) + info.get("sudah", []):
        kata |= {w for w in re.findall(r"[a-zA-Z]{4,}", str(d).lower())}
    nama_kasus = iri.rsplit("#", 1)[-1].lower()
    kata |= set(re.findall(r"[a-z]{4,}", nama_kasus))

    skor = []
    for baris in korpus_:
        teks = baris.get("teks", "").lower()
        identitas = baris.get("id", "").lower()
        s = sum(1 for k in kata if k in teks or k in identitas)
        if s:
            skor.append((s, baris))
    skor.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    return [b["teks"] for _, b in skor[:maks]]


def _fakta_sebagai_teks(info: dict) -> str:
    baris = [
        f"Keperluan: {info['label']}",
        f"Instansi: {info['lembaga']}",
        f"Akta/surat: {info['akta']}",
        f"Status: {info['status']}",
        f"Sudah ada: {', '.join(info['sudah']) or 'belum ada data'}",
        f"Masih kurang: {', '.join(info['kurang']) or 'tidak ada'}",
        f"Langkah berikutnya: {info['saran']}",
        f"Perkiraan waktu: {info['waktu']}",
        f"Perkiraan biaya: {info['biaya']}",
    ]
    if info.get("dasar"):
        baris.append("Dasar: " + "; ".join(info["dasar"]))
    return "\n".join(baris)


_PROMPT = """Kamu pendamping awam untuk layanan Notaris/PPAT. Jawab SINGKAT, maksimal 150 kata, dengan bahasa sehari-hari.

Aturan mutlak:
1. Hanya boleh memakai fakta yang tertulis di DATA dan KONTEKS di bawah. Jangan menambah instansi, akta, tarif, atau pasal yang tidak ada di sana.
2. Kalau pertanyaan user tidak terjawab dari DATA/KONTEKS, bilang terus terang "belum ada di data saya" dan sarankan tanya langsung ke pejabat yang tercantum.
3. Akhiri dengan satu kalimat: ini arahan awal, bukan pengganti Notaris/PPAT.
4. Jangan mengarang pasal atau nomor undang-undang.

DATA (dari ontologi, bukan dari ingatanmu):
{fakta}

KONTEKS (penjelasan bahasa awam yang relevan):
{konteks}

PERTANYAAN USER:
{pertanyaan}

JAWABAN:"""


def _ollama(prompt: str, *, timeout: int = 120) -> str:
    import urllib.request

    body = json.dumps(
        {
            "model": os.environ.get("NOTARIS_OLLAMA_MODEL", "llama3"),
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        os.environ.get("NOTARIS_OLLAMA_URL", "http://localhost:11434/api/generate"),
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")).get("response", "").strip()


def _openai_compatible(prompt: str, *, timeout: int = 120) -> str:
    import urllib.request

    key = os.environ.get("NOTARIS_LLM_API_KEY", "")
    base = os.environ.get("NOTARIS_LLM_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("NOTARIS_LLM_MODEL", "deepseek-chat")
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()


def llm_tersedia() -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen(
            os.environ.get("NOTARIS_OLLAMA_URL", "http://localhost:11434/api/tags").replace("/generate", "/tags"),
            timeout=3,
        ) as resp:
            return resp.status == 200
    except Exception:
        return bool(os.environ.get("NOTARIS_LLM_API_KEY"))


def jawab(pertanyaan: str, info: dict) -> str:
    """Jawaban bahasa awam yang di-grounding ke fakta A-Box. Selalu ada fallback."""
    if info is None:
        return (
            "Keperluan itu belum dikenali di data saya. Coba ceritakan dengan kata yang lebih umum, "
            "misalnya 'jual tanah', 'warisan', 'hibah', 'bikin PT', atau 'wasiat'."
        )
    p = _PROMPT.format(
        fakta=_fakta_sebagai_teks(info),
        konteks="\n".join(f"- {k}" for k in konteks(info["iri"], info)) or "- (tidak ada konteks tambahan)",
        pertanyaan=pertanyaan,
    )
    try:
        if os.environ.get("NOTARIS_LLM_API_KEY"):
            return _openai_compatible(p)
        return _ollama(p)
    except Exception:
        return jawaban_terstruktur(info)


def jawaban_terstruktur(info: dict) -> str:
    """Fallback tanpa LLM: format fakta A-Box apa adanya."""
    if info is None:
        return "Keperluan belum dikenali."
    bagian = [
        f"Keperluan: {info['label']}.",
        f"Instansi: {info['lembaga']}. Akta/surat: {info['akta']}. Status: {info['status']}.",
    ]
    if info["kurang"]:
        bagian.append("Yang masih kurang: " + ", ".join(info["kurang"]) + ".")
    bagian.append(f"Langkah berikutnya: {info['saran']}.")
    bagian.append(f"Perkiraan waktu: {info['waktu']}. Perkiraan biaya: {info['biaya']}.")
    bagian.append("Ini arahan awal, bukan pengganti Notaris/PPAT.")
    return " ".join(bagian)


def deteksi(cerita: str):
    return demo.deteksi(cerita)


kandidat_kasus = demo.kandidat_kasus


def slot_untuk(iri: str):
    return demo.slot_untuk(iri)


def selaras(iri: str, jawaban_slot: dict):
    return demo.selaras(iri, jawaban_slot)


def ground(iri: str):
    return demo.ground_case(iri)
