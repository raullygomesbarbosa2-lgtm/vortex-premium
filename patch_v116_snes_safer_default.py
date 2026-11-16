#!/usr/bin/env python3
"""Prefer a lighter bundled SNES core over the previous Mesen-S default."""
from pathlib import Path
p = Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s = p.read_text(encoding='utf-8')
old = 'preferredIds = new String[]{"mesen-s", "mednafen_snes", "bsnes", "bsnes2014_balanced"};'
new = 'preferredIds = new String[]{"bsnes2014_balanced", "mednafen_snes", "mesen-s", "bsnes"};'
assert s.count(old) == 1, 'SNES core preference anchor missing or duplicated'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('SNES legacy alias now prefers the bundled bsnes 2014 Balanced core')
