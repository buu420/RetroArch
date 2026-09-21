# Windows accessibility installer implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Deliver a local Windows x64 installer containing the speech frontend and both DW2 cores.

**Architecture:** Use NSIS 3 Modern UI with a clean allowlisted payload from the existing official 1.22.2 archive, replacing executables with builds of the published speech frontend and core forks. Install into a separate per-user folder. Generate install and removal instructions from the same payload list; preserve player data.

**Tech Stack:** Python 3, NSIS 3.12, MSYS2/MinGW-w64.

**Spec:** The user's installer request and their explicit follow-up to include the DW2 cores. Existing permission to proceed covers the implementation.

## Global constraints

- Package frontend and cores using speech command 95 together.
- Preserve the user's installed prototype and all personal game data.
- Use a clean default config with accessibility enabled, relative data directories, and working core paths.
- Include software and hardware PSX cores, core metadata, required DLLs, assets, and licenses.
- Do not publish an installer or change the focused upstream PR as part of this local packaging task.
- Archive corresponding source/build instructions without private Git history or personal files.

## Review focus

- Existing settings and saves must survive upgrade and uninstall.
- Paths containing spaces and Unicode must work.
- Another RetroArch installation must not be overwritten or unregistered.
- The runtime must resolve dependencies without MSYS2 on PATH.
- Installed core information and the speech ABI must match the binaries.

## Task 1: Build matching runtime

- [x] Build the published speech frontend with accessibility, SAPI, NVDA, Ozone, RGUI, OpenGL/core, ZIP, networking, and database support.
- [x] Preserve the completed software core build and rebuild the hardware variant from the same core commit.
- [x] Record hashes, dependencies, source commits and exact compiler invocation.
- [x] Run the speech bridge harness and binary startup checks. Actual frontend-to-recording-NVDA delivery passed; both real cores also booted the owned game for 600 frames in isolated data directories. Hardware used OpenGL core and Slang.

## Task 2: Package

- [x] Write `pkg/windows-accessibility/build.py` to stage only explicit official distribution data, matched binaries, required runtime DLLs, config, README, core metadata and license/source notices.
- [x] Write `pkg/windows-accessibility/RetroArchAccessibility.nsi` using standard NSIS pages and a unique installation identity. Generate exact file installation/deletion lists. Keep mutable player data.
- [x] Add `pkg/windows-accessibility/retroarch.cfg` and `README.txt` for accessible first launch and core setup.
- [x] Build installer and source archive. Final checksums follow the final source snapshot.

## Task 3: Verify and deliver

- [x] Install silently into a dedicated test folder containing spaces and Unicode; inspect config, binaries, metadata, registry and shortcuts.
- [x] Add save/config/BIOS/game/core sentinel files, reinstall, uninstall and assert all sentinels survive while installed program files are removed.
- [x] Reject an unrelated existing RetroArch installation without changing it.
- [x] Run the installed executable and load both core DLLs with only Windows runtime paths available.
- [x] Obtain one independent installer review and fix actionable findings. NVDA define, early ownership marker, archive provenance and /D precedence corrected. Reviewer reports no remaining actionable issue.
- [x] Place installer, source archive, README and checksum file in the release output directory and report exact verification limits.

## Progress and decisions

Ruling: Use the public command-95 pair rather than the installed command-82 prototype, because the user has just published source forks intended for sharing. This requires a full frontend build and fresh hardware core build. Keep the current installed setup untouched.

Ruling: No original NSIS source or installer was found in the likely local locations or public repository trees. The installed uninstaller identifies NSIS; use official NSIS Modern UI and the verified clean official distribution archive as the base.

Ruling: Use the local packaging makefile wrapper to enable required shader support, NVDA/SAPI defines and a missing D3D9 compiler object. The upstream speech PR and frontend implementation are unchanged. Rebuild dependencies track both packaging build scripts.

Ruling: Preserve autoconfig profiles as mutable user settings. Retain the ownership marker with player data after removal, allowing later reinstalls into that directory. Installer compilation uses an immutable script snapshot.

Ruling: Use a packaging-only Unicode Windows entrypoint to pass UTF-8 arguments to RetroArch. A real speech test in an accented directory exposed the original ACP conversion; it passes with the new entrypoint.

Ruling: Enforce the destination length calculated from the longest bundled resource. The frontend does not support arbitrarily long resource paths, so enabling long paths only in Setup would produce an incomplete usable installation. The normal install test includes spaces and an accented character; a separate excessive-path test verifies rejection before extraction.
