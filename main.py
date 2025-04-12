import yt_dlp
import humanize
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re
from UI import UI


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("my-tube")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        self.root.configure(bg="#f5f7fa")

        self.style = UI()

        self.formats = []
        self.download_path = os.path.expanduser("~/Downloads")
        self.thumbnail_image = None
        self.video_info = None

        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header_frame, text="YouTube Downloader Pro", style='Header.TLabel').pack(side=tk.LEFT)

        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(url_frame, text="URL de la vidéo:").pack(side=tk.LEFT)

        self.url_entry = ttk.Entry(url_frame, width=50, font=('Helvetica', 10))
        self.url_entry.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        self.fetch_btn = ttk.Button(url_frame, text="Récupérer", command=self.fetch_formats)
        self.fetch_btn.pack(side=tk.LEFT, padx=5)

        self.info_frame = ttk.Frame(main_frame)
        self.info_frame.pack(fill=tk.X, pady=10)

        self.thumbnail_frame = ttk.Frame(self.info_frame, width=240, height=135)
        self.thumbnail_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.thumbnail_frame.pack_propagate(False)

        self.thumbnail_label = ttk.Label(self.thumbnail_frame)
        self.thumbnail_label.pack(fill=tk.BOTH, expand=True)

        video_details_frame = ttk.Frame(self.info_frame)
        video_details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.channel_var = tk.StringVar()

        ttk.Label(video_details_frame, textvariable=self.title_var,
                 font=('Helvetica', 12, 'bold'), wraplength=400).pack(anchor=tk.W)
        ttk.Label(video_details_frame, textvariable=self.duration_var).pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(video_details_frame, textvariable=self.channel_var).pack(anchor=tk.W)

        formats_frame = ttk.LabelFrame(main_frame, text="Formats disponibles")
        formats_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "ext", "resolution", "fps", "filesize", "note")
        self.tree = ttk.Treeview(formats_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("ext", text="Format")
        self.tree.heading("resolution", text="Résolution")
        self.tree.heading("fps", text="FPS")
        self.tree.heading("filesize", text="Taille")
        self.tree.heading("note", text="Qualité")

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("ext", width=80, anchor=tk.CENTER)
        self.tree.column("resolution", width=100, anchor=tk.CENTER)
        self.tree.column("fps", width=60, anchor=tk.CENTER)
        self.tree.column("filesize", width=100, anchor=tk.CENTER)
        self.tree.column("note", width=150)

        scrollbar = ttk.Scrollbar(formats_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self.download_selected())

        download_options_frame = ttk.Frame(main_frame)
        download_options_frame.pack(fill=tk.X, pady=(10, 5))

        folder_btn = ttk.Button(download_options_frame, text="Dossier de destination",
                               command=self.choose_directory)
        folder_btn.pack(side=tk.LEFT)

        self.folder_var = tk.StringVar(value=f"Dossier: {self.download_path}")
        folder_label = ttk.Label(download_options_frame, textvariable=self.folder_var,
                                style='Status.TLabel')
        folder_label.pack(side=tk.LEFT, padx=10)

        self.download_btn = ttk.Button(download_options_frame, text="Télécharger",
                                      command=self.download_selected)
        self.download_btn.pack(side=tk.RIGHT)

        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        self.status_label.pack(anchor=tk.W)

        self.info_frame.pack_forget()

    def choose_directory(self):
        """Permet à l'utilisateur de choisir un dossier de destination"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.folder_var.set(f"Dossier: {self.download_path}")

    def fetch_formats(self):
        """Récupère les formats disponibles pour l'URL donnée"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide")
            return

        # Vérifier si l'URL est valide
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', url):
            messagebox.showerror("Erreur", "URL YouTube invalide")
            return

        self.status_var.set("Récupération des informations...")
        self.fetch_btn.config(state=tk.DISABLED)

        for item in self.tree.get_children():
            self.tree.delete(item)

        threading.Thread(target=self._fetch_formats_thread, args=(url,), daemon=True).start()

    def _fetch_formats_thread(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
                self.formats = self.video_info.get('formats', [])

                self.root.after(0, self._update_video_info)
                self.root.after(0, self._update_formats_list)
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Erreur: {str(e)}"))

    def _update_video_info(self):
        """Met à jour les informations de la vidéo dans l'interface"""
        if not self.video_info:
            return

        self.info_frame.pack(fill=tk.X, pady=10, after=self.url_entry.master)

        self.title_var.set(self.video_info.get('title', 'Titre inconnu'))

        duration_secs = self.video_info.get('duration', 0)
        mins, secs = divmod(duration_secs, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            duration_str = f"Durée: {hours}h {mins}m {secs}s"
        else:
            duration_str = f"Durée: {mins}m {secs}s"
        self.duration_var.set(duration_str)

        self.channel_var.set(f"Chaîne: {self.video_info.get('uploader', 'Inconnu')}")

        threading.Thread(target=self._load_thumbnail, daemon=True).start()

    def _load_thumbnail(self):
        """Charge la miniature de la vidéo"""
        try:
            thumbnail_url = self.video_info.get('thumbnail', '')
            if thumbnail_url:
                response = requests.get(thumbnail_url)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((240, 135), Image.LANCZOS)
                self.thumbnail_image = ImageTk.PhotoImage(img)

                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, lambda: self.thumbnail_label.config(image=self.thumbnail_image))
        except Exception as e:
            print(f"Erreur lors du chargement de la miniature: {e}")

    def _update_formats_list(self):
        """Met à jour la liste des formats disponibles"""
        sorted_formats = sorted(
            self.formats,
            key=lambda f: (
                f.get('height', 0) or 0,
                f.get('fps', 0) or 0,
                f.get('filesize', 0) or 0
            ),
            reverse=True
        )

        for f in sorted_formats:
            format_id = f['format_id']
            ext = f.get('ext', 'N/A')

            # Résolution
            height = f.get('height', 0)
            width = f.get('width', 0)
            if height and width:
                resolution = f"{width}x{height}"
            elif height:
                resolution = f"{height}p"
            else:
                resolution = "Audio uniquement"

            # FPS
            fps = f.get('fps', '')
            if fps:
                fps = f"{fps}"
            else:
                fps = "N/A"

            filesize = f.get('filesize')
            if filesize:
                filesize = humanize.naturalsize(filesize)
            else:
                filesize = "Inconnue"

            note = f.get('format_note', '')

            item_id = self.tree.insert("", tk.END, values=(format_id, ext, resolution, fps, filesize, note))

            if 'best' in note.lower() or ('1080p' in resolution and 'mp4' in ext):
                self.tree.selection_set(item_id)
                self.tree.see(item_id)

        self.status_var.set(f"{len(self.formats)} formats disponibles")
        self.fetch_btn.config(state=tk.NORMAL)

    def _show_error(self, message):
        messagebox.showerror("Erreur", message)
        self.status_var.set("Erreur")
        self.fetch_btn.config(state=tk.NORMAL)

    def download_selected(self):
        """Télécharge le format sélectionné"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Erreur", "Veuillez sélectionner un format")
            return

        item = self.tree.item(selected[0])
        format_id = item['values'][0]
        url = self.url_entry.get().strip()

        self.status_var.set(f"Téléchargement du format {format_id}...")
        self.download_btn.config(state=tk.DISABLED)
        self.fetch_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)

        threading.Thread(target=self._download_thread, args=(url, format_id), daemon=True).start()

    def _download_thread(self, url, format_id):
        try:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    p = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        p_float = float(p)
                        self.root.after(0, lambda: self.progress_var.set(p_float))
                        self.root.after(0, lambda: self.status_var.set(
                            f"Téléchargement: {d.get('_percent_str', '0%')} - "
                            f"Vitesse: {d.get('_speed_str', 'N/A')} - "
                            f"ETA: {d.get('_eta_str', 'N/A')}"
                        ))
                    except:
                        pass
                elif d['status'] == 'finished':
                    self.root.after(0, lambda: self.status_var.set("Finalisation..."))

            # Options de téléchargement
            ydl_opts = {
                'format': f"{format_id}+bestaudio[ext=m4a]/best",
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.root.after(0, lambda: self._download_complete())
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Erreur de téléchargement: {str(e)}"))

    def _download_complete(self):
        self.status_var.set("Téléchargement terminé ! 🎉")
        self.download_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)

        messagebox.showinfo(
            "Succès",
            f"Téléchargement terminé avec succès !\n\nLe fichier a été enregistré dans :\n{self.download_path}"
        )

        if messagebox.askyesno("Ouvrir le dossier", "Voulez-vous ouvrir le dossier de destination ?"):
            os.startfile(self.download_path) if os.name == 'nt' else os.system(f'xdg-open "{self.download_path}"')

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()