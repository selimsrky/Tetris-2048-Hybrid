import time, os, random, sys
import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color, WHITE, BLACK
from game_grid import GameGrid
from tetromino import Tetromino
from point import Point 

# --- SETTINGS ---
GRID_HEIGHT, GRID_WIDTH = 20, 12
PANEL_WIDTH = 6 
CELL_SIZE = 40
BASE_SPEED = 0.5 

# Updated to classic 2048 colors based on the PDF design
MAIN_BG_COLOR = Color(205, 193, 180)    # Main grid background color (Beige)
SIDE_PANEL_COLOR = Color(166, 153, 141) # Side panel color (Dark brownish-grey)

def setup_canvas():
    # Setup the canvas dimensions including the side panel
    stddraw.setCanvasSize(CELL_SIZE * (GRID_WIDTH + PANEL_WIDTH), CELL_SIZE * GRID_HEIGHT)
    stddraw.setXscale(-0.5, GRID_WIDTH + PANEL_WIDTH - 0.5)
    stddraw.setYscale(-0.5, GRID_HEIGHT - 0.5)

def draw_ui(score, next_tetromino):
    # Draw the side panel background
    stddraw.setPenColor(SIDE_PANEL_COLOR)
    stddraw.filledRectangle(GRID_WIDTH - 0.5, -0.5, PANEL_WIDTH, GRID_HEIGHT)
    panel_center_x = GRID_WIDTH + PANEL_WIDTH/2 - 0.5
    
    # Draw SCORE text in bold and white
    stddraw.setPenColor(WHITE)
    stddraw.setFontSize(24); stddraw.boldText(panel_center_x, GRID_HEIGHT - 2, "SCORE")
    stddraw.setFontSize(35); stddraw.boldText(panel_center_x, GRID_HEIGHT - 4, str(score))
    
    # Draw NEXT text in bold and white (Moved lower)
    stddraw.setFontSize(24); stddraw.boldText(panel_center_x, 6, "NEXT")
    
    if next_tetromino:
        # Dynamically calculate offsets to perfectly center the shape under the text
        n = len(next_tetromino.tile_matrix)
        pos_x = panel_center_x - (n / 2) + 0.5
        pos_y = 3.5 - (n / 2)
        
        # Position and draw the NEXT tetromino
        original_pos = next_tetromino.bottom_left_cell
        next_tetromino.bottom_left_cell = Point(pos_x, pos_y)
        next_tetromino.draw()
        
        # Restore original position to avoid logic errors during the game
        next_tetromino.bottom_left_cell = original_pos

def show_game_over_screen(score):
    center_x = (GRID_WIDTH + PANEL_WIDTH) / 2 - 0.5
    center_y = GRID_HEIGHT / 2 - 0.5
    box_w, box_h = 12, 9
    while True:
        # 1. Background of the Game Over Box
        stddraw.setPenColor(Color(44, 62, 80)) 
        stddraw.filledRectangle(center_x - box_w/2, center_y - box_h/2, box_w, box_h)
        
        # 2. Border of the Game Over Box
        stddraw.setPenColor(Color(0, 100, 200)) 
        stddraw.setPenRadius(0.01) # Border thickness
        stddraw.rectangle(center_x - box_w/2, center_y - box_h/2, box_w, box_h)
        stddraw.setPenRadius() # Reset to default
        
        # Texts and Buttons
        stddraw.setPenColor(Color(231, 76, 60)); stddraw.setFontSize(75); stddraw.text(center_x, center_y + 3.0, "GAME OVER")
        stddraw.setPenColor(WHITE); stddraw.setFontSize(45); stddraw.text(center_x, center_y + 0.8, f"Score: {score}")
        
        # Play Again Button
        pa_box = (center_x, center_y - 1.2, 8, 1.5)
        stddraw.setPenColor(Color(46, 204, 113)); stddraw.filledRectangle(pa_box[0]-pa_box[2]/2, pa_box[1]-pa_box[3]/2, pa_box[2], pa_box[3])
        stddraw.setPenColor(WHITE); stddraw.setFontSize(32); stddraw.text(pa_box[0], pa_box[1], "PLAY AGAIN")
        
        # Exit Game Button
        ex_box = (center_x, center_y - 3.2, 8, 1.2)
        stddraw.setPenColor(Color(192, 57, 43)); stddraw.filledRectangle(ex_box[0]-ex_box[2]/2, ex_box[1]-ex_box[3]/2, ex_box[2], ex_box[3])
        stddraw.setPenColor(WHITE); stddraw.setFontSize(24); stddraw.text(ex_box[0], ex_box[1], "EXIT GAME")
        
        # Check for mouse clicks on buttons
        if stddraw.mousePressed():
            mx, my = stddraw.mouseX(), stddraw.mouseY()
            if (pa_box[0]-pa_box[2]/2 < mx < pa_box[0]+pa_box[2]/2 and pa_box[1]-pa_box[3]/2 < my < pa_box[1]+pa_box[3]/2):
                return True
            if (ex_box[0]-ex_box[2]/2 < mx < ex_box[0]+ex_box[2]/2 and ex_box[1]-ex_box[3]/2 < my < ex_box[1]+ex_box[3]/2):
                sys.exit()
        stddraw.show(100)

def main():
    setup_canvas()
    Tetromino.grid_height = GRID_HEIGHT
    Tetromino.grid_width = GRID_WIDTH
    
    is_first_game = True
    tetromino_types = ['I','O','Z','S','T','J','L']
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "images", "menu_image.png")
    menu_image = Picture(image_path) if os.path.exists(image_path) else None

    # Main application loop handling restarts
    while True: 
        grid = GameGrid(GRID_HEIGHT, GRID_WIDTH)
        current = Tetromino(random.choice(tetromino_types))
        next_block = Tetromino(random.choice(tetromino_types))
        grid.current_tetromino = current
        
        game_started = False if is_first_game else True
        score = 0
        last_drop_time = time.time()
        
        # Start Screen Loop
        while True:
            if not game_started:
                stddraw.clear(WHITE)
                cx, cy = (GRID_WIDTH + PANEL_WIDTH)/2 - 0.5, GRID_HEIGHT/2 - 0.5
                if menu_image: stddraw.picture(menu_image, cx, cy)
                stddraw.setPenColor(BLACK); stddraw.setFontSize(24); stddraw.text(cx, cy - 4, "Press ENTER to Start")
                if stddraw.hasNextKeyTyped() and stddraw.nextKeyTyped() in ['enter', '\r']: game_started = True
                stddraw.show(50); continue

            # Clear main background
            stddraw.clear(MAIN_BG_COLOR)
            
            # Handle user keyboard inputs
            while stddraw.hasNextKeyTyped():
                key = stddraw.nextKeyTyped()
                if key == 'left': current.move('left', grid)
                elif key == 'right': current.move('right', grid)
                elif key == 'down': current.move('down', grid)
                elif key == 'up': current.rotate(grid)
                elif key == 'space': current.hard_drop(grid)

            # Handle automatic gravity drops
            if (time.time() - last_drop_time) >= BASE_SPEED:
                if not current.move('down', grid):
                    # Lock tetromino to grid if it cannot move down
                    tiles, pos = current.get_min_bounded_tile_matrix(True)
                    game_over, score_increment = grid.update_grid(tiles, pos)
                    score += score_increment 
                    
                    if game_over:
                        if show_game_over_screen(score): is_first_game = False; break 
                        
                    current = next_block
                    next_block = Tetromino(random.choice(tetromino_types))
                    grid.current_tetromino = current
                last_drop_time = time.time()

            # Render the entire game screen
            grid.draw_grid(); current.draw(); draw_ui(score, next_block)
            
            # Draw the outer boundary of the grid
            stddraw.setPenColor(Color(187, 173, 160)); stddraw.setPenRadius(0.008)
            stddraw.rectangle(-0.5, -0.5, GRID_WIDTH, GRID_HEIGHT) 
            stddraw.show(30)

if __name__ == '__main__':
    main()