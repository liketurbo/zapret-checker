#!/usr/bin/env python3

import subprocess
from config_utils import get_configs, update_config
from network_checks import check_yandex_access, check_youtube_access, check_instagram_access
from log import setup_logging
import logging


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


def main():
    setup_logging()
    logger = logging.getLogger()

    yandex_access = check_yandex_access()

    if not yandex_access:
        logger.warning("yandex check failed")
        return

    all_configs = get_configs()

    youtube_config = None
    instagram_config = None

    for config_name in all_configs:
        config = all_configs[config_name]
        logger.info(f"checking config {config_name}")
        update_config(config)

        success = restart_zapret()
        if not success:
            logger.error("failed to restart zapret")
            return

        youtube_access = check_youtube_access()
        if not youtube_access:
            logger.warning("no youtube access")
        else:
            youtube_config = config

        instagram_access = check_instagram_access()
        if not instagram_access:
            logger.warning("no instagram access")
        else:
            instagram_config = config

        if youtube_access and instagram_access:
            logger.info("config worked for both services")
            break

    if not youtube_config and not instagram_config:
        logger.warning("didn't find config that works for any service")
    if not instagram_config:
        logger.warning("found config that only works for youtube")
        update_config(youtube_config)
        restart_zapret()
    if not youtube_config:
        logger.warning("found config that only works for instagram")
        update_config(instagram_config)
        restart_zapret()


if __name__ == "__main__":
    main()
