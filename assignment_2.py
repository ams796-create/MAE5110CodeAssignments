from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from models import inverted_pendulum_walker as model
from integrators import rk4 as integrator

# Fixed controls for this visualization example.
params = {
    "gravity": 9.81,  # m/s^2
    "length": 1.0,  # m
    "mass": 1.0,  # kg
    "incline": 0.06,  # rad
    "angle_of_attack": np.pi / 8,  # rad
    "ankle_torque": 0.0,  # N m
}

initial_state = np.array([0.0, 3.0])
timestep = 1e-4
sim_time = 3.0
desired_number_of_steps = 3

n_timesteps = round(sim_time / timestep) + 1
time_traj = np.arange(n_timesteps) * timestep
state_traj = np.zeros((2, n_timesteps))
state_traj[:, 0] = initial_state
completed_steps = 0

# Simulation loop. Replace this Euler step with your own integrator as needed.
for step, t in enumerate(time_traj[:-1]):
    state = state_traj[:, step]
    next_state = state + timestep * model.dynamics(t, state, params)

    if model.event_guard(state, next_state, params):
        next_state = model.event_dynamics(next_state, params)
        completed_steps += 1

    state_traj[:, step + 1] = next_state
    if completed_steps == desired_number_of_steps:
        break

time_traj = time_traj[: step + 2]
state_traj = state_traj[:, : step + 2]

fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")


def draw_frame(index):
    # The massless swing leg is repositioned instantaneously at each impact.
    model.visualize(state_traj[:, index], params, ax=ax)
    ax.set_title(f"t = {time_traj[index]:.2f} s")


# Simulate at a small timestep, but render only 25 frames per second.
fps = 25
frame_stride = round(1 / (fps * timestep))
frame_indices = list(range(0, time_traj.size, frame_stride))
if frame_indices[-1] != time_traj.size - 1:
    frame_indices.append(time_traj.size - 1)

animation = FuncAnimation(
    fig, draw_frame, frames=frame_indices, interval=1000 / fps, repeat=False
)
output = Path("output/assignment_2")
output.mkdir(parents=True, exist_ok=True)
animation.save(output / "walker.gif", writer=PillowWriter(fps=fps))

# To save an MP4 instead, install FFmpeg and use:
# animation.save(output / "walker.mp4", writer="ffmpeg", fps=fps)
print(f"Saved {output / 'walker.gif'} ({completed_steps} footstrikes).")
plt.show()

def feedback_linearization(state,params,damping):
    gravity = params["gravity"]
    length = params["length"]
    mass = params["mass"]

    angle = state[0]
    angular_velocity = state[1]

    ankle_torque = (-2 * mass * gravity * length
        * np.sin(angle) - damping * angular_velocity)

    min_torque = -0.1 * mass * gravity * length
    max_torque = 0.05 * mass * gravity * length

    ankle_torque = np.clip(ankle_torque, min_torque, max_torque)

    return ankle_torque

def test_feedback_controller(initial_state, params, damping):
    params["ankle_torque"] = 0.0

    timestep = 1e-3
    sim_time = 5.0

    state = initial_state.copy()

    angle_stable_tolerance = 0.01
    angular_velocity_stable_tolerance = 0.01

    stable_time = 0.1
    stable_steps_required = round(stable_time / timestep)
    stable_steps = 0

    for t in np.arange(0, sim_time, timestep):

        params["ankle_torque"] = feedback_linearization(state, params, damping)

        state = state + timestep * model.dynamics(t, state, params)

        if (abs(state[0]) < angle_stable_tolerance and
                abs(state[1]) < angular_velocity_stable_tolerance):
            stable_steps += 1
        else:
            stable_steps = 0

        if stable_steps >= stable_steps_required:
            return True

    return False

def calculate_roa(params,damping):

    angle_values = np.linspace(-0.15, 0.15, 30)
    angular_velocity_values = np.linspace(-0.75, 0.75, 30)

    roa = np.zeros((len(angular_velocity_values), len(angle_values)))

    for i, angular_velocity in enumerate(angular_velocity_values):
        for j, angle in enumerate(angle_values):

            initial_state = np.array([angle, angular_velocity])

            if test_feedback_controller(initial_state, params, damping):
                roa[i, j] = 1

    return angle_values, angular_velocity_values, roa


def roa_event_guard(state, angle_values, angular_velocity_values, roa):
    angle = state[0]
    angular_velocity = state[1]

    if (angle < angle_values[0] or angle > angle_values[-1] or
            angular_velocity < angular_velocity_values[0] or
            angular_velocity > angular_velocity_values[-1]):
        return False

    angle_index = np.argmin(np.abs(angle_values - angle))
    velocity_index = np.argmin(np.abs(angular_velocity_values - angular_velocity))

    return roa[velocity_index, angle_index] == 1


def detect_poincare_section(previous_state, current_state):
    previous_angle = previous_state[0]
    current_angle = current_state[0]

    return previous_angle < 0 <= current_angle


def one_step_return(initial_angular_velocity, angle_of_attack, params):
    params["angle_of_attack"] = angle_of_attack
    params["ankle_torque"] = 0.0

    state = np.array([0.0, initial_angular_velocity])

    dt = 1e-4
    sim_time = 3.0

    impact_occurred = False

    for t in np.arange(0, sim_time, dt):
        previous_state = state.copy()

        current_state = integrator.integrate(model.dynamics, t, 
                            previous_state, dt, params)

        if model.event_guard(previous_state, current_state, params):
            current_state = model.event_dynamics(current_state, params)
            impact_occurred = True

        if impact_occurred and detect_poincare_section(previous_state, current_state):
            return current_state[1]

        state = current_state

    return None


def create_lookup_table(num_angular_velocities, params,
                         roa_angles, roa_angular_velocities, roa):

    max_angular_velocity = np.sqrt((2 * params["gravity"]) / params["length"])

    angular_velocity_sweep = np.linspace(0.0, max_angular_velocity, num_angular_velocities)

    num_angles = 20
    max_angle = np.pi / 7
    min_angle = np.pi / 8
    angle_sweep = np.linspace(min_angle, max_angle, num_angles)

    return_map = np.zeros((len(angular_velocity_sweep), len(angle_sweep)))

    for i, angular_velocity in enumerate(angular_velocity_sweep):
        for j, angle_of_attack in enumerate(angle_sweep):

            next_velocity = one_step_return(angular_velocity, angle_of_attack, params)

            if next_velocity is not None:
                return_map[i, j] = next_velocity
            else:
                return_map[i, j] = np.nan

    steps = np.zeros(len(angular_velocity_sweep))

    best_angle = np.full(len(angular_velocity_sweep), np.nan)

    for i in range(len(angular_velocity_sweep)):
        for j in range(len(angle_sweep)):

            next_velocity = return_map[i, j]

            if np.isnan(next_velocity):
                continue

            next_state = np.array([0.0, next_velocity])

            if roa_event_guard(next_state, roa_angles, roa_angular_velocities, roa):
                steps[i] = 1
                best_angle[i] = angle_sweep[j]
                break

    current_step = 2
    max_grid_error = 0.0

    while True:
        found_new_state = False

        for i in range(len(angular_velocity_sweep)):

            if steps[i] != 0:
                continue

            for j in range(len(angle_sweep)):

                next_velocity = return_map[i, j]

                if np.isnan(next_velocity):
                    continue

                closest_index = np.argmin(
                    np.abs(angular_velocity_sweep - next_velocity))

                grid_error = abs(next_velocity - angular_velocity_sweep[closest_index])

                max_grid_error = max(max_grid_error, grid_error)

                grid_spacing = angular_velocity_sweep[1] - angular_velocity_sweep[0]

                if (grid_error <= grid_spacing / 2 and
                    steps[closest_index] == current_step - 1):

                    steps[i] = current_step
                    best_angle[i] = angle_sweep[j]
                    found_new_state = True
                    break

        if not found_new_state:
            break

        current_step += 1

    transitions = []

    for i in range(1, len(steps)):
        if steps[i] != steps[i - 1]:
            transitions.append((int(steps[i - 1]), int(steps[i]), 
                                angular_velocity_sweep[i]))

    return angular_velocity_sweep, steps, best_angle

def simulate_lookup_controller(initial_angular_velocity, params,
                               angular_velocity_sweep, best_angle,
                               roa_angles, roa_angular_velocities, roa):

    dt = 1e-4
    sim_time = 10.0

    state = np.array([0.0, initial_angular_velocity])

    state_history = [state.copy()]
    impact_occurred = False

    closest_index = np.argmin(np.abs(angular_velocity_sweep - state[1]))
    params["angle_of_attack"] = best_angle[closest_index]
    params["ankle_torque"] = 0.0

    for t in np.arange(0, sim_time, dt):

        previous_state = state.copy()

        state = integrator.integrate(model.dynamics, t, state, dt, params)

        if model.event_guard(previous_state, state, params):
            state = model.event_dynamics(state, params)
            impact_occurred = True

        if roa_event_guard(state, roa_angles, roa_angular_velocities, roa):
            print("Reached RoA")
            break

        if impact_occurred and detect_poincare_section(previous_state, state):
            print("Poincare crossing:", state[1])

            closest_index = np.argmin(np.abs(angular_velocity_sweep - state[1]))

            params["angle_of_attack"] = best_angle[closest_index]
            impact_occurred = False

        state_history.append(state.copy())

    return np.array(state_history)


# saved_roa = np.load("output/assignment_2/roa.npz")

# roa_angles = saved_roa["angle_values"]
# roa_angular_velocities = saved_roa["velocity_values"]
# roa = saved_roa["roa"]

# grid_resolutions = [10, 20, 25, 30, 35, 40, 45]

# for resolution in grid_resolutions:

#     steps, max_grid_error, transitions = create_lookup_table(resolution,
#         params, roa_angles, roa_angular_velocities, roa)

#     print("\nGrid resolution:", resolution)
#     print("Maximum grid error:", max_grid_error)
#     print("Maximum steps:", int(np.max(steps)))

#     for old_step, new_step, velocity in transitions:
#         print(old_step, "to", new_step, "at", velocity, "rad/s")

saved_roa = np.load("output/assignment_2/roa.npz")

roa_angles = saved_roa["angle_values"]
roa_angular_velocities = saved_roa["velocity_values"]
roa = saved_roa["roa"]

saved_lookup = np.load("output/assignment_2/lookup_table_80.npz")

angular_velocity_sweep = saved_lookup["angular_velocity_sweep"]
steps = saved_lookup["steps"]
best_angle = saved_lookup["best_angle"]

# RoA plot
plt.figure()

plt.imshow(roa, origin="lower", extent=[roa_angles[0], roa_angles[-1], 
            roa_angular_velocities[0], roa_angular_velocities[-1]], aspect="auto")

plt.xlabel("Angle (rad)")
plt.ylabel("Angular Velocity (rad/s)")
plt.title("Region of Attraction")

plt.savefig("output/assignment_2/RoA.png", dpi=300,
    bbox_inches="tight")

plt.show()


# three step trajectory plot
three_step_indices = np.where(steps == 3)[0]
initial_index = three_step_indices[0]

initial_angular_velocity = angular_velocity_sweep[initial_index]

state_history = simulate_lookup_controller(initial_angular_velocity, params,
                            angular_velocity_sweep, best_angle, roa_angles, 
                            roa_angular_velocities, roa)

plt.figure()

plt.plot(state_history[:, 0],state_history[:, 1])

plt.xlabel("Angle (rad)")
plt.ylabel("Angular Velocity (rad/s)")
plt.title("Lookup Controller Trajectory")

plt.grid()

plt.savefig("output/assignment_2/trajectory.png", dpi=300, bbox_inches="tight")

plt.show()


# steps until standstill
steps_plot = steps.copy()
steps_plot[steps_plot == 0] = np.nan

plt.figure()

plt.plot(angular_velocity_sweep,steps_plot,"o-")

plt.xlabel("Initial Angular Velocity (rad/s)")
plt.ylabel("Steps to Reach RoA")
plt.title("Steps to Reach Standstill")

plt.yticks([1, 2, 3, 4])
plt.grid()

plt.savefig("output/assignment_2/steps_to_standstill.png", dpi=300,
    bbox_inches="tight")

plt.show()