#!/usr/bin/env python3
"""Run the packaged frontend with a test core and an isolated recording NVDA DLL."""
# Copyright 2026 buu420. SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import os
import shutil
import subprocess
from pathlib import Path

NVDA = r'''
#include <windows.h>
#include <stdio.h>
__declspec(dllexport) unsigned long __stdcall nvdaController_testIfRunning(void) { return 0; }
__declspec(dllexport) unsigned long __stdcall nvdaController_cancelSpeech(void) { return 0; }
__declspec(dllexport) unsigned long __stdcall nvdaController_speakText(const wchar_t *text)
{
   char buffer[4096];
   FILE *file;
   WideCharToMultiByte(CP_UTF8, 0, text, -1, buffer, sizeof(buffer), NULL, NULL);
   file = fopen("recorded-speech.txt", "ab");
   if (!file) return 1;
   fprintf(file, "%s\n", buffer);
   fclose(file);
   return 0;
}
__declspec(dllexport) unsigned long __stdcall nvdaController_brailleMessage(const wchar_t *text)
{ return nvdaController_speakText(text); }
'''

CORE = r'''
#include "libretro.h"
#include <stdio.h>
#include <string.h>
static retro_environment_t environment;
static retro_video_refresh_t video;
static unsigned frames;
RETRO_API void retro_set_environment(retro_environment_t cb)
{ bool yes = true; environment = cb; cb(RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME, &yes); }
RETRO_API void retro_set_video_refresh(retro_video_refresh_t cb) { video = cb; }
RETRO_API void retro_set_audio_sample(retro_audio_sample_t cb) { (void)cb; }
RETRO_API void retro_set_audio_sample_batch(retro_audio_sample_batch_t cb) { (void)cb; }
RETRO_API void retro_set_input_poll(retro_input_poll_t cb) { (void)cb; }
RETRO_API void retro_set_input_state(retro_input_state_t cb) { (void)cb; }
RETRO_API void retro_init(void) {}
RETRO_API void retro_deinit(void) {}
RETRO_API unsigned retro_api_version(void) { return RETRO_API_VERSION; }
RETRO_API void retro_get_system_info(struct retro_system_info *info)
{ memset(info, 0, sizeof(*info)); info->library_name = "Speech verification"; info->library_version = "1"; info->valid_extensions = ""; }
RETRO_API void retro_get_system_av_info(struct retro_system_av_info *info)
{
   memset(info, 0, sizeof(*info));
   info->geometry.base_width = info->geometry.max_width = 32;
   info->geometry.base_height = info->geometry.max_height = 32;
   info->geometry.aspect_ratio = 1;
   info->timing.fps = 60; info->timing.sample_rate = 44100;
}
RETRO_API void retro_set_controller_port_device(unsigned port, unsigned device) { (void)port; (void)device; }
RETRO_API void retro_reset(void) {}
RETRO_API void retro_run(void)
{
   static unsigned short pixels[32 * 32];
   if (!frames++) {
      struct retro_accessibility_speech request = { "DW2 speech integration: Agumon, 42 damage.", 10, "test", 0 };
      bool accepted = environment(RETRO_ENVIRONMENT_ACCESSIBILITY_SPEAK, &request);
      FILE *file = fopen("core-request.txt", "w");
      if (file) { fprintf(file, "%u %u\n", RETRO_ENVIRONMENT_ACCESSIBILITY_SPEAK, accepted); fclose(file); }
   }
   video(pixels, 32, 32, 64);
}
RETRO_API size_t retro_serialize_size(void) { return 0; }
RETRO_API bool retro_serialize(void *data, size_t size) { (void)data; (void)size; return false; }
RETRO_API bool retro_unserialize(const void *data, size_t size) { (void)data; (void)size; return false; }
RETRO_API void retro_cheat_reset(void) {}
RETRO_API void retro_cheat_set(unsigned index, bool enabled, const char *code) { (void)index; (void)enabled; (void)code; }
RETRO_API bool retro_load_game(const struct retro_game_info *game) { (void)game; return true; }
RETRO_API bool retro_load_game_special(unsigned type, const struct retro_game_info *info, size_t count)
{ (void)type; (void)info; (void)count; return false; }
RETRO_API void retro_unload_game(void) {}
RETRO_API unsigned retro_get_region(void) { return RETRO_REGION_NTSC; }
RETRO_API void *retro_get_memory_data(unsigned id) { (void)id; return NULL; }
RETRO_API size_t retro_get_memory_size(unsigned id) { (void)id; return 0; }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--gcc", type=Path, required=True)
    args = parser.parse_args()
    assert b"nvdaControllerClient64.dll" in (args.payload / "retroarch.exe").read_bytes(), "NVDA was not compiled into the frontend"
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    for file in args.payload.iterdir():
        if file.suffix.lower() in (".exe", ".dll") and "uninstall" not in file.name.lower():
            shutil.copy2(file, work / file.name)
    (work / "nvda-recording.c").write_text(NVDA, encoding="utf-8")
    (work / "speech-core.c").write_text(CORE, encoding="utf-8")
    build_env = os.environ.copy()
    build_env["PATH"] = str(args.gcc.parent) + os.pathsep + build_env["PATH"]
    header_dir = Path(__file__).resolve().parents[2] / "libretro-common/include"
    for source, output in (("nvda-recording.c", "nvdaControllerClient64.dll"), ("speech-core.c", "speech-test-libretro.dll")):
        subprocess.run([str(args.gcc), "-shared", "-O2", "-std=c89", "-static-libgcc",
                        "-I" + str(header_dir), str(work / source), "-o", str(work / output)],
                       check=True, env=build_env, capture_output=True)
    (work / "test.cfg").write_text('''accessibility_enable = "true"
config_save_on_exit = "false"
video_driver = "null"
audio_driver = "null"
input_driver = "null"
menu_driver = "rgui"
menu_show_start_screen = "false"
pause_nonactive = "false"
menu_pause_libretro = "false"
''', encoding="utf-8")
    runtime_env = os.environ.copy()
    runtime_env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
    try:
        result = subprocess.run([str(work / "retroarch.exe"), "--config", str(work / "test.cfg"),
                                 "-L", str(work / "speech-test-libretro.dll"), "--verbose", "--max-frames", "8"],
                                cwd=work, env=runtime_env, timeout=30, capture_output=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.TimeoutExpired as error:
        (work / "frontend.log").write_bytes((error.stdout or b"") + (error.stderr or b""))
        raise
    (work / "frontend.log").write_bytes(result.stdout + result.stderr)
    assert result.returncode == 0, (result.returncode, "See frontend.log")
    assert (work / "core-request.txt").read_text().strip() == "65631 1"
    assert "DW2 speech integration: Agumon, 42 damage." in (work / "recorded-speech.txt").read_text(encoding="utf-8")
    print("PASS: real packaged frontend accepted command 95 and delivered the core's exact text to the recording NVDA client. No live NVDA instance was controlled.")


if __name__ == "__main__":
    main()
