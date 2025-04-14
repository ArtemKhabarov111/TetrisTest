from os import path, getcwd
from random import choice
import db_manager

# components
from game import Game
from preview import Preview
from score import Score
from settings import *


class Main:
    def __init__(self):
        # general
        pygame.init()
        db_manager.initialize_db()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Singleplayer Tetris")

        # shapes
        self.next_shapes = [choice(list(TETROMINOS.keys())) for _ in range(3)]

        # components
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()

        # audio
        self.music = pygame.mixer.Sound(path.join(getcwd(), 'sounds', 'tetris_original.mp3'))
        self.music.set_volume(0.1)
        self.music.play(-1, fade_ms=500)

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.music.fadeout(1000)  # Smoothly fade out music
                    return

            # display
            self.display_surface.fill(GRAY)

            # components
            self.game.run()
            if self.game.exit_to_menu:
                self.music.fadeout(1000)
                return

            self.score.run()
            self.preview.run(self.next_shapes)

            # game update
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    main = Main()
    main.run()
