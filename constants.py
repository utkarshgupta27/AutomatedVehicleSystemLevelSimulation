""" Global Parameters """
SCALE = 4

""" Screen Parameters """
SCREEN_WIDTH = 128*SCALE
SCREEN_HEIGHT = 128*SCALE
GAME_TICKS = 60

""" Game Parameters """
NUM_OBSTACLES = 0

""" Map Parameters """
MAP_WIDTH = 254*SCALE
MAP_HEIGHT = 254*SCALE
BORDER = 4*SCALE

""" Vehicle Parameters """
VEHICLE_LENGTH = 11*SCALE     #(0.1m)
VEHICLE_WIDTH  = 5.5*SCALE     #(0.1m)
MASS   = 650/SCALE   #(kg)
C_DRAG_ROAD = 50     #0.4257
C_DRAG_GRASS = 50
C_BRAKE = 1000000
POS_BUFFER_LENGTH = 60

""" Obstacle Parameters """
OBSTACLE_LENGTH = 20*SCALE
OBSTACLE_WIDTH = 10*SCALE

""" Sound Parameters """
SOUND_ON = False

"""Map Parameters"""
# Define colors for different road types and greenery
colors = {
    "asphalt": (50, 50, 50),  # Dark Gray
    "gravel": (139, 69, 19),  # Saddle Brown
    "dirt": (210, 180, 140),  # Tan
    "snow": (255, 250, 250),  # Snow
    "greenery": (0, 128, 0)   # Green
}
roughness = {
    "asphalt": 0.1,   # Roughness scale: 0 (smooth) to 1 (very rough)
    "gravel": 0.6,
    "dirt": 0.8,
    "snow": 0.7
}
friction = {
    "asphalt": 0.9,   # Friction scale: 0 (no friction) to 1 (high friction)
    "gravel": 0.5,
    "dirt": 0.4,
    "snow": 0.3
}