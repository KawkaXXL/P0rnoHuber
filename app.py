# Wykonal ASPLOT.pl
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from core import QUALITY, build_command, parse_urls

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('P0rnoHuber 1.0')
        self.geometry('850x700')
        self.minsize(740, 620)
        self.events = queue.Queue()
        self.proc = None
        self.lock = threading.Lock()
        self.busy = False
        self.stopping = threading.Event()
        self.closing = False
        self.folder = tk.StringVar(value=str(Path.home() / 'Downloads' / 'P0rnoHuber'))
        self.quality = tk.StringVar(value='Najlepsza')
        self.playlists = tk.BooleanVar(value=False)
        self.audio = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Gotowy. Jeden link w każdej linii.')
        self.item = ''
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('TButton', padding=7)
        panel = ttk.Frame(self, padding=20)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='P0rnoHuber', font=('Segoe UI', 21, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='Wykonal ASPLOT.pl', font=('Segoe UI', 10)).pack(anchor='w', pady=(2, 0))
        ttk.Label(panel, text='YouTube + Pornhub  /  filmy, Shorts, playlisty i MP3').pack(anchor='w', pady=(3, 16))
        ttk.Label(panel, text='Linki — po jednym w każdej linii').pack(anchor='w')
        self.urls = ScrolledText(panel, height=5, wrap='word', font=('Segoe UI', 10))
        self.urls.pack(fill='x', pady=(5, 10))
        ttk.Checkbutton(panel, text='Playlisty / kanały YouTube (może pobrać wiele filmów)', variable=self.playlists).pack(anchor='w')
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=10)
        ttk.Label(row, text='Jakość do:').pack(side='left')
        ttk.Combobox(row, textvariable=self.quality, values=QUALITY, state='readonly', width=14).pack(side='left', padx=8)
        ttk.Checkbutton(row, text='Tylko dźwięk — MP3', variable=self.audio).pack(side='left', padx=12)
        ttk.Label(panel, text='Folder zapisu').pack(anchor='w')
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=(5, 12))
        ttk.Entry(row, textvariable=self.folder).pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='Wybierz…', command=self.pick_folder).pack(side='left', padx=(8, 0))
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=(0, 12))
        self.start_btn = ttk.Button(row, text='Pobierz kolejkę', command=self.start)
        self.start_btn.pack(side='left')
        self.stop_btn = ttk.Button(row, text='Przerwij', command=self.stop, state='disabled')
        self.stop_btn.pack(side='left', padx=8)
        ttk.Button(row, text='O programie', command=self.about).pack(side='right', padx=8)
        ttk.Button(row, text='Otwórz folder', command=self.open_folder).pack(side='right')
        self.progress = ttk.Progressbar(panel, maximum=100)
        self.progress.pack(fill='x')
        ttk.Label(panel, textvariable=self.status, wraplength=780).pack(anchor='w', pady=8)
        self.log = ScrolledText(panel, height=12, state='disabled', wrap='word', font=('Consolas', 9))
        self.log.pack(fill='both', expand=True)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.after(100, self.poll)

    def about(self):
        messagebox.showinfo('O programie — P0rnoHuber',
            'P0rnoHuber 1.0\nWykonal ASPLOT.pl\nhttps://asplot.pl\n\n'
            'YouTube i Pornhub: pobieranie filmów, kolejka linków,\n'
            'playlisty i kanały YouTube, zapis MP3.\n\n'
            'Silnik: yt-dlp | Multimedia: FFmpeg | JavaScript: Deno\n'
            'Dostępność pobierania zależy od serwisu i materiału.')

    def pick_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)

    def open_folder(self):
        try:
            path = Path(self.folder.get()).expanduser().resolve()
            path.mkdir(parents=True, exist_ok=True)
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.Popen(['xdg-open', str(path)])
        except OSError as exc:
            messagebox.showerror('Folder', str(exc))

    def start(self):
        if self.busy:
            return
        try:
            urls = parse_urls(self.urls.get('1.0', 'end'), self.playlists.get())
            if not self.folder.get().strip():
                raise ValueError('Wybierz folder zapisu.')
            folder = Path(self.folder.get()).expanduser().resolve()
            folder.mkdir(parents=True, exist_ok=True)
            jobs = [build_command(url, folder, self.quality.get(), self.playlists.get(), self.audio.get()) for url in urls]
        except (ValueError, OSError) as exc:
            messagebox.showerror('Nie można rozpocząć', str(exc))
            return
        self.busy = True
        self.stopping.clear()
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.progress['value'] = 0
        self.status.set('Uruchamianie…')
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')
        threading.Thread(target=self.download, args=(jobs,), daemon=True).start()

    def download(self, jobs):
        succeeded = failed = 0
        try:
            for i, args in enumerate(jobs, 1):
                if self.stopping.is_set():
                    break
                self.events.put(('item', f'Link {i}/{len(jobs)}'))
                flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                
                with self.lock:
                    if self.stopping.is_set():
                        break
                    self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        stdin=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace',
                        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, creationflags=flags,
                        start_new_session=(os.name != 'nt'))
                    proc = self.proc
                for line in proc.stdout:
                    self.events.put(('line', line.rstrip()))
                code = proc.wait()
                proc.stdout.close()
                with self.lock:
                    self.proc = None
                if self.stopping.is_set():
                    break
                if code == 0:
                    succeeded += 1
                else:
                    failed += 1
        except Exception as exc:
            self.events.put(('line', str(exc)))
            failed += 1
        finally:
            self.events.put(('done', (succeeded, failed)))

    def stop(self):
        if self.stopping.is_set():
            return
        self.stopping.set()
        self.status.set('Zatrzymywanie pobierania i procesów pomocniczych…')
        self.stop_btn.configure(state='disabled')
        threading.Thread(target=self.kill_tree, daemon=True).start()

    def kill_tree(self):
        with self.lock:
            proc = self.proc
            if not proc or proc.poll() is not None:
                return
            try:
                if os.name == 'nt':
                    result = subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                    if result.returncode and proc.poll() is None:
                        proc.kill()
                else:
                    os.killpg(proc.pid, signal.SIGKILL)
            except (OSError, subprocess.TimeoutExpired):
                if proc.poll() is None:
                    proc.kill()

    def append_log(self, line):
        self.log.configure(state='normal')
        self.log.insert('end', line + '\n')
        if int(self.log.index('end-1c').split('.')[0]) > 600:
            self.log.delete('1.0', '100.0')
        self.log.see('end')
        self.log.configure(state='disabled')

    def poll(self):
        for _ in range(150):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'item':
                self.item = value
                self.progress['value'] = 0
                self.status.set(value + ' — analizowanie…')
                self.append_log('\n' + value)
            elif kind == 'line':
                if value.startswith('PROGRESS|'):
                    parts = value.split('|')
                    match = re.search(r'(\d+(?:\.\d+)?)%', parts[1])
                    if match:
                        self.progress['value'] = min(100, float(match[1]))
                    self.status.set(self.item + ' — ' + ' / '.join(parts[1:]))
                else:
                    self.append_log(value)
                    if value.startswith(('[Merger]', '[ExtractAudio]')):
                        self.status.set(self.item + ' — scalanie / konwersja…')
            else:
                self.busy = False
                self.start_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
                ok, failed = value
                if self.stopping.is_set():
                    self.status.set('Przerwano. Ponów te same linki, aby wznowić dostępne pliki .part.')
                else:
                    self.status.set(f'Koniec kolejki. Linki zakończone bez błędu: {ok}; z błędem: {failed}. Szczegóły w logu.')
                if self.closing:
                    self.destroy()
                    return
        self.after(100, self.poll)

    def close(self):
        if self.busy:
            self.closing = True
            self.stop()
        else:
            self.destroy()

if __name__ == '__main__':
    App().mainloop()
