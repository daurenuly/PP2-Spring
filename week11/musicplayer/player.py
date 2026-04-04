import pygame
import sys
import os


class MusicPlayer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.WIDTH, self.HEIGHT = 600, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Music Player")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        tracks_path = os.path.join(BASE_DIR, "tracks")

        self.playlist = self.load_tracks("C:\\Users\\abyla\\OneDrive\\Документы\\PP2\\week11\\musicplayer\\tracks")
        self.current_index = 0

        self.is_playing = False
        self.track_length = 0  # длительность трека

    def load_tracks(self, folder):
        tracks = []
        for file in os.listdir(folder):
            if file.endswith(".mp3") or file.endswith(".wav"):
                tracks.append(os.path.join(folder, file))
        return tracks

    def play(self):
        if not self.playlist:
            return

        track = self.playlist[self.current_index]

        pygame.mixer.music.load(track)
        pygame.mixer.music.play()

        sound = pygame.mixer.Sound(track)
        self.track_length = int(sound.get_length())

        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def draw_progress_bar(self, pos):
        bar_x = 20
        bar_y = 180
        bar_width = 560
        bar_height = 10

        # фон
        pygame.draw.rect(self.screen, (80, 80, 80),
                         (bar_x, bar_y, bar_width, bar_height))

        if self.track_length > 0:
            progress = pos / self.track_length
            progress_width = int(bar_width * progress)

            pygame.draw.rect(self.screen, (0, 200, 0),
                             (bar_x, bar_y, progress_width, bar_height))

    def draw_ui(self):
        self.screen.fill((30, 30, 30))

        if self.playlist:
            track_name = os.path.basename(self.playlist[self.current_index])
        else:
            track_name = "No tracks"

        text = self.font.render(f"Track: {track_name}", True, (255, 255, 255))
        self.screen.blit(text, (20, 40))

        status = "Playing" if self.is_playing else "Stopped"
        status_text = self.font.render(f"Status: {status}", True, (200, 200, 200))
        self.screen.blit(status_text, (20, 80))

        pos = max(0, pygame.mixer.music.get_pos() // 1000)

        time_text = self.font.render(f"Time: {pos}s / {self.track_length}s",
                                     True, (200, 200, 200))
        self.screen.blit(time_text, (20, 120))

        self.draw_progress_bar(pos)

        # управление
        controls = [
            "P = Play",
            "S = Stop",
            "N = Next",
            "B = Back",
            "Q = Quit"
        ]

        for i, c in enumerate(controls):
            txt = self.font.render(c, True, (150, 150, 150))
            self.screen.blit(txt, (20, 220 + i * 30))

    def handle_keys(self, event):
        if event.key == pygame.K_p:
            self.play()

        elif event.key == pygame.K_s:
            self.stop()

        elif event.key == pygame.K_n:
            self.next_track()

        elif event.key == pygame.K_b:
            self.prev_track()

        elif event.key == pygame.K_q:
            pygame.quit()
            sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    self.handle_keys(event)

            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(30)