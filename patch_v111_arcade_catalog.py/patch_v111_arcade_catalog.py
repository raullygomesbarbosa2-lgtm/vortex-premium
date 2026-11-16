#!/usr/bin/env python3
"""Route Arcade choices through the bundled core catalog."""
from pathlib import Path
import re
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text()
pattern=r'    private void showArcadeCoreChooser\(File rom\) \{.*?\n    \}\n(?=\n    private void launchSelectedGame)'
replacement='''    private void showArcadeCoreChooser(File rom) {
        try {
            if (!isArm64AppProcess()) throw new IllegalStateException("Os núcleos Arcade do catálogo exigem a versão ARM64 do app.");
            ArrayList<CoreCatalogEntry> arcadeCores = new ArrayList<>();
            Set<String> ids = new HashSet<>(java.util.Arrays.asList("fbneo", "mamearcade", "mame2016", "hbmame", "dice"));
            for (CoreCatalogEntry core : loadCoreCatalog()) {
                if (ids.contains(core.id) && core.system.toLowerCase(Locale.ROOT).contains("arcade")) arcadeCores.add(core);
            }
            if (arcadeCores.isEmpty()) throw new IllegalStateException("O catálogo não contém núcleos Arcade compatíveis.");
            String[] labels = new String[arcadeCores.size()];
            for (int i=0; i<arcadeCores.size(); i++) {
                CoreCatalogEntry core=arcadeCores.get(i);
                labels[i]=core.name + " • " + core.coreFile;
            }
            new android.app.AlertDialog.Builder(this)
                .setTitle("Arcade • núcleo disponível / versão")
                .setItems(labels, (dialog, which) -> {
                    try {
                        CoreCatalogEntry core=arcadeCores.get(which);
                        File extracted=extractCatalogCore(core);
                        startRetroGame(rom, extracted, core.coreFile, core.name + " • " + core.system);
                    } catch (Exception error) { showGameOpenError(error); }
                })
                .setNegativeButton("Cancelar", null).show();
        } catch (Exception error) { showGameOpenError(error); }
    }'''
s2,n=re.subn(pattern,lambda _:replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('Arcade chooser anchor not found')
p.write_text(s2)
