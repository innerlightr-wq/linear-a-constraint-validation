#!/usr/bin/env node
/*
 * Minimal extraction of LinearAInscriptions.js's `inscriptions` Map into
 * JSON on stdout. The upstream file is a JavaScript Map literal, not JSON
 * (confirmed by direct inspection, docs/SCHEMA_MAPPING.md), so it must be
 * evaluated, not parsed as text.
 *
 * INDEPENDENT IMPLEMENTATION -- written from this project's own schema
 * inspection, not copied from any external project's extract_raw.js (see
 * docs/EXTERNAL_FOUNDATION_AUDIT.md).
 *
 * Deliberately drops `translatedWords`: that field carries Linear
 * B-derived semantic glosses (interpretation), not the transcription
 * itself -- the same principle documented independently in
 * docs/SCHEMA_MAPPING.md, not something this project's H1 protocol needs
 * or should import.
 *
 * Usage: node src/extract_raw_js.js <path-to-LinearAInscriptions.js>
 * Output: a JSON array of {name, site, findspot, scribe, context, support,
 * transliteratedWords} objects, one per tablet, to stdout.
 *
 * NOT RUN AGAINST THE REAL CORPUS in the protocol-freeze / ingestion phase
 * this file was added in -- see docs/CORPUS_PROVENANCE.md and the
 * pre-analysis report for what has and has not been executed.
 */
const fs = require('fs');
const vm = require('vm');

const path = process.argv[2];
if (!path) {
  console.error('usage: node extract_raw_js.js <path-to-LinearAInscriptions.js>');
  process.exit(1);
}

const source = fs.readFileSync(path, 'utf8');
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(source, sandbox);

const out = [];
for (const [id, rec] of sandbox.inscriptions) {
  out.push({
    name: rec.name || id,
    site: rec.site || null,
    findspot: rec.findspot || null,
    scribe: rec.scribe || null,
    context: rec.context || null,
    support: rec.support || null,
    transliteratedWords: rec.transliteratedWords || [],
  });
}
process.stdout.write(JSON.stringify(out));
