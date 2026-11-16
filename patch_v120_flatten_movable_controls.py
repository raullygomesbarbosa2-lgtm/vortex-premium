#!/usr/bin/env python3
"""Make face and special buttons root-level overlay children so each stays above GL video."""
from pathlib import Path
import re
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
add_pattern=r'    private void addGridKey\(GridLayout grid, String text, int keyCode, int row, int column\) \{.*?\n    \}\n\n    private GridLayout.LayoutParams gridParams'
add_replacement='''    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        // Put each face key directly in the full-screen overlay, not inside the
        // GridLayout. A GLSurfaceView may be composited above nested descendants.
        Button button = keyButton(text, keyCode, dp(58), dp(58));
        String id = "face_" + text;
        button.setTag(id);
        int x = "A".equals(text) ? 76 : "B".equals(text) ? 84 : "C".equals(text) ? 76 : 84;
        int y = ("C".equals(text) || "D".equals(text)) ? 82 : 72;
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(dp(58), dp(58));
        gameOverlayRoot.addView(button, params);
        registerTouchControl(gameOverlayRoot, id, button, x, y);
    }

    private GridLayout.LayoutParams gridParams'''
s,n=re.subn(add_pattern,lambda _:add_replacement,s,count=1,flags=re.S)
assert n==1,'face button builder anchor not found exactly once'
special_pattern=r'    private void rebuildSpecialButtons\(\) \{.*?\n    \}\n\n    private Button overlayMenuButton'
special_replacement='''    private void rebuildSpecialButtons() {
        if (specialControlsRow == null || gameOverlayRoot == null) return;
        for (int slot = 0; slot < MAX_SPECIAL_SLOTS; slot++) endTouchSpecialChord(slot);
        specialControlsRow.removeAllViews();
        // Remove the old direct-overlay buttons before rebuilding the configurable
        // slots. Each button remains a top-level child above the GL game surface.
        for (int i = gameOverlayRoot.getChildCount() - 1; i >= 0; i--) {
            View child = gameOverlayRoot.getChildAt(i);
            Object tag = child.getTag();
            if (tag instanceof String && ((String) tag).startsWith("special_")) {
                gameOverlayRoot.removeViewAt(i);
                touchControlViews.remove(String.valueOf(tag));
                touchControlDefaults.remove(String.valueOf(tag));
            }
        }
        int visible = 0;
        for (int slot = 0; slot < MAX_SPECIAL_SLOTS; slot++) {
            if (specialTriggerForSlot(slot).isEmpty()) continue;
            Button button = specialChordButton(slot);
            int x = Math.min(82, 30 + visible * 10);
            FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(dp(58), dp(58));
            gameOverlayRoot.addView(button, params);
            registerTouchControl(gameOverlayRoot, "special_" + slot, button, x, 17);
            visible++;
        }
        specialControlsRow.setVisibility(View.GONE);
    }

    private Button overlayMenuButton'''
s,n=re.subn(special_pattern,lambda _:special_replacement,s,count=1,flags=re.S)
assert n==1,'special button builder anchor not found exactly once'
p.write_text(s,encoding='utf-8')
print('Moved all A/B/C/D and round special buttons into the top-level overlay; each now has normal saved x/y drag positions')
