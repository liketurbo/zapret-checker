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
    return _check_ping("youtube.com") and _check_curl(YOUTUBE_RICKROLL) and _check_video_stream(YOUTUBE_RICKROLL)


def check_instagram_access():
    return _check_ping("instagram.com") and _check_curl(
        "https://instagram.com")
