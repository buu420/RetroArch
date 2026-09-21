# Invoke from the RetroArch source root; see build-runtime.ps1.
include Makefile.win

# Makefile.win does not consume configure's include paths or SAPI define.
DEFINES += -DHAVE_SAPI -DHAVE_NVDA
CFLAGS += $(INCLUDE_DIRS)
CXXFLAGS += $(INCLUDE_DIRS) -std=c++11
LIBS := $(filter-out sapi.dll,$(LIBS))
LDFLAGS += -mwindows -municode

# D3D9 HLSL also needs the shared compiler object.
RARCH_OBJ += $(OBJDIR)/gfx/common/d3dcompiler_common.o
$(TARGET): $(OBJDIR)/gfx/common/d3dcompiler_common.o
RARCH_OBJ += $(OBJDIR)/pkg/windows-accessibility/entrypoint.o
$(TARGET): $(OBJDIR)/pkg/windows-accessibility/entrypoint.o

# Rebuild when packaging's compiler settings change.
$(RARCH_OBJ): pkg/windows-accessibility/frontend.mk pkg/windows-accessibility/build-runtime.ps1
