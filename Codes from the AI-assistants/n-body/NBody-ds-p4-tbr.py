#!/usr/bin/env python3
"""
N-Body Simulation with Euler's Symplectic Integrator
Optimized for performance on Ubuntu 24.04.4 with 8GB RAM
"""

import numpy as np
import sys
import time
from typing import Tuple

# Constants
SOLAR_MASS = 4.0 * np.pi * np.pi  # 39.47841760435743
DAYS_PER_YEAR = 365.24
G = 1.0  # Gravitational constant in these units

class NBodySimulation:
    def __init__(self):
        """Initialize simulation with Jovian planets and Sun"""
        # Initialize bodies: Sun, Jupiter, Saturn, Uranus, Neptune
        self.n_bodies = 5
        self.bodies = ['Sun', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        
        # Pre-allocate arrays for performance
        self.positions = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.velocities = np.zeros((self.n_bodies, 3), dtype=np.float64)
        self.masses = np.zeros(self.n_bodies, dtype=np.float64)
        
        # Sun
        self.positions[0] = [0.0, 0.0, 0.0]
        self.velocities[0] = [0.0, 0.0, 0.0]
        self.masses[0] = SOLAR_MASS
        
        # Jupiter
        self.positions[1] = [
            4.84143144246472090e+00,
            -1.16032004402742839e+00,
            -1.03622044471123109e-01
        ]
        self.velocities[1] = [
            1.66007664274403694e-03 * DAYS_PER_YEAR,
            7.69901118419740425e-03 * DAYS_PER_YEAR,
            -6.90460016972063023e-05 * DAYS_PER_YEAR
        ]
        self.masses[1] = 9.54791938424326609e-04 * SOLAR_MASS
        
        # Saturn
        self.positions[2] = [
            8.34336671824457987e+00,
            4.12479856412430479e+00,
            -4.03523417114321381e-01
        ]
        self.velocities[2] = [
            -2.76742510726862411e-03 * DAYS_PER_YEAR,
            4.99852801234917238e-03 * DAYS_PER_YEAR,
            2.30417297573763929e-05 * DAYS_PER_YEAR
        ]
        self.masses[2] = 2.85885980666130812e-04 * SOLAR_MASS
        
        # Uranus
        self.positions[3] = [
            1.28943695621391310e+01,
            -1.51111514016986312e+01,
            -2.23307578892655734e-01
        ]
        self.velocities[3] = [
            2.96460137564761618e-03 * DAYS_PER_YEAR,
            2.37847173959480950e-03 * DAYS_PER_YEAR,
            -2.96589568540237556e-05 * DAYS_PER_YEAR
        ]
        self.masses[3] = 4.36624404335156298e-05 * SOLAR_MASS
        
        # Neptune
        self.positions[4] = [
            1.53796971148509165e+01,
            -2.59193146099879641e+01,
            1.79258772950371181e-01
        ]
        self.velocities[4] = [
            2.68067772490389322e-03 * DAYS_PER_YEAR,
            1.62824170038242295e-03 * DAYS_PER_YEAR,
            -9.51592254519715870e-05 * DAYS_PER_YEAR
        ]
        self.masses[4] = 5.15138902046611451e-05 * SOLAR_MASS
        
        # Pre-compute mass products for pairwise calculations
        self.mass_matrix = np.outer(self.masses, self.masses)
        
        # Cache for acceleration calculations
        self.acceleration = np.zeros((self.n_bodies, 3), dtype=np.float64)
        
    def compute_accelerations(self):
        """Compute gravitational accelerations for all bodies using vectorized operations"""
        # Clear previous accelerations
        self.acceleration.fill(0.0)
        
        # Vectorized pairwise distance and acceleration calculation
        for i in range(self.n_bodies):
            # Calculate all position differences at once
            r_vec = self.positions - self.positions[i]
            
            # Calculate squared distances (avoid sqrt for performance)
            r_squared = np.sum(r_vec * r_vec, axis=1)
            
            # Avoid division by zero for self-interaction
            r_squared[i] = 1.0
            
            # Calculate r^(-3) using inverse square root
            # This is faster than computing r^(-3) directly
            inv_r3 = 1.0 / (r_squared * np.sqrt(r_squared))
            
            # Zero out self-interaction
            inv_r3[i] = 0.0
            
            # Vectorized acceleration calculation
            # a_i = Σ_j G * m_j * (r_j - r_i) / |r_j - r_i|^3
            self.acceleration[i] = np.sum(
                G * self.masses[:, np.newaxis] * r_vec * inv_r3[:, np.newaxis],
                axis=0
            )
    
    def euler_symplectic_step(self, dt: float):
        """
        Perform one step of Euler's symplectic (semi-implicit Euler) integrator
        v_{n+1} = v_n + a_n * dt
        r_{n+1} = r_n + v_{n+1} * dt
        """
        # Update velocities
        self.velocities += self.acceleration * dt
        
        # Update positions with new velocities
        self.positions += self.velocities * dt
    
    def compute_energy(self) -> Tuple[float, float, float]:
        """Compute kinetic and potential energy of the system"""
        # Kinetic energy: 0.5 * Σ m_i * v_i²
        v_squared = np.sum(self.velocities * self.velocities, axis=1)
        kinetic = 0.5 * np.sum(self.masses * v_squared)
        
        # Potential energy: -G * Σ_{i<j} (m_i * m_j) / |r_i - r_j|
        potential = 0.0
        for i in range(self.n_bodies):
            for j in range(i + 1, self.n_bodies):
                r_vec = self.positions[i] - self.positions[j]
                distance = np.sqrt(np.sum(r_vec * r_vec))
                if distance > 0:
                    potential -= G * self.masses[i] * self.masses[j] / distance
        
        return kinetic, potential, kinetic + potential
    
    def simulate(self, n_steps: int, dt: float = 0.01):
        """
        Run the simulation for n_steps with time step dt (in years)
        
        Args:
            n_steps: Number of integration steps
            dt: Time step in years (default: 0.01 years ≈ 3.65 days)
        """
        print(f"Starting simulation with {n_steps:,} steps")
        print(f"Time step: {dt:.6f} years")
        print(f"Total simulation time: {n_steps * dt:.2f} years")
        print(f"Number of bodies: {self.n_bodies}")
        
        # Initial energy
        kin_ini, pot_ini, tot_ini = self.compute_energy()
        print(f"\nInitial energy:")
        print(f"  Kinetic: {kin_ini:.10f}")
        print(f"  Potential: {pot_ini:.10f}")
        print(f"  Total: {tot_ini:.10f}")
        
        # Progress tracking
        progress_interval = max(1, n_steps // 20)  # 20 updates
        
        # Main simulation loop
        start_time = time.time()
        for step in range(n_steps):
            # Compute accelerations
            self.compute_accelerations()
            
            # Integration step
            self.euler_symplectic_step(dt)
            
            # Progress reporting
            if (step + 1) % progress_interval == 0:
                elapsed = time.time() - start_time
                steps_per_sec = (step + 1) / elapsed
                percent = 100.0 * (step + 1) / n_steps
                print(f"Progress: {percent:.1f}% | "
                      f"Steps/sec: {steps_per_sec:.0f} | "
                      f"Elapsed: {elapsed:.1f}s", end='\r')
        
        total_time = time.time() - start_time
        print(f"\n\nSimulation completed in {total_time:.2f} seconds")
        print(f"Average performance: {n_steps / total_time:.0f} steps/second")
        
        # Final energy
        kin_fin, pot_fin, tot_fin = self.compute_energy()
        print(f"\nFinal energy:")
        print(f"  Kinetic: {kin_fin:.10f}")
        print(f"  Potential: {pot_fin:.10f}")
        print(f"  Total: {tot_fin:.10f}")
        print(f"\nEnergy conservation (relative error): "
              f"{abs((tot_fin - tot_ini) / tot_ini):.6e}")
        
        # Memory usage information
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()
        print(f"\nMemory usage: {mem_info.rss / 1024**2:.1f} MB")
        
        return self.positions, self.velocities


def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            n_steps = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of steps: {sys.argv[1]}")
            print("Usage: python nbody.py [n_steps]")
            sys.exit(1)
    else:
        n_steps = 50000000  # Default as specified
    
    # Check if we have enough memory
    import psutil
    mem = psutil.virtual_memory()
    if mem.available < 1 * 1024**3:  # Less than 1GB available
        print("Warning: Low memory available. Consider reducing n_steps.")
    
    # Create and run simulation
    sim = NBodySimulation()
    
    # Adaptive time step based on simulation length
    # For long simulations, use a larger time step to complete in reasonable time
    dt = 0.01  # 0.01 years ≈ 3.65 days
    
    # Run simulation
    final_positions, final_velocities = sim.simulate(n_steps, dt)
    
    # Output final state
    print("\nFinal positions and velocities:")
    for i, body in enumerate(sim.bodies):
        print(f"\n{body}:")
        print(f"  Position: {final_positions[i]}")
        print(f"  Velocity: {final_velocities[i]}")
        print(f"  Mass: {sim.masses[i]:.6e}")


if __name__ == "__main__":
    # Check for required packages
    try:
        import numpy as np
        import psutil
    except ImportError as e:
        print(f"Required package missing: {e}")
        print("Install with: pip install numpy psutil")
        sys.exit(1)
    
    main()