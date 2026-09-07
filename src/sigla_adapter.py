"""
Adapter: decoded SigLA `data` structure -> kuro_protocol.Record/Token.

INDEPENDENT IMPLEMENTATION, written from this project's own schema
inspection (docs/SIGLA_SCHEMA_MAPPING.md), not copied from any external
project. Deliberately kept SEPARATE from src/lineara_adapter.py (see that
module and this project's own instructions) so that a CORPUS DIFFERENCE
(mwenge vs. SigLA) can never be confused with an ANALYSIS DIFFERENCE: both
adapters map into the exact same frozen kuro_protocol.Record/Token
structures, and neither modifies kuro_protocol.py itself.

SCOPE, STATED HONESTLY: this adapter implements what
docs/SIGLA_DATA_ADEQUACY_AUDIT.md classifies as AVAILABLE or DERIVABLE
(tablet ID, site, ordered sign sequence, KU-RO/KI-RO/PO-TO-KU-RO detection
via syllable-adjacency). Numerals, fractions, fraction confidence, and
damage/uncertainty extraction are classified OPEN or AMBIGUOUS in that
audit and are NOT implemented here -- every Record this adapter produces
currently has signgroup tokens only, no numeral tokens. This is a deliberate
scope limit for the schema-audit/adapter-construction phase (Phase 9 of
this project's own instructions forbids computing any H1 statistic this
round), not an oversight. A future phase that resolves the numeral/fraction
OPEN items should extend this module, not invent values now.

RULE B REMAINS BLOCKED. No commodity-ID handling of any kind is
implemented here.
"""
from __future__ import annotations

import os
import sys
from typing import Iterator, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kuro_protocol import Token, Record, TARGETS  # noqa: E402
from ocaml_marshal_decoder import OcamlBlock  # noqa: E402


# --------------------------------------------------------------- Map utilities
def _is_map_node(v) -> bool:
    """An OCaml stdlib Map.t node: Empty=0, Node(l,k,v,r,h) as a tag-0,
    5-field block. Format-level utility, reused from this project's own
    exploration of the real structure (docs/SIGLA_SCHEMA_MAPPING.md)."""
    return isinstance(v, OcamlBlock) and v.tag == 0 and len(v.fields) == 5


def map_items(root) -> Iterator[tuple]:
    """Inorder traversal of an OCaml Map.t, yielding (key, value) pairs in
    key order. Iterative (explicit stack), not recursive -- the real
    structure is deep enough to exceed Python's default recursion limit.

    Standard iterative-inorder algorithm: descend fully left (pushing each
    node visited along the way), then pop-yield-descend-right. An earlier
    version of this function pushed (right, yield, left) in sequence on a
    single stack, which yields a node's own (key, value) BEFORE its left
    subtree is fully exhausted whenever the left subtree is itself
    non-trivial -- caught by this project's own synthetic tests
    (tests/test_sigla_adapter.py), not by any real-data run.
    """
    stack = []
    current = root
    while stack or (current != 0 and _is_map_node(current)):
        while current != 0 and _is_map_node(current):
            stack.append(current)
            current = current.fields[0]  # left
        current = stack.pop()
        _left, key, value, right, _height = current.fields
        yield (key, value)
        current = right


def _opt(v):
    """OCaml option: None=0 (immediate), Some(x)=tag-0 1-field block."""
    if v == 0:
        return None
    if isinstance(v, OcamlBlock) and v.tag == 0 and len(v.fields) == 1:
        return v.fields[0]
    return v  # not an option-shaped value; return as-is rather than guess


# --------------------------------------------------------- document iteration
class SiglaDocument:
    __slots__ = ("tablet_id", "site", "period", "raw_value")

    def __init__(self, tablet_id: str, site: Optional[str], period: Optional[str], raw_value):
        self.tablet_id = tablet_id
        self.site = site
        self.period = period
        self.raw_value = raw_value


def iter_documents(data_top_value) -> Iterator[SiglaDocument]:
    """`data_top_value` is the decoded top-level value of the `data` blob
    (a 1-field block wrapping the document Map, per
    docs/SIGLA_SCHEMA_MAPPING.md). Yields one SiglaDocument per entry, in
    document-ID order.

    CORRECTION (found via real-document validation, Task 6 of this
    project's own schema-resolution round -- NOT caught by the earlier
    synthetic tests, whose fixtures modeled the *unwrapped* document tuple
    directly): the Map's value for each document is itself `Some(doc_tuple)`
    -- one extra OCaml `option` layer -- not the 5-field document tuple
    directly. This must be unwrapped via `_opt()` before the metadata tuple
    (doc_tuple.fields[0]) is reachable. Confirmed directly against real
    document "HT 13": the raw map value has tag=0, exactly 1 field, and
    that field is the 5-field document tuple.
    """
    doc_map = data_top_value.fields[0]
    for key, value in map_items(doc_map):
        tablet_id = key.decode("utf-8", errors="replace") if isinstance(key, bytes) else str(key)
        doc_tuple = _opt(value)
        site = None
        period = None
        if isinstance(doc_tuple, OcamlBlock) and len(doc_tuple.fields) >= 1:
            meta = doc_tuple.fields[0]
            if isinstance(meta, OcamlBlock) and len(meta.fields) >= 8:
                site_raw = meta.fields[2]
                if isinstance(site_raw, bytes):
                    site = site_raw.decode("utf-8", errors="replace")
                period_raw = _opt(meta.fields[7]) if len(meta.fields) > 7 else None
                if isinstance(period_raw, bytes):
                    period = period_raw.decode("utf-8", errors="replace")
        yield SiglaDocument(tablet_id, site, period, doc_tuple)


# ------------------------------------------------------ ordered sign sequence
def extract_ordered_signs(doc_value) -> list:
    """⚠ NOT VALIDATED -- DEMONSTRATED UNRELIABLE ON REAL DATA, DO NOT TRUST.

    Tested against real document "HT 13" (a ~15-syllable tablet):
    `_collect_indexed_entries` returned 129 "entries", with index value 1
    repeated 44 times and implausible outlier indices (704, 705 -- almost
    certainly misidentified pixel bounding-box coordinates, not sign
    indices, given the bbox format `[x,y,w,h]` observed elsewhere in this
    schema). This confirms the loose "small int + nested block" heuristic
    below matches unrelated substructure throughout the document (word
    groups, bounding boxes, etc.), not specifically the sign-attestation
    array. The output of this function must NOT be fed into
    `detect_targets`/`sigla_document_to_record` and trusted as a faithful
    ordered sign sequence -- see docs/SIGLA_DATA_ADEQUACY_AUDIT.md, Gate A
    = FAIL, and docs/SIGLA_SCHEMA_MAPPING.md for the full finding. Retained
    in this form, rather than deleted, only as a documented negative result
    and a starting point for whoever next identifies the correct field path
    for the true sign-attestation array.

    (Original design intent, preserved for context:) best-effort extraction
    of the per-document ordered sign-attestation array, returning a list of
    raw transliteration strings, in claimed index order, for entries where a
    transliteration could be resolved.
    """
    if not (isinstance(doc_value, OcamlBlock) and len(doc_value.fields) >= 5):
        return []
    sign_array_root = doc_value.fields[4]
    entries = _collect_indexed_entries(sign_array_root)
    out = []
    for idx, entry in sorted(entries, key=lambda p: p[0]):
        translit = _find_short_transliteration(entry)
        if translit is not None:
            out.append(translit)
    return out


def _collect_indexed_entries(node) -> list:
    """The sign-attestation array was observed (docs/SIGLA_SCHEMA_MAPPING.md)
    as a chain of blocks each carrying a small integer index among its
    fields. This walks the chain structure defensively -- if the real shape
    varies, entries simply won't be found (returns fewer/no entries) rather
    than raising, consistent with this adapter's OPEN-not-guessed policy."""
    entries = []
    stack = [node]
    seen = set()
    while stack:
        v = stack.pop()
        if isinstance(v, OcamlBlock):
            oid = id(v)
            if oid in seen:
                continue
            seen.add(oid)
            index_candidates = [f for f in v.fields if isinstance(f, int) and 0 < f < 10000]
            if index_candidates and any(isinstance(f, OcamlBlock) for f in v.fields):
                entries.append((index_candidates[0], v))
            stack.extend(v.fields)
    return entries


def _find_short_transliteration(node, max_depth=6) -> Optional[str]:
    """Depth-bounded search for a short (1-6 char) printable-ASCII bytes
    value nested under `node` -- the pattern observed for syllable
    transliterations (docs/SIGLA_SCHEMA_MAPPING.md). Conservative: many
    short strings in a sign record are NOT transliterations (sign class
    "AB", citation codes); this returns the first candidate found via a
    fixed, documented traversal order, not a confirmed field path. This is
    exactly the kind of thing later, real-data-verified work (out of scope
    this round per Phase 9) should replace with a precise field index once
    fully confirmed."""
    stack = [(node, 0)]
    seen = set()
    while stack:
        v, d = stack.pop()
        if d > max_depth:
            continue
        if isinstance(v, bytes):
            if 1 <= len(v) <= 6 and all(97 <= c <= 122 for c in v):  # lowercase a-z only
                return v.decode("ascii")
            continue
        if isinstance(v, OcamlBlock):
            oid = id(v)
            if oid in seen:
                continue
            seen.add(oid)
            for f in v.fields:
                stack.append((f, d + 1))
    return None


# --------------------------------------------------- target detection (word-level)
def detect_targets(ordered_transliterations: list) -> list:
    """CORPUS-SPECIFIC parsing logic (explicitly permitted by this
    project's own rules -- see module docstring): SigLA does not store
    KU-RO/KI-RO/PO-TO-KU-RO as a single joined string (confirmed,
    docs/SIGLA_SCHEMA_MAPPING.md); this detects them via sliding-window
    adjacency over the ordered syllable sequence, joining with '-' exactly
    as the canonical transliteration is written.

    Returns a list of (start_index, window_length, target_label) matches.
    Does NOT claim these windows are true word-groups -- only that their
    joined form matches one of the three declared target strings
    (H1_PROTOCOL.md #1). This is a documented heuristic, not a resolution
    of SigLA's real word-boundary structure (OPEN, see schema mapping).

    ⚠ Its input, in practice, comes from `extract_ordered_signs`, which is
    itself DEMONSTRATED UNRELIABLE on real data (see that function's
    docstring). A match found by this function is therefore only as
    trustworthy as its input sequence -- currently not trustworthy at all
    for real SigLA documents. This function's own adjacency logic is
    independently unit-tested (tests/test_sigla_adapter.py) and correct
    given a genuinely faithful input sequence; it is the *upstream*
    extraction that is not yet validated.
    """
    matches = []
    n = len(ordered_transliterations)
    windows = [(2, "KU-RO"), (2, "KI-RO"), (4, "PO-TO-KU-RO")]
    for length, label in windows:
        target_syllables = label.split("-")
        for i in range(n - length + 1):
            window = ordered_transliterations[i:i + length]
            if [s.lower() for s in window] == [s.lower() for s in target_syllables]:
                matches.append((i, length, label))
    return matches


def sigla_document_to_record(doc: SiglaDocument) -> Record:
    """Full pipeline: SiglaDocument -> kuro_protocol.Record. Produces
    signgroup tokens for the ordered sign sequence, with target-matched
    spans given the canonical target sign_ids (matching lineara_adapter's
    own convention) and all other signs given a generic placeholder id
    (the syllable string itself). NO numeral tokens are produced (see
    module docstring) -- every Record from this adapter currently has an
    empty arithmetically-testable sample if run through kuro_protocol,
    which is correct given the current OPEN status of numeral extraction,
    not a bug.
    """
    signs = extract_ordered_signs(doc.raw_value)
    matches = detect_targets(signs)
    match_starts = {}
    for start, length, label in matches:
        match_starts[start] = (length, label)

    tokens = []
    i = 0
    while i < len(signs):
        if i in match_starts:
            length, label = match_starts[i]
            tokens.append(Token(kind="signgroup", sign_ids=TARGETS[label]))
            i += length
        else:
            tokens.append(Token(kind="signgroup", sign_ids=(signs[i],)))
            i += 1
    return Record(tablet_id=doc.tablet_id, tokens=tokens)
