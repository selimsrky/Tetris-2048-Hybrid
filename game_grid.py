import lib.stddraw as stddraw
from lib.color import Color
from point import Point
import numpy as np

class GameGrid:
    def __init__(self, grid_h, grid_w):
        # Initialize grid dimensions
        self.grid_height = grid_h
        self.grid_width = grid_w
        # Create a 2D matrix filled with None using NumPy
        self.tile_matrix = np.full((grid_h, grid_w), None)
        self.current_tetromino = None
        self.game_over = False
        
        # 2048-Themed Color Settings
        self.empty_cell_color = Color(205, 193, 180) 
        self.line_color = Color(187, 173, 160)       
        self.boundary_color = Color(187, 173, 160)   
        self.line_thickness = 0.005                  
        self.box_thickness = 5 * self.line_thickness 

    def display(self, speed=500):
        # Clear the background and render game elements
        stddraw.clear(self.empty_cell_color)
        self.draw_grid()
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        self.draw_boundaries()
        stddraw.show(speed)

    def draw_grid(self):
        # Draw locked tiles in the grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None:
                    self.tile_matrix[row][col].draw(Point(col, row))
        
        # Draw inner grid lines
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        
        for x in np.arange(start_x + 1, end_x, 1):
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()

    def draw_boundaries(self):
        # Draw the outer boundary of the game area
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def is_occupied(self, row, col):
        # Check if a cell is out of bounds or already occupied by a tile
        if not (0 <= row < self.grid_height and 0 <= col < self.grid_width):
            return True
        return self.tile_matrix[row][col] is not None

    def update_grid(self, tiles_to_lock, blc_position):
        # Locks the tetromino blocks into the grid
        self.current_tetromino = None
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
        
        for col in range(n_cols):
            for row in range(n_rows):
                if tiles_to_lock[row][col] is not None:
                    pos_x = blc_position.x + col
                    pos_y = blc_position.y + (n_rows - 1) - row
                    # Verify if the position is within grid boundaries
                    if 0 <= pos_y < self.grid_height and 0 <= pos_x < self.grid_width:
                        self.tile_matrix[pos_y][pos_x] = tiles_to_lock[row][col]
                    else:
                        # If the block is locked above the grid, game is over
                        self.game_over = True
        
        score_increment = 0
        if not self.game_over:
            # 1. Calculate scores from numerical merges (2048 logic)
            merge_pts = self.merge_and_fall_chained()
            # 2. Perform line clearing and count the number of cleared lines (Tetris logic)
            lines_cleared = self.clear_lines()
            # 3. Calculate line clearing scores (1 line = 100 points)
            line_pts = lines_cleared * 100
            
            # Sum up total score increment to return to main.py
            score_increment = merge_pts + line_pts
            
        return self.game_over, score_increment

    def merge_and_fall_chained(self):
        # Handles chained 2048-style vertical merges and gravity
        total_merge_score = 0
        while True:
            merged_in_this_pass = False
            self.apply_gravity() # Ensure tiles are settled before checking for merges
            for col in range(self.grid_width):
                for row in range(self.grid_height - 1):
                    t_bottom = self.tile_matrix[row][col]
                    t_top = self.tile_matrix[row+1][col]
                    
                    # Merge logic: if two vertical adjacent tiles have the same number
                    if t_bottom and t_top and t_bottom.number == t_top.number:
                        new_val = t_bottom.number * 2
                        total_merge_score += new_val
                        t_bottom.number = new_val
                        self.tile_matrix[row+1][col] = None # Remove the top tile
                        merged_in_this_pass = True
            
            # Continue checking until no more merges are possible in a single pass
            if not merged_in_this_pass:
                break
        return total_merge_score

    def apply_gravity(self):
        # Makes all tiles fall down to the lowest possible empty cell in their column
        for col in range(self.grid_width):
            # Collect all existing tiles in the column
            column_tiles = [self.tile_matrix[row][col] for row in range(self.grid_height) if self.tile_matrix[row][col] is not None]
            # Re-place them starting from the bottom (index 0)
            for row in range(self.grid_height):
                if row < len(column_tiles):
                    self.tile_matrix[row][col] = column_tiles[row]
                else:
                    self.tile_matrix[row][col] = None

    def clear_lines(self):
        # Identifies and removes full horizontal lines
        lines_cleared = 0
        r = 0
        while r < self.grid_height:
            # Check if all cells in the current row are filled
            if all(self.tile_matrix[r][c] is not None for c in range(self.grid_width)):
                lines_cleared += 1
                # Clear the row and shift all rows above it downward
                for i in range(r, self.grid_height - 1):
                    self.tile_matrix[i] = self.tile_matrix[i+1].copy()
                # Initialize the top row as empty
                self.tile_matrix[self.grid_height-1] = np.full(self.grid_width, None)
                # Do not increment 'r' because the shifted row needs to be checked again
            else:
                r += 1
        return lines_cleared