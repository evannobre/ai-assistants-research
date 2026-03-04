#!/usr/bin/env python3
"""
N-Body Simulation of Jupiter's Galilean Moons and the Sun
Uses vectorized NumPy operations for performance
"""

import numpy as np
import argparse
import time
from dataclasses import dataclass

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)

@dataclass
class Body:
    """Represents a celestial body"""
    name: str
    mass: float  # kg
    position: np.ndarray  # m (x, y, z)
    velocity: np.ndarray  # m/s (vx, vy, vz)

def initialize_jupiter_system():
    """
    Initialize Jupiter system with Sun, Jupiter, and Galilean moons
    Using approximate orbital parameters
    """
    bodies = []
    
    # Sun (stationary at origin for simplicity)
    bodies.append(Body(
        name="Sun",
        mass=1.989e30,
        position=np.array([0.0, 0.0, 0.0]),
        velocity=np.array([0.0, 0.0, 0.0])
    ))
    
    # Jupiter (simplified circular orbit)
    jupiter_dist = 7.785e11  # ~5.2 AU in meters
    jupiter_vel = np.sqrt(G * bodies[0].mass / jupiter_dist)
    bodies.append(Body(
        name="Jupiter",
        mass=1.898e27,
        position=np.array([jupiter_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel, 0.0])
    ))
    
    # Galilean moons (relative to Jupiter)
    # Io
    io_dist = 4.217e8
    io_vel = np.sqrt(G * bodies[1].mass / io_dist)
    bodies.append(Body(
        name="Io",
        mass=8.932e22,
        position=np.array([jupiter_dist + io_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel + io_vel, 0.0])
    ))
    
    # Europa
    europa_dist = 6.711e8
    europa_vel = np.sqrt(G * bodies[1].mass / europa_dist)
    bodies.append(Body(
        name="Europa",
        mass=4.800e22,
        position=np.array([jupiter_dist, europa_dist, 0.0]),
        velocity=np.array([-europa_vel, jupiter_vel, 0.0])
    ))
    
    # Ganymede
    ganymede_dist = 1.070e9
    ganymede_vel = np.sqrt(G * bodies[1].mass / ganymede_dist)
    bodies.append(Body(
        name="Ganymede",
        mass=1.482e23,
        position=np.array([jupiter_dist - ganymede_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel - ganymede_vel, 0.0])
    ))
    
    # Callisto
    callisto_dist = 1.883e9
    callisto_vel = np.sqrt(G * bodies[1].mass / callisto_dist)
    bodies.append(Body(
        name="Callisto",
        mass=1.076e23,
        position=np.array([jupiter_dist, -callisto_dist, 0.0]),
        velocity=np.array([callisto_vel, jupiter_vel, 0.0])
    ))
    
    return bodies

def compute_accelerations(positions, masses):
    """
    Vectorized acceleration computation using NumPy
    
    Args:
        positions: (N, 3) array of positions
        masses: (N,) array of masses
    
    Returns:
        (N, 3) array of accelerations
    """
    N = len(masses)
    accelerations = np.zeros_like(positions)
    
    # Compute all pairwise displacement vectors
    # r_ij = r_j - r_i (broadcasting: (N, 1, 3) - (1, N, 3) = (N, N, 3))
    r_vectors = positions[np.newaxis, :, :] - positions[:, np.newaxis, :]
    
    # Compute distances with small epsilon to avoid division by zero
    distances = np.linalg.norm(r_vectors, axis=2)
    np.fill_diagonal(distances, 1.0)  # Avoid self-interaction
    
    # Compute gravitational forces (vectorized)
    # F_ij = G * m_j / r_ij^3 * r_vec_ij
    force_magnitudes = G * masses[np.newaxis, :] / distances**3
    np.fill_diagonal(force_magnitudes, 0.0)
    
    # Sum all forces on each body
    accelerations = np.sum(force_magnitudes[:, :, np.newaxis] * r_vectors, axis=1)
    
    return accelerations

def leapfrog_step(bodies, dt):
    """
    Leapfrog integration (symplectic, energy-conserving)
    
    Args:
        bodies: list of Body objects
        dt: timestep in seconds
    """
    N = len(bodies)
    
    # Extract positions, velocities, and masses as arrays
    positions = np.array([body.position for body in bodies])
    velocities = np.array([body.velocity for body in bodies])
    masses = np.array([body.mass for body in bodies])
    
    # Half-step velocity update
    accelerations = compute_accelerations(positions, masses)
    velocities += 0.5 * dt * accelerations
    
    # Full-step position update
    positions += dt * velocities
    
    # Half-step velocity update (with new positions)
    accelerations = compute_accelerations(positions, masses)
    velocities += 0.5 * dt * accelerations
    
    # Update bodies
    for i, body in enumerate(bodies):
        body.position = positions[i]
        body.velocity = velocities[i]

def compute_energy(bodies):
    """Compute total energy of the system"""
    N = len(bodies)
    positions = np.array([body.position for body in bodies])
    velocities = np.array([body.velocity for body in bodies])
    masses = np.array([body.mass for body in bodies])
    
    # Kinetic energy
    kinetic = 0.5 * np.sum(masses * np.sum(velocities**2, axis=1))
    
    # Potential energy
    potential = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            r = np.linalg.norm(positions[i] - positions[j])
            potential -= G * masses[i] * masses[j] / r
    
    return kinetic + potential

def run_simulation(bodies, total_time, dt, verbose=False, benchmark=False):
    """
    Run N-body simulation
    
    Args:
        bodies: list of Body objects
        total_time: total simulation time in seconds
        dt: timestep in seconds
        verbose: print progress
        benchmark: measure performance
    """
    n_steps = int(total_time / dt)
    
    if benchmark:
        start_time = time.perf_counter()
    
    initial_energy = compute_energy(bodies)
    
    for step in range(n_steps):
        leapfrog_step(bodies, dt)
        
        if verbose and step % (n_steps // 10) == 0:
            progress = 100 * step / n_steps
            energy = compute_energy(bodies)
            energy_error = abs((energy - initial_energy) / initial_energy) * 100
            print(f"Progress: {progress:.1f}% | Energy error: {energy_error:.6f}%")
    
    if benchmark:
        elapsed = time.perf_counter() - start_time
        final_energy = compute_energy(bodies)
        energy_error = abs((final_energy - initial_energy) / initial_energy) * 100
        
        print("\n=== Performance Results ===")
        print(f"Total steps: {n_steps:,}")
        print(f"Bodies: {len(bodies)}")
        print(f"Elapsed time: {elapsed:.3f} seconds")
        print(f"Steps per second: {n_steps / elapsed:,.0f}")
        print(f"Time per step: {elapsed / n_steps * 1000:.4f} ms")
        print(f"Final energy error: {energy_error:.6f}%")
    
    return bodies

def main():
    parser = argparse.ArgumentParser(
        description="N-Body simulation of Jupiter's moons",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--days', type=float, default=30.0,
        help='Simulation duration in Earth days (default: 30)'
    )
    parser.add_argument(
        '--timestep', type=float, default=3600.0,
        help='Integration timestep in seconds (default: 3600 = 1 hour)'
    )
    parser.add_argument(
        '--benchmark', action='store_true',
        help='Run performance benchmark'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Print verbose progress information'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    print("Initializing Jupiter system...")
    bodies = initialize_jupiter_system()
    
    print(f"\nSimulating {len(bodies)} bodies:")
    for body in bodies:
        print(f"  - {body.name}")
    
    # Convert days to seconds
    total_time = args.days * 86400.0
    
    print(f"\nSimulation parameters:")
    print(f"  Duration: {args.days} days")
    print(f"  Timestep: {args.timestep} seconds ({args.timestep/3600:.2f} hours)")
    print(f"  Total steps: {int(total_time / args.timestep):,}")
    print()
    
    # Run simulation
    bodies = run_simulation(
        bodies, 
        total_time, 
        args.timestep,
        verbose=args.verbose,
        benchmark=args.benchmark
    )
    
    # Print final positions
    if not args.benchmark:
        print("\nFinal positions (relative to Sun):")
        for body in bodies:
            dist = np.linalg.norm(body.position)
            print(f"  {body.name:10s}: {dist/1e9:.3f} million km from Sun")

if __name__ == "__main__":
    main()
