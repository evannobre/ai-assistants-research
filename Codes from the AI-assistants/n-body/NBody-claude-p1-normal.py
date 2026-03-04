#!/usr/bin/env python3
"""
N-Body Simulation of the Jovian System (Jupiter + Galilean Moons + Sun)
Uses vectorized NumPy operations for maximum performance with native libraries.
"""

import numpy as np
import argparse
import time
from typing import Tuple

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)

# Body data: [mass (kg), initial position (m), initial velocity (m/s)]
# Reference frame: Jupiter at origin
BODIES = {
    'Sun': {
        'mass': 1.989e30,
        'pos': np.array([-7.785e11, 0.0, 0.0]),  # ~5.2 AU from Jupiter
        'vel': np.array([0.0, -13070.0, 0.0])     # Orbital velocity
    },
    'Jupiter': {
        'mass': 1.898e27,
        'pos': np.array([0.0, 0.0, 0.0]),
        'vel': np.array([0.0, 0.0, 0.0])
    },
    'Io': {
        'mass': 8.932e22,
        'pos': np.array([4.217e8, 0.0, 0.0]),
        'vel': np.array([0.0, 17334.0, 0.0])
    },
    'Europa': {
        'mass': 4.800e22,
        'pos': np.array([6.709e8, 0.0, 0.0]),
        'vel': np.array([0.0, 13740.0, 0.0])
    },
    'Ganymede': {
        'mass': 1.482e23,
        'pos': np.array([1.070e9, 0.0, 0.0]),
        'vel': np.array([0.0, 10880.0, 0.0])
    },
    'Callisto': {
        'mass': 1.076e23,
        'pos': np.array([1.883e9, 0.0, 0.0]),
        'vel': np.array([0.0, 8204.0, 0.0])
    }
}


class NBodySimulator:
    """Vectorized n-body gravity simulator using NumPy."""
    
    def __init__(self, bodies: dict):
        """Initialize simulator with body data."""
        self.n = len(bodies)
        self.names = list(bodies.keys())
        
        # Initialize state vectors (positions, velocities, masses)
        self.masses = np.array([bodies[name]['mass'] for name in self.names])
        self.positions = np.array([bodies[name]['pos'] for name in self.names])
        self.velocities = np.array([bodies[name]['vel'] for name in self.names])
        
    def compute_accelerations(self) -> np.ndarray:
        """
        Compute gravitational accelerations using vectorized operations.
        Returns: (n, 3) array of accelerations
        """
        # Compute all pairwise displacement vectors: r_ij = r_j - r_i
        # Shape: (n, n, 3) where [i, j, :] is the vector from body i to body j
        displacements = self.positions[np.newaxis, :, :] - self.positions[:, np.newaxis, :]
        
        # Compute distances: |r_ij|
        # Add small epsilon to avoid division by zero for self-interaction
        distances = np.sqrt(np.sum(displacements**2, axis=2)) + 1e-10
        
        # Zero out self-interactions by setting diagonal to infinity
        np.fill_diagonal(distances, np.inf)
        
        # Compute force magnitudes: G * m_j / r_ij^3
        # Shape: (n, n)
        force_magnitudes = G * self.masses[np.newaxis, :] / distances**3
        
        # Compute force vectors: F_ij = (G * m_j / r_ij^3) * r_ij
        # Shape: (n, n, 3)
        forces = force_magnitudes[:, :, np.newaxis] * displacements
        
        # Sum forces from all other bodies and divide by mass for acceleration
        # Shape: (n, 3)
        accelerations = np.sum(forces, axis=1) / self.masses[:, np.newaxis]
        
        return accelerations
    
    def step_leapfrog(self, dt: float):
        """
        Advance simulation by one timestep using leapfrog integration.
        This is a symplectic integrator that conserves energy well.
        """
        # Half-step velocity update
        acc = self.compute_accelerations()
        self.velocities += 0.5 * acc * dt
        
        # Full-step position update
        self.positions += self.velocities * dt
        
        # Half-step velocity update
        acc = self.compute_accelerations()
        self.velocities += 0.5 * acc * dt
    
    def step_rk4(self, dt: float):
        """
        Advance simulation using 4th-order Runge-Kutta method.
        More accurate but slower than leapfrog.
        """
        def derivatives(pos, vel):
            """Compute derivatives for RK4."""
            old_pos = self.positions.copy()
            self.positions = pos
            acc = self.compute_accelerations()
            self.positions = old_pos
            return vel, acc
        
        # RK4 integration
        p0, v0 = self.positions, self.velocities
        
        k1v, k1a = derivatives(p0, v0)
        k2v, k2a = derivatives(p0 + 0.5*dt*k1v, v0 + 0.5*dt*k1a)
        k3v, k3a = derivatives(p0 + 0.5*dt*k2v, v0 + 0.5*dt*k2a)
        k4v, k4a = derivatives(p0 + dt*k3v, v0 + dt*k3a)
        
        self.positions += (dt/6.0) * (k1v + 2*k2v + 2*k3v + k4v)
        self.velocities += (dt/6.0) * (k1a + 2*k2a + 2*k3a + k4a)
    
    def compute_energy(self) -> Tuple[float, float, float]:
        """Compute kinetic, potential, and total energy of the system."""
        # Kinetic energy: 0.5 * m * v^2
        ke = 0.5 * np.sum(self.masses * np.sum(self.velocities**2, axis=1))
        
        # Potential energy: -G * m_i * m_j / r_ij (sum over all pairs)
        pe = 0.0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                r = np.linalg.norm(self.positions[j] - self.positions[i])
                pe -= G * self.masses[i] * self.masses[j] / r
        
        return ke, pe, ke + pe
    
    def run(self, duration: float, dt: float, method: str = 'leapfrog', 
            verbose: bool = False) -> dict:
        """
        Run simulation for specified duration.
        
        Args:
            duration: Total simulation time (seconds)
            dt: Timestep size (seconds)
            method: Integration method ('leapfrog' or 'rk4')
            verbose: Print progress updates
            
        Returns:
            Dictionary with simulation statistics
        """
        n_steps = int(duration / dt)
        
        # Choose integration method
        step_func = self.step_leapfrog if method == 'leapfrog' else self.step_rk4
        
        # Initial energy for conservation check
        _, _, initial_energy = self.compute_energy()
        
        # Run simulation
        start_time = time.perf_counter()
        
        for step in range(n_steps):
            step_func(dt)
            
            if verbose and (step + 1) % (n_steps // 10) == 0:
                progress = 100 * (step + 1) / n_steps
                elapsed = time.perf_counter() - start_time
                print(f"Progress: {progress:.0f}% | Elapsed: {elapsed:.2f}s")
        
        end_time = time.perf_counter()
        
        # Final energy for conservation check
        _, _, final_energy = self.compute_energy()
        energy_error = abs((final_energy - initial_energy) / initial_energy)
        
        return {
            'duration': duration,
            'dt': dt,
            'n_steps': n_steps,
            'n_bodies': self.n,
            'method': method,
            'wall_time': end_time - start_time,
            'steps_per_second': n_steps / (end_time - start_time),
            'initial_energy': initial_energy,
            'final_energy': final_energy,
            'energy_error': energy_error
        }


def main():
    parser = argparse.ArgumentParser(
        description='N-Body simulation of the Jovian system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 1-day simulation with default settings
  python jovian_nbody.py
  
  # Performance benchmark with different timesteps
  python jovian_nbody.py --benchmark
  
  # Long simulation with RK4 integration
  python jovian_nbody.py --duration 7 --method rk4 --verbose
        """
    )
    
    parser.add_argument('--duration', type=float, default=1.0,
                        help='Simulation duration in days (default: 1.0)')
    parser.add_argument('--dt', type=float, default=60.0,
                        help='Timestep in seconds (default: 60.0)')
    parser.add_argument('--method', choices=['leapfrog', 'rk4'], default='leapfrog',
                        help='Integration method (default: leapfrog)')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run performance benchmark with varying timesteps')
    parser.add_argument('--verbose', action='store_true',
                        help='Print progress updates during simulation')
    
    args = parser.parse_args()
    
    if args.benchmark:
        print("=" * 70)
        print("JOVIAN SYSTEM N-BODY SIMULATION - PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"Bodies: {len(BODIES)}")
        print(f"Method: {args.method}")
        print()
        
        timesteps = [120.0, 60.0, 30.0, 15.0, 10.0]
        duration = 86400.0  # 1 day in seconds
        
        for dt in timesteps:
            sim = NBodySimulator(BODIES)
            results = sim.run(duration, dt, method=args.method, verbose=False)
            
            print(f"Timestep: {dt:6.1f}s | Steps: {results['n_steps']:7d} | "
                  f"Time: {results['wall_time']:7.3f}s | "
                  f"Rate: {results['steps_per_second']:8.1f} steps/s | "
                  f"Energy err: {results['energy_error']:.2e}")
        
        print("=" * 70)
        
    else:
        print("=" * 70)
        print("JOVIAN SYSTEM N-BODY SIMULATION")
        print("=" * 70)
        
        duration_seconds = args.duration * 86400.0  # Convert days to seconds
        
        print(f"Duration: {args.duration} days ({duration_seconds:.0f} seconds)")
        print(f"Timestep: {args.dt} seconds")
        print(f"Method: {args.method}")
        print(f"Bodies: {len(BODIES)}")
        print()
        
        sim = NBodySimulator(BODIES)
        results = sim.run(duration_seconds, args.dt, method=args.method, 
                         verbose=args.verbose)
        
        print()
        print("RESULTS:")
        print(f"  Total steps: {results['n_steps']:,}")
        print(f"  Wall time: {results['wall_time']:.3f} seconds")
        print(f"  Performance: {results['steps_per_second']:.1f} steps/second")
        print(f"  Initial energy: {results['initial_energy']:.6e} J")
        print(f"  Final energy: {results['final_energy']:.6e} J")
        print(f"  Energy error: {results['energy_error']:.2e}")
        print("=" * 70)


if __name__ == '__main__':
    main()