#!/usr/bin/env python3
"""Route built-in console buttons to the packaged 128-core catalog when the JNI copy is absent."""
from pathlib import Path
p = Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s = p.read_text(encoding='utf-8')
old='''    private CoreCatalogEntry findCoreCatalogEntry(String id) throws Exception {
        if (id == null) throw new IllegalStateException("A seleção do núcleo foi perdida. Escolha o núcleo novamente.");
        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.id.equals(id)) return entry;
        throw new IllegalArgumentException("O núcleo selecionado não está mais no catálogo. Escolha outro núcleo.");
    }
'''
new='''    private CoreCatalogEntry findCoreCatalogEntry(String id) throws Exception {
        if (id == null) throw new IllegalStateException("A seleção do núcleo foi perdida. Escolha o núcleo novamente.");
        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.id.equals(id)) return entry;
        throw new IllegalArgumentException("O núcleo selecionado não está mais no catálogo. Escolha outro núcleo.");
    }

    private CoreCatalogEntry findCoreCatalogEntryByFile(String coreFile) throws Exception {
        if (coreFile == null || !coreFile.matches("[A-Za-z0-9._-]+[.]so")) return null;
        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.coreFile.equals(coreFile)) return entry;
        return null;
    }
'''
assert s.count(old)==1, 'core lookup anchor not unique'
s=s.replace(old,new,1)
old='''    private void startRetroGame(File rom, String coreLibrary, String systemLabel) {
        File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);
        startRetroGame(rom, nativeCore, coreLibrary, systemLabel);
    }
'''
new='''    private void startRetroGame(File rom, String coreLibrary, String systemLabel) {
        try {
            File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);
            if (!nativeCore.isFile() || nativeCore.length() == 0) {
                // The 128-core build stores extra Libretro cores in assets/corepacks,
                // not in Android's JNI library directory. Resolve the same core by its
                // exact filename and extract/verify it before handing it to LibretroDroid.
                CoreCatalogEntry packagedCore = findCoreCatalogEntryByFile(coreLibrary);
                if (packagedCore == null) {
                    throw new IllegalStateException("O núcleo " + coreLibrary + " não está instalado neste APK nem no catálogo dos 128 núcleos.");
                }
                nativeCore = extractCatalogCore(packagedCore);
            }
            startRetroGame(rom, nativeCore, coreLibrary, systemLabel);
        } catch (Exception error) {
            showGameOpenError(error);
        }
    }
'''
assert s.count(old)==1, 'launcher overload anchor not unique'
s=s.replace(old,new,1)
p.write_text(s, encoding='utf-8')
print('Built-in console launches now fall back to SHA-verified corepack assets for all catalog entries')
