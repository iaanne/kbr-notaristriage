"""Lapisan baca-tulis di atas ontology Notaris Triage.

Pola proyek ini: fakta selalu datang dari ontology, tidak pernah dari teks
karangan. Modul ini dipakai bersama oleh demo/, notaris/, dan eval/.
"""

from pathlib import Path

#: Akar repo, satu tingkat di atas paket ini.
AKAR = Path(__file__).resolve().parent.parent

#: T-Box: skema dan aturan SWRL, tanpa individu.
TTL = AKAR / "ontology" / "notaris-triage.ttl"

#: A-Box: seluruh individu domain, dipisah dari skema.
ABOX = AKAR / "data" / "abox.ttl"

#: Folder data. Sebagian isinya hasil generate, bukan sumber kebenaran.
DATA = AKAR / "data"

__all__ = ["AKAR", "TTL", "ABOX", "DATA"]