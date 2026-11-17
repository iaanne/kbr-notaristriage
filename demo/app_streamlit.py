# notriage KB — pendamping notaris/PPAT untuk orang awam.
# UI web terang ala Lexa AI: latar putih, konten di tengah, tanpa sidebar terbuka.
# Penalaran OWL/SWRL dijalankan Pellet di Protégé;
# berkas ini dan notaris/chatbot.py hanya membaca fakta dari ontology.
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
AKAR = Path(__file__).resolve().parent.parent
if str(AKAR) not in sys.path:
    sys.path.insert(0, str(AKAR))

from notaris import chatbot
from notaris.ontology import muat_ontology, nama_lokal

st.set_page_config(
    page_title="Notriage KB",
    page_icon="\u2696\ufe0f",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def _css() -> str:
    root_gelap = """
:root {
  --bg: #14110d;
  --panel: #1d1a15;
  --panel2: #221e18;
  --line: #2d2820;
  --line2: #3a342a;
  --ink: #ece4d6;
  --muted: #a39884;
  --accent: #c9a25e;
  --accent-btn: #c9a25e;
  --accent-contrast: #14110d;
  --accent-strong: #b8924f;
  --accent-soft: rgba(201, 162, 94, 0.14);
  --red: #cf7a58;
  --ok: #c9a25e;
  --none: #6e675a;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
}
"""
    root_terang = """
:root {
  --bg: #f5f5f2;
  --panel: #ffffff;
  --panel2: #eceae4;
  --line: #e0ddd4;
  --line2: #cbc7ba;
  --ink: #29241c;
  --muted: #6f6a5e;
  --accent: #8f6f1c;
  --accent-btn: #c9a25e;
  --accent-contrast: #14110d;
  --accent-strong: #b08a3e;
  --accent-soft: rgba(201, 162, 94, 0.16);
  --red: #b3402a;
  --ok: #b08a3e;
  --none: #a39e8f;
  --shadow: 0 1px 3px rgba(41, 36, 28, 0.09);
}
"""
    shared = """
.stApp { background: var(--bg); color: var(--ink); }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
/* kendali buka-tutup sidebar harus tetap terlihat meski header disembunyikan */
[data-testid="stExpandSidebarButton"] { visibility: visible !important; }
[data-testid="stExpandSidebarButton"] button,
[data-testid="stExpandSidebarButton"] svg { color: var(--ink); fill: var(--ink); }
[data-testid="stExpandSidebarButton"] button:hover { background: var(--accent-soft); }
.block-container { padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1180px; }

html, body, [class*="css"], .stMarkdown, p, div, span, label, input, textarea, button {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stMarkdown div { color: var(--ink); }

/* Strip bawah (fixed chat input): ikut var(--bg), matikan gradient bawaan Streamlit */
section[data-testid="stMain"] { background: transparent !important; }
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
  background: var(--bg) !important; box-shadow: none !important; border: none !important;
}
[data-testid="stBottom"] > *, [data-testid="stBottomBlockContainer"] > * { background: transparent !important; }
[data-testid="stBottom"]::before, [data-testid="stBottom"]::after,
[data-testid="stBottomBlockContainer"]::before, [data-testid="stBottomBlockContainer"]::after {
  background: none !important; display: none !important;
}
[data-testid="stChatInput"] > div { background: transparent !important; }

/* Toggle tema, melayang di pojok kanan atas */
div.st-key-btn-tema { position: fixed; top: 0.55rem; right: 0.75rem; z-index: 1000; height: 0; overflow: visible; }
div.st-key-btn-tema button {
  border-radius: 999px !important; padding: 0.22rem 0.85rem !important; font-size: 0.78rem !important;
  box-shadow: var(--shadow) !important; background: var(--panel) !important; color: var(--ink) !important;
  border: 1px solid var(--line2) !important; min-height: 0 !important; height: auto !important;
}
div.st-key-btn-tema button:hover { border-color: var(--accent-btn) !important; color: var(--accent) !important; }

.nt-brand { display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.9rem; }
.nt-brand-ico {
  width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
  background: var(--accent-soft); display: flex; align-items: center;
  justify-content: center; font-size: 1.25rem;
}
.nt-brand-nama { font-size: 1.02rem; font-weight: 700; color: var(--ink); line-height: 1.15; letter-spacing: -0.01em; }
.nt-brand-sub { font-size: 0.72rem; color: var(--muted); margin-top: 0.12rem; }
.nt-side-label {
  font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin: 1rem 0 0.4rem 0;
}
.nt-sesi-time { color: var(--muted); font-size: 0.72rem; margin: -0.3rem 0 0.5rem 0.2rem; }

/* Header */
.nt-kicker { font-size: 0.7rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--accent); font-weight: 700; }
.nt-title { font-size: 1.7rem; line-height: 1.25; margin: 0.4rem 0 0.25rem 0; color: var(--ink); font-weight: 700; letter-spacing: -0.01em; }
.nt-sub { color: var(--muted); font-size: 0.92rem; margin-bottom: 1.1rem; }

/* Hero (tampilan kosong) */
.nt-hero { text-align: center; padding: 6.5vh 0 2.2vh 0; }
.nt-hero-ico {
  width: 64px; height: 64px; margin: 0 auto 1rem auto; border-radius: 18px;
  background: var(--accent-soft); display: flex; align-items: center;
  justify-content: center; font-size: 1.9rem;
}
.nt-hero-title { font-size: 1.75rem; font-weight: 700; color: var(--ink); letter-spacing: -0.015em; }
.nt-hero-sub { color: var(--muted); font-size: 0.93rem; max-width: 520px; margin: 0.5rem auto 0 auto; line-height: 1.55; }

.nt-sug {
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 0.85rem 0.95rem; margin-bottom: 0.35rem; text-align: left;
  box-shadow: var(--shadow); transition: border-color 0.15s ease;
  height: 150px; display: flex; flex-direction: column; overflow: hidden;
}
.nt-sug:hover { border-color: var(--accent-btn); }
.nt-sug-ico {
  width: 30px; height: 30px; border-radius: 8px; background: var(--accent-soft);
  display: flex; align-items: center; justify-content: center; font-size: 0.95rem; margin-bottom: 0.45rem; flex-shrink: 0;
}
.nt-sug-judul { font-weight: 600; color: var(--ink); font-size: 0.9rem; }
.nt-sug-desc { color: var(--muted); font-size: 0.78rem; line-height: 1.45; margin-top: 0.18rem; flex: 1; }

/* Ikhtisar peraturan */
.nt-ikh-judul { color: var(--ink); font-size: 0.95rem; font-weight: 600; }
.nt-ikh-meta { color: var(--accent); font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; margin-top: 0.25rem; }
.nt-ikh-kasus { color: var(--muted); font-size: 0.8rem; margin-top: 0.45rem; }

/* Badge & chips */
.nt-badge {
  display: inline-block; padding: 0.28rem 0.7rem; border-radius: 999px;
  border: 1px solid var(--line2); background: var(--panel);
  color: var(--ink); font-size: 0.8rem; margin-right: 0.35rem;
}
.nt-badge-accent { border-color: var(--accent-btn); color: var(--accent); background: var(--accent-soft); }

/* Panel kartu */
.nt-card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  padding: 1rem 1.1rem; margin-bottom: 0.75rem; box-shadow: var(--shadow);
}
.nt-card h4 {
  margin: 0 0 0.5rem 0; font-size: 0.7rem; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--muted); font-weight: 700;
}
.nt-kv { display: flex; justify-content: space-between; gap: 0.8rem; padding: 0.32rem 0; border-bottom: 1px dashed var(--line2); }
.nt-kv:last-child { border-bottom: none; }
.nt-k { color: var(--muted); font-size: 0.85rem; }
.nt-v { color: var(--ink); font-size: 0.9rem; text-align: right; }

.nt-doc {
  display: flex; align-items: center; gap: 0.55rem;
  padding: 0.45rem 0.6rem; border: 1px solid var(--line);
  border-radius: 10px; margin: 0.3rem 0; font-size: 0.85rem; background: var(--panel2);
}
.nt-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--red); flex-shrink: 0; }
.nt-dot-ok { background: var(--ok); }
.nt-dot-none { background: var(--none); }

.nt-dasar { font-size: 0.75rem; color: var(--muted); padding: 0.18rem 0; }
.nt-disclaimer {
  color: var(--muted); font-size: 0.72rem; border-top: 1px solid var(--line);
  padding-top: 0.6rem; margin-top: 1rem;
}

/* Footer di bawah input */
.nt-foot { text-align: center; font-size: 0.76rem; color: var(--muted); margin-top: 0.55rem; line-height: 1.55; }
.nt-foot b { color: var(--ink); }

/* Tombol */
.stButton button {
  background: var(--panel); color: var(--ink); border: 1px solid var(--line2);
  border-radius: 10px; font-weight: 500; box-shadow: var(--shadow);
}
.stButton button:hover { border-color: var(--accent-btn); color: var(--accent); background: var(--panel); }
div.stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--accent-btn) !important; color: var(--accent-contrast) !important;
  border: 1px solid var(--accent-btn) !important; box-shadow: var(--shadow);
}
div.stButton > button[data-testid="stBaseButton-primary"]:hover { background: var(--accent-strong) !important; border-color: var(--accent-strong) !important; color: var(--accent-contrast) !important; }
div.stButton > button[data-testid="stBaseButton-secondary"] {
  background: var(--panel) !important; color: var(--ink) !important; border: 1px solid var(--line2) !important;
}

/* Chat */
[data-testid="stChatMessage"] { background: transparent; border: none; padding: 0.35rem 0; }
[data-testid="stChatMessageContent"] {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: 0.7rem 0.9rem; color: var(--ink);
  box-shadow: var(--shadow);
}
[data-testid="stChatInput"] {
  max-width: 720px; margin: 1.4rem auto 0.35rem auto !important;
  border: 1px solid var(--line2) !important; border-radius: 14px !important;
  background: var(--panel) !important; box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18) !important; padding: 0 !important;
}
[data-testid="stChatInput"] > div { flex-direction: row !important; align-items: center !important; gap: 0.3rem; padding: 0.3rem 0.45rem !important; }
[data-testid="stChatInput"] > div > div { flex-direction: row !important; align-items: center !important; gap: 0.3rem; background: transparent !important; }
[data-testid="stChatInput"] > div > div > div:first-child { flex: 1 1 auto !important; min-width: 0 !important; }
[data-testid="stChatInput"] > div > div > div:last-child { flex: 0 0 auto !important; align-items: center !important; justify-content: flex-end !important; height: auto !important; }
[data-testid="stChatInput"] > div > div > div:last-child > div:first-child { display: none !important; }
[data-testid="stChatInput"] textarea {
  background: transparent !important; color: var(--ink) !important;
  border: none !important; border-radius: 0 !important;
  caret-color: var(--ink) !important;
  height: 2.4rem; line-height: 1.4;
  padding: 0.55rem 0.75rem !important;
  margin: 0 !important; min-height: 0 !important; max-height: 7.5rem !important;
  box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; opacity: 1 !important; }
[data-testid="stChatInput"] div:not([data-testid="stChatInputSubmitButton"]) { background: transparent !important; }
[data-testid="stChatInputSubmitButton"] { background: var(--accent-btn) !important; border-radius: 10px !important; border: none !important; color: var(--accent-contrast) !important; }
[data-testid="stChatInputSubmitButton"]:hover { background: var(--accent-strong) !important; }
[data-testid="stChatInput"] [data-testid="stChatInputSecondary"] { display: none; }
</style>
"""
    root = root_gelap if st.session_state.get("tema", "terang") == "gelap" else root_terang
    return "<style>" + root + shared

CSS = _css()

st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- state
for key, default in [
    ("messages", []),
    ("stage", "idle"),          # idle -> slots -> done
    ("case_iri", None),
    ("slot_index", 0),
    ("slot_jawaban", {}),
    ("info", None),
    ("halaman", "chat"),        # chat | ikhtisar
]:
    if key not in st.session_state:
        st.session_state[key] = default

engine = "Ollama lokal (llama3)" if chatbot.llm_tersedia() else "Mode terstruktur (LLM tidak merespons)"

SESI_DIR = AKAR / "data" / "sesi"


def judul_sesi() -> str:
    info = st.session_state.get("info")
    if info and info.get("label"):
        return info["label"]
    for m in st.session_state.messages:
        if m["role"] == "user":
            teks = m["content"].strip()
            return (teks[:60] + "…") if len(teks) > 60 else teks
    return "Sesi tanpa keperluan"


def _slug(teks: str) -> str:
    teks = re.sub(r"[^a-z0-9]+", "-", teks.lower()).strip("-")
    return (teks[:48] or "sesi").strip("-")


def simpan_sesi() -> str | None:
    if not st.session_state.messages:
        return None
    SESI_DIR.mkdir(parents=True, exist_ok=True)
    judul = judul_sesi()
    waktu = datetime.now()
    nama = f"{_slug(judul)}-{waktu.strftime('%Y%m%d-%H%M%S')}.json"
    payload = {
        "title": judul,
        "saved_at": waktu.strftime("%Y-%m-%d %H:%M:%S"),
        "messages": st.session_state.messages,
        "info": st.session_state.info,
    }
    (SESI_DIR / nama).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return nama


def sesi_tersimpan() -> list[dict]:
    if not SESI_DIR.exists():
        return []
    keluar = []
    for berkas in sorted(SESI_DIR.glob("*.json"), reverse=True)[:12]:
        try:
            data = json.loads(berkas.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_file"] = berkas.name
        keluar.append(data)
    return keluar


def muat_sesi(nama_file: str) -> dict | None:
    jalur = SESI_DIR / nama_file
    if not jalur.exists() or jalur.parent != SESI_DIR:
        return None
    try:
        return json.loads(jalur.read_text(encoding="utf-8"))
    except Exception:
        return None


def waktu_relatif(stempel: str) -> str:
    try:
        t = datetime.strptime(stempel, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return stempel[:16]
    menit = int((datetime.now() - t).total_seconds() // 60)
    if menit < 1:
        return "baru saja"
    if menit < 60:
        return f"{menit} menit lalu"
    jam = menit // 60
    if jam < 24:
        return f"{jam} jam lalu"
    return f"{jam // 24} hari lalu"


# ---------------------------------------------------------------- chat
def dorong(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})


def selesaikan_kasus(iri, jawaban_slot):
    iri = chatbot.selaras(iri, jawaban_slot)
    info = chatbot.ground(iri)
    st.session_state.info = info
    st.session_state.stage = "done"
    if info is None:
        dorong("assistant", "Datanya tidak ketemu di ontologi. Ceritakan ulang dari awal, atau tekan Sesi baru.")
        return
    dorong("assistant", chatbot.jawab(f"Ringkas hasil triase untuk keperluan: {info['label']}.", info)
           + ("\n\n📚 **Referensi** (dari ontologi):\n" + "\n".join(f"• {s}" for s in info["dasar"])
              if info["dasar"] else ""))
    if "saved_file" not in st.session_state:
        st.session_state.saved_file = simpan_sesi()


def jawab_sebagai_user(teks: str):
    """State machine: idle -> slots -> done."""
    teks = teks.strip()
    if not teks:
        return

    dorong("user", teks)

    if st.session_state.stage == "idle":
        iri = chatbot.deteksi(teks)
        if iri is None:
            dorong("assistant", "Keperluan itu belum saya kenali. Coba pakai kata yang lebih umum: 'jual tanah', 'waris', 'hibah', 'bikin PT', 'wasiat', atau 'fidusia'.")
            return
        st.session_state.case_iri = iri
        st.session_state.stage = "slots"
        st.session_state.slot_index = 0
        st.session_state.slot_jawaban = {}
        dari_kandidat = chatbot.kandidat_kasus()[iri]["label"]
        slot = chatbot.slot_untuk(iri)
        if not slot:
            selesaikan_kasus(iri, {})
            return
        dorong("assistant", f"Terdeteksi: **{dari_kandidat}**. Beberapa pertanyaan dulu supaya arahannya tepat.")
        dorong("assistant", f"{slot[0][1]} *(ya/tidak, atau angka)*")
        return

    if st.session_state.stage == "slots":
        iri = st.session_state.case_iri
        slot = chatbot.slot_untuk(iri)
        idx = st.session_state.slot_index
        nama = slot[idx][0]
        st.session_state.slot_jawaban[nama] = teks
        idx += 1
        st.session_state.slot_index = idx
        if idx < len(slot):
            dorong("assistant", f"{slot[idx][1]} *(ya/tidak, atau angka)*")
            return
        selesaikan_kasus(iri, st.session_state.slot_jawaban)
        return

    # done: tanya jawab bebas, tetap di-grounding ke fakta kasus
    info = st.session_state.info
    dorong("assistant", chatbot.jawab(teks, info))


# ---------------------------------------------------------------- data aturan
def data_ikhtisar() -> list[dict]:
    """Daftar aturan ber-`:sumber` dan kasus yang mendasarinya, dibaca dari ontologi."""
    g = muat_ontology()
    P = ("PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#> "
         "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ")
    hasil = []
    for aturan, sumber in g.query(P + "SELECT ?a ?s WHERE { ?a :sumber ?s . } ORDER BY ?a"):
        tipe = [nama_lokal(r[0]) for r in g.query(P + f"SELECT ?t WHERE {{ <{aturan}> a ?t . }}")
                if nama_lokal(r[0]) != "NamedIndividual"]
        kasus = [str(r[1]) for r in g.query(
            P + f"SELECT ?k ?l WHERE {{ ?k :dasarKasus <{aturan}> ; rdfs:label ?l . }} ORDER BY ?l")]
        hasil.append({
            "nama": nama_lokal(aturan),
            "tipe": tipe[0] if tipe else "AturanHukum",
            "sumber": str(sumber),
            "kasus": kasus,
        })
    return hasil


# ---------------------------------------------------------------- sesi yang dibuka
view = st.session_state.get("view")
sesi_view = muat_sesi(view) if view else None

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div class="nt-brand">'
        '<div class="nt-brand-ico">\u2696\ufe0f</div>'
        '<div><div class="nt-brand-nama">Notriage KB</div>'
        '<div class="nt-brand-sub">Pendamping notaris &amp; PPAT</div></div></div>',
        unsafe_allow_html=True,
    )

    if st.button("\uff0b Percakapan Baru", type="primary", use_container_width=True, key="btn-sesi-baru"):
        simpan_sesi()
        for key in ["messages", "stage", "case_iri", "slot_index", "slot_jawaban", "info", "saved_file", "view", "halaman"]:
            st.session_state.pop(key, None)
        st.session_state.halaman = "chat"
        st.rerun()

    if st.button("\U0001f4ca Ikhtisar Peraturan", type="secondary", use_container_width=True, key="btn-ikhtisar"):
        st.session_state.halaman = "ikhtisar"
        st.session_state.pop("view", None)
        st.rerun()

    st.markdown('<div class="nt-side-label">Percakapan terakhir</div>', unsafe_allow_html=True)
    tersimpan = sesi_tersimpan()
    if not tersimpan:
        st.markdown('<div class="nt-dasar">Belum ada sesi tersimpan.</div>', unsafe_allow_html=True)
    for sesi in tersimpan:
        judul = sesi.get("title", "Sesi")
        aktif = view == sesi["_file"]
        label = ("\u25cf " if aktif else "\U0001f5ea ") + judul
        if st.button(label, key=f"buka-{sesi['_file']}", use_container_width=True):
            st.session_state.halaman = "chat"
            st.session_state.view = sesi["_file"]
            st.rerun()
        st.markdown(f'<div class="nt-sesi-time">{waktu_relatif(sesi.get("saved_at", ""))}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="nt-dasar" style="margin-top:0.8rem">Mesin jawab: {engine}</div>', unsafe_allow_html=True)
    st.markdown('<div class="nt-dasar">Sumber: ontologi T-Box + A-Box + 8 aturan SWRL (Pellet, Protégé).</div>', unsafe_allow_html=True)
    st.markdown('<div class="nt-disclaimer">Arahan awal, bukan pengganti Notaris/PPAT. Biaya dan waktu hanya perkiraan umum.</div>', unsafe_allow_html=True)

# ------------------------------------------------------- toggle tema
_tema = st.session_state.get("tema", "terang")
if st.button("🌙 Gelap" if _tema == "terang" else "☀️ Terang", key="btn-tema"):
    st.session_state.tema = "gelap" if _tema == "terang" else "terang"
    st.rerun()

# ---------------------------------------------------------------- halaman
if st.session_state.halaman == "ikhtisar":
    st.markdown('<div class="nt-kicker">Ikhtisar Peraturan</div>', unsafe_allow_html=True)
    st.markdown('<div class="nt-title">Dasar hukum yang dipakai sistem</div>', unsafe_allow_html=True)
    st.markdown('<div class="nt-sub">Daftar aturan yang dirujuk ontologi, beserta kasus yang mendasarinya.</div>', unsafe_allow_html=True)
    for item in data_ikhtisar():
        kasus = ", ".join(item["kasus"]) if item["kasus"] else "belum terpakai kasus"
        st.markdown(
            f'<div class="nt-card">'
            f'<div class="nt-ikh-judul">{item["sumber"]}</div>'
            f'<div class="nt-ikh-meta">{item["tipe"]} · {item["nama"]}</div>'
            f'<div class="nt-ikh-kasus">Dipakai kasus: {kasus}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if st.button("Kembali ke percakapan", use_container_width=True):
        st.session_state.halaman = "chat"
        st.rerun()
else:
    if not sesi_view and not st.session_state.messages:
        # Tampilan kosong ala Lexa: sambutan + kartu contoh yang bisa diklik.
        st.markdown(
            '<div class="nt-hero">'
            '<div class="nt-hero-ico">\u2696\ufe0f</div>'
            '<div class="nt-hero-title">Ada yang bisa saya bantu hari ini?</div>'
            '<div class="nt-hero-sub">Tanyakan keperluan notaris Anda, dan Notriage KB akan menunjukkan akta, instansi, dokumen, dan aturannya yang relevan.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        contoh = [
            ("\U0001f4b0", "Jual beli tanah", "PPAT, AJB, dan biaya jual beli tanah bersertifikat.", "mau jual tanah shm"),
            ("\U0001f3db\ufe0f", "Warisan belum balik nama", "Waris tanpa surat keterangan waris? Lengkapi dulu.", "mau jual tanah warisan belum balik nama"),
            ("\U0001f3e2", "Pendirian PT", "Syarat dan prosedur mendirikan PT perorangan.", "mau bikin PT perorangan sendiri"),
            ("\U0001f4dc", "Buat wasiat", "Cara membuat wasiat di notaris, saksi, dan syaratnya.", "mau buat wasiat"),
        ]
        _, tengah, _ = st.columns([1, 1.5, 1])
        with tengah:
            for i in range(0, len(contoh), 2):
                cols = st.columns(2, gap="medium")
                for col, (ikon, judul, desk, teks) in zip(cols, contoh[i:i + 2]):
                    with col:
                        st.markdown(
                            f'<div class="nt-sug">'
                            f'<div class="nt-sug-ico">{ikon}</div>'
                            f'<div class="nt-sug-judul">{judul}</div>'
                            f'<div class="nt-sug-desc">{desk}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        if st.button("Tanyakan", key=f"hero-{i}-{judul}", use_container_width=True):
                            jawab_sebagai_user(teks)
                            st.rerun()

    if sesi_view is not None or st.session_state.messages:
        col_chat, col_panel = st.columns([2.05, 1], gap="large")
        tampilkan_kolom = True
    else:
        col_chat = col_panel = None
        tampilkan_kolom = False

    # ------------------------------------------------------------ panel kanan
    if tampilkan_kolom:
      with col_panel:
        info = sesi_view["info"] if (sesi_view and sesi_view.get("info")) else st.session_state.info
        st.markdown('<div class="nt-card"><h4>Panel kasus</h4>', unsafe_allow_html=True)
        if info is None:
            st.markdown('<div class="nt-k" style="font-style:italic">Belum ada kasus terdeteksi. Ceritakan keperluan Anda di sebelah kiri.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="nt-badge nt-badge-accent">{info["label"]}</div>'
                f'<div class="nt-badge">{info["lembaga"]}</div><br><br>'
                f'<div class="nt-kv"><span class="nt-k">Instansi</span><span class="nt-v">{info["lembaga"]}</span></div>'
                f'<div class="nt-kv"><span class="nt-k">Akta / surat</span><span class="nt-v">{info["akta"]}</span></div>'
                f'<div class="nt-kv"><span class="nt-k">Status</span><span class="nt-v">{info["status"]}</span></div>'
                f'<div class="nt-kv"><span class="nt-k">Waktu</span><span class="nt-v">{info["waktu"]}</span></div>'
                f'<div class="nt-kv"><span class="nt-k">Biaya</span><span class="nt-v">{info["biaya"]}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<h4 style="margin-top:0.6rem">Sudah ada</h4>', unsafe_allow_html=True)
            for d in info["sudah"] or ["(belum dicatat di ontologi)"]:
                st.markdown(f'<div class="nt-doc"><span class="nt-dot nt-dot-ok"></span>{d}</div>', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-top:0.6rem">Masih kurang</h4>', unsafe_allow_html=True)
            for d in info["kurang"] or ["(belum dicatat di ontologi)"]:
                st.markdown(f'<div class="nt-doc"><span class="nt-dot nt-dot-none"></span>{d}</div>', unsafe_allow_html=True)
            if info["dasar"]:
                st.markdown('<h4 style="margin-top:0.6rem">Dasar</h4>', unsafe_allow_html=True)
                for s in info["dasar"]:
                    st.markdown(f'<div class="nt-dasar">§ {s}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="nt-dasar" style="margin-top:0.6rem"><b>Langkah:</b> {info["saran"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------ chat
    if tampilkan_kolom:
      with col_chat:
        if sesi_view is not None:
            st.markdown(
                f'<div class="nt-card"><h4>Riwayat sesi</h4>'
                f'<div class="nt-k">{sesi_view.get("title", "Sesi")}</div>'
                f'<div class="nt-dasar">Tersimpan {sesi_view.get("saved_at", "")}</div></div>',
                unsafe_allow_html=True,
            )
            for msg in sesi_view.get("messages", []):
                with st.chat_message(msg["role"], avatar="\U0001f464" if msg["role"] == "user" else "\u2696\ufe0f"):
                    st.markdown(msg["content"])
            if st.button("Tutup riwayat, kembali ke chat", use_container_width=True):
                st.session_state.pop("view", None)
                st.rerun()
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="\U0001f464" if msg["role"] == "user" else "\u2696\ufe0f"):
                    st.markdown(msg["content"])

    placeholder = "Tulis pertanyaan Anda di sini…" if st.session_state.stage == "idle" else (
        "Jawab pertanyaan di atas…" if st.session_state.stage == "slots" else "Tanya lanjutan soal kasus ini…"
    )
    if prompt := st.chat_input(placeholder):
        jawab_sebagai_user(prompt)
        st.rerun()
    st.markdown(
        '<div class="nt-foot"><b>Notriage KB bisa keliru — baca naskah peraturannya di sumber sebelum bertindak.</b><br>'
        'Notriage KB membantu menunjukkan instansi, akta, dokumen, dan aturan yang relevan beserta nomornya; '
        'bukan menyimpulkan hukumnya dan bukan pengganti Notaris/PPAT. Biaya dan waktu hanya perkiraan umum.</div>',
        unsafe_allow_html=True,
    )
