from vehicle_params import vehicle_parameters
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
def main():
    #vehicle_length= vehicle_parameters("length")
    pass

class Car(object):

    def __init__(self):
        self.mass= vehicle_parameters["mass"]
        self.drag_coefficient= vehicle_parameters["drag_coefficient"]
        self.max_steering_angle= np.pi/6  #30 degrees in radian
        self.max_acceptable_acceleration = 5.0 # in m/s^2
        pass
    
    def traction_control(self, acceleration, engine_torque):
        if acceleration > self.max_acceptable_acceleration:
            return engine_torque* self.max_acceptable_acceleration / acceleration
        return engine_torque
    
    def longitudinal_dynamics(self,v, engine_torque, brake_force):
        rho = 1.225 # air density in kg /m^3
        g =9.81
        a=0
        
        F_engine= engine_torque/vehicle_parameters["tire_radius"]
        F_drag = 0.5 * rho * vehicle_parameters["frontal_area"] * self.drag_coefficient * v**2
        F_rolling = self.mass * g * 0.015 # coefficient of rolling = 0.015

        engine_torque= self.traction_control(a,engine_torque)
        F_engine= engine_torque/vehicle_parameters["tire_radius"]

        F_net = F_engine - F_drag - F_rolling - brake_force
        #print(F_net)
        a = F_net /self.mass
        return a
    
    def lateral_dynamics(self, v_y, slip_angle):
        F_cornering = -vehicle_parameters["tire_cornering_stiffness"] * slip_angle
        a_y = F_cornering / self.mass
        return a_y

    def equations_of_motion(self, state, t , engine_torque, brake_force, steering_angle, slip_angle):    
        position, velocity, lateral_position, lateral_velocity, orientation = state # current state variables
        slip_angle=np.arctan2(lateral_velocity,velocity)
        adjust_slip_angle = slip_angle + steering_angle
        acceleration = self.longitudinal_dynamics(velocity, engine_torque, brake_force)
        lateral_acceleration= self.lateral_dynamics(lateral_velocity, adjust_slip_angle)
        dv_dt=acceleration
        dv_y_dt=lateral_acceleration
        dx_dt=velocity * np.cos(orientation + steering_angle)
        dy_dt=velocity * np.sin(orientation + steering_angle)
        dtheta_dt= velocity / vehicle_parameters["wheelbase"] * np.tan(steering_angle)
        return [dx_dt, dv_dt,dy_dt, dv_y_dt, dtheta_dt]


if __name__=="__main__":
    main()
    car=Car()
    #Initial state
    initial_state=[0,0,0,0,0] # [position, velocity, lateral_position, lateral_velocity]
    # Sample inputs
    engine_torque = 320
    slip_angle = 0.05
    brake_force=0 
    steering_angle = 0# Adjust between -vehicle["max_steering_angle"] and vehicle["max_steering_angle"]
    #time points
    t=np.linspace(0,10,100) # from 0 to 10 sec, 100 points

    #solve differential equations
    solution = odeint(car.equations_of_motion,initial_state, t, args=(engine_torque, brake_force, steering_angle, slip_angle))
    positions=solution[:,0]
    velocities=solution[:,1]
    print(solution)
    print("positions, velocity: {},{}".format(positions, velocities))

    #plotting velocity vs time
    plt.figure(figsize=(10,5))
    plt.subplot(2,1,1)
    plt.plot(t,velocities, label='Velocity (m/s)', color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('velocity (m/s)')
    plt.title('Velocity vs Time')
    plt.grid(True)
    plt.legend()
    #plotting position vs time
    plt.subplot(2,1,2)
    plt.plot(t,positions, label='Position (m)', color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m/s)')
    plt.title('Position vs Time')
    plt.grid(True)
    plt.legend()

    plt.tight_layout
    plt.show()