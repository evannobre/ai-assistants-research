#!/usr/bin/env python3
"""
N-body simulation for Jovian planets and Sun using Euler's symplectic integrator.
Optimized for performance with NumPy vectorization.
"""

import sys
import time
import numpy as np
from typing import Tuple, List, Optional

# Constants
SOLAR_MASS = 4.0 * np.pi * np.pi  # ~39.47841760435743
DAYS_PER_YEAR = 365.24
G = 1.0  # Gravitational constant in astronomical units


class NBodySimulation:
    """Optimized N-body simulation using Euler's symplectic integrator."""
    
    def __init__(self, dt: float = 0.01, softener: float = 1e-4):
        """
        Initialize simulation parameters.
        
        Args:
            dt: Time step for integration
            softener: Softening parameter to avoid singularities
        """
        self.dt = dt
        self.softener = softener
        self.bodies = None
        self.masses = None
        self.n_bodies = 0
        
        # Pre-allocated arrays for performance
        self._positions = None
        self._velocities = None
        self._accelerations = None
        self._dist_vec = None
        self._dist_sq = None
        
    def initialize_solar_system(self) -> None:
        """Initialize the solar system with Sun and Jovian planets."""
        # Define initial conditions
        bodies_data = [
            # Sun
            (np.array([0.0, 0.0, 0.0], dtype=np.float64),
             np.array([0.0, 0.0, 0.0], dtype=np.float64),
             SOLAR_MASS),
            # Jupiter
            (np.array([4.84143144246472090e+00, 
                       -1.16032004402742839e+00, 
                       -1.03622044471123109e-01], dtype=np.float64),
             np.array([1.66007664274403694e-03 * DAYS_PER_YEAR,
                       7.69901118419740425e-03 * DAYS_PER_YEAR,
                       -6.90460016972063023e-05 * DAYS_PER_YEAR], dtype=np.float64),
             9.54791938424326609e-04 * SOLAR_MASS),
            # Saturn
            (np.array([8.34336671824457987e+00,
                       4.12479856412430479e+00,
                       -4.03523417114321381e-01], dtype=np.float64),
             np.array([-2.76742510726862411e-03 * DAYS_PER_YEAR,
                       4.99852801234917238e-03 * DAYS_PER_YEAR,
                       2.30417297573763929e-05 * DAYS_PER_YEAR], dtype=np.float64),
             2.85885980666130812e-04 * SOLAR_MASS),
            # Uranus
            (np.array([1.28943695621391310e+01,
                       -1.51111514016986312e+01,
                       -2.23307578892655734e-01], dtype=np.float64),
             np.array([2.96460137564761618e-03 * DAYS_PER_YEAR,
                       2.37847173959480950e-03 * DAYS_PER_YEAR,
                       -2.96589568540237556e-05 * DAYS_PER_YEAR], dtype=np.float64),
             4.36624404335156298e-05 * SOLAR_MASS),
            # Neptune
            (np.array([1.53796971148509165e+01,
                       -2.59193146099879641e+01,
                       1.79258772950371181e-01], dtype=np.float64),
             np.array([2.68067772490389322e-03 * DAYS_PER_YEAR,
                       1.62824170038242295e-03 * DAYS_PER_YEAR,
                       -9.51592254519715870e-05 * DAYS_PER_YEAR], dtype=np.float64),
             5.15138902046611451e-05 * SOLAR_MASS)
        ]
        
        self.n_bodies = len(bodies_data)
        
        # Pre-allocate arrays for vectorized operations
        self._positions = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self._velocities = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self._accelerations = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.masses = np.zeros(self.n_bodies, dtype=np.float64)
        
        # Fill arrays with initial data
        for i, (pos, vel, mass) in enumerate(bodies_data):
            self._positions[i] = pos
            self._velocities[i] = vel
            self.masses[i] = mass
            
        # Adjust Sun's velocity to center the system
        self._center_system()
        
    def _center_system(self) -> None:
        """Adjust velocities so that the total momentum is zero."""
        total_mass = np.sum(self.masses)
        momentum = np.sum(self.masses[:, np.newaxis] * self._velocities, axis=0)
        self._velocities[0] = -momentum / total_mass  # Sun gets opposite velocity
        
    def _compute_accelerations(self) -> None:
        """Compute gravitational accelerations for all bodies using vectorized operations."""
        # Reset accelerations
        self._accelerations.fill(0.0)
        
        # Vectorized computation of accelerations
        for i in range(self.n_bodies):
            # Calculate position differences between body i and all others
            diff = self._positions - self._positions[i]
            
            # Calculate squared distances with softening
            dist_sq = np.sum(diff**2, axis=1) + self.softener**2
            dist_cubed = dist_sq * np.sqrt(dist_sq)
            
            # Calculate gravitational force contributions
            force_factor = G * self.masses[i] * self.masses[:, np.newaxis] / dist_cubed[:, np.newaxis]
            
            # Sum forces on all bodies (excluding self-interaction)
            mask = np.arange(self.n_bodies) != i
            self._accelerations[mask] += force_factor[mask] * diff[mask] / self.masses[mask, np.newaxis]
        
    def step(self) -> None:
        """Perform one integration step using Euler's symplectic method."""
        # Compute accelerations at current positions
        self._compute_accelerations()
        
        # Update velocities (v = v + a * dt)
        self._velocities += self._accelerations * self.dt
        
        # Update positions (x = x + v * dt)
        self._positions += self._velocities * self.dt
        
    def energy(self) -> float:
        """Compute total energy of the system."""
        kinetic = 0.0
        potential = 0.0
        
        # Kinetic energy: 0.5 * m * v^2
        kinetic = 0.5 * np.sum(self.masses * np.sum(self._velocities**2, axis=1))
        
        # Potential energy: -G * m_i * m_j / r_ij
        for i in range(self.n_bodies):
            for j in range(i + 1, self.n_bodies):
                diff = self._positions[i] - self._positions[j]
                dist = np.sqrt(np.sum(diff**2))
                potential -= G * self.masses[i] * self.masses[j] / dist
                
        return kinetic + potential
    
    def run_simulation(self, n_steps: int, progress_interval: int = 1000000) -> Tuple[float, float]:
        """
        Run the simulation for a specified number of steps.
        
        Args:
            n_steps: Number of integration steps
            progress_interval: Interval for progress reporting
            
        Returns:
            Tuple of (final_energy, execution_time)
        """
        start_time = time.perf_counter()
        
        print(f"Starting simulation with {n_steps:,} steps...")
        initial_energy = self.energy()
        print(f"Initial energy: {initial_energy:.9f}")
        
        for step in range(n_steps):
            self.step()
            
            # Progress reporting
            if (step + 1) % progress_interval == 0:
                elapsed = time.perf_counter() - start_time
                rate = (step + 1) / elapsed
                print(f"Step {step + 1:,}/{n_steps:,} "
                      f"({(step + 1)/n_steps*100:.1f}%) - "
                      f"{rate:,.0f} steps/sec")
                
                # Memory usage monitoring
                if hasattr(self, '_positions'):
                    mem_mb = (self._positions.nbytes + 
                             self._velocities.nbytes + 
                             self._accelerations.nbytes + 
                             self.masses.nbytes) / (1024 * 1024)
                    print(f"  Memory usage: {mem_mb:.2f} MB")
        
        final_energy = self.energy()
        execution_time = time.perf_counter() - start_time
        
        print(f"\nSimulation completed in {execution_time:.2f} seconds")
        print(f"Final energy: {final_energy:.9f}")
        print(f"Energy drift: {abs(final_energy - initial_energy):.2e}")
        
        return final_energy, execution_time


def main():
    """Main entry point with command line argument parsing."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n_steps>")
        print(f"Example: {sys.argv[0]} 50000000")
        sys.exit(1)
    
    try:
        n_steps = int(sys.argv[1])
        if n_steps <= 0:
            raise ValueError("Number of steps must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Validate memory constraints (8GB RAM)
    MAX_MEMORY_MB = 8 * 1024  # 8 GB in MB
    estimated_memory_mb = (5 * 3 * 8 * 3) / (1024 * 1024)  # Rough estimate for 5 bodies
    if estimated_memory_mb > MAX_MEMORY_MB * 0.8:  # Use 80% as safety margin
        print(f"Warning: Estimated memory usage ({estimated_memory_mb:.1f} MB) "
              f"exceeds safety limit")
    
    # Configure numpy for optimal performance
    np.seterr(all='ignore')  # Ignore floating point warnings
    np.set_printoptions(precision=6, suppress=True)
    
    # Create and run simulation
    print("=" * 60)
    print("N-Body Simulation - Jovian Planets and Sun")
    print("=" * 60)
    
    # Optimize time step based on simulation size
    # Smaller dt for large simulations to maintain stability
    dt = 0.001 if n_steps > 10000000 else 0.01
    
    sim = NBodySimulation(dt=dt, softener=1e-4)
    sim.initialize_solar_system()
    
    final_energy, exec_time = sim.run_simulation(n_steps)
    
    # Performance metrics
    steps_per_sec = n_steps / exec_time
    print(f"\nPerformance: {steps_per_sec:,.0f} steps/second")
    print(f"Time per step: {exec_time/n_steps*1e6:.2f} microseconds")
    
    # Display final positions and velocities
    print("\nFinal positions (AU):")
    for i, pos in enumerate(sim._positions):
        print(f"  Body {i}: [{pos[0]:12.6f}, {pos[1]:12.6f}, {pos[2]:12.6f}]")
    
    print("\nFinal velocities (AU/year):")
    for i, vel in enumerate(sim._velocities):
        print(f"  Body {i}: [{vel[0]:12.6f}, {vel[1]:12.6f}, {vel[2]:12.6f}]")


if __name__ == "__main__":
    main()