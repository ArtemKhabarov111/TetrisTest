import settings
import db_manager

from settings import *
from timer import Timer
from random import choice
from os import path, getcwd


class Game:
    def __init__(self, get_next_shape, update_score):
        # General
        self.game_over_active = None
        self.new_high_score = False
        self.exit_to_menu = False
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft=(PADDING, PADDING))
        self.sprites = pygame.sprite.Group()
        self.ghost_images = {}

        # Game connection
        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # Tetromino
        self.field_data = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

        # Timer
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.1
        self.down_pressed = False

        self.timers = {
            "vertical move": Timer(UPDATE_START_SPEED, True, self.move_down),
            "horizontal move": Timer(MOVE_WAIT_TIME * 0.3),
            "rotate": Timer(ROTATE_WAIT_TIME)
        }

        self.timers["vertical move"].activate()

        # Score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        # Sound
        self.landing_sound = pygame.mixer.Sound(path.join(getcwd(), "sounds", "landing.wav"))
        self.landing_sound.set_volume(0.08)

    def get_ghost_image(self, color):
        if color not in self.ghost_images:
            img = pygame.image.load(
                path.join(getcwd(), "graphics", f"skin{settings.SKIN}", f"{color}.png")
            ).convert_alpha()
            img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            img.set_alpha(GHOST_BLOCK_TRANSPARENCY)
            self.ghost_images[color] = img
        return self.ghost_images[color]

    def draw_ghost(self):
        ghost_positions = self.tetromino.get_ghost_positions()
        ghost_image = self.get_ghost_image(self.tetromino.color)
        for pos in ghost_positions:
            draw_pos = (int(pos.x * CELL_SIZE), int(pos.y * CELL_SIZE))
            self.surface.blit(ghost_image, draw_pos)

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.1
            self.timers["vertical move"].duration = self.down_speed

        self.update_score(self.current_lines, self.current_score, self.current_level)

    def prompt_username(self):
        # Show a "New high score" screen
        for t in self.timers.values():
            t.deactivate()
        pygame.event.clear()

        font_large = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 64)
        font_small = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 32)

        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.fill("black")

        input_text = ""
        active = True
        while active:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif evt.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if input_text:
                            active = False
                    else:
                        if len(input_text) < 15 and evt.unicode.isprintable():
                            input_text += evt.unicode

            self.display_surface.blit(overlay, (0, 0))

            title_surf = font_large.render("New High Score!", True, "white")
            prompt_surf = font_small.render("Enter your Username:", True, "white")
            entry_surf = font_small.render(input_text + "_", True, "white")

            # Render stats
            score_text = font_small.render(f"Score: {self.current_score}", True, "white")
            level_text = font_small.render(f"Level: {self.current_level}", True, "white")
            lines_text = font_small.render(f"Lines: {self.current_lines}", True, "white")

            # Calculate the center of display
            cx = self.display_surface.get_width() // 2
            cy = self.display_surface.get_height() // 2

            # Blit elements
            self.display_surface.blit(title_surf, title_surf.get_rect(center=(cx, cy - 100)))
            self.display_surface.blit(prompt_surf, prompt_surf.get_rect(center=(cx, cy - 50)))
            self.display_surface.blit(entry_surf, entry_surf.get_rect(center=(cx, cy)))
            self.display_surface.blit(score_text, score_text.get_rect(center=(cx, cy + 50)))
            self.display_surface.blit(level_text, level_text.get_rect(center=(cx, cy + 100)))
            self.display_surface.blit(lines_text, lines_text.get_rect(center=(cx, cy + 150)))

            pygame.display.update()

        db_manager.insert_score(input_text, self.current_score, self.current_level, self.current_lines)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                self.game_over_active = True  # Set game over flag

                # Compare with DB high score
                highest = db_manager.get_high_score()
                if self.current_score > highest:
                    # Prompt for name and save
                    self.new_high_score = True
                    self.prompt_username()

                    # Return to menu after saving record
                    self.exit_to_menu = True
                else:
                    # Standard game over screen
                    self.game_over_screen()
                    self.restart_game()
                break

    def game_over_screen(self):
        # Deactivate all timers
        for timer in self.timers.values():
            timer.deactivate()

        # Clear any queued events
        pygame.event.clear()

        # Create large and small fonts
        large_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 64)
        small_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 32)

        # Render texts for game over and final stats
        game_over_text = large_font.render("Game Over", True, "white")
        score_text = small_font.render(f"Score: {self.current_score}", True, "white")
        level_text = small_font.render(f"Level: {self.current_level}", True, "white")
        lines_text = small_font.render(f"Lines: {self.current_lines}", True, "white")
        continue_text = small_font.render("Press any button to continue", True, "white")

        # Create an overlay surface covering the entire display
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.fill("black")

        # Compute center of display for positioning
        center_x = self.display_surface.get_width() // 2
        center_y = self.display_surface.get_height() // 2

        # Determine positions for texts
        game_over_rect = game_over_text.get_rect(center=(center_x, center_y - 100))
        score_rect = score_text.get_rect(center=(center_x, center_y - 50))
        level_rect = level_text.get_rect(center=(center_x, center_y))
        lines_rect = lines_text.get_rect(center=(center_x, center_y + 50))
        continue_rect = continue_text.get_rect(center=(center_x, center_y + 100))

        # Blit texts onto the overlay
        overlay.blit(game_over_text, game_over_rect)
        overlay.blit(score_text, score_rect)
        overlay.blit(level_text, level_rect)
        overlay.blit(lines_text, lines_rect)
        overlay.blit(continue_text, continue_rect)

        # Blit the overlay to the display and update
        self.display_surface.blit(overlay, (0, 0))
        pygame.display.update()

        # Wait until a key or mouse button is pressed
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False

    def restart_game(self):
        # Reset the flag
        self.game_over_active = False

        # Reset game state
        self.field_data = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.sprites.empty()  # Remove all sprites from the group

        # Set all blocks to 0
        for row in self.field_data:
            for col in range(COLUMNS):
                row[col] = 0

        self.current_score = 0
        self.current_lines = 0
        self.current_level = 1
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.1

        # Update the score display
        self.update_score(self.current_lines, self.current_score, self.current_level)

        # Create a new tetromino
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

        # Reinitialize timers
        self.timers["vertical move"] = Timer(UPDATE_START_SPEED, True, self.move_down)
        self.timers["horizontal move"] = Timer(MOVE_WAIT_TIME * 0.3)
        self.timers["rotate"] = Timer(ROTATE_WAIT_TIME)

        # Activate vertical move timer
        self.timers["vertical move"].activate()

    def create_new_tetromino(self):
        self.landing_sound.play()
        self.check_game_over()

        if self.game_over_active:
            return

        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):
        for col in range(COLUMNS):
            for row in range(ROWS):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                pygame.draw.rect(self.surface, LINE_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 1)

    def input(self):
        # Ignore inputs when the game is over
        if getattr(self, 'game_over_active', False):
            return

        keys = pygame.key.get_pressed()

        # Check horizontal movement
        if not self.timers["horizontal move"].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers["horizontal move"].activate()

            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers["horizontal move"].activate()

        # Check rotation
        if not self.timers["rotate"].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers["rotate"].activate()

        # Down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers["vertical move"].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers["vertical move"].duration = self.down_speed

    def check_finished_rows(self):
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:
                for block in self.field_data[delete_row]:
                    block.kill()
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # Rebuild field data only with blocks within bounds.
            self.field_data = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
            for block in list(self.sprites):
                # Only add blocks with y in the visible range.
                if 0 <= block.pos.y < ROWS:
                    self.field_data[int(block.pos.y)][int(block.pos.x)] = block
                else:
                    block.kill()

            self.calculate_score(len(delete_rows))

    def run(self):
        # Update
        self.input()
        self.timer_update()
        self.sprites.update()

        # Drawing
        self.surface.fill("black")
        self.draw_ghost()
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, OUTLINE_COLOR, self.rect, 2)


class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):
        # Setup
        self.shape = shape
        self.block_positions = TETROMINOS[shape]["shape"]
        self.color = TETROMINOS[shape]["color"]
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data
        self.ghost_positions = None
        self.needs_ghost_update = True

        # Create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # Collisions
    def next_move_horizontal_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    # Movement
    def move_horizontal(self, amount):
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount
            self.needs_ghost_update = True

    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
            self.needs_ghost_update = True
        else:
            # When locking, only add blocks with y >= 0 and mark them as locked.
            for block in self.blocks:
                if block.pos.y >= 0:
                    self.field_data[int(block.pos.y)][int(block.pos.x)] = block
                    block.locked = True
            self.create_new_tetromino()

    # rotate
    def rotate(self):
        if self.shape != "O":
            # Pivot point
            pivot_pos = self.blocks[0].pos

            # New block positions
            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            # Collision check
            for pos in new_block_positions:
                # Horizontal / wall check
                if pos.x < 0 or pos.x >= COLUMNS:
                    return

                # Vertical / floor check
                if pos.y >= ROWS:
                    return

                # Only check collision if the block is on or below the top of the grid
                if pos.y >= 0 and self.field_data[int(pos.y)][int(pos.x)]:
                    return

            # If no collisions, update block positions
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

            # Update ghost block position
            self.needs_ghost_update = True

    def get_ghost_positions(self):
        if not self.needs_ghost_update and self.ghost_positions:
            return self.ghost_positions
        drop_distance = self.get_max_drop_distance()
        ghost_positions = []
        for block in self.blocks:
            pos = block.pos.copy()
            pos.y += drop_distance  # Increment y by drop_distance
            ghost_positions.append(pos)
        self.ghost_positions = ghost_positions
        self.needs_ghost_update = False
        return self.ghost_positions

    def get_max_drop_distance(self):
        max_distance = ROWS  # Start with a high number
        for block in self.blocks:
            distance = 0
            current_y = int(block.pos.y)
            while current_y + distance + 1 < ROWS and not self.field_data[current_y + distance + 1][int(block.pos.x)]:
                distance += 1
            max_distance = min(max_distance, distance)
        return max_distance


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, block):
        super().__init__(group)
        self.image = (pygame.image.load(path.join(getcwd(), "graphics", f"skin{settings.SKIN}", f"{block}.png")).
                      convert_alpha())
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))

        # Positioning
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.pos * CELL_SIZE)
        self.locked = False

    def rotate(self, pivot_pos):
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < COLUMNS:
            return True
        if self.pos.y >= 0 and field_data[int(self.pos.y)][x]:
            return True
        return False

    def vertical_collide(self, y, field_data):
        if y >= ROWS:
            return True
        if y >= 0 and field_data[int(y)][int(self.pos.x)]:
            return True

    def update(self):
        # Killing blocks that are out of bounds to prevent ghost blocks
        if self.locked and self.pos.y < 0:
            self.kill()
        else:
            self.rect.topleft = self.pos * CELL_SIZE
