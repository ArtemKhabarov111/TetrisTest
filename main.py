import os
import sys
import sqlite3
import settings
import db_manager

from settings import *
from os import path, getcwd

# Define your database file
DB_FILE = 'tetris_records.db'

GAME_WIDTH = 660
GAME_HEIGHT = 840

pygame.init()
db_manager.initialize_db()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")
clock = pygame.time.Clock()

current_skin = 1  # Global variable for currently equipped skin
settings.SKIN = current_skin
leaderboard_scroll = 0


class Main:
    def __init__(self, text, rect, color=BLUE, hover_color=GREEN):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 48)
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


# Create menu buttons
button_width = 300
button_height = 90
singleplayer_button = Main("Singleplayer", (PADDING, PADDING, button_width, button_height))
multiplayer_button = Main("Multiplayer", (PADDING * 2 + button_width, PADDING, button_width, button_height))


class SkinOption:
    def __init__(self, skin_id, image, cell_rect):
        self.skin_id = skin_id
        self.image = image
        self.cell_rect = cell_rect

        # Center the image in the cell; image size is 280x160
        self.image_rect = self.image.get_rect(center=cell_rect.center)

        # Create an equip button in the bottomright corner of the image.
        button_w, button_h = 80, 40
        self.button_rect = pygame.Rect(0, 0, button_w, button_h)

        self.button_rect.bottomright = (self.image_rect.right, self.image_rect.bottom)
        self.font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 24)

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


# Global list to store skin options
skin_options = []


def load_skin_options(top_field_rect):
    options = []
    # Define available skin IDs
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

        # Load skin image
        image_path = path.join(getcwd(), "graphics", "packs", f"pack{skin_id}.png")
        skin_image = pygame.image.load(image_path).convert_alpha()
        option = SkinOption(skin_id, skin_image, cell_rect)
        options.append(option)
    return options


def draw_fields(surface):
    # Calculate the area below buttons
    fields_area_top = PADDING + button_height + PADDING
    fields_area_height = GAME_HEIGHT - fields_area_top - PADDING

    # Two fields with padding
    field_width = GAME_WIDTH - 2 * PADDING
    field_height = (fields_area_height - PADDING) // 2

    # Top and bottom fields
    top_field_rect = pygame.Rect(PADDING, fields_area_top, field_width, field_height + 40)
    bottom_field_rect = pygame.Rect(PADDING, fields_area_top + field_height + PADDING * 3, field_width, field_height-40)

    # Draw top field (black with a white outline)
    pygame.draw.rect(surface, "black", top_field_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, top_field_rect, 2)

    # Draw bottom field (black with a white outline)
    pygame.draw.rect(surface, "black", bottom_field_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, bottom_field_rect, 2)

    return top_field_rect, bottom_field_rect


def get_leaderboard():
    # return top 100 leaderboard records sorted by score
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, score, level, lines FROM leaderboard ORDER BY score DESC LIMIT 100")
    records = cursor.fetchall()
    conn.close()
    return records


def draw_leaderboard(surface, rect, scroll_offset):
    # Render leaderboard inside rectangle
    # Font
    title_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 36)
    header_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 30)
    row_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 24)

    # Get records
    records = get_leaderboard()

    columns = [
        {"header": "Place", "width": 80},
        {"header": "Username", "width": 200},
        {"header": "Score", "width": 120},
        {"header": "Level", "width": 100},
        {"header": "Lines", "width": 100},
    ]

    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    base_y = rect.y
    title_text = title_font.render("Leaderboard", True, "WHITE")
    title_rect = title_text.get_rect(center=(rect.centerx, base_y + 25))
    surface.blit(title_text, (title_rect.x, title_rect.y - scroll_offset))

    header_y = title_rect.bottom
    x_start = rect.x + 15  # Left margin for table columns

    # Draw headers for each column
    x_offset = x_start
    for col in columns:
        header_surf = header_font.render(col["header"], True, "WHITE")

        # Create a rectangle for the column area.
        col_rect = pygame.Rect(x_offset, header_y - scroll_offset, col["width"], header_surf.get_height())
        header_rect = header_surf.get_rect(center=col_rect.center)
        surface.blit(header_surf, header_rect)
        x_offset += col["width"]

    # Row parameters
    row_height = 40
    row_y = header_y + row_height  # Top position of the first row

    # Draw each row
    for idx, record in enumerate(records):
        username, score, level, lines = record
        place = str(idx + 1)
        row_values = [place, username, str(score), str(level), str(lines)]
        x_offset = x_start
        for i, val in enumerate(row_values):
            row_surf = row_font.render(val, True, "WHITE")
            col_width = columns[i]["width"]
            col_rect = pygame.Rect(x_offset, row_y - scroll_offset, col_width, row_surf.get_height())
            row_text_rect = row_surf.get_rect(center=col_rect.center)
            surface.blit(row_surf, row_text_rect)
            x_offset += col_width
        row_y += row_height

    surface.set_clip(prev_clip)

    # Return the total height of the drawn content
    total_height = row_y - base_y
    return total_height


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
            main_game.run()
            state = "menu"  # Return to menu after exiting
            pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")

        elif state == "multiplayer":
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            from multiplayer import Multiplayer
            main_game = Multiplayer()
            main_game.run()
            state = "menu"  # Return to menu after exiting
            pygame.display.set_caption("Tetris by IO-34 Artem Khabarov")


def run_main_menu():
    global current_skin, skin_options, leaderboard_scroll
    while True:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if singleplayer_button.is_clicked(event):
                return "singleplayer"
            if multiplayer_button.is_clicked(event):
                return "multiplayer"

            # Check skin option clicks.
            for option in skin_options:
                if option.handle_event(event):
                    current_skin = option.skin_id
                    settings.SKIN = current_skin

            # Handle mouse wheel events for scrolling the leaderboard
            if event.type == pygame.MOUSEBUTTONDOWN:
                # pygame.mouse.get_pos() to check if the cursor is in the leaderboard area
                mouse_x, mouse_y = event.pos

                top_field_rect, bottom_field_rect = draw_fields(screen)
                if bottom_field_rect.collidepoint(mouse_x, mouse_y):
                    if event.button == 4:  # Scroll up
                        leaderboard_scroll = max(leaderboard_scroll - 20, 0)
                    elif event.button == 5:  # Scroll down
                        total_content_height = draw_leaderboard(screen, bottom_field_rect, leaderboard_scroll)
                        max_scroll = max(total_content_height - bottom_field_rect.height, 0)
                        leaderboard_scroll = min(leaderboard_scroll + 20, max_scroll)

        # Draw screen
        screen.fill(GRAY)

        # Draw menu buttons
        singleplayer_button.draw(screen)
        multiplayer_button.draw(screen)

        # Draw additional fields
        top_field_rect, bottom_field_rect = draw_fields(screen)
        if not skin_options:
            skin_options = load_skin_options(top_field_rect)
        for option in skin_options:
            option.draw(screen)

        # Draw leaderboard
        total_content_height = draw_leaderboard(screen, bottom_field_rect, leaderboard_scroll)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    game_loop()
