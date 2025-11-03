import numpy as np

def calculate_accelerations(masses, positions, G):
    N = positions.shape[0]
    accelerations = np.zeros_like(positions)
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            
            # Vector from body i to body j
            r_ij = positions[j] - positions[i] # This is (r_j - r_i)
            
            # Distance squared + softening factor (to avoid division by zero if bodies coincide)
            # Softening is typically small, e.g., (epsilon)^2
            # For planetary scales, actual collisions are rare, but good for numerical stability.
            # Let's assume distinct positions for simplicity here, but add epsilon if needed.
            dist_sq = np.sum(r_ij**2)
            dist = np.sqrt(dist_sq)
            
            if dist == 0: # Avoid division by zero, though unlikely with real initial data
                continue

            # Force magnitude (scalar part of F_i formula for one j) / m_i
            force_scalar_over_m_i = G * masses[j] / (dist_sq * dist) # This is G * m_j / |r_j - r_i|^3
            
            # Acceleration contribution from body j onto body i
            accelerations[i] += force_scalar_over_m_i * r_ij
            
    return accelerations

import numpy as np

def calculate_accelerations_optimized(masses, positions, G, epsilon_sq=1e-12):
    N = positions.shape[0]
    accelerations = np.zeros_like(positions)

    # Calculate all pairwise position differences
    # r_ji = positions[j] - positions[i]
    # Using broadcasting:
    # positions[:, np.newaxis, :] gives shape (N, 1, 3)
    # positions[np.newaxis, :, :] gives shape (1, N, 3)
    # delta_pos will have shape (N, N, 3) where delta_pos[i, j, :] = pos[j] - pos[i]
    delta_pos = positions[np.newaxis, :, :] - positions[:, np.newaxis, :]

    # Calculate squared distances (N, N)
    # Add epsilon_sq for softening and to avoid division by zero if two bodies are at the same exact spot.
    dist_sq = np.sum(delta_pos**2, axis=2) + epsilon_sq 
    inv_dist_cubed = dist_sq**(-1.5) # 1 / (distance^3)

    # Calculate accelerations: G * m_j / dist_ij^3 * (r_j - r_i)
    # masses[np.newaxis, :, np.newaxis] gives shape (1, N, 1) to align for broadcasting
    # The result of G * masses... will be (1, N, 1)
    # delta_pos is (N, N, 3)
    # The term G * masses[j] * inv_dist_cubed[i,j] is broadcasted
    accel_contributions = G * masses[np.newaxis, :, np.newaxis] * inv_dist_cubed[:, :, np.newaxis] * delta_pos

    # Sum contributions for each body i from all other bodies j
    # We need to ensure we don't sum the contribution of a body to itself (which would be NaN or Inf due to dist=0 if not for epsilon)
    # The diagonal of dist_sq will be epsilon_sq, so inv_dist_cubed will be large but finite.
    # However, delta_pos[i,i,:] is zero, so accel_contributions[i,i,:] will be zero.
    accelerations = np.sum(accel_contributions, axis=1)
    
    return accelerations

# At the beginning of the simulation loop, after getting initial positions and velocities:
# current_accelerations = calculate_accelerations_optimized(masses, current_positions, G)

# Inside the simulation loop for one time step dt:
def integration_step_verlet(positions, velocities, accelerations, masses, G, dt):
    # 1. Update positions
    new_positions = positions + velocities * dt + 0.5 * accelerations * dt**2
    
    # 2. Calculate intermediate velocities (v_temp for v(t + dt/2) concept)
    #    Here, it's more like v_almost_final = v(t) + a(t) * dt/2
    velocities_half_step = velocities + 0.5 * accelerations * dt
    
    # 3. Calculate new accelerations based on new positions
    new_accelerations = calculate_accelerations_optimized(masses, new_positions, G)
    
    # 4. Update final velocities for the step
    new_velocities = velocities_half_step + 0.5 * new_accelerations * dt
    
    return new_positions, new_velocities, new_accelerations

# --- Initial Setup ---
# Gravitational constant
G_val = 6.67430e-11 # N m^2 / kg^2 (adjust units if using astronomical units)

# Body masses (kg) - Example (use actual values)
# Sun, Jupiter, Saturn, Uranus, Neptune
mass_values = np.array([1.989e30, 1.898e27, 5.683e26, 8.681e25, 1.024e25]) 

# Initial positions (meters, from a common origin like Solar System Barycenter or Sun)
# Ensure you get these from an ephemeris service like JPL HORIZONS for a specific date.
# Example structure:
# positions_initial = np.array([
#     [x_sun, y_sun, z_sun],      # Sun
#     [x_jup, y_jup, z_jup],      # Jupiter
#     [x_sat, y_sat, z_sat],      # Saturn
#     [x_ura, y_ura, z_ura],      # Uranus
#     [x_nep, y_nep, z_nep]       # Neptune
# ]) # Shape (5, 3)

# Initial velocities (m/s)
# Example structure:
# velocities_initial = np.array([
#     [vx_sun, vy_sun, vz_sun],   # Sun
#     [vx_jup, vy_jup, vz_jup],   # Jupiter
#     ...
# ]) # Shape (5, 3)

# --- Simulation Parameters ---
dt_seconds = 3600 * 24  # Time step (e.g., 1 day in seconds)
total_time_seconds = 365.25 * 24 * 3600 * 10 # Simulate for 10 years
num_steps = int(total_time_seconds / dt_seconds)

# --- Initialize State ---
current_positions = np.copy(positions_initial) 
current_velocities = np.copy(velocities_initial)
current_accelerations = calculate_accelerations_optimized(mass_values, current_positions, G_val)

# --- Data Logging (Optional but recommended) ---
# Store trajectory data. For N=5, this is small.
trajectory_positions = np.zeros((num_steps + 1, current_positions.shape[0], current_positions.shape[1]))
trajectory_positions[0] = current_positions

# --- Simulation Loop ---
for step in range(num_steps):
    current_positions, current_velocities, current_accelerations = \
        integration_step_verlet(current_positions, current_velocities, current_accelerations, 
                                mass_values, G_val, dt_seconds)
    
    trajectory_positions[step + 1] = current_positions
    
    if (step + 1) % (num_steps // 100) == 0: # Print progress
        print(f"Step {step+1}/{num_steps} completed. Sim Time: {(step+1)*dt_seconds / (365.25*24*3600):.2f} years")

# --- Post-Processing / Visualization ---
# Use trajectory_positions for plotting orbits (e.g., with Matplotlib)
# Check for energy conservation, angular momentum conservation (good sanity checks)