def test_initial_condition(initial_state, params):

    state = initial_state.copy()

    dt = 1e-4
    max_steps = 20

    num_impacts = 0

    