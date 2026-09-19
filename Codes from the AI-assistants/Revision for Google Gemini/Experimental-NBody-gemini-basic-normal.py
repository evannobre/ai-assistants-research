import math
import time
import argparse
import sys

# Gravitational constant in m^3 kg^-1 s^-2
G = 6.67430e-11 

class Body:
    """Represents a celestial body in 3D space."""
    __slots__ = ['name', 'mass', 'pos', 'vel', 'acc']
    
    def __init__(self, name, mass, pos, vel):
        self.name = name
        self.mass = mass
        self.pos = list(pos)
        self.vel = list(vel)
        self.acc = [0.0, 0.0, 0.0]

def compute_accelerations(bodies):
    """Calculates the gravitational acceleration for all bodies."""
    # Reset accelerations
    for b in bodies:
        b.acc[0] = b.acc[1] = b.acc[2] = 0.0
        
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            b1 = bodies[i]
            b2 = bodies[j]
            
            dx = b2.pos[0] - b1.pos[0]
            dy = b2.pos[1] - b1.pos[1]
            dz = b2.pos[2] - b1.pos[2]
            
            dist_sq = dx**2 + dy**2 + dz**2
            dist = math.sqrt(dist_sq)
            
            # force_mag = G / dist^2
            force_mag = G / dist_sq
            
            # Accel = Force * Mass (of the other object)
            a1 = force_mag * b2.mass
            a2 = force_mag * b1.mass
            
            # Normalize vector directions
            dx_norm = dx / dist
            dy_norm = dy / dist
            dz_norm = dz / dist
            
            # Apply to body 1
            b1.acc[0] += a1 * dx_norm
            b1.acc[1] += a1 * dy_norm
            b1.acc[2] += a1 * dz_norm
            
            # Apply to body 2 (opposite direction)
            b2.acc[0] -= a2 * dx_norm
            b2.acc[1] -= a2 * dy_norm
            b2.acc[2] -= a2 * dz_norm

def velocity_verlet_step(bodies, dt):
    """Advances the simulation by one time step (dt) using Velocity Verlet."""
    # 1. Update positions based on current velocities and accelerations
    for b in bodies:
        b.pos[0] += b.vel[0] * dt + 0.5 * b.acc[0] * (dt ** 2)
        b.pos[1] += b.vel[1] * dt + 0.5 * b.acc[1] * (dt ** 2)
        b.pos[2] += b.vel[2] * dt + 0.5 * b.acc[2] * (dt ** 2)
        
    # Store old accelerations to compute new velocities later
    old_accs = [[b.acc[0], b.acc[1], b.acc[2]] for b in bodies]
    
    # 2. Compute new accelerations based on new positions
    compute_accelerations(bodies)
    
    # 3. Update velocities based on average of old and new accelerations
    for i, b in enumerate(bodies):
        b.vel[0] += 0.5 * (old_accs[i][0] + b.acc[0]) * dt
        b.vel[1] += 0.5 * (old_accs[i][1] + b.acc[1]) * dt
        b.vel[2] += 0.5 * (old_accs[i][2] + b.acc[2]) * dt

def get_jovian_system():
    """Returns the Sun and the Jovian (gas giant) planets with approximate starting vectors."""
    # Data is approximate: masses in kg, distances in meters, velocities in m/s
    return [
        Body("Sun", 1.989e30, [0, 0, 0], [0, 0, 0]),
        Body("Jupiter", 1.898e27, [7.78e11, 0, 0], [0, 13070, 0]),
        Body("Saturn", 5.683e26, [1.434e12, 0, 0], [0, 9680, 0]),
        Body("Uranus", 8.681e25, [2.871e12, 0, 0], [0, 6800, 0]),
        Body("Neptune", 1.024e26, [4.495e12, 0, 0], [0, 5430, 0])
    ]

def main():
    parser = argparse.ArgumentParser(description="N-Body Simulation of the Jovian System.")
    parser.add_argument('--benchmark', action='store_true', help="Run in performance evaluation mode without printing state.")
    parser.add_argument('--steps', type=int, default=10000, help="Number of simulation steps.")
    parser.add_argument('--dt', type=float, default=86400, help="Time step in seconds (default: 1 day = 86400s).")
    
    args = parser.parse_args()
    
    bodies = get_jovian_system()
    
    # Initialize the first acceleration state
    compute_accelerations(bodies)
    
    print(f"Starting simulation for {args.steps} steps (dt = {args.dt}s)...")
    
    start_time = time.perf_counter()
    
    if args.benchmark:
        # Tight loop for performance evaluation
        for _ in range(args.steps):
            velocity_verlet_step(bodies, args.dt)
    else:
        # Loop with basic output
        for step in range(args.steps):
            velocity_verlet_step(bodies, args.dt)
            if step % max(1, (args.steps // 10)) == 0:
                sys.stdout.write(f"Step {step}/{args.steps} completed...\r")
                sys.stdout.flush()
        print("\nFinal Positions (x, y, z in meters):")
        for b in bodies:
            print(f"{b.name:8}: {b.pos[0]:.2e}, {b.pos[1]:.2e}, {b.pos[2]:.2e}")

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    print("\n--- Performance Evaluation ---")
    print(f"Total time   : {elapsed:.4f} seconds")
    print(f"Time per step: {(elapsed / args.steps) * 1e6:.2f} microseconds")
    print(f"Steps per sec: {args.steps / elapsed:,.0f}")

if __name__ == "__main__":
    main()