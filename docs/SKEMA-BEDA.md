# Bukti beda skema vs paper existing

Task spesifik: **Triase Tuntas** — cerita awam menjadi lima keluaran wajib
(instansi + versi akta + ceklis dokumen + status + langkah berikutnya), tidak
boleh tutup sebelum slot lengkap.

Skema kini terdiri atas T-Box (`ontology/notaris-triage.ttl`), A-Box
(`data/abox.ttl`), dan R-Box (8 `swrl:Imp` di dalam T-Box). Kelas domain menjadi
subclass LKIF-Core, dan penalaran dijalankan Pellet di Protégé.

## 1. vs LexID (Muninggar & Krisnadhi 2023, JIKI)

LexID = knowledge graph retrieval 20rb+ regulasi (metadata + isi pasal),
relasi antar-dokumen (amends/repeals/implements/hasLegalBasis), evaluasi F1
retrieval. Tidak ada triase, tidak ada akta privat/PPAT.

| LexID | Notaris-Triage (ini) | Beda |
|---|---|---|
| `LegalDocument` + 33 subclass jenis regulasi | `Akta` + subclass versi layanan (AJB, Hibah, APHB, Fidusia, Wasiat, PT/CV, Kawin) | Domain regulasi vs domain layanan notaris |
| `Norm`, `RuleAct`, `Concept`, `CompoundExpression` | `KasusTriage`, `CeritaAwam`, `JenisTransaksi`, `StatusPenanganan` | Semantik pasal vs status triase awam |
| `hasLegalBasis`, `amends`, `repeals`, `implements` | `butuhAkta`, `ditanganiOleh`, `butuhDokumen`, `berstatus`, `saranLangkah` | Relasi dokumen vs relasi kebutuhan menuju solusi |
| `Person/Office/City`, `PlaceOfPromulgation` | `Tokoh` (WargaAwam/AhliWaris), peran LKIF (PejabatNotaris/PPAT/Saksi), `Lembaga` (Notaris/PPAT/Pengadilan/BPN/AHU/Dukcapil) | Metadata pengesahan vs aktor penanganan |
| Query: isi pasal / status amandemen | CQ1–CQ10: instansi + akta + kurang dokumen + estimasi | Retrieval vs triase tuntas |
| Tidak ada SWRL triase | 8 SWRL R1–R8 peristiwa menuju akta menuju status | Tidak ada inferensi kasus di LexID |

## 2. vs Loutas et al. 2011 (SemanticGov Portal)

Loutas = portal layanan publik umum (SIM, chamber of commerce),
Service Tree Ontology (STO) + Public Service Ontology + STL/QM,
fokus find-service + cek eligibility + versi layanan.

| Loutas | Notaris-Triage (ini) | Beda |
|---|---|---|
| `ServiceType` → `ServiceVersion` (layanan publik) | `JenisTransaksi` → `KasusTriage` + `StatusPenanganan` (kasus hukum) | Layanan admin vs peristiwa hukum |
| `InternalNode/LeafNode/Question/SparqlQuery` (STO meta) | Tidak dipakai; dialog = slot-filling yang slot-nya dibaca dari badan aturan SWRL | Struktur tree berbeda, nama berbeda |
| `Public Service Ontology` (GEA: SocietalEntity, Evidence, Outcome) | `Akta`/`DokumenSyarat`/`ObjekHukum`/`KomponenBiaya`/`AturanHukum` | Model layanan vs model akta-dokumen-biaya |
| Output: deskripsi layanan + eligibility | Output: lima keluaran triase + tolak tutup sebelum lengkap | Eligibility sekali vs pengawalan sampai tuntas |
| dievaluasi via prototype portal eGov | Dievaluasi via 10 CQ + 9 skenario `--test` + Pellet | Metrik berbeda |

## 3. vs B-Team 3 (proposal tim)

B-Team 3 = ide empat lapis + tabel beda referensi, masih konsep
(belum ada OWL jalan, CQ, SPARQL, SWRL executable). Ini = perwujudan
executable-nya dengan kalimat, nama kelas, dan 9 kasus contoh yang
diparafrase baru. Satu selisih yang dicatat jujur: B-Team 3 dan proposal
menyebut UFO dan LexID, sedangkan hasil ini memakai LKIF-Core saja
(alasan di `README.md`).

## Reuse LKIF-Core

Kelas domain dipetakan ke LKIF-Core, bukan dicopy persis:

| Kelas kita | Superclass LKIF |
|---|---|
| `Akta` | `lkif-expr:Document` |
| `AturanHukum` | `lkif-expr:Document` |
| `UndangUndang` | `AturanHukum` (turunan, tanpa superclass LKIF tambahan) |
| `PeraturanPemerintah` | `AturanHukum` (turunan, tanpa superclass LKIF tambahan) |
| `DokumenSyarat` | `lkif-expr:Document` |
| `ObjekHukum` | `lkif-process:Physical_Object` |
| `JenisTransaksi` | `lkif-action:Transaction` |
| `Lembaga` | `lkif-action:Organisation` |
| `PeristiwaHukum` | `lkif-la:Act_of_Law` |
| `Tokoh` | `lkif-action:Agent` |
| `WargaAwam` | `lkif-la:Natural_Person` |
| `PejabatNotaris`, `PejabatPPAT` | `lkif-lr:Professional_Legal_Role` |
| `SaksiAkta` | `lkif-lr:Legal_Role` |

Catatan pemetaan: kelas peran sengaja tidak dibuat subclass `Tokoh`, karena
LKIF menyatakan `Agent` dan `Role` saling lepas. Menyatukannya membuat ontology
inkonsisten di Pellet.

Modul `lkif-norm` tidak diimpor. Pellet 2.2.0 tidak selesai mengklasifikasinya
(StackOverflow pada `Blocking` saat precompute), sehingga `Akta` dan
`AturanHukum` dipetakan ke `lkif-expr:Document`. Sisanya tetap memakai kelas
LKIF asli dari modul yang lolos uji.

Deklarasi `owl:TransitiveProperty` pada properti LKIF yang punya rantai
`rdfs:subPropertyOf` dibuang dari tiga modul tersalin: `mereology`,
`relative-places`, dan `time`. Plugin Pellet di Protege memaksa
`IGNORE_UNSUPPORTED_AXIOMS=false`, dan Pellet 2.2.0 menolak kombinasi transitive
dengan subproperti. Hierarki `rdfs:subPropertyOf` dan `owl:inverseOf` tetap
utuh, dan transitivitas `:terkaitAturan` milik kita tidak disentuh.

## Ekspresivitas DL: SROIQ(D)

T-Box mencapai **SROIQ(D)**, bukan hanya SHIQ(D). Tiap huruf punya sumber yang
bisa ditunjuk di berkas.

| Huruf | Arti | Sumber di ontology |
| --- | --- | --- |
| S | ALC + peran transitif | `:terkaitAturan` `owl:TransitiveProperty` |
| H | hierarki peran | `rdfs:subPropertyOf` pada properti LKIF |
| I | peran invers | `owl:inverseOf` pada `:aktaUntuk` dan `:ditanganiOleh` |
| Q | kardinalitas berkualifikasi | `:KasusTriage` tepat satu `:punyaJenis` pada `:JenisTransaksi` |
| D | tipe data | `xsd:boolean`, `xsd:integer`, `xsd:string` pada 10 data property |
| O | nominal | `:KasusWarisJual` ≡ `:KasusTriage` ⊓ (`:punyaJenis` value `:trans_warisJual`) |
| R | inklusi peran kompleks | `:dasarKasus` `owl:propertyChainAxiom` (`:butuhAkta` `:berdasarPada`) |

Konsekuensi yang harus disebut jujur: nominal mewajibkan satu individu bernama di
dalam kelas ekspresi, sehingga `:trans_warisJual` dideklarasikan di T-Box. Itu
satu-satunya individu di sana. Nominal juga membuat Pellet mengklasifikasi
seluruh A-Box, jadi precompute atas 79 individu butuh sekitar 1 sampai 4 menit.
Rantai properti sendiri murah (sekitar 4 detik).

## Cara verifikasi cepat (untuk dosen)

1. Protégé, tab Entities: cari `LegalDocument`, `Norm`, `ServiceTree` di
   namespace kita, hasilnya kosong (tidak ada di skema ini). Cari `KasusTriage`,
   `saranLangkah`, `butuhAkta`, hasilnya ada (orisinal).
2. Tab Classes: buka `Akta`, lihat superclass-nya `lkif:Document`
   (bukti reuse lewat `owl:imports`).
3. Jalankan Pellet: ontology konsisten, aturan R1–R8 muncul di tab SWRL.
4. Uji penalaran: buka `data/uji-penalaran.ttl`, jalankan Pellet, periksa
   `:kasus_uji_waris`. `berstatus` harus berisi `:status_belumLengkap` dan
   `butuhDokumen` harus berisi `:dok_SKWaris`, padahal keduanya tidak ditulis di
   berkas (hasil inferensi R2). Periksa juga `:kasus_uji_rantai`:
   `dasarKasus` harus berisi `:aturan_ppat` (hasil rantai properti) dan individu
   itu harus bertipe `:KasusWarisJual` (hasil nominal). Keduanya sudah
   dikonfirmasi di GUI: `:dasarKasus :aturan_ppat` dan `:KasusWarisJual` muncul
   berlatar kuning (inferred), sedangkan fakta masukan tidak.
5. `python3 demo/app.py --test`: 9/9 deteksi + grounding, 10/10 CQ ada baris.
