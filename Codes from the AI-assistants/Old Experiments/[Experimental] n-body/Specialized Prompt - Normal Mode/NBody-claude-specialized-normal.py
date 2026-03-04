#!/usr/bin/env python3
"""
N-Body Simulation for the Jovian System
Optimized for Ubuntu 24.10 with memory constraints (10GB SSD, 16GB RAM)
Uses Leapfrog integration scheme for numerical stability
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
from typing import Tuple, Optional
import gc

class JovianNBodySimulation:
    """
    N-Body simulation of the Jovian system using vectorized NumPy operations.
    Implements the Leapfrog integration scheme for better energy conservation.
    """
    
    # Gravitational constant (m³/kg/s²)
    G = 6.67430e-11
    
    # Astronomical Unit in meters
    AU = 1.496e11
    
    # Body data: [mass (kg), x (AU), y (AU), vx (AU/year), vy (AU/year)]
    # Data based on NASA JPL ephemeris
    BODIES = {
        'Sun': [1.989e30, 0.0, 0.0, 0.0, 0.0],
        'Jupiter': [1.898e27, 5.204, 0.0, 0.0, 2.755],
        'Io': [8.93e22, 5.204 + 0.00282, 0.0, 0.0, 2.755 + 11.86],
        'Europa': [4.80e22, 5.204 + 0.00449, 0.0, 0.0, 2.755 + 9.39],
        'Ganymede': [1.48e23, 5.204 + 0.00718, 0.0, 0.0, 2.755 + 7.33],
        'Callisto': [1.08e23, 5.204 + 0.01259, 0.0, 0.0, 2.755 + 5.51]
    }
    
    def __init__(self, dt: float = 0.001, memory_efficient: bool = True):
        """
        Initialize the simulation.
        
        Args:
            dt: Time step in years
            memory_efficient: Use memory optimization techniques
        """
        self.dt = dt
        self.memory_efficient = memory_efficient
        self.n_bodies = len(self.BODIES)
        
        # Convert time step to seconds
        self.dt_sec = dt * 365.25 * 24 * 3600
        
        # Initialize arrays
        self._initialize_arrays()
        
    def _initialize_arrays(self):
        """Initialize position, velocity, and mass arrays."""
        self.masses = np.zeros(self.n_bodies, dtype=np.float64)
        self.positions = np.zeros((self.n_bodies, 2), dtype=np.float64)
        self.velocities = np.zeros((self.n_bodies, 2), dtype=np.float64)
        
        # Load initial conditions
        for i, (name, data) in enumerate(self.BODIES.items()):
            self.masses[i] = data[0]
            self.positions[i] = [data[1] * self.AU, data[2] * self.AU]  # Convert to meters
            # Convert velocity from AU/year to m/s
            self.velocities[i] = [data[3] * self.AU / (365.25 * 24 * 3600), 
                                data[4] * self.AU / (365.25 * 24 * 3600)]
    
    def compute_forces(self) -> np.ndarray:
        """
        Compute gravitational forces using vectorized operations.
        
        Returns:
            Array of forces acting on each body
        """
        forces = np.zeros_like(self.positions)
        
        # Compute all pairwise distances and force vectors at once
        # Shape: (n_bodies, n_bodies, 2)
        r_vectors = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]
        
        # Compute distances, avoiding division by zero
        r_distances = np.linalg.norm(r_vectors, axis=2)
        
        # Prevent division by zero and self-interaction
        mask = r_distances > 0
        r_distances = np.where(mask, r_distances, 1.0)
        
        # Compute force magnitudes: F = G * m1 * m2 / r²
        # Shape: (n_bodies, n_bodies)
        force_magnitudes = (self.G * self.masses[:, np.newaxis] * self.masses[np.newaxis, :] / 
                          (r_distances ** 3))
        
        # Zero out self-interactions
        force_magnitudes = np.where(mask, force_magnitudes, 0.0)
        
        # Compute force vectors and sum over all interactions
        # Shape: (n_bodies, 2)
        forces = np.sum(force_magnitudes[:, :, np.newaxis] * r_vectors, axis=1)
        
        return forces
    
    def leapfrog_step(self):
        """
        Perform one integration step using the Leapfrog method.
        This method provides better energy conservation than Euler integration.
        """
        # Compute current forces
        forces = self.compute_forces()
        accelerations = forces / self.masses[:, np.newaxis]
        
        # Leapfrog integration
        # v(t + dt/2) = v(t) + a(t) * dt/2
        self.velocities += accelerations * (self.dt_sec / 2)
        
        # r(t + dt) = r(t) + v(t + dt/2) * dt
        self.positions += self.velocities * self.dt_sec
        
        # Compute new forces and accelerations
        forces = self.compute_forces()
        accelerations = forces / self.masses[:, np.newaxis]
        
        # v(t + dt) = v(t + dt/2) + a(t + dt) * dt/2
        self.velocities += accelerations * (self.dt_sec / 2)
    
    def compute_energy(self) -> Tuple[float, float]:
        """
        Compute total kinetic and potential energy of the system.
        
        Returns:
            Tuple of (kinetic_energy, potential_energy)
        """
        # Kinetic energy
        kinetic = 0.5 * np.sum(self.masses[:, np.newaxis] * self.velocities**2)
        
        # Potential energy
        potential = 0.0
        for i in range(self.n_bodies):
            for j in range(i + 1, self.n_bodies):
                r = np.linalg.norm(self.positions[i] - self.positions[j])
                potential -= self.G * self.masses[i] * self.masses[j] / r
        
        return kinetic, potential
    
    def run_simulation(self, n_steps: int, save_interval: int = 100) -> dict:
        """
        Run the n-body simulation for a specified number of steps.
        
        Args:
            n_steps: Number of integration steps
            save_interval: Save data every N steps (for memory efficiency)
            
        Returns:
            Dictionary containing simulation results
        """
        print(f"Running Jovian N-Body simulation for {n_steps} steps...")
        print(f"Time step: {self.dt} years ({self.dt_sec:.2e} seconds)")
        print(f"Total simulation time: {n_steps * self.dt:.2f} years")
        
        # Pre-allocate arrays for results (memory efficient)
        n_saves = n_steps // save_interval + 1
        saved_positions = np.zeros((n_saves, self.n_bodies, 2), dtype=np.float32)
        saved_energies = np.zeros((n_saves, 2), dtype=np.float32)
        saved_times = np.zeros(n_saves, dtype=np.float32)
        
        start_time = time.time()
        save_idx = 0
        
        # Save initial state
        saved_positions[0] = self.positions.copy()
        ke, pe = self.compute_energy()
        saved_energies[0] = [ke, pe]
        saved_times[0] = 0.0
        save_idx = 1
        
        # Main simulation loop
        for step in range(1, n_steps + 1):
            self.leapfrog_step()
            
            # Save data periodically
            if step % save_interval == 0 and save_idx < n_saves:
                saved_positions[save_idx] = self.positions.copy()
                ke, pe = self.compute_energy()
                saved_energies[save_idx] = [ke, pe]
                saved_times[save_idx] = step * self.dt
                save_idx += 1
                
                # Memory cleanup
                if self.memory_efficient and step % (save_interval * 10) == 0:
                    gc.collect()
            
            # Progress reporting
            if step % (n_steps // 10) == 0:
                elapsed = time.time() - start_time
                progress = step / n_steps
                eta = elapsed / progress - elapsed
                print(f"Progress: {progress*100:.1f}% | "
                      f"Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")
        
        total_time = time.time() - start_time
        print(f"Simulation completed in {total_time:.2f} seconds")
        print(f"Performance: {n_steps/total_time:.0f} steps/second")
        
        return {
            'positions': saved_positions[:save_idx],
            'energies': saved_energies[:save_idx],
            'times': saved_times[:save_idx],
            'body_names': list(self.BODIES.keys()),
            'dt': self.dt,
            'total_time': total_time
        }
    
    def create_visualization(self, results: dict, show_animation: bool = False):
        """
        Create visualization of the simulation results.
        
        Args:
            results: Results dictionary from run_simulation
            show_animation: Whether to show animated plot
        """
        positions = results['positions']
        times = results['times']
        body_names = results['body_names']
        
        # Convert positions back to AU for plotting
        positions_au = positions / self.AU
        
        plt.style.use('dark_background')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Colors for different bodies
        colors = ['yellow', 'orange', 'red', 'blue', 'green', 'purple']
        
        # Plot 1: Orbital trajectories
        ax1.set_title('Jovian System Orbits', fontsize=14, fontweight='bold')
        for i, name in enumerate(body_names):
            if name == 'Sun':
                ax1.plot(positions_au[:, i, 0], positions_au[:, i, 1], 
                        'o', color=colors[i], markersize=8, label=name)
            else:
                ax1.plot(positions_au[:, i, 0], positions_au[:, i, 1], 
                        '-', color=colors[i], linewidth=1, alpha=0.8, label=name)
                ax1.plot(positions_au[-1, i, 0], positions_au[-1, i, 1], 
                        'o', color=colors[i], markersize=4)
        
        ax1.set_xlabel('X (AU)')
        ax1.set_ylabel('Y (AU)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # Plot 2: Energy conservation
        energies = results['energies']
        total_energy = energies[:, 0] + energies[:, 1]
        energy_drift = (total_energy - total_energy[0]) / abs(total_energy[0]) * 100
        
        ax2.set_title('Energy Conservation', fontsize=14, fontweight='bold')
        ax2.plot(times, energies[:, 0], 'b-', label='Kinetic', alpha=0.8)
        ax2.plot(times, energies[:, 1], 'r-', label='Potential', alpha=0.8)
        ax2.plot(times, total_energy, 'g-', label='Total', linewidth=2)
        ax2.set_xlabel('Time (years)')
        ax2.set_ylabel('Energy (J)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Energy drift
        ax3.set_title('Energy Drift (Quality Check)', fontsize=14, fontweight='bold')
        ax3.plot(times, energy_drift, 'r-', linewidth=2)
        ax3.set_xlabel('Time (years)')
        ax3.set_ylabel('Energy Drift (%)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Distances from Jupiter
        ax4.set_title('Moon Distances from Jupiter', fontsize=14, fontweight='bold')
        jupiter_idx = body_names.index('Jupiter')
        for i, name in enumerate(body_names):
            if name not in ['Sun', 'Jupiter']:
                distances = np.linalg.norm(positions_au[:, i, :] - positions_au[:, jupiter_idx, :], axis=1)
                ax4.plot(times, distances, color=colors[i], linewidth=1, label=name)
        
        ax4.set_xlabel('Time (years)')
        ax4.set_ylabel('Distance from Jupiter (AU)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print simulation statistics
        print(f"\nSimulation Statistics:")
        print(f"Total energy drift: {energy_drift[-1]:.6f}%")
        print(f"Maximum energy drift: {np.max(np.abs(energy_drift)):.6f}%")
        print(f"Integration stability: {'Excellent' if np.max(np.abs(energy_drift)) < 0.01 else 'Good' if np.max(np.abs(energy_drift)) < 0.1 else 'Fair'}")


def main():
    """Main function to run the Jovian system simulation."""
    print("Jovian N-Body Simulation")
    print("=" * 50)
    
    # Initialize simulation with optimized parameters
    sim = JovianNBodySimulation(dt=0.0001, memory_efficient=True)  # 0.0001 years ≈ 0.876 hours
    
    # Run simulation for 12 years (approximately one Jupiter orbit)
    n_steps = 120000  # 12 years / 0.0001 years per step
    save_interval = 200  # Save every 200 steps to manage memory
    
    # Run the simulation
    results = sim.run_simulation(n_steps, save_interval)
    
    # Create visualization
    sim.create_visualization(results)
    
    # Optional: Save results to file (memory efficient format)
    # np.savez_compressed('jovian_simulation.npz', **results)
    # print("Results saved to 'jovian_simulation.npz'")


if __name__ == "__main__":
    main()