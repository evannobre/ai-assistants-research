#!/usr/bin/env python3
"""
N-Body Simulation using Symplectic Euler Integration
Optimized for performance with NumPy vectorization
"""

import numpy as np
import sys
import time
from typing import Tuple, List
import gc

# Physical constants
SOLAR_MASS = 4 * np.pi * np.pi
DAYS_PER_YEAR = 365.24

class NBodySystem:
    """
    N-Body gravitational simulation using symplectic Euler integration
    """
    
    def __init__(self):
        self.n_bodies = 5  # Sun + 4 Jovian planets
        self.dt = 0.01  # Time step
        
        # Initialize arrays for positions, velocities, and masses
        self.positions = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.velocities = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.masses = np.zeros(self.n_bodies, dtype=np.float64)
        
        # Temporary arrays for force calculations (reused to minimize allocations)
        self.forces = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.r_vec = np.zeros(3, dtype=np.float64)
        
        self._initialize_ephemeris()
        self._offset_momentum()
    
    def _initialize_ephemeris(self):
        """Initialize positions, velocities, and masses from ephemeris data"""
        
        # Sun
        self.positions[0] = np.array([0.0, 0.0, 0.0])
        self.velocities[0] = np.array([0.0, 0.0, 0.0])
        self.masses[0] = SOLAR_MASS
        
        # Jupiter
        self.positions[1] = np.array([
            4.84143144246472090e+00,
            -1.16032004402742839e+00,
            -1.03622044471123109e-01
        ])
        self.velocities[1] = np.array([
            1.66007664274403694e-03 * DAYS_PER_YEAR,
            7.69901118419740425e-03 * DAYS_PER_YEAR,
            -6.90460016972063023e-05 * DAYS_PER_YEAR
        ])
        self.masses[1] = 9.54791938424326609e-04 * SOLAR_MASS
        
        # Saturn
        self.positions[2] = np.array([
            8.34336671824457987e+00,
            4.12479856412430479e+00,
            -4.03523417114321381e-01
        ])
        self.velocities[2] = np.array([
            -2.76742510726862411e-03 * DAYS_PER_YEAR,
            4.99852801234917238e-03 * DAYS_PER_YEAR,
            2.30417297573763929e-05 * DAYS_PER_YEAR
        ])
        self.masses[2] = 2.85885980666130812e-04 * SOLAR_MASS
        
        # Uranus
        self.positions[3] = np.array([
            1.28943695621391310e+01,
            -1.51111514016986312e+01,
            -2.23307578892655734e-01
        ])
        self.velocities[3] = np.array([
            2.96460137564761618e-03 * DAYS_PER_YEAR,
            2.37847173959480950e-03 * DAYS_PER_YEAR,
            -2.96589568540237556e-05 * DAYS_PER_YEAR
        ])
        self.masses[3] = 4.36624404335156298e-05 * SOLAR_MASS
        
        # Neptune
        self.positions[4] = np.array([
            1.53796971148509165e+01,
            -2.59193146099879641e+01,
            1.79258772950371181e-01
        ])
        self.velocities[4] = np.array([
            2.68067772490389322e-03 * DAYS_PER_YEAR,
            1.62824170038242295e-03 * DAYS_PER_YEAR,
            -9.51592254519715870e-05 * DAYS_PER_YEAR
        ])
        self.masses[4] = 5.15138902046611451e-05 * SOLAR_MASS
    
    def _offset_momentum(self):
        """
        Offset the momentum of the Sun to ensure the center of mass is at rest
        This conserves momentum in the system
        """
        total_momentum = np.sum(self.masses[:, np.newaxis] * self.velocities, axis=0)
        self.velocities[0] = -total_momentum / self.masses[0]
    
    def compute_forces(self):
        """
        Compute gravitational forces between all bodies
        Uses vectorized operations for performance
        """
        self.forces.fill(0.0)
        
        # Compute pairwise forces
        for i in range(self.n_bodies):
            for j in range(i + 1, self.n_bodies):
                # Vector from i to j
                self.r_vec = self.positions[j] - self.positions[i]
                
                # Distance squared and distance
                r_squared = np.dot(self.r_vec, self.r_vec)
                r_distance = np.sqrt(r_squared)
                
                # Avoid division by zero (shouldn't happen with real data)
                if r_distance < 1e-15:
                    continue
                
                # Force magnitude: G * m1 * m2 / r^3 (G = 1 in our units)
                force_magnitude = self.masses[i] * self.masses[j] / (r_distance * r_squared)
                
                # Force vector
                force_vec = force_magnitude * self.r_vec
                
                # Apply Newton's third law
                self.forces[i] += force_vec
                self.forces[j] -= force_vec
    
    def symplectic_euler_step(self):
        """
        Perform one step of symplectic Euler integration
        
        Symplectic Euler method:
        1. Update velocities using current positions: v_{n+1} = v_n + a_n * dt
        2. Update positions using new velocities: x_{n+1} = x_n + v_{n+1} * dt
        
        This method preserves energy better than standard Euler for oscillatory systems
        """
        # Compute forces at current positions
        self.compute_forces()
        
        # Update velocities: v += F/m * dt
        accelerations = self.forces / self.masses[:, np.newaxis]
        self.velocities += accelerations * self.dt
        
        # Update positions using new velocities: x += v * dt
        self.positions += self.velocities * self.dt
    
    def compute_energy(self) -> float:
        """
        Compute total energy of the system (kinetic + potential)
        Used for energy conservation verification
        """
        # Kinetic energy: 0.5 * m * v^2
        kinetic = 0.5 * np.sum(self.masses * np.sum(self.velocities**2, axis=1))
        
        # Potential energy: -G * m1 * m2 / r
        potential = 0.0
        for i in range(self.n_bodies):
            for j in range(i + 1, self.n_bodies):
                r_vec = self.positions[j] - self.positions[i]
                r_distance = np.sqrt(np.dot(r_vec, r_vec))
                if r_distance > 1e-15:
                    potential -= self.masses[i] * self.masses[j] / r_distance
        
        return kinetic + potential
    
    def simulate(self, n_steps: int, energy_check_interval: int = 1000000):
        """
        Run the n-body simulation for n_steps
        
        Args:
            n_steps: Number of integration steps to perform
            energy_check_interval: How often to check energy conservation
        """
        print(f"Starting n-body simulation with {n_steps:,} steps")
        print(f"Time step: {self.dt}")
        print(f"Number of bodies: {self.n_bodies}")
        
        # Initial energy
        initial_energy = self.compute_energy()
        print(f"Initial energy: {initial_energy:.10e}")
        
        start_time = time.time()
        
        # Main simulation loop
        for step in range(n_steps):
            self.symplectic_euler_step()
            
            # Periodic energy conservation check and progress report
            if step % energy_check_interval == 0 and step > 0:
                current_energy = self.compute_energy()
                energy_drift = abs((current_energy - initial_energy) / initial_energy)
                elapsed = time.time() - start_time
                steps_per_sec = step / elapsed
                
                print(f"Step {step:,}: Energy drift = {energy_drift:.2e}, "
                      f"Speed = {steps_per_sec:.0f} steps/sec")
                
                # Force garbage collection to manage memory
                if step % (energy_check_interval * 5) == 0:
                    gc.collect()
        
        end_time = time.time()
        final_energy = self.compute_energy()
        
        # Final statistics
        total_time = end_time - start_time
        steps_per_second = n_steps / total_time
        energy_drift = abs((final_energy - initial_energy) / initial_energy)
        
        print(f"\nSimulation completed!")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Performance: {steps_per_second:.0f} steps/second")
        print(f"Initial energy: {initial_energy:.10e}")
        print(f"Final energy: {final_energy:.10e}")
        print(f"Energy drift: {energy_drift:.2e}")
        
        return {
            'total_time': total_time,
            'steps_per_second': steps_per_second,
            'energy_drift': energy_drift,
            'final_positions': self.positions.copy(),
            'final_velocities': self.velocities.copy()
        }

def main():
    """Main function to run the simulation"""
    
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Usage: python nbody_simulation.py <number_of_steps>")
        print("Example: python nbody_simulation.py 50000000")
        sys.exit(1)
    
    try:
        n_steps = int(sys.argv[1])
        if n_steps <= 0:
            raise ValueError("Number of steps must be positive")
    except ValueError as e:
        print(f"Error: Invalid number of steps - {e}")
        sys.exit(1)
    
    # Memory usage estimate
    estimated_memory_mb = (n_steps * 5 * 6 * 8) / (1024 * 1024)  # Rough estimate
    if estimated_memory_mb > 8000:  # Conservative limit for 16GB system
        print(f"Warning: Estimated memory usage (~{estimated_memory_mb:.0f} MB) may be high")
        print("Consider reducing the number of steps or optimizing further")
    
    # Create and run simulation
    system = NBodySystem()
    results = system.simulate(n_steps)
    
    # Optional: Print final positions
    print(f"\nFinal positions:")
    body_names = ["Sun", "Jupiter", "Saturn", "Uranus", "Neptune"]
    for i, name in enumerate(body_names):
        pos = results['final_positions'][i]
        print(f"{name}: ({pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f})")

if __name__ == "__main__":
    main()