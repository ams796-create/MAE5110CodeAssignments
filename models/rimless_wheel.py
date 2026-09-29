import numpy as np

def dynamics(t,state,params):
    gravity = params["gravity"]
    spoke_length = params["spoke_length"]

    angle = state[0]
    angular_velocity = state[1]

    angular_acceleration = (gravity * np.sin(angle))/spoke_length

    state_derivative = np.array([angular_velocity, angular_acceleration])
    return state_derivative

def generate_params():
    params = {
        "gravity": 9.81,
        "num_spokes": 6,
        "spoke_length": 1,
        "downhill_inc": np.deg2rad(20)
    }
    params["alpha"] = np.pi/params["num_spokes"]

    return params

def detect_impact(state,params):
    angle = state[0]

    detect_impact_angle = params["downhill_inc"] + params["alpha"]

    return angle >= detect_impact_angle

def reset_impact(state,params):
    angular_velocity = state[1]

    reset_impact_angle = params["downhill_inc"] - params["alpha"]

    reset_angular_velocity = angular_velocity * np.cos(2 * params["alpha"])

    reset_state = [reset_impact_angle, reset_angular_velocity]

    return reset_state