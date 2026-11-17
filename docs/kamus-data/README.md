# Kamus data notaris-triage

Hasil generate dari ontology, bukan diketik manual. Sumber: `ontology/notaris-triage.ttl`
(T-Box + R-Box), `data/abox.ttl` (A-Box), `data/uji-penalaran.ttl` (uji), dan
`queries/*.rq` (10 CQ).

Bangkitkan ulang setelah ontology berubah:

```
python3 tools/build_kamus_data.py
```

Keluaran: 13 CSV (satu per sheet), satu `notaris-triage-kamus-data.xlsx`, dan
`peta-pikiran.md` (mind map Mermaid).

## Isi sheet

| Sheet | Kolom penting |
| --- | --- |
| Ringkasan | ukuran, nilai, keterangan |
| Kelas | IRI, prefiks, label, superclass kita, superclass LKIF, restriksi, grup disjoint, modul LKIF, DBpedia |
| ObjectProperty | IRI, domain, range, karakteristik, inverse, subPropertyOf, propertyChainAxiom |
| DataProperty | IRI, domain, range xsd |
| AnnotationProperty | IRI, label, komentar |
| AturanSWRL | nama, body, head |
| Individu | IRI, label, kelas, jumlah fakta, kataKunci, prioritas, fakta kunci |
| Referensi | IRI, label, tipe, sumber (judul UU), DBpedia |
| LKIF | modul, IRI resmi, berkas lokal, diimpor, lisensi, catatan |
| DBpedia | nama, IRI kita, DBpedia EN, id.dbpedia, status, catatan |
| KompetensiCQ | nomor, berkas, pertanyaan |
| IriNamespace | prefix, IRI, dipakai untuk |
| Riwayat | urutan, tahap, pekerjaan, status |

## Status pemetaan DBpedia

Kolom status di sheet DBpedia menyebut tingkat verifikasi, karena tidak semua
konsep punya padanan.

- `terverifikasi (sameAs)`: resource DBpedia ada dan punya `owl:sameAs` ke
  DBpedia bahasa Indonesia. Bukti paling kuat.
- `terverifikasi (resource)`: resource DBpedia bahasa Inggris ada, tanpa sameAs
  ke versi Indonesia.
- `perkiraan`: konsep mirip tetapi bukan padanan tepat, misalnya proses untuk
  pejabat.
- `tidak ada padanan`: sudah dicek ke endpoint DBpedia, tidak ada.
- `belum diperiksa`: sengaja tidak diklaim.

Pemetaan DBpedia hanya untuk dokumentasi dan tidak di-`asserted` ke ontology.
