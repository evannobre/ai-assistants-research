import math
import argparse
import time
from itertools import combinations

# --- Constants ---
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
AU = 1.496e11    # Astronomical Unit in meters

class Vector:
    """A minimal 3D Vector class using native Python slots for memory efficiency."""
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"({self.x:.2e}, {self.y:.2e}, {self.z:.2e})"

class Body:
    """Represents a celestial body."""
    __slots__ = ('name', 'mass', 'pos', 'vel', 'acc')

    def __init__(self, name, mass, x, y, z, vx, vy, vz):
        self.name = name
        self.mass = mass
        self.pos = Vector(x, y, z)
        self.vel = Vector(vx, vy, vz)
        self.acc = Vector(0.0, 0.0, 0.0)

def compute_accelerations(bodies):
    """
    Calculates interactions between all unique pairs of bodies.
    F = G * m1 * m2 / r^2
    a = F / m
    """
    # Reset accelerations to zero
    for body in bodies:
        body.acc.x = 0.0
        body.acc.y = 0.0
        body.acc.z = 0.0

    # Calculate forces for every unique pair (Newton's 3rd Law optimization)
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    for b1, b2 in combinations(bodies, 2):
        dx = b2.pos.x - b1.pos.x
        dy = b2.pos.y - b1.pos.y
        dz = b2.pos.z - b1.pos.z
        
        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq)
        
        # F = G*m1*m2 / r^2
        # a = F/m  => a = G*m_other / r^2
        # Direction vector (normalized) is (dx, dy, dz) / dist
        # So vector a = (G * m_other / r^3) * vector_r
        
        f_common = G / (dist_sq * dist)
        
        # Acceleration exerted on b1 by b2
        a1 = f_common * b2.mass
        b1.acc.x += a1 * dx
        b1.acc.y += a1 * dy
        b1.acc.z += a1 * dz
        
        # Acceleration exerted on b2 by b1 (opposite direction)
        a2 = f_common * b1.mass
        b2.acc.x -= a2 * dx
        b2.acc.y -= a2 * dy
        b2.acc.z -= a2 * dz

def run_simulation(args):
    # --- Initial Conditions (Approximate for visual stability) ---
    # Positions (m) are placed on X axis, Velocities (m/s) on Y axis.
    # Data source: NASA Planetary Fact Sheet (Approximate Mean)
    
    sun = Body("Sun", 1.989e30, 0, 0, 0, 0, 0, 0)
    
    jupiter = Body("Jupiter", 1.898e27, 
                   5.20 * AU, 0, 0, 
                   0, 13.07e3, 0)
                   
    saturn = Body("Saturn", 5.683e26, 
                  9.58 * AU, 0, 0, 
                  0, 9.68e3, 0)
                  
    uranus = Body("Uranus", 8.681e25, 
                  19.22 * AU, 0, 0, 
                  0, 6.80e3, 0)
                  
    neptune = Body("Neptune", 1.024e26, 
                   30.05 * AU, 0, 0, 
                   0, 5.43e3, 0)

    bodies = [sun, jupiter, saturn, uranus, neptune]

    # Offset Sun momentum to ensure system barycenter remains static
    px = py = pz = 0.0
    for b in bodies:
        px += b.mass * b.vel.x
        py += b.mass * b.vel.y
        pz += b.mass * b.vel.z
    
    sun.vel.x -= px / sun.mass
    sun.vel.y -= py / sun.mass
    sun.vel.z -= pz / sun.mass

    # --- Simulation Loop (Velocity Verlet) ---
    dt = args.step_size * 24 * 3600 # Convert days to seconds
    steps = int((args.years * 365.25) / args.step_size)
    
    print(f"Simulating {args.years} years with dt={args.step_size} days...")
    print(f"Total steps: {steps}")
    
    start_time = time.perf_counter()
    
    # Pre-calculate initial accelerations
    compute_accelerations(bodies)
    
    for i in range(steps):
        # 1. First half-kick (Update Velocity)
        # 2. Drift (Update Position)
        for b in bodies:
            b.vel.x += 0.5 * b.acc.x * dt
            b.vel.y += 0.5 * b.acc.y * dt
            b.vel.z += 0.5 * b.acc.z * dt
            
            b.pos.x += b.vel.x * dt
            b.pos.y += b.vel.y * dt
            b.pos.z += b.vel.z * dt
            
        # 3. Recalculate forces at new positions
        compute_accelerations(bodies)
        
        # 4. Second half-kick (Update Velocity)
        for b in bodies:
            b.vel.x += 0.5 * b.acc.x * dt
            b.vel.y += 0.5 * b.acc.y * dt
            b.vel.z += 0.5 * b.acc.z * dt
            
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    # --- Output ---
    if args.perf:
        print("-" * 30)
        print(f"PERFORMANCE REPORT")
        print(f"Steps/Sec: {steps / duration:.2f}")
        print(f"Time:      {duration:.4f} seconds")
        print("-" * 30)
    else:
        print("\nFinal Positions (AU):")
        for b in bodies:
            print(f"{b.name:8}: {b.pos.x/AU:8.2f}  {b.pos.y/AU:8.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N-Body Solar System Simulation")
    parser.add_argument("--years", type=float, default=10.0, help="Simulation duration in years")
    parser.add_argument("--step_size", type=float, default=1.0, help="Time step in days")
    parser.add_argument("--perf", action="store_true", help="Run in performance evaluation mode")
    
    args = parser.parse_args()
    run_simulation(args)