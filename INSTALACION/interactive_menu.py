#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menú interactivo con flechas y espacio usando curses nativo.
No requiere dependencias externas.
"""

import curses
import sys


class InteractiveMenu:
    """Menú interactivo con navegación por flechas y selección con espacio."""

    def __init__(self, options, title="", multi_select=True, show_help=True):
        """
        Args:
            options: Lista de diccionarios con 'name', 'description', 'dependencies'
            title: Título del menú
            multi_select: Permitir selección múltiple
            show_help: Mostrar ayuda de controles
        """
        self.options = options
        self.title = title
        self.multi_select = multi_select
        self.show_help = show_help
        self.selected = set()
        self.current_idx = 0
        self.scroll_offset = 0

    def _get_display_lines(self, max_width):
        """Generar líneas de visualización."""
        lines = []

        # Título
        if self.title:
            lines.append(("title", self.title))
            lines.append(("separator", "═" * min(max_width - 4, 70)))

        # Opciones
        for i, opt in enumerate(self.options):
            check = "x" if i in self.selected else " "
            name = opt.get("name", f"Opción {i+1}")
            desc = opt.get("description", "")
            deps = opt.get("dependencies", "")

            # Construir línea
            line = f"  [{check}] {name}"
            if desc:
                line += f" — {desc}"
            if deps and deps != "ninguna":
                line += f" | deps: {deps}"

            lines.append(("option", line, i))

        # Ayuda
        if self.show_help:
            lines.append(("separator", "─" * min(max_width - 4, 70)))
            if self.multi_select:
                lines.append(("help", "  ↑↓: Navegar | Espacio: Seleccionar | Enter: Confirmar | q: Salir"))
            else:
                lines.append(("help", "  ↑↓: Navegar | Enter: Seleccionar | q: Salir"))

        return lines

    def run(self):
        """Ejecutar el menú interactivo y retornar índices seleccionados."""
        try:
            return curses.wrapper(self._run_curses)
        except Exception:
            # Fallback a modo texto si curses falla
            return self._run_fallback()

    def _run_curses(self, stdscr):
        """Ejecutar menú con curses."""
        curses.curs_set(0)  # Ocultar cursor
        stdscr.keypad(True)

        # Configurar colores
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Título
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Seleccionado
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Ayuda
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal

        while True:
            stdscr.clear()
            max_y, max_x = stdscr.getmaxyx()
            max_width = max_x

            lines = self._get_display_lines(max_width)

            # Calcular ventana visible
            visible_height = max_y - 2  # Dejar espacio para status
            if self.current_idx >= self.scroll_offset + visible_height:
                self.scroll_offset = self.current_idx - visible_height + 1
            elif self.current_idx < self.scroll_offset:
                self.scroll_offset = self.current_idx

            # Dibujar líneas
            y = 0
            for i, line_data in enumerate(lines):
                if y >= max_y - 1:
                    break

                line_type = line_data[0]

                if line_type == "title":
                    try:
                        stdscr.addstr(y, 0, line_data[1][:max_width-1], curses.color_pair(1) | curses.A_BOLD)
                    except curses.error:
                        pass
                    y += 1

                elif line_type == "separator":
                    try:
                        stdscr.addstr(y, 0, line_data[1][:max_width-1], curses.color_pair(4))
                    except curses.error:
                        pass
                    y += 1

                elif line_type == "option":
                    opt_idx = line_data[2]
                    text = line_data[1][:max_width-1]

                    # Determinar si está visible en scroll
                    if opt_idx < self.scroll_offset or opt_idx >= self.scroll_offset + visible_height:
                        continue

                    # Determinar estilo
                    if opt_idx == self.current_idx:
                        attr = curses.color_pair(2) | curses.A_BOLD
                        text = "→" + text[1:]  # Reemplazar espacio con flecha
                    elif opt_idx in self.selected:
                        attr = curses.color_pair(2)
                    else:
                        attr = curses.color_pair(4)

                    try:
                        stdscr.addstr(y, 0, text, attr)
                    except curses.error:
                        pass
                    y += 1

                elif line_type == "help":
                    try:
                        stdscr.addstr(y, 0, line_data[1][:max_width-1], curses.color_pair(3))
                    except curses.error:
                        pass
                    y += 1

            # Status bar
            status = f"  [{len(self.selected)} seleccionados]"
            try:
                stdscr.addstr(max_y-1, 0, status[:max_width-1], curses.color_pair(3))
            except curses.error:
                pass

            stdscr.refresh()

            # Capturar tecla
            key = stdscr.getch()

            if key == curses.KEY_UP:
                self.current_idx = max(0, self.current_idx - 1)
            elif key == curses.KEY_DOWN:
                self.current_idx = min(len(self.options) - 1, self.current_idx + 1)
            elif key == ord(' '):  # Espacio
                if self.multi_select:
                    if self.current_idx in self.selected:
                        self.selected.remove(self.current_idx)
                    else:
                        self.selected.add(self.current_idx)
                else:
                    return [self.current_idx]
            elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter
                if self.multi_select:
                    return sorted(list(self.selected))
                else:
                    return [self.current_idx]
            elif key == ord('q') or key == ord('Q') or key == 27:  # q o Escape
                return None
            elif key == ord('a') or key == ord('A'):  # Seleccionar todos
                if self.multi_select:
                    self.selected = set(range(len(self.options)))
            elif key == ord('n') or key == ord('N'):  # Deseleccionar todos
                self.selected.clear()

    def _run_fallback(self):
        """Fallback a modo texto si curses no funciona."""
        print(f"\n{'═' * 70}")
        if self.title:
            print(f"  {self.title}")
            print(f"{'═' * 70}")

        for i, opt in enumerate(self.options):
            check = "x" if i in self.selected else " "
            name = opt.get("name", f"Opción {i+1}")
            desc = opt.get("description", "")
            deps = opt.get("dependencies", "")

            line = f"  [{check}] {i+1}. {name}"
            if desc:
                line += f" — {desc}"
            if deps and deps != "ninguna":
                line += f" | deps: {deps}"
            print(line)

        print(f"{'─' * 70}")
        print("  Comandos: [número] toggle | [T] Todas | [N] Ninguna | [V] Volver")
        print(f"{'─' * 70}")

        while True:
            response = input("  Selección: ").strip().upper()

            if response == "V":
                return None
            elif response == "T":
                self.selected = set(range(len(self.options)))
            elif response == "N":
                self.selected.clear()
            else:
                try:
                    nums = [int(x) for x in response.split()]
                    for n in nums:
                        if 1 <= n <= len(self.options):
                            idx = n - 1
                            if idx in self.selected:
                                self.selected.remove(idx)
                            else:
                                self.selected.add(idx)
                except (ValueError, IndexError):
                    print("  ❌ Selección inválida")
                    continue

            # Mostrar selección actual
            if self.selected:
                selected_names = [self.options[i]["name"] for i in sorted(self.selected)]
                print(f"\n  Seleccionados: {', '.join(selected_names)}")
                confirm = input("  ¿Confirmar selección? (s/N): ").strip().lower()
                if confirm == 's':
                    return sorted(list(self.selected))
            print()


def show_interactive_menu(options, title="", multi_select=True):
    """
    Mostrar menú interactivo y retornar opciones seleccionadas.

    Args:
        options: Lista de diccionarios con 'name', 'description', 'dependencies'
        title: Título del menú
        multi_select: Permitir selección múltiple

    Returns:
        Lista de diccionarios seleccionados, o None si se cancela
    """
    menu = InteractiveMenu(options, title, multi_select)
    selected_indices = menu.run()

    if selected_indices is None:
        return None

    return [options[i] for i in selected_indices]


# Prueba rápida
if __name__ == "__main__":
    test_options = [
        {"name": "skill-1", "description": "Primera skill", "dependencies": "ninguna"},
        {"name": "skill-2", "description": "Segunda skill", "dependencies": "Git"},
        {"name": "skill-3", "description": "Tercera skill", "dependencies": "Python"},
        {"name": "skill-4", "description": "Cuarta skill", "dependencies": "ninguna"},
    ]

    result = show_interactive_menu(test_options, "📦 SKILLS DE PRUEBA")
    if result:
        print("\nSeleccionados:")
        for item in result:
            print(f"  → {item['name']}")
    else:
        print("\nCancelado")
