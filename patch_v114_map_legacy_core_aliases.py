#!/usr/bin/env python3
"""Map old built-in core filenames to catalog cores bundled in the 128-core APK."""
from pathlib import Path
p=Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s=p.read_text(encoding='utf-8')
anchor='''    private CoreCatalogEntry findCoreCatalogEntryByFile(String coreFile) throws Exception {
        if (coreFile == null || !coreFile.matches("[A-Za-z0-9._-]+[.]so")) return null;
        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.coreFile.equals(coreFile)) return entry;
        return null;
    }
'''
replacement='''    private CoreCatalogEntry findCoreCatalogEntryByFile(String coreFile) throws Exception {
        if (coreFile == null || !coreFile.matches("[A-Za-z0-9._-]+[.]so")) return null;
        ArrayList<CoreCatalogEntry> cores = loadCoreCatalog();
        for (CoreCatalogEntry entry : cores) if (entry.coreFile.equalsIgnoreCase(coreFile)) return entry;

        // Older console shortcuts named cores that are not in this APK. Map those
        // stable legacy filenames to the closest matching core that is actually
        // bundled, instead of asking Android to dlopen a nonexistent JNI library.
        String wanted = coreFile.toLowerCase(Locale.ROOT);
        String[] preferredIds;
        if (wanted.contains("snes9x") || wanted.contains("snes")) {
            preferredIds = new String[]{"mesen-s", "mednafen_snes", "bsnes", "bsnes2014_balanced"};
        } else if (wanted.contains("genesis_plus") || wanted.contains("picodrive") || wanted.contains("genesis")) {
            preferredIds = new String[]{"blastem", "clownmdemu", "gearsystem"};
        } else if (wanted.contains("fceumm") || wanted.contains("quicknes")) {
            preferredIds = new String[]{"fceumm", "mesen", "nestopia"};
        } else if (wanted.contains("gambatte")) {
            preferredIds = new String[]{"gambatte", "DoubleCherryGB", "mesen2"};
        } else if (wanted.contains("mednafen_gba") || wanted.contains("mgba")) {
            preferredIds = new String[]{"mgba", "gpsp", "mednafen_gba"};
        } else if (wanted.contains("stella")) {
            preferredIds = new String[]{"stella2014", "stella", "stella2023"};
        } else if (wanted.contains("prosystem")) {
            preferredIds = new String[]{"prosystem"};
        } else if (wanted.contains("pce")) {
            preferredIds = new String[]{"mednafen_pce_fast", "geargrafx", "mednafen_pce"};
        } else if (wanted.contains("lynx")) {
            preferredIds = new String[]{"mednafen_lynx", "gearlynx", "handy"};
        } else if (wanted.contains("ngp") || wanted.contains("neopop")) {
            preferredIds = new String[]{"mednafen_ngp"};
        } else if (wanted.contains("wswan") || wanted.contains("wonderswan")) {
            preferredIds = new String[]{"mednafen_wswan"};
        } else {
            return null;
        }
        for (String preferred : preferredIds) {
            for (CoreCatalogEntry entry : cores) if (entry.id.equalsIgnoreCase(preferred)) return entry;
        }
        return null;
    }
'''
assert s.count(anchor)==1, 'legacy lookup anchor missing or duplicated'
s=s.replace(anchor,replacement,1)
p.write_text(s,encoding='utf-8')
print('Mapped 11 legacy console-core aliases to available packaged cores, preserving exact filename matches first')
