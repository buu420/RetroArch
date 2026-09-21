#!/usr/bin/env python3
"""Exercise the real installer in a new isolated directory on Windows."""
# Copyright 2026 buu420. SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import winreg
from pathlib import Path

REGKEY = r"Software\RetroArchAccessibility"
UNINSTALLKEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\RetroArchAccessibility"


def registry_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGKEY, 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            return winreg.QueryValueEx(key, "InstallDir")[0]
    except FileNotFoundError:
        return None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, **kwargs):
    return subprocess.run(command, timeout=180, capture_output=True,
                          creationflags=subprocess.CREATE_NO_WINDOW, **kwargs)


def installer_run(installer, destination):
    # NSIS requires /D last and unquoted, including when its path has spaces.
    command = subprocess.list2cmdline([str(installer), "/S"]) + " /D=" + str(destination)
    return execute(command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installer", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True,
                        help="New test directory; this script never recursively deletes it")
    args = parser.parse_args()
    assert args.installer.is_file(), "Installer has not been built"
    assert registry_path() is None, "An existing accessibility installation must not be changed by this test"
    shortcuts = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/RetroArch Accessibility"
    assert not shortcuts.exists(), "Existing user shortcuts must not be overwritten by this test"
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    destination = work / "Installed avec espaces é"
    checks = []
    interrupted = work / "Interrupted install"
    command = subprocess.list2cmdline([str(args.installer), "/S"]) + " /D=" + str(interrupted)
    process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.monotonic() + 90
    marker = interrupted / "accessibility-install.ini"
    def marker_ready():
        try:
            data = marker.read_bytes()
            encoding = "utf-16" if data.startswith(b"\xff\xfe") else "utf-8"
            return "buu420-retroarch-accessibility" in data.decode(encoding)
        except (OSError, UnicodeError):
            return False
    while not marker_ready() and process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.02)
    assert marker_ready(), "Setup did not establish ownership before extraction"
    assert process.poll() is None, "Setup finished before interruption could be tested"
    process.kill()
    process.wait(timeout=10)
    assert installer_run(args.installer, interrupted).returncode == 0, "Interrupted install could not be repaired"
    command = subprocess.list2cmdline([str(interrupted / "Uninstall-Accessibility.exe"), "/S"])
    assert execute(command + " _?=" + str(interrupted), cwd=work).returncode == 0
    assert registry_path() is None
    assert not shortcuts.exists()
    checks.append("An interrupted first install retains ownership, repairs successfully and can be uninstalled")
    result = installer_run(args.installer, destination)
    assert result.returncode == 0, f"Install failed: {result.returncode}"
    assert Path(registry_path()) == destination
    assert len(list(shortcuts.glob("*.lnk"))) == 4
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALLKEY, 0,
                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
        uninstall_command = winreg.QueryValueEx(key, "UninstallString")[0]
        assert uninstall_command == f'"{destination / "Uninstall-Accessibility.exe"}"'
    manifest = json.loads((destination / "package-manifest.json").read_text())
    for file in manifest["files"]:
        assert digest(destination / file["path"]) == file["sha256"], file["path"]
    config = destination / "retroarch.cfg"
    assert 'accessibility_enable = "true"' in config.read_text()
    assert 'libretro_directory = ":\\cores"' in config.read_text()
    for name in ("mednafen_psx_libretro", "mednafen_psx_hw_libretro"):
        assert (destination / "cores" / (name + ".lck")).exists()
        assert "DW2 Accessibility" in (destination / "info" / (name + ".info")).read_text()
    checks.append(f"Fresh install: all {len(manifest['files'])} packaged file hashes, Unicode/spaces, speech defaults, core metadata/locks, registration and shortcuts")
    env = os.environ.copy()
    env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    result = execute([str(destination / "retroarch.exe"), "--features"], cwd=destination, env=env)
    assert result.returncode == 0, (result.returncode, result.stderr)
    assert b"OpenGL" in result.stdout and b"yes" in result.stdout
    (work / "runtime-features.txt").write_bytes(result.stdout)
    result = execute([str(destination / "retroarch.exe"), "--version"], cwd=destination, env=env)
    assert result.returncode == 0
    (work / "runtime-version.txt").write_bytes(result.stdout + result.stderr)
    loader = """import ctypes,os,sys
from pathlib import Path
root=Path(sys.argv[1])
with os.add_dll_directory(str(root)):
 for name in ('mednafen_psx_libretro','mednafen_psx_hw_libretro'):
  core=ctypes.CDLL(str(root/'cores'/(name+'.dll')))
  core.retro_api_version.restype=ctypes.c_uint
  assert core.retro_api_version()==1
print('Both installed cores load and report libretro API 1')
"""
    result = execute([sys.executable, "-c", loader, str(destination)], cwd=destination, env=env)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    checks.append("Frontend starts and both cores load with only Windows on PATH")
    sentinels = {
        "retroarch.cfg": config.read_bytes() + b'\n# User settings sentinel\n',
        "retroarch-core-options.cfg": b'beetle_psx_internal_resolution = "2x"\n',
        "saves/player.mcr": b"personal memory card",
        "states/player.state": b"personal save state",
        "system/scph5501.bin": b"test sentinel, not a real BIOS",
        "games/my game.cue": b"test sentinel, not a real game",
        "config/my controls.cfg": b"user controller mapping",
        "cores/user_added_libretro.dll": b"user-added core sentinel",
        "assets/user-added.txt": b"user asset",
    }
    profile = next((destination / "autoconfig").rglob("*.cfg"))
    sentinels[str(profile.relative_to(destination))] = b"user-edited controller profile"
    for name, contents in sentinels.items():
        file = destination / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(contents)
    (destination / "retroarch.exe").write_bytes(b"old build to replace")
    # No /D here: upgrade must recover the previous custom path from 64-bit registry.
    result = execute([str(args.installer), "/S"])
    assert result.returncode == 0, result.returncode
    expected = next(file["sha256"] for file in manifest["files"] if file["path"] == "retroarch.exe")
    assert digest(destination / "retroarch.exe") == expected
    for name, contents in sentinels.items():
        assert (destination / name).read_bytes() == contents, name
    checks.append("Upgrade replaces program while preserving all ten player-data sentinels")
    unrelated = work / "Another RetroArch"
    unrelated.mkdir()
    (unrelated / "retroarch.exe").write_bytes(b"unrelated executable")
    (unrelated / "retroarch.cfg").write_bytes(b"unrelated config")
    result = installer_run(args.installer, unrelated)
    assert result.returncode != 0, "Installer accepted an unrelated RetroArch"
    assert (unrelated / "retroarch.exe").read_bytes() == b"unrelated executable"
    assert (unrelated / "retroarch.cfg").read_bytes() == b"unrelated config"
    assert Path(registry_path()) == destination
    checks.append("Unrelated RetroArch installation rejected without changes")
    too_long = work / ("Long destination " + "x" * 170)
    result = installer_run(args.installer, too_long)
    assert result.returncode != 0, "Installer accepted a path too long for frontend resources"
    assert not too_long.exists()
    assert Path(registry_path()) == destination
    checks.append("Excessive destination length rejected before extraction regardless of Windows long-path policy")
    command = subprocess.list2cmdline([str(destination / "Uninstall-Accessibility.exe"), "/S"])
    command += " _?=" + str(destination)
    result = execute(command, cwd=work)
    assert result.returncode == 0, result.returncode
    assert registry_path() is None
    assert not shortcuts.exists()
    assert not (destination / "retroarch.exe").exists()
    assert not (destination / "cores/mednafen_psx_libretro.dll").exists()
    assert not (destination / "cores/mednafen_psx_hw_libretro.dll").exists()
    for name, contents in sentinels.items():
        assert (destination / name).read_bytes() == contents, name
    checks.append("Uninstall removes installed programs/registration/shortcuts and preserves every player-data sentinel")
    (work / "verification.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
