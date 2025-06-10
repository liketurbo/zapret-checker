import subprocess


def _check_ping(hostname):
    try:
        subprocess.run(['ping', '-c', '4', hostname],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _check_curl(url):
    try:
        subprocess.run(['curl', '-s', '--max-time', '5', url],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _check_video_stream(url):
    try:
        result = subprocess.run(
            ['yt-dlp', '--get-url', '--format', 'best', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=True
        )
        stream_url = result.stdout.decode().strip()

        subprocess.run([
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
            check=True
        )

        return True

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def check_yandex_access():
    return _check_ping("www.yandex.ru") and _check_curl("https://www.yandex.ru")


def check_youtube_access():
    YOUTUBE_RICKROLL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    return _check_ping("www.youtube.com") and _check_curl(YOUTUBE_RICKROLL) and _check_video_stream(YOUTUBE_RICKROLL)


def check_instagram_access():
    return _check_ping("www.instagram.com") and _check_curl(
        "https://www.instagram.com")
