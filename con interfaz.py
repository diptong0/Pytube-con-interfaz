import tkinter as tk
from tkinter import ttk, messagebox
from pytube import Playlist, YouTube
from pytube.exceptions import VideoUnavailable, AgeRestrictedError
import threading
import os



#cambiar carpeta destino


destino = 'musica'

class DownloadThread(threading.Thread):
    def __init__(self, url, formato, is_playlist):
        super().__init__()
        self.url = url
        self.formato = formato
        self.is_playlist = is_playlist
        self.cancelled = False

    def run(self):
        try:
            if self.is_playlist:
                self.download_playlist()
            else:
                self.download_video()
        except Exception as e:
            download_status.config(text=f"Error: {str(e)}")

    def download_playlist(self):
        p = Playlist(self.url)
        playlist_title.config(text=f'Descargando: {p.title}')
        for video_url in p.video_urls:
            if self.cancelled:
                print("Descarga de la playlist cancelada.")
                break

            try:
                yt = YouTube(video_url)
            except (VideoUnavailable, AgeRestrictedError):
                print(f'Video {video_url} is unavailable, skipping.')
            else:
                print(f'Downloading video: {video_url} {yt.title} - Formato: {self.formato}')
                self.download_video_format(yt)

        if not self.cancelled:
            download_status.config(text=f"Descarga de la playlist finalizada: {p.title}")

    def download_video(self):
        yt = YouTube(self.url)
        print(f'Downloading video: {self.url} {yt.title} - Formato: {self.formato}')
        self.download_video_format(yt)
        download_status.config(text=f"Descarga del video finalizada: {yt.title}")

    def download_video_format(self, yt):
        try:
            if self.formato == "mp3":
                audio_stream = yt.streams.filter(only_audio=True).first()
                audio_file_path = destino + "\\" + audio_stream.default_filename
                if os.path.exists(audio_file_path):
                    print(f"El archivo {audio_file_path} ya existe, saltando la descarga.")
                    return
                audio_stream.download(destino)

                # Convertir el archivo descargado a formato MP3
                mp3_file_path = audio_file_path.replace(".mp4", ".mp3")
                if os.path.exists(mp3_file_path):
                    print(f"El archivo {mp3_file_path} ya existe, eliminando la versión MP4.")
                    os.remove(audio_file_path)  # Eliminar la versión MP4
                else:
                    os.rename(audio_file_path, mp3_file_path)
            else:
                video_stream = yt.streams.filter(file_extension=self.formato).first()
                video_file_path = destino + "\\" + video_stream.default_filename
                if os.path.exists(video_file_path):
                    print(f"El archivo {video_file_path} ya existe, saltando la descarga.")
                    return
                video_stream.download(destino)

        except AgeRestrictedError:
            print(
                f"El video {yt.title} tiene restricciones de edad y no se puede descargar sin iniciar sesión en YouTube.")


def download_playlist():
    global download_thread
    url = playlist_url_entry.get()
    formato = playlist_formato_var.get()

    if download_thread and download_thread.is_alive():
        download_thread.cancelled = True
        download_thread.join()

    download_thread = DownloadThread(url, formato, True)
    download_thread.start()

def download_video():
    global download_thread
    url = video_url_entry.get()
    formato = video_formato_var.get()

    if download_thread and download_thread.is_alive():
        download_thread.cancelled = True
        download_thread.join()

    download_thread = DownloadThread(url, formato, False)
    download_thread.start()

def exit_application():
    ventana.destroy()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Descargador de YouTube")

# Crear pestañas
notebook = ttk.Notebook(ventana)
playlist_tab = ttk.Frame(notebook)
video_tab = ttk.Frame(notebook)

notebook.add(playlist_tab, text='Playlist')
notebook.add(video_tab, text='Video')
notebook.pack(fill='both', expand=True)

# Crear y colocar widgets (elementos) en la pestaña de playlist
playlist_url_label = tk.Label(playlist_tab, text="URL de la Playlist:")
playlist_url_label.grid(row=0, column=0, padx=10, pady=10)

playlist_url_entry = tk.Entry(playlist_tab, width=50)
playlist_url_entry.grid(row=0, column=1, padx=10, pady=10)

playlist_formato_label = tk.Label(playlist_tab, text="Formato de Descarga:")
playlist_formato_label.grid(row=1, column=0, padx=10, pady=10)

playlist_formato_var = tk.StringVar(playlist_tab)
playlist_formato_var.set("mp4")  # Formato predeterminado
playlist_formato_menu = tk.OptionMenu(playlist_tab, playlist_formato_var, "mp4", "mp3", "720p", "1080p")
playlist_formato_menu.grid(row=1, column=1, padx=10, pady=10)

playlist_download_button = tk.Button(playlist_tab, text="Descargar Playlist", command=download_playlist)
playlist_download_button.grid(row=2, column=0, columnspan=2, pady=10)

# Etiqueta de título para la playlist
playlist_title = tk.Label(playlist_tab, text="")
playlist_title.grid(row=3, column=0, columnspan=2, pady=10)

# Crear y colocar widgets (elementos) en la pestaña de video
video_url_label = tk.Label(video_tab, text="URL del Video:")
video_url_label.grid(row=0, column=0, padx=10, pady=10)

video_url_entry = tk.Entry(video_tab, width=50)
video_url_entry.grid(row=0, column=1, padx=10, pady=10)

video_formato_label = tk.Label(video_tab, text="Formato de Descarga:")
video_formato_label.grid(row=1, column=0, padx=10, pady=10)

video_formato_var = tk.StringVar(video_tab)
video_formato_var.set("mp4")  # Formato predeterminado
video_formato_menu = tk.OptionMenu(video_tab, video_formato_var, "mp4", "mp3", "720p", "1080p")
video_formato_menu.grid(row=1, column=1, padx=10, pady=10)

video_download_button = tk.Button(video_tab, text="Descargar Video", command=download_video)
video_download_button.grid(row=2, column=0, columnspan=2, pady=10)

# Etiqueta de título para el video
video_title = tk.Label(video_tab, text="")
video_title.grid(row=3, column=0, columnspan=2, pady=10)

# Etiqueta de estado
download_status = tk.Label(ventana, text="")
download_status.pack(pady=10)

# Crear botón para salir
exit_button = tk.Button(ventana, text="Salir", command=exit_application)
exit_button.pack(pady=10)

# Variable para almacenar el hilo de descarga
download_thread = None

# Iniciar el bucle principal de la interfaz gráfica
ventana.mainloop()
