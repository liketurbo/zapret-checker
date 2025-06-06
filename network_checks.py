import subprocess

def check_ping(hostname):
    try:
        subprocess.run(['ping', '-c', '4', hostname],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def check_curl(url):
    try:
        subprocess.run(['curl', '-s', '--max-time', '5', url],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def check_video_stream(url):
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