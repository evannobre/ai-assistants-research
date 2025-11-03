import numpy as np

# Define gravitational constant
G = 6.67430e-11  # m³/kg/s²

# Define planetary masses (Sun, Jupiter, Saturn, Uranus, Neptune) in kg
masses = np.array([1.989e30, 1.898e27, 5.683e26, 8.681e25, 1.024e26])

# Initial positions and velocities (example values in meters and meters per second)
positions = np.array([
    [0, 0, 0],        # Sun
    [7.78e11, 0, 0],  # Jupiter
    [1.43e12, 0, 0],  # Saturn
    [2.87e12, 0, 0],  # Uranus
    [4.50e12, 0, 0]   # Neptune
], dtype=np.float64)

velocities = np.array([
    [0, 0, 0],        # Sun
    [0, 1.3e4, 0],    # Jupiter
    [0, 9.7e3, 0],    # Saturn
    [0, 6.8e3, 0],    # Uranus
    [0, 5.4e3, 0]     # Neptune
], dtype=np.float64)

# Time step (1 day in seconds)
dt = 86400  

def compute_accelerations(positions, masses):
    """ Compute gravitational acceleration for each body """
    n = len(masses)
    accelerations = np.zeros_like(positions)
    for i in range(n):
        for j in range(n):
            if i != j:
                r_vec = positions[j] - positions[i]
                r_mag = np.linalg.norm(r_vec)
                accelerations[i] += G * masses[j] * r_vec / r_mag**3
    return accelerations

# Simulating for 365 days
for _ in range(365):
    accelerations = compute_accelerations(positions, masses)
    velocities += accelerations * dt
    positions += velocities * dt

print("Final positions:\n", positions)
