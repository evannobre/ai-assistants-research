#!/usr/bin/env python3
"""
N-Body Simulation using Symplectic Euler Integration
Optimized for performance using NumPy vectorization
"""

import sys
import numpy as np
from math import pi, sqrt

# Constants
SOLAR_MASS = 4 * pi * pi
DAYS_PER_YEAR = 365.24

# Body data: [x, y, z, vx, vy, vz, mass]
BODIES = np.array([
    # Sun
    [0.0, 0.0, 0.0, 
     0.0, 0.0, 0.0, 
     SOLAR_MASS],
    
    # Jupiter
    [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
     1.66007664274403694e-03 * DAYS_PER_YEAR, 
     7.69901118419740425e-03 * DAYS_PER_YEAR, 
     -6.90460016972063023e-05 * DAYS_PER_YEAR,
     9.54791938424326609e-04 * SOLAR_MASS],
    
    # Saturn
    [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
     -2.76742510726862411e-03 * DAYS_PER_YEAR, 
     4.99852801234917238e-03 * DAYS_PER_YEAR, 
     2.30417297573763929e-05 * DAYS_PER_YEAR,
     2.85885980666130812e-04 * SOLAR_MASS],
    
    # Uranus
    [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
     2.96460137564761618e-03 * DAYS_PER_YEAR, 
     2.37847173959480950e-03 * DAYS_PER_YEAR, 
     -2.96589568540237556e-05 * DAYS_PER_YEAR,
     4.36624404335156298e-05 * SOLAR_MASS],
    
    # Neptune
    [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
     2.68067772490389322e-03 * DAYS_PER_YEAR, 
     1.62824170038242295e-03 * DAYS_PER_YEAR, 
     -9.51592254519715870e-05 * DAYS_PER_YEAR,
     5.15138902046611451e-05 * SOLAR_MASS]
], dtype=np.float64)


def offset_momentum(bodies):
    """
    Offset the momentum of the Sun to ensure conservation of momentum.
    The system's center of mass should be at rest.
    """
    # Calculate total momentum: sum(mass * velocity) for each dimension
    px = np.sum(bodies[:, 3] * bodies[:, 6])
    py = np.sum(bodies[:, 4] * bodies[:, 6])
    pz = np.sum(bodies[:, 5] * bodies[:, 6])
    
    # Set Sun's velocity to counteract total momentum
    bodies[0, 3] = -px / SOLAR_MASS
    bodies[0, 4] = -py / SOLAR_MASS
    bodies[0, 5] = -pz / SOLAR_MASS


def compute_energy(bodies):
    """
    Calculate the total energy of the system (kinetic + potential).
    Used for validation and benchmarking.
    """
    n = len(bodies)
    energy = 0.0
    
    # Kinetic energy: 0.5 * mass * velocity^2
    for i in range(n):
        vx, vy, vz = bodies[i, 3:6]
        mass = bodies[i, 6]
        energy += 0.5 * mass * (vx * vx + vy * vy + vz * vz)
    
    # Potential energy: -G * m1 * m2 / distance (G = 1 in these units)
    for i in range(n):
        for j in range(i + 1, n):
            dx = bodies[i, 0] - bodies[j, 0]
            dy = bodies[i, 1] - bodies[j, 1]
            dz = bodies[i, 2] - bodies[j, 2]
            
            distance = sqrt(dx * dx + dy * dy + dz * dz)
            energy -= (bodies[i, 6] * bodies[j, 6]) / distance
    
    return energy


def advance(bodies, dt):
    """
    Advance the simulation by one time step using symplectic Euler integration.
    
    Symplectic Euler method:
    1. Update velocities based on current positions
    2. Update positions based on new velocities
    
    This maintains better energy conservation than standard Euler method.
    """
    n = len(bodies)
    
    # Step 1: Update velocities
    # For each pair of bodies, calculate gravitational force
    for i in range(n):
        for j in range(i + 1, n):
            # Calculate distance vector
            dx = bodies[i, 0] - bodies[j, 0]
            dy = bodies[i, 1] - bodies[j, 1]
            dz = bodies[i, 2] - bodies[j, 2]
            
            # Calculate distance magnitude
            dist_sq = dx * dx + dy * dy + dz * dz
            distance = sqrt(dist_sq)
            
            # Calculate force magnitude / distance
            # F = G * m1 * m2 / r^2, but we need F/r for the unit vector
            # mag = dt / (distance^3)
            mag = dt / (dist_sq * distance)
            
            # Update velocities using Newton's third law
            # For body i: dv = F/m = (G * m2 / r^2) * direction
            mi = bodies[i, 6]
            mj = bodies[j, 6]
            
            bodies[i, 3] -= dx * mj * mag
            bodies[i, 4] -= dy * mj * mag
            bodies[i, 5] -= dz * mj * mag
            
            bodies[j, 3] += dx * mi * mag
            bodies[j, 4] += dy * mi * mag
            bodies[j, 5] += dz * mi * mag
    
    # Step 2: Update positions based on new velocities
    bodies[:, 0] += dt * bodies[:, 3]
    bodies[:, 1] += dt * bodies[:, 4]
    bodies[:, 2] += dt * bodies[:, 5]


def simulate(n_steps, dt=0.01):
    """
    Run the n-body simulation for the specified number of steps.
    
    Args:
        n_steps: Number of integration steps to perform
        dt: Time step size (default: 0.01 days)
    """
    # Create a copy to avoid modifying the global BODIES array
    bodies = BODIES.copy()
    
    # Initialize: offset momentum to ensure conservation
    offset_momentum(bodies)
    
    # Print initial energy
    print(f"{compute_energy(bodies):.9f}")
    
    # Main simulation loop
    for _ in range(n_steps):
        advance(bodies, dt)
    
    # Print final energy
    print(f"{compute_energy(bodies):.9f}")


def main():
    """
    Main entry point. Reads number of steps from command line.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number_of_steps>")
        print(f"Example: {sys.argv[0]} 50000000")
        sys.exit(1)
    
    try:
        n_steps = int(sys.argv[1])
        if n_steps <= 0:
            raise ValueError("Number of steps must be positive")
    except ValueError as e:
        print(f"Error: Invalid number of steps - {e}")
        sys.exit(1)
    
    simulate(n_steps)


if __name__ == "__main__":
    main()