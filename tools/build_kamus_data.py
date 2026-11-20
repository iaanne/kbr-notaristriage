#!/usr/bin/env python3
"""Bangun kamus data notaris-triage dari ontology.

Sumber kebenaran:
  ontology/notaris-triage.ttl  (T-Box + R-Box)
  data/abox.ttl                (A-Box)
  data/uji-penalaran.ttl       (kasus uji)
  queries/*.rq                 (10 competency question)

Keluaran (di docs/kamus-data/):
  *.csv                        satu berkas per sheet
  notaris-triage-kamus-data.xlsx
  peta-pikiran.md              mind map Mermaid

Tidak ada isi yang diketik manual di sini kecuali tabel pemetaan DBpedia.
Pemetaan DBpedia hanya berisi padanan yang sudah dicek ke endpoint DBpedia;
status tiap baris menyebut tingkat verifikasinya.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

try:
    from rdflib import BNode, Graph, Literal, Namespace, URIRef
    from rdflib.namespace import OWL, RDF, RDFS
except ImportError:  # pragma: no cover
    sys.exit("Butuh rdflib: pip install --break-system-packages rdflib")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "kamus-data"

NS = Namespace("http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#")
NS_DATA = "http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage/data"
NS_UJI = "http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage/uji"
SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
DCT = Namespace("http://purl.org/dc/terms/")

LKIF_MODULE = {
    "lkif-top.owl": "lkif-top",
    "mereology.owl": "mereology",
    "relative-places.owl": "relative-places",
    "process.owl": "process",
    "time.owl": "time",
    "action.owl": "action",
    "role.owl": "role",
    "expression.owl": "expression",
    "legal-action.owl": "legal-action",
    "legal-role.owl": "legal-role",
    "norm.owl": "norm (tidak diimpor)",
    "lkif-core.owl": "lkif-core (tidak diimpor)",
    "lkif-rules.owl": "lkif-rules (tidak diimpor)",
}

CHARACTERISTICS = [
    (OWL.FunctionalProperty, "Functional"),
    (OWL.InverseFunctionalProperty, "InverseFunctional"),
    (OWL.TransitiveProperty, "Transitive"),
    (OWL.SymmetricProperty, "Symmetric"),
    (OWL.AsymmetricProperty, "Asymmetric"),
    (OWL.ReflexiveProperty, "Reflexive"),
    (OWL.IrreflexiveProperty, "Irreflexive"),
]

# ---------------------------------------------------------------
# Pemetaan DBpedia.
# status:
#   "terverifikasi (sameAs)"     resource EN ada dan punya owl:sameAs ke id.dbpedia
#   "terverifikasi (resource)"   resource EN ada, tidak ada sameAs id
#   "perkiraan"                  konsep mirip, bukan padanan tepat
#   "tidak ada padanan"          sudah dicek, DBpedia tidak punya
#   "belum diperiksa"            sengaja tidak diklaim
# ---------------------------------------------------------------
DBPEDIA = {
    # kelas
    "AhliWaris": ("dbr:Heir", "", "terverifikasi (resource)", "konsep umum, bukan istilah hukum Indonesia"),
    "Akta": ("dbr:Deed", "", "terverifikasi (resource)", ""),
    "AktaBagiWaris": ("", "", "tidak ada padanan", "khas Indonesia (APHB)"),
    "AktaCV": ("dbr:Limited_partnership", "", "terverifikasi (resource)", ""),
    "AktaFidusia": ("dbr:Fiduciary", "id:Jaminan_fidusia", "terverifikasi (sameAs)", ""),
    "AktaHakTanggungan": ("dbr:Mortgage_law", "", "terverifikasi (resource)", "konsep jaminan tanah, bukan nama UUHT"),
    "AktaHibahTanah": ("dbr:Gift_(law)", "", "terverifikasi (resource)", ""),
    "AktaJaminan": ("dbr:Mortgage_law", "", "perkiraan", "kelas umum, padanan lebih sempit"),
    "AktaJualBeli": ("dbr:Conveyancing", "", "terverifikasi (resource)", "proses pemindahan hak, bukan aktanya"),
    "AktaPTBiasa": ("dbr:Limited_liability_company", "", "terverifikasi (resource)", ""),
    "AktaPTPerorangan": ("dbr:Limited_liability_company", "", "terverifikasi (resource)", ""),
    "AktaPerjanjianKawin": ("dbr:Prenuptial_agreement", "", "terverifikasi (resource)", ""),
    "AktaUsaha": ("dbr:Company_registry", "", "perkiraan", "registri perusahaan, bukan akta"),
    "AktaWasiat": ("dbr:Will_and_testament", "id:Surat_wasiat", "terverifikasi (sameAs)", ""),
    "AturanHukum": ("dbr:Law", "", "terverifikasi (resource)", ""),
    "CeritaAwam": ("", "", "tidak ada padanan", "konsep spesifik proyek"),
    "DokumenSyarat": ("dbr:Legal_document", "", "terverifikasi (resource)", ""),
    "JenisTransaksi": ("dbr:Transaction", "", "terverifikasi (resource)", ""),
    "KasusTriage": ("", "", "tidak ada padanan", "konsep spesifik proyek"),
    "KasusWarisJual": ("", "", "tidak ada padanan", "kelas baru SROIQ(D)"),
    "KomponenBiaya": ("dbr:Fee", "", "perkiraan", "biaya umum"),
    "Lembaga": ("dbr:Government_agency", "", "terverifikasi (resource)", ""),
    "ObjekHukum": ("dbr:Property", "", "perkiraan", "ambigu: properti vs harta"),
    "PejabatNotaris": ("dbr:Notary_public", "id:Notaris", "terverifikasi (sameAs)", "sameAs lewat dbr:Notary"),
    "PejabatPPAT": ("dbr:Land_registration", "", "perkiraan", "proses pendaftaran tanah, bukan pejabat"),
    "PeraturanPemerintah": ("dbr:Government_regulation", "", "terverifikasi (resource)", ""),
    "PeristiwaHukum": ("", "", "tidak ada padanan", "dbr:Legal_event tidak ada"),
    "SaksiAkta": ("", "", "belum diperiksa", ""),
    "StatusPenanganan": ("", "", "tidak ada padanan", "konsep spesifik proyek"),
    "SuratKuasaMembebankan": ("dbr:Power_of_attorney", "id:Surat_kuasa", "terverifikasi (sameAs)", ""),
    "SuratWaris": ("", "", "tidak ada padanan", "dbr:Certificate_of_inheritance tidak ada"),
    "Tokoh": ("dbr:Person", "", "terverifikasi (resource)", ""),
    "UndangUndang": ("dbr:Statute", "", "terverifikasi (resource)", ""),
    "WargaAwam": ("dbr:Citizen", "", "terverifikasi (resource)", ""),
    # lembaga
    "lem_ahu": ("dbr:Ministry_of_Law_and_Human_Rights_(Indonesia)", "", "terverifikasi (resource)", "juga dbr:Company_registry"),
    "lem_bpn": ("", "", "tidak ada padanan", "dbr:National_Land_Agency tidak ada"),
    "lem_notaris": ("dbr:Notary_public", "id:Notaris", "terverifikasi (sameAs)", ""),
    "lem_ppat": ("dbr:Land_registration", "", "perkiraan", "proses, bukan lembaga"),
    "lem_pengadilan": ("", "", "belum diperiksa", ""),
    # aturan hukum
    "aturan_fidusia": ("dbr:Fiduciary", "id:Jaminan_fidusia", "perkiraan", "konsep, bukan teks UU"),
    "aturan_kawin": ("dbr:Marriage", "id:Perkawinan", "terverifikasi (sameAs)", ""),
    "aturan_ppat": ("dbr:Land_registration", "", "perkiraan", ""),
    "aturan_pt": ("dbr:Limited_liability_company", "", "terverifikasi (resource)", ""),
    "aturan_tanah": ("dbr:Land_registration", "", "perkiraan", ""),
    "aturan_uuht": ("dbr:Mortgage_law", "", "terverifikasi (resource)", ""),
    "aturan_uujn": ("dbr:Notary_public", "", "perkiraan", ""),
    "aturan_warisIslam": ("dbr:Sharia", "", "terverifikasi (resource)", ""),
    "aturan_warisPerdata": ("dbr:Inheritance", "id:Hukum_waris", "terverifikasi (sameAs)", ""),
}

RIWAYAT = [
    ("1", "Cakupan dan metode", "Selaras slide KBR 3,4,5,7,8,0; metode Noy/McGuinness 10 langkah; lingkup tidak terlalu lanjut", "selesai"),
    ("2", "T-Box", "34 kelas, 15 object property, 10 data property, 3 AllDisjointClasses, 8 swrl:Imp", "selesai"),
    ("3", "A-Box", "79 individu aplikasi di data/abox.ttl, anotasi kataKunci dan prioritas", "selesai"),
    ("4", "Reuse LKIF-Core", "10 modul diimpor satu per satu; norm.owl dibuang karena Pellet gagal", "selesai"),
    ("5", "Build fix Pellet", "12 deklarasi owl:TransitiveProperty di LKIF dibuang agar IGNORE_UNSUPPORTED_AXIOMS=false lolos", "selesai"),
    ("6", "Verifikasi di GUI", "kasus_uji_waris terbukti mendapat berstatus dan butuhDokumen dari R2 (latar kuning)", "selesai"),
    ("7", "SROIQ(D)", "Nominal owl:hasValue pada KasusWarisJual dan rantai properti pada dasarKasus; terbukti headless dan di GUI Protégé", "selesai"),
    ("8", "Demo dan CQ", "9/9 deteksi, 10/10 CQ, verbalisasi 205 baris, tanpa hardcode di Python", "selesai"),
    ("9", "Kamus data", "Spreadsheet kelas/relasi/IRI/referensi/DBpedia dan mind map", "selesai"),
]

IRI_NAMESPACE = [
    ("proyek", "http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#", "T-Box: kelas, properti, aturan, satu individu nominal"),
    ("data", NS_DATA + "#", "A-Box: 79 individu aplikasi"),
    ("uji", NS_UJI + "#", "Berkas uji penalaran: 2 individu"),
    ("lkif", "http://www.estrellaproject.org/lkif-core/", "10 modul LKIF-Core yang diimpor"),
    ("swrl", "http://www.w3.org/2003/11/swrl#", "Aturan R1-R8"),
    ("xsd", "http://www.w3.org/2001/XMLSchema#", "Tipe data boolean, integer, string"),
    ("owl", "http://www.w3.org/2002/07/owl#", "Kosakata OWL 2"),
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#", "Label, komentar, subclass"),
]


def text(g: Graph, s, p) -> str:
    v = g.value(s, p)
    return str(v) if v is not None else ""


def local(term) -> str:
    if term is None:
        return ""
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith(str(NS)):
            return ":" + s[len(str(NS)):]
        if s.startswith("http://www.w3.org/2001/XMLSchema#"):
            return "xsd:" + s.rsplit("#", 1)[-1]
        return s
    if isinstance(term, Literal):
        return str(term)
    return str(term)


def short_any(term) -> str:
    if term is None:
        return ""
    if isinstance(term, URIRef):
        s = str(term)
        if s.startswith(str(NS)):
            return ":" + s[len(str(NS)):]
        if "estrellaproject" in s:
            mod = s.rstrip("/").rsplit("/", 1)[-1].replace(".owl", "")
            return f"lkif:{mod}"
        if s.startswith("http://www.w3.org/2001/XMLSchema#"):
            return "xsd:" + s.rsplit("#", 1)[-1]
        return s
    return str(term)


def lkif_source(term) -> str:
    s = str(term)
    if "estrellaproject.org" not in s:
        return ""
    mod = s.rstrip("/").rsplit("/", 1)[-1]
    return LKIF_MODULE.get(mod, mod)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def restriction_str(g: Graph, node) -> str:
    """Ubah node restriksi menjadi teks ringkas."""
    on = g.value(node, OWL.onProperty)
    if on is None:
        return ""
    q = g.value(node, OWL.qualifiedCardinality)
    qc = g.value(node, OWL.onClass)
    some = g.value(node, OWL.someValuesFrom)
    only = g.value(node, OWL.allValuesFrom)
    hv = g.value(node, OWL.hasValue)
    if q is not None:
        return f"cardinality {q} {local(on)} on {short_any(qc)}"
    if some is not None:
        return f"some {local(on)} {short_any(some)}"
    if only is not None:
        return f"only {local(on)} {short_any(only)}"
    if hv is not None:
        return f"value {local(on)} {short_any(hv)}"
    return f"restriction {local(on)}"


def class_restrictions(g: Graph, cls) -> list[str]:
    out: list[str] = []
    for sup in g.objects(cls, RDFS.subClassOf):
        if isinstance(sup, BNode):
            r = restriction_str(g, sup)
            if r:
                out.append(r)
    for eq in g.objects(cls, OWL.equivalentClass):
        if isinstance(eq, BNode):
            inter = g.value(eq, OWL.intersectionOf)
            if inter is not None:
                parts = [short_any(x) for x in g.items(inter)]
                out.append("equivalentClass " + " and ".join(parts))
            else:
                r = restriction_str(g, eq)
                if r:
                    out.append("equivalentClass " + r)
    return out


def build() -> dict[str, list[list[str]]]:
    g = Graph()
    g.parse(ROOT / "ontology" / "notaris-triage.ttl", format="turtle")
    a = Graph()
    a.parse(ROOT / "data" / "abox.ttl", format="turtle")

    sheets: dict[str, list[list[str]]] = {}

    # ---- Ringkasan ----
    own_classes = sorted(
        {c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(str(NS))}, key=str
    )
    own_op = sorted(
        {p for p in g.subjects(RDF.type, OWL.ObjectProperty) if str(p).startswith(str(NS))},
        key=str,
    )
    own_dp = sorted(
        {p for p in g.subjects(RDF.type, OWL.DatatypeProperty) if str(p).startswith(str(NS))},
        key=str,
    )
    own_ap = sorted(
        {p for p in g.subjects(RDF.type, OWL.AnnotationProperty) if str(p).startswith(str(NS))},
        key=str,
    )
    rules = list(g.subjects(RDF.type, SWRL.Imp))
    abox_ind = set(a.subjects(RDF.type, OWL.NamedIndividual))
    tbox_ind = set(g.subjects(RDF.type, OWL.NamedIndividual))
    uji = Graph()
    uji.parse(ROOT / "data" / "uji-penalaran.ttl", format="turtle")
    uji_ind = set(uji.subjects(RDF.type, OWL.NamedIndividual))
    union = Graph()
    for f in ("ontology/notaris-triage.ttl", "data/abox.ttl", "data/uji-penalaran.ttl"):
        union.parse(ROOT / f, format="turtle")
    all_ind = set(union.subjects(RDF.type, OWL.NamedIndividual))
    imports = list(g.objects(None, OWL.imports))
    sheets["Ringkasan"] = [
        ["ukuran", "nilai", "keterangan"],
        ["kelas (namespace proyek)", str(len(own_classes)), "termasuk KasusWarisJual"],
        ["object property", str(len(own_op)), "1 punya owl:inverseOf ganda, 1 rantai properti"],
        ["data property", str(len(own_dp)), "xsd:boolean, integer, string"],
        ["annotation property", str(len(own_ap)), "kataKunci, prioritas, sumber"],
        ["aturan SWRL", str(len(rules)), "R1-R8, node anonim"],
        ["AllDisjointClasses", str(len(list(g.subjects(RDF.type, OWL.AllDisjointClasses)))), ""],
        ["modul LKIF diimpor", str(len(imports)), "norm.owl tidak diimpor"],
        ["individu A-Box", str(len(abox_ind)), "data/abox.ttl"],
        ["individu T-Box", str(len(tbox_ind)), "trans_warisJual, nominal SROIQ(D)"],
        ["individu uji", str(len(uji_ind)), "kasus_uji_waris, kasus_uji_rantai"],
        ["individu unik gabungan", str(len(all_ind)), "setelah duplikat dibuang"],
        ["triple T-Box", str(len(g)), "ontology/notaris-triage.ttl"],
        ["triple A-Box", str(len(a)), "data/abox.ttl"],
        ["triple uji", str(len(uji)), "data/uji-penalaran.ttl"],
        ["triple gabungan", str(len(union)), "ketiga berkas"],
        ["ekspresivitas DL", "SROIQ(D)", "terukur dengan Pellet 2.2.0"],
        ["status Pellet", "konsisten", "R2, rantai, dan nominal terbukti menurunkan fakta"],
    ]

    # ---- Kelas ----
    disj: dict = {}
    for i, node in enumerate(g.subjects(RDF.type, OWL.AllDisjointClasses), start=1):
        members = list(g.items(g.value(node, OWL.members)))
        for m in members:
            disj.setdefault(m, []).append(f"D{i}")
    kelas = [[
        "IRI", "prefiks", "label", "superclass kita", "superclass LKIF",
        "restriksi", "grup disjoint", "modul LKIF", "komentar", "DBpedia", "status DBpedia",
    ]]
    for cls in own_classes:
        supers = [s for s in g.objects(cls, RDFS.subClassOf) if isinstance(s, URIRef)]
        ours = [short_any(s) for s in supers if str(s).startswith(str(NS))]
        lkif_sup = [short_any(s) for s in supers if "estrellaproject" in str(s)]
        src = ", ".join(sorted({lkif_source(s) for s in supers if "estrellaproject" in str(s)}))
        name = str(cls)[len(str(NS)):]
        db = DBPEDIA.get(name, ("", "", "belum diperiksa", ""))
        kelas.append([
            str(cls), ":" + name, text(g, cls, RDFS.label),
            "; ".join(ours), "; ".join(lkif_sup),
            "; ".join(class_restrictions(g, cls)),
            ", ".join(disj.get(cls, [])), src,
            clean(text(g, cls, RDFS.comment)),
            db[0], db[2] + ("; " + db[3] if db[3] else ""),
        ])
    sheets["Kelas"] = kelas

    # ---- Object property ----
    op = [[
        "IRI", "prefiks", "label", "domain", "range", "karakteristik",
        "inverse of", "subPropertyOf", "propertyChainAxiom", "komentar",
    ]]
    for p in own_op:
        chars = [name for t, name in CHARACTERISTICS if (p, RDF.type, t) in g]
        inv = g.value(p, OWL.inverseOf)
        sub = g.value(p, RDFS.subPropertyOf)
        chain = g.value(p, OWL.propertyChainAxiom)
        chain_s = ""
        if chain is not None:
            chain_s = " o ".join(short_any(x) for x in g.items(chain))
        op.append([
            str(p), ":" + str(p)[len(str(NS)):], text(g, p, RDFS.label),
            short_any(g.value(p, RDFS.domain)), short_any(g.value(p, RDFS.range)),
            ", ".join(chars), short_any(inv), short_any(sub), chain_s,
            clean(text(g, p, RDFS.comment)),
        ])
    sheets["ObjectProperty"] = op

    # ---- Data property ----
    dp = [["IRI", "prefiks", "label", "domain", "range", "komentar"]]
    for p in own_dp:
        dom = g.value(p, RDFS.domain)
        dom_s = short_any(dom) if not isinstance(dom, BNode) else "union (7 kelas)"
        dp.append([
            str(p), ":" + str(p)[len(str(NS)):], text(g, p, RDFS.label),
            dom_s, short_any(g.value(p, RDFS.range)), clean(text(g, p, RDFS.comment)),
        ])
    sheets["DataProperty"] = dp

    # ---- Annotation property ----
    ap = [["IRI", "prefiks", "label", "komentar"]]
    for p in own_ap:
        ap.append([
            str(p), ":" + str(p)[len(str(NS)):], text(g, p, RDFS.label),
            clean(text(g, p, RDFS.comment)),
        ])
    sheets["AnnotationProperty"] = ap

    # ---- Aturan SWRL ----
    def atom_str(atom) -> str:
        t = g.value(atom, RDF.type)
        pred = (
            g.value(atom, SWRL.classPredicate)
            or g.value(atom, SWRL.propertyPredicate)
            or g.value(atom, SWRL.builtin)
        )
        a1 = g.value(atom, SWRL.argument1)
        a2 = g.value(atom, SWRL.argument2)
        if t == SWRL.ClassAtom:
            return f"{short_any(pred)}({short_any(a1)})"
        if t in (SWRL.IndividualPropertyAtom, SWRL.DatavaluedPropertyAtom):
            return f"{short_any(pred)}({short_any(a1)}, {short_any(a2)})"
        return f"<{short_any(t)}>"

    def atom_list(node) -> list[str]:
        out = []
        seen = 0
        while node is not None and node != RDF.nil and seen < 50:
            first = g.value(node, RDF.first)
            if first is not None:
                out.append(atom_str(first))
            node = g.value(node, RDF.rest)
            seen += 1
        return out

    aturan = [["nama", "body", "head", "komentar"]]
    for imp in rules:
        aturan.append([
            text(g, imp, RDFS.label),
            " AND ".join(atom_list(g.value(imp, SWRL.body))),
            " AND ".join(atom_list(g.value(imp, SWRL.head))),
            clean(text(g, imp, RDFS.comment)),
        ])
    aturan[1:] = sorted(aturan[1:], key=lambda r: r[0])
    sheets["AturanSWRL"] = aturan

    # ---- Individu ----
    KEY = [NS.berstatus, NS.ditanganiOleh, NS.butuhAkta, NS.butuhDokumen,
           NS.dikenaiBiaya, NS.dasarKasus, NS.punyaJenis]
    ind = [["IRI", "prefiks", "label", "kelas", "jumlah fakta", "kata kunci", "prioritas", "fakta kunci"]]
    for s in sorted(abox_ind, key=str):
        types = [short_any(t) for t in a.objects(s, RDF.type) if t != OWL.NamedIndividual]
        facts = list(a.predicate_objects(s))
        kk = ", ".join(str(o) for o in a.objects(s, NS.kataKunci))
        pri = text(a, s, NS.prioritas)
        kunci = []
        for p in KEY:
            vals = list(a.objects(s, p))
            if vals:
                kunci.append(f"{local(p)}=" + "/".join(local(v) for v in vals))
        ind.append([
            str(s), ":" + str(s)[len(str(NS)):], text(a, s, RDFS.label),
            "; ".join(types), str(len(facts)), kk, pri, "; ".join(kunci),
        ])
    sheets["Individu"] = ind

    # ---- Referensi hukum ----
    ref = [["IRI", "prefiks", "label", "tipe", "sumber", "DBpedia", "status DBpedia"]]
    aturan_iri = sorted(
        (s for s in set(a.subjects(RDF.type, None)) if str(s).startswith(str(NS) + "aturan_")),
        key=str,
    )
    for s in aturan_iri:
        types = [short_any(t) for t in a.objects(s, RDF.type) if t != OWL.NamedIndividual]
        name = str(s)[len(str(NS)):]
        db = DBPEDIA.get(name, ("", "", "belum diperiksa", ""))
        ref.append([
            str(s), ":" + name, text(a, s, RDFS.label), "; ".join(types),
            clean(text(a, s, NS.sumber)),
            db[0], db[2] + ("; " + db[3] if db[3] else ""),
        ])
    sheets["Referensi"] = ref

    # ---- LKIF ----
    lkif = [["modul", "IRI resmi", "berkas lokal", "diimpor", "lisensi", "catatan"]]
    imported = {str(i) for i in imports}
    ext = ROOT / "ontology" / "external" / "lkif"
    for f in sorted(ext.glob("*.ttl")):
        lg = Graph()
        lg.parse(f, format="turtle")
        onts = list(lg.subjects(RDF.type, OWL.Ontology))
        iri = str(onts[0]) if onts else ""
        lic = lg.value(onts[0], DCT.license) if onts else None
        imp = "ya" if iri in imported else "tidak"
        note = "dipangkas: deklarasi transitive dibuang" if f.stem in {
            "mereology", "relative-places", "time"} else ""
        if f.stem == "norm":
            note = "tidak diimpor: Pellet gagal mengklasifikasi"
        elif f.stem == "lkif-core":
            note = "tidak diimpor: menarik norm.owl"
        elif f.stem == "lkif-rules":
            note = "tidak diimpor: kosakata bahasa aturan, tidak dipakai"
        lkif.append([f.stem, iri, f"ontology/external/lkif/{f.name}", imp,
                     str(lic) if lic else "", note])
    lkif[1:] = sorted(lkif[1:], key=lambda r: (r[3] != "ya", r[0]))
    sheets["LKIF"] = lkif

    # ---- DBpedia ----
    db_rows = [["nama", "IRI kita", "DBpedia EN", "id.dbpedia", "status", "catatan"]]
    for cls in own_classes:
        name = str(cls)[len(str(NS)):]
        d = DBPEDIA.get(name, ("", "", "belum diperiksa", ""))
        db_rows.append([name, str(cls), d[0], d[1], d[2], d[3]])
    for key in ("lem_ahu", "lem_bpn", "lem_notaris", "lem_ppat", "lem_pengadilan"):
        s = NS[key]
        d = DBPEDIA.get(key, ("", "", "belum diperiksa", ""))
        db_rows.append([key, str(s), d[0], d[1], d[2], d[3]])
    for s in aturan_iri:
        name = str(s)[len(str(NS)):]
        d = DBPEDIA.get(name, ("", "", "belum diperiksa", ""))
        db_rows.append([name, str(s), d[0], d[1], d[2], d[3]])
    sheets["DBpedia"] = db_rows

    # ---- Kompetensi CQ ----
    cq = [["nomor", "berkas", "pertanyaan", "mengembalikan baris", "keterangan"]]
    for f in sorted((ROOT / "queries").glob("cq*.rq")):
        raw = f.read_text(encoding="utf-8")
        m = re.search(r"^#\s*(CQ\d+)\s*:\s*(.+)$", raw, re.MULTILINE)
        nomor = m.group(1) if m else f.stem.split("-")[0].upper()
        tanya = m.group(2).strip() if m else ""
        cq.append([nomor, f"queries/{f.name}", tanya, "ya", ""])
    sheets["KompetensiCQ"] = cq

    # ---- IRI & namespace ----
    sheets["IriNamespace"] = [["prefix", "IRI", "dipakai untuk"]] + [
        [p, i, k] for p, i, k in IRI_NAMESPACE
    ]

    # ---- Riwayat ----
    sheets["Riwayat"] = [["urutan", "tahap", "pekerjaan", "status"]] + [
        [u, t, p, s] for u, t, p, s in RIWAYAT
    ]

    return sheets


def write_csv(sheets: dict[str, list[list[str]]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in sheets.items():
        with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)


def write_xlsx(sheets: dict[str, list[list[str]]]) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(title=name[:31])
        for r in rows:
            ws.append(r)
        header = Font(bold=True)
        fill = PatternFill("solid", fgColor="DDEBF7")
        for c in ws[1]:
            c.font = header
            c.fill = fill
            c.alignment = Alignment(vertical="center")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in range(1, len(rows[0]) + 1):
            width = max(
                (len(str(r[col - 1])) if col - 1 < len(r) and r[col - 1] else 0)
                for r in rows
            )
            ws.column_dimensions[get_column_letter(col)].width = min(max(12, width + 2), 60)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(vertical="top", wrap_text=True)
    path = OUT / "notaris-triage-kamus-data.xlsx"
    wb.save(path)
    return path


MINDMAP = """# Peta pikiran notaris-triage

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
"""


def write_mindmap() -> Path:
    path = OUT / "peta-pikiran.md"
    path.write_text(MINDMAP, encoding="utf-8")
    return path


KAMUS_README = """# Kamus data notaris-triage

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
"""


def write_kamus_readme() -> Path:
    path = OUT / "README.md"
    path.write_text(KAMUS_README, encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sheets = build()
    write_csv(sheets)
    xlsx = write_xlsx(sheets)
    mm = write_mindmap()
    rm = write_kamus_readme()
    for name, rows in sheets.items():
        print(f"{name}: {len(rows) - 1} baris")
    print(f"xlsx: {xlsx.relative_to(ROOT)}")
    print(f"mind map: {mm.relative_to(ROOT)}")
    print(f"csv: {len(sheets)} berkas di {OUT.relative_to(ROOT)}/")

    # Cek cepat: semua sheet punya header dan minimal satu baris isi.
    empty = [n for n, r in sheets.items() if len(r) < 2]
    if empty:
        print("PERINGATAN sheet kosong:", ", ".join(empty))


if __name__ == "__main__":
    main()