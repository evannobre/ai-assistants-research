#!/usr/bin/env python3
"""
N-Body Simulation of the Jovian System
Simulates Jupiter's major moons (Io, Europa, Ganymede, Callisto) and Jupiter itself orbiting the Sun.
Uses the Velocity Verlet integration method for improved energy conservation.

Usage:
    python3 jovian_nbody.py [--benchmark] [--days DAYS] [--dt TIMESTEP] [--output FILE]
"""

import numpy as np
import argparse
import time
import sys
from typing import Tuple, Optional

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
AU = 1.495978707e11  # Astronomical Unit (m)
DAY = 86400.0  # Seconds in a day

# Body data: [mass (kg), initial position (AU), initial velocity (AU/day)]
# Using simplified circular orbit approximations
BODIES = {
    'Sun': {
        'mass': 1.989e30,
        'pos': np.array([0.0, 0.0, 0.0]),
        'vel': np.array([0.0, 0.0, 0.0])
    },
    'Jupiter': {
        'mass': 1.898e27,
        'pos': np.array([5.2, 0.0, 0.0]),  # ~5.2 AU from Sun
        'vel': np.array([0.0, 2.755, 0.0])  # Orbital velocity in AU/day
    },
    'Io': {
        'mass': 8.93e22,
        'pos': np.array([5.2 + 0.002819, 0.0, 0.0]),  # Jupiter + orbital radius
        'vel': np.array([0.0, 2.755 + 11.46, 0.0])  # Jupiter vel + orbital vel
    },
    'Europa': {
        'mass': 4.80e22,
        'pos': np.array([5.2 + 0.004486, 0.0, 0.0]),
        'vel': np.array([0.0, 2.755 + 9.23, 0.0])
    },
    'Ganymede': {
        'mass': 1.48e23,
        'pos': np.array([5.2 + 0.007155, 0.0, 0.0]),
        'vel': np.array([0.0, 2.755 + 7.16, 0.0])
    },
    'Callisto': {
        'mass': 1.08e23,
        'pos': np.array([5.2 + 0.012585, 0.0, 0.0]),
        'vel': np.array([0.0, 2.755 + 5.51, 0.0])
    }
}


class NBodySimulator:
    """Efficient N-Body simulator using vectorized NumPy operations."""
    
    def __init__(self, bodies: dict):
        """Initialize simulator with body data."""
        self.n = len(bodies)
        self.names = list(bodies.keys())
        
        # Initialize state arrays (vectorized for performance)
        self.masses = np.array([bodies[name]['mass'] for name in self.names])
        self.positions = np.array([bodies[name]['pos'] * AU for name in self.names])
        self.velocities = np.array([bodies[name]['vel'] * AU / DAY for name in self.names])
        self.accelerations = np.zeros_like(self.positions)
        
        # Pre-allocate arrays to avoid repeated allocation
        self.forces = np.zeros_like(self.positions)
        
    def compute_accelerations(self) -> np.ndarray:
        """
        Compute gravitational accelerations using vectorized operations.
        Time complexity: O(n²) but vectorized for performance.
        """
        acc = np.zeros_like(self.positions)
        
        # Vectorized pairwise force calculation
        for i in range(self.n):
            # Compute displacement vectors from body i to all other bodies
            r_vec = self.positions - self.positions[i]
            
            # Compute distances (with small epsilon to avoid division by zero)
            r_mag = np.linalg.norm(r_vec, axis=1)
            r_mag[i] = 1.0  # Avoid self-interaction
            
            # Compute gravitational forces (vectorized)
            # F = G * m1 * m2 / r² in direction of r_vec
            with np.errstate(divide='ignore', invalid='ignore'):
                force_magnitudes = G * self.masses / (r_mag ** 3)
                force_magnitudes[i] = 0.0  # No self-force
            
            # Sum forces from all other bodies
            forces = force_magnitudes[:, np.newaxis] * r_vec
            acc[i] = np.sum(forces, axis=0) / self.masses[i]
        
        return acc
    
    def step_velocity_verlet(self, dt: float):
        """
        Perform one timestep using Velocity Verlet integration.
        This method provides better energy conservation than Euler or RK4 for orbital mechanics.
        
        Algorithm:
        1. x(t+dt) = x(t) + v(t)*dt + 0.5*a(t)*dt²
        2. a(t+dt) = compute_acceleration(x(t+dt))
        3. v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        """
        # Store current accelerations
        a_current = self.accelerations.copy()
        
        # Update positions
        self.positions += self.velocities * dt + 0.5 * a_current * dt * dt
        
        # Compute new accelerations
        self.accelerations = self.compute_accelerations()
        
        # Update velocities
        self.velocities += 0.5 * (a_current + self.accelerations) * dt
    
    def get_total_energy(self) -> float:
        """Calculate total energy (kinetic + potential) for conservation check."""
        # Kinetic energy
        ke = 0.5 * np.sum(self.masses * np.sum(self.velocities**2, axis=1))
        
        # Potential energy
        pe = 0.0
        for i in range(self.n):
            for j in range(i+1, self.n):
                r = np.linalg.norm(self.positions[i] - self.positions[j])
                pe -= G * self.masses[i] * self.masses[j] / r
        
        return ke + pe
    
    def simulate(self, total_days: float, dt_days: float, 
                 verbose: bool = False, output_file: Optional[str] = None):
        """
        Run the simulation for specified duration.
        
        Args:
            total_days: Total simulation time in days
            dt_days: Timestep in days
            verbose: Print progress information
            output_file: Optional file to save trajectory data
        """
        dt = dt_days * DAY  # Convert to seconds
        n_steps = int(total_days / dt_days)
        
        # Initialize accelerations
        self.accelerations = self.compute_accelerations()
        
        # Energy conservation check
        initial_energy = self.get_total_energy()
        
        if verbose:
            print(f"Starting simulation: {total_days} days, {n_steps} steps")
            print(f"Initial total energy: {initial_energy:.6e} J")
        
        # Optional trajectory storage (memory-efficient: store every nth step)
        store_interval = max(1, n_steps // 1000)  # Store max 1000 points
        trajectories = [] if output_file else None
        
        start_time = time.perf_counter()
        
        # Main simulation loop
        for step in range(n_steps):
            self.step_velocity_verlet(dt)
            
            # Store trajectory data at intervals
            if output_file and step % store_interval == 0:
                trajectories.append(self.positions.copy() / AU)  # Store in AU
            
            # Progress reporting
            if verbose and step % (n_steps // 10) == 0:
                progress = 100 * step / n_steps
                elapsed = time.perf_counter() - start_time
                print(f"Progress: {progress:.1f}% ({elapsed:.2f}s)")
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        # Final energy check
        final_energy = self.get_total_energy()
        energy_error = abs((final_energy - initial_energy) / initial_energy) * 100
        
        if verbose:
            print(f"\nSimulation complete!")
            print(f"Time elapsed: {elapsed:.4f} seconds")
            print(f"Steps per second: {n_steps/elapsed:.2f}")
            print(f"Final total energy: {final_energy:.6e} J")
            print(f"Energy conservation error: {energy_error:.6f}%")
        
        # Save trajectories if requested
        if output_file and trajectories:
            np.savez_compressed(output_file, 
                              trajectories=np.array(trajectories),
                              names=self.names,
                              days=total_days,
                              dt=dt_days)
            if verbose:
                print(f"Trajectories saved to {output_file}")
        
        return elapsed, energy_error


def benchmark_mode(days: float = 365.0, dt: float = 0.1):
    """Run benchmark with different configurations."""
    print("=" * 60)
    print("N-BODY SIMULATION BENCHMARK - JOVIAN SYSTEM")
    print("=" * 60)
    print(f"System: 6 bodies (Sun + Jupiter + 4 Galilean moons)")
    print(f"Duration: {days} days")
    print(f"Timestep: {dt} days")
    print(f"Total steps: {int(days/dt)}")
    print("=" * 60)
    
    # Memory usage estimation
    n_bodies = len(BODIES)
    n_steps = int(days / dt)
    memory_per_step = n_bodies * 3 * 8 * 3  # 3 vectors (pos, vel, acc) * 3D * 8 bytes
    total_memory_mb = (memory_per_step * n_steps) / (1024 * 1024)
    
    print(f"\nEstimated memory usage: {total_memory_mb:.2f} MB")
    
    if total_memory_mb > 1024:  # Warn if > 1GB
        print("WARNING: High memory usage. Consider reducing timesteps or duration.")
    
    print("\nInitializing simulator...")
    sim = NBodySimulator(BODIES)
    
    print("Running simulation...")
    elapsed, energy_error = sim.simulate(days, dt, verbose=True)
    
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total time: {elapsed:.4f} seconds")
    print(f"Time per step: {elapsed/n_steps*1000:.6f} ms")
    print(f"Steps per second: {n_steps/elapsed:.2f}")
    print(f"Simulated time per wall second: {days/elapsed:.2f} days/s")
    print(f"Energy conservation error: {energy_error:.6f}%")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='N-Body simulation of the Jovian system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmark with default settings (365 days)
  python3 jovian_nbody.py --benchmark
  
  # Run custom simulation
  python3 jovian_nbody.py --days 30 --dt 0.01 --output trajectories.npz
  
  # Quick performance test
  python3 jovian_nbody.py --benchmark --days 100 --dt 0.5
        """
    )
    
    parser.add_argument('--benchmark', action='store_true',
                       help='Run in benchmark mode with detailed performance metrics')
    parser.add_argument('--days', type=float, default=365.0,
                       help='Simulation duration in days (default: 365)')
    parser.add_argument('--dt', type=float, default=0.1,
                       help='Timestep in days (default: 0.1)')
    parser.add_argument('--output', type=str,
                       help='Output file for trajectory data (NPZ format)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.days <= 0 or args.dt <= 0:
        print("Error: days and dt must be positive", file=sys.stderr)
        sys.exit(1)
    
    if args.dt > args.days:
        print("Error: timestep cannot be larger than total duration", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.benchmark:
            benchmark_mode(args.days, args.dt)
        else:
            sim = NBodySimulator(BODIES)
            elapsed, energy_error = sim.simulate(args.days, args.dt, 
                                                verbose=True, 
                                                output_file=args.output)
            print(f"\nSimulation completed in {elapsed:.4f}s")
            print(f"Energy error: {energy_error:.6f}%")
    
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
