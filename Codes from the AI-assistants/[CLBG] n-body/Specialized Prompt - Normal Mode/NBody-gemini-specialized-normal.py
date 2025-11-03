import numpy as np
import math

# --- Constants ---
SOLAR_MASS = 4 * math.pi * math.pi
DAYS_PER_YEAR = 365.24
DT = 1.0 / DAYS_PER_YEAR # Time step: 1 day
NUM_ITERATIONS = 50_000_000

# --- Ephemeris Data ---
# Structure: [(positions), (velocities), (mass)]
# Positions and velocities are converted to NumPy arrays for easier vector operations
# Masses are scalar floats

initial_bodies_data = [
    (np.array([0.0, 0.0, 0.0], dtype=np.float64), np.array([0.0, 0.0, 0.0], dtype=np.float64), SOLAR_MASS), # Sun
    (np.array([4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01], dtype=np.float64),
     np.array([1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR], dtype=np.float64),
     9.54791938424326609e-04 * SOLAR_MASS), # Jupiter
    (np.array([8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01], dtype=np.float64),
     np.array([-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR], dtype=np.float64),
     2.85885980666130812e-04 * SOLAR_MASS), # Saturn
    (np.array([1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01], dtype=np.float64),
     np.array([2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR], dtype=np.float64),
     4.36624404335156298e-05 * SOLAR_MASS), # Uranus
    (np.array([1.53796971148509165e+00, -2.59193146099879641e+01, 1.79258772950371181e-01], dtype=np.float64),
     np.array([2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR], dtype=np.float64),
     5.15138902046611451e-05 * SOLAR_MASS)  # Neptune
]

num_bodies = len(initial_bodies_data)

# Initialize arrays for positions, velocities, and masses
positions = np.array([data[0] for data in initial_bodies_data])
velocities = np.array([data[1] for data in initial_bodies_data])
masses = np.array([data[2] for data in initial_bodies_data])

# --- Center of Mass Correction ---
total_momentum = np.sum(masses[:, np.newaxis] * velocities, axis=0)
total_mass = np.sum(masses)
velocities -= total_momentum / total_mass

# --- Simulation Loop ---
print(f"Starting N-body simulation for {NUM_ITERATIONS} iterations...")

for iteration in range(NUM_ITERATIONS):
    accelerations = np.zeros_like(positions) # Initialize accelerations to zero

    # Calculate accelerations for all bodies
    for i in range(num_bodies):
        for j in range(i + 1, num_bodies):
            # Vector from body i to body j
            r_ij = positions[j] - positions[i]

            # Squared distance
            dist_sq = np.sum(r_ij * r_ij) # Dot product
            
            # To avoid division by zero if bodies are exactly at the same point
            # For astronomical simulations, this is rare, but good practice.
            # A small epsilon can be added to dist_sq to prevent sqrt(0) or 1/0,
            # but for this problem, it's likely not critical unless your DT is very large.
            # dist_sq = max(dist_sq, 1e-12) # Small epsilon if needed

            dist_cubed = dist_sq * np.sqrt(dist_sq)

            # Gravitational constant is implicitly 1 due to SOLAR_MASS definition
            # Acceleration contribution for body i
            accel_i = (masses[j] / dist_cubed) * r_ij
            # Acceleration contribution for body j (opposite direction, scaled by mass_i)
            accel_j = (-masses[i] / dist_cubed) * r_ij

            accelerations[i] += accel_i
            accelerations[j] += accel_j

    # Symplectic Euler Step 1: Update Velocities
    velocities += accelerations * DT

    # Symplectic Euler Step 2: Update Positions
    positions += velocities * DT

    # Optional: Print progress or save data periodically
    if (iteration + 1) % (NUM_ITERATIONS // 100) == 0: # Print every 1%
        print(f"Iteration {iteration + 1}/{NUM_ITERATIONS} ({(iteration + 1) / NUM_ITERATIONS * 100:.2f}%)")

print("Simulation finished.")
# You can add code here to print final positions, velocities, or perform further analysis.
# Example: print(positions)