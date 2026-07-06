#!/usr/bin/env python3
"""Extract library data: Calibre (owned books + read flags) and Goodreads (read history).

Writes library.json next to this script. That file contains the FULL library,
including archived books — it is gitignored on purpose; do not commit it.
"""
import sqlite3, csv, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
CALIBRE_DB = os.path.expanduser('~/Drive/Calibre Library/metadata.db')
GOODREADS_CSV = os.path.expanduser('~/Drive/Claude/books/goodreads_library_export.csv')
OUT = os.path.join(HERE, 'library.json')

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = s.lower().split(':')[0]
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[^a-z0-9 ]', '', s)
    s = re.sub(r'\bthe \b|\ba \b|\ban \b', '', s)
    return ' '.join(s.split())

# ---------- Calibre ----------
con = sqlite3.connect(f'file:{CALIBRE_DB}?mode=ro', uri=True)
cur = con.cursor()

books = {}
for bid, title, ts, pubdate in cur.execute("SELECT id, title, timestamp, pubdate FROM books"):
    books[bid] = {
        'id': bid, 'title': title,
        'added': (ts or '')[:10],
        'pubdate': (pubdate or '')[:10],
        'authors': [], 'series': None, 'series_index': None, 'tags': [],
        'read': False, 'date_read': None, 'pages': None, 'words': None,
        'archived': False, 'priority': None,
    }

for bid, name in cur.execute("""SELECT bal.book, a.name FROM books_authors_link bal
                                JOIN authors a ON a.id=bal.author"""):
    if bid in books: books[bid]['authors'].append(name.replace('|', ','))

for bid, name, idx in cur.execute("""SELECT bsl.book, s.name, b.series_index
                                     FROM books_series_link bsl JOIN series s ON s.id=bsl.series
                                     JOIN books b ON b.id=bsl.book"""):
    if bid in books:
        books[bid]['series'] = name
        books[bid]['series_index'] = idx

for bid, name in cur.execute("""SELECT btl.book, t.name FROM books_tags_link btl
                                JOIN tags t ON t.id=btl.tag"""):
    if bid in books: books[bid]['tags'].append(name)

# Custom columns: 1=Read(bool) 8=Date Read 5=Pages 6=Words 4=Archived(bool) 9=Priority(rating)
for bid, val in cur.execute("SELECT book, value FROM custom_column_1"):
    if bid in books: books[bid]['read'] = bool(val)
for bid, val in cur.execute("SELECT book, value FROM custom_column_8"):
    if bid in books and val: books[bid]['date_read'] = str(val)[:10]
for bid, val in cur.execute("SELECT book, value FROM custom_column_5"):
    if bid in books: books[bid]['pages'] = val
for bid, val in cur.execute("SELECT book, value FROM custom_column_6"):
    if bid in books: books[bid]['words'] = val
for bid, val in cur.execute("SELECT book, value FROM custom_column_4"):
    if bid in books: books[bid]['archived'] = bool(val)
for bid, val in cur.execute("""SELECT l.book, c.value FROM books_custom_column_9_link l
                               JOIN custom_column_9 c ON c.id=l.value"""):
    if bid in books: books[bid]['priority'] = val

calibre = list(books.values())

# ---------- Goodreads ----------
gr = []
with open(GOODREADS_CSV) as f:
    for row in csv.DictReader(f):
        gr.append({
            'title': row['Title'], 'author': row['Author'],
            'rating': int(row['My Rating'] or 0),
            'avg': float(row['Average Rating'] or 0),
            'pages': int(row['Number of Pages'] or 0) if row['Number of Pages'] else None,
            'date_read': row['Date Read'].replace('/', '-') if row['Date Read'] else None,
            'date_added': row['Date Added'].replace('/', '-') if row['Date Added'] else None,
            'shelf': row['Exclusive Shelf'],
            'read_count': int(row['Read Count'] or 0),
        })

# Backfill Calibre read status/dates from the Goodreads read shelf
gr_read_by_norm = {norm(g['title']): g for g in gr if g['shelf'] == 'read'}
enriched = 0
for b in calibre:
    g = gr_read_by_norm.get(norm(b['title']))
    if g:
        b['gr_rating'] = g['rating']
        if not b['date_read'] and g['date_read']:
            b['date_read'] = g['date_read']
        if not b['read'] and g['read_count'] > 0:
            b['read'] = True
        if not b['pages'] and g['pages']:
            b['pages'] = g['pages']
        enriched += 1

print(f"calibre={len(calibre)} goodreads={len(gr)} matched={enriched}")
json.dump({'calibre': calibre, 'goodreads': gr}, open(OUT, 'w'))
print('wrote', OUT)
