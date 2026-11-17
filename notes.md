# Notes — Scope Ontologi Notaris Triage

Pertanyaan: ontologi Notaris Triage sudah luas atau masih sempit? Bisa ditambah source saja tidak?

## Jawaban jujur

Sempit, tapi bukan otomatis cacat untuk tugas.

## Yang dicakup sekarang

- 9 jenis keperluan utama: jual beli tanah, waris, hibah, PT perorangan, CV, fidusia, wasiat, kawin, jual beli dengan jaminan APHT/SKMHT sebagai akta.
- 8 aturan triage: instansi, akta, dokumen, status, biaya.
- 34 kelas, 15 object property, 10 data property.

## Yang belum dicakup

- Sengketa waris kompleks.
- Pemisahan waris Islam vs perdata.
- HGB, HGU, hak guna usaha/building.
- Perjanjian kredit lengkap (di luar APHT/SKMHT).
- Pajak detail per daerah (BPHTB berbeda per perda).
- Putusan pengadilan dan eksekusi.
- PT biasa, firma, koperasi, yayasan.
- Roya, grosse akta, waarmerking, legalisir.
- Balik nama, pemecahan/penggabungan hak.
- Status tanah non-SHM (HGB, Letter C, girik, tanah adat).
- PPh detail per transaksi.
- Kombinasi multi-jenis (waris + jual + jaminan sekaligus).

## Apakah "kurang source"?

Bukan cuma itu. Sumber hukum bisa ditemukan untuk semua; yang langka adalah pemodelan: kelas, properti, aturan SWRL, dan individu per kasus, plus validasi bahwa aturannya benar.

Menambah PDF peraturan tidak membuat ontologi jadi luas. Yang menambah luas adalah aturan dan kasus yang benar.

## Risiko kalau dipaksakan luas

- Aturan salah. Misalnya tarif BPHTB per daerah berbeda; hardcode satu angka berarti KB menyesatkan di daerah lain.
- Reasoner makin berat (nominal + lebih banyak individu + lebih banyak aturan).
- Dosen bisa tanya "siapa validasi aturan ini?" dan jawabannya harus notaris, bukan desk research.

## Posisi yang sehat

Sempit tapi benar dan bisa dijelaskan lebih baik daripada luas tapi setengah jadi.

## Urutan kalau mau dilebarkan

1. Pisahkan waris Islam vs perdata.
2. Tambah HGB dan hak guna usaha.
3. Tambah aturan biaya/BPHTB per jenis transaksi (bukan per daerah).
4. Tambah dokumen checklist per kasus secara detail.
5. Baru kemudian PT biasa / firma / yayasan.
6. Validasi notaris kalau dosennya minta.

## Jawaban untuk dosen

"Scope saya sengaja membatasi pada triase keperluan paling umum masyarakat awam: 9 jenis transaksi dengan alur instansi, akta, dokumen, status, dan biaya. Ontologi ini tidak menggantikan notaris; yang tidak dimodelkan dinyatakan tidak dicakup. Memperluas ke sengketa kompleks dan pajak per daerah butuh validasi praktisi dan data per daerah, bukan sekadar menambah peraturan."
