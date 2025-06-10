import os
import shutil

TARGET_ZAPRET_DIR = os.getenv('ZAPRET_DIR', '/tmp/zapret')
TARGET_ROOT_DIR = os.getenv('ROOT_DIR', '/tmp')
TARGET_IPSET_DIR = os.path.join(TARGET_ZAPRET_DIR, 'ipset')

DEFAULT_NFQWS_PORTS_TCP = "80,443"
DEFAULT_NFQWS_PORTS_UDP = "443"
DEFAULT_DISABLE_IPV6 = 1
DEFAULT_WS_USER = "daemon"
DEFAULT_FWTYPE = "nftables"

DEFAULT_IPSET_FILES = {
    './files/zapret-hosts-google.txt',
    './files/zapret-hosts-user-exclude.txt',
    './files/zapret-hosts-user.txt'
}


def parse_config(file_path):
    tcp_ports = None
    udp_ports = None
    disable_ipv6 = None
    ws_user = None
    fwtype = None
    commands = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("NFQWS_PORTS_TCP="):
                tcp_ports = line.split("=", 1)[1].strip()
            elif line.startswith("NFQWS_PORTS_UDP="):
                udp_ports = line.split("=", 1)[1].strip()
            elif line.startswith("DISABLE_IPV6="):
                disable_ipv6 = line.split("=", 1)[1].strip()
            elif line.startswith("WS_USER="):
                ws_user = line.split("=", 1)[1].strip()
            elif line.startswith("FWTYPE="):
                fwtype = line.split("=", 1)[1].strip()
            else:
                commands.append(line.strip())

    return {
        "tcp_ports": tcp_ports or DEFAULT_NFQWS_PORTS_TCP,
        "udp_ports": udp_ports or DEFAULT_NFQWS_PORTS_UDP,
        "disable_ipv6": int(disable_ipv6) if disable_ipv6 is not None else DEFAULT_DISABLE_IPV6,
        "ws_user": ws_user or DEFAULT_WS_USER,
        "fwtype": fwtype or DEFAULT_FWTYPE,
        "command": " ".join(commands),
    }


def get_configs():
    configs = []
    configs_dir = './configs/discussion-168'

    for entry in os.listdir(configs_dir):
        entry_path = os.path.join(configs_dir, entry)

        if os.path.isfile(entry_path):
            config = parse_config(entry_path)
            config['ipset_files'] = DEFAULT_IPSET_FILES.copy()
            configs.append(config)
        elif os.path.isdir(entry_path):
            config = None
            ipset_files = DEFAULT_IPSET_FILES.copy()

            for file in os.listdir(entry_path):
                file_path = os.path.join(entry_path, file)

                if file == 'config.txt':
                    config = parse_config(file_path)
                else:
                    ipset_files.add(file_path)

            config['ipset_files'] = ipset_files
            configs.append(config)

    return configs


def update_config(config):
    with open('./files/default-config.txt') as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('NFQWS_PORTS_TCP='):
            new_lines.append(f'NFQWS_PORTS_TCP="{config["tcp_ports"]}"\n')
        elif stripped_line.startswith('NFQWS_PORTS_UDP='):
            new_lines.append(f'NFQWS_PORTS_UDP="{config["udp_ports"]}"\n')
        elif stripped_line.startswith('DISABLE_IPV6='):
            new_lines.append(f'DISABLE_IPV6={config["disable_ipv6"]}\n')
        elif stripped_line.startswith('WS_USER='):
            new_lines.append(f'WS_USER="{config["ws_user"]}"\n')
        elif stripped_line.startswith('FWTYPE='):
            new_lines.append(f'FWTYPE={config["fwtype"]}\n')
        elif stripped_line.startswith('NFQWS_OPT='):
            new_lines.append(f'NFQWS_OPT="{config["command"]}"\n')
        else:
            new_lines.append(line)

    os.makedirs(TARGET_ZAPRET_DIR, exist_ok=True)

    config_path = os.path.join(TARGET_ZAPRET_DIR, 'config')
    with open(config_path, 'w') as f:
        f.writelines(new_lines)

    os.makedirs(TARGET_IPSET_DIR, exist_ok=True)

    for ipset_file in config['ipset_files']:
        dst = os.path.join(TARGET_IPSET_DIR, os.path.basename(ipset_file))
        shutil.copy2(ipset_file, dst)
