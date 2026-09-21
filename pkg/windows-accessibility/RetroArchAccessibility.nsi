; Copyright 2026 buu420. SPDX-License-Identifier: GPL-3.0-or-later
Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"
!include "x64.nsh"

!define PRODUCT "RetroArch Accessibility"
!define REGKEY "Software\RetroArchAccessibility"
!define UNINSTALLKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\RetroArchAccessibility"
!define ID "buu420-retroarch-accessibility"

Name "${PRODUCT}"
OutFile "${INSTALLER_OUT}"
InstallDir "$LOCALAPPDATA\Programs\RetroArch Accessibility"
InstallDirRegKey HKCU "${REGKEY}" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize on
CRCCheck on
ShowInstDetails show
ShowUninstDetails show
BrandingText "Community accessibility build by buu420"
VIProductVersion "2026.9.21.0"
VIAddVersionKey /LANG=1033 "ProductName" "${PRODUCT}"
VIAddVersionKey /LANG=1033 "CompanyName" "buu420"
VIAddVersionKey /LANG=1033 "LegalCopyright" "RetroArch, Mednafen and contributors; accessibility by buu420"
VIAddVersionKey /LANG=1033 "FileDescription" "RetroArch with Digimon World 2 accessibility"
VIAddVersionKey /LANG=1033 "FileVersion" "2026.09.21"

!define MUI_ABORTWARNING
!define MUI_ICON "${SOURCE_ROOT}\media\retroarch.ico"
!define MUI_UNICON "${SOURCE_ROOT}\media\retroarch.ico"
!define MUI_WELCOMEPAGE_TEXT "Install the speech-enabled RetroArch frontend and both Digimon World 2 accessibility cores.$\r$\n$\r$\nSpeech starts enabled. Use your own game image and PlayStation BIOS.$\r$\n$\r$\nClose this accessibility build before installing an update."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${SOURCE_ROOT}\COPYING"
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE ValidateDirectory
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TEXT "Installation complete. Open RetroArch Accessibility from the Start menu. Getting Started explains game setup and navigation controls."
!insertmacro MUI_PAGE_FINISH
!define MUI_UNCONFIRMPAGE_TEXT_TOP "Remove RetroArch Accessibility? Saves, settings, games, BIOS files and other player data will be kept."
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "This package requires 64-bit Windows." /SD IDOK
    SetErrorLevel 2
    Quit
  ${EndIf}
  SetRegView 64
  SetShellVarContext current
FunctionEnd

Function ValidateDirectory
  StrLen $0 "$INSTDIR"
  ; The frontend also needs every resource to fit within MAX_PATH.
  ${If} $0 > ${MAX_INSTALL_DIR}
    Goto path_too_long
  ${EndIf}
  ${GetRoot} "$INSTDIR" $0
  ${If} "$INSTDIR" == "$0\"
    Goto invalid
  ${EndIf}
  ${If} "$INSTDIR" == "$0"
    Goto invalid
  ${EndIf}
  ReadINIStr $0 "$INSTDIR\accessibility-install.ini" "Package" "Id"
  ${If} $0 == "${ID}"
    Goto owned_directory
  ${EndIf}
  FindFirst $0 $1 "$INSTDIR\*.*"
check_empty:
  ${If} $1 == ""
    FindClose $0
    Goto directory_ok
  ${EndIf}
  ${If} $1 != "."
  ${AndIf} $1 != ".."
    FindClose $0
    Goto invalid
  ${EndIf}
  FindNext $0 $1
  Goto check_empty
owned_directory:
  IfFileExists "$INSTDIR\retroarch.exe" 0 directory_ok
  ClearErrors
  FileOpen $0 "$INSTDIR\retroarch.exe" a
  IfErrors in_use
  FileClose $0
directory_ok:
  Return
invalid:
  MessageBox MB_ICONSTOP "Choose a separate empty folder, or this package's existing folder. Setup will not overwrite another installation or install into a drive root." /SD IDOK
  SetErrorLevel 2
  Abort
in_use:
  MessageBox MB_ICONSTOP "Close RetroArch Accessibility and check that this folder is writable, then run setup again." /SD IDOK
  SetErrorLevel 2
  Abort
path_too_long:
  MessageBox MB_ICONSTOP "Choose a shorter destination folder so all RetroArch resources fit within Windows path limits." /SD IDOK
  SetErrorLevel 2
  Abort
FunctionEnd

Section "RetroArch and Digimon World 2 cores"
  Call ValidateDirectory
  ClearErrors
  SetOutPath "$INSTDIR"
  WriteINIStr "$INSTDIR\accessibility-install.ini" "Package" "Id" "${ID}"
  WriteUninstaller "$INSTDIR\Uninstall-Accessibility.exe"
  IfErrors install_failed
  SetOverwrite on
  !include "${INSTALL_FILES}"
  IfErrors install_failed
  SetOverwrite off
  SetOutPath "$INSTDIR"
  File /oname=retroarch.cfg "${PAYLOAD}\retroarch.accessibility-default.cfg"
  SetOverwrite on
  CreateDirectory "$INSTDIR\saves"
  CreateDirectory "$INSTDIR\states"
  CreateDirectory "$INSTDIR\system"
  CreateDirectory "$INSTDIR\config"
  CreateDirectory "$INSTDIR\screenshots"
  CreateDirectory "$INSTDIR\playlists"
  CreateDirectory "$INSTDIR\downloads"
  CreateDirectory "$INSTDIR\logs"
  WriteINIStr "$INSTDIR\accessibility-install.ini" "Package" "Version" "2026.09.21"
  WriteUninstaller "$INSTDIR\Uninstall-Accessibility.exe"
  IfErrors install_failed
  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\${PRODUCT}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk" "$INSTDIR\retroarch.exe" '--config "$INSTDIR\retroarch.cfg"'
  CreateShortCut "$SMPROGRAMS\${PRODUCT}\Getting Started.lnk" "$INSTDIR\README-Accessibility.txt"
  CreateShortCut "$SMPROGRAMS\${PRODUCT}\Data Folder.lnk" "$INSTDIR"
  CreateShortCut "$SMPROGRAMS\${PRODUCT}\Uninstall.lnk" "$INSTDIR\Uninstall-Accessibility.exe"
  WriteRegStr HKCU "${REGKEY}" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayName" "${PRODUCT} with Digimon World 2"
  WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayVersion" "2026.09.21"
  WriteRegStr HKCU "${UNINSTALLKEY}" "Publisher" "buu420 / Libretro contributors"
  WriteRegStr HKCU "${UNINSTALLKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayIcon" "$INSTDIR\retroarch.exe"
  WriteRegStr HKCU "${UNINSTALLKEY}" "UninstallString" '$\"$INSTDIR\Uninstall-Accessibility.exe$\"'
  WriteRegStr HKCU "${UNINSTALLKEY}" "QuietUninstallString" '$\"$INSTDIR\Uninstall-Accessibility.exe$\" /S'
  WriteRegDWORD HKCU "${UNINSTALLKEY}" "EstimatedSize" ${PAYLOAD_KB}
  WriteRegDWORD HKCU "${UNINSTALLKEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINSTALLKEY}" "NoRepair" 1
  IfErrors install_failed
  SetErrorLevel 0
  Goto install_done
install_failed:
  MessageBox MB_ICONSTOP "Installation could not finish. Check free space, folder permissions and whether RetroArch is running, then retry." /SD IDOK
  SetErrorLevel 2
  Abort
install_done:
SectionEnd

Function un.onInit
  SetRegView 64
  SetShellVarContext current
  ReadINIStr $0 "$INSTDIR\accessibility-install.ini" "Package" "Id"
  ${If} $0 != "${ID}"
    MessageBox MB_ICONSTOP "This folder is not a RetroArch Accessibility installation." /SD IDOK
    SetErrorLevel 2
    Quit
  ${EndIf}
  IfFileExists "$INSTDIR\retroarch.exe" 0 un_init_done
  ClearErrors
  FileOpen $0 "$INSTDIR\retroarch.exe" a
  IfErrors 0 +4
    MessageBox MB_ICONSTOP "Close RetroArch Accessibility before uninstalling." /SD IDOK
    SetErrorLevel 2
    Quit
  FileClose $0
un_init_done:
FunctionEnd

Section "Uninstall"
  ; Only remove files explicitly shipped in this build. Never recursively delete.
  !include "${UNINSTALL_FILES}"
  Delete "$INSTDIR\Uninstall-Accessibility.exe"
  ; Retain ownership with player data so reinstalls can reuse this folder.
  ReadRegStr $0 HKCU "${REGKEY}" "InstallDir"
  ${If} $0 == "$INSTDIR"
    Delete "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT}\Getting Started.lnk"
    Delete "$SMPROGRAMS\${PRODUCT}\Data Folder.lnk"
    Delete "$SMPROGRAMS\${PRODUCT}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${PRODUCT}"
    DeleteRegKey HKCU "${UNINSTALLKEY}"
    DeleteRegKey HKCU "${REGKEY}"
  ${EndIf}
  RMDir "$INSTDIR"
  SetErrorLevel 0
  Goto un_done
un_failed:
  MessageBox MB_ICONSTOP "Some program files could not be removed. Close RetroArch, check folder permissions and run this uninstaller again. Player data has been kept." /SD IDOK
  SetErrorLevel 2
  Abort
un_done:
SectionEnd
