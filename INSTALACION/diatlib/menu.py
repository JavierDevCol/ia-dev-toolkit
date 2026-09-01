"""Motor de menú interactivo, stdlib puro (Linux, macOS, Windows nativo).

Abstrae la lectura de teclado (termios/tty en Unix, msvcrt en Windows), habilita
ANSI en Windows, redibuja en el sitio y cae a menú numérico si no hay TTY.
"""

import os
import sys

from .ui import CYAN, WHITE, DIM, NC, enable_ansi_windows

# Constantes de tecla
UP, DOWN, SPACE, ENTER, QUIT, CHAR, OTHER = (
    "UP", "DOWN", "SPACE", "ENTER", "QUIT", "CHAR", "OTHER")

HIDE, SHOW = "\033[?25l", "\033[?25h"


# ============================================================
# LECTURA DE TECLAS  (por plataforma)
# ============================================================
if os.name == "nt":
    import msvcrt

    class raw_mode:
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def read_key():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):                # prefijo de tecla especial
            return {"H": UP, "P": DOWN}.get(msvcrt.getwch(), OTHER)
        if ch == " ":              return SPACE
        if ch in ("\r", "\n"):     return ENTER
        if ch in ("\x03", "\x1b"): return QUIT
        if ch.lower() == "q":      return QUIT
        return (CHAR, ch.lower())

else:
    import termios
    import tty

    class raw_mode:
        def __enter__(self):
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            return self
        def __exit__(self, *a):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def read_key():
        ch = sys.stdin.read(1)
        if ch == "\x1b":                          # ESC: ¿solo ESC o flecha?
            seq = sys.stdin.read(2)
            if seq in ("[A", "OA"): return UP
            if seq in ("[B", "OB"): return DOWN
            return QUIT
        if ch == " ":            return SPACE
        if ch in ("\r", "\n"):   return ENTER
        if ch == "\x03":         return QUIT
        if ch.lower() == "q":    return QUIT
        return (CHAR, ch.lower())


# ============================================================
# REDIBUJADO EN EL SITIO
# ============================================================
def _draw(lines, prev_count):
    if prev_count:
        sys.stdout.write(f"\033[{prev_count}A")
    for ln in lines:
        sys.stdout.write("\033[2K" + ln + "\n")
    sys.stdout.flush()
    return len(lines)


# ============================================================
# MULTISELECCIÓN  (submenús)
# ============================================================
def multiselect(title, options, preselected=None):
    """options: [(value, label, description), ...] -> set de values o None.
    ↑↓ mover · ESPACIO toggle · T todas · N ninguna · V volver · Q salir."""
    if not sys.stdin.isatty():
        return _numeric_fallback(title, options, preselected)

    enable_ansi_windows()
    selected = set(preselected or [])
    cursor, prev = 0, 0

    def frame():
        out = ["", f"{CYAN}{'═'*70}{NC}", f"  📦 {title}", f"{CYAN}{'═'*70}{NC}"]
        for i, (val, label, desc) in enumerate(options):
            mark = "[X]" if val in selected else "[ ]"
            if i == cursor:
                out.append(f"{WHITE}❯ {mark}  {label:<32}{NC} — {desc}")
            else:
                out.append(f"  {mark}  {label:<32} {DIM}— {desc}{NC}")
        out.append(f"{CYAN}{'─'*70}{NC}")
        out.append("  [ESPACIO] toggle · ↑↓ mover · [T] todas · [N] ninguna · [V] volver")
        return out

    sys.stdout.write(HIDE)
    try:
        with raw_mode():
            while True:
                prev = _draw(frame(), prev)
                k = read_key()
                if k == UP:
                    cursor = (cursor - 1) % len(options)
                elif k == DOWN:
                    cursor = (cursor + 1) % len(options)
                elif k == SPACE:
                    v = options[cursor][0]
                    selected.discard(v) if v in selected else selected.add(v)
                elif k == ENTER:
                    return selected
                elif k == (CHAR, "t"):
                    selected = {o[0] for o in options}
                elif k == (CHAR, "n"):
                    selected = set()
                elif k == QUIT or k == (CHAR, "v"):
                    return None
    finally:
        sys.stdout.write(SHOW)
        sys.stdout.flush()


# ============================================================
# MENÚ PRINCIPAL  (una acción; ESPACIO abre submenú)
# ============================================================
def menu_select(title, options):
    """options: [(value, label, description), ...] -> value elegido o None (Q/ESC)."""
    if not sys.stdin.isatty():
        return _numeric_fallback_single(title, options)

    enable_ansi_windows()
    cursor, prev = 0, 0

    def frame():
        out = ["", f"{CYAN}{'═'*60}{NC}", f"  {title}", f"{CYAN}{'═'*60}{NC}", ""]
        for i, (val, label, desc) in enumerate(options):
            if i == cursor:
                out.append(f"{WHITE}❯ {label:<20}{NC} — {desc}")
            else:
                out.append(f"  {label:<20} {DIM}— {desc}{NC}")
        out.append(f"{CYAN}{'─'*60}{NC}")
        out.append("  ↑↓ mover · [ESPACIO] seleccionar · [Q] salir")
        return out

    sys.stdout.write(HIDE)
    try:
        with raw_mode():
            while True:
                prev = _draw(frame(), prev)
                k = read_key()
                if k == UP:
                    cursor = (cursor - 1) % len(options)
                elif k == DOWN:
                    cursor = (cursor + 1) % len(options)
                elif k in (SPACE, ENTER):
                    return options[cursor][0]
                elif k == QUIT:
                    return None
    finally:
        sys.stdout.write(SHOW)
        sys.stdout.flush()


# ============================================================
# FALLBACKS  (sin TTY: pipes, CI)
# ============================================================
def _numeric_fallback(title, options, preselected=None):
    print(f"\n  {title}")
    for i, (_, label, desc) in enumerate(options, 1):
        print(f"   {i}. {label} — {desc}")
    raw = input("  Números separados por coma (vacío = ninguno): ").strip()
    if not raw:
        return set(preselected or [])
    idx = {int(x) for x in raw.replace(" ", "").split(",") if x.isdigit()}
    return {options[i-1][0] for i in idx if 1 <= i <= len(options)}


def _numeric_fallback_single(title, options):
    print(f"\n  {title}")
    for i, (_, label, desc) in enumerate(options, 1):
        print(f"   {i}. {label} — {desc}")
    raw = input("  Selección (número, vacío = salir): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw)-1][0]
    return None
