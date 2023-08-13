from datetime import time
import pygame
from pygame.locals import *
import numpy as np
from car_model import Car
from scipy.integrate import odeint
from constants import *
from Road import Road
# Window dimensions
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255) # Color of background
class Simulation:
    
    def __init__(self):
        pygame.init() # Initialize pygame
        # Set up the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE|DOUBLEBUF|RESIZABLE)
        pygame.display.set_caption("Car Animation")

        self.clock = pygame.time.Clock()
        self.exit = False
        # Load the car image
        self.car_image = pygame.image.load("car.png")  # Assuming you have a car.png image
        self.car=Car()
        self.road = Road()

        #precompute the car motion
        self.position_pixels, self.lateral_positions_pixels,self.orientations, self.velocities= self.position_pixel()
    
    def position_pixel(self):
        #Initial state
        initial_state=[0,0,0,0,0] # [position, velocity, lateral_position, lateral_velocity]
        # Sample inputs
        engine_torque = 320
        slip_angle = 0.05
        brake_force=0 # for full brake put 845.0

        # Time points
        t_points={
            'straight': np.linspace(0, 4, 5 * 50),#From 0 to 5 sec, 50 points
            'turn_right': np.linspace(4, 5, 50),
            'little_straight': np.linspace(5, 7, 2 * 50),
            'turn_left': np.linspace(7, 15, 8 * 50)        
        }
        steering_angle = {
            'straight': 0,
            'turn_right': 30 * (np.pi / 180),
            'little_straight':0,
            'turn_left': -30 * (np.pi / 180)
        }

        #solve differential equations
        def solve(t, angle, state):
            return odeint(self.car.equations_of_motion,state, t_points[t], args=(engine_torque, brake_force, steering_angle[angle], slip_angle))
    #   # Concatenate solutions
        solutions=[solve('straight','straight',initial_state)]
        for t in ['turn_right','little_straight','turn_left']:
            solutions.append(solve(t,t,solutions[-1][-1]))
        solution = np.vstack(solutions)
        positions=solution[:,0]
        velocities=solution[:,1]
        lateral_positions = solution[:,2]
        
        # Convert positions to screen coordinates
        # Note: This is a basic scaling for demonstration purposes.
        positions_pixels = positions * 30  # Scaling factor
        lateral_positions_pixels = -lateral_positions * 30  # Scaling factor
        orientation = solution[:,4]
        # print("Time: {}s | Position: {} | Lateral Position: {} | Orientation: {}".format(time, positions_pixels, lateral_positions_pixels, orientation))

        return positions_pixels,lateral_positions_pixels, orientation, velocities

    def rotated_car(self, steering_angle):
        """return the car image rotated by the given angle
            in pygame rotation is counter clockwise, but 
            in our model, positive steering angle means clockwise (right turn) 
        """
        car_scaled = pygame.transform.scale(self.car_image,(44,22))
        return pygame.transform.rotate(car_scaled, -np.degrees(steering_angle))
    
    def draw_car(self,x_pos, y_pos, rotated_img,orientation):
        """Draw the car at the specified x& Y-coordinate."""
        # Get the size of the car image
        car_width, car_height = rotated_img.get_size()
        #calculating new position based on the orientation of the car
        x_pos += np.cos(orientation) * 5
        y_pos -= np.sin(orientation)* 5
        # Draw the car at the bottom of the screen and at the specified x-coordinate
        x_center=WIDTH/2 + x_pos - car_width/2
        y_center=HEIGHT/2 - y_pos- car_height/2
            # Get road properties based on car position
        self.screen.blit(rotated_img, (x_center, y_center))
    
    def draw_road(self,i):
        # Get road properties based on car position
        properties = self.road.get_road_properties(int(self.position_pixels[i]))

        # Draw the greenery on top and bottom
        self.screen.fill(colors["greenery"])
        print(properties)
        pygame.draw.rect(self.screen, colors[properties["road_type"]], (0, HEIGHT // 3, WIDTH, HEIGHT // 3))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
    def display_text(self,message, x, y, color=(0, 0, 0)):
        font = pygame.font.SysFont(None, 25)
        text = font.render(message, True, color)
        self.screen.blit(text, (x, y))
    def draw_graph(self, positions, velocities):
        """Draw a graph representing the car's position and velocity over time."""
        graph_width, graph_height = 300, 150
        graph_x, graph_y = WIDTH - graph_width - 10, 10

        # Draw graph background
        pygame.draw.rect(self.screen, (200, 200, 200), (graph_x, graph_y, graph_width, graph_height))

        # Assuming max_position and max_velocity to normalize values
        max_position = max(positions)
        max_velocity = max(velocities)

        # Plotting points
        for i in range(1, len(positions)):
            pygame.draw.line(self.screen, (255, 0, 0), 
                             (graph_x + (i - 1) * graph_width / len(positions), graph_y + graph_height - (positions[i-1] / max_position) * graph_height),
                             (graph_x + i * graph_width / len(positions), graph_y + graph_height - (positions[i] / max_position) * graph_height))

            pygame.draw.line(self.screen, (0, 0, 255), 
                             (graph_x + (i - 1) * graph_width / len(positions), graph_y + graph_height - (velocities[i-1] / max_velocity) * graph_height),
                             (graph_x + i * graph_width / len(positions), graph_y + graph_height - (velocities[i] / max_velocity) * graph_height))

        # Legend
        self.display_text("Position (red)", WIDTH - 200, graph_y + graph_height + 5)
        self.display_text("Velocity (blue)", WIDTH - 200, graph_y + graph_height + 25)

if __name__ == "__main__":
    sim=Simulation()
    # Main loop
    i = 0
    sim.screen.fill(WHITE)
    positions_over_time = []
    velocities_over_time = []
    while not sim.exit:
        sim.handle_events()        
        # Draw car
        if i < len(sim.position_pixels):
            sim.draw_road(i)
            orientation= sim.orientations[i]
            steering_angle = orientation
            font = pygame.font.SysFont(None, 25)
            text = font.render("Steering Angle: {:.2f}".format(steering_angle), True, (0, 0, 0))
            # Displaying position and velocity:
            pos_text = "Position: {:.2f}".format(sim.position_pixels[i])
            vel_text = "Velocity: {:.2f}".format(sim.lateral_positions_pixels[i])
            sim.display_text(pos_text, 10, 30)
            sim.display_text(vel_text, 10, 50)

            sim.screen.blit(text, (10,10))
            current_position = sim.position_pixels[i]
            current_velocity = sim.velocities[i]  # Assuming the solution's second column is velocity
            
            positions_over_time.append(current_position)
            velocities_over_time.append(current_velocity)

            # Draw graphs and speedometer
            sim.draw_graph(positions_over_time[-100:], velocities_over_time[-100:])  # Only display last 100 values
            rotated_img = sim.rotated_car(steering_angle)
            sim.draw_car(sim.position_pixels[i], sim.lateral_positions_pixels[i], rotated_img, orientation)
            i += 1
        else:
            rotated_img = sim.rotated_car(0)

        pygame.display.flip()
        sim.clock.tick(50)  # 30 frames per second

    pygame.quit()
