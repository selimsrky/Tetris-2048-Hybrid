# A class for modeling a point as a location in 2D space
class Point:
    # --- SKELETON (Keep original structure) ---
    def __init__(self, x=0, y=0):
        """Constructor: Creates a point at a given location."""
        self.x = x
        self.y = y

    def translate(self, dx, dy):
        """Moves this point by dx along the x-axis and dy along the y-axis."""
        self.x += dx
        self.y += dy

    def move(self, x, y):
        """Moves this point to a specific coordinate (x, y)."""
        self.x = x
        self.y = y

    def __str__(self):
        """Returns the string representation of the point."""
        return f'({self.x}, {self.y})'

    # --- NEW ADDITIONS (Optimizations for Tetris logic) ---
    def __eq__(self, other):
        """Enables comparison: point1 == point2."""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def is_within_bounds(self, grid_width, grid_height):
        """Checks if the point is inside the grid boundaries."""
        return 0 <= self.x < grid_width and 0 <= self.y < grid_height