# Peta pikiran notaris-triage

Dua diagram: struktur ontology, lalu perjalanan pekerjaan. Sumbernya sama dengan
spreadsheet `notaris-triage-kamus-data.xlsx`.

## 1. Struktur ontology

```mermaid
mindmap
  root((Ontologi Triase Notaris/PPAT))
    T-Box 34 kelas
      Taksonomi LKIF
        expression Document
        action Agent Organisation Transaction
        legal-role Legal_Role
        process Physical_Object
      Kelas domain
        KasusTriage
        KasusWarisJual nominal
        Akta 11 turunan
        AturanHukum
        Lembaga
        DokumenSyarat
        StatusPenanganan
      Kualitas
        3 grup AllDisjointClasses
        restriksi some only value
        domain dan range sempit
    Relasi 25 properti
      Object 15
        butuhAkta inverse aktaUntuk
        ditanganiOleh inverse menangani
        berdasarPada
        dasarKasus rantai properti
        berstatus functional
      Data 10
        adaSKWaris boolean
        cakapHukum boolean
        jumlahPendiri integer
        saranLangkah string
    A-Box 79 individu
      Kasus 9
      Akta 11
      Lembaga 7
      Dokumen 14
      Objek 8
      Status 6
      Jenis 8
      Aturan 9
      Biaya 6
    R-Box 8 aturan
      R1 jual beli
      R2 waris tanpa SKW
      R3 sengketa waris
      R4 hibah
      R5 PT perorangan
      R6 fidusia
      R7 wasiat
      R8 perjanjian kawin
    Referensi 9 aturan
      UUPA dan PP 18/2021
      PP 24/2016 PPAT
      UUHT 4/1996
      UUJN 2/2014
      UU Fidusia 42/1999
      UU PT dan Cipta Kerja
      KUHPerdata waris
      KHI waris
      UU Perkawinan dan MK 69/2015
    Ekspresivitas SROIQ D
      O nominal owl hasValue
      R propertyChainAxiom
      biaya nominal 1 sampai 4 menit
```

## 2. Perjalanan pekerjaan

```mermaid
mindmap
  root((Perjalanan proyek))
    Cakupan dan metode
      selaras slide KBR
      Noy McGuinness 10 langkah
      lingkup tidak terlalu lanjut
    Tiga lapisan
      T-Box skema
      A-Box 79 individu
      R-Box 8 aturan SWRL
    Reuse LKIF
      awal lkif-core plus norm
      ganti 10 modul terpisah
      norm dibuang
    Pellet gagal
      transitive plus subproperty
      buang 12 deklarasi transitive
      setelan plugin disamakan
    Terbukti di GUI
      R2 menurunkan dua kepala
      latar kuning inferred
    SROIQ D
      baseline SHIQ D
      tambah O nominal
      tambah R rantai
      hasil konsisten
      terbukti di GUI
    Demo dan CQ
      baca lewat SPARQL
      9 dari 9 deteksi
      10 dari 10 CQ
      verbalisasi 205 baris
    Dokumentasi
      README
      PROGRESS
      SKEMA BEDA
      kamus data
```
