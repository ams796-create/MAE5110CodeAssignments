import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("plots", exist_ok=True)

from models import rimless_wheel as model
from integrators import rk4 as integrator

# ==================================================
# functions
# ==================================================

def test_initial_state(initial_state, params):

    state = initial_state.copy()

    dt = 1e-4
    sim_time = 5.0
    time = np.arange(0, sim_time, dt)

    previous_omega = None
    tolerance = 1e-3

    for t in time[:-1]:

        state = integrator.integrate(model.dynamics, t, state, dt, params)

        if state[1] <= 0:
            return 0

        if model.detect_impact(state, params):

            state = model.reset_impact(state, params)
            current_omega = state[1]

            if previous_omega is not None:
                if abs(current_omega - previous_omega) < tolerance:
                    return 1

            previous_omega = current_omega

    return 0


def one_step_return(omega, params):

    state = np.array([params["downhill_inc"] - params["alpha"], omega])

    dt = 1e-4
    sim_time = 5.0
    time = np.arange(0, sim_time, dt)

    for t in time[:-1]:

        state = integrator.integrate(model.dynamics, t, state, dt, params)

        if state[1] <= 0:
            return None

        if model.detect_impact(state, params):

            state = model.reset_impact(state, params)

            return state[1]

    return None

def calculate_roa(theta_values, omega_values, params):

    roa = np.zeros((len(omega_values), len(theta_values)))

    for i, omega in enumerate(omega_values):
        for j, theta in enumerate(theta_values):

            initial_state = np.array([theta, omega])

            roa[i, j] = test_initial_state(initial_state, params)

    return roa

def limit_cycle(fixed_omega, params):

    state = np.array([params["downhill_inc"] - params["alpha"], fixed_omega])

    dt = 1e-4
    sim_time = 2.0
    time = np.arange(0, sim_time, dt)
    theta_cycle = []
    omega_cycle = []

    for t in time[:-1]:

        theta_cycle.append(state[0])
        omega_cycle.append(state[1])

        state = integrator.integrate(model.dynamics, t, state, dt, params)

        if model.detect_impact(state, params):
            break

    return np.array(theta_cycle), np.array(omega_cycle) 


def calculate_return_map(omega_inputs, params):

    omega_outputs = []

    for omega in omega_inputs:

        next_omega = one_step_return(omega, params)

        if next_omega is None:
            omega_outputs.append(np.nan)
        else:
            omega_outputs.append(next_omega)

    return np.array(omega_outputs)

def plot_roa(theta_values, omega_values, roa, title, filename):

    plt.figure()
    plt.imshow(roa, origin="lower", aspect="auto",
        extent=[theta_values[0], theta_values[-1], omega_values[0], omega_values[-1]], 
        vmin=0, vmax=1)

    cbar = plt.colorbar(ticks=[0, 1])
    cbar.ax.set_yticklabels(["Failure", "Stable Rolling"])

    plt.xlabel("Initial Angle (rad)")
    plt.ylabel("Initial Angular Velocity (rad/s)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig("plots/" + filename, dpi=300)
    plt.close() 


def find_fixed_point(omega_inputs, omega_outputs):

    valid = ~np.isnan(omega_outputs)
    difference = np.abs(omega_outputs[valid] - omega_inputs[valid])
    fixed_index = np.argmin(difference)
    fixed_omega = omega_inputs[valid][fixed_index]

    return fixed_omega

def calculate_floquet(fixed_omega, params):

    delta = 0.01

    return_minus = one_step_return(fixed_omega - delta, params)
    return_plus = one_step_return(fixed_omega + delta, params)

    if return_minus is None or return_plus is None:
        return np.nan

    floquet = (return_plus - return_minus) / (2 * delta)

    return floquet

# ==================================================
# implementation and plots
# ==================================================
params = model.generate_params()

# # Brute Force RoA Estimation
# theta_values = np.linspace(params["downhill_inc"] - params["alpha"],
#     params["downhill_inc"] + params["alpha"], 25)

# omega_values = np.linspace(0.1, 2.0, 25)
# roa = calculate_roa(theta_values, omega_values, params)

# # Poincare Return Map

# omega_inputs = np.linspace(0.1, 2.5, 100)
# omega_outputs = calculate_return_map(omega_inputs, params)
# fixed_omega = find_fixed_point(omega_inputs,omega_outputs)
# floquet = calculate_floquet(fixed_omega,params)

# print("Fixed point:", fixed_omega)
# print("Floquet multiplier:", floquet)

# # Limit cycle
# theta_cycle, omega_cycle = limit_cycle(fixed_omega, params)

# # plot RoA
# plt.figure()

# plt.imshow(roa, origin="lower", aspect="auto", extent=[theta_values[0], theta_values[-1],
#         omega_values[0], omega_values[-1]], vmin=0, vmax=1)

# cbar = plt.colorbar(ticks=[0, 1])
# cbar.ax.set_yticklabels(["Failure", "Stable Rolling"])

# plt.plot(theta_cycle, omega_cycle, "k-", linewidth=2, label="Stable Limit Cycle")

# plt.plot(params["downhill_inc"] - params["alpha"], fixed_omega, "ko", label="Poincare Fixed Point")

# plt.xlabel("Initial Angle (rad)")
# plt.ylabel("Initial Angular Velocity (rad/s)")
# plt.title("Region of Attraction and Stable Limit Cycle")

# plt.legend()
# plt.tight_layout()
# plt.savefig("plots/roa_limit_cycle.png", dpi=300)
# plt.close()

# # plot return map
# plt.figure()

# plt.plot(omega_inputs, omega_outputs, label="Return Map")
# plt.plot(omega_inputs, omega_inputs, "--", label="Identity")
# plt.plot(fixed_omega, fixed_omega, "ko", label=f"Fixed Point = {fixed_omega:.2f} rad/s")

# plt.xlabel("Current Post-Impact Angular Velocity (rad/s)")
# plt.ylabel("Next Post-Impact Angular Velocity (rad/s)")
# plt.title("Poincare Return Map")

# plt.legend()
# plt.tight_layout()
# plt.savefig("plots/poincare_return_map.png", dpi=300)
# plt.close()

# Slope Effects

slope_values = np.deg2rad([10, 15, 20, 25, 30])
floquet_slopes = []

for slope in slope_values:

    params = model.generate_params()
    params["downhill_inc"] = slope

    print("Slope:", round(np.rad2deg(slope)),"degrees") 

    theta_values = np.linspace(params["downhill_inc"] - params["alpha"],
        params["downhill_inc"] + params["alpha"], 25)
    omega_values = np.linspace(0.1, 2.0, 25)
    roa = calculate_roa(theta_values, omega_values, params)

    plot_roa(theta_values, omega_values, roa,
        f"Region of Attraction, Slope = {np.rad2deg(slope):.0f} deg", 
        f"roa_slope_{np.rad2deg(slope):.0f}.png")

    omega_inputs = np.linspace(0.1, 2.5, 100)
    omega_outputs = calculate_return_map(omega_inputs, params)
    fixed_omega = find_fixed_point(omega_inputs, omega_outputs)
    floquet = calculate_floquet(fixed_omega, params)
    floquet_slopes.append(floquet)

    if np.isnan(floquet):
        print("No stable rolling fixed point")
    else:
        print("Fixed point:", fixed_omega)
        print("Floquet multiplier:", floquet)

plt.figure()

plt.plot(np.rad2deg(slope_values), floquet_slopes, "o-")

plt.xlabel("Slope (deg)")
plt.ylabel("Floquet Multiplier")
plt.title("Floquet Multiplier vs. Slope")
plt.tight_layout()
plt.savefig("plots/floquet_vs_slope.png", dpi=300)
plt.close()

# Spoke Effects

num_spokes_values = range(6, 13)
floquet_spokes = []

for num_spokes in num_spokes_values:

    params = model.generate_params()

    params["num_spokes"] = num_spokes
    params["alpha"] = np.pi / num_spokes

    print("Number of spokes:", num_spokes)

    theta_values = np.linspace(params["downhill_inc"] - params["alpha"],
        params["downhill_inc"] + params["alpha"], 15)
    omega_values = np.linspace(0.1, 4.0, 15)
    roa = calculate_roa(theta_values, omega_values, params)

    plot_roa(theta_values, omega_values, roa,
        f"Region of Attraction, Spokes = {num_spokes}",
        f"roa_spokes_{num_spokes}.png")

    omega_inputs = np.linspace(0.1, 5.0, 100)
    omega_outputs = calculate_return_map(omega_inputs,params)
    fixed_omega = find_fixed_point(omega_inputs, omega_outputs)

    floquet = calculate_floquet(fixed_omega, params)

    floquet_spokes.append(floquet)

    if np.isnan(floquet):
        print("No stable rolling fixed point")
    else:
        print("Fixed point:", fixed_omega)
        print("Floquet multiplier:", floquet)

plt.figure()

plt.plot(num_spokes_values, floquet_spokes, "o-")

plt.xlabel("Number of Spokes")
plt.ylabel("Floquet Multiplier")
plt.title("Floquet Multiplier vs. Number of Spokes")
plt.tight_layout()
plt.savefig("plots/floquet_vs_spokes.png", dpi=300)
plt.close()

print("simulation complete")
