#!/usr/bin/env python3
"""
N-body simulation using symplectic Euler integration.
Optimized with NumPy for performance.
"""

import numpy as np
import sys
from time import perf_counter

# Constants
PI = np.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

def create_bodies():
    """Initialize the celestial bodies with positions, velocities, and masses."""
    # Bodies: Sun, Jupiter, Saturn, Uranus, Neptune
    positions = np.array([
        [0.0, 0.0, 0.0],  # Sun
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01],  # Jupiter
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01],  # Saturn
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01],  # Uranus
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01],  # Neptune
    ], dtype=np.float64)
    
    velocities = np.array([
        [0.0, 0.0, 0.0],  # Sun
        [1.66007664274403694e-03 * DAYS_PER_YEAR, 
         7.69901118419740425e-03 * DAYS_PER_YEAR, 
         -6.90460016972063023e-05 * DAYS_PER_YEAR],  # Jupiter
        [-2.76742510726862411e-03 * DAYS_PER_YEAR, 
         4.99852801234917238e-03 * DAYS_PER_YEAR, 
         2.30417297573763929e-05 * DAYS_PER_YEAR],  # Saturn
        [2.96460137564761618e-03 * DAYS_PER_YEAR, 
         2.37847173959480950e-03 * DAYS_PER_YEAR, 
         -2.96589568540237556e-05 * DAYS_PER_YEAR],  # Uranus
        [2.68067772490389322e-03 * DAYS_PER_YEAR, 
         1.62824170038242295e-03 * DAYS_PER_YEAR, 
         -9.51592254519715870e-05 * DAYS_PER_YEAR],  # Neptune
    ], dtype=np.float64)
    
    masses = np.array([
        SOLAR_MASS,
        9.54791938424326609e-04 * SOLAR_MASS,  # Jupiter
        2.85885980666130812e-04 * SOLAR_MASS,  # Saturn
        4.36624404335156298e-05 * SOLAR_MASS,  # Uranus
        5.15138902046611451e-05 * SOLAR_MASS,  # Neptune
    ], dtype=np.float64)
    
    return positions, velocities, masses

def offset_momentum(velocities, masses):
    """Adjust Sun's velocity to offset total system momentum."""
    momentum = np.sum(velocities * masses[:, np.newaxis], axis=0)
    velocities[0] = -momentum / masses[0]

def compute_energy(positions, velocities, masses):
    """Calculate total energy of the system."""
    n = len(masses)
    
    # Kinetic energy
    ke = 0.5 * np.sum(masses * np.sum(velocities * velocities, axis=1))
    
    # Potential energy
    pe = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            delta = positions[i] - positions[j]
            distance = np.sqrt(np.sum(delta * delta))
            pe -= (masses[i] * masses[j]) / distance
    
    return ke + pe

def advance(positions, velocities, masses, dt):
    """
    Advance the simulation by dt using symplectic Euler integration.
    This is the performance-critical function.
    """
    n = len(masses)
    
    # Update velocities first (symplectic Euler)
    for i in range(n):
        for j in range(i + 1, n):
            delta = positions[i] - positions[j]
            dist_sq = np.sum(delta * delta)
            mag = dt / (dist_sq * np.sqrt(dist_sq))
            
            # Update velocities
            velocities[i] -= delta * masses[j] * mag
            velocities[j] += delta * masses[i] * mag
    
    # Update positions
    positions += dt * velocities

def main():
    n_steps = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    dt = 0.01
    
    positions, velocities, masses = create_bodies()
    offset_momentum(velocities, masses)
    
    # Initial energy
    energy_initial = compute_energy(positions, velocities, masses)
    print(f"Initial energy: {energy_initial:.9f}")
    
    # Run simulation
    start_time = perf_counter()
    
    for _ in range(n_steps):
        advance(positions, velocities, masses, dt)
    
    elapsed = perf_counter() - start_time
    
    # Final energy
    energy_final = compute_energy(positions, velocities, masses)
    print(f"Final energy:   {energy_final:.9f}")
    print(f"Energy drift:   {abs(energy_final - energy_initial):.9e}")
    print(f"Time elapsed:   {elapsed:.3f} seconds")
    print(f"Steps per sec:  {n_steps / elapsed:.0f}")

if __name__ == "__main__":
    main()
