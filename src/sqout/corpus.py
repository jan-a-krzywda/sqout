"""The corpus snapshot — sqout's own copy of the citation structure.

SpinLib is a paper library, not a dependency. Rather than reading its
`works.json` live, `sync-corpus` copies it here once and every run reads only
the copy. The tradeoff is drift: the snapshot ages. `meta.json` records where
it came from and when, and runs warn past `corpus.stale_after_days`.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .config import Config, ConfigError


class CorpusError(Exception):
    """Raised only by sync; loading a missing snapshot degrades instead."""


@dataclass(frozen=True)
class Snapshot:
    """Loaded corpus. `ids` maps OpenAlex ID -> cite_key; `titles` cite_key -> title."""
    ids: dict[str, str]
    titles: dict[str, str]
    synced_at: str | None = None
    source: str | None = None

    def __bool__(self) -> bool:
        return bool(self.ids)

    @property
    def age_days(self) -> int | None:
        if not self.synced_at:
            return None
        try:
            return (date.today() - date.fromisoformat(self.synced_at[:10])).days
        except ValueError:
            return None


EMPTY = Snapshot(ids={}, titles={})


def sync(cfg: Config, source: Path | None = None) -> dict:
    """Copy the corpus `works.json` into `.local/corpus/`. Returns the metadata.

    This is the only function in sqout that reads a path outside the project.
    """
    src = (source or cfg.corpus.source)
    if src is None:
        raise ConfigError(
            'corpus.source is not set in config/sqout.yaml, and no --from was given.'
        )
    src = Path(src).expanduser()
    if not src.exists():
        raise CorpusError(
            f'corpus source not found: {src}\n'
            f'Point corpus.source at a works.json, or pass --from <path>.'
        )

    payload = src.read_bytes()
    try:
        works = json.loads(payload)
    except ValueError as exc:
        raise CorpusError(f'{src} is not valid JSON: {exc}') from exc
    if not isinstance(works, dict):
        raise CorpusError(
            f'{src}: expected a JSON object keyed by cite_key, got {type(works).__name__}'
        )

    cfg.corpus_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, cfg.corpus_snapshot)

    meta = {
        'source': str(src),
        'sha256': hashlib.sha256(payload).hexdigest(),
        'synced_at': datetime.now().isoformat(timespec='seconds'),
        'n_records': len(works),
        'n_with_references': sum(
            1 for r in works.values()
            if isinstance(r, dict) and r.get('referenced_works')
        ),
    }
    cfg.corpus_meta.write_text(json.dumps(meta, indent=2) + '\n')
    return meta


def load(cfg: Config) -> Snapshot:
    """Load the snapshot. Returns EMPTY when absent or unreadable.

    A missing snapshot is not an error: it costs the connection line and the
    centrality signal, and the rest of the pipeline runs unchanged.
    """
    if not cfg.corpus_snapshot.exists():
        return EMPTY

    try:
        works = json.loads(cfg.corpus_snapshot.read_text())
    except ValueError:
        return EMPTY
    if not isinstance(works, dict):
        return EMPTY

    ids: dict[str, str] = {}
    titles: dict[str, str] = {}
    for cite_key, rec in works.items():
        if not isinstance(rec, dict):
            continue
        oa_id = rec.get('openalex_id')
        if oa_id:
            ids[oa_id] = cite_key
        titles[cite_key] = rec.get('title') or cite_key

    meta = {}
    if cfg.corpus_meta.exists():
        try:
            meta = json.loads(cfg.corpus_meta.read_text())
        except ValueError:
            meta = {}

    return Snapshot(
        ids=ids,
        titles=titles,
        synced_at=meta.get('synced_at'),
        source=meta.get('source'),
    )


def staleness_warning(cfg: Config, snap: Snapshot) -> str | None:
    """A one-line warning if the snapshot is missing or past its shelf life."""
    if not snap:
        return (
            'no corpus snapshot — connection lines and centrality will be absent. '
            'Run `sqout sync-corpus` to add them.'
        )
    age = snap.age_days
    if age is not None and age > cfg.corpus.stale_after_days:
        return (
            f'corpus snapshot is {age} days old '
            f'(threshold {cfg.corpus.stale_after_days}). Run `sqout sync-corpus`.'
        )
    return None
