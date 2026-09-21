RetroArch Accessibility with Digimon World 2
Windows x64 development build - 2026.09.21

Install
-------
Run RetroArch-Accessibility-2026.09.21-Win64-Setup.exe. This installs for
your Windows account into a separate RetroArch Accessibility folder.
Open RetroArch Accessibility from the Start menu. Speech is enabled on
first launch. NVDA is used when running; Windows speech is the fallback.

The Start menu also has Getting Started, Data Folder, and Uninstall entries.
The installer does not start a game automatically.

Play Digimon World 2
-------------------
Use your own USA game image (SLUS_011.93) and PlayStation BIOS. Put BIOS
files in the installation's system folder. In RetroArch choose Load Core,
then Sony - PlayStation (Beetle PSX - DW2 Accessibility), then Load Content
and select your game's CUE, CHD or M3U file. Keep a BIN beside its CUE.

The Beetle PSX HW - DW2 Accessibility core is also included for hardware
rendering. Start with the software Beetle PSX core if unsure.

Keyboard navigation during gameplay:
  Home / End: change navigation category.
  Page Up / Page Down: select target.
  Delete: repeat target or guidance direction.
  Numpad Enter: start or stop guidance.
  Scroll Lock: toggle Game Focus if RetroArch intercepts these keys.

Use the game's normal controls for movement and interactions. The core
includes dialogue and menu narration, battle details, named NPCs, domain
objects and floors, direct portal guidance, and story objectives.

Updates and player data
-----------------------
The two bundled cores are locked against RetroArch's core updater, so it
does not replace them with ordinary upstream builds. Install an updated
accessibility package to update this set. Other cores can still be added.

Reinstalling preserves retroarch.cfg, core options, controller settings,
saves, save states, game images and BIOS files. Uninstalling also keeps
player data. To reset settings, close RetroArch, rename retroarch.cfg,
then copy retroarch.accessibility-default.cfg to retroarch.cfg.

This package uses a matched experimental speech interface. Keep its
frontend and cores together; earlier private prototypes use a different
interface. This separate installation does not migrate an existing setup.

Source and credits
------------------
Frontend: https://github.com/buu420/RetroArch/tree/accessibility/core-speech
Core: https://github.com/buu420/beetle-psx-libretro/tree/dw2-accessibility
Speech proposal: https://github.com/libretro/RetroArch/pull/19603

This is a community accessibility build by buu420. RetroArch is developed
by the Libretro team and contributors; Beetle PSX derives from Mednafen.
NVDA Controller Client is by NV Access and contributors. RetroArch assets,
controller profiles and other bundled support files are from Libretro.

Licenses are in the licenses directory and with the bundled resources.
The companion Sources.zip contains the frontend and core source plus
packaging/build instructions. See BUILD-SOURCES.txt for dependency source
locations. Game-derived fallback dialogue in the cores is generated from
the builder's own game; it is not relicensed as emulator source.

No game image, PlayStation BIOS, personal saves or personal configuration
is included. The installer is unsigned. Complete playthrough coverage is
not claimed; report the location, input, expected speech and actual speech.
