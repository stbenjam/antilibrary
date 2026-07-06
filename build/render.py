#!/usr/bin/env python3
"""Substitute payload.json into the template -> ../index.html."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, 'antilibrary.template.html')).read()
data = open(os.path.join(HERE, 'payload.json')).read()
assert '__DATA__' in tpl
out = os.path.join(HERE, '..', 'index.html')
open(out, 'w').write(tpl.replace('__DATA__', data))
print('wrote', os.path.abspath(out), os.path.getsize(out), 'bytes')
