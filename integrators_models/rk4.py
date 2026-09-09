import numpy as np

def integrate(t, state, params, timestep, model):
    k1 = model.dynamics(t, state, params)
    k2 = model.dynamics(t+timestep/2 , state + k1*(timestep/2), params)
    k3 = model.dynamics(t+timestep/2, state + k2*(timestep/2), params) 
    k4 = model.dynamics(t+timestep, state + timestep*k3, params) 

    next_state = state + (timestep/6)*(k1 + 2*k2 + 2*k3 + k4)
    return next_state