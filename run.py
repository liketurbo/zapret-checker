#!/usr/bin/env python3

import subprocess
from config_utils import get_configs, update_config
from network_checks import test_yandex_access, test_youtube_access, test_instagram_access
from log import setup_logging
import sys
import termios
import tty


def restart_zapret():
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


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def clear_screen():
    print("\033c", end='')


def hide_cursor():
    print("\033[?25l", end='')


def show_cursor():
    print("\033[?25h", end='')


def display_menu(options, current_idx, current_config_name, status_msg):
    clear_screen()
    hide_cursor()
    print("zapret configuration manager\n")

    test_options = [
        "test yandex access",
        "test youtube access",
        "test instagram access",
    ]

    for idx, option in enumerate(test_options):
        prefix = '  '
        if idx == current_idx and current_idx < len(test_options):
            prefix = '> '
        print(f"{prefix}{option}")

    print('\n  select configuration:')

    config_start_idx = len(test_options)
    for idx, option in enumerate(options):
        display_idx = config_start_idx + idx
        prefix = '  '
        if display_idx == current_idx:
            prefix = '> '
        postfix = ''
        if current_config_name == option:
            postfix = ' *'
        print(f"{prefix}{option}{postfix}")

    if status_msg[0]:
        status_text, status_type = status_msg
        status_prefix = {
            'loading': '[loading]',
            'error': '[error]',
            'success': '[success]'
        }.get(status_type)
        print(f"\n{status_prefix} {status_text}")

    print("\nUse ↑/↓ arrows, Enter to select, 'q' to quit")


def main():
    try:
        setup_logging()

        all_configs = get_configs()

        config_keys = list(all_configs.keys())
        config_keys.sort()

        current_config_name = None
        current_idx = 0
        status_msg = (None, 'success')

        total_options = 3 + len(config_keys)

        while True:
            display_menu(config_keys, current_idx,
                         current_config_name, status_msg)
            key = get_key()

            if key == '\x1b':
                next_key = get_key()
                if next_key == '[':
                    arrow = get_key()
                    if arrow == 'A':  # up arrow
                        current_idx = max(0, current_idx - 1)
                    elif arrow == 'B':  # down arrow
                        current_idx = min(total_options - 1, current_idx + 1)
            elif key == '\r':
                if current_idx == 0:
                    status_msg = ('testing yandex access...', 'loading')
                    display_menu(config_keys, current_idx,
                                 current_config_name, status_msg)
                    success = test_yandex_access()
                    status_msg = ('yandex test completed',
                                  'success' if success else 'error')
                elif current_idx == 1:
                    status_msg = ('testing youtube access...', 'loading')
                    display_menu(config_keys, current_idx,
                                 current_config_name, status_msg)
                    success = test_youtube_access()
                    status_msg = ('youtube test completed',
                                  'success' if success else 'error')
                elif current_idx == 2:
                    status_msg = ('testing instagram access...', 'loading')
                    display_menu(config_keys, current_idx,
                                 current_config_name, status_msg)
                    success = test_instagram_access()
                    status_msg = ('instagram test completed',
                                  'success' if success else 'error')
                elif current_idx >= 3:
                    config_name = config_keys[current_idx - 3]
                    current_config_name = config_name
                    config = all_configs[config_name]
                    status_msg = ('setting config...', 'loading')
                    display_menu(config_keys, current_idx,
                                 current_config_name, status_msg)
                    update_config(config)
                    status_msg = ('restarting zapret...', 'loading')
                    display_menu(config_keys, current_idx,
                                 current_config_name, status_msg)
                    success = restart_zapret()
                    status_msg = ('zapret restart completed',
                                  'success' if success else 'error')
            elif key.lower() == 'q':
                return
    finally:
        show_cursor()


if __name__ == "__main__":
    main()
