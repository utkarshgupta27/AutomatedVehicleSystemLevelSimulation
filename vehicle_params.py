vehicle_parameters = {
    # Geometric properties
    "length": 4.5,               # Total vehicle length in meters
    "width": 1.8,                # Total vehicle width in meters
    "height": 1.5,               # Total vehicle height in meters
    "wheelbase": 2.7,            # Distance between front and rear axles in meters
    "track_width": 1.6,          # Distance between the centers of two wheels on the same axle in meters
    
    # Mass properties
    "mass": 1500,                # Vehicle's total mass in kg
    "inertia": 2800,             # Moment of inertia (generally around the vehicle's vertical axis for yaw motion)
    "center_of_gravity": {
        "x": 0.5,                # Location of the center of gravity on the vehicle's longitudinal axis (from front)
        "y": 0,                  # Location of the center of gravity on the vehicle's lateral axis (generally center)
        "z": 0.4                 # Height of the center of gravity from the ground (important for roll dynamics)
    },

    # Powertrain properties
    "max_power": 120,            # Maximum power of the engine in kW
    "max_torque": 320,           # Maximum torque in N.m
    "transmission_ratios": [3.5, 2.5, 1.8, 1.4, 1.0],  # Gears
    "final_drive_ratio": 3.2,    # Final drive ratio
    "engine_efficiency": 0.8,    # A measure of how efficiently the engine converts fuel energy to work
    "traction_limit": 5.0, # max m/s^2,
    "max_breaking_force": 5000,
    
    # Tires
    "tire_radius": 0.3,          # Radius of the tire in meters
    "tire_width": 0.2,           # Width of the tire in meters
    "tire_slip_angle": 0.1,      # Typical tire slip angle in radians (used for traction modeling)
    "tire_friction_coefficient": 0.9,  # Coefficient of friction for the tires (may vary based on road conditions)
    "tire_cornering_stiffness": 10000,

    # Aerodynamics
    "drag_coefficient": 0.3,     # Drag coefficient (Cd) for the vehicle
    "frontal_area": 2.2,         # Frontal area in m^2 (used for drag calculations)
    
    # Suspension properties (assuming a simple linear spring-damper model)
    "spring_constant": 30000,    # Spring constant in N/m
    "damping_ratio": 0.3,        # Damping ratio (used to compute damper coefficient)
}
