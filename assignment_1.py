# MAE 5510 Assignment 1 Rimless Wheel
import numpy as np
import matplotlib.pyplot as plt
from math import pi

from models import rimless_wheel as model
from integrators_models import rk4 as integrator

# Parameters of Rimless Wheel
params = {
        "gravity": 9.81,  # gravity m/s^2)
        "length": 0.5,  # spokes length (m)
        "mass": .2,  # point mass (kg)

    }
N = 20 # number of spokes
gamma = pi/6 # inclination angle (rad) 
alpha = pi/N # half the angle between adjacent spokes
coeff_restitution = 0.1  # coefficient of restitution 

# Set-Up
initial_state = np.array([gamma, 3]) # Starts at angle  from the vertical, with 0 initial angular velocity
timestep = 0.0001 
sim_time = 1

n_timesteps = int(sim_time / timestep) + 1 # Gets an integer for the number of time steps from the specified sim time and timestep
time_traj = np.arange(n_timesteps) * timestep # Creates an array of values from 0 to # of timesteps (minus 1) and multiplies each by the timestep, (creates time vector)
state_traj = np.zeros((2, n_timesteps)) # 2 rows and # of timesteps columns array of zeros, used to store position and velocity
state_traj[:, 0] = initial_state

# Simulation Loop
for step, t in enumerate(time_traj[:-1]):
    state_traj[:, step+1] = integrator.integrate(t, state_traj[:, step], params, timestep, model)

    theta = state_traj[0, step+1]
    theta_dot = state_traj[1, step+1]

    rolling_foward = theta_dot>0 and theta>= gamma + alpha # end condition of rolling foward is theta=gamma+alpha
    rolling_backward = theta_dot<0 and theta<= gamma - alpha # end condition of rolling backward is alpha=gamma-theta

    if rolling_foward or rolling_backward:
        if  rolling_foward == True:
            theta = theta - 2*alpha
        elif rolling_backward == True:
            theta = theta + 2*alpha

        theta_dot=theta_dot*np.cos(2*alpha)
        state_traj[0, step+1] = theta
        state_traj[1, step+1] = theta_dot


# Phase Portrait Plot
plt.figure()
plt.plot(state_traj[0], state_traj[1], label='Trajectory')
plt.xlabel("angle θ (rad)")
plt.ylabel("angular velocity ω (rad/s)")
plt.title("Rimless Wheel Phase Portrait")
plt.tight_layout()

plt.axvline(gamma - alpha, color="tab:orange", linestyle="--", label=r"$\gamma - \alpha$")
plt.axvline(gamma + alpha, color="tab:green", linestyle="--", label=r"$\gamma + \alpha$")
plt.axvline(gamma, color="gray", linestyle=":", label=r"$\gamma$")
plt.axhline(0, color="black", linewidth=0.5)
plt.legend()
plt.savefig("phase_portrait.png")
print("Phase Portrait complete, Please check folder for updated phase_portrait.png")