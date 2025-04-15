from settings import *
from os import path, getcwd


class Score:
    def __init__(self):
        # Create a surface for displaying the score, level, and lines
        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING))
        self.rect = self.surface.get_rect(bottomright=(WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING))
        self.display_surface = pygame.display.get_surface()

        # Font
        self.font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 30)

        # Increment
        self.increment_height = self.surface.get_height() / 3

        # Data
        self.score = 0
        self.level = 1
        self.lines = 0

    def display_text(self, pos, text):
        # Render and display text on the score surface
        text_surface = self.font.render(f"{text[0]}: {text[1]}", True, "white")
        text_rect = text_surface.get_rect(center=pos)
        self.surface.blit(text_surface, text_rect)

    def run(self):
        self.surface.fill("black")
        for i, text in enumerate([("Score", self.score), ("Level", self.level), ("Lines", self.lines)]):
            x = self.surface.get_width() // 2
            y = self.increment_height / 2 + i * self.increment_height
            self.display_text((x, y), text)

            # Blit the score surface to the main display
            self.display_surface.blit(self.surface, self.rect)

            # Draw a border around the score area
            pygame.draw.rect(self.display_surface, OUTLINE_COLOR, self.rect, 2)
