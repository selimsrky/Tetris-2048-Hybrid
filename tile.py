import lib.stddraw as stddraw
from lib.color import Color

class Tile:
    # Class variables
    boundary_thickness = 0.004
    font_family, font_size = 'Arial', 24

    def __init__(self, number=2):
        self.number = number
        # Classic 2048 grid line color
        self.box_color = Color(187, 173, 160) 

    def set_number(self, number):
        self.number = number

    def get_colors(self):
        """Original 2048 number/color mapping"""
        colors = {
            2:    (Color(238, 228, 218), Color(119, 110, 101)), # Cream background, Dark Gray text
            4:    (Color(237, 224, 200), Color(119, 110, 101)), # Beige background, Dark Gray text
            8:    (Color(242, 177, 121), Color(249, 246, 242)), # Orange background, White text
            16:   (Color(245, 149, 99),  Color(249, 246, 242)), # Dark Orange background, White text
            32:   (Color(246, 124, 95),  Color(249, 246, 242)), # Reddish Orange background, White text
            64:   (Color(246, 94, 59),   Color(249, 246, 242)), # Red background, White text
            128:  (Color(237, 207, 114), Color(249, 246, 242)), # Yellow background, White text
            256:  (Color(237, 204, 97),  Color(249, 246, 242)), # Dark Yellow background, White text
            512:  (Color(237, 200, 80),  Color(249, 246, 242)), # Gold background, White text
            1024: (Color(237, 197, 63),  Color(249, 246, 242)), # Dark Gold background, White text
            2048: (Color(237, 194, 46),  Color(249, 246, 242)), # 2048 Gold background, White text
        }
        # Default super dark color if the number is not in the list (in case the game continues beyond 2048)
        default_bg = Color(60, 58, 50)
        default_fg = Color(249, 246, 242)
        return colors.get(self.number, (default_bg, default_fg))

    def draw(self, position, length=1):
        bg_color, fg_color = self.get_colors()

        # Background
        stddraw.setPenColor(bg_color)
        stddraw.filledSquare(position.x, position.y, length / 2)

        # Boundary (Box)
        stddraw.setPenColor(self.box_color)
        stddraw.setPenRadius(Tile.boundary_thickness)
        stddraw.square(position.x, position.y, length / 2)
        stddraw.setPenRadius()

        # Text (Number)
        stddraw.setPenColor(fg_color)
        stddraw.setFontFamily(Tile.font_family)
        stddraw.setFontSize(Tile.font_size)
        stddraw.text(position.x, position.y, str(self.number))
        
