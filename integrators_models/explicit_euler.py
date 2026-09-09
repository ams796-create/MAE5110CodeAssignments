import numpy as np

def integrate(t, state, params, timestep,model):
    next_state = state + timestep * model.dynamics(t, state, params)
    return next_state