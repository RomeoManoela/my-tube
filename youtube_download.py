import os
import re
import threading
import time
import tkinter as tk
from io import BytesIO
from tkinter import ttk, filedialog, messagebox

import humanize
import requests
import yt_dlp
from PIL import Image, ImageTk

from ui import UI


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My-Tube")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # Appliquer le style moderne
        self.style = UI()

        # Variables
        self.formats = []
        self.download_path = os.path.expanduser("~/Downloads")
        self.thumbnail_image = None
        self.video_info = None
        self.is_playlist = False
        self.playlist_videos = []
        self.current_playlist_index = 0
        self.playlist_download_active = False
        self.download_active = False
        self.download_thread = None
        self.download_cancelled = False

        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="My-Tube", style='Header.TLabel').pack(side=tk.LEFT)

        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="URL de la vidéo:").pack(side=tk.LEFT)

        self.url_entry = ttk.Entry(url_frame, width=50, font=('Helvetica', 10))
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.fetch_btn = ttk.Button(url_frame, text="Récupérer", command=self.fetch_formats)
        self.fetch_btn.pack(side=tk.LEFT, padx=5)

        playlist_controls_frame = ttk.Frame(main_frame)
        playlist_controls_frame.pack(fill=tk.X, pady=(0, 10))

        self.prev_video_btn = ttk.Button(playlist_controls_frame, text="◀ Précédente",
                                         command=self.load_previous_playlist_video, state=tk.DISABLED)
        self.prev_video_btn.pack(side=tk.LEFT, padx=5)

        self.next_video_btn = ttk.Button(playlist_controls_frame, text="Suivante ▶",
                                         command=self.load_next_playlist_video, state=tk.DISABLED)
        self.next_video_btn.pack(side=tk.LEFT, padx=5)

        self.download_all_btn = ttk.Button(playlist_controls_frame, text="Télécharger la playlist",
                                           command=self.download_playlist, state=tk.DISABLED)
        self.download_all_btn.pack(side=tk.RIGHT, padx=5)

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

        self.cancel_btn = ttk.Button(download_options_frame, text="Annuler",
                                     command=self.cancel_download, style='Danger.TButton')

        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                        maximum=100, style='TProgressbar')
        self.progress.pack(fill=tk.X, padx=10)

        self.download_stats_frame = ttk.Frame(main_frame)
        self.download_stats_frame.pack(fill=tk.X, pady=5)

        self.percent_var = tk.StringVar(value="0%")
        self.download_size_var = tk.StringVar(value="-- / --")
        self.download_speed_var = tk.StringVar(value="-- KB/s")
        self.elapsed_time_var = tk.StringVar(value="00:00")
        self.download_eta_var = tk.StringVar(value="--:--")

        stats_frame = ttk.Frame(self.download_stats_frame)
        stats_frame.pack(fill=tk.X, padx=10)

        ttk.Label(stats_frame, text="Progression:", style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.percent_var, width=6, style='Status.TLabel').grid(row=0, column=1,
                                                                                                   sticky=tk.W)

        ttk.Label(stats_frame, text="Taille:", style='Status.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.download_size_var, style='Status.TLabel').grid(row=0, column=3,
                                                                                                sticky=tk.W)

        ttk.Label(stats_frame, text="Vitesse:", style='Status.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.download_speed_var, width=10, style='Status.TLabel').grid(row=1,
                                                                                                           column=1,
                                                                                                           sticky=tk.W)

        ttk.Label(stats_frame, text="Écoulé:", style='Status.TLabel').grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.elapsed_time_var, style='Status.TLabel').grid(row=1, column=3,
                                                                                               sticky=tk.W)

        ttk.Label(stats_frame, text="Restant:", style='Status.TLabel').grid(row=1, column=4, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, textvariable=self.download_eta_var, style='Status.TLabel').grid(row=1, column=5,
                                                                                               sticky=tk.W)

        self.download_stats_frame.pack_forget()

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        self.status_label.pack(anchor=tk.W)

        self.info_frame.pack_forget()  # Cacher le cadre d'info jusqu'à ce qu'une vidéo soit chargée

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

        # Vérifier si l'URL est valide - accepter plus de formats d'URL YouTube
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/.+$', url):
            messagebox.showerror("Erreur", "URL YouTube invalide")
            return

        self.status_var.set("Récupération des informations...")
        self.fetch_btn.config(state=tk.DISABLED)

        for item in self.tree.get_children():
            self.tree.delete(item)

        threading.Thread(target=self._fetch_formats_thread, args=(url,), daemon=True).start()

    def _fetch_formats_thread(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'ignoreerrors': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if 'entries' in info and len(info.get('entries', [])) > 0:
                    self.is_playlist = True
                    self.playlist_videos = info.get('entries', [])
                    self.current_playlist_index = 0

                    if self.playlist_videos and len(self.playlist_videos) > 0:
                        first_video = self.playlist_videos[0]
                        video_url = first_video.get('url') or first_video.get('webpage_url')

                        if video_url:
                            with yt_dlp.YoutubeDL({'quiet': True}) as ydl2:
                                self.video_info = ydl2.extract_info(video_url, download=False)
                                self.formats = self.video_info.get('formats', [])

                    self.root.after(0, self._update_video_info)
                    self.root.after(0, self._update_formats_list)
                    self.root.after(0, self._enable_playlist_controls)
                else:
                    self.is_playlist = False
                    self.playlist_videos = []
                    self.video_info = info
                    self.formats = info.get('formats', [])

                    self.root.after(0, self._update_video_info)
                    self.root.after(0, self._update_formats_list)
                    self.root.after(0, self._disable_playlist_controls)
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Erreur: {str(e)}"))

    def _update_playlist_info(self, playlist_info):
        """Met à jour l'interface avec les informations de la playlist"""
        self.playlist_frame.pack(fill=tk.X, pady=10, after=self.url_entry.master)

        self.playlist_title_var.set(f"Playlist: {playlist_info.get('title', 'Inconnue')}")
        self.playlist_count_var.set(f"Nombre de vidéos: {len(self.playlist_videos)}")
        self.current_video_var.set(f"Vidéo actuelle: {self.current_playlist_index + 1}/{len(self.playlist_videos)}")

        self.prev_video_btn.config(state=tk.DISABLED if self.current_playlist_index == 0 else tk.NORMAL)
        self.next_video_btn.config(
            state=tk.DISABLED if self.current_playlist_index >= len(self.playlist_videos) - 1 else tk.NORMAL)

    def load_next_playlist_video(self):
        """Charge la vidéo suivante dans la playlist"""
        if not self.is_playlist or not self.playlist_videos:
            return

        if self.current_playlist_index < len(self.playlist_videos) - 1:
            self.current_playlist_index += 1
            self._load_playlist_video_at_index(self.current_playlist_index)

    def load_previous_playlist_video(self):
        """Charge la vidéo précédente dans la playlist"""
        if not self.is_playlist or not self.playlist_videos:
            return

        if self.current_playlist_index > 0:
            self.current_playlist_index -= 1
            self._load_playlist_video_at_index(self.current_playlist_index)

    def _load_playlist_video_at_index(self, index):
        """Charge la vidéo à l'index spécifié dans la playlist"""
        if not self.is_playlist or index < 0 or index >= len(self.playlist_videos):
            return

        self.status_var.set(f"Chargement de la vidéo {index + 1}/{len(self.playlist_videos)}...")

        self.prev_video_btn.config(state=tk.DISABLED)
        self.next_video_btn.config(state=tk.DISABLED)
        self.download_all_btn.config(state=tk.DISABLED)
        self.fetch_btn.config(state=tk.DISABLED)

        for item in self.tree.get_children():
            self.tree.delete(item)

        video = self.playlist_videos[index]
        video_url = video.get('url') or video.get('webpage_url')

        if not video_url:
            self._show_error("URL de vidéo invalide dans la playlist")
            return

        threading.Thread(target=self._load_playlist_video_thread, args=(video_url, index), daemon=True).start()

    def _load_playlist_video_thread(self, url, index):
        """Charge les détails d'une vidéo de playlist dans un thread séparé"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                self.video_info = ydl.extract_info(url, download=False)
                self.formats = self.video_info.get('formats', [])

                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, self._update_video_info)
                self.root.after(0, self._update_formats_list)
                self.root.after(0, lambda: self._update_playlist_controls(index))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Erreur: {str(e)}"))

    def _update_playlist_controls(self, index):
        """Met à jour les contrôles de playlist après le chargement d'une vidéo"""
        playlist_length = len(self.playlist_videos)

        self.status_var.set(f"Vidéo {index + 1}/{playlist_length} chargée")

        self.root.title(f"My-Tube - Playlist ({index + 1}/{playlist_length})")

        # Activer/désactiver les boutons de navigation
        self.prev_video_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.next_video_btn.config(state=tk.NORMAL if index < playlist_length - 1 else tk.DISABLED)
        self.download_all_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)

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

            height = f.get('height', 0)
            width = f.get('width', 0)
            if height and width:
                resolution = f"{width}x{height}"
            elif height:
                resolution = f"{height}p"
            else:
                resolution = "Audio uniquement"

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

        if self.download_active:
            messagebox.showinfo("Information", "Un téléchargement est déjà en cours")
            return

        item = self.tree.item(selected[0])
        format_id = item['values'][0]
        url = self.url_entry.get().strip()

        if self.is_playlist and self.current_playlist_index < len(self.playlist_videos):
            video = self.playlist_videos[self.current_playlist_index]
            url = video.get('webpage_url') or video.get('url')

        self._reset_download_stats()
        self.status_var.set("Préparation du téléchargement...")
        self.download_btn.config(state=tk.DISABLED)
        self.fetch_btn.config(state=tk.DISABLED)

        self.download_stats_frame.pack(fill=tk.X, pady=5, before=self.status_label.master)

        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

        self.download_active = True
        self.download_cancelled = False

        self.download_thread = threading.Thread(target=self._download_thread, args=(url, format_id), daemon=True)
        self.download_thread.start()

    def _download_thread(self, url, format_id):
        self.downloaded_filepath = None
        self.download_speeds = []
        start_time = time.time()

        try:
            def progress_hook(d):
                if self.download_cancelled:
                    raise Exception("Téléchargement annulé par l'utilisateur")

                if d['status'] == 'downloading':
                    # Stocker le chemin du fichier pour une utilisation ultérieure
                    if 'filename' in d:
                        self.downloaded_filepath = d['filename']

                    current_time = time.time()

                    # Récupérer les données de progression
                    percent_str = d.get('_percent_str', '0%')
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)

                    self.current_download_size = downloaded_bytes
                    if total_bytes > 0:
                        self.total_download_size = total_bytes

                    if speed:
                        self.download_speeds.append(speed)
                        if len(self.download_speeds) > 5:
                            self.download_speeds.pop(0)

                    try:
                        p_float = float(percent_str.replace('%', ''))
                        self.root.after(0, lambda p=p_float: (self.progress_var.set(p), self.root.update_idletasks()))
                    except (ValueError, AttributeError):
                        pass

                    self.root.after(0, lambda: self._update_download_stats(
                        percent_str,
                        downloaded_bytes,
                        total_bytes,
                        current_time - start_time,
                        eta
                    ))
                elif d['status'] == 'finished':
                    self.downloaded_filepath = d.get('filename')
                    self.root.after(0, lambda: self.status_var.set("Finalisation..."))

            timestamp = time.strftime("%Y%m%d_%H%M%S")

            ydl_opts = {
                'format': f"{format_id}+bestaudio[ext=m4a]/best",
                'outtmpl': os.path.join(self.download_path, f'%(title)s_{timestamp}.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if not self.download_cancelled:
                self.root.after(0, lambda: self._download_complete())
            else:
                self.root.after(0, lambda: self._download_cancelled())

        except Exception as e:
            if self.download_cancelled:
                self.root.after(0, lambda: self._download_cancelled())
            else:
                self.root.after(0, lambda: self._show_error(f"Erreur de téléchargement: {str(e)}"))
        finally:
            self.download_active = False

    def _download_complete(self):
        """Appelé lorsque le téléchargement est terminé avec succès"""
        self.status_var.set("Téléchargement terminé ! 🎉")
        self.download_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)
        self.progress_var.set(100)

        self.download_stats_frame.pack_forget()
        self.cancel_btn.pack_forget()

        self.download_active = False
        self.download_cancelled = False

        messagebox.showinfo(
            "Succès",
            f"Téléchargement terminé avec succès !\n\nLe fichier a été enregistré dans :\n{self.download_path}"
        )

        if messagebox.askyesno("Ouvrir le dossier", "Voulez-vous ouvrir le dossier de destination ?"):
            os.startfile(self.download_path) if os.name == 'nt' else os.system(f'xdg-open "{self.download_path}"')

    def _download_cancelled(self):
        """Appelé lorsque le téléchargement d'une seule vidéo est annulé"""
        self.download_active = False

        self.download_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)

        self.cancel_btn.config(state=tk.NORMAL)

        self.cancel_btn.pack_forget()
        self.download_stats_frame.pack_forget()

        self.progress_var.set(0)

        messagebox.showinfo("Téléchargement annulé",
                           "Le téléchargement a été annulé par l'utilisateur.")

        self.status_var.set("Téléchargement annulé")

        self.download_cancelled = False

    def _update_download_stats(self, percent, downloaded_bytes, total_bytes, elapsed, eta):
        """Met à jour toutes les statistiques de téléchargement en une seule fois"""
        # Pourcentage
        self.percent_var.set(percent)

        if downloaded_bytes and total_bytes:
            size_str = f"{humanize.naturalsize(downloaded_bytes)} / {humanize.naturalsize(total_bytes)}"
        elif downloaded_bytes:
            size_str = f"{humanize.naturalsize(downloaded_bytes)} / ???"
        else:
            size_str = "-- / --"
        self.download_size_var.set(size_str)

        # Vitesse moyenne
        avg_speed = sum(self.download_speeds) / len(self.download_speeds) if self.download_speeds else 0
        speed_str = humanize.naturalsize(avg_speed).replace(' ', '') + "/s" if avg_speed else "-- KB/s"
        self.download_speed_var.set(speed_str)

        # Temps écoulé
        elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed))
        self.elapsed_time_var.set(elapsed_str)

        # Temps restant
        eta_str = time.strftime("%M:%S", time.gmtime(eta)) if eta else "--:--"
        self.download_eta_var.set(eta_str)

        status_icons = ["⏳", "📥", "🔽", "⬇️"]
        icon = status_icons[int(elapsed) % len(status_icons)]
        self.status_var.set(f"{icon} Téléchargement en cours... {percent}")

        self.root.title(f"My-Tube - {percent}")

    def _reset_download_stats(self):
        """Réinitialise les statistiques de téléchargement"""
        self.progress_var.set(0)
        self.percent_var.set("0%")
        self.download_size_var.set("-- / --")
        self.download_speed_var.set("-- KB/s")
        self.elapsed_time_var.set("00:00")
        self.download_eta_var.set("--:--")
        self.downloaded_filepath = None
        self.download_speeds = []

    def download_playlist(self):
        """Télécharge toutes les vidéos de la playlist"""
        if not self.is_playlist or not self.playlist_videos:
            messagebox.showerror("Erreur", "Aucune playlist détectée")
            return

        if self.download_active:
            messagebox.showinfo("Information", "Un téléchargement est déjà en cours")
            return

        total_videos = len(self.playlist_videos)
        if not messagebox.askyesno("Confirmation",
                                   f"Voulez-vous télécharger les {total_videos} vidéos de cette playlist?\n\n"
                                   f"Les vidéos seront téléchargées dans: {self.download_path}"):
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Erreur", "Veuillez sélectionner un format pour le téléchargement")
            return

        item = self.tree.item(selected[0])
        format_id = item['values'][0]

        self.download_btn.config(state=tk.DISABLED)
        self.fetch_btn.config(state=tk.DISABLED)
        self.download_all_btn.config(state=tk.DISABLED)
        self.prev_video_btn.config(state=tk.DISABLED)
        self.next_video_btn.config(state=tk.DISABLED)

        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

        self.playlist_download_active = True
        self.current_playlist_download_index = 0
        self.download_active = True
        self.download_cancelled = False
        self.successful_downloads = 0

        self._download_next_playlist_video(format_id)

    def _download_next_playlist_video(self, format_id):
        """Télécharge la prochaine vidéo de la playlist"""
        if self.download_cancelled:
            self.root.after(0, self._playlist_download_cancelled)
            return

        if self.current_playlist_download_index >= len(self.playlist_videos):
            self.root.after(0, self._playlist_download_complete)
            return

        video = self.playlist_videos[self.current_playlist_download_index]
        video_url = video.get('webpage_url') or video.get('url')
        video_title = video.get('title', f"Vidéo {self.current_playlist_download_index + 1}")

        self.status_var.set(
            f"Téléchargement de la playlist ({self.current_playlist_download_index + 1}/{len(self.playlist_videos)}): {video_title}")

        self._reset_download_stats()

        self.download_stats_frame.pack(fill=tk.X, pady=5, before=self.status_label.master)

        threading.Thread(target=self._download_playlist_video_thread,
                         args=(video_url, format_id, video_title),
                         daemon=True).start()

    def _download_playlist_video_thread(self, url, format_id, video_title):
        """Télécharge une vidéo de la playlist dans un thread séparé"""
        self.downloaded_filepath = None
        self.download_speeds = []
        start_time = time.time()
        success = False

        try:
            if self.download_cancelled:
                return

            def progress_hook(d):
                if self.download_cancelled:
                    raise Exception("Téléchargement annulé par l'utilisateur")

                if d['status'] == 'downloading':
                    if 'filename' in d:
                        self.downloaded_filepath = d['filename']

                    current_time = time.time()

                    percent_str = d.get('_percent_str', '0%')
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)

                    self.current_download_size = downloaded_bytes
                    if total_bytes > 0:
                        self.total_download_size = total_bytes

                    if speed:
                        self.download_speeds.append(speed)
                        if len(self.download_speeds) > 5:
                            self.download_speeds.pop(0)

                    try:
                        p_float = float(percent_str.replace('%', ''))
                        self.root.after(0, lambda p=p_float: (self.progress_var.set(p), self.root.update_idletasks()))
                    except (ValueError, AttributeError):
                        pass

                    self.root.after(0, lambda: self._update_download_stats(
                        percent_str,
                        downloaded_bytes,
                        total_bytes,
                        current_time - start_time,
                        eta
                    ))
                elif d['status'] == 'finished':
                    self.downloaded_filepath = d.get('filename')
                    self.root.after(0, lambda: self.status_var.set("Finalisation..."))

            timestamp = time.strftime("%Y%m%d_%H%M%S")

            ydl_opts = {
                'format': f"{format_id}+bestaudio[ext=m4a]/best",
                'outtmpl': os.path.join(self.download_path, f'%(title)s_{timestamp}.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
            }

            if not self.download_cancelled:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    success = True
                    self.successful_downloads += 1

        except Exception as e:
            if self.download_cancelled:
                # Ne rien faire si c'est une annulation
                pass
            else:
                self.root.after(0, lambda: self.status_var.set(f"Erreur: {str(e)}"))

        finally:
            if self.download_cancelled:
                return

            self.current_playlist_download_index += 1

            self.root.after(500, lambda: self._download_next_playlist_video(format_id))

    def _enable_playlist_controls(self):
        """Active les contrôles de playlist"""
        playlist_length = len(self.playlist_videos)
        self.status_var.set(f"Playlist détectée: {playlist_length} vidéos")

        if hasattr(self, 'download_all_btn'):
            self.download_all_btn.config(state=tk.NORMAL)

        if hasattr(self, 'prev_video_btn'):
            self.prev_video_btn.config(state=tk.DISABLED)

        if hasattr(self, 'next_video_btn'):
            self.next_video_btn.config(state=tk.NORMAL if playlist_length > 1 else tk.DISABLED)

        self.root.title(f"My-Tube - Playlist ({self.current_playlist_index + 1}/{playlist_length})")

    def _disable_playlist_controls(self):
        """Désactive les contrôles de playlist"""
        if hasattr(self, 'download_all_btn'):
            self.download_all_btn.config(state=tk.DISABLED)

        if hasattr(self, 'prev_video_btn'):
            self.prev_video_btn.config(state=tk.DISABLED)

        if hasattr(self, 'next_video_btn'):
            self.next_video_btn.config(state=tk.DISABLED)

        self.root.title("My-Tube")

    def cancel_download(self):
        """Annule le téléchargement en cours"""
        if not self.download_active:
            return

        self.download_cancelled = True

        self.cancel_btn.config(state=tk.DISABLED)

        if self.playlist_download_active:
            self.status_var.set("Annulation du téléchargement de la playlist...")
            self.playlist_download_active = False
            self.root.after(100, self._playlist_download_cancelled)
        else:
            self.status_var.set("Annulation du téléchargement...")
            self.root.after(100, self._download_cancelled)

    def _playlist_download_complete(self):
        """Appelé lorsque le téléchargement de la playlist est terminé"""
        self.playlist_download_active = False
        self.download_active = False

        self.download_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)
        self.download_all_btn.config(state=tk.NORMAL)
        self.prev_video_btn.config(state=tk.NORMAL if self.current_playlist_index > 0 else tk.DISABLED)
        self.next_video_btn.config(
            state=tk.NORMAL if self.current_playlist_index < len(self.playlist_videos) - 1 else tk.DISABLED)

        self.cancel_btn.pack_forget()
        self.download_stats_frame.pack_forget()

        messagebox.showinfo("Succès", f"Téléchargement de la playlist terminé !\n\n"
                                      f"{self.successful_downloads} vidéos sur {self.total_playlist_videos} ont été téléchargées dans :\n"
                                      f"{self.download_path}")

        self.status_var.set("Prêt")
        self.progress_var.set(0)

    def _playlist_download_cancelled(self):
        """Appelé lorsque le téléchargement de la playlist est annulé"""
        self.playlist_download_active = False
        self.download_active = False
        self.download_cancelled = True

        self.download_btn.config(state=tk.NORMAL)
        self.fetch_btn.config(state=tk.NORMAL)
        self.download_all_btn.config(state=tk.NORMAL)
        self.prev_video_btn.config(state=tk.NORMAL if self.current_playlist_index > 0 else tk.DISABLED)
        self.next_video_btn.config(
            state=tk.NORMAL if self.current_playlist_index < len(self.playlist_videos) - 1 else tk.DISABLED)

        self.cancel_btn.config(state=tk.NORMAL)

        self.cancel_btn.pack_forget()
        self.download_stats_frame.pack_forget()

        total = getattr(self, 'total_playlist_videos', len(self.playlist_videos))
        messagebox.showinfo("Téléchargement annulé",
                            f"Le téléchargement de la playlist a été annulé.\n"
                            f"{self.successful_downloads} vidéos sur {total} ont été téléchargées avant l'annulation.")

        self.status_var.set("Téléchargement annulé")
        self.progress_var.set(0)

        self.download_cancelled = False
