import numpy as np

import integrators
from models import pendulum


def total_energy(state, params):
    kinetic_energy, potential_energy = pendulum.calculate_energy(state, params)
    return kinetic_energy + potential_energy


def test_energy_conserved_with_no_damping_or_torque():
    params = pendulum.generate_params()
    params["damping_coeff"] = 0.0
    params["torque"] = 0.0

    state = np.array([0.5, 0.0])
    initial_energy = total_energy(state, params)

    timestep = 0.01
    time = 0.0
    for step in range(100):
        state = integrators.rk4(pendulum.dynamics, time, state, timestep, params)
        time = time + timestep

    final_energy = total_energy(state, params)

    assert np.isclose(final_energy, initial_energy, atol=1e-2)


def test_damping_dissipates_energy():
    params = pendulum.generate_params()
    params["damping_coeff"] = 0.5
    params["torque"] = 0.0

    state = np.array([0.5, 0.0])
    initial_energy = total_energy(state, params)

    timestep = 0.01
    time = 0.0
    for step in range(100):
        state = integrators.rk4(pendulum.dynamics, time, state, timestep, params)
        time = time + timestep

    final_energy = total_energy(state, params)

    assert final_energy < initial_energy


def test_torque_injects_energy():
    params = pendulum.generate_params()
    params["damping_coeff"] = 0.0
    params["torque"] = 1.0

    state = np.array([0.0, 0.0])
    initial_energy = total_energy(state, params)

    timestep = 0.01
    time = 0.0
    for step in range(100):
        state = integrators.rk4(pendulum.dynamics, time, state, timestep, params)
        time = time + timestep

    final_energy = total_energy(state, params)

    assert final_energy > initial_energy
