import numpy as np
import time
import argparse

# Constants (Using AU, Days, and Solar Masses for stability)
G = 0.000295912208286  # Gravitational constant in AU^3 / (solar_mass * day^2)

def get_accelerations(pos, masses):
    """Calculates the acceleration for each body."""
    n = pos.shape[0]
    acc = np.zeros_like(pos)
    for i in range(n):
        for j in range(i + 1, n):
            diff = pos[j] - pos[i]
            dist_sq = np.sum(diff**2)
            dist = np.sqrt(dist_sq)
            force_mag = G * diff / (dist**3)
            acc[i] += force_mag * masses[j]
            acc[j] -= force_mag * masses[i]
    return acc

def simulate(pos, vel, masses, dt, steps):
    """Velocity Verlet integration."""
    acc = get_accelerations(pos, masses)
    for _ in range(steps):
        # 1. Half-step velocity
        vel += 0.5 * acc * dt
        # 2. Full-step position
        pos += vel * dt
        # 3. New acceleration
        acc = get_accelerations(pos, masses)
        # 4. Final half-step velocity
        vel += 0.5 * acc * dt
    return pos, vel

def main():
    parser = argparse.ArgumentParser(description="Jovian N-Body Simulation")
    parser.add_argument("--perf", action="store_true", help="Enable performance evaluation")
    args = parser.parse_args()

    # Data: Sun, Jupiter, Saturn, Uranus, Neptune
    # Positions (AU), Velocities (AU/day), Masses (Solar Mass)
    # (Simplified initial state for demo)
    masses = np.array([1.0, 0.000954, 0.000285, 0.000043, 0.000051])
    pos = np.array([
        [0.0, 0.0, 0.0],          # Sun
        [5.2, 0.0, 0.0],          # Jupiter
        [9.5, 0.0, 0.0],          # Saturn
        [19.2, 0.0, 0.0],         # Uranus
        [30.1, 0.0, 0.0]          # Neptune
    ])
    vel = np.array([
        [0.0, 0.0, 0.0],
        [0.0, 0.0075, 0.0],
        [0.0, 0.0054, 0.0],
        [0.0, 0.0039, 0.0],
        [0.0, 0.0031, 0.0]
    ])

    dt = 1.0  # 1 day per step
    steps = 3650  # 10 years

    if args.perf:
        start_time = time.time()
        final_pos, _ = simulate(pos, vel, masses, dt, steps)
        end_time = time.time()
        print(f"Performance: {steps} steps took {end_time - start_time:.4f} seconds")
    else:
        final_pos, _ = simulate(pos, vel, masses, dt, steps)
        print("Final Positions after 10 years:\n", final_pos)

if __name__ == "__main__":
    main()