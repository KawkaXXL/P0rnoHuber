# P0rnoHuber 1.0

Created by ASPLOT.pl

Desktop video downloader for YouTube and Pornhub, with download queues,
YouTube playlists, quality selection, and MP3 audio export.

## Requirements

- Windows 10 or 11, 64-bit.
- Python 3.12, 64-bit, with tkinter and Python Launcher.
- Internet access.

## Prepare the bin folder

Create a folder named `bin` next to `app.py` and place these files directly inside it:

| File | Download |
|---|---|
| `yt-dlp.exe` | [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases/latest) — select `yt-dlp.exe` for Windows x64. |
| `ffmpeg.exe` | [FFmpeg builds](https://github.com/yt-dlp/FFmpeg-Builds/releases) — select a Windows win64 static build, not a shared build. |
| `ffprobe.exe` | Included in the same FFmpeg archive. |
| `deno.exe` | [Deno releases](https://github.com/denoland/deno/releases/latest) — extract `deno-x86_64-pc-windows-msvc.zip`. |

Extract `ffmpeg.exe` and `ffprobe.exe` from the FFmpeg archive's `bin` directory.
The static build does not require the additional FFmpeg DLLs used by shared builds.
Extract `deno.exe` from its archive. Do not place these executables inside extra
subfolders. They run automatically in the background; no installation is needed.

## Run from source

Open Command Prompt in the directory containing `app.py` and `core.py`, then run:

```bat
py app.py
```

With all four executables in `bin`, no additional Python packages are required
to run the application. Python must include tkinter.

## Build a Windows executable

Open Command Prompt in the source directory and install PyInstaller:

```bat
py -m pip install -U pyinstaller
```

Build the application:

```bat
py -m PyInstaller --noconfirm --clean --onefile --windowed --name P0rnoHuber app.py
```

The executable will be created at `dist\P0rnoHuber.exe`.
Copy the prepared `bin` folder into `dist`, so the final layout is:

| Path | Purpose |
|---|---|
| `dist/P0rnoHuber.exe` | Application |
| `dist/bin/yt-dlp.exe` | Download engine |
| `dist/bin/ffmpeg.exe` | Video/audio merging and MP3 conversion |
| `dist/bin/ffprobe.exe` | Media inspection |
| `dist/bin/deno.exe` | JavaScript runtime for YouTube support |

Run `dist\P0rnoHuber.exe`. The complete `dist` folder is portable and does not
require Python on the destination computer. Keep `bin` next to the application;
the application executable does not embed these external tools.

---

WAŻNE dot. WYDANIA WINDOWS / IMPORTANT about WINDOWS RELEASE 

Dlaczego paczka ma około 200 MB?

Sam P0rnoHuber jest niewielki. Większość miejsca zajmują dołączone narzędzia: FFmpeg i FFprobe do obsługi obrazu i dźwięku, yt-dlp do pobierania oraz Deno potrzebne do obsługi YouTube. W aplikacji znajduje się też środowisko Pythona.

Dołączyłem je, żeby nie trzeba było niczego osobno instalować ani konfigurować. Rozpakowujesz całą paczkę, uruchamiasz program i możesz pobierać.

-

Why is the download around 200 MB?

P0rnoHuber itself is small. Most of the space is taken up by the included tools: FFmpeg and FFprobe for handling video and audio, yt-dlp for downloading, and Deno for YouTube support. The application also includes the Python runtime.

I bundled these so you don’t have to install or configure them yourself. Just extract the whole archive, open the app, and start downloading.
