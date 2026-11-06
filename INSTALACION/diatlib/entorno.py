"""Garantía de PATH: asegura que el bin esté en el PATH de forma persistente.

Idempotente y cross-shell (zsh/bash/fish) en Unix; registro + broadcast en Windows.
Lo usa el bootstrap (garantía inicial) y `diat --check`/`--status` (auto-reparación).
También ofrece crear PAT_AZURE (PAT de Azure DevOps) para las skills que lo usan.
"""

import getpass
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
    _broadcast_env_change()
    return True


def _broadcast_env_change():
    import ctypes
    HWND_BROADCAST, WM_SETTINGCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x1A, 0x2
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
        SMTO_ABORTIFHUNG, 5000, None)               # avisa a procesos nuevos


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


def remove_bin_from_path():
    """Quita el bin del PATH (inversa de ensure_bin_on_path)."""
    bin_dir = paths.get_bin_path()
    if os.name == "nt":
        _remove_path_windows(bin_dir)
    else:
        _remove_path_unix(bin_dir)


def _remove_path_unix(bin_dir):
    for rc in _rc_targets():
        if not rc.exists():
            continue
        content = rc.read_text(encoding="utf-8")
        if "# >>> diat >>>" not in content and "fish_add_path" not in content:
            continue
        out, skip = [], False
        for ln in content.splitlines():
            if ln.strip() == "# >>> diat >>>":
                skip = True
                continue
            if ln.strip() == "# <<< diat <<<":
                skip = False
                continue
            if skip:
                continue
            if ln.strip() == "# diat":
                continue
            if "fish_add_path" in ln and str(bin_dir) in ln:
                continue
            out.append(ln)
        rc.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def _remove_path_windows(bin_dir):
    import winreg
    bin_str = str(bin_dir)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                         winreg.KEY_READ | winreg.KEY_WRITE)
    try:
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            return
        parts = [p for p in current.split(";") if p and p.lower() != bin_str.lower()]
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
    finally:
        winreg.CloseKey(key)


# ============================================================
# PAT_AZURE
# ============================================================
PAT_VAR = "PAT_AZURE"
PAT_SKILLS = {"ado-variable-groups", "ado-variable-groups-write", "ado-wi-query",
              "entrega-ambiente-banco-opcion3"}
PAT_BEGIN, PAT_END = "# >>> diat PAT_AZURE >>>", "# <<< diat PAT_AZURE <<<"


def has_pat():
    return bool(os.environ.get(PAT_VAR))


def _write_pat_unix(pat):
    """Escribe (o reemplaza) el bloque PAT_AZURE en los rc del usuario y los deja en 600."""
    for rc in _rc_targets():
        content = rc.read_text(encoding="utf-8") if rc.exists() else ""
        out, skip = [], False
        for ln in content.splitlines():             # quita un bloque previo
            if ln.strip() == PAT_BEGIN:
                skip = True
            elif ln.strip() == PAT_END:
                skip = False
            elif not skip:
                out.append(ln)
        line = (f"set -gx {PAT_VAR} '{pat}'" if rc.name == "config.fish"
                else f"export {PAT_VAR}='{pat}'")
        rc.parent.mkdir(parents=True, exist_ok=True)
        rc.write_text("\n".join(out).rstrip() + f"\n\n{PAT_BEGIN}\n{line}\n{PAT_END}\n",
                      encoding="utf-8")
        rc.chmod(0o600)                             # el PAT queda en texto plano


def _write_pat_windows(pat):
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE)
    try:
        winreg.SetValueEx(key, PAT_VAR, 0, winreg.REG_SZ, pat)
    finally:
        winreg.CloseKey(key)
    _broadcast_env_change()


def ensure_pat(installed_skills, interactive=True):
    """Si alguna skill instalada usa PAT_AZURE y no existe, la pide y la persiste.
    Sin PAT (vacío o no interactivo) se continúa avisando. Nunca imprime el PAT."""
    needed = sorted(PAT_SKILLS & set(installed_skills))
    if not needed or has_pat():
        return
    pat = ""
    if interactive:
        print(f"\n  🔑 {PAT_VAR} no existe. La usan: {', '.join(needed)}")
        pat = getpass.getpass("     PAT de Azure DevOps (Enter para omitir): ").strip()
    if pat and ("'" in pat or any(c.isspace() for c in pat)):
        print_warning("PAT con caracteres inválidos; no se guardó.")
        pat = ""
    if not pat:
        print_warning(f"Falta {PAT_VAR}: estas skills no funcionarán bien hasta crearla: "
                      f"{', '.join(needed)}")
        print(f"     Créala con: export {PAT_VAR}='<tu PAT>' en tu perfil del shell"
              if os.name != "nt" else f"     Créala con: setx {PAT_VAR} \"<tu PAT>\"")
        return
    _write_pat_windows(pat) if os.name == "nt" else _write_pat_unix(pat)
    os.environ[PAT_VAR] = pat                       # disponible ya en este proceso
    print_warning(f"{PAT_VAR} guardada. Reinicia la terminal y Claude Code/OpenCode para que la tomen.")
