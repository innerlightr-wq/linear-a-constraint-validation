"""
Adapter: raw lineara.xyz tablet records -> kuro_protocol.Record/Token.

INDEPENDENT IMPLEMENTATION, written from this project's own schema
inspection (docs/SCHEMA_MAPPING.md), not copied from any external project.

Input shape (one dict per tablet, as produced by src/extract_raw_js.js, or
an equivalently-shaped synthetic/mock dict in tests):

    {
        "name": str,
        "site": str | None,
        "findspot": str | None,
        "scribe": str | None,
        "context": str | None,
        "support": str | None,
        "transliteratedWords": list[str],
    }

Implements exactly the four normalization rules declared in
docs/SCHEMA_MAPPING.md (N1-N4) and no others. No semantic interpretation is
introduced; `translatedWords` is never read by this module (it is dropped
upstream, in src/extract_raw_js.js, per the same documented rationale).
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kuro_protocol import Token, Record, TARGETS  # noqa: E402

WORD_SEPARATOR = "\U00010101"  # U+10101 AEGEAN WORD SEPARATOR DOT (𐄁), per annotations.js's own "word separator" tag
LINE_BREAK = "\n"

# Best-effort mapping of composed Unicode fraction glyphs to values, built
# from the Corazza et al. (2021) fraction system cited in the frozen H1
# protocol (docs/H1_PROTOCOL.md #3), using the same
# superscript-numerator / FRACTION SLASH / subscript-denominator Unicode
# convention directly observed for 1/2 in real data during schema mapping
# (docs/SCHEMA_MAPPING.md). ONLY "¹⁄₂" (1/2) has been
# confirmed present in a real tablet during this ingestion phase; the rest
# follow the same glyph-construction pattern but are NOT individually
# confirmed against real examples yet -- flagged OPEN, not asserted as
# verified.
_SUP = {"1": "¹", "2": "²", "3": "³", "4": "⁴",
        "8": "⁸", "10": "¹⁰", "16": "¹⁶",
        "20": "²⁰", "30": "³⁰", "40": "⁴⁰",
        "60": "⁶⁰"}
_SLASH = "⁄"
_SUB = {"2": "₂", "4": "₄", "8": "₈", "10": "₁₀",
         "16": "₁₆", "20": "₂₀", "30": "₃₀",
         "40": "₄₀", "60": "₆₀"}

FRACTION_GLYPHS = {}
for num, den in [(1, 2), (1, 4), (1, 8), (1, 10), (1, 16), (1, 20), (1, 30),
                  (1, 40), (1, 60)]:
    glyph = _SUP[str(num)] + _SLASH + _SUB[str(den)]
    FRACTION_GLYPHS[glyph] = num / den

_NUMERAL_RE = re.compile(r"^\d+$")
_DAMAGE_CHARS = re.compile(r"[\[\]?]")


def is_numeral_string(s: str) -> bool:
    return bool(_NUMERAL_RE.match(s))


def is_fraction_glyph(s: str) -> bool:
    return s in FRACTION_GLYPHS


def is_damaged_string(s: str) -> bool:
    """N.B.: conservative and undifferentiated -- any of '[', ']', '?'
    anywhere in the raw string is treated as DAMAGED (protocol §6). This
    does not distinguish physical damage from disputed reading; that
    distinction is not confirmed available in this source (see
    docs/SCHEMA_MAPPING.md) and is not invented here."""
    return bool(_DAMAGE_CHARS.search(s))


def target_sign_ids_for(word: str) -> tuple | None:
    """N4: match by exact transliteration string against the declared
    fallback (H1_PROTOCOL.md §1), since GORILA sign IDs are unavailable in
    this source. Returns the canonical target tuple if `word` (stripped of
    damage markers) is exactly one of the three declared target strings,
    else None."""
    cleaned = _DAMAGE_CHARS.sub("", word)
    for label, ids in TARGETS.items():
        if cleaned == label:
            return ids
    return None


def raw_tablet_to_record(raw: dict, fallback_log: list | None = None) -> Record:
    """Convert one raw tablet dict into a kuro_protocol.Record.

    `fallback_log`, if given, has one entry appended per tablet noting that
    N4 (transliteration-string fallback matching, not GORILA sign-ID
    matching) was used -- per H1_PROTOCOL.md §1's explicit requirement that
    this fact be logged per-tablet, not silently absorbed.
    """
    tablet_id = raw["name"]
    words = raw.get("transliteratedWords") or []
    tokens: list[Token] = []

    for w in words:
        if w == LINE_BREAK:
            tokens.append(Token(kind="ruling"))                      # N1
            continue
        if w == WORD_SEPARATOR:
            continue                                                  # N3
        if is_fraction_glyph(w):
            value = FRACTION_GLYPHS[w]
            if tokens and tokens[-1].kind == "numeral":               # N2
                frac_list = tokens[-1].fractions or []
                frac_list.append({"value": value, "confidence": None})
                tokens[-1].fractions = frac_list
            else:
                tokens.append(Token(kind="numeral",
                                     fractions=[{"value": value, "confidence": None}]))
            continue
        if is_numeral_string(w):
            damaged = is_damaged_string(w)
            tokens.append(Token(kind="numeral", value=float(w), damaged=damaged))
            continue

        # signgroup
        damaged = is_damaged_string(w)
        target_ids = target_sign_ids_for(w)
        if target_ids is not None:
            tokens.append(Token(kind="signgroup", sign_ids=target_ids, damaged=damaged))
        else:
            cleaned = _DAMAGE_CHARS.sub("", w)
            tokens.append(Token(kind="signgroup", sign_ids=(cleaned,), damaged=damaged))

    if fallback_log is not None:
        fallback_log.append({
            "tablet_id": tablet_id,
            "note": "N4: matched via transliteration string, GORILA sign ID unavailable",
        })

    return Record(tablet_id=tablet_id, tokens=tokens)
