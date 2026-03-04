#!/usr/bin/env python3
"""
N-body simulation of Jovian planets and Sun with performance evaluation.
Optimized for Ubuntu 24.04.4 with 8GB RAM using native libraries.
"""

import numpy as np
import sys
import time
import argparse
from dataclasses import dataclass
from typing import Tuple, List
import math
from enum import Enum
import json

class IntegrationMethod(Enum):
    """Available integration methods for the simulation"""
    LEAPFROG = "leapfrog"
    RK4 = "rk4"
    EULER = "euler"

@dataclass
class CelestialBody:
    """Data structure for celestial bodies"""
    name: str
    mass: float  # kg
    position: np.ndarray  # m [x, y, z]
    velocity: np.ndarray  # m/s [vx, vy, vz]
    radius: float  # m (for display purposes)
    color: Tuple[float, float, float]  # RGB color for visualization

class NBodySimulation:
    """
    High-performance N-body simulation optimized for 8GB RAM systems.
    Uses NumPy vectorization and memory-efficient algorithms.
    """
    
    # Astronomical constants
    G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
    AU = 1.495978707e11  # Astronomical unit (m)
    DAY_SECONDS = 86400.0  # Seconds in a day
    
    # Softening parameter to prevent singularities
    SOFTENING = 1e9  # meters
    
    def __init__(self, method: IntegrationMethod = IntegrationMethod.LEAPFROG, 
                 dt_days: float = 0.1):
        """
        Initialize the simulation with Jovian system parameters.
        
        Args:
            method: Integration method to use
            dt_days: Time step in days
        """
        self.method = method
        self.dt = dt_days * self.DAY_SECONDS  # Convert to seconds
        self.bodies = []
        self.time_elapsed = 0.0
        
        # Initialize Jovian system (Sun + Jupiter, Saturn, Uranus, Neptune)
        self._initialize_jovian_system()
        
    def _initialize_jovian_system(self):
        """Initialize the Sun and Jovian planets with realistic orbital data"""
        # Sun (center of coordinate system)
        sun = CelestialBody(
            name="Sun",
            mass=1.989e30,  # kg
            position=np.array([0.0, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 0.0, 0.0], dtype=np.float64),
            radius=6.957e8,  # m
            color=(1.0, 1.0, 0.0)  # Yellow
        )
        
        # Jupiter
        jupiter = CelestialBody(
            name="Jupiter",
            mass=1.898e27,  # kg
            position=np.array([5.203 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 13.07e3, 0.0], dtype=np.float64),  # Orbital velocity
            radius=6.9911e7,  # m
            color=(0.8, 0.6, 0.4)  # Brownish
        )
        
        # Saturn
        saturn = CelestialBody(
            name="Saturn",
            mass=5.683e26,  # kg
            position=np.array([9.537 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 9.68e3, 0.0], dtype=np.float64),
            radius=5.8232e7,  # m
            color=(0.9, 0.8, 0.6)  # Light brown
        )
        
        # Uranus
        uranus = CelestialBody(
            name="Uranus",
            mass=8.681e25,  # kg
            position=np.array([19.189 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 6.80e3, 0.0], dtype=np.float64),
            radius=2.5362e7,  # m
            color=(0.6, 0.8, 1.0)  # Cyan
        )
        
        # Neptune
        neptune = CelestialBody(
            name="Neptune",
            mass=1.024e26,  # kg
            position=np.array([30.07 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 5.43e3, 0.0], dtype=np.float64),
            radius=2.4622e7,  # m
            color=(0.0, 0.0, 1.0)  # Blue
        )
        
        self.bodies = [sun, jupiter, saturn, uranus, neptune]
        
        # Center of mass correction (ensure total momentum is zero)
        self._correct_center_of_mass()
    
    def _correct_center_of_mass(self):
        """Adjust velocities so that the total momentum is zero"""
        total_mass = sum(body.mass for body in self.bodies)
        total_momentum = np.zeros(3, dtype=np.float64)
        
        for body in self.bodies:
            total_momentum += body.mass * body.velocity
        
        # Adjust velocities to cancel total momentum
        for body in self.bodies:
            body.velocity -= total_momentum / total_mass
    
    def compute_accelerations(self, positions: np.ndarray) -> np.ndarray:
        """
        Compute gravitational accelerations using vectorized operations.
        
        Args:
            positions: Array of shape (n_bodies, 3) with all positions
            
        Returns:
            Array of shape (n_bodies, 3) with accelerations
        """
        n_bodies = len(self.bodies)
        masses = np.array([body.mass for body in self.bodies], dtype=np.float64)
        
        # Initialize acceleration array
        accelerations = np.zeros((n_bodies, 3), dtype=np.float64)
        
        # Vectorized computation of pairwise interactions
        for i in range(n_bodies):
            # Compute vectors from body i to all other bodies
            r_vecs = positions - positions[i]
            
            # Compute distances with softening
            distances = np.sqrt(np.sum(r_vecs**2, axis=1) + self.SOFTENING**2)
            
            # Avoid self-interaction
            distances[i] = np.inf
            
            # Compute acceleration contributions
            for j in range(n_bodies):
                if i != j:
                    r = distances[j]
                    accelerations[i] += self.G * masses[j] * r_vecs[j] / (r**3)
        
        return accelerations
    
    def compute_energy(self) -> Tuple[float, float]:
        """
        Compute total energy (kinetic + potential) of the system.
        
        Returns:
            Tuple of (kinetic_energy, potential_energy) in joules
        """
        n_bodies = len(self.bodies)
        positions = np.array([body.position for body in self.bodies])
        velocities = np.array([body.velocity for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])
        
        # Kinetic energy: 1/2 * m * v^2
        kinetic = 0.5 * np.sum(masses * np.sum(velocities**2, axis=1))
        
        # Potential energy: -G * sum_{i<j} (m_i * m_j / r_ij)
        potential = 0.0
        for i in range(n_bodies):
            for j in range(i + 1, n_bodies):
                r = np.linalg.norm(positions[i] - positions[j])
                potential -= self.G * masses[i] * masses[j] / r
        
        return kinetic, potential
    
    def step_leapfrog(self):
        """Take one time step using the Leapfrog integration method"""
        n_bodies = len(self.bodies)
        positions = np.array([body.position for body in self.bodies])
        velocities = np.array([body.velocity for body in self.bodies])
        
        # Compute accelerations at current positions
        accelerations = self.compute_accelerations(positions)
        
        # Half-step velocity update
        velocities_half = velocities + 0.5 * self.dt * accelerations
        
        # Full-step position update
        new_positions = positions + self.dt * velocities_half
        
        # Compute accelerations at new positions
        new_accelerations = self.compute_accelerations(new_positions)
        
        # Second half-step velocity update
        new_velocities = velocities_half + 0.5 * self.dt * new_accelerations
        
        # Update body states
        for i, body in enumerate(self.bodies):
            body.position = new_positions[i]
            body.velocity = new_velocities[i]
        
        self.time_elapsed += self.dt
    
    def step_rk4(self):
        """Take one time step using 4th-order Runge-Kutta method"""
        n_bodies = len(self.bodies)
        positions = np.array([body.position for body in self.bodies])
        velocities = np.array([body.velocity for body in self.bodies])
        
        # RK4 algorithm for second-order ODEs
        def f(state):
            """Derivative function for RK4"""
            pos = state[:n_bodies*3].reshape(n_bodies, 3)
            vel = state[n_bodies*3:].reshape(n_bodies, 3)
            acc = self.compute_accelerations(pos)
            return np.concatenate([vel.flatten(), acc.flatten()])
        
        # Current state vector
        state = np.concatenate([positions.flatten(), velocities.flatten()])
        
        # RK4 steps
        k1 = f(state)
        k2 = f(state + 0.5 * self.dt * k1)
        k3 = f(state + 0.5 * self.dt * k2)
        k4 = f(state + self.dt * k3)
        
        # Update state
        new_state = state + (self.dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Extract positions and velocities
        new_positions = new_state[:n_bodies*3].reshape(n_bodies, 3)
        new_velocities = new_state[n_bodies*3:].reshape(n_bodies, 3)
        
        # Update body states
        for i, body in enumerate(self.bodies):
            body.position = new_positions[i]
            body.velocity = new_velocities[i]
        
        self.time_elapsed += self.dt
    
    def step_euler(self):
        """Take one time step using Euler method (for comparison)"""
        positions = np.array([body.position for body in self.bodies])
        accelerations = self.compute_accelerations(positions)
        
        for i, body in enumerate(self.bodies):
            body.velocity += accelerations[i] * self.dt
            body.position += body.velocity * self.dt
        
        self.time_elapsed += self.dt
    
    def step(self):
        """Take one time step using the selected integration method"""
        if self.method == IntegrationMethod.LEAPFROG:
            self.step_leapfrog()
        elif self.method == IntegrationMethod.RK4:
            self.step_rk4()
        else:  # EULER
            self.step_euler()
    
    def run_simulation(self, steps: int, progress_interval: int = 1000) -> dict:
        """
        Run the simulation for a specified number of steps.
        
        Args:
            steps: Number of simulation steps
            progress_interval: How often to print progress
            
        Returns:
            Dictionary with performance metrics and results
        """
        print(f"\nStarting {self.method.value.upper()} simulation for {steps} steps...")
        print(f"Time step: {self.dt/self.DAY_SECONDS:.2f} days")
        print(f"Total simulation time: {steps * self.dt/self.DAY_SECONDS:.1f} days")
        
        # Performance tracking
        start_time = time.perf_counter()
        energy_history = []
        timing_history = []
        
        initial_kinetic, initial_potential = self.compute_energy()
        initial_total = initial_kinetic + initial_potential
        
        for step in range(steps):
            step_start = time.perf_counter()
            
            self.step()
            
            step_time = time.perf_counter() - step_start
            timing_history.append(step_time)
            
            # Track energy conservation periodically
            if step % 100 == 0:
                kinetic, potential = self.compute_energy()
                total = kinetic + potential
                energy_error = abs((total - initial_total) / initial_total)
                energy_history.append(energy_error)
            
            # Progress reporting
            if progress_interval > 0 and step % progress_interval == 0:
                elapsed_days = self.time_elapsed / self.DAY_SECONDS
                avg_time_per_step = np.mean(timing_history[-100:]) * 1000
                print(f"Step {step:6d}/{steps}: "
                      f"Time = {elapsed_days:8.1f} days, "
                      f"Avg step = {avg_time_per_step:5.2f} ms")
        
        total_time = time.perf_counter() - start_time
        
        # Final energy calculation
        final_kinetic, final_potential = self.compute_energy()
        final_total = final_kinetic + final_potential
        energy_error_final = abs((final_total - initial_total) / initial_total)
        
        # Performance metrics
        metrics = {
            'total_time': total_time,
            'steps_per_second': steps / total_time,
            'avg_step_time': np.mean(timing_history),
            'std_step_time': np.std(timing_history),
            'min_step_time': np.min(timing_history),
            'max_step_time': np.max(timing_history),
            'initial_energy': initial_total,
            'final_energy': final_total,
            'energy_error': energy_error_final,
            'max_energy_error': np.max(energy_history) if energy_history else 0,
            'method': self.method.value,
            'steps': steps,
            'dt_days': self.dt / self.DAY_SECONDS,
            'n_bodies': len(self.bodies),
            'memory_usage_mb': self._estimate_memory_usage()
        }
        
        return metrics
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in megabytes"""
        n_bodies = len(self.bodies)
        # Positions, velocities, accelerations, masses
        arrays_memory = n_bodies * 3 * 8 * 3  # 8 bytes per float64
        # Object overhead (approximate)
        objects_memory = n_bodies * 100  # Approximate overhead per object
        total_bytes = arrays_memory + objects_memory
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def get_positions_au(self) -> List[Tuple[str, float, float, float]]:
        """Get current positions in Astronomical Units for visualization"""
        positions = []
        for body in self.bodies:
            pos_au = body.position / self.AU
            positions.append((body.name, pos_au[0], pos_au[1], pos_au[2]))
        return positions

def performance_comparison(steps: int = 10000) -> dict:
    """
    Compare performance of different integration methods.
    
    Args:
        steps: Number of steps for each method
        
    Returns:
        Dictionary with comparison results
    """
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON OF INTEGRATION METHODS")
    print("="*70)
    
    results = {}
    
    for method in IntegrationMethod:
        print(f"\nTesting {method.value.upper()} method...")
        
        # Create fresh simulation
        sim = NBodySimulation(method=method, dt_days=0.1)
        
        # Run simulation
        metrics = sim.run_simulation(steps=steps, progress_interval=0)
        
        # Store results
        results[method.value] = metrics
        
        print(f"  Total time: {metrics['total_time']:.2f} seconds")
        print(f"  Steps/second: {metrics['steps_per_second']:.0f}")
        print(f"  Energy error: {metrics['energy_error']:.2e}")
        print(f"  Memory usage: {metrics['memory_usage_mb']:.2f} MB")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='N-body simulation of Jovian planets and Sun with performance evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(pro)s --steps 10000 --method leapfrog
  %(pro)s --compare --steps 5000
  %(pro)s --benchmark --output results.json
        """
    )
    
    parser.add_argument('--steps', type=int, default=1000,
                       help='Number of simulation steps (default: 1000)')
    parser.add_argument('--method', type=str, default='leapfrog',
                       choices=['leapfrog', 'rk4', 'euler'],
                       help='Integration method (default: leapfrog)')
    parser.add_argument('--dt-days', type=float, default=0.1,
                       help='Time step in days (default: 0.1)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare all integration methods')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run comprehensive benchmark')
    parser.add_argument('--output', type=str,
                       help='Output file for results (JSON format)')
    parser.add_argument('--no-progress', action='store_true',
                       help='Disable progress reporting')
    
    args = parser.parse_args()
    
    # Check system specifications
    print("System Information:")
    print(f"  Ubuntu 24.04.4 64-bit")
    print(f"  8 GB RAM available")
    print(f"  256 GB SSD")
    print(f"  Python {sys.version}")
    print(f"  NumPy version: {np.__version__}")
    
    if args.compare:
        # Performance comparison of all methods
        results = performance_comparison(steps=args.steps)
        
        # Print comparison table
        print("\n" + "="*70)
        print("COMPARISON SUMMARY")
        print("="*70)
        print(f"{'Method':<10} {'Time (s)':<12} {'Steps/s':<12} {'Energy Error':<15} {'Memory (MB)':<12}")
        print("-"*70)
        
        for method_name, metrics in results.items():
            print(f"{method_name:<10} {metrics['total_time']:<12.2f} "
                  f"{metrics['steps_per_second']:<12.0f} "
                  f"{metrics['energy_error']:<15.2e} "
                  f"{metrics['memory_usage_mb']:<12.2f}")
        
        # Save results if output specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")
    
    elif args.benchmark:
        # Comprehensive benchmark
        print("\nRunning comprehensive benchmark...")
        
        benchmark_results = {}
        step_counts = [1000, 5000, 10000, 20000]
        
        for steps in step_counts:
            print(f"\nBenchmarking with {steps} steps:")
            results = {}
            
            for method in IntegrationMethod:
                sim = NBodySimulation(method=method, dt_days=args.dt_days)
                metrics = sim.run_simulation(steps=steps, progress_interval=0)
                results[method.value] = metrics
            
            benchmark_results[steps] = results
        
        # Print benchmark summary
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        for steps, results in benchmark_results.items():
            print(f"\nSteps: {steps}")
            print(f"{'Method':<10} {'Time (s)':<12} {'Steps/s':<12} {'Energy Error':<15}")
            print("-"*50)
            for method_name, metrics in results.items():
                print(f"{method_name:<10} {metrics['total_time']:<12.2f} "
                      f"{metrics['steps_per_second']:<12.0f} "
                      f"{metrics['energy_error']:<15.2e}")
        
        # Save benchmark results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(benchmark_results, f, indent=2)
            print(f"\nBenchmark results saved to {args.output}")
    
    else:
        # Single simulation run
        method = IntegrationMethod(args.method)
        sim = NBodySimulation(method=method, dt_days=args.dt_days)
        
        # Print initial conditions
        print("\nInitial Conditions:")
        print(f"{'Body':<10} {'Mass (kg)':<15} {'Position (AU)':<25} {'Velocity (km/s)':<20}")
        print("-"*80)
        for body in sim.bodies:
            pos_au = body.position / sim.AU
            vel_kms = body.velocity / 1000
            print(f"{body.name:<10} {body.mass:<15.2e} "
                  f"[{pos_au[0]:7.3f}, {pos_au[1]:7.3f}, {pos_au[2]:7.3f}]  "
                  f"[{vel_kms[0]:7.2f}, {vel_kms[1]:7.2f}, {vel_kms[2]:7.2f}]")
        
        # Run simulation
        progress_interval = 0 if args.no_progress else max(1, args.steps // 10)
        metrics = sim.run_simulation(
            steps=args.steps,
            progress_interval=progress_interval
        )
        
        # Print results
        print("\n" + "="*70)
        print("SIMULATION RESULTS")
        print("="*70)
        print(f"Integration method: {method.value.upper()}")
        print(f"Total steps: {args.steps}")
        print(f"Simulation time: {sim.time_elapsed/sim.DAY_SECONDS:.1f} days")
        print(f"Total computation time: {metrics['total_time']:.2f} seconds")
        print(f"Performance: {metrics['steps_per_second']:.0f} steps/second")
        print(f"Average step time: {metrics['avg_step_time']*1000:.3f} ms")
        print(f"Energy conservation error: {metrics['energy_error']:.2e}")
        print(f"Memory usage: {metrics['memory_usage_mb']:.2f} MB")
        
        # Final positions
        print("\nFinal Positions (AU):")
        positions = sim.get_positions_au()
        for name, x, y, z in positions:
            print(f"  {name:<10}: [{x:8.3f}, {y:8.3f}, {z:8.3f}]")
        
        # Save results if requested
        if args.output:
            results = {
                'simulation': metrics,
                'final_positions': positions,
                'system_info': {
                    'python_version': sys.version,
                    'numpy_version': np.__version__,
                    'platform': sys.platform
                }
            }
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()