import subprocess
import logging

logger = logging.getLogger()


def _check_ping(hostname):
    try:
        subprocess.run(['ping', '-c', '4', hostname],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _check_curl(url):
    try:
        subprocess.run(['curl', '-s', url],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _check_video_stream(url):
    try:
        result = subprocess.run(
            ['yt-dlp', '--get-url',  url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=True
        )
        urls = result.stdout.decode().strip().splitlines()

        for stream_url in urls:
            curl = subprocess.run([
                'curl',
                '--range', '0-1',
                '-s',
                '-o', '/dev/null',
                '-w', '%{http_code}',
                stream_url
            ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            if curl.stdout.decode().strip() == '206':
                return True

        return False

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def check_yandex_access():
    return _check_ping("yandex.ru") and _check_curl("https://yandex.ru")


def check_youtube_access():
    YOUTUBE_RICKROLL = "https://youtube.com/watch?v=dQw4w9WgXcQ"
    ping_success = _check_ping("youtube.com")
    if not ping_success:
        logger.warning("youtube ping failed")
    curl_success = _check_curl(YOUTUBE_RICKROLL)
    if not curl_success:
        logger.warning("youtube curl failed")
    stream_success = _check_video_stream(YOUTUBE_RICKROLL)
    if not stream_success:
        logger.warning("youtube stream failed")
    return ping_success and curl_success and stream_success


def check_instagram_access():
    ping_success = _check_ping("instagram.com")
    if not ping_success:
        logger.warning("instagram ping failed")
    curl_success = _check_curl("https://instagram.com")
    if not curl_success:
        logger.warning("instagram curl failed")
    return ping_success and curl_success
