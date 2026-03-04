import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Constants
G = 6.67430e-11  # m^3 kg^-1 s^-2
DAYS_PER_YEAR = 365.2422
SECONDS_PER_DAY = 86400
SIMULATION_DURATION_YEARS = 100
SIMULATION_DURATION_SECONDS = SIMULATION_DURATION_YEARS * DAYS_PER_YEAR * SECONDS_PER_DAY

# Masses (kg)
masses = {
    "Sun": 1.9885e30,
    "Jupiter": 1.898e27,
    "Saturn": 5.683e26,
    "Uranus": 8.681e25,
    "Neptune": 1.024e26
}
names = ["Sun", "Jupiter", "Saturn", "Uranus", "Neptune"]
masses_array = np.array([masses[name] for name in names])
n_bodies = len(masses_array)

# Initial conditions (hypothetical example; replace with real data)
# Positions in meters, velocities in m/s
positions = np.array([
    [0.0, 0.0, 0.0],                      # Sun
    [7.4e11, 0.0, 0.0],                    # Jupiter (approx 5 AU)
    [1.35e12, 0.0, 0.0],                   # Saturn
    [2.7e12, 0.0, 0.0],                    # Uranus
    [4.5e12, 0.0, 0.0]                     # Neptune
])
velocities = np.array([
    [0.0, 0.0, 0.0],                       # Sun
    [0.0, 13.07e3, 0.0],                   # Jupiter
    [0.0, 9.68e3, 0.0],                    # Saturn
    [0.0, 6.80e3, 0.0],                    # Uranus
    [0.0, 5.43e3, 0.0]                     # Neptune
])

# Flatten initial state
initial_state = np.hstack([positions.flatten(), velocities.flatten()])

# Derivative function (vectorized)
def n_body_derivatives(t, state):
    state = state.reshape(-1)
    positions = state[:3*n_bodies].reshape(n_bodies, 3)
    velocities = state[3*n_bodies:].reshape(n_bodies, 3)
    
    # Compute displacements (n_bodies, n_bodies, 3)
    dr = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    
    # Squared distances with softening to prevent division by zero
    r_squared = np.sum(dr**2, axis=2) + (1e5)**2  # Softening 100 km
    
    # Compute accelerations (n_bodies, 3)
    r_cubed = r_squared**1.5
    acceleration = G * (dr * masses_array[np.newaxis, :, np.newaxis] / r_cubed[:, :, np.newaxis]).sum(axis=1)
    
    # Derivatives: velocities and accelerations
    derivatives = np.hstack([velocities.ravel(), acceleration.ravel()])
    return derivatives

# Solve using SciPy's solve_ivp with higher-order method
solution = solve_ivp(
    fun=n_body_derivatives,
    t_span=(0, SIMULATION_DURATION_SECONDS),
    y0=initial_state,
    method='DOP853',
    rtol=1e-8,
    atol=1e-10,
    dense_output=True
)

# Extract results
t_eval = np.linspace(0, SIMULATION_DURATION_SECONDS, 1000)
states = solution.sol(t_eval).T  # (n_time, n_states)

# Reshape to (n_time, n_bodies, 3)
positions = states[:, :3*n_bodies].reshape(-1, n_bodies, 3)

# Plot orbits in 2D (XY plane)
plt.figure(figsize=(10, 10))
colors = ['yellow', 'orange', 'brown', 'blue', 'purple']
for i, name in enumerate(names):
    x = positions[:, i, 0] / 1e12  # Convert to trillion meters
    y = positions[:, i, 1] / 1e12
    plt.plot(x, y, label=name, color=colors[i])
plt.xlabel('X (Trillion meters)')
plt.ylabel('Y (Trillion meters)')
plt.title(f'Orbits of Jovian Planets and Sun over {SIMULATION_DURATION_YEARS} Years')
plt.legend()
plt.grid(True)
plt.show()