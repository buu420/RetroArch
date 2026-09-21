/* Copyright 2026 buu420. SPDX-License-Identifier: GPL-3.0-or-later */
#include <windows.h>
#include <shellapi.h>
#include <stdlib.h>

int main(int argc, char *argv[]);

/* RetroArch's file APIs consume UTF-8; the Windows CRT's __argv uses ACP. */
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous,
      LPWSTR command_line, int show)
{
   int argc = 0;
   int i;
   int result = EXIT_FAILURE;
   LPWSTR *wide = CommandLineToArgvW(GetCommandLineW(), &argc);
   char **args;
   (void)instance;
   (void)previous;
   (void)command_line;
   (void)show;
   if (!wide)
      return EXIT_FAILURE;
   args = (char**)calloc((size_t)argc + 1, sizeof(*args));
   if (!args)
   {
      LocalFree(wide);
      return EXIT_FAILURE;
   }
   for (i = 0; i < argc; i++)
   {
      int size = WideCharToMultiByte(CP_UTF8, 0, wide[i], -1,
            NULL, 0, NULL, NULL);
      if (!size)
         goto done;
      args[i] = (char*)malloc(size);
      if (!args[i] || !WideCharToMultiByte(CP_UTF8, 0, wide[i], -1,
               args[i], size, NULL, NULL))
         goto done;
   }
   result = main(argc, args);
done:
   for (i = 0; i < argc; i++)
      free(args[i]);
   free(args);
   LocalFree(wide);
   return result;
}
