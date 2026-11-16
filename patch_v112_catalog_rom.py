#!/usr/bin/env python3
"""Fix the shared 128-core catalog launch path for ROM ZIP containers."""
from pathlib import Path
p = Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
s = p.read_text()
old = '''        final String sha256;\n\n        CoreCatalogEntry(String id, String name, String system, String coreZip, String coreFile, String sha256) {'''
new = '''        final String sha256;\n        final String supportedExtensions;\n\n        CoreCatalogEntry(String id, String name, String system, String coreZip, String coreFile, String sha256, String supportedExtensions) {'''
assert old in s, 'catalog entry declaration anchor missing'
s=s.replace(old,new,1)
old='''            this.sha256 = sha256;\n        }\n    }'''
new='''            this.sha256 = sha256;\n            this.supportedExtensions = supportedExtensions;\n        }\n    }'''
assert old in s, 'catalog entry constructor anchor missing'
s=s.replace(old,new,1)
old='''            String hash = item.getString("sha256").toLowerCase(Locale.ROOT);'''
new='''            String hash = item.getString("sha256").toLowerCase(Locale.ROOT);\n            String extensions = item.optString("supportedExtensions", "");'''
assert old in s, 'catalog extension field anchor missing'
s=s.replace(old,new,1)
old='''            cores.add(new CoreCatalogEntry(id, name, system, zip, file, hash));'''
new='''            cores.add(new CoreCatalogEntry(id, name, system, zip, file, hash, extensions));'''
assert old in s, 'catalog entry construction anchor missing'
s=s.replace(old,new,1)
start=s.index('    private void openCatalogGame(Uri uri) throws Exception {')
end=s.index('    private void openSelectedGame(Uri uri, int requestCode) throws Exception {',start)
new_methods=r'''    private void openCatalogGame(Uri uri) throws Exception {
        enterImmersiveMode();
        final CoreCatalogEntry core = findCoreCatalogEntry(pendingCatalogCoreId);
        pendingCatalogCoreId = null;
        File game = copyRom(uri);
        String extension = fileExtension(game.getName());
        // Preserve existing behavior for normal files and cores which natively accept ZIP.
        if (!".zip".equals(extension) || supportsCatalogExtension(core, ".zip")) {
            launchCatalogGame(game, core);
            return;
        }

        ArrayList<String> matches = listMatchingCatalogZipEntries(game, core);
        // Metadata can be incomplete and some cores consume their own ZIP format.
        // If no clearly matching entry exists, pass the archive through unchanged.
        if (matches.isEmpty()) {
            launchCatalogGame(game, core);
            return;
        }
        // Extract the complete archive into a private, traversal-safe folder. This keeps
        // sidecar files together for formats such as CUE/BIN and multi-file games.
        final File extractedRoot = extractCatalogRomArchive(game);
        if (matches.size() == 1) {
            launchCatalogGame(resolveExtractedEntry(extractedRoot, matches.get(0)), core);
            return;
        }
        final String[] choices = matches.toArray(new String[matches.size()]);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha a ROM compatível com " + core.name)
                .setItems(choices, (dialog, which) -> {
                    try { launchCatalogGame(resolveExtractedEntry(extractedRoot, choices[which]), core); }
                    catch (Exception error) { showGameOpenError(error); }
                })
                .setNegativeButton("Cancelar", null).show();
    }

    private ArrayList<String> listMatchingCatalogZipEntries(File archive, CoreCatalogEntry core) throws Exception {
        ArrayList<String> matches = new ArrayList<>();
        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {
            java.util.Enumeration<? extends java.util.zip.ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                java.util.zip.ZipEntry entry = entries.nextElement();
                if (entry.isDirectory()) continue;
                if (supportsCatalogExtension(core, fileExtension(entry.getName()))) matches.add(entry.getName());
            }
        }
        return matches;
    }

    private String fileExtension(String name) {
        String base = new java.io.File(name).getName().toLowerCase(Locale.ROOT);
        int dot = base.lastIndexOf('.');
        return dot < 0 ? "" : base.substring(dot);
    }

    private boolean supportsCatalogExtension(CoreCatalogEntry core, String extension) {
        if (extension == null || extension.isEmpty()) return false;
        for (String value : core.supportedExtensions.toLowerCase(Locale.ROOT).split("\\|")) {
            String item = value.trim();
            if (!item.isEmpty() && ("." + item).equals(extension)) return true;
        }
        return false;
    }

    private String formatCatalogExtensions(CoreCatalogEntry core) {
        StringBuilder result = new StringBuilder();
        for (String value : core.supportedExtensions.split("\\|")) {
            String item = value.trim();
            if (item.isEmpty() || item.equals("/")) continue;
            if (result.length() > 0) result.append(", ");
            result.append('.').append(item);
        }
        return result.length() == 0 ? "formato específico do console" : result.toString();
    }

    private File extractCatalogRomArchive(File archive) throws Exception {
        File romDir = new File(getFilesDir(), "roms");
        File destinationRoot = new File(romDir, "catalog_zip_" + System.currentTimeMillis());
        if (!destinationRoot.mkdirs()) throw new IllegalStateException("Não foi possível preparar a extração segura do ZIP.");
        long total = 0;
        int files = 0;
        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {
            java.util.Enumeration<? extends java.util.zip.ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                java.util.zip.ZipEntry entry = entries.nextElement();
                String name = entry.getName().replace('\\', '/');
                if (name.startsWith("/") || name.matches("^[A-Za-z]:.*")) throw new IllegalArgumentException("O ZIP contém um caminho inválido; extração cancelada.");
                File target = new File(destinationRoot, name);
                String rootPath = destinationRoot.getCanonicalPath() + File.separator;
                if (!target.getCanonicalPath().startsWith(rootPath)) throw new IllegalArgumentException("O ZIP tenta gravar fora da pasta do jogo; extração cancelada.");
                if (entry.isDirectory()) {
                    if (!target.isDirectory() && !target.mkdirs()) throw new IllegalStateException("Não foi possível criar uma pasta do jogo.");
                    continue;
                }
                if (++files > 4096) throw new IllegalArgumentException("O ZIP contém arquivos demais (limite: 4096).");
                File parent = target.getParentFile();
                if (!parent.isDirectory() && !parent.mkdirs()) throw new IllegalStateException("Não foi possível preparar os arquivos auxiliares da ROM.");
                try (InputStream input = zip.getInputStream(entry); FileOutputStream output = new FileOutputStream(target)) {
                    byte[] buffer = new byte[64 * 1024];
                    int count;
                    while ((count = input.read(buffer)) != -1) {
                        total += count;
                        if (total > 1024L * 1024L * 1024L) throw new IllegalArgumentException("O ZIP descompactado excede o limite de 1 GiB.");
                        output.write(buffer, 0, count);
                    }
                }
            }
        } catch (Exception error) {
            deleteTree(destinationRoot);
            throw error;
        }
        return destinationRoot;
    }

    private void deleteTree(File file) {
        if (file == null || !file.exists()) return;
        File[] children = file.listFiles();
        if (children != null) for (File child : children) deleteTree(child);
        file.delete();
    }

    private File resolveExtractedEntry(File rootDir, String entryName) throws Exception {
        String safeName = entryName.replace('\\', '/');
        File target = new File(rootDir, safeName);
        if (!target.getCanonicalPath().startsWith(rootDir.getCanonicalPath() + File.separator) || !target.isFile()) {
            throw new IllegalArgumentException("A ROM escolhida não foi encontrada dentro do ZIP.");
        }
        return target;
    }

    private void launchCatalogGame(File game, CoreCatalogEntry core) throws Exception {
        File library = extractCatalogCore(core);
        startRetroGame(game, library, core.coreFile, core.name + " • " + core.system);
    }

'''
s=s[:start]+new_methods+s[end:]
p.write_text(s)
print('Patched 128-core ROM ZIP handling with extension checks, safe archive extraction and sidecar preservation')
