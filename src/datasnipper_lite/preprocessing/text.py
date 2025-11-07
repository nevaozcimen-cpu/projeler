"""
Metin önişleme yardımcıları.

Eşleştirme motorunun daha tutarlı sonuç üretmesi için metin normalizasyonu, sadeleştirme ve
token seviyesinde temizleme adımları sağlar.
"""

from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str, *, lowercase: bool = True, collapse_spaces: bool = True) -> str:
    """
    Temel metin normalizasyonu.

    Args:
        text: Kaynak metin.
        lowercase: Küçük harfe indirgeme bayrağı.
        collapse_spaces: Birden fazla boşluğu tek boşlukta birleştirme.
    """

    if lowercase:
        text = text.lower()
    if collapse_spaces:
        text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()
