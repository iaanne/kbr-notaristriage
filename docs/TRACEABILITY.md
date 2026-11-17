# Traceability — task Triase Tuntas: pasal → ontology → rule → CQ (desk research)

Task dikunci: input cerita awam menjadi lima keluaran wajib (instansi + versi
akta + ceklis dokumen + status + langkah berikutnya), tidak tutup sebelum slot
lengkap. Sumber pengetahuan mengacu regulasi publik, bukan wawancara. Jika dosen
meminta, tambah lembar validasi notaris belakangan.

Pembagian berkas: skema dan aturan di `ontology/notaris-triage.ttl` (T-Box +
R-Box), individu di `data/abox.ttl` (A-Box). Aturan dijalankan Pellet di Protégé.

| Kebutuhan awam | Sumber umum | Kelas/Properti | Rule | CQ | Kasus individu |
|---|---|---|---|---|---|
| Jual beli SHM | PP 18/2021 pendaftaran tanah; PP 24/2016 kewenangan PPAT | KasusTriage, punyaJenis, ditanganiOleh, butuhAkta | R1 | CQ1, CQ9, CQ10 | kasus_jualbeli_shm |
| Jual warisan belum SKW | KUHPerdata waris + KHI; praktik SKW kelurahan/notaris; PPAT butuh alas hak jelas | adaSKWaris, berstatus, butuhDokumen | R2 | CQ2, CQ9 | kasus_waris_belumSKW |
| Waris sengketa | HIR/RBg + PA/PN untuk penetapan sengketa; notaris/PPAT tidak boleh akta sengketa | adaSepakat=false → Pengadilan | R3 | CQ3 | kasus_waris_sengketa |
| Hibah tanah | KUHPerdata hibah; PPAT berwenang; BPHTB (UU PDRD) | AktaHibahTanah, dikenaiBiaya BPHTB | R4 | CQ4 | kasus_hibah_tanah |
| PT perorangan | UU 40/2007 jo. UU 11/2020 Cipta Kerja; pendaftaran AHU | jumlahPendiri=1, modalKecil | R5 | CQ5 | kasus_ptperorangan |
| CV | KUHD + pendaftaran badan usaha AHU | AktaCV | (A-Box) | CQ5 | kasus_cv |
| Fidusia motor | UU 42/1999 fidusia wajib akta notaris + daftar AHU | AktaFidusia, perluDaftarDi AHU | R6 | CQ6 | kasus_fidusia_motor |
| Wasiat | KUHPerdata wasiat; UUJN akta wasiat; daftar wasiat Kemenkumham | AktaWasiat | R7 | CQ7 | kasus_wasiat |
| Pisah harta | UU 1/1974 jo. MK 69/2015, dapat dibuat sebelum/sesudah nikah; catat Dukcapil | AktaPerjanjianKawin | R8 | CQ8 | kasus_kawin |
| Kredit bank jaminan tanah | UUHT 4/1996: APHT di PPAT lalu daftar BPN; SKMHT hanya kuasa pendahulu yang wajib disusul APHT | AktaHakTanggungan, SuratKuasaMembebankan | — | — | akta_APHT, akta_SKMHT |
| Kelengkapan dan biaya | SOP umum kantor notaris/PPAT + PNBP AHU/BPN | sudahPunyaDokumen, perkiraanWaktu/Biaya | — | CQ9, CQ10 | semua kasus |

## Catatan

- Kredibilitas sumber: tiap individu `AturanHukum` membawa anotasi `:sumber`
  berisi kutipan resmi, jadi dasar hukum di demo dapat ditelusuri balik.
- Ruang lingkup LKIF: pemetaan kelas ke LKIF-Core ada di `docs/SKEMA-BEDA.md`.
- Relasi LexID: kelas `AturanHukum` dan properti `terkaitAturan` (transitive)
  meniru pola `hasLegalBasis`/`amends` LexID secara ringkas, tanpa menyalin
  skemanya.
- Relasi Loutas: alur tanya-jawab STO diadopsi sebagai slot-filling di
  `demo/app.py`, bukan sebagai Service Tree Ontology yang sama. Slot dibaca dari
  badan aturan SWRL, bukan ditulis di kode.
