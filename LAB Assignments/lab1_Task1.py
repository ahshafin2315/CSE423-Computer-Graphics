import numpy as np
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
W_Width, W_Height = 700, 700

# Rain parameters
drop_ends = None
drop_lengths = None
rain_speed = 0.3
rain_slant = 90
rad = math.radians(rain_slant)
m = math.tan(rad)
m_inv = 1/m

# Day/Night Transition
day_color =  np.array([0.95, 0.95, 0.95])  # (Daytime)
night_color =  1.0 - day_color  # (Nighttime)
current_color = np.copy(day_color)
line_color = 1.0 - current_color
transition_speed = 0.005
is_night = False
is_transitioning = False

def update_slope():
    global m, m_inv
    rad = math.radians(rain_slant)
    m = math.tan(rad) if rain_slant != 90 else float('inf')
    m_inv = 1 / m if rain_slant != 90 else 0

def draw_points(x, y, size=1):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def draw_line(x1, y1, x2, y2, size=1):
    glLineWidth(size)
    glBegin(GL_LINES)
    glVertex2f(x1,y1) #start
    glVertex2f(x2,y2) #end
    glEnd()

def draw_triangle(x1, y1, x2, y2, x3, y3, size=1):
    glLineWidth(size)
    glBegin(GL_TRIANGLES)
    # anti-clockwise
    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(x1,y1) #p1
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(x2,y2) #p2
    glColor3f(0.0, 0.0, 1.0)
    glVertex2f(x3,y3) #p3
    glEnd()

def draw_house():
    global line_color
    
    glColor3f(*line_color)

    # Walls outline
    wall_blp = np.array([-150, -140])
    wall_tlp = np.array([-150, 60])
    wall_brp = np.array([150, -140])
    wall_trp = np.array([150, 60])
    draw_line(*wall_blp, *wall_tlp, size=4) # left
    draw_line(*wall_brp, *wall_trp, size=4) # right
    draw_line(*wall_tlp, *wall_trp, size=4) # top
    draw_line(*wall_blp, *wall_brp, size=4) # bottom

    # Roof outline
    roof_tp =  np.array([0, 160])
    roof_blp = np.array([-180, 60])
    roof_brp = np.array([180, 60])
    draw_line(*roof_blp, *roof_tp, size=4)   # Roof outline (left)
    draw_line(*roof_tp, *roof_brp, size=4)   # Roof outline (right)
    draw_line(*roof_blp, *roof_brp, size=4)  # Roof outline (bottom)

    # Door outline
    door_blp = np.array([-100, -140])
    door_tlp = np.array([-100, -20])
    door_brp = np.array([-20, -140])
    door_trp = np.array([-20, -20])
    draw_line(*door_blp, *door_tlp, size=4) # left
    draw_line(*door_brp, *door_trp, size=4) # right
    draw_line(*door_tlp, *door_trp, size=4) # top
    draw_line(*door_blp, *door_brp, size=4) # bottom

    # Door knob
    draw_points(-40, -80, size=6)
    
    # Window outer box
    window_blp = np.array([50, -20])
    window_tlp = np.array([50, 20])
    window_brp = np.array([90, -20])
    window_trp = np.array([90, 20])
    draw_line(*window_blp, *window_tlp, size=4) # left
    draw_line(*window_brp, *window_trp, size=4) # right
    draw_line(*window_tlp, *window_trp, size=4) # top
    draw_line(*window_blp, *window_brp, size=4) # bottom

    # Window grid
    grid_n = (window_tlp+window_trp)//2
    grid_s = (window_blp+window_brp)//2
    grid_w = (window_blp+window_tlp)//2
    grid_e = (window_brp+window_trp)//2
    draw_line(*grid_n, *grid_s, size=4)   # Vertical divider
    draw_line(*grid_w, *grid_e, size=4)   # Horizontal divider


# Rain drops initialization
def initialize_rain():
    global drop_ends, rain_drop_end, drop_lengths, W_Width, W_Height
    x_start = -W_Width // 2
    x_end = W_Width // 2
    y_start = 0
    y_end = W_Height // 2
    spacing = 10

    drop_ends = []
    drop_lengths = []
    d = 3
    diff = y_end // d
    y_ranges = [(y_start, diff - 10), (diff, 2 * diff - 10), (2 * diff, y_end)]
    for x in range(x_start, x_end + 1, spacing):
        for y in range(d):
            endp = [x, np.random.randint(*y_ranges[y])]
            drop_ends.append(endp)
            len = np.random.randint(5, diff - 15)
            drop_lengths.append(len)

    drop_ends = np.array(drop_ends, dtype=np.float64)
    drop_lengths = np.array(drop_lengths, dtype=np.float64)

# Function to draw rain
def draw_rain():
    global drop_ends, m_inv, drop_lengths, line_color
    glColor3f(*line_color)
    glBegin(GL_LINES)
    for i in range(len(drop_ends)):
        endP = drop_ends[i]
        newX = (endP[1]+drop_lengths[i]-endP[1])*m_inv + endP[0]
        glVertex2f(endP[0] , endP[1])
        glVertex2f(newX , endP[1]+drop_lengths[i])
    glEnd()

# Update rain positions
def animate_rain():
    global drop_ends, m_inv, rain_slant, rain_speed, W_Height, W_Width
    cut_height = 90
    drop_ends[:, 1] -= rain_speed
    drop_ends[:, 0] -= m_inv if rain_slant != 90 else 0
    drop_ends[drop_ends[:, 1] <= cut_height, 1] = W_Height // 2

    out_of_leftBound = drop_ends[:, 0] < -W_Width // 2
    drop_ends[out_of_leftBound, 0] = W_Width // 2

    out_of_rightBound = drop_ends[:, 0] > W_Width // 2
    drop_ends[out_of_rightBound, 0] = -W_Width // 2


# Animate day/night transition
def animate_day_night():
    global current_color, line_color, is_night, is_transitioning

    if not is_transitioning:
        return
    
    if is_night:
        current_color = current_color - transition_speed
    else:
        current_color = current_color + transition_speed
    line_color = 1.0 - current_color

    # Check if transition is complete
    if current_color[0] <= night_color[0] or current_color[0] >= day_color[0]:
        is_transitioning = False

# Key input listener for toggling day/night
def keyboardListener(key, x, y):
    global is_night, is_transitioning

    if key == b'n':  # Press 'n' to toggle night/day
        is_night = not is_night
        is_transitioning = True
        print("Night/Day Toggled!")
    
def specialKeyListener(key, x, y):
    global rain_slant

    if key == GLUT_KEY_LEFT:  # Left arrow key to bend rain left
        if rain_slant > 45:
            rain_slant -= 1
            update_slope()
            print("Rain bending left")
        else:
            print("Left limit reached")
    elif key == GLUT_KEY_RIGHT:  # Right arrow key to bend rain right
        if rain_slant < 135:
            rain_slant += 1
            update_slope()
            print("Rain bending right")
        else:
            print("Right limit reached")


# Display function
def display():
    global current_color

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(*current_color, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,200,	0,0,0,	0,1,0)

    # Draw the house and rain
    draw_house()
    draw_rain()

    glutSwapBuffers()


# Idle function to animate
def animate():
    glutPostRedisplay()
    animate_rain()
    animate_day_night()


def init():
    initialize_rain()
    update_slope()
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)


glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(500, 100)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

glutCreateWindow(b"House with Rain and Day/Night Transition")
init()

glutDisplayFunc(display)
glutIdleFunc(animate)
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)

glutMainLoop()
