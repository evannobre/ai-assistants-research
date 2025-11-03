import numpy as np

G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
DAY = 86400      # Seconds in a day
YEAR = 365.25 * DAY

# Masses in kg
masses = np.array([
    1.989e30,     # Sun
    1.898e27,     # Jupiter
    5.683e26,     # Saturn
    8.681e25,     # Uranus
    1.024e26      # Neptune
])

# Initial positions (m) and velocities (m/s)
# Approximate values as of J2000 epoch
positions = np.array([
    [0.0, 0.0, 0.0],                       # Sun
    [7.785e11, 0.0, 0.0],                 # Jupiter
    [1.433e12, 0.0, 0.0],                 # Saturn
    [2.877e12, 0.0, 0.0],                 # Uranus
    [4.503e12, 0.0, 0.0]                  # Neptune
], dtype=np.float64)

velocities = np.array([
    [0.0, 0.0, 0.0],                       # Sun
    [0.0, 1.307e4, 0.0],                  # Jupiter
    [0.0, 9.69e3, 0.0],                   # Saturn
    [0.0, 6.8e3, 0.0],                    # Uranus
    [0.0, 5.43e3, 0.0]                    # Neptune
], dtype=np.float64)

def compute_accelerations(positions, masses):
    N = len(masses)
    accelerations = np.zeros_like(positions)
    for i in range(N):
        for j in range(N):
            if i != j:
                diff = positions[j] - positions[i]
                r = np.linalg.norm(diff)
                if r > 0:
                    accelerations[i] += G * masses[j] * diff / r**3
    return accelerations

def velocity_verlet(positions, velocities, masses, dt, steps):
    pos_history = np.zeros((steps, len(masses), 3), dtype=np.float64)
    acc = compute_accelerations(positions, masses)

    for step in range(steps):
        # Store current state
        pos_history[step] = positions

        # Update positions
        positions += velocities * dt + 0.5 * acc * dt**2

        # Compute new accelerations
        new_acc = compute_accelerations(positions, masses)

        # Update velocities
        velocities += 0.5 * (acc + new_acc) * dt

        # Prepare for next step
        acc = new_acc

    return pos_history

# Simulation parameters
dt = 5 * DAY     # 5 days per step
total_years = 100
steps = int((total_years * YEAR) / dt)

print(f"Running simulation for {total_years} years ({steps} steps)...")

trajectory = velocity_verlet(positions, velocities, masses, dt, steps)

# Save final output (last snapshot)
np.save("jovian_simulation.npy", trajectory)

print("Simulation complete. Output saved to 'jovian_simulation.npy'.")
