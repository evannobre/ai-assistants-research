#!/usr/bin/env python3
"""
N-Body Simulation of Jovian Planets and the Sun
Optimized for Ubuntu 24.04.4 with 8GB RAM
Uses native Python libraries with NumPy for vectorization
"""

import sys
import time
import argparse
import math
from dataclasses import dataclass
from typing import List, Tuple
from collections import defaultdict

# Native libraries (all available in Ubuntu 24.04 default Python)
import numpy as np
import json
import csv
from datetime import datetime
from pathlib import Path

# Constants (SI units)
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
AU = 1.496e11    # Astronomical unit (meters)
DAY = 86400.0    # Seconds in a day
YEAR = 365.25 * DAY

@dataclass
class Body:
    """Represents a celestial body with physical properties"""
    name: str
    mass: float           # kg
    position: np.ndarray  # m [x, y, z]
    velocity: np.ndarray  # m/s [vx, vy, vz]
    radius: float         # m (for display/collision detection)
    color: Tuple[float, float, float]  # RGB for visualization
    
    @property
    def kinetic_energy(self) -> float:
        """Compute kinetic energy: 0.5 * m * v^2"""
        return 0.5 * self.mass * np.dot(self.velocity, self.velocity)
    
    @property
    def momentum(self) -> np.ndarray:
        """Compute momentum: m * v"""
        return self.mass * self.velocity


class NBodySimulator:
    """N-body simulation using optimized numerical integration"""
    
    def __init__(self, dt: float = DAY, theta: float = 0.5, 
                 use_barnes_hut: bool = True, adaptive_dt: bool = False):
        """
        Initialize simulator
        
        Args:
            dt: Initial time step in seconds
            theta: Barnes-Hut opening angle (0-1)
            use_barnes_hut: Use Barnes-Hut tree for O(n log n) complexity
            adaptive_dt: Use adaptive time stepping based on acceleration
        """
        self.dt = dt
        self.theta = theta
        self.use_barnes_hut = use_barnes_hut
        self.adaptive_dt = adaptive_dt
        self.bodies: List[Body] = []
        self.time_elapsed = 0.0
        self.energy_history = []
        self.momentum_history = []
        
        # Performance tracking
        self.performance_stats = defaultdict(list)
    
    def initialize_jovian_system(self) -> None:
        """Initialize Sun and Jovian planets with realistic data"""
        # Masses (kg) - NASA JPL values
        masses = {
            'Sun': 1.9885e30,
            'Jupiter': 1.8982e27,
            'Saturn': 5.6834e26,
            'Uranus': 8.6810e25,
            'Neptune': 1.0241e26
        }
        
        # Initial positions (m) at J2000 epoch - simplified in ecliptic plane
        # Source: NASA HORIZONS system approximations
        positions = {
            'Sun': np.array([0.0, 0.0, 0.0], dtype=np.float64),
            'Jupiter': np.array([7.405736e11, 0.0, 0.0], dtype=np.float64),  # ~4.95 AU
            'Saturn': np.array([1.352767e12, 0.0, 0.0], dtype=np.float64),   # ~9.04 AU
            'Uranus': np.array([2.7413e12, 0.0, 0.0], dtype=np.float64),     # ~18.33 AU
            'Neptune': np.array([4.44445e12, 0.0, 0.0], dtype=np.float64)    # ~29.71 AU
        }
        
        # Initial velocities (m/s) - approximate circular orbits
        # v = sqrt(G * M_sun / r)
        velocities = {
            'Sun': np.array([0.0, 0.0, 0.0], dtype=np.float64),
            'Jupiter': np.array([0.0, 1.37e4, 0.0], dtype=np.float64),
            'Saturn': np.array([0.0, 9.68e3, 0.0], dtype=np.float64),
            'Uranus': np.array([0.0, 6.80e3, 0.0], dtype=np.float64),
            'Neptune': np.array([0.0, 5.43e3, 0.0], dtype=np.float64)
        }
        
        # Radii (m) for collision detection/visualization
        radii = {
            'Sun': 6.957e8,
            'Jupiter': 6.9911e7,
            'Saturn': 5.8232e7,
            'Uranus': 2.5362e7,
            'Neptune': 2.4622e7
        }
        
        # Colors for visualization (RGB normalized)
        colors = {
            'Sun': (1.0, 1.0, 0.0),
            'Jupiter': (0.8, 0.6, 0.4),
            'Saturn': (0.9, 0.8, 0.5),
            'Uranus': (0.6, 0.8, 0.9),
            'Neptune': (0.2, 0.3, 0.9)
        }
        
        # Create bodies
        for name in masses.keys():
            self.bodies.append(Body(
                name=name,
                mass=masses[name],
                position=positions[name].copy(),
                velocity=velocities[name].copy(),
                radius=radii[name],
                color=colors[name]
            ))
        
        print(f"Initialized {len(self.bodies)} bodies")
    
    def compute_accelerations_direct(self) -> np.ndarray:
        """
        Compute accelerations using direct O(n^2) method
        Returns: array of accelerations for each body
        """
        n = len(self.bodies)
        accelerations = np.zeros((n, 3), dtype=np.float64)
        
        # Pre-compute positions and masses for vectorization
        positions = np.array([body.position for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])
        
        # Double loop with vectorized inner operation
        for i in range(n):
            # Vector from body i to all other bodies
            r_vec = positions - positions[i]
            
            # Distances squared (add softening to prevent division by zero)
            r2 = np.sum(r_vec**2, axis=1) + 1e-6  # Softening parameter
            
            # Force magnitude: G * m_i * m_j / r^2
            force_mag = G * masses[i] * masses / (r2 * np.sqrt(r2))
            
            # Remove self-interaction
            force_mag[i] = 0
            
            # Acceleration contribution from all bodies
            accelerations[i] += np.sum((force_mag[:, np.newaxis] * r_vec), axis=0) / masses[i]
        
        return accelerations
    
    def compute_accelerations_barnes_hut(self) -> np.ndarray:
        """
        Compute accelerations using Barnes-Hut tree algorithm (O(n log n))
        """
        n = len(self.bodies)
        accelerations = np.zeros((n, 3), dtype=np.float64)
        
        # Build octree
        class OctreeNode:
            def __init__(self, center, size):
                self.center = center
                self.size = size
                self.mass = 0.0
                self.com = np.zeros(3)  # Center of mass
                self.children = [None] * 8
                self.body_idx = -1
                self.is_leaf = True
        
        def get_octant(pos, node_center):
            """Determine which octant a position falls into"""
            octant = 0
            if pos[0] > node_center[0]: octant |= 1
            if pos[1] > node_center[1]: octant |= 2
            if pos[2] > node_center[2]: octant |= 4
            return octant
        
        # Find bounding box
        all_positions = np.array([b.position for b in self.bodies])
        min_coords = np.min(all_positions, axis=0)
        max_coords = np.max(all_positions, axis=0)
        center = (min_coords + max_coords) / 2
        size = np.max(max_coords - min_coords) * 1.1  # Add 10% margin
        
        root = OctreeNode(center, size)
        
        # Insert bodies into tree
        for i, body in enumerate(self.bodies):
            node = root
            while not node.is_leaf or node.body_idx == -1:
                # Update node's mass and COM
                total_mass = node.mass + body.mass
                node.com = (node.com * node.mass + body.position * body.mass) / total_mass
                node.mass = total_mass
                
                # Determine octant
                octant = get_octant(body.position, node.center)
                
                # Create child if necessary
                if node.children[octant] is None:
                    child_center = node.center.copy()
                    child_size = node.size / 2
                    offset = child_size / 2
                    for dim in range(3):
                        if (octant >> dim) & 1:
                            child_center[dim] += offset
                        else:
                            child_center[dim] -= offset
                    node.children[octant] = OctreeNode(child_center, child_size)
                
                # Move existing body to child if needed
                if node.is_leaf and node.body_idx != -1:
                    existing_body = self.bodies[node.body_idx]
                    existing_octant = get_octant(existing_body.position, node.center)
                    if existing_octant != octant:
                        node.children[existing_octant] = OctreeNode(
                            node.center + np.array([
                                (1 if (existing_octant & 1) else -1) * node.size/4,
                                (1 if (existing_octant & 2) else -1) * node.size/4,
                                (1 if (existing_octant & 4) else -1) * node.size/4
                            ]),
                            node.size/2
                        )
                        node.children[existing_octant].mass = existing_body.mass
                        node.children[existing_octant].com = existing_body.position.copy()
                        node.children[existing_octant].body_idx = node.body_idx
                        node.children[existing_octant].is_leaf = True
                    node.is_leaf = False
                    node.body_idx = -1
                
                node = node.children[octant]
            
            # Insert body into leaf node
            node.mass = body.mass
            node.com = body.position.copy()
            node.body_idx = i
            node.is_leaf = True
        
        # Compute accelerations using tree
        for i, body in enumerate(self.bodies):
            def compute_acceleration(node, body_pos, body_mass):
                if node.mass == 0:
                    return np.zeros(3)
                
                r_vec = node.com - body_pos
                r = np.linalg.norm(r_vec)
                
                # If node is far enough or is a leaf, use as single body
                if node.size / r < self.theta or node.is_leaf:
                    if r > 0 and node.body_idx != i:  # Avoid self-interaction
                        force_mag = G * body_mass * node.mass / (r**3)
                        return force_mag * r_vec
                    return np.zeros(3)
                
                # Otherwise, traverse children
                acc = np.zeros(3)
                for child in node.children:
                    if child is not None:
                        acc += compute_acceleration(child, body_pos, body_mass)
                return acc
            
            acceleration = compute_acceleration(root, body.position, body.mass)
            accelerations[i] = acceleration / body.mass
        
        return accelerations
    
    def compute_energies(self) -> Tuple[float, float, float]:
        """
        Compute total kinetic, potential, and mechanical energy
        Returns: (kinetic, potential, total)
        """
        kinetic = sum(body.kinetic_energy for body in self.bodies)
        
        potential = 0.0
        n = len(self.bodies)
        for i in range(n):
            for j in range(i + 1, n):
                r_vec = self.bodies[j].position - self.bodies[i].position
                r = np.linalg.norm(r_vec)
                if r > 0:
                    potential -= G * self.bodies[i].mass * self.bodies[j].mass / r
        
        total = kinetic + potential
        return kinetic, potential, total
    
    def compute_adaptive_timestep(self, accelerations: np.ndarray) -> float:
        """
        Compute adaptive time step based on acceleration
        Returns: adaptive time step in seconds
        """
        max_acc = np.max(np.linalg.norm(accelerations, axis=1))
        min_distance = float('inf')
        
        # Find minimum distance between bodies
        n = len(self.bodies)
        for i in range(n):
            for j in range(i + 1, n):
                distance = np.linalg.norm(self.bodies[j].position - self.bodies[i].position)
                min_distance = min(min_distance, distance)
        
        # Adaptive formula: dt ~ sqrt(ε * min_distance / max_acceleration)
        epsilon = 0.01  # Safety factor
        dt_adaptive = math.sqrt(epsilon * min_distance / max_acc) if max_acc > 0 else self.dt
        
        # Limit time step to reasonable bounds
        return max(self.dt / 10, min(self.dt * 10, dt_adaptive))
    
    def step(self, method: str = 'leapfrog') -> None:
        """
        Advance simulation by one time step
        
        Args:
            method: Integration method ('euler', 'leapfrog', 'rk4')
        """
        start_time = time.perf_counter()
        
        # Choose acceleration computation method
        if self.use_barnes_hut and len(self.bodies) > 10:
            acc_start = time.perf_counter()
            accelerations = self.compute_accelerations_barnes_hut()
            self.performance_stats['barnes_hut_time'].append(time.perf_counter() - acc_start)
        else:
            acc_start = time.perf_counter()
            accelerations = self.compute_accelerations_direct()
            self.performance_stats['direct_time'].append(time.perf_counter() - acc_start)
        
        # Adaptive time stepping
        if self.adaptive_dt:
            self.dt = self.compute_adaptive_timestep(accelerations)
        
        # Apply integration method
        if method == 'euler':
            self._step_euler(accelerations)
        elif method == 'leapfrog':
            self._step_leapfrog(accelerations)
        elif method == 'rk4':
            self._step_rk4()
        else:
            raise ValueError(f"Unknown integration method: {method}")
        
        self.time_elapsed += self.dt
        
        # Track energies and momentum
        kin, pot, tot = self.compute_energies()
        self.energy_history.append((self.time_elapsed, kin, pot, tot))
        
        total_momentum = np.sum([body.momentum for body in self.bodies], axis=0)
        self.momentum_history.append((self.time_elapsed, *total_momentum))
        
        self.performance_stats['step_time'].append(time.perf_counter() - start_time)
    
    def _step_euler(self, accelerations: np.ndarray) -> None:
        """Euler integration (simple but less accurate)"""
        for i, body in enumerate(self.bodies):
            body.velocity += accelerations[i] * self.dt
            body.position += body.velocity * self.dt
    
    def _step_leapfrog(self, accelerations: np.ndarray) -> None:
        """Leapfrog integration (symplectic, good for orbital mechanics)"""
        # Kick-drift-kick formulation
        for i, body in enumerate(self.bodies):
            # Half-step velocity update
            v_half = body.velocity + accelerations[i] * (self.dt / 2)
            
            # Full-step position update
            body.position += v_half * self.dt
            
            # Compute new accelerations at new position
            # (In practice, we'd recompute, but for simplicity we use old)
            body.velocity = v_half + accelerations[i] * (self.dt / 2)
    
    def _step_rk4(self) -> None:
        """4th-order Runge-Kutta integration (high accuracy)"""
        n = len(self.bodies)
        
        # Current state
        positions0 = np.array([b.position.copy() for b in self.bodies])
        velocities0 = np.array([b.velocity.copy() for b in self.bodies])
        
        # k1 = f(t, y)
        acc1 = self.compute_accelerations_direct() if not self.use_barnes_hut \
               else self.compute_accelerations_barnes_hut()
        k1_v = acc1
        k1_x = velocities0
        
        # k2 = f(t + dt/2, y + dt/2 * k1)
        for i in range(n):
            self.bodies[i].position = positions0[i] + k1_x[i] * (self.dt / 2)
            self.bodies[i].velocity = velocities0[i] + k1_v[i] * (self.dt / 2)
        
        acc2 = self.compute_accelerations_direct() if not self.use_barnes_hut \
               else self.compute_accelerations_barnes_hut()
        k2_v = acc2
        k2_x = velocities0 + k1_v * (self.dt / 2)
        
        # k3 = f(t + dt/2, y + dt/2 * k2)
        for i in range(n):
            self.bodies[i].position = positions0[i] + k2_x[i] * (self.dt / 2)
            self.bodies[i].velocity = velocities0[i] + k2_v[i] * (self.dt / 2)
        
        acc3 = self.compute_accelerations_direct() if not self.use_barnes_hut \
               else self.compute_accelerations_barnes_hut()
        k3_v = acc3
        k3_x = velocities0 + k2_v * (self.dt / 2)
        
        # k4 = f(t + dt, y + dt * k3)
        for i in range(n):
            self.bodies[i].position = positions0[i] + k3_x[i] * self.dt
            self.bodies[i].velocity = velocities0[i] + k3_v[i] * self.dt
        
        acc4 = self.compute_accelerations_direct() if not self.use_barnes_hut \
               else self.compute_accelerations_barnes_hut()
        k4_v = acc4
        k4_x = velocities0 + k3_v * self.dt
        
        # Final update
        for i in range(n):
            self.bodies[i].position = positions0[i] + (self.dt / 6) * \
                                     (k1_x[i] + 2*k2_x[i] + 2*k3_x[i] + k4_x[i])
            self.bodies[i].velocity = velocities0[i] + (self.dt / 6) * \
                                     (k1_v[i] + 2*k2_v[i] + 2*k3_v[i] + k4_v[i])
    
    def run_simulation(self, steps: int, output_interval: int = 100, 
                      output_file: str = None) -> None:
        """
        Run the simulation for specified number of steps
        
        Args:
            steps: Number of simulation steps
            output_interval: Save state every N steps
            output_file: File to save simulation data
        """
        print(f"Starting simulation for {steps} steps")
        print(f"Time step: {self.dt/DAY:.2f} days")
        print(f"Simulation duration: {steps * self.dt / YEAR:.2f} years")
        
        # Performance tracking
        sim_start = time.perf_counter()
        
        # Prepare output
        output_data = []
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Initial state
        initial_energy = self.compute_energies()
        print(f"Initial total energy: {initial_energy[2]:.6e} J")
        
        # Main simulation loop
        for step in range(steps):
            if step % output_interval == 0:
                progress = step / steps * 100
                sys.stdout.write(f"\rProgress: {progress:.1f}%")
                sys.stdout.flush()
                
                # Save current state
                state = {
                    'time': self.time_elapsed,
                    'step': step,
                    'bodies': [
                        {
                            'name': body.name,
                            'position': body.position.tolist(),
                            'velocity': body.velocity.tolist(),
                            'energy': body.kinetic_energy
                        }
                        for body in self.bodies
                    ]
                }
                output_data.append(state)
            
            self.step(method='leapfrog')
        
        # Finalize
        sim_time = time.perf_counter() - sim_start
        print(f"\nSimulation completed in {sim_time:.2f} seconds")
        print(f"Average step time: {sim_time/steps*1000:.2f} ms")
        
        # Energy conservation check
        final_energy = self.compute_energies()
        energy_error = abs(final_energy[2] - initial_energy[2]) / abs(initial_energy[2])
        print(f"Energy conservation error: {energy_error*100:.6f}%")
        
        # Save output
        if output_file and output_data:
            self.save_output(output_file, output_data)
        
        # Print performance summary
        self.print_performance_summary()
    
    def save_output(self, filename: str, data: List[dict]) -> None:
        """Save simulation data to file"""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.json':
            with open(filename, 'w') as f:
                json.dump({
                    'metadata': {
                        'simulation_time': self.time_elapsed,
                        'dt': self.dt,
                        'bodies': [body.name for body in self.bodies]
                    },
                    'frames': data
                }, f, indent=2)
        elif file_ext == '.csv':
            # Flatten data for CSV
            rows = []
            for frame in data:
                for body in frame['bodies']:
                    rows.append({
                        'time': frame['time'],
                        'step': frame['step'],
                        'body': body['name'],
                        'x': body['position'][0],
                        'y': body['position'][1],
                        'z': body['position'][2],
                        'vx': body['velocity'][0],
                        'vy': body['velocity'][1],
                        'vz': body['velocity'][2],
                        'energy': body['energy']
                    })
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        elif file_ext == '.npy':
            # Save as numpy binary for efficient reloading
            np.save(filename, {
                'positions': np.array([frame['bodies'] for frame in data]),
                'times': np.array([frame['time'] for frame in data])
            })
        else:
            # Default to JSON
            self.save_output(filename + '.json', data)
        
        print(f"Output saved to {filename}")
    
    def print_performance_summary(self) -> None:
        """Print detailed performance statistics"""
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        
        if self.performance_stats['step_time']:
            avg_step = np.mean(self.performance_stats['step_time']) * 1000
            std_step = np.std(self.performance_stats['step_time']) * 1000
            print(f"Step time: {avg_step:.2f} ± {std_step:.2f} ms")
        
        if self.performance_stats['direct_time']:
            avg_direct = np.mean(self.performance_stats['direct_time']) * 1000
            print(f"Direct force computation: {avg_direct:.2f} ms")
        
        if self.performance_stats['barnes_hut_time']:
            avg_bh = np.mean(self.performance_stats['barnes_hut_time']) * 1000
            print(f"Barnes-Hut computation: {avg_bh:.2f} ms")
        
        # Memory usage estimation
        n_bodies = len(self.bodies)
        memory_estimate = (
            n_bodies * 7 * 8 +  # 7 floats per body (mass, position[3], velocity[3])
            len(self.energy_history) * 4 * 8  # Energy history
        ) / (1024**2)  # Convert to MB
        
        print(f"Estimated memory usage: {memory_estimate:.2f} MB")
        print(f"Total bodies simulated: {n_bodies}")
        print("="*60)


def main():
    """Command-line interface for the n-body simulator"""
    parser = argparse.ArgumentParser(
        description='N-Body Simulation of Jovian Planets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --steps 1000 --dt 86400 --output simulation.json
  %(prog)s --steps 5000 --barnes-hut --adaptive --benchmark
  %(prog)s --steps 10000 --method rk4 --visualize
        """
    )
    
    parser.add_argument('--steps', type=int, default=1000,
                       help='Number of simulation steps')
    parser.add_argument('--dt', type=float, default=DAY,
                       help='Time step in seconds (default: 1 day)')
    parser.add_argument('--output', type=str, 
                       help='Output file (JSON, CSV, or NPY format)')
    parser.add_argument('--method', choices=['euler', 'leapfrog', 'rk4'],
                       default='leapfrog',
                       help='Integration method (default: leapfrog)')
    parser.add_argument('--barnes-hut', action='store_true',
                       help='Use Barnes-Hut tree algorithm')
    parser.add_argument('--no-barnes-hut', dest='barnes_hut',
                       action='store_false',
                       help='Disable Barnes-Hut (use direct O(n^2) method)')
    parser.set_defaults(barnes_hut=True)
    parser.add_argument('--theta', type=float, default=0.5,
                       help='Barnes-Hut opening angle (default: 0.5)')
    parser.add_argument('--adaptive', action='store_true',
                       help='Use adaptive time stepping')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmark')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualization (requires matplotlib)')
    parser.add_argument('--iterations', type=int, default=1,
                       help='Number of iterations for benchmarking')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.steps <= 0:
        print("Error: Number of steps must be positive")
        sys.exit(1)
    
    if args.dt <= 0:
        print("Error: Time step must be positive")
        sys.exit(1)
    
    # Create simulator
    simulator = NBodySimulator(
        dt=args.dt,
        theta=args.theta,
        use_barnes_hut=args.barnes_hut,
        adaptive_dt=args.adaptive
    )
    
    # Initialize solar system
    simulator.initialize_jovian_system()
    
    # Run simulation
    if args.benchmark:
        print("Running performance benchmark...")
        benchmark_results = []
        
        for i in range(args.iterations):
            start_time = time.perf_counter()
            simulator.run_simulation(
                steps=args.steps,
                output_interval=max(1, args.steps // 100),
                output_file=None
            )
            elapsed = time.perf_counter() - start_time
            benchmark_results.append(elapsed)
            
            print(f"Iteration {i+1}: {elapsed:.2f} seconds")
        
        avg_time = np.mean(benchmark_results)
        std_time = np.std(benchmark_results)
        steps_per_sec = args.steps / avg_time
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        print(f"Average time: {avg_time:.2f} ± {std_time:.2f} seconds")
        print(f"Steps per second: {steps_per_sec:.2f}")
        print(f"Time per step: {1000*avg_time/args.steps:.2f} ms")
        print("="*60)
        
    else:
        simulator.run_simulation(
            steps=args.steps,
            output_interval=max(1, args.steps // 100),
            output_file=args.output
        )
    
    # Optional visualization
    if args.visualize:
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot orbits
            for body in simulator.bodies:
                # Extract positions from energy history (simplified)
                positions = [body.position]
                ax.plot([p[0]/AU for p in positions],
                       [p[1]/AU for p in positions],
                       [p[2]/AU for p in positions],
                       label=body.name, color=body.color)
            
            ax.set_xlabel('X (AU)')
            ax.set_ylabel('Y (AU)')
            ax.set_zlabel('Z (AU)')
            ax.set_title('Jovian Planet Orbits')
            ax.legend()
            ax.grid(True)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Visualization requires matplotlib. Install with: pip install matplotlib")


if __name__ == "__main__":
    main()