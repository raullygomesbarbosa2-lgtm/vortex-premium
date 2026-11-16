#!/usr/bin/env python3
"""Exclude Sony PlayStation families from the selected core catalog for this build."""
from pathlib import Path
p=Path('app/src/main/assets/core_catalog.json')
import json
c=json.loads(p.read_text(encoding='utf-8'))
old=c['cores']
exclude=('playstation','sony - playstation','psp','pcee2','pcsx2','armsx2','swanstation','mednafen_psx','pcsx_rearmed','ppsspp','pokketstation')
kept=[]
removed=[]
for x in old:
 text=' '.join(str(x.get(k,'')) for k in ('id','name','system')).lower()
 if any(term in text for term in exclude): removed.append((x.get('id'),x.get('name')))
 else: kept.append(x)
if not removed: print('No PlayStation, PS2, PSP or PocketStation cores were present; no changes needed')
c['cores']=kept
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Excluded:',removed)
print('Remaining cores:',len(kept))
