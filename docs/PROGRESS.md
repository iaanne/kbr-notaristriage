# Log Progress Mingguan — untuk laporan dosen & dokumentasi

## Build v0.4.0 — SROIQ(D) (SELESAI)

Syarat tugas menuntut ekspresivitas DL sampai SROIQ(D). Baseline terukur saat itu
`SHIQ(D)`: S, H, I, Q, D sudah ada, O dan R belum.

1. **Huruf O (nominal).** Ditambah kelas terdefinisi `:KasusWarisJual` ≡
   `:KasusTriage` ⊓ (`:punyaJenis` value `:trans_warisJual`) memakai
   `owl:hasValue`. Konstruk itu mewajibkan individu bernama, jadi
   `:trans_warisJual` dideklarasikan di T-Box. Ini satu-satunya individu di T-Box
   dan sengaja didokumentasikan di komentar header.
2. **Huruf R (inklusi peran kompleks).** Ditambah
   `:dasarKasus owl:propertyChainAxiom ( :butuhAkta :berdasarPada )`. Maknanya:
   bila kasus butuh akta dan akta berdasar suatu aturan, aturan itu menjadi dasar
   kasus.
3. **Kasus uji baru.** `data/uji-penalaran.ttl` kini memuat `:kasus_uji_rantai`
   dengan `:butuhAkta :akta_PHB` dan `:adaSKWaris true`, tanpa `:dasarKasus`.
   Rantai harus menurunkan `:dasarKasus :aturan_ppat`, dan nominal harus
   mengetikkannya sebagai `:KasusWarisJual`.
4. **Kandidat yang ditolak setelah diuji.** `owl:oneOf` membuat Pellet
   menggantung lebih dari 200 detik. `DataHasValue` tidak dihitung sebagai O oleh
   pemeriksa ekspresivitas Pellet. `owl:IrreflexiveProperty`,
   `owl:AsymmetricProperty`, dan properti disjoint diterima tetapi tidak
   menaikkan nama DL. `USE_PSEUDO_NOMINALS=true` tidak menolong dalam 120 detik
   dan penalarannya tidak lengkap.
5. **Verifikasi headless** dengan setelan plugin Protégé
   (`IGNORE_UNSUPPORTED_AXIOMS=false`, `SILENT_UNDEFINED_ENTITY_HANDLING=true`)
   atas berkas asli, tanpa menyuntik aksioma:
   `DL = SROIQ(D)`, `konsisten = true`,
   `kasus_uji_waris` → `berstatus :status_belumLengkap` dan
   `butuhDokumen :dok_SKWaris`,
   `kasus_uji_rantai` → `dasarKasus :aturan_ppat` dan bertipe `:KasusWarisJual`.
   Waktu precompute 64 detik pada percobaan itu (rentang wajar 1 sampai 4 menit,
   tergantung mesin dan cache).
6. **Angka baru.** T-Box 681 triple, A-Box 541 triple, berkas uji 18 triple,
   gabungan 1238. 34 kelas, 15 object property, 10 data property, 3
   `AllDisjointClasses`, 8 `swrl:Imp`, 81 individu unik (79 A-Box, 2 uji, 1
   deklarasi nominal di T-Box yang individunya sama dengan di A-Box).
7. **Regresi.** `python3 demo/app.py --test` → 9/9 deteksi + grounding, 10/10 CQ
   ada baris. `python3 -m notaris.verbalisasi --cek` → 205 baris. Profil OWL 2 DL
   masih melaporkan 10 pelanggaran, semuanya `dct:license` yang tidak
   dideklarasikan di berkas LKIF, bukan di skema kita; tidak ada pelanggaran baru.
8. **Biaya waktu.** Nominal yang mahal, bukan rantai. Tanpa nominal 3,9 detik,
   dengan rantai 4,1 detik, dengan nominal langsung 150 detik ke atas. Karena itu
   README memuat peringatan agar menunggu saat Start reasoner atas A-Box penuh.
9. **Konfirmasi di GUI Protégé.** Setelah Start reasoner atas
   `data/uji-penalaran.ttl`, individu `:kasus_uji_rantai` diperiksa di tab
   Individuals: `:dasarKasus :aturan_ppat` muncul berlatar kuning (inferred dari
   rantai properti) dan `:KasusWarisJual` muncul di daftar Types juga berlatar
   kuning (inferred dari nominal), sedangkan `:butuhAkta`, `:punyaJenis`, dan
   `:adaSKWaris` tetap tanpa latar karena assertion. Jadi O dan R terbukti di
   GUI, bukan hanya headless. `:berstatus` sengaja tidak muncul di kasus ini
   karena `:adaSKWaris true` membuat R2 tidak menyala; kasus ini diisolasi untuk
   menguji rantai dan nominal saja.

## Build v0.3.0 — disesuaikan dengan materi dosen (SELESAI)

Perubahan besar: proyek diturunkan ke lingkup yang benar-benar diajarkan, lalu
disusun ulang.

1. **Satu ontology, satu import.** Dibuang tumpukan gUFO + LexID. Yang dipakai
   hanya LKIF-Core sebagai *legal core* (CC BY 4.0, disalin ke
   `ontology/external/lkif/`). Alasan selisih dengan proposal dicatat di
   `README.md`.
2. **T-Box dan A-Box dipisah.** `ontology/notaris-triage.ttl` kini murni skema
   dan aturan, tanpa individu. Seluruh 79 individu pindah ke `data/abox.ttl`.
3. **Kata kunci pindah ke ontology.** Daftar `POLA`, `CASE_IRI`, dan `SLOTS`
   dihapus dari `demo/app.py`. Kata kunci kini anotasi `:kataKunci` dan
   `:prioritas` pada tiap kasus; slot pertanyaan dibaca dari badan `swrl:Imp`.
4. **Pemetaan LKIF.** Kelas domain menjadi subclass LKIF (Akta, AturanHukum,
   Lembaga, Tokoh, peran, dan seterusnya). Kelas peran sengaja tidak dibuat
   subclass Tokoh karena LKIF menyatakan Agent dan Role saling lepas. Modul
   `norm` tidak diimpor (lihat catatan build fix di bawah), jadi Akta dan
   AturanHukum memakai `lkif-expr:Document`.
5. **Penalaran di Protégé.** Reasoner yang dipakai Pellet, bukan Python.
   Demo hanya penampil dan membaca hasil lewat SPARQL.
6. **Katalog import per folder.** Protégé mencari `catalog-v001.xml` di folder
   berkas yang dibuka. Katalog karenanya diletakkan di `ontology/catalog-v001.xml`
   dan `data/catalog-v001.xml`, bukan di akar repo. Keduanya memetakan IRI LKIF
   dan IRI ontology kita ke berkas lokal, supaya Protégé tidak butuh jaringan.
7. **Berkas uji penalaran Pellet.** `data/uji-penalaran.ttl` memuat satu individu
   (`:kasus_uji_waris`) dengan fakta masukan saja, tanpa kepala aturan. Ia
   mengimpor A-Box dan dipakai membuktikan Pellet menurunkan `berstatus
   :status_belumLengkap` dan `butuhDokumen :dok_SKWaris` lewat R2.
8. **Verifikasi.** T-Box 660 triple, A-Box 541 triple, berkas uji 11 triple,
   gabungan 1212; 34 kelas, 15 object property, 10 data property, 3
   `AllDisjointClasses`, 8 `swrl:Imp`, 80 individu, 0 individu di T-Box. Semua
   kelas dan properti yang dipakai A-Box terdeklarasi di T-Box. Closure import
   lengkap di tiga jalur buka (uji, A-Box, T-Box), tanpa IRI tak terpetakan.
   `python3 demo/app.py --test` → 9/9 deteksi + grounding, 10/10 CQ ada baris.
   `python3 -m notaris.verbalisasi --cek` → 205 baris.

## Build fix — aturan benar-benar dibaca Pellet (SELESAI)

Dua cacat yang membuat Pellet tidak menurunkan apa pun, ditemukan dengan
menjalankan Pellet headless atas `data/uji-penalaran.ttl`:

1. **Aturan SWRL tidak terparsing.** Aturan ditulis sebagai `:rule_R1 a swrl:Imp`
   (node bernama). OWL API dan Pellet hanya memparsing aturan dari node anonim.
   Gejalanya: `swrl:Imp` terbaca 8, tetapi `Body()` dan `Head()` kosong, jadi
   tidak ada kepala aturan yang pernah diturunkan. Perbaikan: aturan ditulis
   ulang sebagai node anonim `[ a swrl:Imp ; ... ]` dengan `swrl:body` dan
   `swrl:head` berupa `swrl:AtomList` eksplisit. Nama R1–R8 pindah ke
   `rdfs:label`. `notaris/ontology.py` mengambil nama aturan dari label itu.
2. **A-Box bikin ontology tidak konsisten.** Nilai `:penjelasanAwam`,
   `:perkiraanBiaya`, `:perkiraanWaktu`, dan `:saranLangkah` ditulis sebagai
   literal berbahasa `"..."@id`, padahal `rdfs:range` keempatnya `xsd:string`.
   Literal berbahasa bertipe `rdf:langString`, bukan `xsd:string`, sehingga
   Pellet menandai ontology tidak konsisten. Perbaikan: keempat properti itu
   kini bernilai string biasa (tanpa `@id`); properti anotasi seperti
   `rdfs:label`, `rdfs:comment`, `:kataKunci`, dan `:sumber` tetap boleh `@id`.

Verifikasi ulang lewat Pellet headless: delapan aturan membaca body dan head
lengkap, ontology konsisten.

## Build fix — Pellet berhenti menggantung karena modul LKIF `norm` (SELESAI)

Gejala: dengan T-Box + A-Box penuh, `isConsistent()` tidak selesai (lebih dari
10 menit), sedangkan LKIF saja, T-Box saja, dan potongan A-Box semuanya cepat.

1. **Penyebab.** Uji per modul menunjukkan `norm.owl` satu-satunya modul yang
   membuat precompute Pellet 2.2.0 gagal: `StackOverflowError` berulang di
   `org.mindswap.pellet.tableau.blocking.Blocking.isDirectlyBlockedByDescendant`.
   Modul lain (`lkif-top`, `mereology`, `relative-places`, `process`, `time`,
   `action`, `role`, `expression`, `legal-action`, `legal-role`) selesai di
   bawah 250 ms. Beban beratnya berasal dari siklus
   `Legal_Source ≡ ∃bears.(Norm ⊔ Legal_Expression)`, `Norm ≡ ∃qualifies.
   Normatively_Qualified`, dan `Normatively_Qualified ⊑ ∃normatively_comparable.
   Normatively_Qualified`.
2. **Perbaikan.** T-Box tidak lagi mengimpor `lkif-core.owl` (yang menarik
   `norm.owl`), melainkan 10 modul LKIF yang aman satu per satu. `Akta` dan
   `AturanHukum` dipetakan ke `lkif-expr:Document`; `UndangUndang` dan
   `PeraturanPemerintah` cukup turunan `AturanHukum`.
3. **Verifikasi.** Precompute ketiga tipe atas A-Box penuh: 871 ms. Pellet
   headless atas `data/uji-penalaran.ttl`: 8 aturan terbaca lengkap,
   `KONSISTEN: true`, dan R2 menurunkan `berstatus :status_belumLengkap` serta
   `butuhDokumen :dok_SKWaris`.

## Build fix — Pellet menolak transitif LKIF di Protege (SELESAI)

Gejala: Pellet di Protege gagal dengan `UnsupportedFeatureException` pada
`TransitiveObjectProperty(...mereology.owl#part)`, sedangkan Pellet headless
biasa berjalan normal.

1. **Penyebab.** Static initializer plugin Pellet di Protege memaksa
   `PelletOptions.IGNORE_UNSUPPORTED_AXIOMS = false`, padahal nilai bawaan
   Pellet adalah `true`. Dengan nilai itu, Pellet 2.2.0 menolak properti
   transitive yang punya rantai `rdfs:subPropertyOf`; `RBox.ignoreTransitivity`
   melempar galat untuk `contains`.
2. **Perbaikan.** Deklarasi `owl:TransitiveProperty` dihapus dari tiga modul
   LKIF tersalin: `mereology.ttl` (composed_of, contains, composes,
   contained_in, part_of, part), `relative-places.ttl` (covered_by, cover,
   exactly_coincide, relatively_fixed), dan `time.ttl` (before, after).
   `rdfs:subPropertyOf`, `owl:inverseOf`, `owl:SymmetricProperty`, dan semua
   kelas tetap. Transitivitas `:terkaitAturan` milik ontology kita tidak
   disentuh, karena properti itu tidak punya subproperti sehingga diterima
   Pellet.
3. **Verifikasi.** Dengan setelan plugin yang sama
   (`IGNORE_UNSUPPORTED_AXIOMS=false`, `SILENT_UNDEFINED_ENTITY_HANDLING=true`):
   `createReasoner` berhasil, precompute selesai, `konsisten=true`, dan R2
   menurunkan `berstatus :status_belumLengkap` serta `butuhDokumen
   :dok_SKWaris`. Angka triple tidak berubah karena trim terjadi di berkas
   LKIF, di luar hitungan T-Box (660 triple).
4. **Uji GUI.** Di Protege, `Start reasoner` berjalan tanpa galat. Panel
   Property assertions `kasus_uji_waris` menampilkan `berstatus
   :status_belumLengkap` dan `butuhDokumen :dok_SKWaris` dengan latar kuning,
   yaitu tanda assertion hasil inferensi, bukan assertion masukan.

## Minggu 1 — Proposal + referensi (SELESAI, sebelum build)
- Proposal revisi B-Team 3 (stakeholder awam, ide KB 4 lapis, SDG 16/10/9).
- Referensi terkumpul: LexID JIKI 2023, Loutas SemanticGov 2011, 8 PPT dosen.

## Minggu 2 — Model KB v0.1 (SELESAI)
- `ontology/notaris-triage.ttl`: 849 triple, 30 kelas, 16 object property,
  10 data property, 9 kasus ABox, 7 SWRL.
- Bukti: lolos parse rdflib; OWL-RL expand 849→1847 tanpa error.

## Build ini — v0.2.0 Task Triase Tuntas + Skema Ganti Total (SELESAI, hari ini)
1. Header ontology dikunci: task Triase Tuntas (5 output wajib, tolak tutup
   sebelum slot lengkap) + pernyataan skema orisinal.
2. Baru: `docs/SKEMA-BEDA.md` — tabel side-by-side vs LexID, vs Loutas,
   vs B-Team 3 + cara verifikasi 3 langkah di Protege.
3. `docs/TRACEABILITY.md` dibetulkan (typo + pernyataan task).
4. `README.md` menautkan SKEMA-BEDA.
5. Verifikasi ulang (angka untuk laporan):
   - Triple: 849; SWRL: 7; CQ: 10/10 ada baris; demo `--test`: 8/8 OK.
   - Cek kontaminasi skema: LegalDocument/RuleAct/ServiceTree/PublicService → BERSIH TOTAL.
   - Simulasi interaktif warisan (belum/sudah/sudah) → status `belum lengkap` + suruh urus SKW dulu (benar).

## Bukti yang bisa dibawa ke dosen minggu ini
1. Screenshot Protege: Class hierarchy + HermiT "consistent".
2. Screenshot tab SPARQL: jalankan `queries/cq02-waris-jual.rq`.
3. Screenshot terminal: `python3 demo/app.py --test` (8/8 + 10/10).
4. Tunjukkan `docs/SKEMA-BEDA.md` sebagai jawaban "skema tidak sama dengan paper".

## Berikutnya (belum dikerjakan)
- Uji HermiT manual di Protege (butuh GUI, tidak bisa via CLI).
- Tambah kasus bila dosen minta (mis. HGB, waris Islam vs perdata dipisah).
- Lembar validasi notaris (opsional, bila diminta).
- Laporan akhir + slide.

## Build fix — presisi model (hari ini)
1. Domain/range: diverifikasi 16/16 object property + 10/10 data property lengkap;
   `penjelasanAwam` diperketat dari `owl:Thing` menjadi union 7 kelas pemakai.
2. R7 diluruskan (wasiat saja) + R8 baru untuk perjanjian kawin → 8 SWRL;
   body rule yang terlepas saat save Protege dibangun ulang dari nol.
3. SKMHT/APHT dipisah presisi hukum (UUHT 4/1996): `AktaHakTanggungan`
   (akta pokok, PPAT, daftar BPN) vs `SuratKuasaMembebankan` (kuasa
   pendahulu, tidak didaftar, wajib disusul APHT); tambah `aturan_uuht`.
   Verifikasi: 1028 triple, 8 SWRL, CQ 10/10, demo 8/8, RL expand OK.

## Build fix — cakupan penjelasan awam (hari ini)
1. `penjelasanAwam` naik 35 → 56 triple. Semua tambahan dijaga tetap di dalam
   domain yang sudah ada (union 7 kelas: Akta, AturanHukum, JenisTransaksi,
   KomponenBiaya, Lembaga, ObjekHukum, StatusPenanganan) — tidak ada satu pun
   axiom yang berubah, diff murni aditif (+21 baris).
2. Diprioritaskan yang paling berguna buat masyarakat awam: komponen biaya
   (PNBP, PPh, honor), objek hukum, status penanganan, dan acuan aturan
   (fidusia, kawin, PT, tanah, waris Islam/perdata).
3. Yang SENGAJA belum diperluas: `DokumenSyarat` dan `KasusTriage` di luar
   domain union. Domain itu diperketat setelah review dosen (lihat entri
   "Build fix — presisi model"), jadi melapasnya keputusan yang belum diambil
   sendiri. Lemma `dok_*` dan `kasus_*` menunggu keputusan separately.
4. Verifikasi: parse 1028 triple; swrl:Imp R1..R8 utuh; AllDisjointClasses
   tetap 3; 31 kelas + 1 union, 16 object property, 10 data property, 79
   individu; RL expand 1028→2209 tanpa error; CQ 10/10; demo 8/8.
