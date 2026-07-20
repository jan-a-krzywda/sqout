"""Stage 4b — ground each paper against the corpus. Read-only.

Resolve the paper's arXiv DOI through OpenAlex to get its reference list, then
intersect that against the corpus snapshot. The overlap is two things at once:
the centrality signal for ranking, and the raw material for the brief's
"Connection" line — the part no generic tool can produce.

Nothing here writes to the corpus. No `library.bib` append, no `works.json`
merge, no graph rebuild; those are M2.

EXPECT THIS STAGE TO MISS MOST OF THE TIME, for two separate reasons — the
second one measured against the live API on 2026-07-20 and worse than the spec
anticipated:

  1. Indexing lag. DataCite registration and OpenAlex indexing both trail
     arXiv posting, so a same-day preprint often has no record at all.

  2. Preprint records carry no reference list. Even when the arXiv DOI *does*
     resolve, OpenAlex's preprint record is usually a stub: the references
     live on the separate record for the published version, under a different
     DOI. Measured example — arXiv:2112.08863 ("Semiconductor Spin Qubits"):
     the arXiv-DOI record (W4320341678) reports 0 referenced_works, while the
     Rev. Mod. Phys. record for the same paper (W4380590907) reports 664.

Consequence: on a typical morning this stage yields no connection lines. It
earns its keep on older papers and on re-runs after a preprint is published,
not on the daily firehose. Getting real day-one connections needs a semantic
route (embeddings over abstracts) rather than a citation route — that is the
spec's M3 work, and this stage is the evidence for why it matters.

Every miss is ordinary, not an error: centrality stays NULL and the brief is
written to read correctly without it.
"""
from __future__ import annotations

import logging
import sqlite3

from . import corpus, openalex, store
from .config import Config

log = logging.getLogger(__name__)

# Overlap count that saturates the centrality signal. Citing ten corpus papers
# rather than five says "lands in a dense part of your library"; the difference
# between twenty and thirty says little more.
SATURATION = 10.0


def run(cfg: Config, conn: sqlite3.Connection, snap: corpus.Snapshot | None = None) -> int:
    """Annotate filtered papers with corpus overlap. Returns papers connected."""
    if not cfg.connect.enabled:
        log.info('connect: disabled in config')
        return 0

    rows = store.papers_with_status(conn, 'filtered')
    if not rows:
        return 0

    snap = snap if snap is not None else corpus.load(cfg)
    if not snap:
        log.warning(
            'connect: no corpus snapshot, skipping. Run `sqout sync-corpus`.'
        )
        return 0

    dois = {r['cite_key']: openalex.arxiv_doi(r['arxiv_id']) for r in rows}
    dois = {k: v for k, v in dois.items() if v}

    try:
        resolved = openalex.resolve_by_doi(
            dois, mailto=cfg.connect.openalex_mailto
        )
    except openalex.OpenAlexError as exc:
        # Non-fatal by design: rank and brief both handle absent centrality.
        log.warning('connect: OpenAlex unavailable, continuing without: %s', exc)
        return 0

    connected = 0
    no_refs = 0
    for row in rows:
        record = resolved.get(row['cite_key'])
        if record is None:
            # Not indexed yet — the common case for fresh preprints.
            continue

        refs = record['referenced_works']
        if not refs:
            # Resolved, but the preprint record is a stub with no reference
            # list. Record the OpenAlex ID anyway: it is what a later re-run
            # (or M2's ingest) needs, and it distinguishes "we found it but it
            # told us nothing" from "we never found it".
            store.upsert_paper(
                conn,
                row['cite_key'],
                doi=record['doi'],
                openalex_id=record['openalex_id'],
            )
            no_refs += 1
            continue

        cited_keys = openalex.overlap(refs, snap.ids)
        store.upsert_paper(
            conn,
            row['cite_key'],
            doi=record['doi'],
            openalex_id=record['openalex_id'],
            centrality=min(len(cited_keys) / SATURATION, 1.0),
            cited_in_corpus=[snap.titles.get(k, k) for k in cited_keys],
        )
        if cited_keys:
            connected += 1

    log.info(
        'connect: %d/%d resolved, %d had no reference list, %d cite the corpus',
        len(resolved), len(rows), no_refs, connected,
    )
    if rows and not connected:
        log.info(
            'connect: no connection lines this run. Expected for same-day '
            'preprints — OpenAlex preprint records usually carry no references.'
        )
    return connected
