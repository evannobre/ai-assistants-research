import numpy as np

# --- Constants ---
G = 6.67430e-11  # m^3 kg^-1 s^-2
# Example: 1 day in seconds
dt = 3600.0 * 24.0 # Time step in seconds
# Example: 20 Earth years
total_time = 20 * 365.25 * 24 * 3600 # Total simulation time in seconds
num_steps = int(total_time / dt)

# --- Initial Conditions (Placeholder values - replace with actual data) ---
# Masses (kg) - Sun, Jupiter, Saturn, Uranus, Neptune
masses = np.array([
    1.989e30,  # Sun
    1.898e27,  # Jupiter
    5.683e26,  # Saturn
    8.681e25,  # Uranus
    1.024e26   # Neptune
])
num_bodies = len(masses)

# Positions (m) - [x, y, z] for each body relative to the Solar System Barycenter (SSB) or Sun
# These need to be obtained from an ephemeris service like JPL Horizons for a specific date.
# Using placeholder zeros for structure.
positions = np.zeros((num_bodies, 3))
# Example for Jupiter (approximate distance from Sun in AU, converted to meters, on x-axis)
# positions[1] = [5.2 * 1.496e11, 0, 0]

# Velocities (m/s) - [vx, vy, vz] for each body
# These also need to be obtained from an ephemeris service.
# Using placeholder zeros for structure.
velocities = np.zeros((num_bodies, 3))
# Example for Jupiter (approximate orbital speed, on y-axis)
# velocities[1] = [0, 13.06e3, 0]

# Accelerations (m/s^2)
accelerations = np.zeros((num_bodies, 3))

# For storing trajectory (optional)
trajectory = np.zeros((num_steps, num_bodies, 3))

def calculate_accelerations(current_positions, current_masses):
    n = current_positions.shape[0]
    accel = np.zeros_like(current_positions) # Initialize accelerations to zero
    for i in range(n):
        for j in range(n):
            if i == j:
                continue # No self-gravity

            # Vector from body i to body j
            r_vec = current_positions[j] - current_positions[i]

            # Distance squared (add small epsilon to avoid division by zero if bodies coincide)
            dist_sq = np.sum(r_vec**2)
            epsilon = 1e-9 # Softening factor to prevent extreme forces at close encounters
            dist_cubed = (dist_sq + epsilon)**1.5

            # Gravitational force contribution from body j on body i
            accel[i] += G * current_masses[j] * r_vec / dist_cubed
    return accel.

def calculate_accelerations_vectorized(current_positions, current_masses):
    n = current_positions.shape[0]
    accel = np.zeros_like(current_positions)

    # Expand dimensions for broadcasting
    # pos_i will be (N, 1, 3), pos_j will be (1, N, 3)
    pos_i = current_positions[:, np.newaxis, :]
    pos_j = current_positions[np.newaxis, :, :]

    # Differences in positions (N, N, 3)
    # r_vec[i, j, :] is the vector from body i to body j
    r_vec = pos_j - pos_i

    # Distances squared (N, N)
    # dist_sq[i, j] is the squared distance between body i and body j
    dist_sq = np.sum(r_vec**2, axis=2)

    # Avoid division by zero where i == j by setting those distances to infinity (or a large number)
    # or handle by masking later. A small softening factor is more common.
    epsilon_sq = 1e-18 # Softening factor squared (epsilon is distance)
    inv_dist_cubed = (dist_sq + epsilon_sq)**(-1.5)

    # Set diagonal elements to zero to avoid self-interaction in the sum
    # (where dist_sq is zero or epsilon_sq for i==j)
    np.fill_diagonal(inv_dist_cubed, 0.)

    # Calculate accelerations: G * m_j * r_vec_ij / |r_ij|^3
    # masses_j will be (1, N, 1) to broadcast correctly with r_vec (N, N, 3)
    masses_j_broadcast = current_masses[np.newaxis, :, np.newaxis]

    # Sum over j for each i
    # accel_contributions is (N, N, 3)
    accel_contributions = G * masses_j_broadcast * r_vec * inv_dist_cubed[:, :, np.newaxis]
    accel = np.sum(accel_contributions, axis=1) # Sum over the j-th body

    return accel.

# --- Main Simulation Loop ---

# Initial acceleration calculation
accelerations = calculate_accelerations_vectorized(positions, masses)

print("Starting simulation...")
for step in range(num_steps):
    # (1) Update velocities by a half step (using current accelerations)
    velocities += accelerations * (dt / 2.0)

    # (2) Update positions by a full step (using updated half-step velocities)
    positions += velocities * dt

    # (3) Calculate new accelerations based on new positions
    accelerations = calculate_accelerations_vectorized(positions, masses)

    # (4) Update velocities by another half step (using new accelerations)
    velocities += accelerations * (dt / 2.0)

    # Store results (optional)
    if step % 100 == 0: # Store every 100 steps, for example
        trajectory[step // 100] = positions
        # Simple progress update
        # print(f"Step {step}/{num_steps}, Time: {step*dt/(3600*24):.1f} days")
        # print(f"Jupiter position: {positions[1]/1.496e11} AU") # Position of Jupiter in AU

    if step % (num_steps // 100) == 0 and step > 0 : # Print progress roughly 100 times
        print(f"Progress: {100 * step / num_steps:.1f}%")

print("Simulation finished.")

# --- Post-processing / Visualization (Example) ---
# (Using matplotlib - not strictly "native" but standard for plotting in Python)
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# fig = plt.figure(figsize=(10, 10))
# ax = fig.add_subplot(111, projection='3d')

# colors = ['yellow', 'orange', 'lightgoldenrodyellow', 'lightblue', 'darkblue']
# for i in range(num_bodies):
#     # Plot only stored trajectory points
#     valid_trajectory_points = trajectory[:num_steps//100, i, :]
#     ax.plot(valid_trajectory_points[:, 0], valid_trajectory_points[:, 1], valid_trajectory_points[:, 2],
#             label=f'Body {i}', color=colors[i])

# ax.set_xlabel("X (m)")
# ax.set_ylabel("Y (m)")
# ax.set_zlabel("Z (m)")
# ax.set_title("N-Body Simulation of Jovian Planets and Sun")
# # Optional: Set equal aspect ratio for a more realistic orbit shape, but might make visualization difficult
# # ax.set_aspect('equal', adjustable='box')
# ax.legend()
# plt.show()