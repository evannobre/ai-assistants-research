#!/usr/bin/env python3
"""
N-Body Simulation of the Jovian System
Simulates gravitational interactions between Jupiter, its major moons, and the Sun
Optimized for performance using NumPy vectorization
"""

import numpy as np
import argparse
import time
import sys
from dataclasses import dataclass
from typing import Tuple

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
AU = 1.496e11    # Astronomical Unit (m)

@dataclass
class CelestialBody:
    """Represents a celestial body with its physical properties"""
    name: str
    mass: float      # kg
    position: np.ndarray  # m (3D vector)
    velocity: np.ndarray  # m/s (3D vector)
    
class NBodySimulator:
    """
    Implements the n-body gravitational simulation using the Velocity Verlet algorithm
    for improved numerical stability and energy conservation.
    """
    
    def __init__(self, bodies: list[CelestialBody], dt: float = 3600.0):
        """
        Initialize the n-body simulator
        
        Args:
            bodies: List of CelestialBody objects
            dt: Time step in seconds (default: 1 hour)
        """
        self.n = len(bodies)
        self.dt = dt
        self.bodies = bodies
        
        # Vectorized state arrays for performance
        self.masses = np.array([b.mass for b in bodies])
        self.positions = np.array([b.position for b in bodies])
        self.velocities = np.array([b.velocity for b in bodies])
        
        # Pre-compute initial accelerations
        self.accelerations = self._compute_accelerations()
        
    def _compute_accelerations(self) -> np.ndarray:
        """
        Compute gravitational accelerations for all bodies using vectorized operations.
        Time complexity: O(n^2) but heavily optimized with NumPy
        
        Returns:
            Array of acceleration vectors for each body
        """
        acc = np.zeros_like(self.positions)
        
        # Compute pairwise interactions using broadcasting
        for i in range(self.n):
            # Displacement vectors from body i to all other bodies
            r_vec = self.positions - self.positions[i]
            
            # Distance cubed (with small epsilon to avoid division by zero)
            r_mag = np.linalg.norm(r_vec, axis=1)
            r_mag[i] = 1.0  # Avoid self-interaction
            r3 = r_mag ** 3
            
            # Vectorized gravitational acceleration
            # a_i = G * sum(m_j * r_ij / |r_ij|^3)
            acc[i] = G * np.sum(
                (self.masses[:, np.newaxis] * r_vec) / r3[:, np.newaxis],
                axis=0
            )
            acc[i] -= G * self.masses[i] * r_vec[i] / (r3[i] + 1e-10)
            
        return acc
    
    def step(self) -> None:
        """
        Perform one simulation step using the Velocity Verlet integration method.
        This method provides better energy conservation than Euler's method.
        
        Velocity Verlet algorithm:
        1. x(t+dt) = x(t) + v(t)*dt + 0.5*a(t)*dt^2
        2. a(t+dt) = compute accelerations at new positions
        3. v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        """
        # Store current accelerations
        acc_old = self.accelerations
        
        # Update positions
        self.positions += self.velocities * self.dt + 0.5 * acc_old * self.dt ** 2
        
        # Compute new accelerations
        self.accelerations = self._compute_accelerations()
        
        # Update velocities using average of old and new accelerations
        self.velocities += 0.5 * (acc_old + self.accelerations) * self.dt
        
    def simulate(self, steps: int, progress_interval: int = 1000) -> float:
        """
        Run the simulation for a specified number of steps
        
        Args:
            steps: Number of simulation steps
            progress_interval: Print progress every N steps
            
        Returns:
            Elapsed wall-clock time in seconds
        """
        start_time = time.perf_counter()
        
        for step in range(steps):
            self.step()
            
            if (step + 1) % progress_interval == 0:
                elapsed = time.perf_counter() - start_time
                rate = (step + 1) / elapsed
                print(f"Step {step + 1}/{steps} | Rate: {rate:.2f} steps/s | "
                      f"Elapsed: {elapsed:.2f}s", end='\r')
        
        elapsed_time = time.perf_counter() - start_time
        print()  # New line after progress
        return elapsed_time
    
    def get_orbital_energy(self) -> Tuple[float, float, float]:
        """
        Calculate total system energy (kinetic + potential).
        Useful for validating simulation accuracy.
        
        Returns:
            Tuple of (kinetic_energy, potential_energy, total_energy) in Joules
        """
        # Kinetic energy: 0.5 * m * v^2
        ke = 0.5 * np.sum(self.masses * np.sum(self.velocities ** 2, axis=1))
        
        # Potential energy: -G * m_i * m_j / |r_ij|
        pe = 0.0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                r = np.linalg.norm(self.positions[i] - self.positions[j])
                pe -= G * self.masses[i] * self.masses[j] / r
        
        return ke, pe, ke + pe

def create_jovian_system() -> list[CelestialBody]:
    """
    Initialize the Jovian system with realistic orbital parameters.
    Data source: NASA JPL Horizons System (approximate values)
    
    Returns:
        List of CelestialBody objects representing the system
    """
    bodies = []
    
    # Sun (stationary at origin for simplicity)
    bodies.append(CelestialBody(
        name="Sun",
        mass=1.989e30,  # kg
        position=np.array([0.0, 0.0, 0.0]),
        velocity=np.array([0.0, 0.0, 0.0])
    ))
    
    # Jupiter (at approximately 5.2 AU from Sun)
    jupiter_dist = 5.2 * AU
    jupiter_vel = np.sqrt(G * bodies[0].mass / jupiter_dist)  # Circular orbit
    bodies.append(CelestialBody(
        name="Jupiter",
        mass=1.898e27,  # kg
        position=np.array([jupiter_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel, 0.0])
    ))
    
    # Io (innermost Galilean moon)
    io_dist = jupiter_dist + 421.7e6  # 421,700 km from Jupiter
    io_vel_rel = np.sqrt(G * bodies[1].mass / 421.7e6)
    bodies.append(CelestialBody(
        name="Io",
        mass=8.93e22,  # kg
        position=np.array([io_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel + io_vel_rel, 0.0])
    ))
    
    # Europa
    europa_dist = jupiter_dist + 671.1e6
    europa_vel_rel = np.sqrt(G * bodies[1].mass / 671.1e6)
    bodies.append(CelestialBody(
        name="Europa",
        mass=4.80e22,  # kg
        position=np.array([europa_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel + europa_vel_rel, 0.0])
    ))
    
    # Ganymede (largest moon)
    ganymede_dist = jupiter_dist + 1.070e9
    ganymede_vel_rel = np.sqrt(G * bodies[1].mass / 1.070e9)
    bodies.append(CelestialBody(
        name="Ganymede",
        mass=1.48e23,  # kg
        position=np.array([ganymede_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel + ganymede_vel_rel, 0.0])
    ))
    
    # Callisto (outermost Galilean moon)
    callisto_dist = jupiter_dist + 1.883e9
    callisto_vel_rel = np.sqrt(G * bodies[1].mass / 1.883e9)
    bodies.append(CelestialBody(
        name="Callisto",
        mass=1.08e23,  # kg
        position=np.array([callisto_dist, 0.0, 0.0]),
        velocity=np.array([0.0, jupiter_vel + callisto_vel_rel, 0.0])
    ))
    
    return bodies

def main():
    """Main entry point with command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description='N-Body Simulation of the Jovian System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Performance Evaluation:
  Use --benchmark to run a standard performance test
  Use --steps to control simulation length
  
Memory usage: ~O(n) where n is number of bodies (minimal for this system)
Expected RAM usage: < 100 MB for Jovian system
        """
    )
    
    parser.add_argument(
        '--steps', 
        type=int, 
        default=10000,
        help='Number of simulation steps (default: 10000)'
    )
    
    parser.add_argument(
        '--dt', 
        type=float, 
        default=3600.0,
        help='Time step in seconds (default: 3600 = 1 hour)'
    )
    
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmark with multiple step counts'
    )
    
    parser.add_argument(
        '--energy-check',
        action='store_true',
        help='Calculate and display system energy (slower)'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    print("Initializing Jovian System...")
    print(f"Bodies: Sun, Jupiter, Io, Europa, Ganymede, Callisto")
    print(f"Time step: {args.dt}s ({args.dt/3600:.2f} hours)")
    print("-" * 60)
    
    if args.benchmark:
        print("\n=== PERFORMANCE BENCHMARK ===\n")
        test_steps = [1000, 5000, 10000, 50000]
        
        for steps in test_steps:
            bodies = create_jovian_system()
            sim = NBodySimulator(bodies, dt=args.dt)
            
            print(f"\nRunning {steps} steps...")
            elapsed = sim.simulate(steps, progress_interval=max(1, steps // 10))
            
            steps_per_sec = steps / elapsed
            time_per_step_ms = (elapsed / steps) * 1000
            
            print(f"Results:")
            print(f"  Total time: {elapsed:.3f}s")
            print(f"  Steps/second: {steps_per_sec:.2f}")
            print(f"  Time/step: {time_per_step_ms:.4f}ms")
            print(f"  Memory efficient: O(n) storage with n=6 bodies")
    else:
        # Standard simulation run
        bodies = create_jovian_system()
        sim = NBodySimulator(bodies, dt=args.dt)
        
        if args.energy_check:
            ke0, pe0, te0 = sim.get_orbital_energy()
            print(f"Initial Energy: KE={ke0:.3e} J, PE={pe0:.3e} J, Total={te0:.3e} J\n")
        
        print(f"Running simulation for {args.steps} steps...")
        elapsed = sim.simulate(args.steps)
        
        simulated_time_days = (args.steps * args.dt) / 86400
        print(f"\nSimulation complete!")
        print(f"  Wall time: {elapsed:.3f}s")
        print(f"  Performance: {args.steps / elapsed:.2f} steps/second")
        print(f"  Simulated time: {simulated_time_days:.2f} days")
        
        if args.energy_check:
            ke1, pe1, te1 = sim.get_orbital_energy()
            energy_drift = abs((te1 - te0) / te0) * 100
            print(f"\nFinal Energy: KE={ke1:.3e} J, PE={pe1:.3e} J, Total={te1:.3e} J")
            print(f"Energy conservation error: {energy_drift:.6f}%")
        
        # Display final positions
        print(f"\nFinal positions (in AU):")
        for i, body in enumerate(bodies):
            pos_au = sim.positions[i] / AU
            print(f"  {body.name:10s}: ({pos_au[0]:8.4f}, {pos_au[1]:8.4f}, {pos_au[2]:8.4f})")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)