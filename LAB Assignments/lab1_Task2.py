import numpy as np
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
W_WIDTH, W_HEIGHT = 500, 500

# Global Variables
points = np.empty((0, 7), dtype=np.float64)  # Each point has [x, y, dx, dy, r, g, b]
blink_states = np.empty((0, 5), dtype=np.float64)  # [is_blinking, blink_start_time, r, g, b]
frozen_screen = False
bg_color = np.array([0.0, 0.0, 0.0])  # Background color
global_blinking = False  # Tracks global blinking state

def create_new_point(mouse_x, mouse_y):
    global points, blink_states, global_blinking
    if frozen_screen:
        return

    # Random velocity in diagonal directions
    velocity = np.random.choice([-0.05, 0.05], size=2)
    color = np.random.rand(3)  # Random color (RGB)

    # Append new point
    new_point = np.array([mouse_x, mouse_y, *velocity, *color])
    points = np.vstack([points, new_point])

    # Add blink state, syncing with global blinking
    new_blink = np.array([global_blinking, 0.0, *color])  # [is_blinking, blink_start_time, r, g, b]
    blink_states = np.vstack([blink_states, new_blink])


def draw_points():
    global points
    for point in points:
        x, y, r, g, b = point[0], point[1], point[4], point[5], point[6]
        glPointSize(10)
        glBegin(GL_POINTS)
        glColor3f(r, g, b)
        glVertex2f(x, y)
        glEnd()


def update_positions():
    global points
    if frozen_screen:
        return

    # Update positions
    points[:, :2] += points[:, 2:4]

    # Handle boundary collisions (reverse velocity)
    x_out_of_bounds = (points[:, 0] >= W_WIDTH / 2) | (points[:, 0] <= -W_WIDTH / 2)
    y_out_of_bounds = (points[:, 1] >= W_HEIGHT / 2) | (points[:, 1] <= -W_HEIGHT / 2)

    points[x_out_of_bounds, 2] *= -1  # Reverse x velocity
    points[y_out_of_bounds, 3] *= -1  # Reverse y velocity


def handle_blinking():
    global points, blink_states
    if frozen_screen or not global_blinking:  # Skip if frozen or blinking is globally off
        return

    current_time = time.time()
    for i, blink_state in enumerate(blink_states):
        if blink_state[0]:  # If blinking is active
            elapsed = (current_time - blink_state[1]) % 1.0  # Cycle every 1 second
            if elapsed < 0.5:
                points[i, 4:7] = bg_color  # Set to background color
            else:
                points[i, 4:7] = blink_state[2:5]  # Restore original color


def toggle_blinking():
    global blink_states, global_blinking
    global_blinking = not global_blinking  # Toggle global state
    for i, blink_state in enumerate(blink_states):
        blink_states[i, 0] = global_blinking  # Update blinking state for each point
        if not global_blinking:  # If blinking is turned off
            points[i, 4:7] = blink_state[2:5]  # Restore original color
        else:  # If blinking is turned on
            blink_states[i, 1] = time.time()  # Reset blinking timer


def adjust_speed(scale_factor, top_value=1.0, min_value=0.01):
    global points
    if frozen_screen:
        return

    new_velocities = points[:, 2:4] * scale_factor
    speeds = np.linalg.norm(new_velocities, axis=1)  # Magnitude of velocities
    speeds_clipped = np.clip(speeds, min_value, top_value)  # Ensure within [min_value, top_value]
    
    # Recalculate velocity components while preserving direction
    factors = speeds_clipped / np.maximum(speeds, 1e-6)  # Avoid division by zero
    points[:, 2:4] = new_velocities * factors[:, np.newaxis]


def screen_to_world(x, y):
    world_x = x - (W_WIDTH / 2)
    world_y = (W_HEIGHT / 2) - y
    return world_x, world_y


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(*bg_color, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)

    draw_points()
    glutSwapBuffers()


def mouse_listener(button, state, x, y):
    global frozen_screen
    if frozen_screen:
        return

    world_x, world_y = screen_to_world(x, y)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        create_new_point(world_x, world_y)
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        toggle_blinking()


def keyboard_listener(key, x, y):
    global frozen_screen
    if key == b' ':
        frozen_screen = not frozen_screen


def special_key_listener(key, x, y):
    if key == GLUT_KEY_UP:
        adjust_speed(scale_factor=2.0, top_value=3.0, min_value=0.01)  # Increase speed
    elif key == GLUT_KEY_DOWN:
        adjust_speed(scale_factor=0.5, top_value=1.0, min_value=0.01)  # Decrease speed


def animate():
    if not frozen_screen:
        update_positions()
        handle_blinking()
    glutPostRedisplay()


def init():
    glClearColor(*bg_color, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)


# OpenGL setup
glutInit()
glutInitWindowSize(W_WIDTH, W_HEIGHT)
glutInitWindowPosition(500, 100)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

glutCreateWindow(b"Interactive Moving Points")
init()

glutDisplayFunc(display)
glutIdleFunc(animate)
glutKeyboardFunc(keyboard_listener)
glutSpecialFunc(special_key_listener)
glutMouseFunc(mouse_listener)

glutMainLoop()
