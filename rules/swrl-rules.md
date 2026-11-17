# Aturan SWRL — versi manusia (parafrase orisinal)

Sumber pengetahuan: desk research UUJN No. 2/2014, PP 24/2016 (PPAT),
KUHPerdata/KHI (waris), UU 42/1999 (fidusia), UU PT + Cipta Kerja (PT perorangan),
UU Perkawinan + Putusan MK 69/2015. Bukan salinan kalimat B-Team 3.

Format: JIKA (body) MAKA (head). Variabel `?k` = satu individu kasus triase.

Mesin penalar: **Pellet di dalam Protégé**. Pellet menangani OWL 2 DL sekaligus
aturan SWRL, jadi cukup satu reasoner. Python tidak menalar; demo hanya membaca
hasil. Gaya aturan mengikuti slide SWRL: badan memuat atom kelas dan atom
properti, kepala menambah fakta baru. Semua individu yang dirujuk ada di
`data/abox.ttl`.

## R1 — Jual beli tanah bersertifikat yang sepakat → PPAT + AJB
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_jualBeli) ∧ punyaObjek(?k, obj_tanahSHM)
     ∧ adaSertifikat(?k, true) ∧ adaSepakat(?k, true)
MAKA ditanganiOleh(?k, lem_ppat) ∧ butuhAkta(?k, akta_AJB)

## R2 — Jual warisan tanpa SKW → belum lengkap + butuh SKW
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_warisJual) ∧ adaSKWaris(?k, false)
MAKA berstatus(?k, status_belumLengkap) ∧ butuhDokumen(?k, dok_SKWaris)

## R3 — Waris tidak sepakat → rujuk pengadilan/mediasi
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_warisBagi) ∧ adaSepakat(?k, false)
MAKA ditanganiOleh(?k, lem_pengadilan) ∧ berstatus(?k, status_rujukPengadilan)

## R4 — Hibah tanah → PPAT + akta hibah + BPHTB
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_hibah) ∧ punyaObjek(?k, obj_tanahSHM)
MAKA ditanganiOleh(?k, lem_ppat) ∧ butuhAkta(?k, akta_hibah) ∧ dikenaiBiaya(?k, biaya_BPHTB)

## R5 — Usaha 1 pendiri modal kecil → PT perorangan via AHU
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_dirikanUsaha)
     ∧ jumlahPendiri(?k, 1) ∧ modalKecil(?k, true)
MAKA butuhAkta(?k, akta_PTperorangan) ∧ ditanganiOleh(?k, lem_ahu)

## R6 — Utang jaminan kendaraan → notaris + fidusia
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_utangJaminan) ∧ punyaObjek(?k, obj_kendaraan)
MAKA ditanganiOleh(?k, lem_notaris) ∧ butuhAkta(?k, akta_fidusia)

## R7 — Wasiat cakap hukum → notaris + wasiat
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_wasiat) ∧ cakapHukum(?k, true)
MAKA ditanganiOleh(?k, lem_notaris) ∧ butuhAkta(?k, akta_wasiat)

## R8 — Atur harta kawin sepakat → notaris + perjanjian kawin
JIKA KasusTriage(?k) ∧ punyaJenis(?k, trans_kawinHarta) ∧ cakapHukum(?k, true)
     ∧ adaSepakat(?k, true)
MAKA ditanganiOleh(?k, lem_notaris) ∧ butuhAkta(?k, akta_kawin)

## Catatan

- Versi mesin (SWRL RDF) ada di `ontology/notaris-triage.ttl` sebagai delapan
  `swrl:Imp` anonim berlabel R1 sampai R8, bisa dibuka di Protégé lewat tab SWRL.
  Aturan sengaja anonim: Pellet dan OWL API hanya memparsing aturan dari node
  anonim, bukan dari IRI bernama. Nama R1–R8 ada di `rdfs:label`.
- Aturan R1–R8 memakai properti yang sama persis dengan fakta masukan kasus di
  A-Box. Pellet menurunkan kepala aturan dari fakta itu; hasilnya bisa
  disimpan lewat *File → Save inferred ontology* bila ingin dibaca dari luar.
- Bukti penalaran terpisah: `data/uji-penalaran.ttl` memuat satu kasus dengan
  fakta masukan saja. Setelah Pellet dijalankan, R2 menurunkan `berstatus
  :status_belumLengkap` dan `butuhDokumen :dok_SKWaris` pada `:kasus_uji_waris`.
- Bila berkas di-*save* ulang dari Protégé, badan aturan bisa terlepas
  (Protégé tidak selalu *round-trip* `swrl:Imp` dalam format Turtle).
  Kembalikan dari git bila itu terjadi.
