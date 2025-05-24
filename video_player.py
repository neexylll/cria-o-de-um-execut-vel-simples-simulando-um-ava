import tkinter as tk
import vlc
import os

class VideoPlayer(tk.Toplevel):
    def __init__(self, video_path):
        super().__init__()
        self.title("Video Player")
        self.geometry("640x480")

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.video_frame = tk.Frame(self)
        self.video_frame.pack(fill=tk.BOTH, expand=1)

        self.player.set_hwnd(self.video_frame.winfo_id())  # Windows
        

        media = self.instance.media_new(video_path)
        self.player.set_media(media)
        self.player.play()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.player.stop()
        self.destroy()

def criar_interface():
    root = tk.Tk()
    root.title("Seleção de Temas e Vídeos")
    root.geometry("400x600")

    temas = {
        "Tema 1": ["videos/tema1_video1.mp4", "videos/tema1_video2.mp4", "videos/tema1_video3.mp4"],
        "Tema 2": ["videos/tema2_video1.mp4", "videos/tema2_video2.mp4", "videos/tema2_video3.mp4"],
        "Tema 3": ["videos/tema3_video1.mp4", "videos/tema3_video2.mp4", "videos/tema3_video3.mp4"],
        "Tema 4": ["videos/tema4_video1.mp4", "videos/tema4_video2.mp4", "videos/tema4_video3.mp4"],
        "Tema 5": ["videos/tema5_video1.mp4", "videos/tema5_video2.mp4", "videos/tema5_video3.mp4"],
    }

    for tema, lista_videos in temas.items():
        frame_tema = tk.LabelFrame(root, text=tema, padx=10, pady=10)
        frame_tema.pack(fill="both", expand=True, padx=10, pady=5)

        for i, caminho_video in enumerate(lista_videos, start=1):
            if not os.path.isfile(caminho_video):
                label_erro = tk.Label(frame_tema, text=f"Arquivo não encontrado: {caminho_video}", fg="red")
                label_erro.pack(anchor="w")
                continue

            btn = tk.Button(frame_tema, text=f"Vídeo {i}", 
                            command=lambda c=caminho_video: VideoPlayer(c))
            btn.pack(fill="x", pady=2)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
