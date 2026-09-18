# MAE 5510 Assignment 1 Rimless Wheel
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import time
from models import rimless_wheel as model
from integrators_models import rk4 as integrator
print("Assignment 1 script initiated...")

# Physical Parameters of Rimless Wheel
params = {
        "gravity": 9.81,  # gravity m/s^2)
        "length": 0.5,  # spokes length (m)
        "mass": .2,  # point mass (kg)

    }
N = [6, 9, 12] # number of spokes
alpha = []
for n in N:
    alpha = alpha + [pi / n]
gamma = [np.deg2rad(0), np.deg2rad(2.5), np.deg2rad(5)] # inclination angle (rad)
gamma_case = gamma[2]   # main test case: 5 deg
alpha_case = pi/10   # main test case: N = 10
timestep = 0.001

def simulate_rimless_wheel(initial_state, gamma, alpha, params, model, integrator, timestep, sim_time, n_check): 
    n_timesteps = int(sim_time / timestep) + 1
    final_step = n_timesteps - 1
    time_traj = np.arange(n_timesteps) * timestep 
    state_traj = np.zeros((2, n_timesteps)) 
    state_traj[:, 0] = initial_state
    impact_count = 0
    impact_directions = []   
    impact_velocities = []      
    
    for step, t in enumerate(time_traj[:-1]): # Integration loop
        state_traj[:, step+1] = integrator.integrate(t, state_traj[:, step], params, timestep, model)

        theta = state_traj[0, step+1]
        theta_dot = state_traj[1, step+1]

        rolling_foward = theta_dot>0 and theta>= gamma + alpha # end state of rolling forward
        rolling_backward = theta_dot<0 and theta<= gamma - alpha # end state of rolling backward

        if rolling_foward or rolling_backward:
            impact_count = impact_count + 1 
            if rolling_foward == True:
                theta = theta - 2*alpha
                impact_directions = impact_directions + [1] # append vector     
            elif rolling_backward == True:
                theta = theta + 2*alpha
                impact_directions = impact_directions + [-1] # append vector    
                
            theta_dot = theta_dot*np.cos(2*alpha)
            impact_velocities = impact_velocities + [theta_dot]
            state_traj[0, step+1] = theta
            state_traj[1, step+1] = theta_dot
 
            if impact_count >= n_check and all(d == impact_directions[-1] for d in impact_directions[-n_check:]): # check if the last n_check impacts were all the same direction and then stop early
                final_step = step + 1
                break

    state_traj = state_traj[:, :final_step+1] # trim the state_traj vector    
    return state_traj, impact_count, impact_directions, impact_velocities

def check_if_stable(impact_count, impact_directions, n_check):
    if impact_count == 0:
        return 0  # it never impacted, "true" rest
    recent = impact_directions[-min(n_check, impact_count):] # grab last n_check impacts (or fewer if there are not enough yet)
    if all(d == 1 for d in recent):
        return 2  # last several impacts all forward, aka forward rolling
    elif all(d == -1 for d in recent):
        return 1  # last several impacts all backward, aka backward rolling
    else:
        return 0  # recent impacts still mixed, "rocking" in place, aka rest

def calc_ROA(gamma,alpha):
    # Set-up for ROA
    timestep = 0.001 
    sim_time = 10 # s
    theta_range = np.linspace(gamma - alpha, gamma + alpha, 20)
    theta_dot_range = np.linspace(-3.5, 3.5, 20) # rad/s
    outcome_grid = np.zeros((len(theta_dot_range), len(theta_range)))

    # Run ROA tests
    start_time = time.time()

    for i, td0 in enumerate(theta_dot_range):
        for j, th0 in enumerate(theta_range):
            traj, impact_count, impact_directions, impact_velocities = simulate_rimless_wheel(np.array([th0, td0]), gamma, alpha, params, model, integrator, timestep, sim_time, n_check=15)
            outcome_grid[i,j] = check_if_stable(impact_count, impact_directions, n_check=15)

    elapsed = time.time() - start_time
    print(f"RoA grid took {elapsed:.1f} seconds")

    return theta_range, theta_dot_range, outcome_grid

def calc_floquet(alpha):
    floquet=(np.cos((2*alpha)))**2 # See derivation in writeup
    return floquet

def plot_roa(theta_range,theta_dot_range, outcome_grid):
    plt.figure()
    plt.pcolormesh(theta_range, theta_dot_range, outcome_grid, vmin=0, vmax=2, shading="auto")
    cbar = plt.colorbar(label="0=rest, 1=rolling backward, 2=rolling forward")
    cbar.set_ticks([0, 1, 2])
    plt.xlabel("Angle θ (rad)")
    plt.ylabel("Angular Velocity ω (rad/s)")
    plt.tight_layout()

def plot_state_space(state_traj,initial_state, gamma, alpha):
    plt.figure()
    plt.plot(state_traj[0], state_traj[1], label='Trajectory')
    plt.plot(initial_state[0], initial_state[1], 'o', color="red", markersize=10, label="Initial State")
    plt.xlabel("angle θ (rad)")
    plt.ylabel("angular velocity ω (rad/s)")
    plt.title("Rimless Wheel Phase Portrait")
    plt.tight_layout()
    plt.axvline(gamma - alpha, color="tab:orange", linestyle="--", label=r"$\gamma - \alpha$")
    plt.axvline(gamma + alpha, color="tab:green", linestyle="--", label=r"$\gamma + \alpha$")
    plt.axvline(gamma, color="gray", linestyle=":", label=r"$\gamma$")
    plt.axhline(0, color="black", linewidth=0.5)
    plt.legend()

def find_fixed_point(gamma, alpha, guess_theta_dot, params, model, integrator, timestep):
    # Run the return map for a while and grab the last velocity it settles near
    traj, count, directions, velocities = simulate_rimless_wheel(
        np.array([gamma - alpha, guess_theta_dot]), gamma, alpha, params, model, integrator, timestep, sim_time=30, n_check=100
    )
    return velocities[-1]


# 1.) Sanity checks
sim_time = 10 # [s]
# Check 1, Aggressive Forward Initial Velocity:
initial_state=[0,3]
state_traj, impact_count, impact_directions, impact_velocities = simulate_rimless_wheel(initial_state, gamma_case, alpha_case, params, model, integrator, timestep, sim_time, n_check=15)
plot_state_space(state_traj,initial_state, gamma_case, alpha_case)
plt.savefig("phase_portrait_1.png")
print("Phase Portrait Check 1 complete, Please check folder for updated phase_portrait_1.png")

# Check 2, Aggressive Backward Initial Velocity:
initial_state=[0,-3]
state_traj, impact_count, impact_directions, impact_velocities = simulate_rimless_wheel(initial_state, gamma_case, alpha_case, params, model, integrator, timestep, sim_time, n_check=15)
plot_state_space(state_traj,initial_state, gamma_case, alpha_case)
plt.savefig("phase_portrait_2.png")
print("Phase Portrait Check 2 complete, Please check folder for updated phase_portrait_2.png")

# Check 3, Theta Increase
initial_state=[3,3]
state_traj, impact_count, impact_directions, impact_velocities = simulate_rimless_wheel(initial_state,  gamma_case, alpha_case, params, model, integrator, timestep, sim_time, n_check=15)
plot_state_space(state_traj,initial_state, gamma_case, alpha_case)
plt.savefig("phase_portrait_3.png")
print("Phase Portrait Check 3 complete, Please check folder for updated phase_portrait_3.png")

# Check 4, comes to rest with zero inclination and very little initial velocity
initial_state=[0,3]
state_traj, impact_count, impact_directions, impact_velocities = simulate_rimless_wheel(initial_state,  gamma[0], alpha_case, params, model, integrator, timestep, 40, n_check=100)
plot_state_space(state_traj,initial_state, gamma[0], alpha_case)
plt.savefig("phase_portrait_4.png")
print("Phase Portrait Check 4 complete, Please check folder for updated phase_portrait_4.png")

# 2.) State-space plot showing the RoA of every stable attractor, include fixed points + limit cycles
theta_dot_star = find_fixed_point(gamma_case, alpha_case, 3.0, params, model, integrator, timestep)

limit_cycle_state_traj, lc_impact_count, lc_impact_directions, lc_impact_velocities = simulate_rimless_wheel(
    np.array([gamma_case - alpha_case, theta_dot_star]), gamma_case, alpha_case, params, model, integrator, timestep, sim_time=2, n_check=1
)
rest_state_traj, rest_impact_count, rest_impact_directions, rest_impact_velocities = simulate_rimless_wheel(
    np.array([gamma_case - alpha_case, 0.02 * theta_dot_star]), gamma_case, alpha_case, params, model, integrator, timestep, sim_time=10, n_check=1000
)
theta_range, theta_dot_range, outcome_grid = calc_ROA(gamma_case, alpha_case)
plot_roa(theta_range, theta_dot_range, outcome_grid)
plt.plot(limit_cycle_state_traj[0], limit_cycle_state_traj[1], color="crimson", linewidth=2, label="Rolling forward limit cycle")
plt.plot(rest_state_traj[0], rest_state_traj[1], color="deepskyblue", linewidth=2, label="Fixed point attractor")
plt.legend()
plt.title("Regions of Attraction")
plt.savefig("roa_with_attractors.png")
print("RoA with attractors complete, Please check folder for roa_with_attractors.png")

# 3.) 1D poincare return-map plot, w/ fixed point and the identity line
return_map_state_traj, rm_impact_count, rm_impact_directions, rm_impact_velocities = simulate_rimless_wheel(
    np.array([gamma_case - alpha_case, theta_dot_star - 0.2]), gamma_case, alpha_case, params, model, integrator, timestep, sim_time=50, n_check=10000
)
theta_dot_now = []
theta_dot_next = []
for k in range(len(rm_impact_velocities) - 1):
    theta_dot_now = theta_dot_now + [rm_impact_velocities[k]]
    theta_dot_next = theta_dot_next + [rm_impact_velocities[k+1]]

plot_window = [theta_dot_star - 0.3, theta_dot_star + 0.3]
plt.figure()
plt.plot(theta_dot_now, theta_dot_next, 'o-', color="black", label="Return map")
plt.plot(plot_window, plot_window, '--', color="gray", label="Identity line (y = x)")
plt.xlim(plot_window)
plt.ylim(plot_window)
plt.xlabel(r"$\dot\theta_n$ (rad/s)")
plt.ylabel(r"$\dot\theta_{n+1}$ (rad/s)")
plt.plot(rm_impact_velocities[-1], rm_impact_velocities[-1], 'o', color="red", markersize=10, label="Fixed point")
plt.title("Poincare Return Map")
plt.legend()
plt.tight_layout()
plt.savefig("return_map.png")
print("Poincare Return map complete, Please check folder for return_map.png")
print("Estimated fixed point (last impact velocity):", rm_impact_velocities[-1])

# 4.) Visualization of how gamma and N affects the RoA and local convergence
# Part 1: ROA
# Sweep N, holding gamma fixed at 5 degrees
for i in range(len(N)):
    theta_range, theta_dot_range, outcome_grid = calc_ROA(gamma_case, alpha[i])
    plot_roa(theta_range, theta_dot_range, outcome_grid)
    plt.title(f"RoA, N={N[i]}, gamma=5 deg")
    plt.savefig(f"roa_N{N[i]}.png")
    print(f"RoA for N={N[i]} complete, Please check folder for roa_N{N[i]}.png")

# Sweep gamma, holding N fixed at 10
gamma_deg = [0, 2.5, 5] # for labeling
for i in range(len(gamma)):
    theta_range, theta_dot_range, outcome_grid = calc_ROA(gamma[i], alpha_case)
    plot_roa(theta_range, theta_dot_range, outcome_grid)
    plt.title(f"RoA, N=10, gamma={gamma_deg[i]} deg")
    plt.savefig(f"roa_gamma{gamma_deg[i]}.png")
    print(f"RoA for gamma={gamma_deg[i]} deg complete, Please check folder for roa_gamma{gamma_deg[i]}.png")

# Part 2: Floquet Multiplier
# Visualize the local convergence variation: Floquet multiplier vs N
N = [6, 7, 8, 9, 10, 11, 12] # number of spokes
alpha = []
for n in N:
    alpha = alpha + [pi / n]
gamma = [np.deg2rad(0), np.deg2rad(2.5), np.deg2rad(5)] # inclination angle (rad)


floquet_vs_N = []
for i in range(len(N)):
    floquet_vs_N = floquet_vs_N + [calc_floquet(alpha[i])]

plt.figure()
plt.plot(N, floquet_vs_N, 'o-', color="black")
plt.xlabel("# of Spokes N")
plt.ylabel("Floquet Multiplier")
plt.title("Floquet Multiplier vs Number of Spokes")
plt.tight_layout()
plt.savefig("floquet_vs_N.png")
print("Floquet vs N complete, Please check folder for floquet_vs_N.png")

# Same data, plotted against alpha instead of N
alpha_deg = []
for a in alpha:
    alpha_deg = alpha_deg + [np.rad2deg(a)]

plt.figure()
plt.plot(alpha_deg, floquet_vs_N, 'o-', color="black")
plt.xlabel("Half-Spoke Angle α (deg)")
plt.ylabel("Floquet Multiplier")
plt.title("Floquet Multiplier vs Alpha")
plt.tight_layout()
plt.savefig("floquet_vs_alpha.png")
print("Floquet vs Alpha complete, Please check folder for floquet_vs_alpha.png")

# Floquet multiplier vs gamma, holding N fixed at 10
floquet_vs_gamma = []
for i in range(len(gamma)):
    floquet_vs_gamma = floquet_vs_gamma + [calc_floquet(alpha[1])]

plt.figure()
plt.plot(gamma_deg, floquet_vs_gamma, 'o-', color="black")
plt.xlabel("Incline Angle γ (deg)")
plt.ylabel("Floquet Multiplier")
plt.title("Floquet Multiplier vs Incline angle")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig("floquet_vs_gamma.png")
print("Floquet vs Gamma complete, Please check folder for floquet_vs_gamma.png")



print("Assignment 1 script complete!")