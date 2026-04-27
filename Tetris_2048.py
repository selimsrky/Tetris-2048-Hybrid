import time
import os
import random
import pygame # Used for timing
import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color, WHITE, BLACK
from game_grid import GameGrid
from tetromino import Tetromino

# --- SETTINGS ---
GRID_HEIGHT, GRID_WIDTH = 20, 12
PANEL_WIDTH = 6 
CELL_SIZE = 40
BASE_SPEED = 500 # Speed in milliseconds

def setup_canvas():
    """Initializes the canvas size and scale"""
    canvas_height = CELL_SIZE * GRID_HEIGHT
    canvas_width = CELL_SIZE * (GRID_WIDTH + PANEL_WIDTH)
    stddraw.setCanvasSize(canvas_width, canvas_height)
    stddraw.setXscale(-0.5, GRID_WIDTH + PANEL_WIDTH - 0.5)
    stddraw.setYscale(-0.5, GRID_HEIGHT - 0.5)

def draw_ui(score):
    """Draws the score and control panel on the right side"""
    # Background for side panel
    stddraw.setPenColor(Color(240, 240, 240))
    stddraw.filledRectangle(GRID_WIDTH - 0.5, -0.5, PANEL_WIDTH, GRID_HEIGHT)
    
    # Draw Score
    stddraw.setPenColor(BLACK)
    stddraw.setFontSize(24)
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, GRID_HEIGHT - 2, "SCORE")
    stddraw.setFontSize(30)
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, GRID_HEIGHT - 4, str(score))
    
    # Draw Controls
    stddraw.setFontSize(18)
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, 6, "CONTROLS")
    stddraw.setFontSize(14)
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, 4.5, "Left: Move Left")
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, 3.5, "Right: Move Right")
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, 2.5, "Up: Rotate")
    stddraw.text(GRID_WIDTH + PANEL_WIDTH/2 - 0.5, 1.5, "Space: Drop")

def main():
    setup_canvas()
    Tetromino.grid_height = GRID_HEIGHT
    Tetromino.grid_width = GRID_WIDTH

    grid = GameGrid(GRID_HEIGHT, GRID_WIDTH)
    current = Tetromino(random.choice(['I','O','Z','S','T','J','L']))
    grid.current_tetromino = current

    # Image loading
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "images", "menu_image.png")
    
    menu_image = None
    if os.path.exists(image_path):
        menu_image = Picture(image_path)

    game_started = False
    score = 0
    last_drop_time = pygame.time.get_ticks()
    
    while True:
        # --- MENU SCREEN ---
        if not game_started:
            stddraw.clear(WHITE)
            center_x = (GRID_WIDTH + PANEL_WIDTH) / 2 - 0.5
            center_y = GRID_HEIGHT/2 - 0.5

            if menu_image is not None:
                stddraw.picture(menu_image, center_x, center_y)
            
            stddraw.setPenColor(BLACK)
            stddraw.setFontSize(24)
            stddraw.text(center_x, center_y - 4, "Press ENTER to Start")
            
            if stddraw.hasNextKeyTyped():
                key = stddraw.nextKeyTyped()
                if key == 'enter' or key == '\r':
                    game_started = True
            
            stddraw.show(50)
            continue

        # --- GAME LOOP ---
        stddraw.clear(WHITE)
        
        # 1. Inputs
        while stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == 'left': current.move('left', grid)
            elif key == 'right': current.move('right', grid)
            elif key == 'down': current.move('down', grid)
            elif key == 'up': current.rotate(grid)
            elif key == 'space': current.hard_drop(grid)

        # 2. Gravity Logic
        current_time = pygame.time.get_ticks()
        if (current_time - last_drop_time) >= BASE_SPEED:
            if not current.move('down', grid):
                tiles, pos = current.get_min_bounded_tile_matrix(True)
                game_over, lines_cleared = grid.update_grid(tiles, pos)
                score += (lines_cleared * 100)
                if game_over: break
                current = Tetromino(random.choice(['I','O','Z','S','T','J','L']))
                grid.current_tetromino = current
            last_drop_time = current_time

        # 3. Drawing
        grid.draw_grid() 
        current.draw()
        draw_ui(score)
        
        # 4. Single show call to prevent flickering
        stddraw.show(30)

if __name__ == '__main__':
    main()