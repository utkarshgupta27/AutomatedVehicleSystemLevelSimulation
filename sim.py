import pygame
import numpy as np
from scipy.integrate import odeint
from constants import *
from vehicle_params import vehicle_parameters
from Road import Road

# Constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
RHO = 1.225  # air density in kg/m^3
G = 9.81
F_BRAKE_MAX = 1000  # Maximum brake force
FPS=30
dt = 0.05  # Time step for simulation
engine_torque = 320
slip_angle = 0.05

class CarState:
    def __init__(self, position=0, velocity=0, lateral_position=0, lateral_velocity=0, orientation=0) -> None:
        self.position = position
        self.velocity = velocity
        self.lateral_position = lateral_position
        self.lateral_velocity = lateral_velocity
        self.orientation = orientation #heading
        # self.steering_angle= #front wheel
    def as_list(self):
        return [self.position,self.velocity,self.lateral_position,self.lateral_velocity, self.orientation]

class Car:
    def __init__(self):
        self.mass = vehicle_parameters["mass"]
        self.drag_coefficient = vehicle_parameters["drag_coefficient"]
        self.max_steering_angle = np.pi / 6
        self.max_acceptable_acceleration = 50.0
        self._throttle = 1
        self._brake = 0
        self._steering_angle = 0
    @property
    def throttle(self):
        return self._throttle
    @throttle.setter
    def throttle(self, value):
        self._throttle = max(0, min(1, value))
        print("Debug_set_throttle: ",self._throttle)
    @property
    def brake(self):
        return self._brake
    @brake.setter
    def brake(self, value):
        self._brake = max(0, min(1, value))
        print("Debug_set_brake: ",self._brake)
    @property
    def steering_angle(self):
        return self._steering_angle
    @steering_angle.setter
    def steering_angle(self,value):
        self._steering_angle = max(-self.max_steering_angle,min(value,self.max_steering_angle))
    def traction_control(self, acceleration, engine_torque):
        if acceleration > self.max_acceptable_acceleration:
            return engine_torque * self.max_acceptable_acceleration / acceleration
        return engine_torque

    def longitudinal_dynamics(self, v, engine_torque):
        F_drag = 0.5 * RHO * vehicle_parameters["frontal_area"] * self.drag_coefficient * v ** 2
        F_rolling = self.mass * G * 0.015

        F_net_without_engine_brake = -F_drag - F_rolling
        a = F_net_without_engine_brake / self.mass

        engine_max_torque = self.traction_control(a, engine_torque)
        F_engine_max = engine_max_torque / vehicle_parameters["tire_radius"]
        F_engine = self._throttle * F_engine_max
        F_brake = self._brake * F_BRAKE_MAX

        F_net = F_engine + F_net_without_engine_brake - F_brake

        a = F_net / self.mass
        print("Debug_long_dynamics brake,F_brake,throttle,F_engine,F_net:",self.brake,"\t",F_brake,"\t",self.throttle,"\t",F_engine,"\t",F_net)
        return a

    def lateral_dynamics(self, v_y, slip_angle):
        F_cornering = -vehicle_parameters["tire_cornering_stiffness"] * slip_angle
        a_y = F_cornering / self.mass
        return a_y

    def equations_of_motion(self, state, t, engine_torque, steering_angle, slip_angle):
        position, velocity, lateral_position, lateral_velocity, orientation = state
        slip_angle = np.arctan2(lateral_velocity, velocity)
        adjust_slip_angle = slip_angle + steering_angle

        acceleration = self.longitudinal_dynamics(velocity, engine_torque)
        lateral_acceleration = self.lateral_dynamics(lateral_velocity, adjust_slip_angle)

        dv_dt = acceleration
        dv_y_dt = lateral_acceleration
        dx_dt = velocity * np.cos(orientation)
        dy_dt = velocity * np.sin(orientation)
        dtheta_dt = velocity  * np.sin(steering_angle) / vehicle_parameters["wheelbase"]
        print("debug_equation_of_motion, dtheta_dt:",dtheta_dt)
        return [dx_dt, dv_dt, dy_dt, dv_y_dt, dtheta_dt]

    def get_next_state(self, state: CarState, Dt, engine_torque, slip_angle, steering_angle) -> CarState:
        # Integrate equations of motion over dt to get the next state
        t = [0, Dt]
        current_state_list=state.as_list()
        next_state_values = odeint(self.equations_of_motion, current_state_list, t, args=(engine_torque, steering_angle, slip_angle))[1]
        return CarState(*next_state_values)


class Simulation:
    def __init__(self):
        pygame.init()
        self.setup_display()
        self.car_image = pygame.image.load("car.png")
        self.car = Car()
        self.exit = False
        self.road = Road()
        self.positions, self.lateral_positions, self.orientations, self.velocities = [],[],[],[]
        self.current_state=CarState()

    def setup_display(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("Car Animation")
        self.clock = pygame.time.Clock()

    def display_text(self, message, x, y, color=(0, 0, 0)):
        font = pygame.font.SysFont(None, 25)
        text = font.render(message, True, color)
        self.screen.blit(text, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
        self._handle_continuous_keys()

    def _handle_continuous_keys(self):
        keys = pygame.key.get_pressed()
        
        # Define a factor for steering angle change
        steering_factor = 0.025 * self.car.max_steering_angle

        if keys[pygame.K_UP]:
            self.car.throttle = min(self.car.throttle + 0.1, 1)  # limit throttle to 1
            if self.car.brake > 0:
                self.car.brake = max(self.car.brake - 0.1, 0)        
        if keys[pygame.K_DOWN]:
            self.car.brake = min(self.car.brake + 0.1, 1)  # limit brake to 1
            if self.car.throttle > 0:
                self.car.throttle = max(self.car.throttle - 0.1, 0)

        if keys[pygame.K_LEFT]:
            self.car.steering_angle -= steering_factor
        if keys[pygame.K_RIGHT]:
            self.car.steering_angle += steering_factor
        if keys[pygame.K_SPACE]:
            self.car.throttle = 0
            self.car.brake = 0
            self.car.steering_angle = 0  # Reset the steering when spacebar is pressed

        # Print debug info
        print("Debug_steering_angle: ", self.car.steering_angle)
        print("Debug_max_steering_angle: ", self.car.max_steering_angle)
        print("Debug_min_steering_angle: ", -self.car.max_steering_angle)

    def update_dynamics(self, DT):
        self.current_state = self.car.get_next_state(self.current_state, DT, engine_torque, slip_angle, self.car.steering_angle)
        self.positions = np.append(self.positions, self.current_state.position)
        self.velocities = np.append(self.velocities, self.current_state.velocity)
        self.lateral_positions = np.append(self.lateral_positions, self.current_state.lateral_position)
        self.orientations= np.append(self.orientations,self.current_state.orientation)

    def rotated_car(self, orientation):
        car_scaled = pygame.transform.scale(self.car_image, (44, 22))
        rotated = pygame.transform.rotate(car_scaled, -np.degrees(orientation))
        return rotated if rotated.get_width() != 0 and rotated.get_height() != 0 else car_scaled

    def draw_car(self, x_pos, y_pos, rotated_img, orientation):
        car_width, car_height = rotated_img.get_size()
        # x_pos += np.cos(orientation) * 5
        # y_pos -= np.sin(orientation) * 5
        self.screen.blit(rotated_img, (WIDTH / 2 + x_pos - car_width / 2, HEIGHT / 2 + y_pos - car_height / 2))

    def draw_road(self, i):
        properties = self.road.get_road_properties(int(self.positions[i]))
        self.screen.fill(colors["greenery"])
        pygame.draw.rect(self.screen, colors[properties["road_type"]], (0, HEIGHT // 3, WIDTH, HEIGHT // 3))
    def calculate_distance(self, x1, y1, x2, y2):
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def calculate_acceleration(self, velocities, i):
        if i == 0:
            return 0
        return (velocities[i] - velocities[i-1]) / 0.02  # dt = 1/50 = 0.02
    
    def run(self):
        positions_over_time = []
        lateral_positions_over_time = []
        velocities_over_time = []
        accelerations_over_time=[]
        positions_over_time.append(self.current_state.position)
        lateral_positions_over_time.append(self.current_state.lateral_position)
        velocities_over_time.append(self.current_state.velocity)
        accelerations_over_time.append(0)
        i = 0
        pygame.key.set_repeat(100, 50)  # Delay of 100ms before key repeats, then every 50ms

        while not self.exit:
            # dt = self.clock.tick(FPS) / 1000.0  # Get time taken for the frame in seconds
            self.handle_events()
            self.update_dynamics(dt)
            # self.render(0)
            self.screen.fill((0, 0, 0))

            self.draw_road(i)

            positions_over_time.append(self.current_state.position)
            lateral_positions_over_time.append(self.current_state.lateral_position)
            velocities_over_time.append(self.current_state.velocity)
            acc = self.calculate_acceleration(velocities_over_time, i)
            accelerations_over_time.append(acc)
            
            pos_text = "Position_x: {:.2f}, Position_y: {:.2f}".format(self.current_state.position,self.current_state.lateral_position)
            vel_text = "Velocity: {:.2f}".format(self.current_state.velocity)
            acc_text ="Acceleration: {:.2f}".format(acc)

            self.display_text(pos_text, 10, 30)
            self.display_text(vel_text, 10, 50)
            self.display_text(acc_text,10,70)

            car_rotated_image = self.rotated_car(self.orientations[i])
            self.draw_car(self.positions[i], self.lateral_positions[i], car_rotated_image, self.orientations[i])

            pygame.display.flip()
            i += 1
            if i >= len(self.positions):
                i = 0
            self.clock.tick(FPS)


if __name__ == "__main__":
    sim = Simulation()
    sim.run()
    pygame.quit()
