#!/usr/bin/env python3
"""Use a distinct package ID so Android can install the test build alongside older signed builds."""
from pathlib import Path
p=Path('app/build.gradle')
s=p.read_text(encoding='utf-8')
old="applicationId 'br.com.raully.neohackarcade.pro'"
new="applicationId 'br.com.raully.neohackarcade.pro.controltest'"
assert s.count(old)==1, 'Expected the Vortix applicationId exactly once'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Using separate application ID so a temporary-signature test build can install beside older Vortix builds')
