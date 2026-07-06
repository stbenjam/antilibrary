# The Antilibrary

**Live page: [bitbin.de/antilibrary](https://bitbin.de/antilibrary/)**

A single-file, interactive audit of every book I own and have not read — 118 of them,
66,143 pages, 19 million words — with the quiet arithmetic of whether I will ever
finish (spoiler: at current rates, never).

## How this happened

I gave Claude Code one prompt, with full autonomy and no follow-up questions allowed:

> You have one turn and full autonomy. Look around this machine - especially
> ~/.claude/projects and ~/.claude-personal/projects - and figure out who I am, and
> build me one non-obvious thing I didn't know I wanted. Don't ask questions.
> Surprise me. Avoid reading private data, tokens, etc, and do not take any actions
> off of this machine.

One turn later, Claude (Fable 5) had:

- explored the machine and concluded that between the Calibre library, a Goodreads
  export, an e-reader staging folder, and four different homemade `books:*` skills,
  the thing this machine talks about most is reading;
- noticed that all my existing tooling answers *"what should I read next?"* and none
  of it answers *"will I ever finish the books I already own?"*;
- extracted 448 books from the Calibre database (including my custom read/pages/words
  columns), cross-referenced them with my Goodreads history, and computed acquisition
  vs. completion rates;
- designed and shipped this page: every book rendered as a hoverable spine on a shelf,
  charts for books-in vs. books-out, an elevation profile of Mount Tsundoku, and an
  interactive prognosis with sliders for "what if I read more / bought less" —
  chart colors validated for colorblind safety, light and dark themes hand-tuned.

The numbers are a static snapshot of my library as of July 6, 2026, baked into the
HTML. No data leaves the page; there is no tracking, no network calls, nothing but
one HTML file and my accumulated shame.

Robert Jordan alone is owed 16 books — 26% of every unread page I have.

*(Claude wrote this README too.)*
