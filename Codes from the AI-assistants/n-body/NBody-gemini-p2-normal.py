import numpy as np
import argparse
import time
import sys

# Constants in Astronomical Units (AU), Days, and Solar Masses
G = 0.0002959122082855911  # Gaussian gravitational constant squared

def get_initial_state():
    """
    Initial state for the Sun and Jovian planets.
    Positions (AU) and Velocities (AU/day).
    Data represents an approximate epoch.
    """
    # Mass, Position (x, y, z), Velocity (vx, vy, vz)
    data = {
        "sun":     [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "jupiter": [0.0009547919, 4.8414, -1.1603, -0.1036, 0.0016, 0.0076, 0.0002],
        "saturn":  [0.0002858860, 8.3400, 4.1247, -0.4035, -0.0027, 0.0050, 0.0002],
        "uranus":  [0.0000436624, 12.8946, -15.1111, -0.2233, 0.0029, 0.0024, 0.00004],
        "neptune": [0.0000515138, 15.3796, -25.9033, 0.1792, 0.0026, 0.0015, -0.00006]
    }
    
    masses = np.array([v[0] for v in data.values()])
    pos = np.array([v[1:4] for v in data.values()])
    vel = np.array([v[4:7] for v in data.values()])
    
    return masses, pos, vel

def compute_accelerations(pos, masses):
    n = len(masses)
    acc = np.zeros_like(pos)
    for i in range(n):
        for j in range(i + 1, n):
            r_vec = pos[j] - pos[i]
            dist_sq = np.sum(r_vec**2)
            dist = np.sqrt(dist_sq)
            mag = G / (dist_sq * dist)
            
            force = r_vec * mag
            acc[i] += force * masses[j]
            acc[j] -= force * masses[i]
    return acc

def simulate(steps, dt, profile=False):
    masses, pos, vel = get_initial_state()
    acc = compute_accelerations(pos, masses)
    
    start_time = time.perf_counter()
    
    for _ in range(steps):
        # 1. Update positions (Verlet Half-step)
        pos += vel * dt + 0.5 * acc * dt**2
        
        # 2. Save old acceleration and compute new
        old_acc = acc
        acc = compute_accelerations(pos, masses)
        
        # 3. Update velocities
        vel += 0.5 * (old_acc + acc) * dt

    end_time = time.perf_counter()
    
    if profile:
        print(f"--- Performance Evaluation ---")
        print(f"Total Steps: {steps}")
        print(f"Execution Time: {end_time - start_time:.4f} seconds")
        print(f"Throughput: {steps / (end_time - start_time):.2f} steps/sec")
        print(f"Memory Usage: ~{sys.getsizeof(pos) + sys.getsizeof(vel):.2f} bytes (State only)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N-Body Jovian Simulation")
    parser.add_argument("--steps", type=int, default=10000, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step in days")
    parser.add_argument("--bench", action="store_true", help="Enable performance evaluation")
    
    args = parser.parse_args()
    simulate(args.steps, args.dt, profile=args.bench)