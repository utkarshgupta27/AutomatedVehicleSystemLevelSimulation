import pygame
from pygame.locals import *
import numpy as np
import os
from scipy.integrate import odeint
from car_model import Car
from Road import Road

# Constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("Car Animation")

        self.clock = pygame.time.Clock()
        self.exit = False

        self.load_assets()
        self.car = Car()
        self.road = Road()
        self.initial_state = [0, 100, HEIGHT // 2, 0, 0]  # [position, velocity, lateral_position, lateral_velocity]

        self.steering_angle=0
        self.gear_state ='auto'  # can be 'auto', 'park', or 'manual'

    def load_assets(self):
        self.background_image = pygame.image.load(os.path.join(assets_path, "city", "background.png"))
        self.FourwayCrossing_image = pygame.image.load(os.path.join(assets_path, "city", "4Wayroad800x600.png"))
        self.car_image = pygame.image.load(os.path.join(assets_path, "car.png"))

    def apply_gear_behavior(self, throttle, steering_angle):
        if self.gear_state == 'auto':
            return throttle, steering_angle
        elif self.gear_state == 'park':
            return 0, 0  # No throttle, no steering when in parking gear
        elif self.gear_state == 'manual':
            return throttle, steering_angle  # Allow both throttle and steering in manual mode
        else:
            raise ValueError(f"Unknown gear state: {self.gear_state}")


    def control(self):
        # Get road properties and key controls
        lane_center, _ = self.draw_road()
        throttle_auto,steering_angle_auto  = self.control_car(lane_center) if self.gear_state =="auto" else (0,0)
        throttle_key, steering_angle_key  = self.control_with_keys()

        # Use automatic steering angle when in auto mode, otherwise use manual/key input
        throttle = throttle_auto if self.gear_state =="auto" else throttle_key
        steering_angle = steering_angle_auto if self.gear_state =="auto" else self.steering_angle
        
        throttle, steering_angle = self.apply_gear_behavior(throttle, self.steering_angle)

        if throttle_key:
            throttle = throttle_key
        if steering_angle_key is not None:
            self.steering_angle = steering_angle_key 

        return throttle

    def control_with_keys(self):
        keys = pygame.key.get_pressed()
        throttle = 320
        steering_changed=False
        if keys[K_UP]:
            throttle += 50
        elif keys[K_DOWN]:
            throttle -= 50

        if keys[K_RIGHT]:
            self.steering_angle += 10 * (np.pi / 180) #radians
            steering_changed=True
        elif keys[K_LEFT]:
            self.steering_angle -= 10 * (np.pi / 180)
            steering_changed=True
        
        if keys[K_a]:
            self.gear_state = 'auto'
        elif keys[K_p]:
            self.gear_state = 'park'
        elif keys[K_m]:
            self.gear_state = 'manual'
        print(f"Throttle: {throttle}")


        # Return None for the steering angle if no change was made
        return throttle, self.steering_angle if steering_changed else None
        
    def control_car(self, lane_center):
        if self.gear_state!='auto':
            return 0,0 # No throttle, steering
        error_x = WIDTH // 2 - lane_center[0]
        steering_angle = 0.05 * error_x
        throttle = 320
        return throttle, steering_angle

    def rotated_car(self, steering_angle):
        car_scaled = pygame.transform.scale(self.car_image, (44, 22))
        return pygame.transform.rotate(car_scaled, -np.degrees(steering_angle))

    def update_car_state(self, current_state, throttle, steering_angle,delta_t):
        t = np.linspace(0, delta_t, 2)
        new_state = odeint(self.car.equations_of_motion, current_state[:5], t, args=(throttle, 0, steering_angle, 0.05))
        return new_state[-1]

    def draw_car(self, state, rotated_img,orientation):
        
        # x_pos = lane_center[0] - rotated_img.get_width() / 2
        # y_pos = lane_center[1] - rotated_img.get_height() / 2
        x_pos = state[0]+ np.cos(orientation) * 5
        y_pos =  state[2]- np.sin(orientation)* 5
        x_pos_center=x_pos- rotated_img.get_width() / 2
        y_pos_center=y_pos -  rotated_img.get_height()/2
        self.screen.blit(rotated_img, (x_pos_center, y_pos_center))
        print(f"x_pos: {x_pos_center},y_pos: {y_pos_center}")

    def draw_road(self):
        if self.FourwayCrossing_image.get_size() != (WIDTH, HEIGHT):
            self.FourwayCrossing_image = pygame.transform.scale(self.FourwayCrossing_image, (WIDTH, HEIGHT))
        # Get road properties based on car position
        # properties = self.road.get_road_properties(int(self.position_pixels[i]))    
        lines, com_img = self.road.detect_lanes_pygame(self.FourwayCrossing_image)
        lane_center, _ = self.road.calculate_lane_center_and_slope(lines)
        com_img_swapped = com_img.swapaxes(0, 1)
        com_surface = pygame.surfarray.make_surface(com_img_swapped)
        # print(f"Lane Center: {lane_center}")
        return lane_center, com_surface

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True

    def display_text(self, message, x, y, color=(0, 0, 0)):
        font = pygame.font.SysFont(None, 25)
        text = font.render(message, True, color)
        self.screen.blit(text, (x, y))

    def update_display(self, position, velocity, steering_angle):

        self.display_text(f"Steering Angle: {np.degrees(steering_angle)}", 10, 10)
        self.display_text(f"Position_x: {position[0]:.2f}, Pos_x:{position[1]:.2f}", 10, 30)
        self.display_text(f"Velocity_x: {velocity[0]:.2f},Velocity_y: {velocity[1]:.2f}", 10, 50)
        self.display_text(f"Gear Mode: {self.gear_state.upper()}", 10, 70)

        pygame.display.flip()

    def run_simulation(self):
        self.screen.fill(WHITE)

        positions_over_time = [(self.initial_state[0],self.initial_state[2])]
        velocities_over_time = [(self.initial_state[1],self.initial_state[3])]
        orientations_over_time=[self.initial_state[4]]
        lane_center, _ = self.draw_road()

        while not self.exit:
            self.handle_events()

            throttle = self.control()
            delta_t = self.clock.tick(50)/1000.0 # seconds
            new_state = self.update_car_state(self.initial_state, throttle, self.steering_angle, delta_t)
            self.initial_state = new_state
            positions_over_time.append((new_state[0],new_state[2]))
            velocities_over_time.append((new_state[1],new_state[3]))
            orientations_over_time.append(new_state[4])
            lane_center, com_surface = self.draw_road()
            self.screen.blit(com_surface, (0, 0))  # blitting the processed road image
            if self.gear_state == "auto":
                self.initial_state[2]=lane_center[0]
            self.draw_car(self.initial_state, self.rotated_car(self.steering_angle),new_state[4])
            self.update_display(positions_over_time[-1], velocities_over_time[-1], self.steering_angle)

            self.clock.tick(50)
        
        pygame.quit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run_simulation()
