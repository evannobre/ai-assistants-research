import sys
import time
import numpy as np
from numba import jit, prange  # Optional: For JIT compilation

# Constants
SOLAR_MASS = 4 * np.pi * np.pi
DAYS_PER_YEAR = 365.24
G = 1.0

class OptimizedNBodySimulation:
    def __init__(self):
        self.num_bodies = 5
        
        # Pre-allocate all arrays
        self.positions = np.zeros((self.num_bodies, 3), dtype=np.float64)
        self.velocities = np.zeros((self.num_bodies, 3), dtype=np.float64)
        self.masses = np.zeros(self.num_bodies, dtype=np.float64)
        self.accelerations = np.zeros((self.num_bodies, 3), dtype=np.float64)
        
        self._initialize_bodies()
    
    def _initialize_bodies(self):
        """Initialize with ephemeris data."""
        # Sun
        self.positions[0] = [0.0, 0.0, 0.0]
        self.velocities[0] = [0.0, 0.0, 0.0]
        self.masses[0] = SOLAR_MASS
        
        # Jupiter
        self.positions[1] = [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01]
        self.velocities[1] = [1.66007664274403694e-03, 7.69901118419740425e-03, -6.90460016972063023e-05]
        self.velocities[1] *= DAYS_PER_YEAR
        self.masses[1] = 9.54791938424326609e-04 * SOLAR_MASS
        
        # Saturn
        self.positions[2] = [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01]
        self.velocities[2] = [-2.76742510726862411e-03, 4.99852801234917238e-03, 2.30417297573763929e-05]
        self.velocities[2] *= DAYS_PER_YEAR
        self.masses[2] = 2.85885980666130812e-04 * SOLAR_MASS
        
        # Uranus
        self.positions[3] = [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01]
        self.velocities[3] = [2.96460137564761618e-03, 2.37847173959480950e-03, -2.96589568540237556e-05]
        self.velocities[3] *= DAYS_PER_YEAR
        self.masses[3] = 4.36624404335156298e-05 * SOLAR_MASS
        
        # Neptune
        self.positions[4] = [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01]
        self.velocities[4] = [2.68067772490389322e-03, 1.62824170038242295e-03, -9.51592254519715870e-05]
        self.velocities[4] *= DAYS_PER_YEAR
        self.masses[4] = 5.15138902046611451e-05 * SOLAR_MASS
        
        # Adjust Sun's velocity for center of mass frame
        total_momentum = np.sum(self.masses[:, None] * self.velocities, axis=0)
        self.velocities[0] = -total_momentum / self.masses[0]
    
    def compute_accelerations_optimized(self):
        """Optimized acceleration computation."""
        self.accelerations.fill(0.0)
        
        # Vectorized computation using broadcasting
        for i in range(self.num_bodies):
            # Differences and distances
            dx = self.positions[i, 0] - self.positions[:, 0]
            dy = self.positions[i, 1] - self.positions[:, 1]
            dz = self.positions[i, 2] - self.positions[:, 2]
            
            # Squared distances
            dist_sq = dx*dx + dy*dy + dz*dz
            dist_sq[i] = 1.0  # Avoid self-interaction
            
            # Force magnitude: G * m / r^3
            inv_dist_cube = 1.0 / (dist_sq * np.sqrt(dist_sq))
            force_mag = G * self.masses * inv_dist_cube
            
            # Accumulate accelerations (negative sign because dx = r_i - r_j)
            self.accelerations[i, 0] = -np.sum(force_mag * dx)
            self.accelerations[i, 1] = -np.sum(force_mag * dy)
            self.accelerations[i, 2] = -np.sum(force_mag * dz)
    
    def euler_step_optimized(self, dt):
        """Optimized Euler symplectic step."""
        self.compute_accelerations_optimized()
        
        # Update velocities and positions
        self.velocities += self.accelerations * dt
        self.positions += self.velocities * dt
    
    def simulate_fast(self, n_steps, dt=0.01):
        """Fast simulation with minimal overhead."""
        start_time = time.time()
        
        for step in range(n_steps):
            self.euler_step_optimized(dt)
            
            # Progress reporting for long runs
            if (step + 1) % max(1, n_steps // 20) == 0 and n_steps > 1000:
                elapsed = time.time() - start_time
                steps_per_sec = (step + 1) / elapsed
                remaining = (n_steps - step - 1) / steps_per_sec if steps_per_sec > 0 else 0
                print(f"\rStep {step + 1}/{n_steps} ({100*(step+1)/n_steps:.1f}%) "
                      f"{steps_per_sec:.0f} steps/sec, ETA: {remaining:.0f}s", 
                      end='', flush=True)
        
        total_time = time.time() - start_time
        print(f"\n\nTotal time: {total_time:.2f}s")
        print(f"Performance: {n_steps/total_time:.0f} steps/second")
        
        return total_time


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number_of_steps>")
        print(f"Example: {sys.argv[0]} 50000000")
        sys.exit(1)
    
    n_steps = int(sys.argv[1])
    
    print(f"Starting optimized n-body simulation")
    print(f"Number of steps: {n_steps:,}")
    print(f"Number of bodies: 5")
    print(f"Integrator: Euler symplectic")
    
    simulation = OptimizedNBodySimulation()
    
    # Run simulation
    dt = 0.01  # years
    simulation.simulate_fast(n_steps, dt)


if __name__ == "__main__":
    main()