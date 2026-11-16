#!/usr/bin/env python3
"""Keep the full control group above the GL game image while a nested button is moved."""
from pathlib import Path
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
anchor='''    private void handleTouchLayoutEdit(MotionEvent event) {
'''
helper='''    private void raiseTouchControlBranch(View target) {
        if (target == null || gameOverlayRoot == null) return;
        View branch = target;
        android.view.ViewParent parent = target.getParent();
        while (parent instanceof android.view.ViewGroup && parent != gameOverlayRoot) {
            android.view.ViewGroup group = (android.view.ViewGroup) parent;
            group.setClipChildren(false);
            group.setClipToPadding(false);
            if (group.indexOfChild(branch) >= 0) group.bringChildToFront(branch);
            branch = group;
            parent = group.getParent();
        }
        if (gameOverlayRoot.indexOfChild(branch) >= 0) {
            gameOverlayRoot.bringChildToFront(branch);
            branch.setElevation(dp(30));
        }
        target.bringToFront();
        target.setElevation(dp(31));
        gameOverlayRoot.invalidate();
    }

'''
if 'private void raiseTouchControlBranch(View target)' not in s:
 assert s.count(anchor)==1, 'control editor handler anchor missing'
 s=s.replace(anchor,helper+anchor,1)
call='''                  target.setElevation(dp(24));'''
if call in s:
 s=s.replace(call,call+'\n                  raiseTouchControlBranch(target);',1)
else:
 # Same inline build fix may already have been updated; target the generated editor's elevation instead.
 call2='''                target.setElevation(dp(18));'''
 assert s.count(call2)==1, 'cannot find touch-down elevation point'
 s=s.replace(call2,call2+'\n                raiseTouchControlBranch(target);',1)
p.write_text(s,encoding='utf-8')
print('Added z-order promotion for the root-level overlay group and unclipped all nested controls during edits')
