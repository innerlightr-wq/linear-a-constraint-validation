# SigLA provenance audit

Investigated before downloading or analyzing any SigLA data, per this
project's own discipline of establishing provenance before touching a new
source. Primary source consulted directly: Salgarella, E. & Castellan, S.
(2021), "SigLA: The Signs of Linear A — A Palæographical Database,"
*Grapholinguistics in the 21st Century 2020 Proceedings*, Fluxus Editions
(read in full, pages 945–955, DOI 10.36824/2020-graf-salg), plus the live
site `https://sigla.phis.me/` and `https://sigla.phis.me/about.html`,
fetched directly in this session. Labels: **SOURCE-DERIVED FACT**,
**INFERENCE**, **OPEN**.

## 1. Official/public source

**SOURCE-DERIVED FACT.** `https://sigla.phis.me/`, created by Ester
Salgarella (St John's College, Cambridge) and Simon Castellan (Inria, Univ.
Rennes, CNRS, IRISA), first released 2020-06-18. Published paper: as cited
above.

## 2. Available downloadable/machine-readable representation

**SOURCE-DERIVED FACT.** `https://sigla.phis.me/database.js` is directly
reachable (independently verified this session: HTTP 200, 2,516,528 bytes,
`Last-Modified: Fri, 26 Jun 2026`, `Content-Type: text/javascript`, no
authentication). The paper states the site's own "Import" component
produces a **JSON database** internally from the authors' Krita source
files; the **web interface is written in OCaml and compiled to JavaScript**
that runs entirely client-side, and "the website can be downloaded and run
locally." **INFERENCE** (not directly stated in the paper, but consistent
with everything observed): the publicly-served `database.js` is the
OCaml-compiled application's own serialized data bundle (OCaml `Marshal`
binary format escaped as decimal-octet strings), not the raw JSON the
"Import" tool produces internally — JSON is the authors' stated internal
design choice, but the artifact actually reachable over HTTP requires
decoding the OCaml `Marshal` format to recover it. **OPEN**: whether a raw
JSON export is offered anywhere else (e.g. on request, in a data
repository, or via a different endpoint) was not found in this session's
search and is not confirmed absent.

## 3. Licensing terms

**SOURCE-DERIVED FACT**, confirmed twice independently (site `about.html`,
fetched directly this session; and previously via the external foundation
project's own independent statement, `docs/EXTERNAL_FOUNDATION_AUDIT.md`):
**CC BY-NC-SA 4.0** — "Dataset and drawings are available under the CC
BY-NC-SA 4.0 license." Attribution required; **noncommercial**; **share-alike**
for any redistributed derivative. This project's existing `data/README.md`
policy (fetch locally, never commit raw corpus data) already anticipates
and satisfies this.

## 4. Transcription provenance

**SOURCE-DERIVED FACT**, directly from the paper (§3.1–3.2): SigLA's textual
base is **GORILA** (Godart & Olivier, 1976–1985) — "the extant evidence...
is presented in the five volumes of GORILA... This still remains the only
corpus of Linear A inscriptions" — cross-referenced against **Younger
(2000)**'s transliteration, itself explicitly "based on Godart and Olivier
(1976–1985) transcriptions." The authors did **not** describe re-examining
original tablets or photographs from scratch as an independent primary
reading; their own described innovation is re-**drawing** each document
themselves (using Krita, to avoid GORILA's image copyright), "as faithful to
the originals as possible," plus a structured, sign-by-sign functional
re-classification (syllabogram / logogram / fraction / transaction-sign /
erasure) that GORILA's print format does not support computationally.

## 5. Relationship to GORILA

**SOURCE-DERIVED FACT:** direct and primary. Per the site's own `about.html`
(fetched directly this session), "by August 2021, all tablets from GORILA
are now present in SigLA" — SigLA's scope is explicitly defined as
GORILA-complete coverage, built on GORILA's own transcriptions as its
evidentiary base.

## 6. Relationship to `mwenge/lineara.xyz`

**SOURCE-DERIVED FACT:** **none stated anywhere** — the SigLA paper and
about-page make no mention of `mwenge/lineara.xyz`, and `mwenge/lineara.xyz`'s
own README (read during the primary-corpus ingestion phase) makes no mention
of SigLA. **INFERENCE:** the two projects are independent efforts by
different people (Salgarella & Castellan vs. Rob Hogan), built on
overlapping upstream material (both ultimately derive from GORILA; SigLA
additionally cites Younger 2000, which `mwenge` also credits as an input to
its own word-division/tabulation via George Douros's compilation — so both
projects' inputs overlap partially but were assembled independently, by
different people, using different methods). **They are not the same
digitization pipeline and do not derive from each other**, but they are
**not independent at the level of the underlying readings** — both trace to
GORILA as the common textual ancestor.

## 7. Does SigLA independently recheck readings against tablets/publications?

**SOURCE-DERIVED FACT, precisely:** not against the physical tablets or
original photographs (no such claim is made anywhere in the paper). The
independent work that **is** claimed and credible: the authors' own
redrawing of every document (a genuine act of palaeographic labor, checked
against GORILA's own published photographs/drawings, not against the
objects themselves), a from-scratch sign-by-sign functional classification,
and explicit tracking of erasures and doubtful/unreadable signs (question-mark
convention) as first-class, searchable data. This is real, independent
**scholarly re-examination of the published evidentiary record**, not
independent **primary transcription** of the artifacts.

## 8. Can document identifiers be mapped between the two resources?

**SOURCE-DERIVED FACT:** yes, in principle — SigLA's own document IDs use
the same GORILA-style catalogue convention (e.g. "HT 23a", "HT 11a", "HT
119", visible directly in the paper's own figures) as `mwenge/lineara.xyz`'s
tablet IDs (e.g. "HT1", "HT9a", "HT104"). **OPEN, requires direct
verification once real data is fetched (Phase 6):** exact formatting
differences (spacing, face-letter conventions, joined-tablet notation like
`HT123+124a`) are not yet confirmed to normalize cleanly between the two
sources — this is exactly the cross-corpus document-ID audit Phase 6 exists
to perform, not assumed here.

## 9. Does SigLA contain reading-certainty information unavailable in `mwenge`?

**SOURCE-DERIVED FACT, directly from the paper (§4.1):** yes, in a form
`mwenge/lineara.xyz` was confirmed (in the primary-corpus ingestion phase)
not to have as a structured field. SigLA uses "the question-mark for signs
of doubtful reading or unreadable (instances where traces of a sign are
visible, but the sign can not be recognised)," and separately tracks
**erasures** ("instances where the traces of a previously cancelled sign are
still visible") as their own, independently searchable category
(red-highlighted in the interface). This is a genuine, structured
certainty/damage signal beyond `mwenge`'s bracket-string convention.
**OPEN:** whether this maps onto a **graded** confidence scale (secure /
derived / open, matching Corazza et al. 2021's specific fraction-value
grading, which `H1_PROTOCOL.md` §3 requires) or only a **binary**
certain/doubtful-or-unreadable flag is not yet confirmed — the paper
describes a question-mark convention (binary-shaped) plus a separate
erasure category (a third, distinct signal), not an explicit multi-level
grade. This must be confirmed directly against the real data in Phase 3,
not assumed from the paper's prose alone.

## 10. Does SigLA have sufficient numeral/fraction information for H1?

**SOURCE-DERIVED FACT:** the sign-function color-coding explicitly includes
a dedicated **"orange for fractions (fractional signs accompanying numbers or
concepts)"** category — fractions are a first-class, distinctly-tagged sign
type in SigLA's own data model, not merely inferrable from raw transliteration
as with `mwenge`. This is a structural improvement over `mwenge`'s schema.
**OPEN:** whether the specific numeric *value* of each fraction sign is
encoded directly, or only its identity/function tag (requiring the same kind
of external Corazza-et-al. value lookup `mwenge` needed), is not confirmed
by the paper and must be checked directly against real data (Phase 3).

---

## Replication-relationship classification

# **B — PARTIALLY INDEPENDENT DIGITIZATION / RE-EXAMINATION**

**Not A (independent transcription replication):** both `mwenge/lineara.xyz`
and SigLA trace their base readings to the same GORILA transcriptions (SigLA
explicitly and completely so, per its own paper); SigLA did not perform an
independent primary reading of the physical tablets or original photographs.
Calling this "independent transcription replication" would overstate what
the evidence supports.

**Not C (same transcription lineage, different implementation) either:**
SigLA's redrawing process, sign-by-sign functional re-classification, and
structured doubtful/unreadable and erasure tracking constitute genuine,
non-trivial independent scholarly work layered on top of the shared GORILA
base — this is materially more than a second software implementation over
identical data. A disagreement between `mwenge`-derived and SigLA-derived H1
results **can** reflect genuine differences in reading/classification
judgment, not merely differences in parsing code.

**Not D:** the two sources are sufficiently distinct in methodology,
authorship, and data model (structured function-tags, certainty markers,
erasure tracking) to be worth comparing.

**Practical consequence for how results should be described later:** any
future SigLA H1 result should be reported as a **CROSS-TRANSCRIPTION
REPLICATION** (per this project's own terminology guidance) — informative
about whether the frozen H1 test's outcome is sensitive to transcription
and classification choices made by a second, independent scholarly team,
but **not** informative about whether Linear A itself, examined completely
fresh from the original artifacts, would show the same pattern. Both
`mwenge` and SigLA results ultimately rest on the same GORILA evidentiary
base.
