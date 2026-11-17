# Evaluasi 10 CQ — hasil aktual (rdflib)

Ontology: `ontology/notaris-triage.ttl` (T-Box, 681 triple) + `data/abox.ttl`
(A-Box, 541 triple) = 1222 triple, 8 aturan SWRL, 79 individu aplikasi, dan
ekspresivitas SROIQ(D). Berkas uji Pellet `data/uji-penalaran.ttl` (18 triple,
2 individu) berdiri terpisah dan tidak dipakai query CQ.

| CQ | File | Hasil |
|---|---|---|
| CQ1 jual beli | cq01-jualbeli.rq | 1 baris: PPAT / AJB / siap ke PPAT |
| CQ2 waris jual | cq02-waris-jual.rq | 3 baris dokumen kurang + saran urus SKW |
| CQ3 sengketa | cq03-sengketa.rq | 1 baris: pengadilan / rujuk |
| CQ4 hibah | cq04-hibah.rq | 3 baris: akta hibah + biaya + daftar BPN |
| CQ5 usaha | cq05-usaha.rq | 2 baris: PT perorangan vs CV |
| CQ6 fidusia | cq06-fidusia.rq | 1 baris: notaris / fidusia |
| CQ7 wasiat | cq07-wasiat.rq | 1 baris: wasiat |
| CQ8 kawin | cq08-kawin.rq | 1 baris: perjanjian kawin + Dukcapil |
| CQ9 kelengkapan | cq09-kelengkapan.rq | 19 baris status + kurang + sudah |
| CQ10 biaya waktu | cq10-biaya-waktu.rq | 9 baris saran + waktu + biaya |

Cara ulang: `python3 demo/app.py --test`
(uji ini menjalankan 9 skenario deteksi dan 10 berkas CQ sekaligus).

Di Protégé: buka `data/abox.ttl` (ia mengimpor T-Box, yang mengimpor LKIF),
lalu jalankan Pellet lewat Reasoner. Uji SPARQL di tab SPARQL, aturan di tab
SWRL (delapan aturan berlabel R1 sampai R8).

Uji penalaran Pellet: buka `data/uji-penalaran.ttl` (mengimpor A-Box), jalankan
Pellet, lalu periksa individu `:kasus_uji_waris`. Berkas itu hanya membawa fakta
masukan (`punyaJenis :trans_warisJual`, `adaSKWaris false`), tanpa kepala aturan.
Setelah reasoning, dua fakta berikut harus muncul sebagai hasil inferensi R2:

- `berstatus :status_belumLengkap`
- `butuhDokumen :dok_SKWaris`

Kalau keduanya muncul padahal tidak pernah ditulis di berkas, terbukti Pellet
benar-benar menjalankan R2, bukan sekadar membaca assertion.

Catatan: query dijalankan oleh rdflib atas fakta yang sudah diassert di A-Box,
jadi demo tidak butuh reasoner. Peran Pellet adalah memeriksa konsistensi,
menurunkan fakta tersembunyi (properti inverse dan transitive, tipikal kelas),
dan menjalankan R1–R8 dari fakta masukan kasus.
