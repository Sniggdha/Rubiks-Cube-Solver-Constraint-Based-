import pygame
import sys
import random
import math
import cv2
import numpy as np
import kociemba

# Initialize pygame
pygame.init()

# Set up the display screen with fullscreen mode and fetch width and height
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

# Define button dimensions and spacing
button_width, button_height = 200, 70
button_spacing = 60
num_buttons = 4          # Number of main buttons
num_camera_buttons = 3    # Number of camera-related buttons

# Calculate the total width of all buttons combined
total_buttons_width = num_buttons * button_width + (num_buttons - 1) * button_spacing
total_camera_buttons_width = num_camera_buttons * button_width + (num_camera_buttons - 1) * button_spacing

# Calculate the starting x-coordinates to center buttons
start_x_buttons = (width - total_buttons_width) // 2
start_x_camera_buttons = (width - total_camera_buttons_width) // 2

# Define camera feed display properties
camera_width = 900
camera_height = 550
camera_x = (width - camera_width) // 2
camera_y = (height - camera_height) // 2 - 50
camera_border = 10
camera_feed_rect = pygame.Rect(camera_x + camera_border, camera_y + camera_border, camera_width - 2 * camera_border, camera_height - 2 * camera_border)
button_y = camera_y + camera_height + 100

# Load waterdrop image and define highlight color
waterdrop_image = pygame.image.load('drop.png')
droplet_highlight = (0, 255, 255)

# Define color constants
BLUE = (0, 120, 255)
GREEN = (57, 255, 20)
YELLOW = (255, 255, 0)
PINK = (255, 20, 147)
PURPLE = (180, 0, 255)
ORANGE = (255, 120, 0)
RED = (255, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
droplet_highlight = WHITE

# HSV color ranges for detecting Rubik's Cube colors using a camera
hsvColors = {
    'Blue': [0, [0, 100, 100], [30, 255, 255]],
    'Green': [0, [30, 100, 100], [75, 255, 255]],
    'Red': [0, [118, 120, 120], [140, 255, 255]],
    'Orange': [0, [100, 120, 120], [118, 255, 255]],
    'White': [0, [0, 0, 75], [180, 45, 255]],
    'Yellow': [0, [75, 100, 100], [100, 255, 255]]
}

# RGB color mapping for visualisation in the interface
rgbColors = {
    'Blue': (255, 0, 0), 'Green': (0, 255, 0), 'Red': (0, 0, 255),
    'Orange': (0, 125, 255), 'White': (255, 255, 255), 'Yellow': (0, 255, 255)
}

# Mapping colors to their Rubik's Cube face notation
faces = {'Green': 'F', 'Red': 'R', 'Orange': 'L', 'Blue': 'B', 'White': 'U', 'Yellow': 'D'}
face_to_color = {v: k for k, v in faces.items()}

# List to store solution moves and a counter for solution length
moves_list = []
solution_length = 0

# Representation of the Rubik's Cube as a 2D array for each face
# Each face is a 3x3 grid of color codes
a = [
    [['G', 'G', 'G'], ['G', 'G', 'G'], ['G', 'G', 'G']],  # Front face (Green)
    [['R', 'R', 'R'], ['R', 'R', 'R'], ['R', 'R', 'R']],  # Right face (Red)
    [['B', 'B', 'B'], ['B', 'B', 'B'], ['B', 'B', 'B']],  # Back face (Blue)
    [['O', 'O', 'O'], ['O', 'O', 'O'], ['O', 'O', 'O']],  # Left face (Orange)
    [['W', 'W', 'W'], ['W', 'W', 'W'], ['W', 'W', 'W']],  # Up face (White)
    [['Y', 'Y', 'Y'], ['Y', 'Y', 'Y'], ['Y', 'Y', 'Y']]   # Down face (Yellow)
]

# Unique IDs for each cubie on the cube for tracking during rotations
CUBIE_IDS = {
    'U': [37, 38, 39, 40, 41, 42, 43, 44, 45],
    'L': [28, 29, 30, 31, 32, 33, 34, 35, 36],
    'F': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'R': [10, 11, 12, 13, 14, 15, 16, 17, 18],
    'B': [19, 20, 21, 22, 23, 24, 25, 26, 27],
    'D': [46, 47, 48, 49, 50, 51, 52, 53, 54]
}

# Pairs of cubie positions used for rotation calculations
CUBIE_PAIRS = {
    2: 44, 44: 2, 4: 33, 33: 4, 6: 13, 13: 6, 8: 47, 47: 8,
    38: 20, 20: 38, 40: 29, 29: 40, 42: 11, 11: 42, 22: 15, 15: 22,
    24: 31, 31: 24, 26: 53, 53: 26, 35: 49, 49: 35, 17: 51, 51: 17,
    1: (30, 43), 30: (1, 43), 43: (1, 30), 3: (45, 10), 45: (3, 10), 10: (3, 45),
    7: (36, 46), 36: (7, 46), 46: (7, 36), 9: (16, 48), 16: (9, 48), 48: (9, 16),
    12: (19, 39), 19: (12, 39), 39: (12, 19), 18: (25, 54), 25: (18, 54), 54: (18, 25),
    28: (21, 37), 21: (28, 37), 37: (28, 21), 34: (27, 52), 27: (34, 52), 52: (34, 27),
    5: 5, 14: 14, 23: 23, 32: 32, 41: 41, 50: 50
}

# Set the title of the window
pygame.display.set_caption("Rubik's Cube Solver")

# Instructions for the user
instructions_text = [
    "Key Controls:",
    "'Spacebar' - 'Capture the face' and 'Esc' - 'Exit'",
    "",
    "Scanning Process:",
    "1. Press 'Start Game' then 'Scan Cube' and follow the on-screen grid guide.",
    "2. Hold each face as instructed '(Watch the top colour!)'.",
    "3. Press 'Spacebar' to capture each face.",
    "4. Cube Displayed? Click the 'Waterdrop Button' to fix a cubie.",
    "",
    "Solving Process:",
    "Keep 'Green Middle' facing you with 'white middle' facing up.",
    "1. 'Solve Cube' - Start the solving journey.",
    "2. 'Pause' - Temporarily stop; 'Resume' - Continue; 'Next' - Step through moves.",
    "3. 'Speed Slider' - Control the pace of the solver.",
    "",
    "Celebrate your success and choose to 'Play Again' or 'Exit'.",
    "",
    "Good lighting = Better scanning.",
    "Not happy with a scan? Scan again!",
]

# Join the instructions with newline characters
formatted_instructions = "\n".join(instructions_text)

# Guide for moves with a table for reference
Move_Guide_text = [
    [
        ["Front", "F"],
        ["Left", "L"],
        ["Right", "R"],
        ["Back", "B"],
        ["Up", "U"],
        ["Down", "D"],
        ["Equator slice", "E"],
        ["Middle slice", "M"],
        ["Standing slice", "S"]
    ],
    [
        ["Front Anticlockwise", "Fi"],
        ["Left Anticlockwise", "Li"],
        ["Right Anticlockwise", "Ri"],
        ["Back Anticlockwise", "Bi"],
        ["Up Anticlockwise", "Ui"],
        ["Down Anticlockwise", "Di"],
        ["Equator slice Anticlockwise", "Ei"],
        ["Middle slice Anticlockwise", "Mi"],
        ["Standing slice Anticlockwise", "Si"]
    ],
    [
        ["Front Rotation Twice", "F2"],
        ["Left Rotation Twice", "L2"],
        ["Right Rotation Twice", "R2"],
        ["Back Rotation Twice", "B2"],
        ["Up Rotation Twice", "U2"],
        ["Down Rotation Twice", "D2"],
        ["Equator slice Twice", "E2"],
        ["Middle slice Twice", "M2"],
        ["Standing slice Twice", "S2"]
    ]
]

# Algorithm description text
About_Algorithm_text = "\n".join([
    "Meet the Kociemba Algorithm, your trusty guide to mastering the Rubik's Cube in no time.",
    "",
    "Phase 1: The Simplification Spell! Imagine turning your complex puzzle into a simpler one. That’s what this phase does! It brings your cube into a special state called the “cross.” Here, you’re allowed to make only quarter turns on the Up and Down faces, and half turns on any face. This clever trick narrows down the many ways your cube can be scrambled, making it easier to tackle!",
    "",
    "Phase 2: The Finishing Touch! Now that your cube is in its simpler state, it’s time for the magic to happen! The Kociemba Algorithm has a set of secret moves ready to go. This phase focuses on solving the remaining pieces, ensuring every color is in its right place. It’s like a grand finale where everything falls into place!",
    "",
    "This incredible algorithm is known for its speed and efficiency, solving any cube configuration in 20 moves or fewer! Mastering the Kociemba Algorithm opens the door to advanced solving techniques and a smoother cubing experience."
])

# Define font path
font_path = pygame.font.match_font('arial')

# Rotating cube function that renders a rotating cube on the screen
def cube_animation(surface, size, rotation_angle_x, rotation_angle_y, vertical_offset=50):
    """
    Draws a rotating cube animation on the given surface.

    Args:
        surface (pygame.Surface): The surface to draw on.
        size (int): The base size of the cube.
        rotation_angle_x (float): Rotation angle along the X-axis.
        rotation_angle_y (float): Rotation angle along the Y-axis.
        vertical_offset (int): Offset to adjust the vertical position of the cube.
    """
    scale_factor = 1.2  # Scaling factor for cube size
    scaled_size = size * scale_factor
    colors = [RED, GREEN, BLUE, YELLOW, ORANGE, WHITE]
    
    # Calculate trigonometric values for rotation
    cos_x, sin_x = math.cos(rotation_angle_x), math.sin(rotation_angle_x)
    cos_y, sin_y = math.cos(rotation_angle_y), math.sin(rotation_angle_y)

    # Define initial vertices of a unit cube
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]

    # Apply rotation to cube vertices
    rotated_vertices = []
    for v in vertices:
        rx = v[0] * cos_y - v[2] * sin_y
        ry = v[1]
        rz = v[0] * sin_y + v[2] * cos_y
        ry = ry * cos_x - rz * sin_x
        rz = ry * sin_x + rz * cos_x
        rotated_vertices.append([rx, ry, rz])

    # Define faces of the cube 
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 4, 7, 3],
        [1, 5, 6, 2], [3, 2, 6, 7], [0, 1, 5, 4]
    ]

    # Sort faces by depth to render back faces first
    sorted_faces = sorted(
        [(face, sum(rotated_vertices[i][2] for i in face)) for face in faces],
        key=lambda x: x[1], 
        reverse=True
    )
     # Get surface dimensions for rendering
    width, height = surface.get_size()

    # Render each face of the cube
    for face, _ in sorted_faces:
        points = [
            (int(x * scaled_size // 2 + width // 2), 
             int(y * scaled_size // 2 + height // 2 - vertical_offset)) 
            for x, y in [rotated_vertices[i][:2] for i in face]
        ]

        # Draw the filled polygon representing the face
        pygame.draw.polygon(surface, colors[faces.index(face)], points)
        # Outline the face
        pygame.draw.lines(surface, BLACK, True, points, 2)

        # Draw grid within the face
        for i in range(1, 3):
            start = (points[0][0] + i * (points[1][0] - points[0][0]) // 3,
                     points[0][1] + i * (points[1][1] - points[0][1]) // 3)
            end = (points[3][0] + i * (points[2][0] - points[3][0]) // 3,
                   points[3][1] + i * (points[2][1] - points[3][1]) // 3)
            pygame.draw.line(surface, BLACK, start, end, 2)
        for i in range(1, 3):
            start = (points[0][0] + i * (points[3][0] - points[0][0]) // 3,
                     points[0][1] + i * (points[3][1] - points[0][1]) // 3)
            end = (points[1][0] + i * (points[2][0] - points[1][0]) // 3,
                   points[1][1] + i * (points[2][1] - points[1][1]) // 3)
            pygame.draw.line(surface, BLACK, start, end, 2)

# Class to handle individual falling cube elements in the background
class FallingCube:
    """
    Represents an individual cube element that falls in the background.

    Attributes:
        size (int): Size of the cube.
        x (int): Horizontal position of the cube.
        y (int): Vertical position of the cube.
        speed (float): Speed at which the cube falls.
        rotation (float): Current rotation angle of the cube in radians.
        rotation_speed (float): Speed of rotation.
        color (tuple): RGB color of the cube.

    Methods:
        update(): Updates the cube's position and rotation. Resets the position if it falls out of bounds.
        draw(surface): Draws the cube on the provided Pygame surface.
    """
    def __init__(self):
        # Initial cube setup
        self.size = random.randint(10, 30)
        self.x = random.randint(0, width)
        self.y = random.randint(-100, -self.size)
        self.speed = random.uniform(0.5, 1.5)
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.05, 0.05)
        self.color = random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, WHITE])

    # Update cube's position and rotation
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        if self.y > height:
            self.y = random.randint(-100, -self.size)
            self.x = random.randint(0, width)

    # Draw falling cube on the screen
    def draw(self, surface):
        points = [
            (-self.size/2, -self.size/2),
            (self.size/2, -self.size/2),
            (self.size/2, self.size/2),
            (-self.size/2, self.size/2)
        ]
        rotated_points = [
            (x * math.cos(self.rotation) - y * math.sin(self.rotation) + self.x,
             x * math.sin(self.rotation) + y * math.cos(self.rotation) + self.y)
            for x, y in points
        ]
        pygame.draw.polygon(surface, self.color, rotated_points)
        pygame.draw.lines(surface, WHITE, True, rotated_points, 1)

# Create list of falling cubes for background effect        
falling_cubes = [FallingCube() for _ in range(20)]

# Draws background with a gradient and falling cubes
def draw_background(surface):
    """
    Draws a background with a gradient and animates falling cubes.

    Args:
        surface (pygame.Surface): The surface on which the background is drawn.

    The gradient transitions from purple at the top to blue at the bottom.
    """
    for y in range(height):
        progress = y / height
        color = (
            int(PURPLE[0] * (1 - progress) + BLUE[0] * progress),
            int(PURPLE[1] * (1 - progress) + BLUE[1] * progress),
            int(PURPLE[2] * (1 - progress) + BLUE[2] * progress)
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    for cube in falling_cubes:
        cube.update()
        cube.draw(surface)

# Button class to create buttons
class Button:
    """
    Represents an interactive button element in the UI.

    Attributes:
        original_rect (pygame.Rect): Initial dimensions of the button.
        rect (pygame.Rect): Adjusted dimensions for hover effect.
        text (str): Text displayed on the button.
        color (tuple): Base color of the button.
        hover_color (tuple): Color of the button when hovered.
        is_hovered (bool): Indicates whether the button is currently hovered.
        grow_tween (float): Tweening value for hover animation.
        image (pygame.Surface): Optional image displayed on the button.

    Methods:
        lighten_color(color, amount): Lightens a given color by a specified amount.
        draw(surface, mouse_pos): Renders the button on the surface and handles hover animations.
        is_clicked(pos): Checks if the button is clicked based on the provided position.
    """
    def __init__(self, x, y, width, height, text, color, image=None):
        # Button dimensions
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.color = color
        self.hover_color = self.lighten_color(color, 50)
        self.is_hovered = False
        self.grow_tween = 0
        self.image = image  # Store the image

    # Lighten the button color on hover
    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)

    # Draw button and handle hover effect
    def draw(self, surface, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        # Adjust button size based on hover status
        if self.is_hovered:
            self.grow_tween = min(1, self.grow_tween + 0.1)
        else:
            self.grow_tween = max(0, self.grow_tween - 0.1)
        grow_amount = 10 * self.grow_tween
        self.rect = self.original_rect.inflate(grow_amount, grow_amount)

        # Set button colors based on hover status
        main_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, main_color, self.rect, border_radius=15)
        border_color = WHITE if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=15)

        # Display text or image on button
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (self.rect.width - 10, self.rect.height - 10))
            image_rect = scaled_image.get_rect(center=self.rect.center)
            surface.blit(scaled_image, image_rect)
        elif self.text:
            font = pygame.font.Font(font_path, 24)
            text_color = BLACK if self.is_hovered else WHITE
            text_surface = font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

     # Check if the button was clicked        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Button definitions for different UI actions
buttons = [
    Button(start_x_buttons, button_y, button_width, button_height, "Instructions", PINK),
    Button(start_x_buttons + button_width + button_spacing, button_y, button_width, button_height, "Move Guide", GREEN),
    Button(start_x_buttons + 2 * (button_width + button_spacing), button_y, button_width, button_height, "About Algorithm", BLUE),
    Button(start_x_buttons + 3 * (button_width + button_spacing), button_y, button_width, button_height, "Exit", ORANGE)
]

# Main button to start the game loop and a back button to return to main menu
start_game_button = Button(width // 2 - 120, button_y - button_height - 50, 240, 80, "Start Game", PURPLE)
back_button = Button(width // 2 - button_width // 2, height - button_height - 20, button_width, button_height, "Back to Menu", GREEN)

def create_control_buttons():
    """
    Creates the control buttons for the game interface.

    Returns:
        tuple: A tuple containing three Button instances (pause, resume, and next).
    """
    # Set the initial x and y positions for the buttons based on predefined constants
    control_x = start_x_camera_buttons  # X position for the first button
    control_y = button_y  # Y position for the buttons
    pause_button = Button(control_x, control_y, button_width, button_height, "PAUSE", BLUE)
    resume_button = Button(control_x + button_width + button_spacing, control_y, button_width, button_height, "RESUME", GREEN)
    next_move_button = Button(control_x + 2 * (button_width + button_spacing), control_y, button_width, button_height, "NEXT", YELLOW)
    return pause_button, resume_button, next_move_button

# Function to draw centered text on a given surface
def draw_text(surface, text, font_size, color, y_position):
    """
    Draws a line of centered text on the given surface.

    Args:
        surface (pygame.Surface): The surface on which the text is drawn.
        text (str): The text to be displayed.
        font_size (int): Font size of the text.
        color (tuple): RGB color of the text.
        y_position (int): Vertical position of the text's center.

    The text is automatically centered horizontally.
    """
    font = pygame.font.Font(font_path, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(surface.get_width() // 2, y_position))
    surface.blit(text_surface, text_rect)

# Function to render and wrap long text to fit within a given width
def draw_wrapped_text(surface, text, font_size, color, x_or_rect, y=None, aa=True):
    """
    Renders and wraps long text to fit within a specified width, breaking the text into multiple lines if needed.

    Parameters:
        surface (pygame.Surface): The surface on which to render the text.
        text (str): The text to be rendered.
        font_size (int): The font size to use for rendering the text.
        color (tuple): The color of the text (R, G, B).
        x_or_rect (int or pygame.Rect): The x-coordinate or rectangle defining the area for text placement.
        y (int, optional): The y-coordinate for the text placement, used if x_or_rect is an integer.
        aa (bool, optional): Whether to apply anti-aliasing for smoother text rendering. Defaults to True.
    """
    try:
        font = pygame.font.Font(None, font_size)
    except Exception:
        font = pygame.font.SysFont('arial', font_size)
    
    # Split text into lines while keeping line breaks
    lines = text.splitlines(keepends=True)
    
    # Determine maximum width based on x_or_rect argument
    if isinstance(x_or_rect, pygame.Rect):
        rect = x_or_rect
        max_width = rect.width - 40
        x = rect.left + 20
        y = rect.top + 20 if y is None else y
    else:
        x = x_or_rect
        max_width = surface.get_width() - x - 40 # Fit within screen width
    
    # Get the width of a space character for line-wrapping calculations
    space_width = font.size(' ')[0]
    current_y = y
    
    for line in lines:
        # Skip to next line if current line is empty
        if line.strip() == '':
            current_y += font.get_linesize()
            continue

        # Split line into individual words for wrapping    
        words = line.strip().split()  # Split each line into words
        current_width = 0 # Initialize current width tracker
        wrapped_line = [] # Store words in the current line to be drawn
        
        for word in words:
            # Render word and get its width
            word_surface = font.render(word, aa, color)
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                wrapped_line.append(word)
                current_width += word_width + space_width
            else:
                if wrapped_line:
                    line_surface = font.render(' '.join(wrapped_line), aa, color)
                    surface.blit(line_surface, (x, current_y))
                    current_y += font.get_linesize()
                wrapped_line = [word] # Start new line with the current word
                current_width = word_width + space_width
        
        # Render remaining words in the last wrapped line
        if wrapped_line:
            line_surface = font.render(' '.join(wrapped_line), aa, color)
            surface.blit(line_surface, (x, current_y))
            current_y += font.get_linesize()

# Function to render wrapped text with a background box
def draw_text_in_rect(surface, text, font_size, color, rect, bg_color=(180, 0, 255, 50)):
    """
    Renders wrapped text with a background box behind it to ensure readability.

    Parameters:
        surface (pygame.Surface): The surface on which to render the text and background.
        text (str): The text to be rendered.
        font_size (int): The font size for the text.
        color (tuple): The color of the text (R, G, B).
        rect (pygame.Rect): The rectangle defining the area where the text will be rendered.
        bg_color (tuple, optional): The background color of the box. Defaults to a semi-transparent purple.
    """
    background_rect = rect.inflate(40, 40)
    background_surface = pygame.Surface(background_rect.size, pygame.SRCALPHA)
    background_surface.fill(bg_color)
    surface.blit(background_surface, background_rect.topleft)
    draw_wrapped_text(surface, text, font_size, color, rect)

# Function to draw a Move Guide table within a given rect area
def draw_move_guide(surface, rect):
    """
    Draws a table displaying movement instructions in a specified rectangle area.

    Parameters:
        surface (pygame.Surface): The surface on which to render the table.
        rect (pygame.Rect): The rectangle area where the table will be drawn.
    """
    table_width = (rect.width - 40) // 3    
    cell_height = 50    
    padding = 20    
    font = pygame.font.Font(font_path, 22)    
    y_offset = 80    
    spacing = 60
    total_width = 3 * table_width + 2 * spacing
    start_x = rect.left + (rect.width - total_width) // 2

    for table_index, table in enumerate(Move_Guide_text):
        table_x = start_x + table_index * (table_width + spacing)
        for i, (action, key) in enumerate(table):
            # Define cell rect for action-key pair
            cell_rect = pygame.Rect(table_x, rect.top + y_offset + i * cell_height, table_width, cell_height)
            # Draw cell background and outline
            pygame.draw.rect(surface, (*PURPLE, 128), cell_rect)
            pygame.draw.rect(surface, WHITE, cell_rect, 1)
            # Render action and key text and position within cell
            action_surf = font.render(action, True, WHITE)
            key_surf = font.render(key, True, WHITE)
            action_rect = action_surf.get_rect(midleft=(cell_rect.left + padding, cell_rect.centery))
            key_rect = key_surf.get_rect(midright=(cell_rect.right - padding, cell_rect.centery))
            # Draw action and key text onto cell
            surface.blit(action_surf, action_rect)
            surface.blit(key_surf, key_rect)

# Function to show a popup message with buttons
def show_popup_message(surface, message, buttons=None, is_congratulations=False):
    """
    Displays a popup message with optional buttons and a background overlay. Can also display a congratulatory message.

    Parameters:
        surface (pygame.Surface): The surface on which to display the popup.
        message (str): The message to display in the popup.
        buttons (list, optional): A list of Button objects to be displayed in the popup. Defaults to an "OK" button.
        is_congratulations (bool, optional): Whether the message is a congratulatory message. Defaults to False.

    Returns:
        str: The text of the button that was clicked (if any).
    """
    # Dimensions and Positions
    popup_width = 600
    popup_height = 300
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    # Create a semi-transparent overlay for the popup background
    overlay = pygame.Surface((width, height))
    overlay.fill(BLACK)
    overlay.set_alpha(180)
    surface.blit(overlay, (0, 0))

    # Draw popup background with light lavender color
    POPUP_BG = (180, 180, 230)  # Very light lavender
    pygame.draw.rect(surface, POPUP_BG, popup_rect)

    # Set border color based on message type
    border_color = ORANGE if is_congratulations else (147, 112, 219)
    pygame.draw.rect(surface, border_color, popup_rect, 4)

    # Display congratulatory message if specified
    if is_congratulations:
        total_text_height = 56 + 40  # Main text + subtitle font sizes
        start_y = popup_y + (popup_height - total_text_height - 60) // 2
        font = pygame.font.Font(font_path, 56)

        text = font.render("CONGRATULATIONS!", True, BLACK)
        shadow = font.render("CONGRATULATIONS!", True, ORANGE)
        text_rect = text.get_rect(center=(width // 2, start_y))
        shadow_rect = text_rect.move(2, 2)
        surface.blit(shadow, shadow_rect)
        surface.blit(text, text_rect)
        # Render subtitle
        sub_font = pygame.font.Font(font_path, 40)
        sub_text = sub_font.render(message, True, BLACK)
        sub_text_rect = sub_text.get_rect(center=(width // 2, start_y + 70))
        surface.blit(sub_text, sub_text_rect)
    else:
        # Draw regular message in popup if not congratulatory
        message_rect = popup_rect.inflate(-40, -100)
        message_rect.centery = popup_rect.centery - 20
        draw_wrapped_text(surface, message, 36, WHITE, message_rect)

    # Set up OK button if no other buttons are provided    
    if buttons is None:
        buttons = [
            Button(
                popup_x + (popup_width - 200) // 2,
                popup_y + popup_height - 70,
                200, 50,
                "OK",
                GREEN
            )
        ]

    # Draw each button and detect clicks    
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.is_hovered = button.rect.collidepoint(mouse_pos)
        button.draw(surface, mouse_pos)
    pygame.display.flip()

    # Event loop for waiting on button click
    waiting = True
    result = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        result = button.text  # Capture the button text as the result
                        waiting = False  # Break the loop
                        break  # Exit the button loop

        pygame.display.flip()

    return result

def camera_permissions():
    """
    Displays a permission prompt asking the user to agree to allow camera access. If accepted, the camera is initialized.

    Returns:
        bool: True if the user agrees to allow camera access, False if the user disagrees.
    """
    agreement_surface = pygame.Surface((width, height))
    agree_button = Button(width // 2 - 100, height // 2 + 50, 250, 60, "Agree", BLUE)
    disagree_button = Button(width // 2 - 100, height // 2 + 130, 250, 60, "Disagree", RED)
    buttons = [agree_button, disagree_button]

    title_font = pygame.font.Font(font_path, 72)
    title_shadow = title_font.render("Rubik's Cube Adventure", True, BLACK)
    title = title_font.render("Rubik's Cube Adventure", True, PINK)
    shadow_rect = title_shadow.get_rect(center=(width // 2 + 3, 103))
    title_rect = title.get_rect(center=(width // 2, 100))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if agree_button.is_clicked(mouse_pos):
                    global camera
                    camera = cv2.VideoCapture(0)
                    return True
                elif disagree_button.is_clicked(mouse_pos):
                    pygame.quit()
                    sys.exit()
        draw_background(agreement_surface)

        # Draw title with shadow
        agreement_surface.blit(title_shadow, shadow_rect)
        agreement_surface.blit(title, title_rect)

        # Display messages
        draw_text(agreement_surface, "This game requires access to your camera.", 40, WHITE, height // 2 - 50)
        draw_text(agreement_surface, "Do you agree to allow using camera?", 40, WHITE, height // 2)

        # Draw buttons
        for button in buttons:
            button.draw(agreement_surface, mouse_pos)

        screen.blit(agreement_surface, (0, 0))
        pygame.display.flip()

class Slider:
    """
    A class representing a vertical slider widget.

    Attributes:
        rect (pygame.Rect): Rectangle representing the slider track.
        min_value (int): Minimum value of the slider.
        max_value (int): Maximum value of the slider.
        value (int): Current value of the slider.
        is_dragging (bool): Flag indicating if the slider is being dragged.
        handle_width (int): Width of the slider handle.
        handle_height (int): Height of the slider handle.

    Methods:
        draw(surface): Draws the slider and its handle on the specified surface.
        is_clicked(mouse_pos): Checks if the slider or handle is clicked.
        update(mouse_pos): Updates the slider value based on the mouse position.
    """
    def __init__(self, x, y, height=500, min_value=0, max_value=100, initial_value=50):
        """
        Initializes a slider instance with given position, size, and value range.

        Args:
            x (int): The x-coordinate of the top-left corner of the slider.
            y (int): The y-coordinate of the top-left corner of the slider.
            height (int, optional): The height of the slider (default is 500).
            min_value (int, optional): The minimum value of the slider (default is 0).
            max_value (int, optional): The maximum value of the slider (default is 100).
            initial_value (int, optional): The initial value of the slider (default is 50).
        """
        # Create a rectangle representing the slider's track
        self.rect = pygame.Rect(x, y, 20, height)
        self.min_value = min_value
        self.max_value = max_value 
        self.value = initial_value
        self.is_dragging = False
        self.handle_width = 30
        self.handle_height = 30

    def draw(self, surface):
        """
        Draws the slider, including its track and handle, on the specified surface.

        Args:
            surface (pygame.Surface): The surface to draw the slider on.
        """
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=5)
        
        #y position of the handle based on the current value
        handle_y = self.rect.top + (self.rect.height - self.handle_height) * (
            (self.value - self.min_value) / (self.max_value - self.min_value)
        )
        handle_x = self.rect.left + (self.rect.width - self.handle_width) // 2  # Center the handle horizontally
        handle_rect = pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)  # Create the handle rectangle
        
        # Draw the handle
        pygame.draw.rect(surface, (180, 0, 255), handle_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), handle_rect, 2, border_radius=10)

        #labels
        font = pygame.font.Font(None, 36)
        high_speed_text = font.render("+", True, (255, 255, 255))
        low_speed_text = font.render("-", True, (255, 255, 255))
        surface.blit(high_speed_text, (self.rect.centerx - high_speed_text.get_width() // 2, self.rect.top - 40))
        surface.blit(low_speed_text, (self.rect.centerx - low_speed_text.get_width() // 2, self.rect.bottom + 10))

    def is_clicked(self, mouse_pos):
        """
        Checks if the slider or handle is clicked.

        Args:
            mouse_pos (tuple): The (x, y) position of the mouse cursor.

        Returns:
            bool: True if the slider or handle is clicked, otherwise False.
        """
        handle_y = self.rect.top + (self.rect.height - self.handle_height) * (
            (self.value - self.min_value) / (self.max_value - self.min_value)
        )
        handle_x = self.rect.left + (self.rect.width - self.handle_width) // 2
        handle_rect = pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)
        return handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        """
        Updates the slider value based on the mouse position.

        Args:
            mouse_pos (tuple): The (x, y) position of the mouse cursor.
        """
        if self.is_dragging:
            relative_y = mouse_pos[1] - self.rect.top
            normalized_value = relative_y / self.rect.height
            new_value = self.min_value + (self.max_value - self.min_value) * normalized_value
            self.value = max(self.min_value, min(new_value, self.max_value))

def bgr_to_rgb(bgr_color):
    """
    Converts a color from BGR to RGB format.

    Args:
        bgr_color (tuple): The color in BGR format.

    Returns:
        tuple: The color in RGB format.
    """
    return tuple(reversed(bgr_color))

def draw_cube_face(surface, face_data, x, y, size):
    """
    Draws a single face of the Rubik's Cube on the surface.

    Args:
        surface (pygame.Surface): The surface to draw the face on.
        face_data (list): A list of 9 color values representing the face's 3x3 grid.
        x (int): The x-coordinate of the top-left corner of the face.
        y (int): The y-coordinate of the top-left corner of the face.
        size (int): The size of the face (length of each side).
    """
    cell_size = size // 3  # Calculate the size of each individual cell in the 3x3 grid

    # Loop through each cell in the 3x3 grid
    for i in range(3):
        for j in range(3):
            color_code = face_data[i * 3 + j]
            # Convert the color code to RGB using the predefined mapping
            rgb_color = bgr_to_rgb(rgbColors[face_to_color[color_code]])
            pygame.draw.rect(surface, rgb_color, (x + j * cell_size, y + i * cell_size, cell_size, cell_size))
            pygame.draw.rect(surface, BLACK, (x + j * cell_size, y + i * cell_size, cell_size, cell_size), 1)
    pygame.draw.rect(surface, BLACK, (x, y, size, size), 2)

def scan_cube(surface):
    """
    Scans the Rubik's Cube using the camera and returns the colors of the faces.

    Args:
        surface (pygame.Surface): The surface to display the camera feed on.

    Returns:
        list: A list of lists containing the color data for each face.
        None: If the scanning process is cancelled.
    """
    global camera
    if camera.isOpened():
        camera.release()
    camera = cv2.VideoCapture(0)

    # Rectangle to indicate the camera view area
    pygame.draw.rect(surface, droplet_highlight, (camera_x, camera_y, camera_width, camera_height), camera_border)

    scanned_faces = []  # List to hold the colors of the scanned faces

    # Define the configuration for the faces to be scanned
    # Face name, middle color, top color
    face_configs = [
        ("Front", "Green", "White"),
        ("Right", "Red", "White"),
        ("Back", "Blue", "White"),
        ("Left", "Orange", "White"),
        ("Up", "White", "Blue"),
        ("Down", "Yellow", "Green")
    ]

    # Iterate over each face configuration to scan the face
    for face_name, middle_color, top_color in face_configs:
        # Call the scan_face function to capture the colors of the current face
        face_colors = scan_face(surface, face_name, middle_color, top_color)

        # Check if the scanning was cancelled
        if face_colors is None:
            print("Scanning cancelled.")
            return None  # Exit the function and return None
        
        # Append the scanned colors to the list of scanned faces
        scanned_faces.append(face_colors)

    camera.release()
    cv2.destroyAllWindows()

    return scanned_faces  # Return the list of scanned face colors

def scan_face(surface, face_name, middle_color, top_color):
    """
    Scans a single face of the Rubik's Cube and returns the color data.

    Args:
        surface (pygame.Surface): The surface to display the camera feed on.
        face_name (str): The name of the face being scanned (e.g., "Front").
        middle_color (str): The expected color of the middle cubie.
        top_color (str): The color on top of the cube during scanning.

    Returns:
        list: A list of 9 color values representing the cubies of the face.
        None: If the scanning process is cancelled.
    """
    # Initialize a list to hold the detected colors for the 9 cubies
    data = ['' for _ in range(9)]
    error_message = ""  # Initialize an empty error message

    # Loop to read frames from the camera
    while True:
        ret, img = camera.read()  # Capture a frame from the camera
        if not ret:
            print("Failed to grab frame")
            continue  # Skip to the next iteration if capture fails

        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)  # Convert the image to HSV
        middle_cubie_color = None

        # Loop over each cubie position in the 3x3 grid
        for i in range(3):
            for j in range(3):
                x, y = 500 + 120 * j, 240 + 120 * i  # Calculate the center position of the cubie
                bestColor, bestValue = 'White', 0  # Initialize best color and value

                # Check against all predefined HSV colors
                for key, color in hsvColors.items():
                    # Create a mask to isolate colors in the specified area
                    mask = cv2.inRange(hsv[y-60:y+60, x-60:x+60], 
                                       np.array(color[1]), 
                                       np.array(color[2]))
                    avg = np.average(mask)  # Calculate the average value of the mask
                    # Update the best color if the average exceeds the previous best
                    if avg > bestValue:
                        bestValue, bestColor = avg, key
                
                # Assign the detected color to the data list
                data[3 * i + j] = faces[bestColor]
                # If it's the middle cubie, store its color for later verification
                if i == j == 1:
                    middle_cubie_color = bestColor

                # Draw a rectangle around the detected color on the image
                cv2.rectangle(img, (x-60, y-60), (x+60, y+60), 
                              rgbColors[bestColor], 3)

        # Convert the image back to RGB for rendering with Pygame
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Create a Pygame surface from the image array
        img_surface = pygame.surfarray.make_surface(img).convert()
        # Rotate and flip the surface for correct orientation
        img_surface = pygame.transform.rotate(img_surface, -90)
        img_surface = pygame.transform.flip(img_surface, True, False)
        # Scale the surface to fit the camera feed area
        img_surface = pygame.transform.scale(img_surface, (camera_feed_rect.width, camera_feed_rect.height))

        # Instruction text for the user
        instruction = f"Scan {middle_color} middle cubie keeping {top_color} on top."
        instruction_bg_height = 50
        instruction_bg = pygame.Surface((camera_feed_rect.width, instruction_bg_height), pygame.SRCALPHA)
        instruction_bg.fill((128, 128, 128, 128))
        instruction_bg_y = 0
        img_surface.blit(instruction_bg, (0, instruction_bg_y))
        
        # Draw the instruction text on the image surface
        draw_text(surface=img_surface, text=instruction, font_size=40, color=WHITE, y_position=instruction_bg_y + instruction_bg_height//2)

        # If there's an error message
        if error_message:
            error_bg_height = 40
            error_bg = pygame.Surface((camera_feed_rect.width, error_bg_height), pygame.SRCALPHA)
            error_bg.fill((255, 0, 0, 128))
            error_bg_y = camera_feed_rect.height - error_bg_height
            img_surface.blit(error_bg, (0, error_bg_y))
            
            # Draw the error message on the image surface
            draw_text(surface=img_surface, text=error_message, font_size=32, color=WHITE, y_position=error_bg_y + error_bg_height//2)

        # Blit the entire image surface onto the main surface
        surface.blit(img_surface, camera_feed_rect.topleft)
        pygame.display.flip()

        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Check if the detected middle cubie color matches the expected middle color
                    if middle_cubie_color == face_to_color[faces[middle_color]]:
                        return data  # Return the detected colors if correct
                    else:
                        # Set an error message if the middle color is incorrect
                        error_message = f"Error: The middle cubie should be {middle_color}."
                elif event.key == pygame.K_ESCAPE:
                    return None

# Constants for cube dimensions and positions
CUBE_SIZE = 200  # Size of each face of the cube
CUBE_SPACING = 1  # Spacing between the cube faces
CUBE_START_X = (width - 4 * CUBE_SIZE - 3 * CUBE_SPACING) // 2  # Starting X position for drawing the cube
CUBE_START_Y = 100  # Starting Y position for drawing the cube

def draw_cube(surface, scanned_faces):
    """
    Draws the entire Rubik's Cube using the scanned face data.

    Args:
        surface (pygame.Surface): The surface to draw the cube on.
        scanned_faces (list): A list of face data for the Rubik's Cube.
    """
    # Define the positions for each face of the cube
    positions = [
        (CUBE_SIZE + CUBE_SPACING, 0),  # Up face position
        (0, CUBE_SIZE + CUBE_SPACING),  # Left face position
        (CUBE_SIZE + CUBE_SPACING, CUBE_SIZE + CUBE_SPACING),  # Front face position
        (2 * (CUBE_SIZE + CUBE_SPACING), CUBE_SIZE + CUBE_SPACING),  # Right face position
        (3 * (CUBE_SIZE + CUBE_SPACING), CUBE_SIZE + CUBE_SPACING),  # Back face position
        (CUBE_SIZE + CUBE_SPACING, 2 * (CUBE_SIZE + CUBE_SPACING))   # Down face position
    ]
    
    # Define the order to draw the faces
    face_order = [4, 3, 0, 1, 2, 5]  # [Back, Right, Up, Left, Front, Down]
    
    # Arrange the scanned faces according to the defined order
    ordered_faces = [scanned_faces[i] for i in face_order if i < len(scanned_faces)]
    
    # Iterate through the defined face labels and their positions
    for face, pos in zip('U L F R B D'.split(), positions):
        # Check if the current face is valid (exists in CUBIE_IDS)
        if face not in CUBIE_IDS:
            print(f"Warning: Face '{face}' not found in CUBIE_IDS.")  # Warn if face is not recognized
            continue  # Skip to the next face
        
        # Get the corresponding face data from the ordered list, if available
        face_data = ordered_faces.pop(0) if ordered_faces else None
        if face_data is None:
            print(f"Warning: No data for face '{face}'.")  # Warn if no data for the current face
            continue  # Skip to the next face
        
        # Draw the face using the extracted face data
        draw_cube_face(surface, face_data, CUBE_START_X + pos[0], CUBE_START_Y + pos[1], CUBE_SIZE)

        # If there are fixed cubies to highlight, check if the current face contains any
        if fixed_cubie:
            for cubie in fixed_cubie:
                if cubie in CUBIE_IDS[face]:  # Check if the cubie belongs to the current face
                    index = CUBIE_IDS[face].index(cubie)  # Get the index of the cubie
                    cell_x = index % 3  # Calculate the column position (0-2)
                    cell_y = index // 3  # Calculate the row position (0-2)
                    cell_size = CUBE_SIZE // 3

                    # Create a rectangle for highlighting the cubie
                    highlight_rect = pygame.Rect(
                        CUBE_START_X + pos[0] + cell_x * cell_size, CUBE_START_Y + pos[1] + cell_y * cell_size, cell_size, cell_size)

                    # Draw the highlight rectangle around the cubie
                    pygame.draw.rect(surface, droplet_highlight, highlight_rect, 3)
                    # Scale and draw a water droplet image over the highlighted cubie
                    scaled_image = pygame.transform.scale(waterdrop_image, (cell_size, cell_size))
                    surface.blit(scaled_image, highlight_rect.topleft)

def get_clicked_cubie(mouse_pos):  
    """
    Determines which cubie (cell) of the Rubik's Cube was clicked based on the mouse position.

    Args:
        mouse_pos (tuple): A tuple representing the mouse position (x, y).

    Returns:
        list or None: A list of cubie IDs if a valid cubie was clicked, otherwise None.
    """  
    x, y = mouse_pos
    face_size = CUBE_SIZE
    cell_size = face_size // 3

    # Check if the mouse click is outside
    if (x < CUBE_START_X or x > CUBE_START_X + 4 * face_size + 3 * CUBE_SPACING or
        y < CUBE_START_Y or y > CUBE_START_Y + 3 * face_size + 2 * CUBE_SPACING):
        return None

    # Determine which face of the cube was clicked based on the mouse position
    face_x = (x - CUBE_START_X) // (face_size + CUBE_SPACING)  # face column
    face_y = (y - CUBE_START_Y) // (face_size + CUBE_SPACING)  # face row

    # Identify the face label based on the calculated row and column
    if face_y == 0 and face_x == 1:
        face = 'U'
    elif face_y == 1:
        face = 'L F R B'.split()[face_x]
    elif face_y == 2 and face_x == 1:
        face = 'D'
    else:
        return None

    # Calculate local mouse position within the identified face
    local_x = (x - CUBE_START_X) % (face_size + CUBE_SPACING)
    local_y = (y - CUBE_START_Y) % (face_size + CUBE_SPACING)

    # Determine which cubie (cell) was clicked within the face
    cell_x = local_x // cell_size  # Column index of the clicked cubie
    cell_y = local_y // cell_size  # Row index of the clicked cubie

    # Check if the clicked position is within the bounds of the cubie grid
    if cell_x >= 3 or cell_y >= 3:
        return None

    # Calculate the index of the clicked cubie within the face's cubie array
    cubie_index = cell_y * 3 + cell_x  # Convert 2D coordinates to a 1D index
    cubie_id = CUBIE_IDS[face][cubie_index]  # Get the ID of the clicked cubie

    # Check if the cubie has paired cubies
    if cubie_id in CUBIE_PAIRS:
        paired_cubies = CUBIE_PAIRS[cubie_id]  # Get the paired cubies
        if isinstance(paired_cubies, tuple):
            return [cubie_id] + list(paired_cubies)
        else:
            return [cubie_id, paired_cubies]
    return [cubie_id]  # Return the ID of the single clicked cubie if no pairs exist

def m(s):
    """
    Processes and applies a sequence of moves on the Rubik's Cube based on a move string.

    Args:
        s (str): A string containing the sequence of moves to be applied (e.g., "U D F").

    Returns:
        None: Updates global variables and executes the moves on the cube.
    """
    # Replace single quote with "i" to accommodate the move notation
    s = str.replace(s, "'", "i")
    s = str.upper(s)  # Convert the entire string to uppercase to standardize move notation

    # Split the string into individual moves based on spaces
    k = s.split(' ')

    # Update global variables that track the moves and solution length
    global moves_list, solution_length, a
    solution_length += len(k)  # Increase solution length by the number of new moves

    # Loop through each move in the parsed list
    for word in k:
        moves_list.append(word)  # Add the move to the global moves list
        move(word)  # Execute the move

    # Update the current state of the cube after performing the moves
    global scanned_faces
    scanned_faces = get_current_cube_state()  # Capture the current state of the cube

def rotate(axis):
    """
    Rotates the Rubik's Cube around a specified axis (X, Y, or Z).

    Args:
        axis (str): The axis of rotation. Must be one of 'x', 'y', or 'z'.

    Returns:
        None: Rotates the cube's positions and faces accordingly.
    
    Raises:
        Exception: If the axis provided is not valid.
    """
    axis = str.lower(axis)  # Convert the axis to lowercase for standardization
    if axis == 'x':
        # Perform an X-axis rotation by reassigning the values in array 'a'
        temp = a[0]
        a[0] = a[1]  # Rotate the top face positions
        a[1] = a[4]
        a[4] = a[5]
        a[5] = temp
        # Rotate the adjacent faces accordingly
        rotate_face_counterclockwise("L")
        rotate_face_clockwise("R")
    elif axis == 'y':
        # Perform a Y-axis rotation by reassigning the values in array 'a'
        temp = a[1]
        a[1] = a[2]  # Rotate the left and right face positions
        a[2] = a[5]
        a[5] = a[3]
        a[3] = temp
        # Rotate all visible faces accordingly
        rotate_face_clockwise("L")
        rotate_face_clockwise("F")
        rotate_face_clockwise("R")
        rotate_face_clockwise("B")
        rotate_face_clockwise("U")
        rotate_face_counterclockwise("D")
    elif axis == 'z':
        # Perform a Z-axis rotation by reassigning the values in array 'a'
        temp = a[0]
        a[0] = a[3]  # Rotate the front and back face positions
        a[3] = a[4]
        a[4] = a[2]
        a[2] = temp
        # Rotate the faces that correspond to the Z rotation
        rotate_face_clockwise("L")
        rotate_face_clockwise("L")  # Two counterclockwise for L
        rotate_face_clockwise("D")
        rotate_face_clockwise("D")  # Two counterclockwise for D
        rotate_face_clockwise("F")
        rotate_face_counterclockwise("B")
    else:
        # Raise an exception if the axis provided is invalid
        raise Exception("Invalid rotation: " + axis)
    
def move(mv):
    """
    Executes a specific move on the Rubik's Cube based on a move string.

    Args:
        mv (str): The move string to be executed (e.g., "U", "D2", "R").

    Returns:
        None: Applies the move to the cube.
    
    Raises:
        Exception: If the move is invalid.
    """
    mv = str.upper(mv)  # Convert the move string to uppercase for standardization

    # Execute the corresponding rotation based on the move notation
    if mv == "U":
        up_rot()
    elif mv == "U2":
        up_rot(); up_rot()
    elif mv == "UI":
        up_rot(); up_rot(); up_rot()
    elif mv == "D":
        down_rot()
    elif mv == "D2":
        down_rot(); down_rot()
    elif mv == "DI":
        down_rot(); down_rot(); down_rot()
    elif mv == "F":
        front_rot()
    elif mv == "F2":         # Front face 180 degrees
        front_rot(); front_rot()
    elif mv == "FI":         # Front face counterclockwise
        front_rot(); front_rot(); front_rot()
    elif mv == "B":          # Back face clockwise
        back_rot()
    elif mv == "B2":         # Back face 180 degrees
        back_rot(); back_rot()
    elif mv == "BI":         # Back face counterclockwise
        back_rot(); back_rot(); back_rot()
    elif mv == "L":          # Left face clockwise
        left_rot()
    elif mv == "L2":         # Left face 180 degrees
        left_rot(); left_rot()
    elif mv == "LI":         # Left face counterclockwise
        left_rot(); left_rot(); left_rot()
    elif mv == "R":          # Right face clockwise
        right_rot()
    elif mv == "R2":         # Right face 180 degrees
        right_rot(); right_rot()
    elif mv == "RI":         # Right face counterclockwise
        right_rot(); right_rot(); right_rot()
    elif mv == "M":          # Middle slice clockwise
        middle_slice()
    elif mv == "M2":         # Middle slice 180 degrees
        middle_slice(); middle_slice()
    elif mv == "MI":         # Middle slice counterclockwise
        middle_slice(); middle_slice(); middle_slice()
    elif mv == "E":          # Equatorial slice clockwise
        equator_slice()
    elif mv == "E2":         # Equatorial slice 180 degrees
        equator_slice(); equator_slice()
    elif mv == "EI":         # Equatorial slice counterclockwise
        equator_slice(); equator_slice(); equator_slice()
    elif mv == "S":          # Standing slice clockwise
        standing_slice()
    elif mv == "S2":         # Standing slice 180 degrees
        standing_slice(); standing_slice()
    elif mv == "SI":         # Standing slice counterclockwise
        standing_slice(); standing_slice(); standing_slice()
    elif mv == "X":          # Rotate the cube around the x-axis
        rotate('x')
    elif mv == "Y":          # Rotate the cube around the y-axis
        rotate('y')
    elif mv == "Z":          # Rotate the cube around the z-axis
        rotate('z')
    else:
        # Raise an exception if the move is not recognized
        raise Exception("Invalid Move: " + str(mv))

def up_rot():
    """
    Rotates the top layer (U) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the top face.
    """
    temp = a[4][0][0]
    a[4][0][0] = a[4][2][0]
    a[4][2][0] = a[4][2][2]
    a[4][2][2] = a[4][0][2]
    a[4][0][2] = temp

    temp = a[4][0][1]
    a[4][0][1] = a[4][1][0]
    a[4][1][0] = a[4][2][1]
    a[4][2][1] = a[4][1][2]
    a[4][1][2] = temp

    temp = a[0][0][0]
    a[0][0][0] = a[1][0][0]
    a[1][0][0] = a[2][0][0]
    a[2][0][0] = a[3][0][0]
    a[3][0][0] = temp

    temp = a[0][0][1]
    a[0][0][1] = a[1][0][1]
    a[1][0][1] = a[2][0][1]
    a[2][0][1] = a[3][0][1]
    a[3][0][1] = temp

    temp = a[0][0][2]
    a[0][0][2] = a[1][0][2]
    a[1][0][2] = a[2][0][2]
    a[2][0][2] = a[3][0][2]
    a[3][0][2] = temp

def down_rot():
    """
    Rotates the bottom layer (D) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the bottom face.
    """
    temp = a[5][0][0]
    a[5][0][0] = a[5][2][0]
    a[5][2][0] = a[5][2][2]
    a[5][2][2] = a[5][0][2]
    a[5][0][2] = temp

    temp = a[5][0][1]
    a[5][0][1] = a[5][1][0]
    a[5][1][0] = a[5][2][1]
    a[5][2][1] = a[5][1][2]
    a[5][1][2] = temp

    temp = a[0][2][0]
    a[0][2][0] = a[3][2][0]
    a[3][2][0] = a[2][2][0]
    a[2][2][0] = a[1][2][0]
    a[1][2][0] = temp

    temp = a[0][2][1]
    a[0][2][1] = a[3][2][1]
    a[3][2][1] = a[2][2][1]
    a[2][2][1] = a[1][2][1]
    a[1][2][1] = temp

    temp = a[0][2][2]
    a[0][2][2] = a[3][2][2]
    a[3][2][2] = a[2][2][2]
    a[2][2][2] = a[1][2][2]
    a[1][2][2] = temp

def front_rot():
    """
    Rotates the front face (F) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the front face.
    """
    temp = a[0][0][0]
    a[0][0][0] = a[0][2][0]
    a[0][2][0] = a[0][2][2]
    a[0][2][2] = a[0][0][2]
    a[0][0][2] = temp

    temp = a[0][0][1]
    a[0][0][1] = a[0][1][0]
    a[0][1][0] = a[0][2][1]
    a[0][2][1] = a[0][1][2]
    a[0][1][2] = temp

    temp = a[4][2][0]
    a[4][2][0] = a[3][2][2]
    a[3][2][2] = a[5][0][2]
    a[5][0][2] = a[1][0][0]
    a[1][0][0] = temp

    temp = a[4][2][1]
    a[4][2][1] = a[3][1][2]
    a[3][1][2] = a[5][0][1]
    a[5][0][1] = a[1][1][0]
    a[1][1][0] = temp

    temp = a[4][2][2]
    a[4][2][2] = a[3][0][2]
    a[3][0][2] = a[5][0][0]
    a[5][0][0] = a[1][2][0]
    a[1][2][0] = temp

def back_rot():
    """
    Rotates the back face (B) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the back face.
    """
    temp = a[2][0][0]
    a[2][0][0] = a[2][2][0]
    a[2][2][0] = a[2][2][2]
    a[2][2][2] = a[2][0][2]
    a[2][0][2] = temp

    temp = a[2][0][1]
    a[2][0][1] = a[2][1][0]
    a[2][1][0] = a[2][2][1]
    a[2][2][1] = a[2][1][2]
    a[2][1][2] = temp
    temp = a[4][0][2]
    a[4][0][2] = a[1][2][2]
    a[1][2][2] = a[5][2][0]
    a[5][2][0] = a[3][0][0]
    a[3][0][0] = temp

    temp = a[4][0][1]
    a[4][0][1] = a[1][1][2]
    a[1][1][2] = a[5][2][1]
    a[5][2][1] = a[3][1][0]
    a[3][1][0] = temp

    temp = a[4][0][0]
    a[4][0][0] = a[1][0][2]
    a[1][0][2] = a[5][2][2]
    a[5][2][2] = a[3][2][0]
    a[3][2][0] = temp

def left_rot():
    """
    Rotates the left face (L) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the left face.
    """
    temp = a[3][0][0]
    a[3][0][0] = a[3][2][0]
    a[3][2][0] = a[3][2][2]
    a[3][2][2] = a[3][0][2]
    a[3][0][2] = temp

    temp = a[3][0][1]
    a[3][0][1] = a[3][1][0]
    a[3][1][0] = a[3][2][1]
    a[3][2][1] = a[3][1][2]
    a[3][1][2] = temp
    temp = a[0][0][0]
    a[0][0][0] = a[4][0][0]
    a[4][0][0] = a[2][2][2]
    a[2][2][2] = a[5][0][0]
    a[5][0][0] = temp

    temp = a[0][1][0]
    a[0][1][0] = a[4][1][0]
    a[4][1][0] = a[2][1][2]
    a[2][1][2] = a[5][1][0]
    a[5][1][0] = temp

    temp = a[0][2][0]
    a[0][2][0] = a[4][2][0]
    a[4][2][0] = a[2][0][2]
    a[2][0][2] = a[5][2][0]
    a[5][2][0] = temp

def right_rot():
    """
    Rotates the right face (R) of the Rubik's Cube clockwise.
    It rotates the four corner pieces and the four edge pieces of the right face.
    """
    temp = a[1][0][0]
    a[1][0][0] = a[1][2][0]
    a[1][2][0] = a[1][2][2]
    a[1][2][2] = a[1][0][2]
    a[1][0][2] = temp

    temp = a[1][0][1]
    a[1][0][1] = a[1][1][0]
    a[1][1][0] = a[1][2][1]
    a[1][2][1] = a[1][1][2]
    a[1][1][2] = temp
    temp = a[0][2][2]
    a[0][2][2] = a[5][2][2]
    a[5][2][2] = a[2][0][0]
    a[2][0][0] = a[4][2][2]
    a[4][2][2] = temp

    temp = a[0][1][2]
    a[0][1][2] = a[5][1][2]
    a[5][1][2] = a[2][1][0]
    a[2][1][0] = a[4][1][2]
    a[4][1][2] = temp

    temp = a[0][0][2]
    a[0][0][2] = a[5][0][2]
    a[5][0][2] = a[2][2][0]
    a[2][2][0] = a[4][0][2]
    a[4][0][2] = temp

def middle_slice():
    """
    Performs a middle slice rotation (M) on the Rubik's Cube.
    This rotates the middle layer of the cube, affecting both the edge and corner pieces.
    """
    temp = a[0][0][1]
    a[0][0][1] = a[4][0][1]
    a[4][0][1] = a[2][2][1]
    a[2][2][1] = a[5][0][1]
    a[5][0][1] = temp

    temp = a[0][1][1]
    a[0][1][1] = a[4][1][1]
    a[4][1][1] = a[2][1][1]
    a[2][1][1] = a[5][1][1]
    a[5][1][1] = temp

    temp = a[0][2][1]
    a[0][2][1] = a[4][2][1]
    a[4][2][1] = a[2][0][1]
    a[2][0][1] = a[5][2][1]
    a[5][2][1] = temp

def equator_slice():
    """
    Performs an equator slice rotation (E) on the Rubik's Cube.
    This rotates the middle layer of the cube horizontally, affecting the edge pieces on the top, bottom, front, and back faces.
    """
    temp = a[0][1][0]
    a[0][1][0] = a[3][1][0]
    a[3][1][0] = a[2][1][0]
    a[2][1][0] = a[1][1][0]
    a[1][1][0] = temp

    temp = a[0][1][1]
    a[0][1][1] = a[3][1][1]
    a[3][1][1] = a[2][1][1]
    a[2][1][1] = a[1][1][1]
    a[1][1][1] = temp

    temp = a[0][1][2]
    a[0][1][2] = a[3][1][2]
    a[3][1][2] = a[2][1][2]
    a[2][1][2] = a[1][1][2]
    a[1][1][2] = temp

def standing_slice():
    """
    Performs a standing slice rotation (S) on the Rubik's Cube.
    This affects the middle layer between the left, right, and back faces, rotating the middle slice of the cube.
    """
    temp = a[4][1][0]
    a[4][1][0] = a[3][2][1]
    a[3][2][1] = a[5][1][2]
    a[5][1][2] = a[1][0][1]
    a[1][0][1] = temp

    temp = a[4][1][1]
    a[4][1][1] = a[3][1][1]
    a[3][1][1] = a[5][1][1]
    a[5][1][1] = a[1][1][1]
    a[1][1][1] = temp

    temp = a[4][1][2]
    a[4][1][2] = a[3][0][1]
    a[3][0][1] = a[5][1][0]
    a[5][1][0] = a[1][2][1]
    a[1][2][1] = temp

def rotate_face_counterclockwise(face):
    """
    Rotates a specified face of the Rubik's Cube counterclockwise (90 degrees).
    This is achieved by performing three clockwise rotations on the face.
    
    Parameters:
    face (str): The identifier of the face to rotate ('U', 'D', 'F', 'B', 'L', 'R').
    """
    rotate_face_clockwise(face)
    rotate_face_clockwise(face)
    rotate_face_clockwise(face)

def rotate_face_clockwise(face):
    """
    Rotates a specified face of the Rubik's Cube clockwise (90 degrees).
    This function rotates the cubies on the specified face and its adjacent pieces accordingly.
    
    Parameters:
    face (str): The identifier of the face to rotate ('U', 'D', 'F', 'B', 'L', 'R').
    
    Raises:
    Exception: If an invalid face identifier is provided.
    """
    f_id = -1
    face = str.lower(face)
    if face == "u":
        f_id = 0
    elif face == "f":
        f_id = 1
    elif face == "r":
        f_id = 2
    elif face == "l":
        f_id = 3
    elif face == "d":
        f_id = 4
    elif face == "b":
        f_id = 5
    else:
        raise Exception("Invalid face: " + face)
    temp = a[f_id][0][0]
    a[f_id][0][0] = a[f_id][2][0]
    a[f_id][2][0] = a[f_id][2][2]
    a[f_id][2][2] = a[f_id][0][2]
    a[f_id][0][2] = temp
    temp = a[f_id][0][1]
    a[f_id][0][1] = a[f_id][1][0]
    a[f_id][1][0] = a[f_id][2][1]
    a[f_id][2][1] = a[f_id][1][2]
    a[f_id][1][2] = temp

def get_restricted_faces(fixed_cubie):
    """
    Determines which faces of the Rubik's Cube are restricted by the position of a fixed cubie.
    This function checks the positions of the fixed cubie and adds the affected faces to the restricted set.
    
    Parameters:
    fixed_cubie (list): A list of cubie identifiers that are fixed in position.

    Returns:
    set: A set of restricted face identifiers ('U', 'D', 'F', 'B', 'L', 'R').
    """
    # Initialize an empty set to hold restricted face identifiers
    restricted_faces = set()
    
    # Iterate over each cubie in the provided fixed_cubie list
    for cubie in fixed_cubie:
        # Check if the cubie belongs to the upper face
        if cubie in CUBIE_IDS['U']:
            restricted_faces.add('U')  # Add 'U' to the restricted faces set

        if cubie in CUBIE_IDS['D']:
            restricted_faces.add('D')

        if cubie in CUBIE_IDS['F']:
            restricted_faces.add('F')

        if cubie in CUBIE_IDS['B']:
            restricted_faces.add('B')

        if cubie in CUBIE_IDS['L']:
            restricted_faces.add('L')

        if cubie in CUBIE_IDS['R']:
            restricted_faces.add('R')

    # Return the set of restricted faces
    return restricted_faces

def is_move_allowed(move, restricted_faces):
    """
    Checks if a given move is allowed based on the restricted faces from a fixed cubie.
    The move is allowed only if the face of the move is not restricted.
    
    Parameters:
    move (str): A string representing the move (e.g., 'U', 'R', 'F').
    restricted_faces (set): A set of face identifiers that are restricted by the fixed cubie.
    
    Returns:
    bool: True if the move is allowed, False otherwise.
    """
    # Extract the face identifier from the move
    face = move[0]
    
    # Check if the face is not in the set of restricted faces
    return face not in restricted_faces

def get_current_cube_state():
    """
    Retrieves the current state of the Rubik's Cube.
    This function returns a 6x3x3 matrix representing the colors of each cubie on the cube's faces.
    
    Returns:
    list: A list of 6 lists, each containing a 3x3 grid of cubie colors for each face.
    """
    global a
    
    # Construct the current cube state as a list of lists, where each sub-list
    return [
        [a[i][j][k] for j in range(3) for k in range(3)]  # Flatten each 3x3 face into a single list
        for i in range(6)  # Iterate over all 6 faces of the cube
    ]

def get_kociemba_string(scanned_faces):
    """
    Converts a given set of scanned faces to a Kociemba string.
    The Kociemba string is a compact representation of the cube state, used in the Kociemba algorithm for solving the Rubik's Cube.
    
    Parameters:
    scanned_faces (dict): A dictionary mapping face identifiers ('U', 'R', 'F', 'D', 'L', 'B') to 3x3 matrices of colors.
    
    Returns:
    str: A Kociemba string representing the state of the cube.
    """
    kociemba_string = ''  # Initialize an empty string to hold the Kociemba representation
    face_order = 'URFDLB'  # Define the order in which to read the faces
    face_index = {'U': 4, 'R': 1, 'F': 0, 'D': 5, 'L': 3, 'B': 2}  # Mapping of face identifiers to their indices in scanned_faces

    # Iterate through the defined order of faces
    for face in face_order:
        # Get the colors of the current face using the face_index mapping
        face_colors = scanned_faces[face_index[face]]
        
        # Append each color of the current face to the Kociemba string
        for color in face_colors:
            kociemba_string += color
            
    return kociemba_string  # Return the constructed Kociemba string

def get_affected_faces(move):
    """
    Returns a set of affected faces based on the given move.
    
    Args:
        move (str): The move to evaluate. Can be a single letter (e.g., 'U') or a modifier (e.g., 'U2', 'Ui').
        
    Returns:
        set: A set of faces affected by the move (e.g., 'U', 'D', 'L', 'R').
    """
    affected = set()  # Initialize an empty set to hold affected faces

    # Check if the move is a basic face rotation, inverse or double turns
    if move[0] in ['U', 'D', 'F', 'B', 'L', 'R', 'UI', 'DI', 'FI', 'BI', 'LI', 'RI', 'U2', 'D2', 'F2', 'B2', 'L2', 'R2']:
        affected.add(move[0])  # Add the face being rotated to the affected set
    # Handle the middle layer move (M), which affects U, D, and the faces in between
    elif move[0] == 'M':
        affected.update(['U', 'D', 'F', 'B', 'UI', 'DI', 'FI', 'BI', 'U2', 'D2', 'F2', 'B2'])
    # Handle the equatorial layer move (E), which affects F, R, B, L
    elif move[0] == 'E':
        affected.update(['F', 'R', 'B', 'L', 'FI', 'RI', 'BI', 'LI', 'F2', 'R2', 'B2', 'L2'])
    # Handle the standing layer move (S), which affects U, D, L, R
    elif move[0] == 'S':
        affected.update(['U', 'D', 'L', 'R', 'UI', 'DI', 'LI', 'RI', 'U2', 'D2', 'L2', 'R2'])

    return affected  # Return the set of affected faces

def get_equivalent_move(move, fixed_faces):
    """
    Returns a list of equivalent moves for a given move, considering fixed faces.

    Args:
        move (str): The move to evaluate (e.g., 'U', 'D', 'F', etc.).
        fixed_faces (set): A set of faces that are fixed in place (e.g., {'U', 'F'}).

    Returns:
        list: A list of equivalent moves that would yield the same result (e.g., ['U', 'D']).
    """
    # Dictionary mapping moves to their equivalents, including inverse relationships
    equivalents = {
        'U': ['D', 'E'],
        'D': ['U', 'Ei'],
        'F': ['B', 'Si'],
        'B': ['F', 'S'],
        'L': ['R', 'Mi'],
        'R': ['L', 'M'],
        'Ui': ['Di', 'Ei'],
        'Di': ['Ui', 'E'],
        'Fi': ['Bi', 'S'],
        'Bi': ['Fi', 'Si'],
        'Li': ['Ri', 'M'],
        'Ri': ['Li', 'Mi'],
        'U2': ['D2', 'E2'],
        'D2': ['U2', 'E2'],
        'F2': ['B2', 'S2'],
        'B2': ['F2', 'S2'],
        'L2': ['R2', 'M2'],
        'R2': ['L2', 'M2']
    }

    # Check if the move corresponds to a fixed face
    if move[0] in fixed_faces:
        # If it does, return the list of equivalent moves from the dictionary
        return equivalents.get(move, [move])  # If the move is not in the dictionary, return the original move as a single-element list
    return [move]

def update_reference_frame(reference_frame, move):
    """
    Updates the reference frame of the cube after a move is performed.

    Args:
        reference_frame (dict): A dictionary representing the current reference frame of the cube.
        move (str): The move to apply (e.g., 'U', 'M', 'S').

    Returns:
        dict: The updated reference frame after applying the move.
    """
    # Dictionary mapping moves to their corresponding rotation transformations
    rotations = {
        'E': lambda rf: {
            'U': rf['U'], 'D': rf['D'],
            'F': rf['L'], 'B': rf['R'],
            'L': rf['B'], 'R': rf['F']
        },
        'Ei': lambda rf: {
            'U': rf['U'], 'D': rf['D'],
            'F': rf['R'], 'B': rf['L'],
            'L': rf['F'], 'R': rf['B']
        },
        'E2': lambda rf: {
            'U': rf['U'], 'D': rf['D'],
            'F': rf['B'], 'B': rf['F'],
            'L': rf['R'], 'R': rf['L']
        },
        'M': lambda rf: {
            'U': rf['B'], 'D': rf['F'],
            'F': rf['U'], 'B': rf['D'],
            'L': rf['L'], 'R': rf['R']
        },
        'Mi': lambda rf: {
            'U': rf['F'], 'D': rf['B'],
            'F': rf['D'], 'B': rf['U'],
            'L': rf['L'], 'R': rf['R']
        },
        'M2': lambda rf: {
            'U': rf['D'], 'D': rf['U'],
            'F': rf['B'], 'B': rf['F'],
            'L': rf['L'], 'R': rf['R']
        },
        'S': lambda rf: {
            'U': rf['L'], 'D': rf['R'],
            'F': rf['F'], 'B': rf['B'],
            'L': rf['D'], 'R': rf['U']
        },
        'Si': lambda rf: {
            'U': rf['R'], 'D': rf['L'],
            'F': rf['F'], 'B': rf['B'],
            'L': rf['U'], 'R': rf['D']
        },
        'S2': lambda rf: {
            'U': rf['D'], 'D': rf['U'],
            'F': rf['F'], 'B': rf['B'],
            'L': rf['R'], 'R': rf['L']
        }
    }
    # Check if the move exists in the rotations dictionary
    if move in rotations:
        # Apply the corresponding transformation to the reference frame
        return rotations[move](reference_frame)
    
    # If the move is not recognized, return the original reference frame unchanged
    return reference_frame

def adjust_move_for_reference_frame(move, reference_frame):
    """
    Adjusts a move according to the current reference frame of the cube.

    Args:
        move (str): The move to adjust (e.g., 'U', 'D2').
        reference_frame (dict): A dictionary representing the current reference frame of the cube.

    Returns:
        str: The adjusted move based on the reference frame (e.g., 'F', 'B2').
    """
    # Extract the face from the move
    face = move[0]
    
    # Determine if the move has 'i', '2')
    modifier = move[1:] if len(move) > 1 else ''
    
    # Find the adjusted face based on the reference frame
    adjusted_face = next(key for key, value in reference_frame.items() if value == face)
    
    # Return the adjusted move, combining the adjusted face with its modifier
    return adjusted_face + modifier

def is_cube_solved(current_state):
    """
    Checks if the Rubik's Cube is in a solved state.

    Args:
        current_state (list): The current state of the cube as a list of lists, where each list represents a face.

    Returns:
        bool: True if the cube is solved, False otherwise.
    """
    # Define the solved state of the Rubik's Cube
    solved_state = [
        ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'],  #(Green)
        ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],  #(Red)
        ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],  #(Blue)
        ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],  #(Orange)
        ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'],  #(White)
        ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']   #(Yellow)
    ]
    
    # Flatten the current state of the cube into a single list
    flat_current_state = [color for face in current_state for color in face]
    
    # Flatten the solved state of the cube into a single list
    flat_solved_state = [color for face in solved_state for color in face]
    
    # Compare the flattened current state with the flattened solved state
    return flat_current_state == flat_solved_state

def solve_cube(scanned_faces, fixed_cubie):
    """
    Solves the Rubik's Cube based on the scanned faces and fixed cubie positions.

    Args:
        scanned_faces (dict): A dictionary representing the cube's faces and their current colors.
        fixed_cubie (list): A list of cubies that should remain fixed during the solution.

    Returns:
        list: A list of moves that solve the cube, or None if the cube is already solved or cannot be solved.
    """
    if is_cube_solved(scanned_faces):
        show_popup_message(screen, "Cube already solved.")
        return None
    
    # Convert the scanned faces into a Kociemba string representation
    cube_string = get_kociemba_string(scanned_faces)
    try:
        kociemba_solution = kociemba.solve(cube_string)
        print("Kociemba solution:", kociemba_solution)
        # Convert the Kociemba solution into a list of moves
        original_moves = [move if len(move) == 1 else move[0] + ('i' if "'" in move else '2') for move in kociemba_solution.split()]
        # Get the restricted faces based on fixed cubies
        fixed_faces = get_restricted_faces(fixed_cubie)
        # Initialize a list to hold modified moves
        modified_moves = []
        # Initialize the reference frame to the standard face positions
        reference_frame = {face: face for face in 'UDFBLR'}
        # Process the original moves to adapt them to the current reference frame
        while original_moves:
            move = original_moves.pop(0)
            # Adjust the move for the current reference frame
            adjusted_move = adjust_move_for_reference_frame(move, reference_frame)
            if adjusted_move[0] in fixed_faces:
                equivalent_moves = get_equivalent_move(adjusted_move, fixed_faces)
                # Add the equivalent moves to the modified moves list
                for eq_move in equivalent_moves:
                    modified_moves.append(eq_move)
                    # Update the reference frame based on the equivalent move
                    reference_frame = update_reference_frame(reference_frame, eq_move)
            else:
                # If not affecting fixed faces, just add the adjusted move
                modified_moves.append(adjusted_move)
                # Update the reference frame for the adjusted move
                reference_frame = update_reference_frame(reference_frame, adjusted_move)
        print("Final Solution:")
        print(' '.join(modified_moves))
        return modified_moves
    except Exception as e:
        show_popup_message(screen, "Rubik's cube scanned incorrectly. Please scan again.")
        return None

# Define constants to represent different states or screens in the application
MAIN_MENU = 0
Instructions = 1
Move_Guide = 2
PLAY_GAME = 3
About_Algorithm = 4
CAMERA_VIEW = 5

# Initialize the current state to the main menu
current_state = MAIN_MENU

def main_menu():
    """
    Handles the main menu of the application where the user can navigate to different sections 
    (Instructions, Move Guide, About Algorithm) or start the game. 

    This function includes logic for handling user input, button clicks, and rendering 
    the main menu interface with animations.
    """
    global current_state, rotation_angle_x, rotation_angle_y
    current_state = MAIN_MENU
    rotation_angle_x = math.pi / 6
    rotation_angle_y = math.pi / 4
    running = True
    clock = pygame.time.Clock()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if current_state == MAIN_MENU:
                        for i, button in enumerate(buttons):
                            if button.is_clicked(event.pos):
                                if i == 0: 
                                    current_state = Instructions
                                elif i == 1: 
                                    current_state = Move_Guide
                                elif i == 2: 
                                    current_state = About_Algorithm
                                elif i == 3: running = False
                        if start_game_button.is_clicked(event.pos):
                            game_loop()
                            current_state = MAIN_MENU
                    else:
                        if back_button.is_clicked(event.pos):
                            current_state = MAIN_MENU

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_background(screen)

        title_font = pygame.font.Font(font_path, 72)
        title_shadow = title_font.render("Rubik's Cube Adventure", True, BLACK)
        title = title_font.render("Rubik's Cube Adventure", True, PINK)
        shadow_rect = title.get_rect(center=(width//2 + 3, 103))
        title_rect = title.get_rect(center=(width//2, 100))
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title, title_rect)

        if current_state == MAIN_MENU:
            cube_size = min(width, height) // 4
            cube_animation(screen, cube_size, rotation_angle_x, rotation_angle_y)
            rotation_angle_y += 0.02
            for button in buttons:
                button.draw(screen, mouse_pos)
            start_game_button.draw(screen, mouse_pos)
        else:
            back_button.draw(screen, mouse_pos)
            content_width = width * 3 // 4
            content_height = height * 2 // 3
            content_rect = pygame.Rect((width - content_width) // 2,
                                       (height - content_height) // 2, 
                                       content_width, content_height)
            if current_state == Instructions:
                draw_text_in_rect(screen, formatted_instructions, 40, WHITE, content_rect)
            elif current_state == Move_Guide:
                draw_move_guide(screen, content_rect)
            elif current_state == About_Algorithm:
                draw_text_in_rect(screen, About_Algorithm_text, 40, WHITE, content_rect)
        pygame.display.flip()
        clock.tick(60)

def game_loop():
    """
    The main game loop that handles the scanning of the cube, solving the puzzle, 
    and controlling the user interface during the gameplay. The loop manages 
    interactions with the camera, cube scanning, move execution, and the control 
    buttons for pausing, resuming, and navigating moves.

    Includes logic for managing the game state, showing the cube on screen, 
    and handling cube-solving animations.
    """
    global fixed_cubie, scanned_faces, a, camera
    clock = pygame.time.Clock()
    scanning_complete = False
    scanned_faces = []
    show_water_drop_prompt = False
    fixed_cubie = []
    is_solving = False
    is_paused = False
    current_move_index = 0
    moves_to_execute = []
    move_delay = 1500
    last_move_time = 0
    show_control_buttons = False
    solution_text = ""
    is_selecting_cubie = False
    is_scanning = False
    camera = cv2.VideoCapture(0)
    solve_cube_button = Button(start_x_camera_buttons + button_width + button_spacing, button_y, button_width, button_height, "SOLVE CUBE", GREEN)
    scan_cube_button = Button(start_x_camera_buttons, button_y, button_width, button_height, "SCAN CUBE", YELLOW)
    waterdrop_button = Button(start_x_camera_buttons + 2 * (button_width + button_spacing), button_y, button_width, button_height, "WATER DROP", BLUE, image=waterdrop_image)
    pause_button, resume_button, next_move_button = create_control_buttons()
    speed_adjuster = Slider(waterdrop_button.rect.x + 500, (height) // 4, height=500, min_value=500, max_value=3000, initial_value=1500)

    running = True
    while running:
        screen.fill((255, 255, 255))
        draw_background(screen)

        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if show_control_buttons:
                    if pause_button.is_clicked(mouse_pos) and is_solving:
                        is_paused = True
                    elif resume_button.is_clicked(mouse_pos) and is_solving:
                        is_paused = False
                        last_move_time = current_time
                    elif next_move_button.is_clicked(mouse_pos) and is_solving and is_paused:
                        if current_move_index < len(moves_to_execute):
                            m(moves_to_execute[current_move_index])  # Execute the next move
                            current_move_index += 1  # Move to the next index
                            scanned_faces = get_current_cube_state()  # Update the scanned faces
                    elif speed_adjuster.is_clicked(mouse_pos):
                        speed_adjuster.is_dragging = True
                else:  # If control buttons are not visible
                    if solve_cube_button.is_clicked(mouse_pos):
                        if scanning_complete:
                            moves_to_execute = solve_cube(scanned_faces, fixed_cubie)
                            if moves_to_execute:
                                is_solving = True
                                is_paused = False
                                current_move_index = 0
                                last_move_time = current_time 
                                show_control_buttons = True
                                show_water_drop_prompt = False
                                is_selecting_cubie = False
                                solution_text = ' '.join(moves_to_execute)
                    elif scan_cube_button.is_clicked(mouse_pos):
                        is_scanning = True  # Start scanning process
                        scanning_complete = False
                        scanned_faces = []  # Reset scanned faces
                        fixed_cubie = [] 
                        show_water_drop_prompt = False  # Hide water drop prompt
                        is_selecting_cubie = False 
                        solution_text = ""  # Reset solution text

                        # Start new scan
                        new_faces = scan_cube(screen)
                        if new_faces:
                            scanned_faces = new_faces
                            scanning_complete = True
                            for i, face in enumerate(scanned_faces):  # Update 'a' with scanned faces
                                for j in range(3):
                                    for k in range(3):
                                        a[i][j][k] = face[j*3 + k]
                        is_scanning = False

                    elif waterdrop_button.is_clicked(mouse_pos):
                        if not scanning_complete: 
                            show_popup_message(screen, "Please scan the cube first.")
                        else:
                            show_water_drop_prompt = True
                            is_selecting_cubie = True
                    elif is_selecting_cubie:
                        clicked_cubies = get_clicked_cubie(mouse_pos)
                        if clicked_cubies:
                            fixed_cubie = clicked_cubies
            
            elif event.type == pygame.MOUSEBUTTONUP:
                speed_adjuster.is_dragging = False
            elif event.type == pygame.MOUSEMOTION and speed_adjuster.is_dragging:
                speed_adjuster.update(event.pos)
                move_delay = speed_adjuster.value

        # Always show camera feed at the start and during scanning
        if not scanning_complete or is_scanning:
            pygame.draw.rect(screen, droplet_highlight, (camera_x, camera_y, camera_width, camera_height), camera_border)
            if camera and camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_surface = pygame.surfarray.make_surface(frame).convert()
                    frame_surface = pygame.transform.rotate(frame_surface, -90)
                    frame_surface = pygame.transform.flip(frame_surface, True, False)
                    frame_surface = pygame.transform.scale(frame_surface, (camera_feed_rect.width, camera_feed_rect.height))
                    screen.blit(frame_surface, camera_feed_rect)

        # Draw cube if scanning is complete
        if scanning_complete and not is_scanning:
            draw_cube(screen, scanned_faces)

        mouse_pos = pygame.mouse.get_pos()
        if not show_control_buttons:
            waterdrop_button.draw(screen, mouse_pos)
            solve_cube_button.draw(screen, mouse_pos)
            scan_cube_button.draw(screen, mouse_pos)
        else:
            pause_button.draw(screen, mouse_pos)
            resume_button.draw(screen, mouse_pos)
            next_move_button.draw(screen, mouse_pos)
            if current_move_index < len(moves_to_execute):  # If there are moves to execute
                current_move = moves_to_execute[current_move_index]  # Get current move
                move_text = f"Current Move: {current_move} ({current_move_index + 1}/{len(moves_to_execute)})"
                draw_text(screen, move_text, 30, BLACK, pause_button.rect.top - 30)
                speed_adjuster.draw(screen)

        if solution_text:
            solution_rect = pygame.Rect(0, 30, screen.get_width() - 40, 200)
            solution_rect.centerx = screen.get_width() // 2
            draw_wrapped_text(screen, f"Final Solution: {solution_text}", 40, WHITE, solution_rect)

        if show_water_drop_prompt and is_selecting_cubie and not is_scanning:
            draw_text(screen, "Click on a cubie to fix its position.", 30, droplet_highlight, camera_y + camera_height + 60)

        # Handle solving completion
        if is_solving and not is_paused and moves_to_execute:
            if current_move_index < len(moves_to_execute) and current_time - last_move_time >= move_delay:
                m(moves_to_execute[current_move_index])  # Execute the next move
                current_move_index += 1  # Increment the move index
                last_move_time = current_time  # Update last move time
                scanned_faces = get_current_cube_state()  # Update scanned faces
            elif current_move_index >= len(moves_to_execute):  # If all moves have been executed
                is_solving = False  # Reset solving state
                show_control_buttons = False  # Hide control buttons
                popup_button_width = 200
                play_again_button = Button((width - 2 * popup_button_width - 20) // 2, height // 2 + 50, popup_button_width, button_height, "PLAY AGAIN", GREEN)
                exit_button = Button((width + 20) // 2, height // 2 + 50, popup_button_width, button_height, "EXIT", RED)
                result = show_popup_message(screen, "Cube Solved!", buttons=[play_again_button, exit_button], is_congratulations=True)
                if result == "PLAY AGAIN":
                    if camera and camera.isOpened():
                        camera.release()
                    return True
                elif result == "EXIT" or result == "quit":
                    if camera and camera.isOpened():
                        camera.release()
                    pygame.quit()
                    sys.exit()
                running = False

        pygame.display.flip()
        clock.tick(30)

    if camera and camera.isOpened():
        camera.release()
    return False

def main():
    pygame.init()
    if camera_permissions():
        main_menu()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()