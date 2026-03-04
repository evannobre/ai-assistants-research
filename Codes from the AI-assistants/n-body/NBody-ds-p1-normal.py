import numpy as np
import time
import sys
from typing import Tuple, List, Dict
import argparse

class Body:
    """Represents a celestial body in the simulation."""
    
    def __init__(self, name: str, mass: float, position: np.ndarray, 
                 velocity: np.ndarray, radius: float = 0.0, color: str = 'white'):
        """
        Initialize a celestial body.
        
        Args:
            name: Name of the body
            mass: Mass in kg
            position: Initial position [x, y, z] in meters
            velocity: Initial velocity [vx, vy, vz] in m/s
            radius: Radius for display purposes
            color: Color for visualization
        """
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.acceleration = np.zeros(3, dtype=np.float64)
        self.radius = radius
        self.color = color
        self.position_history = []
        self.mass_history = []
        
    def update_position(self, dt: float):
        """Update position using velocity Verlet integration."""
        self.velocity += 0.5 * self.acceleration * dt
        self.position += self.velocity * dt
        
    def update_acceleration(self, acceleration: np.ndarray):
        """Update acceleration and complete velocity Verlet step."""
        self.velocity += 0.5 * acceleration * dt
        self.acceleration = acceleration


class NBodySimulation:
    """N-body simulation for Jovian system."""
    
    # Physical constants
    G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
    AU = 1.496e11    # Astronomical unit (m)
    DAY = 86400.0    # Seconds in a day
    
    def __init__(self, dt: float = 0.1, soft_factor: float = 1e-4):
        """
        Initialize the n-body simulation.
        
        Args:
            dt: Time step in days
            soft_factor: Softening parameter to prevent singularities
        """
        self.dt = dt * self.DAY  # Convert to seconds
        self.soft_factor = soft_factor
        self.bodies: List[Body] = []
        self.time_elapsed = 0.0
        self.force_calculations = 0
        
    def initialize_jovian_system(self):
        """Initialize the Sun and Jovian planets with approximate data."""
        # Sun (at center with slight motion to keep system centered)
        sun = Body(
            name="Sun",
            mass=1.989e30,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            radius=696340e3,
            color="yellow"
        )
        
        # Jupiter
        jupiter = Body(
            name="Jupiter",
            mass=1.898e27,
            position=[5.2 * self.AU, 0, 0],
            velocity=[0, 13.07e3, 0],  # Orbital velocity
            radius=69911e3,
            color="orange"
        )
        
        # Saturn
        saturn = Body(
            name="Saturn",
            mass=5.683e26,
            position=[9.58 * self.AU, 0, 0],
            velocity=[0, 9.69e3, 0],
            radius=58232e3,
            color="gold"
        )
        
        # Uranus
        uranus = Body(
            name="Uranus",
            mass=8.681e25,
            position=[19.22 * self.AU, 0, 0],
            velocity=[0, 6.81e3, 0],
            radius=25362e3,
            color="lightblue"
        )
        
        # Neptune
        neptune = Body(
            name="Neptune",
            mass=1.024e26,
            position=[30.05 * self.AU, 0, 0],
            velocity=[0, 5.43e3, 0],
            radius=24622e3,
            color="blue"
        )
        
        # Add all bodies to simulation
        self.bodies = [sun, jupiter, saturn, uranus, neptune]
        
        # Give Sun a small velocity to keep system approximately centered
        total_momentum = np.sum([b.mass * b.velocity for b in self.bodies[1:]], axis=0)
        self.bodies[0].velocity = -total_momentum / self.bodies[0].mass
        
    def calculate_accelerations(self) -> List[np.ndarray]:
        """
        Calculate gravitational accelerations for all bodies.
        Uses vectorized computation for efficiency.
        
        Returns:
            List of acceleration vectors for each body
        """
        n = len(self.bodies)
        positions = np.array([body.position for body in self.bodies])
        masses = np.array([body.mass for body in self.bodies])
        
        # Create position difference matrices
        dx = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # Shape: (n, n, 3)
        
        # Calculate distances with softening
        r_squared = np.sum(dx**2, axis=2) + self.soft_factor**2
        r = np.sqrt(r_squared)
        
        # Calculate force magnitudes (G * m_i * m_j / r^3)
        force_magnitudes = self.G * masses[:, np.newaxis] * masses[np.newaxis, :] / (r_squared * r)
        force_magnitudes[np.arange(n), np.arange(n)] = 0  # Remove self-interaction
        
        # Calculate accelerations
        accelerations = np.sum(force_magnitudes[:, :, np.newaxis] * dx, axis=1) / masses[:, np.newaxis]
        
        # Count force calculations
        self.force_calculations += n * (n - 1)
        
        return list(accelerations)
    
    def calculate_energy(self) -> Tuple[float, float, float]:
        """
        Calculate kinetic, potential, and total energy of the system.
        
        Returns:
            Tuple of (kinetic_energy, potential_energy, total_energy)
        """
        kinetic = 0.0
        potential = 0.0
        
        n = len(self.bodies)
        
        # Calculate kinetic energy
        for body in self.bodies:
            v_squared = np.dot(body.velocity, body.velocity)
            kinetic += 0.5 * body.mass * v_squared
        
        # Calculate potential energy
        for i in range(n):
            for j in range(i + 1, n):
                r_vec = self.bodies[j].position - self.bodies[i].position
                r = np.linalg.norm(r_vec)
                potential -= self.G * self.bodies[i].mass * self.bodies[j].mass / r
        
        total = kinetic + potential
        
        return kinetic, potential, total
    
    def step(self):
        """Advance the simulation by one time step using velocity Verlet."""
        # Get current accelerations
        accelerations = self.calculate_accelerations()
        
        # Update positions and velocities
        for i, body in enumerate(self.bodies):
            body.update_position(self.dt)
        
        # Calculate new accelerations at new positions
        new_accelerations = self.calculate_accelerations()
        
        # Update velocities with new accelerations
        for i, body in enumerate(self.bodies):
            body.update_acceleration(new_accelerations[i])
        
        # Update time
        self.time_elapsed += self.dt
        
        # Store history for visualization
        for body in self.bodies:
            body.position_history.append(body.position.copy())
            body.mass_history.append(body.mass)
    
    def run(self, steps: int, progress_interval: int = 1000):
        """
        Run the simulation for a specified number of steps.
        
        Args:
            steps: Number of time steps to simulate
            progress_interval: How often to print progress
        """
        start_time = time.time()
        
        print(f"Starting simulation for {steps} steps (dt = {self.dt/self.DAY:.2f} days)")
        print(f"Initial energy: {self.calculate_energy()[2]:.6e} J")
        print("-" * 50)
        
        for step in range(steps):
            self.step()
            
            if (step + 1) % progress_interval == 0:
                elapsed = time.time() - start_time
                steps_per_sec = (step + 1) / elapsed if elapsed > 0 else 0
                years = self.time_elapsed / (self.DAY * 365.25)
                
                print(f"Step {step + 1}/{steps} | "
                      f"Time: {years:.2f} years | "
                      f"Speed: {steps_per_sec:.1f} steps/sec | "
                      f"Force calcs: {self.force_calculations:,}")
        
        # Final energy calculation
        final_energy = self.calculate_energy()[2]
        print("-" * 50)
        print(f"Final energy: {final_energy:.6e} J")
        print(f"Energy conservation: {abs(initial_energy - final_energy)/initial_energy:.2e}")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        return {
            "total_steps": len(self.bodies[0].position_history) if self.bodies else 0,
            "time_elapsed_years": self.time_elapsed / (self.DAY * 365.25),
            "force_calculations": self.force_calculations,
            "bodies": len(self.bodies)
        }


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="N-body simulation of Jovian system")
    
    parser.add_argument("--steps", type=int, default=10000,
                       help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.1,
                       help="Time step in days")
    parser.add_argument("--soft", type=float, default=1e-4,
                       help="Softening parameter")
    parser.add_argument("--no-progress", action="store_true",
                       help="Disable progress updates")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run performance benchmark")
    
    return parser.parse_args()


def run_benchmark():
    """Run performance benchmark with different configurations."""
    print("=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    configs = [
        {"steps": 1000, "dt": 0.1, "bodies": 5},
        {"steps": 5000, "dt": 0.1, "bodies": 5},
        {"steps": 10000, "dt": 0.1, "bodies": 5},
    ]
    
    for config in configs:
        print(f"\nConfiguration: {config['steps']} steps, {config['bodies']} bodies")
        
        sim = NBodySimulation(dt=config["dt"])
        sim.initialize_jovian_system()
        
        start = time.perf_counter()
        sim.run(config["steps"], progress_interval=config["steps"] + 1)  # No progress
        end = time.perf_counter()
        
        elapsed = end - start
        steps_per_sec = config["steps"] / elapsed
        
        stats = sim.get_performance_stats()
        print(f"  Time: {elapsed:.3f} seconds")
        print(f"  Speed: {steps_per_sec:.1f} steps/second")
        print(f"  Force calculations/sec: {stats['force_calculations']/elapsed:,.0f}")
        print(f"  Simulated time: {stats['time_elapsed_years']:.2f} years")


def main():
    """Main function to run the simulation."""
    args = parse_arguments()
    
    if args.benchmark:
        run_benchmark()
        return
    
    # Create and run simulation
    sim = NBodySimulation(dt=args.dt, soft_factor=args.soft)
    sim.initialize_jovian_system()
    
    # Store initial energy for conservation check
    global initial_energy
    initial_energy = sim.calculate_energy()[2]
    
    # Run simulation
    progress_interval = 1000 if not args.no_progress else args.steps + 1
    sim.run(args.steps, progress_interval=progress_interval)
    
    # Print performance summary
    print("\n" + "=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    
    stats = sim.get_performance_stats()
    print(f"Total steps: {stats['total_steps']:,}")
    print(f"Simulated time: {stats['time_elapsed_years']:.2f} years")
    print(f"Total force calculations: {stats['force_calculations']:,}")
    print(f"Number of bodies: {stats['bodies']}")
    
    # Optional: Save results to file
    save_results = input("\nSave results to file? (y/n): ").lower()
    if save_results == 'y':
        import pickle
        filename = f"nbody_simulation_{int(time.time())}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(sim, f)
        print(f"Results saved to {filename}")


if __name__ == "__main__":
    # Check if NumPy is available
    try:
        import numpy as np
    except ImportError:
        print("Error: NumPy is required for this simulation.")
        print("Install it with: pip install numpy")
        sys.exit(1)
    
    main()