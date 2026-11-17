# KB & Penalaran Triase Notaris dan PPAT Indonesia

Prototype knowledge base dan penalaran untuk membantu masyarakat awam
menentukan instansi, akta, dan dokumen yang dibutuhkan sebelum ke notaris/PPAT.
Skema dan aturan dimodelkan sebagai OWL 2 DL (SROIQ(D)) di Protégé, aturan
ditulis sebagai SWRL dan dijalankan Pellet, lalu demo Python membaca fakta dari
ontology lewat SPARQL tanpa mengarang jawaban.

> Prototype edukasi. Bukan nasihat hukum.

## Struktur

```
data/        A-Box (80 individu, 10 kasus) dan berkas uji penalaran
demo/        penampil CLI dan web (Streamlit)
docs/        traceability pasal, evaluasi CQ, skema beda, progres, kamus data
notaris/     lapisan baca ontology: pemuat, parser SWRL, verbalisasi, chatbot
ontology/    T-Box + R-Box, katalog Protege, salinan LKIF-Core
queries/     10 SPARQL untuk 10 competency question
rules/       8 aturan SWRL versi manusia beserta sumber pasal
tools/       generator kamus data
```

## Prasyarat

Python 3.10+ dengan `rdflib`, dan Protégé 5.6 beserta plugin Pellet untuk
penalaran serta inspeksi ontology. Streamlit hanya dibutuhkan untuk demo web.

## Instalasi

```bash
python3 -m venv .venv
.venv/bin/pip install -r demo/requirements.txt
.venv/bin/pip install streamlit          # opsional, untuk demo web
```

## Menjalankan

```bash
python3 demo/app.py --test                  # 9/9 deteksi + 10/10 CQ
python3 demo/app.py                         # demo CLI
streamlit run demo/app_streamlit.py         # demo web
python3 -m notaris.verbalisasi              # korpus bahasa awam
python3 -m notaris.verbalisasi --cek        # ringkasan tanpa menulis
python3 tools/build_kamus_data.py           # kamus data, xlsx, mind map
```

Contoh input CLI: `mau jual tanah warisan belum balik nama`.

## Buka di Protégé

1. Buka **Protégé** (5.6+), lalu **File > Open** dan pilih `data/abox.ttl`.
   A-Box mengimpor T-Box, dan T-Box mengimpor 10 modul LKIF-Core.
2. Import diselesaikan otomatis lewat `catalog-v001.xml` di folder `data/` dan
   `ontology/` (pastikan kedua katalog tetap di foldernya).
3. Jalankan **Reasoner > Pellet > Start reasoner**. Precompute A-Box penuh
   butuh sekitar 1 sampai 4 menit karena adanya nominal, jadi tunggu sampai
   selesai dan jangan menutup jendela.
4. Periksa hasil di tab **Entities**, **Individuals**, dan tab **SWRL** untuk
   aturan R1 sampai R8. Hasil inferensi ditandai kuning, bukan assertion.
5. Uji penalaran: buka `data/uji-penalaran.ttl`, jalankan Pellet, lalu periksa
   `:kasus_uji_waris` (R2 menurunkan status dan dokumen) dan `:kasus_uji_rantai`
   (rantai properti menurunkan dasar kasus, nominal mengetikkannya sebagai
   `:KasusWarisJual`).

## Sumber Data

Peraturan diambil dari JDIH BPK (`peraturan.bpk.go.id`) sebagai desk research.
Pemetaan pasal ke kelas, aturan, dan CQ ada di `docs/TRACEABILITY.md`, dan setiap
individu `AturanHukum` di A-Box membawa anotasi `:sumber` berisi kutipan resmi
yang dipakai demo. Salinan LKIF-Core 1.0 di `ontology/external/lkif/` berlisensi
CC BY 4.0 (lihat `LICENSE` di folder itu), disalin lokal karena IRI aslinya di
estrellaproject.org mengembalikan 403.

## Metadata

Turtle hanya memuat metadata bermakna: `:sumber` pada aturan hukum,
`:kataKunci` dan `:prioritas` pada kasus, serta label bahasa Indonesia. Arti
istilah ontology dan proyek ada di `docs/ISTILAH.md`, dan rincian isi ontology
per kelas ada di `docs/kamus-data/`.

## Lisensi

Kode proyek ini belum memakai berkas `LICENSE` tersendiri. LKIF-Core di
`ontology/external/lkif/` tetap berlisensi CC BY 4.0 sesuai berkas lisensi
bawaannya.
