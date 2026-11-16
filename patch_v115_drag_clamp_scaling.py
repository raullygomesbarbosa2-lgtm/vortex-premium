#!/usr/bin/env python3
"""Fix touch-layout dragging: account for scaled parent groups and keep controls onscreen."""
from pathlib import Path
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='''            int maxX = Math.max(0, gameOverlayRoot.getWidth() - view.getWidth());
            int maxY = Math.max(0, gameOverlayRoot.getHeight() - view.getHeight());
            int left = Math.max(0, Math.min(maxX, Math.round(desiredLeft - rootLocation[0])));
            int top = Math.max(0, Math.min(maxY, Math.round(desiredTop - rootLocation[1])));
            int x = maxX == 0 ? 0 : Math.round(left * 100f / maxX);
            int y = maxY == 0 ? 0 : Math.round(top * 100f / maxY);
            setTouchPosition(gameOverlayRoot, view, x, y);
            return;
        }
        if (view.getParent() instanceof android.view.ViewGroup) {
            android.view.ViewGroup parent = (android.view.ViewGroup) view.getParent();
            int[] parentLocation = new int[2];
            parent.getLocationInWindow(parentLocation);
            float baseLeft = parentLocation[0] + view.getLeft();
            float baseTop = parentLocation[1] + view.getTop();
            float minX = rootLocation[0] - baseLeft;
            float minY = rootLocation[1] - baseTop;
            float maxX = rootLocation[0] + gameOverlayRoot.getWidth() - view.getWidth() - baseLeft;
            float maxY = rootLocation[1] + gameOverlayRoot.getHeight() - view.getHeight() - baseTop;
            view.setTranslationX(Math.max(minX, Math.min(maxX, desiredLeft - baseLeft)));
            view.setTranslationY(Math.max(minY, Math.min(maxY, desiredTop - baseTop)));
        }
'''
new='''            float sx = Math.max(0.01f, Math.abs(view.getScaleX()));
            float sy = Math.max(0.01f, Math.abs(view.getScaleY()));
            float width = view.getWidth(), height = view.getHeight();
            // Scale around the center: constrain the full visible bounds, not only
            // the unscaled layout box, so large controls cannot be dragged offscreen.
            float minLeft = Math.max(0f, (sx - 1f) * width / 2f);
            float minTop = Math.max(0f, (sy - 1f) * height / 2f);
            float maxLeft = Math.max(minLeft, gameOverlayRoot.getWidth() - (sx + 1f) * width / 2f);
            float maxTop = Math.max(minTop, gameOverlayRoot.getHeight() - (sy + 1f) * height / 2f);
            float left = Math.max(minLeft, Math.min(maxLeft, desiredLeft - rootLocation[0]));
            float top = Math.max(minTop, Math.min(maxTop, desiredTop - rootLocation[1]));
            float rangeX = maxLeft - minLeft, rangeY = maxTop - minTop;
            int x = rangeX == 0f ? 0 : Math.round((left - minLeft) * 100f / rangeX);
            int y = rangeY == 0f ? 0 : Math.round((top - minTop) * 100f / rangeY);
            setTouchPosition(gameOverlayRoot, view, x, y);
            return;
        }
        if (view.getParent() instanceof android.view.ViewGroup) {
            android.view.ViewGroup parent = (android.view.ViewGroup) view.getParent();
            int[] parentLocation = new int[2];
            parent.getLocationInWindow(parentLocation);
            float parentScaleX = Math.max(0.01f, Math.abs(parent.getScaleX()));
            float parentScaleY = Math.max(0.01f, Math.abs(parent.getScaleY()));
            float childScaleX = Math.max(0.01f, Math.abs(view.getScaleX()));
            float childScaleY = Math.max(0.01f, Math.abs(view.getScaleY()));
            float baseLeft = parentLocation[0] + view.getLeft() * parentScaleX;
            float baseTop = parentLocation[1] + view.getTop() * parentScaleY;
            float halfW = view.getWidth() * childScaleX * parentScaleX / 2f;
            float halfH = view.getHeight() * childScaleY * parentScaleY / 2f;
            float centerBaseX = baseLeft + view.getWidth() * parentScaleX / 2f;
            float centerBaseY = baseTop + view.getHeight() * parentScaleY / 2f;
            float wantedCenterX = desiredLeft + halfW;
            float wantedCenterY = desiredTop + halfH;
            float minCenterX = rootLocation[0] + halfW;
            float minCenterY = rootLocation[1] + halfH;
            float maxCenterX = rootLocation[0] + gameOverlayRoot.getWidth() - halfW;
            float maxCenterY = rootLocation[1] + gameOverlayRoot.getHeight() - halfH;
            float screenDx = Math.max(minCenterX, Math.min(maxCenterX, wantedCenterX)) - centerBaseX;
            float screenDy = Math.max(minCenterY, Math.min(maxCenterY, wantedCenterY)) - centerBaseY;
            // Android applies child translations in the parent's local coordinate
            // space. Convert screen-space finger motion through the parent scale.
            view.setTranslationX(screenDx / parentScaleX);
            view.setTranslationY(screenDy / parentScaleY);
            view.bringToFront();
            parent.setClipChildren(false);
            parent.setClipToPadding(false);
        }
'''
assert s.count(old)==1, 'drag coordinate block did not match exactly once'
s=s.replace(old,new,1)
# Account for scaled controls when restoring or changing positions as well.
old='''        params.gravity = Gravity.TOP | Gravity.LEFT;
        params.leftMargin = Math.round(Math.max(0, parent.getWidth() - view.getWidth()) * Math.max(0, Math.min(100, x)) / 100f);
        params.topMargin = Math.round(Math.max(0, parent.getHeight() - view.getHeight()) * Math.max(0, Math.min(100, y)) / 100f);
'''
new='''        params.gravity = Gravity.TOP | Gravity.LEFT;
        float sx = Math.max(0.01f, Math.abs(view.getScaleX()));
        float sy = Math.max(0.01f, Math.abs(view.getScaleY()));
        float minLeft = Math.max(0f, (sx - 1f) * view.getWidth() / 2f);
        float minTop = Math.max(0f, (sy - 1f) * view.getHeight() / 2f);
        float maxLeft = Math.max(minLeft, parent.getWidth() - (sx + 1f) * view.getWidth() / 2f);
        float maxTop = Math.max(minTop, parent.getHeight() - (sy + 1f) * view.getHeight() / 2f);
        float fractionX = Math.max(0, Math.min(100, x)) / 100f;
        float fractionY = Math.max(0, Math.min(100, y)) / 100f;
        params.leftMargin = Math.round(minLeft + (maxLeft - minLeft) * fractionX);
        params.topMargin = Math.round(minTop + (maxTop - minTop) * fractionY);
'''
assert s.count(old)==1, 'position restoration block did not match exactly once'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Patched scaled-control drag bounds and parent-local translation conversion')
