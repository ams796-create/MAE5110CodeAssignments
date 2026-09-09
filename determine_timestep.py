import numpy as np
import matplotlib.pyplot as plt

from models import pendulum as model
from integrators_models import rk4 as integrator

# Basic simulation of the model
params = model.generate_params()

# some set-up
initial_state = np.array([np.pi/4, 0]) # Starts at angle pi/4, with 0 initial velocity

#timestep = 1e-5
timesteps = [1e-2, 1e-1, 2e-1, 3e-1, 4e-1] 
sim_time = 5.0

plt.figure(1)  # single figure to add one line to per timestep
for timestep in timesteps:
    n_timesteps = int(sim_time / timestep) + 1 # Gets an integer for the number of time steps from the specified sim time and timestep
    time_traj = np.arange(n_timesteps) * timestep # Creates an array of values from 0 to # of timesteps (minus 1) and multiplies each by the timestep, (creates time vector)
    state_traj = np.zeros((2, n_timesteps)) # 2 rows and # of timesteps columns array of zeros, used to store position and velocity
    state_traj[:, 0] = initial_state

    # simulation loop
    for step, t in enumerate(time_traj[:-1]):
        state_traj[:, step+1] = integrator.integrate(t, state_traj[:, step], params, timestep, model) # Integrate
    # sanity check the energies: since there is no actuation, and no damping, total energy should stay
    # constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
    # a stand-still.

    kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)
    total_energy = potential_energy + kinetic_energy
    plt.figure(1)
    plt.plot(time_traj, total_energy, label=f"h = {timestep:g}")

    pct_change_traj = abs((total_energy - total_energy[0]) / total_energy[0] * 100)
    plt.figure(2)  # switch to percent change figure
    plt.plot(time_traj, pct_change_traj, label=f"h = {timestep:g}")





plt.axhline(y=2, linestyle='dotted')  # chosen limit of 5%
plt.xlabel("Time (s)")
plt.ylabel("Percent change in total energy (%)")
plt.title("Energy drift over time by timestep")
plt.legend()
plt.tight_layout()
plt.savefig("energy_pct_change_vs_time.png")


print("Plot complete")
