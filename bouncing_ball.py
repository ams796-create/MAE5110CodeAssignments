import numpy as np
import matplotlib.pyplot as plt
import timeit

from models import bouncing_ball as model
from integrators_models import rk4 as integrator

# Basic simulation of the pendulum
params = model.generate_params()

# set-up
initial_state = np.array([1, 0]) # initial height 1 m

timestep = 0.0001 
sim_time = 5.0

n_timesteps = int(sim_time / timestep) + 1 # Gets an integer for the number of time steps from the specified sim time and timestep
time_traj = np.arange(n_timesteps) * timestep # Creates an array of values from 0 to # of timesteps (minus 1) and multiplies each by the timestep, (creates time vector)
state_traj = np.zeros((2, n_timesteps)) # 2 rows and # of timesteps columns array of zeros, used to store position and velocity
state_traj[:, 0] = initial_state

# simulation loop
for step, t in enumerate(time_traj[:-1]):
    state_traj[:, step+1] = integrator.integrate(t, state_traj[:, step], params, timestep, model) # Integrate

    if state_traj[0, step+1] < 0: # check if height is below ground
        state_traj[0, step+1] = state_traj[0, step+1] * -1  # reflect height
        state_traj[1, step+1] = state_traj[1, step+1] * -1  # reverse velocity

   
# sanity check the energies: since there is no actuation, and no damping, total energy should stay
# constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
# a stand-still.

kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)
total_energy= potential_energy + kinetic_energy
print(total_energy[0], total_energy[-1])
print((total_energy[-1] - total_energy[0]) / total_energy[0] * 100)



plt.figure()
plt.plot(time_traj, potential_energy, label="Potential energy")
plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title("Bouncing Ball Energy")
plt.legend()
plt.tight_layout()
#plt.show() # Can't get this to work
plt.savefig("bouncing_ball_energy.png")

# TODO: make a phase portrait plot
plt.figure()
plt.plot(state_traj[0], state_traj[1])
plt.xlabel("height")
plt.ylabel("velocity (m/s)")
plt.title("Bouncing Ball Phase Portrait")
plt.tight_layout()
plt.savefig("phase_portrait.png")




print("Plots complete")
