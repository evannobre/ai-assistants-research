"""
n-body simulation of Jovian planets and Sun
Usage: python nbody.py [--steps N] [--dt SECONDS] [--method METHOD] [--benchmark]
"""

import sys
import time
import argparse
import math
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from enum import Enum

class IntegrationMethod(Enum):
    LEAPFROG = "leapfrog"
    RK4 = "rk4"
    EULER = "euler"

@dataclass
class Body:
    name: str
    mass: float  # kg
    position: np.ndarray  # [x, y, z] in meters
    velocity: np.ndarray  # [vx, vy, vz] in m/s
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    radius: float = 1.0  # for visualization

class NBodySimulator:
    def __init__(self):
        # Physical constants
        self.G = 6.67430e-11  # gravitational constant (m^3 kg^-1 s^-2)
        self.AU = 1.496e11  # astronomical unit (meters)
        
        # Time parameters
        self.dt = 24 * 3600  # 1 day in seconds
        self.current_time = 0.0
        
        # Initialize celestial bodies (Sun + Jovian planets)
        self.bodies = self._initialize_solar_system()
        
        # Performance tracking
        self.force_calculations = 0
        self.start_time = 0.0
        
    def _initialize_solar_system(self) -> List[Body]:
        """Initialize Sun and Jovian planets with approximate initial conditions"""
        
        # Sun (at origin)
        sun = Body(
            name="Sun",
            mass=1.989e30,
            position=np.array([0.0, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 0.0, 0.0], dtype=np.float64),
            color=(1.0, 1.0, 0.0),
            radius=696340e3 / self.AU  # scaled radius
        )
        
        # Jupiter
        jupiter = Body(
            name="Jupiter",
            mass=1.898e27,
            position=np.array([5.2044 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 13.06e3, 0.0], dtype=np.float64),
            color=(0.8, 0.6, 0.4),
            radius=69911e3 / self.AU
        )
        
        # Saturn
        saturn = Body(
            name="Saturn",
            mass=5.683e26,
            position=np.array([9.5826 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 9.68e3, 0.0], dtype=np.float64),
            color=(0.9, 0.8, 0.5),
            radius=58232e3 / self.AU
        )
        
        # Uranus
        uranus = Body(
            name="Uranus",
            mass=8.681e25,
            position=np.array([19.2184 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 6.80e3, 0.0], dtype=np.float64),
            color=(0.6, 0.8, 1.0),
            radius=25362e3 / self.AU
        )
        
        # Neptune
        neptune = Body(
            name="Neptune",
            mass=1.024e26,
            position=np.array([30.1104 * self.AU, 0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 5.43e3, 0.0], dtype=np.float64),
            color=(0.3, 0.5, 1.0),
            radius=24622e3 / self.AU
        )
        
        return [sun, jupiter, saturn, uranus, neptune]
    
    def _compute_accelerations(self, bodies: List[Body]) -> np.ndarray:
        """Compute gravitational accelerations for all bodies (optimized)"""
        n = len(bodies)
        positions = np.array([b.position for b in bodies])
        masses = np.array([b.mass for b in bodies])
        
        # Create position difference matrices using broadcasting
        # This vectorized approach is much faster than nested loops
        dx = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # shape (n, n, 3)
        
        # Compute distances (avoid division by zero)
        r = np.sqrt(np.sum(dx**2, axis=2))
        r[r == 0] = 1.0  # to avoid division by zero for self-interaction
        
        # Compute force magnitude
        r3 = r**3
        force_magnitude = self.G * masses[np.newaxis, :] / r3  # shape (n, n)
        
        # Compute accelerations
        accelerations = np.zeros((n, 3))
        for i in range(n):
            # Skip self-interaction (diagonal elements)
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            
            if np.any(mask):
                # Vectorized computation for all interactions at once
                accel_components = dx[i, mask, :] * force_magnitude[i, mask, np.newaxis]
                accelerations[i] = np.sum(accel_components, axis=0)
        
        self.force_calculations += n * (n - 1)
        return accelerations
    
    def _leapfrog_step(self):
        """Leapfrog integration (velocity Verlet) - symplectic and energy-conserving"""
        n = len(self.bodies)
        positions = np.array([b.position for b in self.bodies])
        velocities = np.array([b.velocity for b in self.bodies])
        
        # Compute current accelerations
        acc = self._compute_accelerations(self.bodies)
        
        # Update positions (half step)
        positions += velocities * self.dt + 0.5 * acc * self.dt**2
        
        # Compute new accelerations
        # Temporarily update positions for acceleration calculation
        original_positions = [b.position.copy() for b in self.bodies]
        for i, body in enumerate(self.bodies):
            body.position = positions[i]
        
        acc_new = self._compute_accelerations(self.bodies)
        
        # Update velocities
        velocities += 0.5 * (acc + acc_new) * self.dt
        
        # Restore and set final positions/velocities
        for i, body in enumerate(self.bodies):
            body.position = positions[i]
            body.velocity = velocities[i]
            body.position = original_positions[i]  # restore for proper update
        
        self.current_time += self.dt
        
    def _rk4_step(self):
        """4th order Runge-Kutta integration (more accurate but slower)"""
        n = len(self.bodies)
        
        # Store initial state
        y0 = np.concatenate([
            np.array([b.position for b in self.bodies]).flatten(),
            np.array([b.velocity for b in self.bodies]).flatten()
        ])
        
        def f(t, y):
            """Derivative function for RK4"""
            # Unpack positions and velocities
            pos_vel = y.reshape((n, 6))
            positions = pos_vel[:, :3]
            velocities = pos_vel[:, 3:]
            
            # Temporarily update bodies
            original_states = [(b.position.copy(), b.velocity.copy()) for b in self.bodies]
            for i, body in enumerate(self.bodies):
                body.position = positions[i]
                body.velocity = velocities[i]
            
            # Compute accelerations
            accelerations = self._compute_accelerations(self.bodies)
            
            # Restore original states
            for i, (pos, vel) in enumerate(original_states):
                self.bodies[i].position = pos
                self.bodies[i].velocity = vel
            
            # Return derivatives: [velocity, acceleration]
            return np.concatenate([velocities.flatten(), accelerations.flatten()])
        
        # RK4 steps
        k1 = f(self.current_time, y0)
        k2 = f(self.current_time + self.dt/2, y0 + self.dt/2 * k1)
        k3 = f(self.current_time + self.dt/2, y0 + self.dt/2 * k2)
        k4 = f(self.current_time + self.dt, y0 + self.dt * k3)
        
        # Update
        y_new = y0 + (self.dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Update bodies
        pos_vel_new = y_new.reshape((n, 6))
        for i, body in enumerate(self.bodies):
            body.position = pos_vel_new[i, :3]
            body.velocity = pos_vel_new[i, 3:]
        
        self.current_time += self.dt
    
    def _euler_step(self):
        """Euler integration (simple but less accurate)"""
        accelerations = self._compute_accelerations(self.bodies)
        
        for i, body in enumerate(self.bodies):
            body.velocity += accelerations[i] * self.dt
            body.position += body.velocity * self.dt
        
        self.current_time += self.dt
    
    def step(self, method: IntegrationMethod = IntegrationMethod.LEAPFROG):
        """Advance simulation by one time step"""
        if method == IntegrationMethod.LEAPFROG:
            self._leapfrog_step()
        elif method == IntegrationMethod.RK4:
            self._rk4_step()
        elif method == IntegrationMethod.EULER:
            self._euler_step()
    
    def run(self, steps: int, method: IntegrationMethod = IntegrationMethod.LEAPFROG, 
            output_file: str = None):
        """Run simulation for specified number of steps"""
        print(f"Starting simulation: {steps} steps, dt={self.dt/86400:.1f} days, method={method.value}")
        print(f"Simulating: {[b.name for b in self.bodies]}")
        
        self.start_time = time.time()
        self.force_calculations = 0
        
        # Open output file if specified
        out_fh = open(output_file, 'w') if output_file else None
        if out_fh:
            out_fh.write("time,body,x,y,z,vx,vy,vz\n")
        
        try:
            for step in range(steps):
                self.step(method)
                
                # Output positions (every 10 steps for performance)
                if out_fh and step % 10 == 0:
                    for body in self.bodies:
                        pos = body.position / self.AU  # Convert to AU
                        vel = body.velocity / 1000  # Convert to km/s
                        out_fh.write(f"{self.current_time/86400:.2f},{body.name},"
                                   f"{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f},"
                                   f"{vel[0]:.6f},{vel[1]:.6f},{vel[2]:.6f}\n")
                
                # Progress indicator
                if steps > 100 and step % (steps // 10) == 0:
                    print(f"  Progress: {100*step/steps:.0f}%")
        
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        
        finally:
            if out_fh:
                out_fh.close()
        
        elapsed = time.time() - self.start_time
        self._print_performance_report(steps, elapsed)
    
    def _print_performance_report(self, steps: int, elapsed: float):
        """Print detailed performance metrics"""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        print(f"Total simulation time: {elapsed:.3f} seconds")
        print(f"Time per step: {elapsed/steps*1000:.3f} ms")
        print(f"Steps per second: {steps/elapsed:.1f}")
        print(f"Force calculations: {self.force_calculations:,}")
        print(f"Force calcs per second: {self.force_calculations/elapsed:,.0f}")
        print(f"Simulated time: {self.current_time/86400:.1f} days")
        print(f"Real-time factor: {self.current_time/elapsed:.3f}")
        
        # Memory usage (approximate)
        import os, psutil
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        print(f"Memory usage: {mem_mb:.1f} MB")
        
        # Energy conservation check
        total_energy = self._compute_total_energy()
        print(f"Total energy: {total_energy:.6e} J")
        print("="*60)
    
    def _compute_total_energy(self) -> float:
        """Compute total energy (kinetic + potential)"""
        kinetic = 0.0
        potential = 0.0
        
        for i, body1 in enumerate(self.bodies):
            kinetic += 0.5 * body1.mass * np.dot(body1.velocity, body1.velocity)
            
            for j, body2 in enumerate(self.bodies[i+1:], i+1):
                r = np.linalg.norm(body1.position - body2.position)
                potential -= self.G * body1.mass * body2.mass / r
        
        return kinetic + potential

def parse_arguments():
    parser = argparse.ArgumentParser(description='N-body simulation of Jovian planets')
    parser.add_argument('--steps', type=int, default=365, 
                       help='Number of simulation steps (default: 365)')
    parser.add_argument('--dt', type=float, default=86400,
                       help='Time step in seconds (default: 86400 = 1 day)')
    parser.add_argument('--method', type=str, default='leapfrog',
                       choices=['leapfrog', 'rk4', 'euler'],
                       help='Integration method (default: leapfrog)')
    parser.add_argument('--output', type=str, default='orbits.csv',
                       help='Output file for trajectory data')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run benchmark mode with multiple step counts')
    return parser.parse_args()

def run_benchmark(simulator):
    """Run performance benchmarks with different step counts"""
    print("Running benchmarks...")
    step_counts = [100, 1000, 10000, 50000]
    methods = [IntegrationMethod.LEAPFROG, IntegrationMethod.RK4, IntegrationMethod.EULER]
    
    results = []
    for method in methods:
        for steps in step_counts:
            # Create fresh simulator for each run
            test_sim = NBodySimulator()
            test_sim.dt = 86400
            
            start = time.time()
            test_sim.run(steps, method=method, output_file=None)
            elapsed = time.time() - start
            
            results.append({
                'method': method.value,
                'steps': steps,
                'time': elapsed,
                'steps_per_sec': steps/elapsed
            })
    
    print("\nBENCHMARK RESULTS:")
    print("Method        Steps   Time (s)   Steps/s")
    print("-" * 40)
    for r in results:
        print(f"{r['method']:12} {r['steps']:7} {r['time']:9.3f} {r['steps_per_sec']:9.1f}")

def main():
    args = parse_arguments()
    
    # Create simulator
    simulator = NBodySimulator()
    simulator.dt = args.dt
    
    # Convert method string to enum
    method_map = {
        'leapfrog': IntegrationMethod.LEAPFROG,
        'rk4': IntegrationMethod.RK4,
        'euler': IntegrationMethod.EULER
    }
    method = method_map[args.method]
    
    if args.benchmark:
        run_benchmark(simulator)
    else:
        simulator.run(args.steps, method=method, output_file=args.output)
        
        # Print final positions
        print("\nFinal positions (AU):")
        for body in simulator.bodies:
            pos_au = body.position / simulator.AU
            print(f"{body.name:10} x={pos_au[0]:8.3f} y={pos_au[1]:8.3f} z={pos_au[2]:8.3f}")

if __name__ == "__main__":
    main()