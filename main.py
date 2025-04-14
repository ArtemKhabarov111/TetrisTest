import os
import sys
from os import path, getcwd
import settings  # Import the settings module to update SKIN
from settings import *  # Import constants like PADDING, BLUE, GREEN, GRAY, OUTLINE_COLOR, etc.

GAME_WIDTH = 660
GAME_HEIGHT = 840

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")
clock = pygame.time.Clock()

# Global variable for currently equipped skin (default to 1)
current_skin = 1
settings.SKIN = current_skin  # ensure that settings.SKIN is updated


# A simple button class for the menu
class Main:
    def __init__(self, text, rect, color=BLUE, hover_color=GREEN):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(path.join(getcwd(), "graphics", "Caveat-Bold.ttf"), 48)
        self.text_surf = self.font.render(text, True, "WHITE")
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# Create menu buttons with dimensions and positioning
button_width = 300
button_height = 90
singleplayer_button = Main("Singleplayer", (PADDING, PADDING, button_width, button_height))
multiplayer_button = Main("Multiplayer", (PADDING * 2 + button_width, PADDING, button_width, button_height))


# A class to represent a skin option with its image and equip button
class SkinOption:
    def __init__(self, skin_id, image, cell_rect):
        self.skin_id = skin_id
        self.image = image
        self.cell_rect = cell_rect
        # Center the image in the cell; image size is 280x160
        self.image_rect = self.image.get_rect(center=cell_rect.center)
        # Create an equip button in the bottom-right corner of the image.
        button_w, button_h = 80, 40
        self.button_rect = pygame.Rect(0, 0, button_w, button_h)
        # Offset the button a few pixels from the image's edge.
        self.button_rect.bottomright = (self.image_rect.right, self.image_rect.bottom)
        self.font = pygame.font.Font(path.join(getcwd(), "graphics", "Caveat-Bold.ttf"), 24)

    def draw(self, surface):
        # Draw the skin image
        surface.blit(self.image, self.image_rect)
        # Choose button color: GREEN if equipped, else BLUE.
        button_color = GREEN if self.skin_id == current_skin else BLUE
        pygame.draw.rect(surface, button_color, self.button_rect)
        # Button text: "Equipped" if active, else "Equip"
        text = "Equipped" if self.skin_id == current_skin else "Equip"
        text_surf = self.font.render(text, True, "WHITE")
        text_rect = text_surf.get_rect(center=self.button_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Return True if the equip button was clicked.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False


# Global list to store skin options; they will be loaded once
skin_options = []


def load_skin_options(top_field_rect):
    options = []
    # Define available skin IDs (adjust if you have more skins)
    available_skins = [1, 2, 3, 4]
    # Calculate cell size for a 2x2 grid inside top_field_rect
    cell_width = top_field_rect.width / 2
    cell_height = top_field_rect.height / 2

    for idx, skin_id in enumerate(available_skins):
        row = idx // 2
        col = idx % 2
        cell_x = top_field_rect.x + col * cell_width
        cell_y = top_field_rect.y + row * cell_height
        cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
        # Load the skin image
        image_path = path.join(getcwd(), "graphics", "packs", f"pack{skin_id}.png")
        skin_image = pygame.image.load(image_path).convert_alpha()
        # Scale the image to 280x160
        skin_image = pygame.transform.scale(skin_image, (280, 160))
        option = SkinOption(skin_id, skin_image, cell_rect)
        options.append(option)
    return options


def draw_fields(surface):
    # Calculate the area below the menu buttons.
    fields_area_top = PADDING + button_height + PADDING
    fields_area_height = GAME_HEIGHT - fields_area_top - PADDING

    # We want two fields with padding between them.
    field_width = GAME_WIDTH - 2 * PADDING
    field_height = (fields_area_height - PADDING) // 2

    # Define the top and bottom field rectangles.
    top_field_rect = pygame.Rect(PADDING, fields_area_top, field_width, field_height + 40)
    bottom_field_rect = pygame.Rect(PADDING, fields_area_top + field_height + PADDING * 3, field_width, field_height-40)

    # Draw the top field (black with a white outline)
    pygame.draw.rect(surface, "black", top_field_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, top_field_rect, 2)

    # Draw the bottom field (black with a white outline)
    pygame.draw.rect(surface, "black", bottom_field_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, bottom_field_rect, 2)

    return top_field_rect, bottom_field_rect


def game_loop():
    global screen, current_skin, skin_options
    state = "menu"

    while True:
        if state == "menu":
            screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
            state = run_main_menu()

        elif state == "singleplayer":
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            from singleplayer import Main as SingleplayerMain
            main_game = SingleplayerMain()
            main_game.run()  # The game will now use settings.SKIN to determine the skin.
            state = "menu"  # Return to menu after exiting
            pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")

        elif state == "multiplayer":
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            from multiplayer import Multiplayer
            main_game = Multiplayer()
            main_game.run()  # The game will now use settings.SKIN to determine the skin.
            state = "menu"  # Return to menu after exiting
            pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")


def run_main_menu():
    global current_skin, skin_options
    while True:
        screen.fill(GRAY)
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if singleplayer_button.is_clicked(event):
                return "singleplayer"
            if multiplayer_button.is_clicked(event):
                return "multiplayer"
            # Check if any skin option's equip button was clicked
            for option in skin_options:
                if option.handle_event(event):
                    current_skin = option.skin_id
                    settings.SKIN = current_skin  # Update the settings variable so in-game skin changes.

        # Draw the menu buttons
        singleplayer_button.draw(screen)
        multiplayer_button.draw(screen)

        # Draw the additional fields
        top_field_rect, bottom_field_rect = draw_fields(screen)

        # If skin options are not loaded yet, load them into a 2x2 grid inside the top field.
        if not skin_options:
            skin_options = load_skin_options(top_field_rect)

        # Draw each skin option (image + equip button)
        for option in skin_options:
            option.draw(screen)

        # (Optional) You can add content to the bottom field if needed.

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    game_loop()
