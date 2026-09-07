#!/usr/bin/env python3
"""
Bounded SigLA schema explorer. SCHEMA INSPECTION ONLY -- not a statistics
tool, not an H1 driver, and has NO corpus-wide mode by design (there is no
flag to iterate "all documents" or count anything across the corpus).

Usage (explicit tablet IDs required -- no default, no wildcard):

    python3 src/explore_sigla_schema.py --tablets "HT 13" "HT 104"
    python3 src/explore_sigla_schema.py --tablets "HT 13" --depth 8
    python3 src/explore_sigla_schema.py --list-signs 44 21 8   # signs blob, by number

Prints a depth-bounded structural dump of the named document(s)/sign(s)
only. Does not compute or print any frequency, rate, or aggregate count.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.setrecursionlimit(200000)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocaml_marshal_decoder import decode, extract_and_decode_ocaml_blob, OcamlBlock  # noqa: E402
import sigla_adapter as sa  # noqa: E402

DEFAULT_RAW_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw", "sigla", "database.js")


def load(raw_path=DEFAULT_RAW_PATH):
    with open(raw_path, "rb") as f:
        content = f.read()
    data_val, _ = decode(extract_and_decode_ocaml_blob(content, b"data"))
    signs_val, _ = decode(extract_and_decode_ocaml_blob(content, b"signs"))
    return data_val, signs_val


def safe_repr(v, maxdepth=8, depth=0, maxlist=40):
    if depth >= maxdepth:
        return "..."
    if isinstance(v, bytes):
        try:
            return repr(v.decode("utf-8"))
        except UnicodeDecodeError:
            return repr(v)
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, OcamlBlock):
        fields = v.fields[:maxlist]
        inner = ", ".join(safe_repr(f, maxdepth, depth + 1, maxlist) for f in fields)
        suffix = ", ..." if len(v.fields) > maxlist else ""
        return f"B{v.tag}[{inner}{suffix}]"
    return repr(v)


def dump_document(data_val, tablet_id: str, depth: int):
    doc_map = data_val.fields[0]
    for key, value in sa.map_items(doc_map):
        kid = key.decode("utf-8", errors="replace") if isinstance(key, bytes) else str(key)
        if kid == tablet_id:
            print(f"=== document {tablet_id!r} (depth<= {depth}) ===")
            print(safe_repr(value, maxdepth=depth))
            print()
            print(f"--- extracted ordered short-string candidates (adapter's own extraction) ---")
            signs = sa.extract_ordered_signs(value)
            print(signs)
            return
    print(f"document {tablet_id!r} NOT FOUND")


def dump_sign(signs_val, sign_number: int, depth: int):
    signs_map = signs_val.fields[0]
    for key, value in sa.map_items(signs_map):
        if key == sign_number:
            print(f"=== sign #{sign_number} (depth<= {depth}) ===")
            print(safe_repr(value, maxdepth=depth))
            print()
            return
    print(f"sign #{sign_number} NOT FOUND")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tablets", nargs="+", default=None,
                     help="explicit tablet IDs to inspect (required unless --list-signs)")
    ap.add_argument("--list-signs", nargs="+", type=int, default=None,
                     help="explicit sign numbers (in the signs.blob) to inspect")
    ap.add_argument("--depth", type=int, default=8,
                     help="max structural print depth (default 8; bounded, no unlimited mode)")
    ap.add_argument("--raw", default=DEFAULT_RAW_PATH)
    args = ap.parse_args()

    if not args.tablets and not args.list_signs:
        print("ERROR: --tablets or --list-signs (with explicit IDs) is required. "
              "There is no corpus-wide mode.", file=sys.stderr)
        sys.exit(2)

    data_val, signs_val = load(args.raw)

    if args.tablets:
        for t in args.tablets:
            dump_document(data_val, t, args.depth)
    if args.list_signs:
        for n in args.list_signs:
            dump_sign(signs_val, n, args.depth)


if __name__ == "__main__":
    main()
