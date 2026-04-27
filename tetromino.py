from tile import Tile  # Used for modeling each numbered tile (2048 logic) on the tetrominoes
from point import Point  # Used for mapping 2D tile positions
import copy as cp  # Used for safely duplicating tiles and positions
import random  # Used for generating random spawn coordinates and random tile numbers
import numpy as np  # Used for handling 2D arrays (matrices) efficiently

# A class for modeling tetrominoes (now supporting all 7 types: I, O, Z, S, T, J, L)
class Tetromino:
    # A dictionary defining the shapes of tetrominoes based on their block coordinates
    # Each coordinate pair (col, row) represents a filled cell in the local n x n matrix
    SHAPES = {
        'I': [(1,0), (1,1), (1,2), (1,3)],
        'O': [(0,0), (0,1), (1,0), (1,1)],
        'Z': [(0,1), (1,1), (1,2), (2,2)],
        'S': [(1,1), (2,1), (0,2), (1,2)],
        'T': [(0,1), (1,1), (2,1), (1,2)],
        'J': [(0,1), (1,1), (2,1), (0,2)],
        'L': [(0,1), (1,1), (2,1), (2,2)]
    }

    # The dimensions of the game grid (shared across all instances)
    grid_height, grid_width = None, None

    def __init__(self, type):
        """
        Constructor: Creates a new Tetromino instance of the given type.
        Initializes the local tile matrix and calculates the spawn position.
        """
        self.type = type
        
        # Determine the size of the local bounding box (n x n) based on the shape type
        if self.type == 'I':
            n = 4
        elif self.type == 'O':
            n = 2
        else: # Applies to Z, S, T, J, L
            n = 3

        # Initialize an empty n x n matrix filled with None
        self.tile_matrix = np.full((n, n), None)

        # Populate the matrix with Tile objects based on the shape's coordinates
        for i in range(4):
            col_index, row_index = self.SHAPES[type][i][0], self.SHAPES[type][i][1]
            # Each tile is randomly numbered using either 2 or 4 as per 2048 rules
            random_number = random.choice([2, 4])
            self.tile_matrix[row_index][col_index] = Tile(random_number)

        # Set the initial spawn location (bottom-left cell) of the tetromino
        self.bottom_left_cell = Point()
        self.bottom_left_cell.y = Tetromino.grid_height - 1
        # Randomize the horizontal spawn position within grid boundaries
        self.bottom_left_cell.x = random.randint(0, Tetromino.grid_width - n)

    def rotate(self, game_grid):
        """
        Rotates the tetromino 90 degrees clockwise.
        Validates the rotation against grid boundaries and existing tiles.
        Returns True if successful, False if blocked.
        """
        n = len(self.tile_matrix)
        # Create a deep copy to revert if the rotation causes a collision
        old_matrix = cp.deepcopy(self.tile_matrix)

        # Rotate the matrix 90 degrees clockwise (k=-1 means -90 degrees mathematically)
        self.tile_matrix = np.rot90(self.tile_matrix, k=-1)

        # Validate the new rotated matrix
        valid_rotation = True
        for row in range(n):
            for col in range(n):
                if self.tile_matrix[row][col] is not None:
                    position = self.get_cell_position(row, col)
                    # Check boundary collisions (walls and floor)
                    if position.x < 0 or position.x >= Tetromino.grid_width or position.y < 0:
                        valid_rotation = False
                        break
                    # Check overlapping collisions with existing tiles on the grid
                    if position.y < Tetromino.grid_height and game_grid.is_occupied(position.y, position.x):
                        valid_rotation = False
                        break
            if not valid_rotation:
                break

        # If the rotation is invalid, revert to the original state
        if not valid_rotation:
            self.tile_matrix = old_matrix
            return False
            
        return True

    def hard_drop(self, game_grid):
        """
        Drops the tetromino instantly to the lowest possible valid row on the grid.
        """
        # Keep moving down until it hits the floor or another tile
        while self.move('down', game_grid):
            pass

    def get_cell_position(self, row, col):
        """
        Calculates the global grid coordinates of a specific tile within the local matrix.
        Returns a Point object representing the actual position on the GameGrid.
        """
        n = len(self.tile_matrix)
        position = Point()
        position.x = self.bottom_left_cell.x + col
        position.y = self.bottom_left_cell.y + (n - 1) - row
        return position

    def get_min_bounded_tile_matrix(self, return_position=False):
        """
        Trims the empty rows and columns around the tetromino.
        This is crucial for the GameGrid's update_grid() function to lock tiles accurately.
        """
        n = len(self.tile_matrix)
        min_row, max_row, min_col, max_col = n - 1, 0, n - 1, 0

        for row in range(n):
            for col in range(n):
                if self.tile_matrix[row][col] is not None:
                    if row < min_row:
                        min_row = row
                    if row > max_row:
                        max_row = row
                    if col < min_col:
                        min_col = col
                    if col > max_col:
                        max_col = col

        copy = np.full((max_row - min_row + 1, max_col - min_col + 1), None)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if self.tile_matrix[row][col] is not None:
                    row_ind = row - min_row
                    col_ind = col - min_col
                    copy[row_ind][col_ind] = cp.deepcopy(self.tile_matrix[row][col])

        if not return_position:
            return copy
        else:
            blc_position = cp.copy(self.bottom_left_cell)
            blc_position.translate(min_col, (n - 1) - max_row)
            return copy, blc_position

    def draw(self):
        """
        Iterates through the local matrix and calls the draw() method of each Tile.
        Tiles are drawn only if they are within the visible grid boundaries.
        """
        n = len(self.tile_matrix)
        for row in range(n):
            for col in range(n):
                if self.tile_matrix[row][col] is not None:
                    position = self.get_cell_position(row, col)
                    if position.y < Tetromino.grid_height:
                        self.tile_matrix[row][col].draw(position)

    def move(self, direction, game_grid):
        """
        Attempts to move the tetromino one step in the specified direction ('left', 'right', 'down').
        Returns True if successful, False if blocked by boundaries or other tiles.
        """
        if not self.can_be_moved(direction, game_grid):
            return False

        if direction == 'left':
            self.bottom_left_cell.x -= 1
        elif direction == 'right':
            self.bottom_left_cell.x += 1
        else: # down
            self.bottom_left_cell.y -= 1

        return True

    def can_be_moved(self, direction, game_grid):
        """
        Checks for collisions against grid boundaries and existing tiles on the GameGrid.
        """
        n = len(self.tile_matrix)

        if direction == 'left' or direction == 'right':
            for row_index in range(n):
                for col_index in range(n):
                    row, col = row_index, col_index

                    if direction == 'left' and self.tile_matrix[row][col] is not None:
                        leftmost = self.get_cell_position(row, col)
                        if leftmost.x == 0:
                            return False
                        if game_grid.is_occupied(leftmost.y, leftmost.x - 1):
                            return False
                        break 

                    row, col = row_index, n - 1 - col_index

                    if direction == 'right' and self.tile_matrix[row][col] is not None:
                        rightmost = self.get_cell_position(row, col)
                        if rightmost.x == Tetromino.grid_width - 1:
                            return False
                        if game_grid.is_occupied(rightmost.y, rightmost.x + 1):
                            return False
                        break 

        else:
            for col in range(n):
                for row in range(n - 1, -1, -1):
                    if self.tile_matrix[row][col] is not None:
                        bottommost = self.get_cell_position(row, col)
                        if bottommost.y == 0:
                            return False
                        if game_grid.is_occupied(bottommost.y - 1, bottommost.x):
                            return False
                        break 

        return True