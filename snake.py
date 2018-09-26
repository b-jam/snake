import random
import time
from pynput import keyboard


class Snake:
    """
    A snake has a head point,
    A direction vector (row, col) with top left 0,0
    And a list of tail points
    """

    def __init__(
        self, head_position, direction, tail_points
    ):
        self.head_position = head_position
        self.direction = direction
        self.tail_points = tail_points

    def point_in_snake(self, point):
        if (
            point == self.head_position
            or point in self.tail_points
        ):
            return True
        return False

    def length(self):
        return 1 + len(self.tail_points)

    def move(self, grid):
        """
        To move the snake
        Find the new head position
        Check if you've collided with yourself
        Check if you've hit the wall
        Move the current head into the tail
        
        If eating food, don't move the end of the tail and place new food
        Otherwise remove the end of the tail to keep same length
        """
        new_head_pos = self.head_position + self.direction
        if new_head_pos in self.tail_points:
            raise Exception(
                "You ate yourself. length {0}".format(
                    self.length()
                )
            )
        grid.check_point_valid(new_head_pos)
        self.tail_points.insert(0, self.head_position)
        self.head_position = new_head_pos
        if new_head_pos == grid.food_position:
            grid.place_food()
        else:
            grid.set_blank(self.tail_points[-1])
            self.tail_points = self.tail_points[:-1]


class Point:
    """
    A class to represent a (row, col) point on the grid
    (0,0) is top left
    Points can be compared using ==, or added with another Point using +

    For the purposes here, the direction vector is also represented using a point class
    """

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if isinstance(other, Point):
            return (
                self.row == other.row
                and self.col == other.col
            )
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(
                self.row + other.row, self.col + other.col
            )
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Point):
            return Point(
                self.row + other.row, self.col + other.col
            )
        return NotImplemented

    def __str__(self):
        return "({0},{1})".format(self.row, self.col)


class Grid:
    """
    A class which stores the grid
    The snake
    and the location of the food.

    Printing this class is the main display
    """

    def __init__(self, rows, cols):
        self.grid = [[" "] * cols for row in range(rows)]
        self.snake = self.initial_snake()
        self.place_food()

    def place_food(self):
        """
        Place a food on the grid,
        making sure it's not a point in the snake already
        """
        points = [
            Point(row, col)
            for row in range(len(self.grid))
            for col in range(len(self.grid[0]))
            if not (
                self.snake.point_in_snake(Point(row, col))
            )
        ]
        point = random.choice(points)
        self.food_position = point

    def draw_food(self):
        """set the grid square which contains food to the right character"""
        self.grid[self.food_position.row][
            self.food_position.col
        ] = "*"

    def draw_snake(self):
        """set the grid squares which contains the snake to the right characters"""
        self.grid[self.snake.head_position.row][
            self.snake.head_position.col
        ] = "="
        for point in self.snake.tail_points:
            self.grid[point.row][point.col] = "-"

    def set_blank(self, point):
        self.grid[point.row][point.col] = " "

    def initial_snake(self):
        """The initial snake always starts in the top left, going right"""
        return Snake(
            Point(0, 1), Point(0, 1), [Point(0, 0)]
        )

    def check_point_valid(self, point):
        if (
            point.row < 0
            or point.row >= len(self.grid)
            or point.col < 0
            or point.col >= len(self.grid[0])
        ):
            raise Exception(
                "You Lost. Length {0}".format(
                    self.snake.length()
                )
            )

    def redraw(self):
        """update snake position in display and update food position"""
        self.draw_snake()
        self.draw_food()
        print(self)

    def update_time(self):
        """Update time by moving the snake and redrawing grid"""
        self.snake.move(self)
        self.redraw()

    def __str__(self):
        output = "\n"
        for row in self.grid:
            output += "|" + "".join(row) + "|\n"
        return output


class KeyListener:
    """A representation of key controls and the actions triggered"""

    keyboard_directions = {
        "up": Point(-1, 0),
        "left": Point(0, -1),
        "down": Point(1, 0),
        "right": Point(0, 1),
        "w": Point(-1, 0),
        "a": Point(0, -1),
        "s": Point(1, 0),
        "d": Point(0, 1),
    }

    def __init__(self, snake):
        self.snake = snake

    def on_press(self, key):
        try:
            k = key.char
        except:
            k = key.name
        self.snake.direction = self.keyboard_directions[k]

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False  # exit on escape


def main():
    """
    The main loop has the keylistener running in a seperate
    thread to listen for keyboard events
    """
    grid = Grid(15, 20)
    keylisten = KeyListener(grid.snake)
    with keyboard.Listener(
        on_press=keylisten.on_press,
        on_release=keylisten.on_release,
    ) as listener:

        while True:
            time.sleep(0.2)
            grid.update_time()


if __name__ == "__main__":
    main()
