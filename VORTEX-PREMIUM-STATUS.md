# Vortex Premium — source snapshot and status

This repository contains a source snapshot of the real Android-native Vortix/NeoHack Libretro emulator project, copied from the upstream source repository. It is not a newly completed, signed or device-tested Vortex Premium release. The original upstream repository is unchanged.

## What is actually in the source

- Native Android application code with LibretroDroid integration and native console cores; this is not a WebView/wrapper demo.
- Existing touchscreen controls, and source patch scripts for per-game layout dragging and control configuration (`patch_v108_move_controls.py`, preceded by `patch_v105_game_controls.py` and `patch_v107_dynamic_specials.py`). These are source changes; no APK build from these patches was verified here.
- Green/neon visual palette is implemented by the existing source patch sequence (`patch_v105_game_controls.py`).
- `app/src/main/assets/core_catalog.json` has 190 unique catalog entries: 165 Libretro and 25 engine/virtual entries. This is catalog metadata, not 190 cores bundled or verified in an APK. The ARM64 preparation script validates the catalog manifest and pinned source metadata; normalized core packages are downloaded during CI, not checked into this source snapshot. Do not describe all 190 as independently running game cores.
- The pre-existing workflow has an ARM64-only experimental 190-entry build and an ARMv7 variant catalog of 178 entries. There is no verified universal APK here; ARMv7 omits entries and the workflow's output/build status is unverified.
- The original Vortix APK was inspected separately and contains 16 Libretro cores plus LibretroDroid for ARM64. It is not a Vortex Premium build and has not been republished here.

## Android version, release and testing

The upstream generated project workflows declare `minSdk 21` (Android 5.0), not Android 6.0 (API 23). This source snapshot must not be advertised as Android 6.0+ until the build configuration is changed and an APK is checked. No release APK was built, signed, installed, or tested on a physical phone as part of this snapshot. No ROM was run on a device. No APK download link is available yet.

## Licenses and distribution

Core license terms vary. The catalog includes modules with non-commercial restrictions (including MAME-family notices); the existing preparation script filters certain license statuses but that does not constitute legal clearance for the full set or commercial sale. Review the per-core license and notice/source obligations for the exact cores selected before redistribution or sale. No ROMs, BIOS, Pix key or user content are included in this archive.

## Source archive

`vortex-premium-source.zip` is a convenience archive of source files from the upstream repository, excluding Git history and compiled APKs. Validate the build and each core/license selection before making a release claim.
