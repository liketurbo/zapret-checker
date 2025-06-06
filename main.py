#!/usr/bin/env python3

from .config_utils import get_configs, update_config
from .network_checks import check_ping, check_curl, check_video_stream

def main():
    configs = get_configs()
    update_config(configs[0])
    print(check_ping("www.youtube.com"))
    print(check_curl("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
    print(check_video_stream("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))


if __name__ == "__main__":
    main()
