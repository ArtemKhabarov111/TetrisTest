import settings

from settings import *
from os import path, getcwd
from pygame.image import load


class Preview:
    def __init__(self):
        # Surface to display next pieces
        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION))
        self.rect = self.surface.get_rect(topright=(WINDOW_WIDTH - PADDING, PADDING))
        self.display_surface = pygame.display.get_surface()

        # Load images for all tetromino shapes based on the selected skin
        self.shape_surfaces = {shape: load(path.join(getcwd(), "graphics", f"skin{settings.SKIN}", f"{shape}.png"))
                               .convert_alpha() for shape in TETROMINOS.keys()}

        # Vertical spacing between shapes preview
        self.increment_height = self.surface.get_height() / 3

    def display_pieces(self, shapes):
        for i, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            rect = shape_surface.get_rect(center=(x, y))
            self.surface.blit(shape_surface, rect)

    def run(self, next_shapes):
        self.surface.fill("black")
        self.display_pieces(next_shapes)

        # Blit the score surface to the main display
        self.display_surface.blit(self.surface, self.rect)

        # Draw a border around the preview area
        pygame.draw.rect(self.display_surface, OUTLINE_COLOR, self.rect, 2, 2)
