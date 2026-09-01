"""Garantía de PATH: asegura que el bin esté en el PATH de forma persistente.

Idempotente y cross-shell (zsh/bash/fish) en Unix; registro + broadcast en Windows.
Lo usa el bootstrap (garantía inicial) y `diat --check`/`--status` (auto-reparación).
"""

import os
from pathlib import Path

from . import paths
from .ui import print_warning

PATH_BLOCK = """\
# >>> diat >>>
case ":$PATH:" in
  *":{bin}:"*) ;;
  *) export PATH="{bin}:$PATH" ;;
esac
# <<< diat <<<"""


def is_bin_on_path():
    return str(paths.get_bin_path()) in os.environ.get("PATH", "").split(os.pathsep)


def _rc_targets():
    """Archivos rc a actualizar según el shell del usuario."""
    shell, home = os.environ.get("SHELL", ""), Path.home()
    targets = []
    if "zsh" in shell:
        targets.append(home / ".zshrc")
    elif "bash" in shell:
        targets += [home / ".bashrc", home / ".bash_profile"]
    elif "fish" in shell:
        targets.append(home / ".config" / "fish" / "config.fish")
    targets.append(home / ".profile")               # red de seguridad login shells POSIX
    return targets


def _ensure_path_unix(bin_dir):
    block = PATH_BLOCK.format(bin=bin_dir)
    changed = False
    for rc in _rc_targets():
        content = rc.read_text(encoding="utf-8") if rc.exists() else ""
        if "# >>> diat >>>" in content:
            continue                                # ya está — idempotente
        if "fish" in rc.name:
            rc.parent.mkdir(parents=True, exist_ok=True)
            rc.write_text(content + f"\n# diat\nfish_add_path {bin_dir}\n", encoding="utf-8")
        else:
            rc.write_text(content.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
        changed = True
    return changed


def _ensure_path_windows(bin_dir):
    import winreg
    import ctypes
    bin_str = str(bin_dir)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                         winreg.KEY_READ | winreg.KEY_WRITE)
    try:
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current = ""
        parts = [p for p in current.split(";") if p]
        if bin_str.lower() in (p.lower() for p in parts):
            return False                            # ya está
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                          ";".join(parts + [bin_str]))
    finally:
        winreg.CloseKey(key)
    HWND_BROADCAST, WM_SETTINGCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x1A, 0x2
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
        SMTO_ABORTIFHUNG, 5000, None)               # avisa a procesos nuevos
    return True


def ensure_bin_on_path():
    """Garantiza que el bin esté en PATH de forma persistente. Idempotente.
    Devuelve True si tuvo que cambiar algo."""
    bin_dir = paths.get_bin_path()
    bin_dir.mkdir(parents=True, exist_ok=True)

    already = is_bin_on_path()
    changed = (_ensure_path_windows(bin_dir) if os.name == "nt"
               else _ensure_path_unix(bin_dir))

    if not already:                                 # que funcione YA en este proceso
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"

    if changed and not already:
        print_warning("PATH actualizado. Reinicia la terminal o ejecuta:")
        print("     source ~/.zshrc   (o ~/.bashrc / ~/.profile)" if os.name != "nt"
              else "     Abre una terminal nueva para que tome efecto.")
    return changed
