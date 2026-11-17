# Demo triase Notaris/PPAT untuk pengguna awam (penampil).
#
# Peran berkas ini: menampilkan hasil. Penalaran OWL dan SWRL dijalankan
# Pellet di dalam Protege, bukan di Python. Karena itu demo tidak menalar:
# ia membaca ontology via SPARQL, lalu memaparkan.
#
# Tidak ada daftar kata kunci, daftar kasus, maupun daftar slot yang ditulis
# di sini. Kata kunci kasus dibaca dari anotasi :kataKunci di A-Box
# (data/abox.ttl), dan pertanyaan slot dibaca dari badan aturan swrl:Imp.
#
# Jalankan: python3 app.py  (CLI)  |  python3 app.py --test  (uji skenario)
# Opsional Streamlit: streamlit run app_streamlit.py
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
if str(AKAR) not in sys.path:
    sys.path.insert(0, str(AKAR))

try:
    from rdflib import URIRef
    from notaris.ontology import (
        NS,
        label,
        muat_aturan,
        muat_ontology,
        nama_lokal,
        slot_dari_aturan,
    )
    from notaris.verbalisasi import PERTANYAAN_SLOT
except ImportError:
    print("Butuh rdflib: pip install --break-system-packages rdflib")
    sys.exit(1)

g = muat_ontology()          # T-Box (skema + aturan) dan A-Box (individu)
ATURAN = muat_aturan(g)      # R1..R8, dibaca dari ontology


def q(sparql):
    return list(g.query(sparql))


# --- Deteksi keperluan: baca :kataKunci tiap kasus dari A-Box --------------

def kandidat_kasus():
    """Semua kasus triase beserta label, prioritas, dan kata kuncinya."""
    Q = """
    PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?kasus ?label ?prioritas ?kunci WHERE {
      ?kasus a :KasusTriage ; rdfs:label ?label .
      OPTIONAL { ?kasus :prioritas ?prioritas . }
      OPTIONAL { ?kasus :kataKunci ?kunci . }
    }"""
    hasil = {}
    for kasus, lab, pri, kunci in q(Q):
        d = hasil.setdefault(str(kasus), {"label": str(lab), "prioritas": 0, "kunci": []})
        if pri is not None:
            d["prioritas"] = int(pri)
        if kunci is not None:
            d["kunci"].append(str(kunci).lower())
    return hasil


def deteksi(cerita):
    """Kasus dengan kata kunci paling banyak cocok; seri diputus :prioritas."""
    teks = cerita.lower()
    skor = []
    for iri, d in kandidat_kasus().items():
        cocok = sum(1 for k in d["kunci"] if k and k in teks)
        if cocok:
            skor.append((cocok, d["prioritas"], iri))
    if not skor:
        return None
    skor.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return skor[0][2]


# --- Fakta kasus dari A-Box -------------------------------------------------

def ground_case(iri):
    """Fakta ground-truth satu kasus: instansi, akta, status, dokumen, saran."""
    Q = f"""
    PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?lembaga ?akta ?status ?saran ?waktu ?biaya WHERE {{
      <{iri}> :ditanganiOleh ?l ; :butuhAkta ?a ; :berstatus ?s ; :saranLangkah ?saran .
      ?l rdfs:label ?lembaga . ?a rdfs:label ?akta . ?s rdfs:label ?status .
      OPTIONAL {{ <{iri}> :perkiraanWaktu ?waktu . }}
      OPTIONAL {{ <{iri}> :perkiraanBiaya ?biaya . }}
    }}"""
    rows = q(Q)
    if not rows:
        return None

    def teks_dokumen(predikat):
        D = f"""
        PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?d WHERE {{ <{iri}> :{predikat} ?x . ?x rdfs:label ?d . }}"""
        return sorted({str(r[0]) for r in q(D)})

    dasar = sorted({
        str(r[0]) for r in q(f"""
        PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?sumber WHERE {{
          {{ <{iri}> :dasarKasus ?x . ?x :sumber ?sumber . }}
          UNION
          {{ <{iri}> :butuhAkta ?a . ?a :berdasarPada ?x . ?x :sumber ?sumber . }}
        }}""")
    })

    sudah = teks_dokumen("sudahPunyaDokumen")
    butuh = teks_dokumen("butuhDokumen")

    r = rows[0]
    return {
        "iri": iri,
        "label": label(g, URIRef(iri)),
        "lembaga": str(r[0]),
        "akta": str(r[1]),
        "status": str(r[2]),
        "saran": str(r[3]),
        "waktu": str(r[4] or "-"),
        "biaya": str(r[5] or "-"),
        "sudah": sudah,
        "kurang": [d for d in butuh if d not in sudah],
        "dasar": dasar,
    }


# --- Slot pertanyaan dari badan aturan SWRL --------------------------------

def aturan_untuk(iri):
    """Aturan yang badannya menyebut jenis keperluan kasus ini."""
    jenis = g.value(URIRef(iri), NS.punyaJenis)
    if jenis is None:
        return None
    for aturan in ATURAN.values():
        for atom in aturan.body:
            if atom.predikat == NS.punyaJenis and atom.argumen2 == jenis:
                return aturan
    return None


def slot_untuk(iri):
    """Slot yang harus dijawab pengguna, dibaca dari swrl:body."""
    aturan = aturan_untuk(iri)
    if aturan is None:
        return []
    return [
        (nama, PERTANYAAN_SLOT.get(nama, f"Pertanyaan untuk {nama}?"))
        for nama in slot_dari_aturan(aturan, g)
    ]


def _kunci(nilai):
    """Kunci pembanding netral: bool, angka, atau teks huruf kecil."""
    if isinstance(nilai, bool):
        return ("bool", nilai)
    s = str(nilai).strip().lower()
    if s in ("true", "ya", "sudah", "ada"):
        return ("bool", True)
    if s in ("false", "tidak", "belum"):
        return ("bool", False)
    try:
        return ("num", int(s))
    except ValueError:
        return ("str", s)


def selaras(iri, jawaban):
    """Pilih ulang kasus sejenis yang faktanya paling cocok dengan jawaban.

    Bukan penalaran DL, hanya pencocokan fakta yang sudah diassert, supaya
    demo tidak menampilkan kasus yang bertentangan dengan jawaban pengguna.
    """
    jenis = g.value(URIRef(iri), NS.punyaJenis)
    kandidat = list(g.subjects(NS.punyaJenis, jenis)) if jenis is not None else []
    if len(kandidat) <= 1:
        return URIRef(iri)

    def skor(k):
        s = 0
        for nama, val in jawaban.items():
            nyata = g.value(k, NS[nama])
            if nyata is None:
                continue
            s += 1 if _kunci(nyata) == _kunci(val) else -1
        return s

    return max(kandidat, key=lambda k: (skor(k), str(k)))


# --- Alur interaktif --------------------------------------------------------

def tanya_slot(iri):
    data = {}
    for nama, pertanyaan in slot_untuk(iri):
        print("BOT:", pertanyaan, "(sudah/belum, ya/tidak, atau angka)")
        j = input("Anda: ").strip().lower()
        if j == "batal":
            return None
        data[nama] = j
    return data


def cetak_hasil(info):
    print("\n----- HASIL TRIASE -----")
    print(f"Keperluan   : {info['label']}")
    print(f"Instansi    : {info['lembaga']}")
    print(f"Akta/surat  : {info['akta']}")
    print(f"Status      : {info['status']}")
    print("Dokumen yang sudah ada:")
    for d in info["sudah"] or ["(belum ada data)"]:
        print(f"  - {d}")
    print("Dokumen yang masih kurang:")
    for d in info["kurang"] or ["(tidak ada)"]:
        print(f"  - {d}")
    print(f"Langkah berikutnya: {info['saran']}")
    print(f"Perkiraan waktu : {info['waktu']}")
    print(f"Perkiraan biaya : {info['biaya']}")
    if info["dasar"]:
        print("Dasar hukum:")
        for s in info["dasar"]:
            print(f"  - {s}")
    print("Catatan: ini arahan awal, bukan pengganti Notaris/PPAT. Bawa ceklis ini saat datang.")
    print("------------------------\n")


def main():
    print("Layanan triase Notaris/PPAT.")
    print("Ceritakan keperluan dengan bahasa sehari-hari. Contoh: 'mau jual tanah warisan belum balik nama'.")
    cerita = input("Anda: ").strip()
    if not cerita:
        print("BOT: Cerita kosong. Ulangi.")
        return
    iri = deteksi(cerita)
    if iri is None:
        print("BOT: Keperluan belum dikenali. Ceritakan ulang dengan kata yang lebih umum.")
        print("     Contoh: 'mau jual tanah', 'warisan belum balik nama', 'mau bikin PT'.")
        return
    print(f"\nKebutuhan tercatat: {kandidat_kasus()[iri]['label']}.")
    if not slot_untuk(iri):
        print("BOT: Tidak ada pertanyaan tambahan untuk keperluan ini.\n")
    data = tanya_slot(iri)
    if data is None:
        print("BOT: Sesi dibatalkan.")
        return
    iri = selaras(iri, data)
    info = ground_case(iri)
    if info is None:
        print("BOT: Data tidak ditemukan di ontology. Ceritakan ulang.")
        return
    cetak_hasil(info)
    print("BOT: Ada yang kurang jelas? (tulis pertanyaan / 'selesai')")
    while True:
        j = input("Anda: ").strip().lower()
        if j in ("selesai", "cukup", "tidak", "ok", ""):
            print("BOT: Sesi selesai. Simpan hasil di atas untuk dibawa ke pejabat.")
            break
        print("BOT: Patokannya tetap ceklis di atas. Bawa dokumennya, tanyakan ke pejabat yang tercantum. ('selesai' untuk tutup)")


def test():
    kasus = [
        ("mau jual tanah shm", "kasus_jualbeli_shm"),
        ("mau jual tanah warisan belum balik nama", "kasus_waris_belumSKW"),
        ("ahli waris ribut tidak sepakat", "kasus_waris_sengketa"),
        ("mau hibah tanah ke anak", "kasus_hibah_tanah"),
        ("mau bikin pt perorangan sendiri", "kasus_ptperorangan"),
        ("mau dirikan cv berdua", "kasus_cv"),
        ("utang jaminan motor bpkb", "kasus_fidusia_motor"),
        ("mau buat wasiat", "kasus_wasiat"),
        ("mau perjanjian pisah harta nikah", "kasus_kawin"),
    ]
    ok = 0
    for cerita, harap in kasus:
        got = deteksi(cerita)
        nama = nama_lokal(got) if got else None
        info = ground_case(got) if got else None
        lolos = (nama == harap) and (info is not None)
        n_slot = len(slot_untuk(got)) if got else 0
        baris = (f"[{'OK' if lolos else 'FAIL'}] '{cerita}' -> {nama} "
                 f"(harap {harap}) | {n_slot} slot")
        if info:
            baris += f" | {info['lembaga']} / {info['akta']}"
        print(baris)
        ok += lolos
    print(f"\n{ok}/{len(kasus)} deteksi + grounding lolos.")

    print("Uji 10 CQ:", end=" ")
    import glob
    n = 0
    berkas = sorted(glob.glob(str(AKAR / "queries" / "*.rq")))
    for f in berkas:
        if list(g.query(open(f, encoding="utf-8").read())):
            n += 1
    print(f"{n}/{len(berkas)} query mengembalikan baris.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
    else:
        main()
