"""
PyPortal Calculator Demo
"""
import time
from collections import namedtuple
import board
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_button import Button
from calculator import Calculator
import adafruit_touchscreen

Coords = namedtuple("Point", "x y")

# Settings
SCREEN_WIDTH = board.DISPLAY.width
SCREEN_HEIGHT = board.DISPLAY.height
BUTTON_WIDTH = SCREEN_WIDTH // 5
BUTTON_HEIGHT = SCREEN_HEIGHT // 7
BUTTON_X_MARGIN = (SCREEN_WIDTH - (BUTTON_WIDTH*4))//5
BUTTON_Y_MARGIN = (SCREEN_HEIGHT - (BUTTON_HEIGHT*6))//7

# Colors
BLACK = 0x0
ORANGE = 0xFF8800
BLUE = 0x0088FF
WHITE = 0xFFFFFF
GRAY = 0x888888

ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(SCREEN_WIDTH, SCREEN_HEIGHT)
)

# Make the display context
calc_group = displayio.Group()
board.DISPLAY.show(calc_group)

# Make a background color fill
color_bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = GRAY
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette)
calc_group.append(bg_sprite)

# Load the font
if SCREEN_WIDTH < 480:
    # Small screen font
    font = bitmap_font.load_font("/fonts/Arial-12.bdf")
else:
    # Large screen font
    font = bitmap_font.load_font("/fonts/Arial-Bold-24.bdf")

buttons = []


# Some button functions
def button_grid(row, col):
    return Coords(BUTTON_X_MARGIN * (col+1) + BUTTON_WIDTH * col,
                  BUTTON_Y_MARGIN * (row+2) + BUTTON_HEIGHT * (row+1))


def add_button(row, col, label, width=1, color=WHITE, text_color=BLACK):
    pos = button_grid(row, col)
    new_button = Button(x=pos.x, y=pos.y,
                        width=BUTTON_WIDTH * width + BUTTON_X_MARGIN * (width - 1),
                        height=BUTTON_HEIGHT, label=label, label_font=font,
                        label_color=text_color, fill_color=color, style=Button.ROUNDRECT)
    buttons.append(new_button)
    return new_button


def find_button(label):
    result = None
    for btn in buttons:
        if btn.label == label:
            result = btn
    return result


border = Rect(
    BUTTON_X_MARGIN, BUTTON_Y_MARGIN, SCREEN_WIDTH-(2*BUTTON_X_MARGIN), BUTTON_HEIGHT,
    fill=WHITE, outline=BLACK, stroke=2
)
calc_display = Label(
    font, text="0", color=BLACK, anchor_point=(1.0, 0.5),
    anchored_position=(SCREEN_WIDTH-BUTTON_X_MARGIN-5, BUTTON_Y_MARGIN+(BUTTON_HEIGHT//2))
)

clear_button = add_button(0, 0, "AC")
add_button(0, 1, "+/-")
add_button(0, 2, "%")
add_button(0, 3, "/", 1, ORANGE, WHITE)
add_button(1, 0, "7")
add_button(1, 1, "8")
add_button(1, 2, "9")
add_button(1, 3, "x", 1, ORANGE, WHITE)
add_button(2, 0, "4")
add_button(2, 1, "5")
add_button(2, 2, "6")
add_button(2, 3, "-", 1, ORANGE, WHITE)
add_button(3, 0, "1")
add_button(3, 1, "2")
add_button(3, 2, "3")
add_button(3, 3, "+", 1, ORANGE, WHITE)
add_button(4, 0, "0", 2)
add_button(4, 2, ".")
add_button(4, 3, "=", 1, BLUE, WHITE)

# Add the display and buttons to the main calc group
calc_group.append(border)
calc_group.append(calc_display)
for b in buttons:
    calc_group.append(b)

calculator = Calculator(calc_display, clear_button)

button = ""
while True:
    point = ts.touch_point
    if point is not None:
        # Button Down Events
        for b in buttons:
            if b.contains(point) and button == "":
                b.selected = True
                button = b.label
    elif button != "":
        # Button Up Events
        last_op = calculator.get_current_operator()
        op_button = find_button(last_op)
        # Deselect the last operation when certain buttons are pressed
        if op_button is not None:
            if button in ('=', 'AC', 'CE'):
                op_button.selected = False
            elif button in ('+', '-', 'x', '/') and button != last_op:
                op_button.selected = False
        calculator.add_input(button)
        b = find_button(button)
        if b is not None:
            if button not in ('+', '-', 'x', '/') or button != calculator.get_current_operator():
                b.selected = False
        button = ""
    time.sleep(0.05)
