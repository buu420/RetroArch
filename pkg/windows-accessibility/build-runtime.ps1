param(
    [string]$Msys = 'C:\msys64',
    [int]$Jobs = 8
)
$ErrorActionPreference = 'Stop'
$runtimeSource = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$env:PATH = "$Msys\mingw64\bin;$Msys\usr\bin;" + $env:PATH
Push-Location $runtimeSource
try {
    & "$Msys\usr\bin\make.exe" -f pkg/windows-accessibility/frontend.mk "-j$Jobs" `
        HAVE_ACCESSIBILITY=1 HAVE_SAPI=1 HAVE_CG=0 HAVE_FREETYPE=0 `
        HAVE_OZONE=1 HAVE_OPENGL_CORE=1 HAVE_GLSL=1 HAVE_SLANG=1 `
        HAVE_BUILTINGLSLANG=1 HAVE_SPIRV_CROSS=1 HAVE_BUILTINSPIRV_CROSS=1 `
        HAVE_ZLIB=1 ZLIB_LIBS=-lz HAVE_LIBRETRODB=1 `
        DEF_FLAGS=-isystemgfx/include/dxsdk OBJDIR=obj-accessibility-installer
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed: $LASTEXITCODE" }
} finally {
    Pop-Location
}
