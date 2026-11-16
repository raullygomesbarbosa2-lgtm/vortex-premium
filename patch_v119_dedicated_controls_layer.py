#!/usr/bin/env python3
"""Place every touch control in a dedicated full-screen layer above the GL game surface."""
from pathlib import Path
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='''        root.addView(retroView, new FrameLayout.LayoutParams(-1, -1));
        addTouchControls(root, systemLabel);
        setContentView(root);
'''
new='''        root.addView(retroView, new FrameLayout.LayoutParams(-1, -1));
        // Keep every touch control in a dedicated full-screen sibling layer.
        // This avoids GL/surface ordering and parent-clipping issues for moved
        // face buttons, round special buttons, L/R shoulders, and menu controls.
        FrameLayout controlsLayer = new FrameLayout(this);
        controlsLayer.setClipChildren(false);
        controlsLayer.setClipToPadding(false);
        controlsLayer.setMotionEventSplittingEnabled(true);
        root.addView(controlsLayer, new FrameLayout.LayoutParams(-1, -1));
        controlsLayer.setElevation(dp(40));
        controlsLayer.bringToFront();
        addTouchControls(controlsLayer, systemLabel);
        setContentView(root);
'''
assert s.count(old)==1, 'could not find unique retro view/control creation anchor'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Moved all touch controls to a dedicated full-screen sibling layer above the GL surface')
