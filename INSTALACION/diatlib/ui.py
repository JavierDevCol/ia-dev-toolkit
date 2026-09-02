"""Salida por consola: colores, mensajes y banner. Sin dependencias externas."""

import os
import sys

# ============================================================
# COLORES ANSI
# ============================================================
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
WHITE = "\033[1;37m"
DIM = "\033[2m"
NC = "\033[0m"


def enable_ansi_windows():
    """Activa el procesamiento de secuencias ANSI en cmd/PowerShell. No-op en Unix."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # VT_PROCESSING
    except Exception:
        pass


# ============================================================
# MENSAJES
# ============================================================
def print_info(msg):
    print(f"  {CYAN}ℹ️  {msg}{NC}")


def print_success(msg):
    print(f"  {GREEN}✅ {msg}{NC}")


def print_warning(msg):
    print(f"  {YELLOW}⚠️  {msg}{NC}")


def print_error(msg):
    print(f"  {RED}❌ {msg}{NC}")


# ============================================================
# BANNER
# ============================================================
_BANNER_ART = [
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢠⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠋⠀⡀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⣼⣷⠀⠀⠙⠒⠚⠛⠛⠛⠛⠛⠓⠒⠒⠦⠚⠀⢀⣴⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠃⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⣀⡠⠤⢴⡷⠤⢤⡤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⢠⢾⣅⠙⢦⡀⠙⢦⡀⠙⢦⡈⠻⣕⢦⡀⠀⠀⠀⠀⠀⠀⣠⠴⢶⡋⠙⠫⣍⠙⢯⡉⠙⢯⡲⣄⠀⠀⠀⠀",
    "⠀⠀⠀⢸⡄⠙⢷⡀⠙⢦⡀⠙⢦⡀⠙⢦⡘⢧⣷⠚⠉⠉⠛⠒⣾⠉⠳⡄⠙⢦⡀⠈⠳⣄⠉⠢⣄⠙⢾⡄⠀⠀⠀",
    "⠀⠀⠀⠸⡝⢧⡀⠙⢦⡀⠙⢦⡀⠙⢦⡀⠙⢦⡝⠀⣠⣤⣤⠀⢹⠳⣄⠙⢦⡀⠉⠳⣄⠈⠑⢄⠈⠳⣼⠁⠀⠀⠀",
    "⠁⠒⠒⠦⠽⣄⠙⢦⡀⠙⢦⡀⠙⢷⣄⠙⣦⠞⠁⠀⠈⢻⠋⠀⠀⢣⡈⠳⣄⠙⢦⡀⠈⠳⣄⠀⠙⣶⣃⣀⣀⣀⣄",
    "⣀⣀⣀⣀⣀⣀⣻⡶⣿⣦⣤⣿⣦⣤⠿⠟⠃⠀⠀⠀⠀⢸⠀⠀⠀⠀⠻⢦⣜⣷⣄⣻⣦⣀⣸⣷⠟⠃⠀⠀⠀⠀⠀",
    "⠉⠉⠉⠉⠉⠉⢹⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣘⠀⠀⠀⠀⠀⠀⠈⠉⠙⠛⠛⠉⠩⢼⠒⠒⠲⠤⠤⠤⠀",
    "⠀⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠙⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠢⠤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡤⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
]


def print_banner():
    indent = " " * 15                      # centra el arte (ancho 43) bajo título/recuadro
    print()
    for line in _BANNER_ART:
        print(f"{CYAN}{indent}{line}{NC}")
    print()
    print(f"{CYAN}                         AI DEVELOPER TOOLKIT{NC}")
    print()
    print(f"{CYAN}        ┌─────────────────────────────────────────────────────────┐{NC}")
    print(f"{CYAN}        │  Skills · Agents · Workflows · Tools · Commands         │{NC}")
    print(f"{CYAN}        └─────────────────────────────────────────────────────────┘{NC}")
    print()
