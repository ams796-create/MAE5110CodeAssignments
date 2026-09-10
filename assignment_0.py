import numpy as np
import matplotlib.pyplot as plt
import timeit

from models import pendulum as model
from integrators_models import rk4 as integrator

# Basic simulation of the pendulum
params = model.generate_params()

# some set-up
initial_state = np.array([np.pi/4, 0]) # Starts at angle pi/4, with 0 initial velocity

timestep = 0.01 
sim_time = 5.0


n_timesteps = int(sim_time / timestep) + 1 # Gets an integer for the number of time steps from the specified sim time and timestep
time_traj = np.arange(n_timesteps) * timestep # Creates an array of values from 0 to # of timesteps (minus 1) and multiplies each by the timestep, (creates time vector)
state_traj = np.zeros((2, n_timesteps)) # 2 rows and # of timesteps columns array of zeros, used to store position and velocity
state_traj[:, 0] = initial_state

# simulation loop

start_time = timeit.default_timer()  # grab time

for step, t in enumerate(time_traj[:-1]):
    state_traj[:, step+1] = integrator.integrate(t, state_traj[:, step], params, timestep, model) # Integrate

print(f"Integration took {timeit.default_timer() - start_time:.4f} seconds")  # print time of integration
# sanity check the energies: since there is no actuation, and no damping, total energy should stay
# constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
# a stand-still.

kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)
total_energy= potential_energy + kinetic_energy


plt.figure()
plt.plot(time_traj, potential_energy, label="Potential energy")
plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title("Pendulum Energy")
plt.legend()
plt.tight_layout()
#plt.show() # Can't get this to work
plt.savefig("model_energy.png")

# phase portrait plot
plt.figure()
plt.plot(state_traj[0], state_traj[1])
plt.xlabel("angle θ (rad)")
plt.ylabel("angular velocity ω (rad/s)")
plt.title("Pendulum Phase Portrait")
plt.tight_layout()
plt.savefig("phase_portrait.png")




print("Plots complete")
