#!/usr/bin/env python3
"""Stage clean resources and a matched runtime, then compile the NSIS installer."""
# Copyright 2026 buu420. SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

VERSION = "2026.09.21.1"
# Keep the public download filenames stable when publishing a new revision.
# The real build version is recorded inside Setup, the manifest and README.
STEM = "RetroArch-Accessibility-2026.09.21-Win64"
RESOURCE_DIRS = ("assets", "autoconfig", "database", "info", "overlays", "shaders")
CORE_NAMES = ("mednafen_psx_libretro", "mednafen_psx_hw_libretro")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def nsis_literal(value):
    return str(value).replace("$", "$$").replace('"', '$\\"')


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def provenance(source):
    if (source / ".git").exists():
        commit = run("git", "rev-parse", "HEAD", cwd=source,
                     capture_output=True, text=True).stdout.strip()
        files = run("git", "ls-files", "-z", cwd=source, capture_output=True)
        return {"commit": commit, "files": sorted(set(files.stdout.decode("utf-8").split("\0")) - {""})}
    metadata = json.loads((source / ".accessibility-source.json").read_text(encoding="utf-8"))
    for relative in metadata["files"]:
        if not (source / relative).resolve().is_relative_to(source.resolve()):
            raise ValueError("Source file list escapes its archive root")
    return metadata


def copy_dependencies(payload, mingw):
    """Copy only imported MinGW runtime libraries, following their imports too."""
    pending = list(payload.rglob("*.dll")) + [payload / "retroarch.exe"]
    visited = set()
    added = []
    while pending:
        binary = pending.pop()
        if binary.name.lower() in visited:
            continue
        visited.add(binary.name.lower())
        result = run(mingw / "bin/objdump.exe", "-p", binary,
                     capture_output=True, text=True)
        for name in re.findall(r"DLL Name:\s*(\S+)", result.stdout):
            dependency = mingw / "bin" / name
            target = payload / name
            if dependency.is_file() and not target.exists():
                copy(dependency, target)
                pending.append(target)
                added.append(name)
    return sorted(added)


def source_zip(output, frontend_source, core_source):
    archive = output / f"{STEM}-Sources.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, source in (("RetroArch", frontend_source), ("beetle-psx", core_source)):
            metadata = provenance(source)
            tracked = set(metadata["files"])
            if name == "RetroArch":
                tracked.update(str(p.relative_to(source)).replace("\\", "/")
                               for p in (source / "pkg/windows-accessibility").rglob("*")
                               if p.is_file() and "__pycache__" not in p.parts)
            for relative in sorted(tracked):
                file = source / relative
                if file.is_file():
                    bundle.write(file, f"{name}/{relative}")
            metadata["files"] = sorted(p for p in tracked if (source / p).is_file())
            bundle.writestr(f"{name}/.accessibility-source.json", json.dumps(metadata, indent=2))
        bundle.write(output / "BUILD-SOURCES.txt", "BUILD-SOURCES.txt")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distribution", type=Path, required=True,
                        help="Extracted, clean official RetroArch distribution")
    parser.add_argument("--core-binaries", type=Path, required=True)
    parser.add_argument("--core-source", type=Path, required=True)
    parser.add_argument("--mingw", type=Path, required=True)
    parser.add_argument("--nsis", type=Path, required=True)
    parser.add_argument("--nvda-license", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True,
                        help="New empty build directory; never recursively deleted")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2]
    package = Path(__file__).resolve().parent
    work, output = args.work.resolve(), args.output.resolve()
    work.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=True)
    payload = work / "payload"
    payload.mkdir()
    for name in RESOURCE_DIRS:
        shutil.copytree(args.distribution / name, payload / name)
    copy(source / "retroarch.exe", payload / "retroarch.exe")
    copy(args.distribution / "nvdaControllerClient64.dll", payload / "nvdaControllerClient64.dll")
    for name in CORE_NAMES:
        copy(args.core_binaries / (name + ".dll"), payload / "cores" / (name + ".dll"))
        (payload / "cores" / (name + ".lck")).touch()
        info = payload / "info" / (name + ".info")
        text = info.read_text(encoding="utf-8")
        label = "Beetle PSX HW" if "_hw_" in name else "Beetle PSX"
        text, count = re.subn(r'^display_name\s*=.*$',
                             f'display_name = "Sony - PlayStation ({label} - DW2 Accessibility)"',
                             text, count=1, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f"Missing core display name: {info}")
        info.write_text(text, encoding="utf-8")
    libraries = copy_dependencies(payload, args.mingw)
    copy(package / "retroarch.cfg", payload / "retroarch.accessibility-default.cfg")
    copy(package / "README.txt", payload / "README-Accessibility.txt")
    copy(source / "COPYING", payload / "licenses/RetroArch-GPL-3.txt")
    copy(args.core_source / "COPYING", payload / "licenses/Beetle-PSX-GPL-2.txt")
    copy(args.nvda_license, payload / "licenses/NVDA-Controller-LGPL-2.1.txt")
    for name in ("gcc-libs", "libwinpthread", "winpthreads", "zlib"):
        location = args.mingw / "share/licenses" / name
        if location.exists():
            shutil.copytree(location, payload / "licenses" / name)
    frontend_commit = provenance(source)["commit"]
    core_commit = provenance(args.core_source)["commit"]
    build_sources = f"""Build sources for RetroArch Accessibility {VERSION}

Frontend source: {frontend_commit}
Core source: {core_commit}
Speech command in both: 95 | RETRO_ENVIRONMENT_EXPERIMENTAL.
The Sources.zip includes the current packaging scripts as well as these sources.

Frontend: run pkg/windows-accessibility/build-runtime.ps1 in Windows PowerShell.
Requires MSYS2 MinGW-w64 GCC, GNU make and zlib, installed in C:\\msys64 by default.
Core: follow beetle-psx/ACCESSIBILITY.md. Generate the fallback message table
from your own USA game, then make -j8 platform=windows_x64 HAVE_HW=0. Preserve
the resulting DLL, run make clean, then make -j8 platform=windows_x64 HAVE_HW=1.
The generated game dialogue is not included in the source archive.

Installer: Python 3.11+ and NSIS 3.12 (Git is needed only for a Git checkout).
The extracted source archive contains its own commit and file-list metadata.
Run build.py --help in
RetroArch/pkg/windows-accessibility for its explicit input paths. Use the clean
official RetroArch 1.22.2 Windows x64 archive for supporting resources:
https://buildbot.libretro.com/stable/1.22.2/windows/x86_64/RetroArch.7z
The original archive's executables and personal installation data are not staged.

Dependencies included as separately replaceable DLLs: {', '.join(libraries)}
MSYS2 source packaging/build recipes:
https://github.com/msys2/MINGW-packages
GCC and runtime source: https://gcc.gnu.org/releases.html
MinGW-w64 runtime source: https://www.mingw-w64.org/downloads/
zlib source: https://zlib.net/
NVDA Controller Client source and build instructions:
https://github.com/nvaccess/nvda/tree/master/extras/controllerClient
NVDA Controller Client license is included in licenses.
NSIS source: https://nsis.sourceforge.io/Download
Libretro resources: https://github.com/libretro/retroarch-assets
https://github.com/libretro/retroarch-joypad-autoconfig
https://github.com/libretro/libretro-database
https://github.com/libretro/libretro-core-info
https://github.com/libretro/common-overlays
https://github.com/libretro/glsl-shaders
https://github.com/libretro/slang-shaders

This community build is unsigned. The installer download URL is kept stable:
https://github.com/buu420/RetroArch/releases/download/accessibility-2026.09.21/RetroArch-Accessibility-2026.09.21-Win64-Setup.exe
See the release notes and package-manifest.json for the current build revision.
"""
    (output / "BUILD-SOURCES.txt").write_text(build_sources, encoding="utf-8")
    copy(output / "BUILD-SOURCES.txt", payload / "BUILD-SOURCES.txt")
    files = sorted(p for p in payload.rglob("*") if p.is_file())
    manifest = {"version": VERSION, "frontend_commit": frontend_commit,
                "core_commit": core_commit, "speech_command": 95,
                "files": [{"path": p.relative_to(payload).as_posix(),
                           "size": p.stat().st_size, "sha256": digest(p)} for p in files]}
    (payload / "package-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    files.append(payload / "package-manifest.json")
    install, remove = [], []
    last_dir = None
    for file in sorted(files):
        relative = str(file.relative_to(payload))
        parent = str(file.parent.relative_to(payload))
        if parent != last_dir:
            install.append('SetOutPath "$INSTDIR' + ("\\" + nsis_literal(parent) if parent != "." else "") + '"')
            last_dir = parent
        mutable = relative.startswith("autoconfig\\")
        if mutable:
            install.append("SetOverwrite off")
        # File reads its source at compile time; /oname is a runtime string.
        install.append('File "/oname=' + nsis_literal(file.name) + '" "${PAYLOAD}\\' + relative + '"')
        if mutable:
            install.append("SetOverwrite on")
        else:
            remove.extend(('ClearErrors', 'Delete "$INSTDIR\\' + nsis_literal(relative) + '"',
                           'IfErrors un_failed'))
    directories = sorted((p for p in payload.rglob("*") if p.is_dir()),
                         key=lambda p: len(p.parts), reverse=True)
    for directory in directories:
        remove.append('RMDir "$INSTDIR\\' + nsis_literal(directory.relative_to(payload)) + '"')
    install_file, remove_file = work / "install-files.nsh", work / "uninstall-files.nsh"
    install_file.write_text("\n".join(install) + "\n", encoding="utf-8-sig")
    remove_file.write_text("\n".join(remove) + "\n", encoding="utf-8-sig")
    installer = output / f"{STEM}-Setup.exe"
    installer_script = work / "RetroArchAccessibility.nsi"
    copy(package / "RetroArchAccessibility.nsi", installer_script)
    with (work / "nsis-build.log").open("w", encoding="utf-8") as log:
        run(args.nsis, "/V3", f"/DPAYLOAD={payload}", f"/DSOURCE_ROOT={source}",
            f"/DPACKAGE_VERSION={VERSION}",
            "/DPACKAGE_VERSION_NUMERIC=" + ".".join(str(int(n)) for n in VERSION.split(".")),
            f"/DINSTALL_FILES={install_file}", f"/DUNINSTALL_FILES={remove_file}",
            f"/DINSTALLER_OUT={installer}",
            f"/DMAX_INSTALL_DIR={258 - max(len(str(p.relative_to(payload))) for p in files)}",
            f"/DPAYLOAD_KB={sum(p.stat().st_size for p in files) // 1024}",
            installer_script, stdout=log, stderr=subprocess.STDOUT)
    archive = source_zip(output, source, args.core_source)
    copy(package / "README.txt", output / "README.txt")
    checksums = "".join(f"{digest(p)}  {p.name}\n" for p in
                        (installer, archive, output / "README.txt", output / "BUILD-SOURCES.txt"))
    (output / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
    print(json.dumps({"installer": str(installer), "sources": str(archive),
                      "payload_files": len(files), "bytes": installer.stat().st_size,
                      "payload": str(payload)}, indent=2))


if __name__ == "__main__":
    main()
