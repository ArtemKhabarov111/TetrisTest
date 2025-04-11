import pygame

# Game size
COLUMNS = 10
ROWS = 20
CELL_SIZE = 40
GAME_WIDTH, GAME_HEIGHT = COLUMNS * CELL_SIZE, ROWS * CELL_SIZE

# sidebar size
SIDEBAR_WIDTH = 200
PREVIEW_HEIGHT_FRACTION = 0.7
SCORE_HEIGHT_FRACTION = 1 - PREVIEW_HEIGHT_FRACTION

# window
PADDING = 20
WINDOW_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH + PADDING * 3
WINDOW_HEIGHT = GAME_HEIGHT + PADDING * 2

# game behaviour
FPS = 165
UPDATE_START_SPEED = 600
MOVE_WAIT_TIME = 200
ROTATE_WAIT_TIME = 200
BLOCK_OFFSET = pygame.Vector2(COLUMNS // 2, -2)

# Skins for blocks (1, 2, 3). 2nd - my favourite
SKIN = 1

# Colors
YELLOW = '#f1e60d'
RED = '#e51b20'
BLUE = '#204b9b'
GREEN = '#65b32e'
PURPLE = '#7b217f'
CYAN = '#6cc6d9'
ORANGE = '#f07e13'
GRAY = '#1C1C1C'
LINE_COLOR = '#606060'
OUTLINE_COLOR = '#A0A0A0'

# shapes
TETROMINOS = {
	'T': {'shape': [(0, 0), (-1, 0), (1, 0), (0, -1)], 'tetromino': 'T', 'color': 'block_T'},
	'O': {'shape': [(0, 0), (0, -1), (1, 0), (1, -1)], 'tetromino': 'O', 'color': 'block_O'},
	'J': {'shape': [(0, 0), (0, -1), (0, 1), (-1, 1)], 'tetromino': 'J', 'color': 'block_J'},
	'L': {'shape': [(0, 0), (0, -1), (0, 1), (1, 1)], 'tetromino': 'L', 'color': 'block_L'},
	'I': {'shape': [(0, 0), (0, -1), (0, -2), (0, 1)], 'tetromino': 'I', 'color': 'block_I'},
	'S': {'shape': [(0, 0), (-1, 0), (0, -1), (1, -1)], 'tetromino': 'S', 'color': 'block_S'},
	'Z': {'shape': [(0, 0), (1, 0), (0, -1), (-1, -1)], 'tetromino': 'Z', 'color': 'block_Z'}
}

SCORE_DATA = {1: 100, 2: 300, 3: 500, 4: 1000}
