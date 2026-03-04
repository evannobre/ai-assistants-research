#!/usr/bin/env python3
"""
N-Body Simulation using Symplectic Euler Integration
Optimized for performance using NumPy vectorization
"""

import sys
import numpy as np
from time import perf_counter

# Constants
PI = np.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# Number of bodies
N_BODIES = 5


def initialize_bodies():
    """
    Initialize position, velocity, and mass arrays for all bodies.
    Returns: positions (5x3), velocities (5x3), masses (5,)
    """
    # Positions [x, y, z] for each body
    positions = np.array([
        # Sun
        [0.0, 0.0, 0.0],
        # Jupiter
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01],
        # Saturn
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01],
        # Uranus
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01],
        # Neptune
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01]
    ], dtype=np.float64)
    
    # Velocities [vx, vy, vz] for each body
    velocities = np.array([
        # Sun
        [0.0, 0.0, 0.0],
        # Jupiter
        [1.66007664274403694e-03 * DAYS_PER_YEAR,
         7.69901118419740425e-03 * DAYS_PER_YEAR,
         -6.90460016972063023e-05 * DAYS_PER_YEAR],
        # Saturn
        [-2.76742510726862411e-03 * DAYS_PER_YEAR,
         4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR],
        # Uranus
        [2.96460137564761618e-03 * DAYS_PER_YEAR,
         2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR],
        # Neptune
        [2.68067772490389322e-03 * DAYS_PER_YEAR,
         1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR]
    ], dtype=np.float64)
    
    # Masses
    masses = np.array([
        SOLAR_MASS,
        9.54791938424326609e-04 * SOLAR_MASS,
        2.85885980666130812e-04 * SOLAR_MASS,
        4.36624404335156298e-05 * SOLAR_MASS,
        5.15138902046611451e-05 * SOLAR_MASS
    ], dtype=np.float64)
    
    return positions, velocities, masses


def offset_momentum(velocities, masses):
    """
    Offset the Sun's momentum to ensure the system's total momentum is zero.
    This is done by adjusting the Sun's velocity.
    """
    # Calculate total momentum: sum(m_i * v_i)
    momentum = np.sum(velocities * masses[:, np.newaxis], axis=0)
    # Set Sun's velocity to balance the system
    velocities[0] = -momentum / masses[0]


def compute_energy(positions, velocities, masses):
    """
    Calculate the total energy of the system (kinetic + potential).
    """
    # Kinetic energy: 0.5 * sum(m_i * v_i^2)
    kinetic = 0.5 * np.sum(masses * np.sum(velocities**2, axis=1))
    
    # Potential energy: -sum(G * m_i * m_j / r_ij) for all pairs i < j
    potential = 0.0
    for i in range(N_BODIES):
        for j in range(i + 1, N_BODIES):
            delta = positions[i] - positions[j]
            distance = np.sqrt(np.sum(delta**2))
            potential -= masses[i] * masses[j] / distance
    
    return kinetic + potential


def advance(positions, velocities, masses, dt):
    """
    Advance the simulation by one time step using symplectic Euler integration.
    
    Symplectic Euler:
    1. Update velocities based on forces at current positions
    2. Update positions based on new velocities
    """
    # Pre-allocate arrays for forces
    # Using a more cache-friendly approach
    
    # For each pair of bodies, calculate gravitational interaction
    for i in range(N_BODIES):
        for j in range(i + 1, N_BODIES):
            # Vector from body i to body j
            delta = positions[i] - positions[j]
            
            # Distance squared
            distance_sq = np.sum(delta**2)
            
            # Distance
            distance = np.sqrt(distance_sq)
            
            # Magnitude of force: G * m_i * m_j / r^3
            # (We multiply by delta to get the force vector)
            mag = dt / (distance * distance_sq)
            
            # Update velocities using Newton's third law
            # F_ij = -F_ji, so we update both bodies simultaneously
            velocities[i] -= delta * masses[j] * mag
            velocities[j] += delta * masses[i] * mag
    
    # Update positions based on new velocities (symplectic step)
    positions += velocities * dt


def run_simulation(n_steps):
    """
    Run the n-body simulation for the specified number of steps.
    """
    dt = 0.01  # Time step
    
    # Initialize the system
    positions, velocities, masses = initialize_bodies()
    
    # Offset momentum to ensure conservation
    offset_momentum(velocities, masses)
    
    # Calculate and print initial energy
    initial_energy = compute_energy(positions, velocities, masses)
    print(f"{initial_energy:.9f}")
    
    # Run simulation
    for _ in range(n_steps):
        advance(positions, velocities, masses, dt)
    
    # Calculate and print final energy
    final_energy = compute_energy(positions, velocities, masses)
    print(f"{final_energy:.9f}")


def main():
    """
    Main entry point for the n-body simulation.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number_of_steps>")
        print(f"Example: {sys.argv[0]} 50000000")
        sys.exit(1)
    
    try:
        n_steps = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid number of steps '{sys.argv[1]}'")
        sys.exit(1)
    
    if n_steps <= 0:
        print(f"Error: Number of steps must be positive")
        sys.exit(1)
    
    # Run simulation with timing
    start_time = perf_counter()
    run_simulation(n_steps)
    end_time = perf_counter()
    
    # Print execution time to stderr
    print(f"\nExecution time: {end_time - start_time:.3f} seconds", file=sys.stderr)


if __name__ == "__main__":
    main()
