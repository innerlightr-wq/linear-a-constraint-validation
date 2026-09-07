"""
Independent decoder for the OCaml `Marshal` module's binary output format.

INDEPENDENT IMPLEMENTATION, written from the documented, stable OCaml
runtime serialization format (the tag-byte layout used by
`caml/intext.h`/`intern.c` in the OCaml runtime), NOT copied from any
external project's decoder. No OCaml runtime was available in this
environment to cross-check against, so correctness here rests on (a) the
documented byte-layout implemented precisely, (b) self-contained unit tests
using hand-constructed byte sequences whose encoding is verified by hand
against the documented layout, and (c) plausibility checks against the
decoded SigLA data's own known structure (document IDs, counts) once
applied for real.

Scope: the subset of the format needed to decode SigLA's `database.js`
blobs -- small/large ints, small/large strings, small/large blocks
(tuples/records/variants), and shared-object backreferences. Floats and
OCaml custom blocks are decoded if encountered but are not the primary
target; if SigLA's data uses none of these where H1-relevant fields live,
they are irrelevant.

This module has ONE job: turn a raw Marshal byte string into plain Python
values (int, bytes, and OcamlBlock(tag, list-of-fields)). It does not know
anything about SigLA's specific schema -- that mapping lives entirely in
src/sigla_adapter.py.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

MAGIC = 0x8495A6BE

# Prefixed (variable-length-encoded-in-tag-byte) ranges
PREFIX_SMALL_BLOCK = 0x80
PREFIX_SMALL_INT = 0x40
PREFIX_SMALL_STRING = 0x20

# Explicit opcodes
CODE_INT8 = 0x00
CODE_INT16 = 0x01
CODE_INT32 = 0x02
CODE_INT64 = 0x03
CODE_SHARED8 = 0x04
CODE_SHARED16 = 0x05
CODE_SHARED32 = 0x06
CODE_DOUBLE_ARRAY32_LITTLE = 0x07
CODE_BLOCK32 = 0x08
CODE_STRING8 = 0x09
CODE_STRING32 = 0x0A
CODE_DOUBLE_BIG = 0x0B
CODE_DOUBLE_LITTLE = 0x0C
CODE_DOUBLE_ARRAY8_BIG = 0x0D
CODE_DOUBLE_ARRAY8_LITTLE = 0x0E
CODE_DOUBLE_ARRAY32_BIG = 0x0F
CODE_DOUBLE_ARRAY64_BIG = 0x10
CODE_DOUBLE_ARRAY64_LITTLE = 0x11
CODE_CUSTOM = 0x12
CODE_BLOCK64 = 0x13
CODE_SHARED64 = 0x14
CODE_STRING64 = 0x15
CODE_DOUBLE_ARRAY64_LITTLE2 = 0x16
CODE_CUSTOM_LEN = 0x18
CODE_CUSTOM_FIXED = 0x19


@dataclass
class OcamlBlock:
    """A decoded OCaml block (tuple / record / variant constructor). `tag`
    is the OCaml block tag; `fields` are the decoded field values in
    declaration order."""
    tag: int
    fields: list = field(default_factory=list)

    def __repr__(self):
        return f"OcamlBlock(tag={self.tag}, fields={self.fields!r})"


class MarshalDecodeError(Exception):
    pass


class _Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.objects: list = []  # for CODE_SHARED* backreferences

    def u8(self) -> int:
        v = self.data[self.pos]
        self.pos += 1
        return v

    def bytes_(self, n: int) -> bytes:
        v = self.data[self.pos:self.pos + n]
        if len(v) != n:
            raise MarshalDecodeError(f"truncated stream: wanted {n} bytes at {self.pos}, got {len(v)}")
        self.pos += n
        return v

    def be_uint(self, n: int) -> int:
        return int.from_bytes(self.bytes_(n), "big", signed=False)

    def be_int(self, n: int) -> int:
        return int.from_bytes(self.bytes_(n), "big", signed=True)

    def register(self, obj):
        """Objects are registered for sharing in the order their *header*
        is read, before their fields are decoded (matches OCaml's intern.c
        behaviour, which allows self-referential/cyclic structures)."""
        self.objects.append(obj)
        return obj

    def read_object(self):
        tag_byte = self.u8()

        if tag_byte >= PREFIX_SMALL_INT and tag_byte < PREFIX_SMALL_BLOCK:
            # 0x40-0x7F: small int, value in low 6 bits
            return tag_byte & 0x3F

        if tag_byte >= PREFIX_SMALL_BLOCK:
            # 0x80-0xFF: small block, tag in low 4 bits, size in next 3
            block_tag = tag_byte & 0x0F
            size = (tag_byte >> 4) & 0x07
            blk = self.register(OcamlBlock(block_tag, []))
            for _ in range(size):
                blk.fields.append(self.read_object())
            return blk

        if tag_byte >= PREFIX_SMALL_STRING:
            # 0x20-0x3F: small string, length in low 5 bits
            length = tag_byte & 0x1F
            s = self.bytes_(length)
            return self.register(s)

        # Explicit opcodes
        if tag_byte == CODE_INT8:
            return self.be_int(1)
        if tag_byte == CODE_INT16:
            return self.be_int(2)
        if tag_byte == CODE_INT32:
            return self.be_int(4)
        if tag_byte == CODE_INT64:
            return self.be_int(8)

        if tag_byte == CODE_SHARED8:
            back = self.be_uint(1)
            return self.objects[len(self.objects) - back]
        if tag_byte == CODE_SHARED16:
            back = self.be_uint(2)
            return self.objects[len(self.objects) - back]
        if tag_byte == CODE_SHARED32:
            back = self.be_uint(4)
            return self.objects[len(self.objects) - back]
        if tag_byte == CODE_SHARED64:
            back = self.be_uint(8)
            return self.objects[len(self.objects) - back]

        if tag_byte == CODE_BLOCK32:
            header = self.be_uint(4)
            block_tag = header & 0xFF
            size = header >> 10
            blk = self.register(OcamlBlock(block_tag, []))
            for _ in range(size):
                blk.fields.append(self.read_object())
            return blk

        if tag_byte == CODE_BLOCK64:
            header = self.be_uint(8)
            block_tag = header & 0xFF
            size = header >> 10
            blk = self.register(OcamlBlock(block_tag, []))
            for _ in range(size):
                blk.fields.append(self.read_object())
            return blk

        if tag_byte == CODE_STRING8:
            length = self.be_uint(1)
            return self.register(self.bytes_(length))
        if tag_byte == CODE_STRING32:
            length = self.be_uint(4)
            return self.register(self.bytes_(length))
        if tag_byte == CODE_STRING64:
            length = self.be_uint(8)
            return self.register(self.bytes_(length))

        if tag_byte == CODE_DOUBLE_BIG:
            return self.register(struct.unpack(">d", self.bytes_(8))[0])
        if tag_byte == CODE_DOUBLE_LITTLE:
            return self.register(struct.unpack("<d", self.bytes_(8))[0])

        if tag_byte in (CODE_DOUBLE_ARRAY8_BIG, CODE_DOUBLE_ARRAY8_LITTLE):
            n = self.be_uint(1)
            fmt = ">d" if tag_byte == CODE_DOUBLE_ARRAY8_BIG else "<d"
            arr = [struct.unpack(fmt, self.bytes_(8))[0] for _ in range(n)]
            return self.register(arr)
        if tag_byte in (CODE_DOUBLE_ARRAY32_BIG, CODE_DOUBLE_ARRAY32_LITTLE):
            n = self.be_uint(4)
            fmt = ">d" if tag_byte == CODE_DOUBLE_ARRAY32_BIG else "<d"
            arr = [struct.unpack(fmt, self.bytes_(8))[0] for _ in range(n)]
            return self.register(arr)
        if tag_byte in (CODE_DOUBLE_ARRAY64_BIG, CODE_DOUBLE_ARRAY64_LITTLE, CODE_DOUBLE_ARRAY64_LITTLE2):
            n = self.be_uint(8)
            fmt = ">d" if tag_byte == CODE_DOUBLE_ARRAY64_BIG else "<d"
            arr = [struct.unpack(fmt, self.bytes_(8))[0] for _ in range(n)]
            return self.register(arr)

        if tag_byte in (CODE_CUSTOM, CODE_CUSTOM_LEN, CODE_CUSTOM_FIXED):
            # Custom blocks (e.g. Int32.t/Int64.t/Nativeint.t boxed values)
            # carry an identifier string then implementation-specific data.
            # Not expected in SigLA's plain-data records; raised explicitly
            # rather than silently mis-decoded if encountered.
            ident = bytearray()
            b = self.u8()
            while b != 0:
                ident.append(b)
                b = self.u8()
            raise MarshalDecodeError(
                f"CODE_CUSTOM block (ident={bytes(ident)!r}) encountered at "
                f"pos {self.pos} -- not implemented, not expected in SigLA's "
                f"plain-data records; stopping rather than guessing.")

        raise MarshalDecodeError(f"unrecognized tag byte 0x{tag_byte:02x} at pos {self.pos - 1}")


def decode(data: bytes):
    """Decode one Marshal-format value (with its 20-byte standard header)
    from `data`. Returns the decoded Python value (int / bytes / OcamlBlock
    / float / list-of-float)."""
    if len(data) < 20:
        raise MarshalDecodeError(f"too short for a Marshal header: {len(data)} bytes")
    magic = int.from_bytes(data[0:4], "big")
    if magic != MAGIC:
        raise MarshalDecodeError(f"bad magic number: 0x{magic:08x}, expected 0x{MAGIC:08x}")
    data_len = int.from_bytes(data[4:8], "big")
    num_objects = int.from_bytes(data[8:12], "big")
    # size32, size64 (data[12:16], data[16:20]) not needed for decoding
    body = data[20:20 + data_len]
    if len(body) != data_len:
        raise MarshalDecodeError(
            f"declared data length {data_len} but only {len(body)} bytes available")
    reader = _Reader(body)
    value = reader.read_object()
    return value, {"num_objects_declared": num_objects, "num_objects_read": len(reader.objects)}


def extract_js_single_quoted_literal(content: bytes, open_quote_idx: int) -> tuple:
    """Scan a JS single-quoted string literal starting at the byte index of
    its opening `'`, honouring JS's own backslash-escaping (only `\\` needs
    protecting inside a JS string; a literal `\\` in source is two
    consecutive backslash bytes and unescapes to one). Returns
    (js_string_value_bytes, index_just_past_the_closing_quote).

    This layer is purely about JS source syntax and knows nothing about
    OCaml -- it exists because the OCaml-formatted content (see
    decode_ocaml_escaped below) is embedded *inside* a JS string literal,
    and that outer layer must be peeled off first, respecting its own
    escaping rules, not assumed to end at the first raw `'`.
    """
    assert content[open_quote_idx] == 0x27, "expected opening ' at given index"
    i = open_quote_idx + 1
    out = bytearray()
    n = len(content)
    while i < n:
        b = content[i]
        if b == 0x5C:  # backslash: JS escape, next byte is the literal value
            i += 1
            out.append(content[i])
            i += 1
            continue
        if b == 0x27:  # unescaped closing quote
            return bytes(out), i + 1
        out.append(b)
        i += 1
    raise MarshalDecodeError("unterminated JS string literal")


_OCAML_ESCAPE_MAP = {
    ord('\\'): 0x5C, ord('"'): 0x22, ord("'"): 0x27,
    ord('n'): 0x0A, ord('t'): 0x09, ord('r'): 0x0D, ord('b'): 0x08,
    ord(' '): 0x20,
}


def decode_ocaml_escaped(js_string_value: bytes) -> bytes:
    """Decode OCaml's own string-literal escaping convention (as produced
    by `Printf.printf "%S"` / `String.escaped`): the value is wrapped in a
    literal pair of `"` characters, and within it, printable-ASCII runs
    appear as literal bytes while non-printable/special bytes are escaped
    as `\\NNN` (exactly 3 decimal digits), or via the mnemonic forms
    `\\\\`, `\\"`, `\\'`, `\\n`, `\\t`, `\\r`, `\\b`. This is a distinct
    escaping layer from the outer JS string syntax (see
    extract_js_single_quoted_literal) -- SigLA's data passes through both,
    in sequence.
    """
    s = js_string_value
    if s[:1] == b'"' and s[-1:] == b'"':
        s = s[1:-1]
    out = bytearray()
    i = 0
    n = len(s)
    while i < n:
        b = s[i]
        if b == 0x5C:  # backslash
            nxt = s[i + 1:i + 2]
            if nxt.isdigit() and len(s[i + 1:i + 4]) == 3 and s[i + 1:i + 4].isdigit():
                out.append(int(s[i + 1:i + 4]))
                i += 4
                continue
            code = _OCAML_ESCAPE_MAP.get(s[i + 1] if i + 1 < n else -1)
            if code is not None:
                out.append(code)
                i += 2
                continue
            raise MarshalDecodeError(f"unrecognized OCaml escape at pos {i}: {s[i:i+4]!r}")
        out.append(b)
        i += 1
    return bytes(out)


def extract_and_decode_ocaml_blob(content: bytes, var_name: bytes):
    """Find `var <var_name> = '...';` in `content`, extract the JS string
    literal (JS-level unescape), then decode the OCaml-level escaping
    inside it, yielding the raw Marshal byte string."""
    marker = b"var " + var_name + b" = "
    idx = content.find(marker)
    if idx == -1:
        raise MarshalDecodeError(f"could not find 'var {var_name.decode()} = ' in content")
    quote_idx = idx + len(marker)
    if content[quote_idx] != 0x27:
        raise MarshalDecodeError(
            f"expected JS single-quote right after '{marker.decode()}', found {content[quote_idx:quote_idx+1]!r}")
    js_value, _end_idx = extract_js_single_quoted_literal(content, quote_idx)
    return decode_ocaml_escaped(js_value)
