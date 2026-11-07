# Wykonal ASPLOT.pl
import os
from pathlib import Path
import shutil
import sys
from urllib.parse import urlsplit, parse_qs

QUALITY = ('Najlepsza', '2160', '1440', '1080', '720', '480')

def base_dir():
    return Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent

def tool(name, root=None):
    root = root or base_dir()
    local = root / 'bin' / (name + ('.exe' if os.name == 'nt' else ''))
    return str(local) if local.is_file() else shutil.which(name)

def validate_url(url, playlists=False):
    try:
        p = urlsplit(url)
        if p.scheme != 'https' or p.username or p.password or p.port not in (None, 443):
            raise ValueError()
        host = (p.hostname or '').lower()
        query = parse_qs(p.query)
        if host == 'pornhub.com' or host.endswith('.pornhub.com'):
            if p.path == '/view_video.php' and query.get('viewkey'):
                return url
        elif host in ('youtu.be', 'www.youtu.be'):
            if p.path.strip('/') and '/' not in p.path.strip('/'):
                return url
        elif host == 'youtube.com' or host.endswith('.youtube.com'):
            parts = p.path.strip('/').split('/')
            if (p.path == '/watch' and query.get('v')) or (len(parts) == 2 and parts[0] in ('shorts', 'live', 'embed') and parts[1]):
                return url
            collection = (p.path == '/playlist' and query.get('list')) or (parts[0].startswith('@') and len(parts[0]) > 1) or (len(parts) >= 2 and parts[0] in ('channel', 'c', 'user'))
            if collection:
                if not playlists:
                    raise ValueError('Dla playlisty lub kanału zaznacz „Playlisty / kanały YouTube”.')
                return url
    except ValueError as exc:
        if str(exc).startswith('Dla playlisty'):
            raise
    raise ValueError('Wymagany link HTTPS do filmu YouTube/Pornhub albo playlisty lub kanału YouTube.')

def parse_urls(text, playlists=False):
    urls = list(dict.fromkeys(line.strip() for line in text.splitlines() if line.strip()))
    if not urls:
        raise ValueError('Wklej przynajmniej jeden link (każdy w osobnej linii).')
    for index, url in enumerate(urls, 1):
        try:
            validate_url(url, playlists)
        except ValueError as exc:
            raise ValueError(f'Link {index}: {exc}') from exc
    return urls

def engine():
    exe = tool('yt-dlp')
    if exe:
        return [exe]
    if getattr(sys, 'frozen', False):
        raise ValueError('Brak bin/yt-dlp.exe. Pobierz silnik według README.md.')
    return [sys.executable, '-m', 'yt_dlp']

def build_command(url, folder, quality, playlists, audio=False):
    validate_url(url, playlists)
    if quality not in QUALITY:
        raise ValueError('Nieznana jakość.')
    ffmpeg, ffprobe, deno = tool('ffmpeg'), tool('ffprobe'), tool('deno')
    if not ffmpeg or not ffprobe:
        raise ValueError('Brak FFmpeg/FFprobe. Umieść je w folderze bin lub dodaj do PATH (instrukcja README.md).')
    if not deno:
        raise ValueError('Brak Deno. Umieść deno.exe w folderze bin lub dodaj do PATH (instrukcja README.md).')
    args = engine() + ['--ignore-config', '--no-plugin-dirs', '--newline', '--no-color',
        '--progress', '--no-quiet', '--progress-delta', '0.5', '--windows-filenames', '--no-overwrites',
        '--continue', '--socket-timeout', '20', '--retries', '3', '--fragment-retries', '3',
        '--no-abort-on-error', '--yes-playlist' if playlists else '--no-playlist',
        '--ffmpeg-location', str(Path(ffmpeg).parent), '--js-runtimes', f'deno:{deno}',
        '--paths', str(folder), '--output', '%(title).140B [%(id)s].%(ext)s',
        '--progress-template', 'download:PROGRESS|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s',
        '--print', 'after_move:FILE|%(filepath)s']
    if audio:
        args += ['-f', 'ba/b', '-x', '--audio-format', 'mp3', '--audio-quality', '0']
    else:
        limit = '' if quality == 'Najlepsza' else f'[height<={quality}]'
        args += ['-f', f'bv*{limit}+ba/b{limit}', '--merge-output-format', 'mkv']
    return args + ['--', url]
