Retro Core Access: Digimon World 2
Windows x64 testing build - 2026.09.21.1 (controller navigation update)

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

Controller navigation: hold L2 / left trigger on player 1's controller, then:
  D-pad Left / Right: previous / next category.
  D-pad Up / Down: previous / next target.
  Left-stick click (L3): start or stop guidance.
  Left face button (Square / Xbox X): repeat target or direction.
  Top face button (Triangle / Xbox Y): read location and coordinates.

Held D-pad directions repeat. Release shortcut buttons and center the sticks
before resuming play. A control still held when L2 is released stays blocked
until released, so it does not also move the player or select a game option.
Core Options > Input > DW2 Controller Navigation is enabled by default.
Disable it to use L2 for ordinary gameplay. Keyboard navigation remains available.
The bindings follow RetroPad positions after any frontend controller remapping.

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

The installer contains bundled cores; it does not download updates by itself.
New revisions use this same download link and filename:
https://github.com/buu420/RetroArch/releases/download/accessibility-2026.09.21/RetroArch-Accessibility-2026.09.21-Win64-Setup.exe
Download it again, close RetroArch Accessibility, and run it over the existing
installation. The build revision is shown at the top of this file and in the
installer's file properties, even though its download filename stays the same.

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
