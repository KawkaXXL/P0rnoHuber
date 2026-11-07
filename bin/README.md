# Narzędzia dla P0rnoHuber 1.0 — Windows x64

Pobierz i umieść w tym folderze cztery pliki:

| Plik | Oficjalne źródło | Co wybrać |
|---|---|---|
| yt-dlp.exe | [yt-dlp Releases](https://github.com/yt-dlp/yt-dlp/releases/latest) | yt-dlp.exe dla Windows x64 |
| ffmpeg.exe | [FFmpeg Builds](https://github.com/yt-dlp/FFmpeg-Builds/releases) | Archiwum Windows win64 static, bez shared w nazwie |
| ffprobe.exe | To samo archiwum FFmpeg | Plik z podfolderu bin |
| deno.exe | [Deno Releases](https://github.com/denoland/deno/releases/latest) | deno-x86_64-pc-windows-msvc.zip |

## Jak przygotować pliki

1. Pobierz yt-dlp.exe i zapisz go tutaj. Nie wybieraj yt-dlp_x86.exe ani ARM64.
2. Rozpakuj paczkę FFmpeg, otwórz jej podfolder bin i skopiuj ffmpeg.exe
   oraz ffprobe.exe tutaj. Z kompilacji static do działania potrzebne są
   te dwa pliki; pozostałe programy i dokumenty nie są wymagane do uruchomienia.
   Wersja shared wymaga dodatkowych DLL — wybierz static, aby uniknąć tej zależności.
3. Rozpakuj archiwum Deno i skopiuj deno.exe tutaj. Nie wybieraj denort.
4. Wszystkie cztery EXE mają leżeć bezpośrednio w tym folderze, bez kolejnych
   podfolderów. Nie trzeba ich instalować ani uruchamiać ręcznie.

P0rnoHuber automatycznie uruchamia te narzędzia w tle. Przy budowaniu EXE skrypt
kopiuje zawartość bin do dist/bin. Zachowaj bin obok P0rnoHuber.exe.

Do publikacji kompletu Portable zachowaj wymagane licencje i informacje o
źródłach pobranych narzędzi zgodnie z warunkami ich dystrybucji. Mogą znajdować
się w dodatkowym katalogu licenses; nie muszą leżeć obok samych EXE.

Repozytorium źródłowe zawiera w bin tylko ten README. Pliki binarne nie są
częścią paczki źródłowej.
