import numpy as np
# Masses in kg
masses = np.array([
    1.9885e30,  # Sun
    1.89819e27, # Jupiter
    5.6834e26,  # Saturn
    8.6813e25,  # Uranus
    1.02413e26  # Neptune
])
N_BODIES = len(masses)

# Example (replace with actual data for a specific epoch)
# Ensure these are in a consistent reference frame (e.g., ICRF, heliocentric)
# initial_positions_m = np.array([[...], ..., [N_BODIES_coords]]) # (N_BODIES, 3)
# initial_velocities_m_s = np.array([[...], ..., [N_BODIES_velocities]]) # (N_BODIES, 3)

# For a simple start, you might place the Sun at origin if using a naive heliocentric frame
# but it's better to get actual barycentric coordinates or let the Sun move too.
# If initial_positions are from JPL HORIZONS, they are typically barycentric for the Solar System.

DT_S = 3600.0 * 24 # Time step in seconds (1 day)
# TOTAL_SIM_YEARS = 100
# TOTAL_SIM_S = TOTAL_SIM_YEARS * 365.25 * 24 * 3600
# NUM_STEPS = int(TOTAL_SIM_S / DT_S)
SOFTENING_FACTOR_SQ = (1.0e7)**2 # (m^2), softening factor squared

# Assuming initial_positions_m is loaded
# positions_history = np.zeros((NUM_STEPS + 1, N_BODIES, 3))
# positions_history[0, :, :] = initial_positions_m.copy()
# current_positions = initial_positions_m.copy()
# current_velocities = initial_velocities_m_s.copy()

def calculate_accelerations(positions, masses_kg, G_const, softening_sq):
    """
    Calculates gravitational accelerations for N bodies.
    - positions: (N, 3) NumPy array of current positions (meters).
    - masses_kg: (N,) NumPy array of masses (kg).
    - G_const: Gravitational constant.
    - softening_sq: Softening factor squared (m^2) to avoid singularities.
    Returns: (N, 3) NumPy array of accelerations (m/s^2).
    """
    n = positions.shape[0]
    accelerations = np.zeros_like(positions) # Shape (N, 3)

    for i in range(n):
        # Calculate vector differences: r_j - r_i for all j
        # This gives vectors from body i to all other bodies j (and to itself)
        r_ij_all = positions - positions[i, :] # Broadcasting: (N,3) - (1,3) -> (N,3)

        # Calculate squared distances: |r_j - r_i|^2
        dist_sq = np.sum(r_ij_all**2, axis=1) # Shape (N,)

        for j in range(n):
            if i == j:
                continue # No self-gravity

            # Denominator for force calculation: (distance^2 + epsilon^2)^(3/2)
            inv_dist_cubed_val = (dist_sq[j] + softening_sq)**(-1.5)
            
            # Acceleration on body i due to body j: G * m_j * (r_j - r_i) / |r_j - r_i|^3
            # r_ij_all[j,:] is the vector from body i to body j
            accelerations[i, :] += G_const * masses_kg[j] * r_ij_all[j,:] * inv_dist_cubed_val
            
    return accelerations

# Inside the main simulation loop, for each time step:

# Let current_positions and current_velocities be the state at time t

# k1: derivatives at the beginning of the step
# k1_p is delta_pos if velocity were constant for dt
# k1_v is delta_vel if acceleration were constant for dt
k1_v = calculate_accelerations(current_positions, masses, G, SOFTENING_FACTOR_SQ) * DT_S
k1_p = current_velocities * DT_S

# k2: derivatives at midpoint, using k1
pos_temp_k2 = current_positions + k1_p / 2.0
vel_temp_k2 = current_velocities + k1_v / 2.0
k2_v = calculate_accelerations(pos_temp_k2, masses, G, SOFTENING_FACTOR_SQ) * DT_S
k2_p = vel_temp_k2 * DT_S

# k3: derivatives at midpoint, using k2
pos_temp_k3 = current_positions + k2_p / 2.0
vel_temp_k3 = current_velocities + k2_v / 2.0
k3_v = calculate_accelerations(pos_temp_k3, masses, G, SOFTENING_FACTOR_SQ) * DT_S
k3_p = vel_temp_k3 * DT_S

# k4: derivatives at the end of the step, using k3
pos_temp_k4 = current_positions + k3_p
vel_temp_k4 = current_velocities + k3_v
k4_v = calculate_accelerations(pos_temp_k4, masses, G, SOFTENING_FACTOR_SQ) * DT_S
k4_p = vel_temp_k4 * DT_S

# Update positions and velocities
current_velocities += (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6.0
current_positions += (k1_p + 2*k2_p + 2*k3_p + k4_p) / 6.0

# (Initialization code: G, masses, initial_positions_m, initial_velocities_m_s,
#  DT_S, NUM_STEPS, SOFTENING_FACTOR_SQ, positions_history,
#  current_positions, current_velocities - as defined before)

print("Starting N-body simulation...")
for step in range(NUM_STEPS):
    # (RK4 integration steps as described in Section 3)
    # k1_v = ...
    # ...
    # current_positions += ...
    # current_velocities += ...

    # Store results
    positions_history[step + 1, :, :] = current_positions

    # Progress indicator (optional, good for long simulations)
    if (step + 1) % (NUM_STEPS // 100_or_less_frequent) == 0: # e.g., every 1% or every 1000 steps
        elapsed_sim_time_years = (step + 1) * DT_S / (365.25 * 24 * 3600)
        print(f"Step {step+1}/{NUM_STEPS} completed. Simulated time: {elapsed_sim_time_years:.2f} years.")
        # Optional: Periodic saving to disk to prevent data loss and manage memory if
        # positions_history becomes too large to hold entirely in RAM before one final save.
        # np.save(f"positions_checkpoint_step_{step+1}.npy", positions_history[:step+2, :, :])

print("Simulation finished.")

np.save("jovian_orbit_simulation_positions.npy", positions_history)
# If velocities were also stored:
# np.save("jovian_orbit_simulation_velocities.npy", velocities_history)