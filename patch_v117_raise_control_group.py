#!/usr/bin/env python3
"""Raise the whole on-screen control group while its nested buttons are dragged."""
from pathlib import Path
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='''        final boolean nested;
        final float offsetX;
        final float offsetY;
        TouchControlDrag(View view, String id, boolean nested, float offsetX, float offsetY) {
            this.view = view; this.id = id; this.nested = nested;
            this.offsetX = offsetX; this.offsetY = offsetY;
        }
'''
new='''        final boolean nested;
        final float offsetX;
        final float offsetY;
        final View host;
        final float hostOriginalElevation;
        TouchControlDrag(View view, String id, boolean nested, float offsetX, float offsetY, View host) {
            this.view = view; this.id = id; this.nested = nested;
            this.offsetX = offsetX; this.offsetY = offsetY;
            this.host = host;
            this.hostOriginalElevation = host == null ? 0f : host.getElevation();
        }
        void raiseHost(int elevation) {
            if (host != null) {
                android.view.ViewParent ancestor = host.getParent();
                while (ancestor instanceof android.view.ViewGroup) {
                    android.view.ViewGroup group = (android.view.ViewGroup) ancestor;
                    group.setClipChildren(false);
                    group.setClipToPadding(false);
                    if (group == host.getRootView()) break;
                    ancestor = group.getParent();
                }
                host.setElevation(elevation);
                host.bringToFront();
                host.requestLayout();
                host.invalidate();
            }
        }
        void restoreHost() {
            if (host != null) {
                host.setElevation(hostOriginalElevation);
                host.invalidate();
            }
        }
'''
assert s.count(old)==1, 'drag class anchor mismatch'
s=s.replace(old,new,1)
old='''                activeTouchControlDrags.put(pointerId, new TouchControlDrag(target, id, nested,
                        x + rootLocation[0] - targetLocation[0], y + rootLocation[1] - targetLocation[1]));
                target.setElevation(dp(18));
'''
new='''                View host = target;
                while (host.getParent() instanceof View && host.getParent() != gameOverlayRoot)
                    host = (View) host.getParent();
                TouchControlDrag drag = new TouchControlDrag(target, id, nested,
                        x + rootLocation[0] - targetLocation[0], y + rootLocation[1] - targetLocation[1], host);
                activeTouchControlDrags.put(pointerId, drag);
                // Face and special buttons live inside a container. Raising only
                // the child cannot put it above the GL game surface; raise the
                // direct overlay child (the entire button group) for this gesture.
                drag.raiseHost(dp(30));
                target.setElevation(dp(31));
'''
assert s.count(old)==1, 'touch-down host setup anchor mismatch'
s=s.replace(old,new,1)
old='''                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
'''
new='''                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
                drag.restoreHost();
'''
assert s.count(old)==1, 'touch-up restore anchor mismatch'
s=s.replace(old,new,1)
old='''                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
            }
            activeTouchControlDrags.clear();
'''
new='''                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
                drag.restoreHost();
            }
            activeTouchControlDrags.clear();
'''
assert s.count(old)==1, 'touch-cancel restore anchor mismatch'
s=s.replace(old,new,1)
old='''            view.setTranslationX(screenDx / parentScaleX);
            view.setTranslationY(screenDy / parentScaleY);
            view.bringToFront();
            parent.setClipChildren(false);
            parent.setClipToPadding(false);
'''
new='''            view.setTranslationX(screenDx / parentScaleX);
            view.setTranslationY(screenDy / parentScaleY);
            view.bringToFront();
            parent.setClipChildren(false);
            parent.setClipToPadding(false);
            // Keep the overlay group above the GL view through the whole drag,
            // including face buttons and configured special/chord buttons.
            for (TouchControlDrag active : activeTouchControlDrags.values())
                if (active.view == view) { active.raiseHost(dp(30)); break; }
'''
assert s.count(old)==1, 'nested drag host redraw anchor mismatch'
s=s.replace(old,new,1)
# If editing is ended while a pointer is still down, restore elevated hosts too.
old='''        for (TouchControlDrag drag : activeTouchControlDrags.values()) persistTouchControlDrag(drag);
        activeTouchControlDrags.clear();
'''
new='''        for (TouchControlDrag drag : activeTouchControlDrags.values()) {
            persistTouchControlDrag(drag);
            drag.view.setElevation(0f);
            drag.restoreHost();
        }
        activeTouchControlDrags.clear();
'''
assert s.count(old)==1, 'editor stop cleanup anchor mismatch'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Patched complete face/special overlay group z-order during editing drags')
