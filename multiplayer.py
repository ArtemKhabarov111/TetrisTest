from settings import *
from timer import Timer
from score import Score
from random import choice
from os import path, getcwd
from preview import Preview
from game import Game, Tetromino


class MultiplayerGame(Game):
    def __init__(self, get_next_shape, update_score, area_rect, controls):
        # Initialize singleplayer game components
        super().__init__(get_next_shape, update_score)
        self.area_rect = area_rect
        self.controls = controls
        self.field_offset = (self.area_rect.x + PADDING, self.area_rect.y + PADDING)
        self.rect.topleft = (0, 0)
        self.game_over_active = False
        self.win_text = "Game Over"

    def input(self):
        # Only process input if this game is active
        if self.game_over_active:
            return

        keys = pygame.key.get_pressed()
        # Horizontal movement
        if not self.timers["horizontal move"].active:
            if keys[self.controls['left']]:
                self.tetromino.move_horizontal(-1)
                self.timers["horizontal move"].activate()
            elif keys[self.controls['right']]:
                self.tetromino.move_horizontal(1)
                self.timers["horizontal move"].activate()

        # Rotation
        if not self.timers["rotate"].active:
            if keys[self.controls['rotate']]:
                self.tetromino.rotate()
                self.timers["rotate"].activate()

        # Down speed-up
        if not self.down_pressed and keys[self.controls['down']]:
            self.down_pressed = True
            self.timers["vertical move"].duration = self.down_speed_faster
        if self.down_pressed and not keys[self.controls['down']]:
            self.down_pressed = False
            self.timers["vertical move"].duration = self.down_speed

    def run(self):
        if not self.game_over_active:
            self.input()
            self.timer_update()
            self.sprites.update()

        # Draw playfield on its own surface.
        self.surface.fill("black")
        self.draw_ghost()
        self.sprites.draw(self.surface)
        self.draw_grid()

        # Blit the play surface with field_offset
        self.display_surface.blit(self.surface, self.field_offset)

        # Draw outline
        field_rect = self.surface.get_rect(topleft=self.field_offset)
        pygame.draw.rect(self.display_surface, OUTLINE_COLOR, field_rect, 2)

    def draw_game_over_overlay(self, win_text=None):
        if win_text:
            self.win_text = win_text

        # Create fonts
        large_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 64)
        small_font = pygame.font.Font(path.join(getcwd(), "graphics", FONT), 32)

        # Render text surfaces
        main_text = large_font.render(self.win_text, True, "white")
        score_text = small_font.render(f"Score: {self.current_score}", True, "white")
        level_text = small_font.render(f"Level: {self.current_level}", True, "white")
        lines_text = small_font.render(f"Lines: {self.current_lines}", True, "white")
        continue_text = small_font.render("", True, "white")

        # Create a black background surface with 150 alpha
        black_area = pygame.Surface((self.area_rect.width, self.area_rect.height))
        black_area.set_alpha(150)
        black_area.fill("black")

        # Blit black background
        self.display_surface.blit(black_area, (self.area_rect.x, self.area_rect.y))

        # Calculate center positions
        center_x = self.area_rect.width // 2
        center_y = self.area_rect.height // 2

        main_rect = main_text.get_rect(center=(center_x, center_y - 40))
        score_rect = score_text.get_rect(center=(center_x, center_y + 20))
        level_rect = level_text.get_rect(center=(center_x, center_y + 70))
        lines_rect = lines_text.get_rect(center=(center_x, center_y + 120))
        continue_rect = continue_text.get_rect(center=(center_x, center_y + 170))

        # Blit the text surfaces on top of the black area
        self.display_surface.blit(main_text, (self.area_rect.x + main_rect.x, self.area_rect.y + main_rect.y))
        self.display_surface.blit(score_text, (self.area_rect.x + score_rect.x, self.area_rect.y + score_rect.y))
        self.display_surface.blit(level_text, (self.area_rect.x + level_rect.x, self.area_rect.y + level_rect.y))
        self.display_surface.blit(lines_text, (self.area_rect.x + lines_rect.x, self.area_rect.y + lines_rect.y))
        self.display_surface.blit(continue_text, (self.area_rect.x + continue_rect.x,
                                                  self.area_rect.y + continue_rect.y))

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                self.game_over_active = True
                # Deactivate all timers to freeze game logic
                for timer in self.timers.values():
                    timer.deactivate()
                break

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
            self.field_data
        )

    def restart_game(self):
        self.game_over_active = False
        self.field_data = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.sprites.empty()
        for row in self.field_data:
            for col in range(COLUMNS):
                row[col] = 0
        self.current_score = 0
        self.current_lines = 0
        self.current_level = 1
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.1
        self.update_score(self.current_lines, self.current_score, self.current_level)
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprites,
            self.create_new_tetromino,
            self.field_data
        )

        # Reinitialize timers.
        self.timers["vertical move"] = Timer(UPDATE_START_SPEED, True, self.move_down)
        self.timers["horizontal move"] = Timer(MOVE_WAIT_TIME * 0.3)
        self.timers["rotate"] = Timer(ROTATE_WAIT_TIME)
        self.timers["vertical move"].activate()


class Multiplayer:
    def __init__(self):
        pygame.init()

        player_area_width = GAME_WIDTH + SIDEBAR_WIDTH + 3 * PADDING
        player_area_height = GAME_HEIGHT + 2 * PADDING

        gap_between_players = 50
        window_width = 2 * player_area_width + gap_between_players
        window_height = player_area_height

        self.display_surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Multiplayer Tetris")
        self.clock = pygame.time.Clock()

        # Controls for each player
        controls1 = {'left': pygame.K_a, 'right': pygame.K_d, 'rotate': pygame.K_w, 'down': pygame.K_s}
        controls2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'rotate': pygame.K_UP, 'down': pygame.K_DOWN}

        # Play surfaces for each player
        self.player1_area = pygame.Rect(0, 0, player_area_width, player_area_height)
        self.player2_area = pygame.Rect(player_area_width + gap_between_players, 0, player_area_width,
                                        player_area_height)

        # Next shapes or each player
        self.next_shapes1 = [choice(list(TETROMINOS.keys())) for _ in range(3)]
        self.next_shapes2 = [choice(list(TETROMINOS.keys())) for _ in range(3)]

        # Game instances for each player
        self.game1 = MultiplayerGame(self.get_next_shape1, self.update_score1, self.player1_area, controls1)
        self.game2 = MultiplayerGame(self.get_next_shape2, self.update_score2, self.player2_area, controls2)

        # Side panels for each player.
        self.score1 = Score()
        self.preview1 = Preview()
        self.score2 = Score()
        self.preview2 = Preview()

        sidebar_x1 = self.player1_area.x + PADDING + GAME_WIDTH + PADDING
        sidebar_y1 = self.player1_area.y + PADDING
        self.preview1.rect.topleft = (sidebar_x1, sidebar_y1)
        self.score1.rect.topleft = (sidebar_x1, sidebar_y1 + int(GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION) + PADDING)

        sidebar_x2 = self.player2_area.x + PADDING + GAME_WIDTH + PADDING
        sidebar_y2 = self.player2_area.y + PADDING
        self.preview2.rect.topleft = (sidebar_x2, sidebar_y2)
        self.score2.rect.topleft = (sidebar_x2, sidebar_y2 + int(GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION) + PADDING)

        # Music
        self.music = pygame.mixer.Sound(path.join(getcwd(), 'sounds', 'tetris_original.mp3'))
        self.music.set_volume(0.1)
        self.music.play(-1, fade_ms=500)

        # Flag. Both players have lost
        self.both_game_over = False

    def update_score1(self, lines, score, level):
        self.score1.lines = lines
        self.score1.score = score
        self.score1.level = level

    def update_score2(self, lines, score, level):
        self.score2.lines = lines
        self.score2.score = score
        self.score2.level = level

    def get_next_shape1(self):
        next_shape = self.next_shapes1.pop(0)
        self.next_shapes1.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def get_next_shape2(self):
        next_shape = self.next_shapes2.pop(0)
        self.next_shapes2.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.music.fadeout(1000)  # Music fade out
                    return

                # Allow to restart game when both players have lost
                if self.both_game_over and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self.game1.restart_game()
                    self.game2.restart_game()
                    self.both_game_over = False

            self.display_surface.fill(GRAY)

            # Run game for each player
            self.game1.run()
            self.game2.run()

            # Draw side panels for each player
            self.preview1.run(self.next_shapes1)
            self.score1.run()
            self.preview2.run(self.next_shapes2)
            self.score2.run()

            # Update final results when both players have finished
            if self.game1.game_over_active and self.game2.game_over_active:
                if not self.both_game_over:
                    if self.game1.current_score > self.game2.current_score:
                        self.game1.draw_game_over_overlay(win_text="You Won")
                        self.game2.draw_game_over_overlay(win_text="Game Over")
                    elif self.game2.current_score > self.game1.current_score:
                        self.game2.draw_game_over_overlay(win_text="You Won")
                        self.game1.draw_game_over_overlay(win_text="Game Over")
                    else:
                        self.game1.draw_game_over_overlay(win_text="Tie")
                        self.game2.draw_game_over_overlay(win_text="Tie")
                    self.both_game_over = True
                else:
                    # Both players are finished and results already shown
                    self.game1.draw_game_over_overlay()
                    self.game2.draw_game_over_overlay()

            # If only one player is finished, show that player's overlay with a waiting message
            elif self.game1.game_over_active:
                self.game1.draw_game_over_overlay(win_text="Wait for opponent")
            elif self.game2.game_over_active:
                self.game2.draw_game_over_overlay(win_text="Wait for opponent")

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    multiplayer = Multiplayer()
    multiplayer.run()
