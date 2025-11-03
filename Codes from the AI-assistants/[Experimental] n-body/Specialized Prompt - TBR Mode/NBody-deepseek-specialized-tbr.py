import numpy as np

# Constants and Initial Conditions
G = 6.67430e-11  # Gravitational constant (m³ kg⁻¹ s⁻²)
dt = 86400        # Time step (1 day in seconds)
num_steps = 36500 # Simulate 100 years (adjustable)
save_interval = 100 # Save data every 100 steps

# Masses (Sun, Jupiter, Saturn, Uranus, Neptune) in kg
masses = np.array([
    1.9885e30, 1.898e27, 5.683e26, 8.681e25, 1.024e26
])

# Semi-major axes (meters)
a = np.array([0.0, 7.785e11, 1.429e12, 2.871e12, 4.495e12])

# Initialize positions (x-axis) and velocities (circular orbit approximation)
positions = np.zeros((5, 3))
positions[:, 0] = a  # All bodies start along the x-axis

velocities = np.zeros_like(positions)
for i in range(1, 5):  # Planets 1-4 (Jovian)
    mu = G * (masses[0] + masses[i])
    r = a[i]
    velocities[i, 1] = np.sqrt(mu / r)  # Circular velocity in y-direction

# Adjust Sun's velocity to balance total momentum
total_momentum = np.sum(masses[1:, np.newaxis] * velocities[1:], axis=0)
velocities[0] = -total_momentum / masses[0]

def compute_accelerations(positions, masses, G):
    """Vectorized acceleration computation using NumPy."""
    n = len(masses)
    dx = positions[np.newaxis, :, :] - positions[:, np.newaxis, :]  # Shape (n, n, 3)
    distances = np.linalg.norm(dx, axis=2)
    np.fill_diagonal(distances, 1.0)  # Avoid division by zero
    m_matrix = masses.reshape(1, n, 1)  # Broadcast masses
    accelerations = np.sum(G * m_matrix * dx / (distances**3)[..., np.newaxis], axis=1)
    return accelerations

# Simulation loop with Velocity Verlet
accelerations = compute_accelerations(positions, masses, G)
history = []

for step in range(num_steps):
    velocities += 0.5 * accelerations * dt
    positions += velocities * dt
    new_accelerations = compute_accelerations(positions, masses, G)
    velocities += 0.5 * new_accelerations * dt
    accelerations = new_accelerations
    
    if step % save_interval == 0:
        history.append(positions.copy())

np.save('orbital_history.npy', np.array(history))  # Save for analysis