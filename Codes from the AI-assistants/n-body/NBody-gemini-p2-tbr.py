#!/usr/bin/env python3
import sys
import math
import time
import argparse
from dataclasses import dataclass
from typing import List

# --- Constants & Physics Configuration ---
PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# --- Data Structures ---
@dataclass
class Body:
    name: str
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float

class NBodySystem:
    def __init__(self, bodies: List[Body]):
        self.bodies = bodies

    def offset_momentum(self):
        """
        Adjusts the Sun's velocity to ensure the center of momentum 
        of the entire system remains at the origin.
        """
        px, py, pz = 0.0, 0.0, 0.0
        for body in self.bodies:
            px += body.vx * body.mass
            py += body.vy * body.mass
            pz += body.vz * body.mass
        
        # The Sun is always the first body in our list
        sun = self.bodies[0]
        sun.vx = -px / SOLAR_MASS
        sun.vy = -py / SOLAR_MASS
        sun.vz = -pz / SOLAR_MASS

    def energy(self) -> float:
        """Calculates the total energy (Kinetic + Potential) of the system."""
        e = 0.0
        for i in range(len(self.bodies)):
            b1 = self.bodies[i]
            # Kinetic Energy: 0.5 * m * v^2
            e += 0.5 * b1.mass * (b1.vx**2 + b1.vy**2 + b1.vz**2)
            
            # Potential Energy: - (G * m1 * m2) / distance
            # Note: G is effectively 1 in these normalized units relative to Solar Mass
            for j in range(i + 1, len(self.bodies)):
                b2 = self.bodies[j]
                dx = b1.x - b2.x
                dy = b1.y - b2.y
                dz = b1.z - b2.z
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                e -= (b1.mass * b2.mass) / distance
        return e

    def advance(self, dt: float):
        """
        Advances the system by time step dt using a symplectic integrator.
        Complexity: O(N^2) for pair-wise interactions.
        """
        bodies = self.bodies
        n = len(bodies)
        
        # 1. Update Velocities based on Forces (Gravity)
        for i in range(n):
            b1 = bodies[i]
            for j in range(i + 1, n):
                b2 = bodies[j]
                dx = b1.x - b2.x
                dy = b1.y - b2.y
                dz = b1.z - b2.z
                
                dist_sq = dx*dx + dy*dy + dz*dz
                mag = dt / (dist_sq * math.sqrt(dist_sq))
                
                # Force components
                # We update b1 and b2 simultaneously (Newton's 3rd Law)
                # to reduce loop cycles.
                
                b1.vx -= dx * b2.mass * mag
                b1.vy -= dy * b2.mass * mag
                b1.vz -= dz * b2.mass * mag
                
                b2.vx += dx * b1.mass * mag
                b2.vy += dy * b1.mass * mag
                b2.vz += dz * b1.mass * mag

        # 2. Update Positions based on new Velocities
        for i in range(n):
            b = bodies[i]
            b.x += dt * b.vx
            b.y += dt * b.vy
            b.z += dt * b.vz

# --- Initialization Data (NASA JPL Horizons / Standard Benchmark Values) ---
def create_jovian_system() -> NBodySystem:
    sun = Body("Sun", 0, 0, 0, 0, 0, 0, SOLAR_MASS)
    
    jupiter = Body(
        "Jupiter",
        4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
        1.66007664274403694e-03 * DAYS_PER_YEAR, 
        7.69901118419740425e-03 * DAYS_PER_YEAR, 
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
        9.54791938424326609e-04 * SOLAR_MASS
    )

    saturn = Body(
        "Saturn",
        8.34336668203263098e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
        -2.76742510726862411e-03 * DAYS_PER_YEAR, 
        4.99852801234917238e-03 * DAYS_PER_YEAR, 
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        2.85885980666130812e-04 * SOLAR_MASS
    )

    uranus = Body(
        "Uranus",
        1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
        2.96460137564761618e-03 * DAYS_PER_YEAR, 
        2.37847173959480950e-03 * DAYS_PER_YEAR, 
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
        4.36624404335156298e-05 * SOLAR_MASS
    )

    neptune = Body(
        "Neptune",
        1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
        2.68067772490389322e-03 * DAYS_PER_YEAR, 
        1.62824170038242295e-03 * DAYS_PER_YEAR, 
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
        5.15138902046611451e-05 * SOLAR_MASS
    )

    return NBodySystem([sun, jupiter, saturn, uranus, neptune])

# --- Main Driver ---
def main():
    parser = argparse.ArgumentParser(description="N-Body Simulation: Sun + Jovian Planets")
    parser.add_argument("steps", type=int, nargs='?', default=1000, 
                        help="Number of simulation steps (default: 1000)")
    parser.add_argument("--perf", action="store_true", 
                        help="Enable performance metrics output")
    
    args = parser.parse_args()
    
    # 1. Initialize
    system = create_jovian_system()
    system.offset_momentum()
    
    dt = 0.01
    steps = args.steps
    
    print(f"Simulating {len(system.bodies)} bodies for {steps} steps (dt={dt})...")
    print(f"Initial Energy: {system.energy():.9f}")

    # 2. Execution Loop
    start_time = time.time()
    
    for _ in range(steps):
        system.advance(dt)
        
    end_time = time.time()
    
    # 3. Final State
    print(f"Final Energy:   {system.energy():.9f}")
    
    # 4. Performance Metrics
    if args.perf:
        duration = end_time - start_time
        print("-" * 30)
        print(f"Execution Time: {duration:.4f} seconds")
        print(f"Steps per sec:  {steps / duration:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    main()