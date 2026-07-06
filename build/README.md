# Build pipeline

The page is generated from local data that never leaves this machine except as
the aggregated snapshot baked into `index.html`.

```
python3 extract.py      # Calibre metadata.db + Goodreads CSV -> library.json
python3 build_data.py   # library.json -> payload.json (the embedded snapshot)
python3 render.py       # template + payload.json -> ../index.html
```

Inputs (paths at the top of `extract.py`):

- `~/Drive/Calibre Library/metadata.db` — opened read-only. Uses the custom
  columns: 1 Read, 4 Archived, 5 Pages, 6 Words, 8 Date Read, 9 Priority.
- `~/Drive/Claude/books/goodreads_library_export.csv` — backfills read
  status/dates for books Calibre doesn't have flagged.

`library.json` and `payload.json` are gitignored: `library.json` contains the
full library including archived books and the complete Goodreads history,
which is more than the page publishes. Only the rendered `index.html` is
committed.

Caveats: the prose in `antilibrary.template.html` (the lede numbers, the
scenario-chip rates in `SCENARIOS`, the Jordan callout) was written against
the July 2026 snapshot — after regenerating with fresh data, re-read the copy
and update any hardcoded numbers that drifted.
