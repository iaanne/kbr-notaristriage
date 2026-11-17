# Istilah Ontologi dan Proyek Notaris Triage

Daftar istilah yang dipakai di ontologi dan proyek ini. Definisi singkat, bahasa Indonesia.
Istilah diurutkan per topik, bukan abjad, supaya mudah dipakai saat menjelaskan ke dosen.

## 1. Konsep dasar

- Knowledge base (KB): kumpulan pengetahuan terstruktur yang bisa dipakai mesin untuk menalar, bukan sekadar data.
- Ontology: model konsep, relasi, dan aturan suatu domain dalam bentuk yang bisa dibaca mesin.
- T-Box: bagian ontologi yang berisi definisi umum, yaitu kelas, hierarki, properti, dan aksioma.
- A-Box: bagian ontologi yang berisi individu atau fakta konkret, misalnya satu kasus tertentu.
- R-Box: istilah yang dipakai di kuliah/proyek ini untuk lapisan aturan. Secara resmi di logika deskripsi, R-Box merujuk aksioma properti/role, bukan aturan SWRL.
- S-Box / skema: istilah lain untuk bagian T-Box.
- Triple: satu pernyataan berbentuk subjek, predikat, objek, misalnya "kasus_1 butuhAkta akta_AJB".
- RDF: format data grafik untuk menyatakan triple. RDF artinya Resource Description Framework.
- IRI: alamat unik sebuah konsep atau individu, misalnya `http://...#KasusTriage`. Mirip URL tapi lebih luas.
- Prefix: singkatan namespace, misalnya `:` untuk namespace ontologi ini dan `lkif-expr:` untuk modul LKIF expression. Namespace artinya awalan alamat IRI.
- Namespace: awalan bersama untuk semua IRI dalam satu ontologi atau modul.
- Turtle (.ttl): format penulisan RDF yang ringkas dan mudah dibaca manusia.
- RDF/XML: format penulisan RDF berbasis XML; dipakai oleh berkas REL (`rel-vocab-20100607.rdf`).
- Literal: nilai data biasa seperti string, integer, boolean. Literal berbeda dengan individu.
- Annotation: atribut yang tidak ikut memengaruhi penalaran, misalnya `rdfs:label`, `rdfs:comment`, `:kataKunci`, `:sumber`.
- Assertion: fakta yang ditulis langsung oleh pemodel.
- Inference: fakta yang diturunkan mesin dari aturan dan aksioma.
- Inferred: istilah untuk hasil inference. Di Protégé tampil berlatar kuning.
- Consistent / konsisten: ontologi tidak mengandung kontradiksi logika.
- Unsatisfiable class: kelas yang tidak mungkin punya individu karena kontradiksi aksioma; di Protégé biasanya muncul merah.

## 2. Kelas, properti, dan aksioma

- Class: konsep atau kategori, misalnya `KasusTriage`, `Akta`, `AturanHukum`.
- Subclass: kelas yang lebih spesifik dari kelas lain; ditandai `rdfs:subClassOf`.
- Equivalent class: dua kelas yang maknanya sama persis; ditandai `owl:equivalentClass`.
- Disjoint class: kumpulan kelas yang tidak boleh berbagi individu; ditandai `owl:AllDisjointClasses`.
- Domain: kelas tempat properti boleh melekat, misalnya domain `butuhAkta` adalah `KasusTriage`.
- Range: kelas tujuan properti, misalnya range `butuhAkta` adalah `Akta`.
- Object property: properti yang menghubungkan dua individu, misalnya `butuhAkta` dari kasus ke akta.
- Data property: properti dari individu ke literal, misalnya `adaSKWaris false`.
- Annotation property: properti anotasi yang tidak ikut penalaran.
- Inverse property: pasangan properti berkebalikan, misalnya `butuhAkta` dan `aktaUntuk`; ditandai `owl:inverseOf`.
- Symmetric property: properti yang bolak-balik sama, misalnya `menikahdengan`; ditandai `owl:SymmetricProperty`.
- Transitive property: properti yang berlaku berantai, misalnya `terkaitAturan`; ditandai `owl:TransitiveProperty`.
- Functional property: properti yang hanya boleh punya satu nilai per individu, misalnya `berstatus`; ditandai `owl:FunctionalProperty`.
- Property chain: rantai properti yang menyimpulkan properti baru; di proyek ini `dasarKasus = butuhAkta lalu berdasarPada`; ditandai `owl:propertyChainAxiom`.
- Nominal: kelas yang didefinisikan dari individu tertentu; di proyek ini `KasusWarisJual` dari `trans_warisJual`; ditandai `owl:hasValue`.
- Qualified number restriction: pembatasan jumlah dengan syarat kelas, misalnya "minimal 1 pendiri"; ditandai `owl:minQualifiedCardinality` atau sejenisnya.
- Class expression: definisi kelas dari gabungan konstruk, misalnya `KasusTriage and (punyaJenis value trans_warisJual)`.
- hasValue: konstruk nominal yang mensyaratkan nilai tertentu pada properti.
- oneOf: daftar individu eksplisit sebagai kelas; di proyek ini dicoba tapi membuat Pellet menggantung lebih dari 200 detik, jadi tidak dipakai.
- rdfs:range xsd:string: properti bernilai teks biasa; literal berbahasa (`"..."@id`) tidak cocok dengan range ini dan membuat Pellet menandai ontologi tidak konsisten.
- Literal berbahasa: literal dengan `@id`, misalnya `"teks"@id`; bertipe `rdf:langString`, bukan `xsd:string`.

## 3. Logika dan ekspresivitas

- Description Logic (DL): keluarga logika formal untuk ontologi.
- OWL 2 DL: varian OWL 2 yang bisa diputuskan reasoner dan cocok untuk reasoning kompleks.
- OWL 2 Full: varian OWL 2 tanpa jaminan bisa diputuskan; tidak dipakai di sini.
- SROIQ(D): nama ekspresivitas OWL 2 DL yang dituntut tugas.
  - S: transitive property.
  - R: complex role inclusion atau property chain.
  - O: nominal atau hasValue.
  - I: inverse property.
  - Q: qualified number restriction.
  - (D): datatypes, yaitu tipe data seperti integer, boolean, string.
- SHIQ(D): ekspresivitas sebelum build v0.4.0; belum punya O dan R.
- SWRL: aturan jika-maka untuk ontologi; dibaca Pellet. SWRL artinya Semantic Web Rule Language.
- Rule (R1 sampai R8): aturan SWRL di `ontology/notaris-triage.ttl`, ditulis sebagai node anonim.
- AtomList: daftar atom dalam badan/kepala aturan SWRL.
- Imp: tipe yang menandai `swrl:Imp`, yaitu satu aturan SWRL.
- Variable: variabel SWRL, di proyek ini `:var_k` untuk satu kasus.
- Property chain axiom: aturan ontologi yang menyimpulkan properti dari dua properti berurutan.

## 4. Reasoner

- Reasoner: mesin yang memeriksa konsistensi dan menurunkan fakta baru dari ontologi.
- Pellet: reasoner yang dipakai proyek ini; membaca OWL 2 DL dan SWRL.
- HermiT: reasoner OWL lain; tidak menjalankan SWRL, jadi tidak dipakai untuk uji aturan.
- Protégé: editor ontologi GUI yang dipakai untuk membuka, memeriksa, dan menalar ontologi.
- Precompute: tahap klasifikasi sebelum reasoner mulai menjawab; di Protégé butuh waktu, apalagi setelah ada nominal.
- Inferred / kuning: hasil turunan reasoner di Protégé, ditandai latar kuning.
- Asserted / tidak kuning: fakta yang diketik pemodel, tanpa latar warna.
- Save inferred ontology: menyimpan hasil reasoner ke berkas baru; tidak boleh ditimpa ke berkas asli.
- Java heap / StackOverflowError: kegagalan mesin Java saat klasifikasi terlalu berat; penyebab modul `norm.owl` dikecualikan.
- OWL-RL expand: pemeriksaan ekspansi aturan OWL-RL; dipakai di awal untuk cek cepat ontologi, bukan untuk membuktikan SWRL.
- PelletOptions IGNORE_UNSUPPORTED_AXIOMS: setelan plugin Protégé yang memaksa false; membuat Pellet menolak transitive property yang punya rantai subproperty. Deklarasi transitive di modul LKIF dipangkas karenanya.

## 5. Import dan reuse

- owl:imports: direktif yang membuat isi ontologi lain ikut dipakai dalam reasoning.
- Legal core: ontology fondasi domain hukum yang dipakai sebagai rujukan bersama; di proyek ini LKIF-Core.
- LKIF-Core: legal core ontology (CC BY 4.0), berisi konsep hukum seperti dokumen, norma, aksi hukum, dan peran hukum.
- LKIF modules: modul-modul LKIF yang diimpor satu per satu (`lkif-top`, `mereology`, `relative-places`, `process`, `time`, `action`, `role`, `expression`, `legal-action`, `legal-role`).
- Modul `norm`: modul LKIF yang sengaja tidak diimpor karena Pellet StackOverflow saat mengklasifikasinya.
- MIREOT: Minimal Information to Reference an External Ontology Term; teknik merujuk istilah ontology luar tanpa mengimpor seluruh file.
- equivalentProperty: dua properti yang maknanya sama; dipakai praktikum keluarga untuk memetakan properti sendiri ke REL.
- subClassOf: cara proyek ini memetakan kelas domain ke kelas LKIF, misalnya `Akta` turunan `lkif-expr:Document`.
- catalog-v001.xml: katalog Protégé yang memetakan IRI import ke berkas lokal, supaya tidak perlu jaringan.
- LOV: Linked Open Vocabularies, katalog kosakata Linked Data; dipakai mencari ontology/vocabulary publik.
- REL: vocab relasi orang (`rel-vocab-20100607.rdf`) yang dipakai praktikum keluarga.
- isDefinedBy: anotasi sumber definisi istilah; jejak asal sebuah istilah eksternal.
- Prefix mapping: pemetaan prefiks ke IRI namespace, misalnya `lkif-expr:` ke `.../expression.owl#`.

## 6. Berkas-berkas proyek

- `ontology/notaris-triage.ttl`: T-Box; skema, kelas, properti, disjointness, aturan SWRL. Hanya berisi satu individu (`trans_warisJual`) karena nominal wajib menamai individu bernama.
- `data/abox.ttl`: A-Box; 79 individu aplikasi; mengimpor T-Box.
- `data/uji-penalaran.ttl`: berkas bukti penalaran; dua individu dengan fakta masukan saja; mengimpor A-Box.
- `demo/app.py`: demo CLI; membaca ontologi lewat SPARQL; tidak mengarang jawaban.
- `demo/app_streamlit.py`: versi web demo.
- `queries/cq01..cq10.rq`: 10 SPARQL untuk competency questions.
- `rules/swrl-rules.md`: aturan versi manusia plus sumber pasal.
- `docs/TRACEABILITY.md`: tabel jejak pasal ke ontologi, aturan, CQ, dan individu.
- `docs/SKEMA-BEDA.md`: bukti skema berbeda dari LexID, Loutas, dan B-Team 3.
- `docs/PROGRESS.md`: log progres mingguan dan build.
- `docs/kamus-data/`: kamus data hasil generate; 13 CSV plus xlsx.
- `tools/build_kamus_data.py`: generator kamus data; tidak ada isi diketik manual.
- `notaris/ontology.py`, `notaris/verbalisasi.py`: lapisan baca ontologi dan verbalisasi ke bahasa awam.
- `data/verbalized.jsonl`: korpus bahasa awam hasil generate; tidak di-commit.
- `data/catalog-v001.xml` dan `ontology/catalog-v001.xml`: katalog Protégé per folder.
- IRI ontology: `http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage` (T-Box), `.../notaris-triage/data` (A-Box), `.../notaris-triage/uji` (uji).

## 7. Bukti dan tolok ukur

- Competency question (CQ): pertanyaan kemampuan yang harus bisa dijawab ontologi; proyek ini punya 10.
- SPARQL: bahasa query untuk mengambil data dari grafik; dijalankan di tab SPARQL Protégé.
- Demo `--test`: uji otomatis; hasil terakhir 9/9 deteksi dan 10/10 CQ berbaris.
- ABox assertion: fakta yang diketik pemodel di A-Box; bukan hasil reasoner.
- Inferred axiom: aksioma hasil reasoner; di Protégé berlatar kuning.
- Yellow highlight: tanda visual hasil inferensi di Protégé.
- `data/uji-penalaran.ttl` vs `data/abox.ttl`: yang pertama untuk bukti murni, yang kedua untuk data aplikasi; keduanya sama-sama A-Box secara isi, tapi fungsi berbeda. Lihat bagian 6.

## 8. Istilah hukum/notaris yang dipakai

- AJB: Akta Jual Beli tanah di depan PPAT.
- APHT: Akta Pemberian Hak Tanggungan; akta pokok jaminan tanah untuk kredit bank; dibuat di PPAT lalu didaftar ke BPN.
- SKMHT: Surat Kuasa Membebankan Hak Tanggungan; kuasa pendahulu, bukan jaminan itu sendiri, wajib disusul APHT.
- PPAT: Pejabat Pembuat Akta Tanah; berwenang membuat AJB, APHT, akta hibah tanah, dll.
- SKW: Surat Keterangan Waris; bukti ahli waris yang sah; dibutuhkan sebelum jual beli harta warisan.
- BPHTB: Bea Perolehan Hak atas Tanah dan Bangunan; pajak hibah/jual beli tanah.
- PNBP: Penerimaan Negara Bukan Pajak; biaya resmi, misalnya di AHU atau BPN.
- AHU: Administrasi Hukum Umum, Kemenkumham; untuk pendaftaran badan usaha dan fidusia.
- BPN: Badan Pertanahan Nasional; pendaftaran hak tanggungan dan balik nama.
- UUJN: Undang-Undang Jabatan Notaris (UU 2/2014).
- PP 24/2016: Peraturan Pemerintah tentang PPAT.
- UUHT 4/1996: Undang-Undang Hak Tanggungan.
- UU 42/1999: Undang-Undang Jaminan Fidusia.
- UU 1/1974 jo. MK 69/2015: Undang-Undang Perkawinan dan putusan MK tentang perjanjian kawin.
- KUHPerdata: Kitab Undang-Undang Hukum Perdata; dasar wasiat, hibah, waris perdata.
- KHI: Kompilasi Hukum Islam; dasar waris perdata Islam.
- HIR/RBg: aturan acara perdata untuk Jawa dan luar Jawa; sengketa waris di rujuk ke pengadilan.
- PT perorangan: badan usaha satu orang sesuai UU Cipta Kerja; didaftar lewat AHU online.
- Fidusia: jaminan atas benda bergerak tanpa menyerahkan barangnya; wajib akta notaris dan daftar AHU.
- Akta wasiat: akta atas kehendak terakhir pewaris; dibuat di hadapan notaris dan didaftarkan ke Kemenkumham.
- Perjanjian kawin: perjanjian pisah harta; bisa dibuat sebelum/sesudah nikah sesuai MK 69/2015; dicatat ke Dukcapil.
- APHB: Akta Pembagian Hak Bersama; akta pembagian harta waris yang sudah sepakat.

## 9. Cara membaca hasil di Protégé

- Tab Classes: lihat hierarki dan disjointness; merah berarti unsatisfiable.
- Tab Object Properties: lihat domain, range, inverse, functional, property chain.
- Tab Data Properties: lihat domain dan range literal.
- Tab Individuals: lihat tipe individu dan property assertion; kuning berarti inferred.
- Tab SWRL: lihat R1–R8; badan dan kepala harus terbaca.
- Tab SPARQL: jalankan `cq02` dst.
- Start reasoner: memulai klasifikasi; untuk nominal biasanya butuh 1 sampai 4 menit.
- Jangan Save dari Protégé atas berkas asli; round-trip SWRL tidak selalu aman.
