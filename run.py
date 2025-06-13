#!/usr/bin/env python3

import subprocess
from config_utils import get_configs, update_config
from network_checks import test_yandex_access, test_youtube_access, test_instagram_access
from log import setup_logging
import sys
import termios
import tty
import signal
from typing import List, Optional, Tuple

test_actions = [
    ("Test Yandex access", test_yandex_access),
    ("Test YouTube access", test_youtube_access),
    ("Test Instagram access", test_instagram_access),
]
EXIT_KEY = 'q'


def restart_zapret() -> bool:
    try:
        subprocess.run(
            ["/etc/init.d/zapret", "restart"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except:
        return False


def get_key() -> str:
    fd = sys.stdin.fileno()
    old_attrs = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)
    return ch


def clear_screen() -> None:
    print("\033c", end='')


def hide_cursor() -> None:
    print("\033[?25l", end='')


def show_cursor() -> None:
    print("\033[?25h", end='')


def display_menu(
    configs: List[str],
    selected: int,
    current: Optional[str],
    status: Tuple[Optional[str], str],
) -> None:
    clear_screen()
    hide_cursor()
    print("Zapret Configuration Manager\n")

    for idx, (label, _) in enumerate(test_actions):
        prefix = "> " if idx == selected else "  "
        print(f"{prefix}{label}")

    print('\n  Select configuration:')
    base_idx = len(test_actions)
    for idx, name in enumerate(configs):
        menu_idx = base_idx + idx
        prefix = "> " if menu_idx == selected else "  "
        active = " *" if name == current else ""
        print(f"{prefix}{name}{active}")

    msg, mtype = status
    if msg:
        label = {'loading': '[...]', 'error': '[!]',
                 'success': '[✓]'}.get(mtype, '')
        print(f"\n{label} {msg}")

    print(f"\nUse ↑/↓ to navigate, Enter to select, '{EXIT_KEY}' to quit")


def cleanup_and_exit(signum=None, frame=None) -> None:
    show_cursor()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    setup_logging()
    configs_map = get_configs()
    configs = sorted(configs_map)

    current_cfg: Optional[str] = None
    selection = 0
    status: Tuple[Optional[str], str] = (None, 'success')
    total = len(test_actions) + len(configs)

    while True:
        display_menu(configs, selection, current_cfg, status)
        key = get_key()

        if key == '\x1b':  # arrow keys prefix
            _next1 = get_key()
            next2 = get_key()
            if next2 == 'A':  # up arrow
                selection = max(0, selection - 1)
            elif next2 == 'B':  # down arrow
                selection = min(total - 1, selection + 1)
        elif key == '\r':  # Enter
            if selection < len(test_actions):
                label, action = test_actions[selection]
                status = (f"{label}...", 'loading')
                display_menu(configs, selection, current_cfg, status)
                ok = action()
                status = (f"{label} {'succeeded' if ok else 'failed'}",
                          'success' if ok else 'error')
            else:
                idx = selection - len(test_actions)
                name = configs[idx]
                current_cfg = name
                status = (f"Applying {name}...", 'loading')
                display_menu(configs, selection, current_cfg, status)
                update_config(configs_map[name])
                status = (f"Restarting zapret...", 'loading')
                display_menu(configs, selection, current_cfg, status)
                ok = restart_zapret()
                status = ("Restart completed" if ok else "Restart failed",
                          'success' if ok else 'error')
        elif key.lower() == EXIT_KEY:
            break

    cleanup_and_exit()


if __name__ == "__main__":
    main()
