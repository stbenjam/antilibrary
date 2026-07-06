#!/usr/bin/env python3
"""Compute the page payload from library.json -> payload.json.

Reads library.json (from extract.py) and writes payload.json next to this
script. payload.json is exactly what gets embedded in the page — nothing
about archived books beyond their count.
"""
import json, collections, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'library.json')))
cal, gr = d['calibre'], d['goodreads']
TODAY = datetime.date.today()

owned = [b for b in cal if not b['archived']]
unread = [b for b in owned if not b['read']]
read_owned = [b for b in owned if b['read']]

# --- spines, sorted by added date (bogus pre-2000 dates first) ---
def added_key(b):
    a = b['added'] or '0000'
    return a if a >= '2000' else '0000'
spines = []
for b in sorted(owned, key=added_key):
    spines.append({
        't': b['title'], 'a': ', '.join(b['authors']),
        'p': b['pages'] or 0, 'r': b['read'],
        's': b['series'], 'si': b['series_index'],
        'ad': b['added'] if (b['added'] or '') >= '2000' else None,
        'dr': b.get('date_read'),
        'pr': b.get('priority'),
    })

# --- yearly flow: inflow to the shelf vs finishes from all sources ---
acq = collections.Counter(b['added'][:4] for b in owned if b['added'] and b['added'] >= '2000')
reads_all = collections.Counter(); seen = set()
for b in cal:
    if b.get('date_read'):
        reads_all[b['date_read'][:4]] += 1; seen.add(b['title'].lower()[:30])
for g in gr:
    if g['shelf'] == 'read' and g['date_read']:
        k = g['title'].lower()[:30]
        if k not in seen: reads_all[g['date_read'][:4]] += 1; seen.add(k)
yearly = [{'y': str(y), 'in': acq.get(str(y), 0), 'out': reads_all.get(str(y), 0)}
          for y in range(2020, TODAY.year + 1)]

# --- monthly TBR curve (owned shelf only), from Oct 2024 to now ---
ms_acq = collections.Counter(b['added'][:7] for b in owned if b['added'] and b['added'] >= '2024')
ms_read = collections.Counter(b['date_read'][:7] for b in owned if b.get('date_read') and (b['date_read'] or '') >= '2024')
months = []
y, m = 2024, 10
while (y, m) <= (TODAY.year, TODAY.month):
    months.append(f'{y}-{m:02d}')
    m += 1
    if m > 12: y, m = y + 1, 1
tbr_now = len(unread)
delta = sum(ms_acq.get(mm, 0) - ms_read.get(mm, 0) for mm in months)
cur = tbr_now - delta
curve = []
for mm in months:
    cur += ms_acq.get(mm, 0) - ms_read.get(mm, 0)
    curve.append({'m': mm, 'tbr': cur, 'in': ms_acq.get(mm, 0), 'out': ms_read.get(mm, 0)})
assert curve[-1]['tbr'] == tbr_now

# --- last-12-month rates (owned shelf) ---
last12 = months[-13:-1]
in12 = sum(ms_acq.get(mm, 0) for mm in last12)
out12 = sum(ms_read.get(mm, 0) for mm in last12)
prev_year = str(TODAY.year - 1)
out_prev_shelf = sum(ms_read.get(f'{prev_year}-{i:02d}', 0) for i in range(1, 13))

# --- elders: longest-waiting unread books ---
elders = []
for b in sorted([b for b in unread if b['added'] and b['added'] >= '2000'], key=lambda b: b['added'])[:8]:
    days = (TODAY - datetime.date.fromisoformat(b['added'])).days
    elders.append({'t': b['title'], 'a': ', '.join(b['authors']), 'days': days, 'ad': b['added'], 'p': b['pages']})
undated = [b['title'] for b in unread if b['added'] and b['added'] < '2000']

# --- author debt ---
adebt = collections.Counter(); apages = collections.Counter()
for b in unread:
    for a in b['authors']:
        adebt[a] += 1; apages[a] += b['pages'] or 0
authors = [{'a': a, 'n': n, 'p': apages[a]} for a, n in adebt.most_common(8)]

# --- series in progress ---
sd = collections.defaultdict(lambda: {'read': [], 'unread': []})
for b in owned:
    if b['series']:
        sd[b['series']]['read' if b['read'] else 'unread'].append((b['series_index'] or 0, b['title']))
series = []
for s, v in sd.items():
    if v['read'] and v['unread']:
        nxt = sorted(v['unread'])[0]
        series.append({'s': s, 'read': len(v['read']), 'left': len(v['unread']), 'next': nxt[1], 'ni': nxt[0]})
series.sort(key=lambda x: (-x['read'], -x['left']))

# --- Wheel of Time ---
wot = [b for b in unread if b['series'] and 'Wheel of Time' in b['series']]
wot_stats = {'n': len(wot), 'pages': sum(b['pages'] or 0 for b in wot), 'words': sum(b['words'] or 0 for b in wot)}

# --- priority-flagged unread ---
pri = [{'t': b['title'], 'a': ', '.join(b['authors']), 'pr': b['priority'], 'ad': b['added']}
       for b in sorted([b for b in unread if b.get('priority')], key=lambda b: -b['priority'])]

# --- tags of the debt ---
tcnt = collections.Counter(t for b in unread for t in b['tags'])
skip = {'Adult', 'General', 'Fiction'}
tags = [{'t': t, 'n': n} for t, n in tcnt.most_common(20) if t not in skip][:8]

totals = {
    'owned': len(owned), 'read': len(read_owned), 'unread': len(unread),
    'archived': len(cal) - len(owned),
    'pages_owed': sum(b['pages'] or 0 for b in unread),
    'words_owed': sum(b['words'] or 0 for b in unread),
    'in12': in12, 'out12': out12, 'out_prev_shelf': out_prev_shelf,
    'pace_all_3yr': round(sum(reads_all.get(str(TODAY.year - i), 0) for i in (1, 2, 3)) / 3, 1),
}

payload = {'generated': TODAY.isoformat(), 'totals': totals, 'spines': spines, 'yearly': yearly,
           'curve': curve, 'elders': elders, 'undated': undated, 'authors': authors,
           'series': series[:8], 'wot': wot_stats, 'priority': pri, 'tags': tags}
out = os.path.join(HERE, 'payload.json')
json.dump(payload, open(out, 'w'), ensure_ascii=False)
print(json.dumps(totals, indent=1))
print('wrote', out, os.path.getsize(out), 'bytes')
