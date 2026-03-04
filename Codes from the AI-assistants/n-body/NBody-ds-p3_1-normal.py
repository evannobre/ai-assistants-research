import sys
import time
import numpy as np

# Constants
SOLAR_MASS = 4 * np.pi * np.pi
DAYS_PER_YEAR = 365.24
G = 1.0  # Gravitational constant in these units

class NBodySimulation:
    def __init__(self):
        # Initialize celestial bodies: [Sun, Jupiter, Saturn, Uranus, Neptune]
        self.num_bodies = 5
        
        # Positions (x, y, z) for each body
        self.positions = np.zeros((self.num_bodies, 3), dtype=np.float64)
        
        # Velocities (vx, vy, vz) for each body
        self.velocities = np.zeros((self.num_bodies, 3), dtype=np.float64)
        
        # Masses for each body
        self.masses = np.zeros(self.num_bodies, dtype=np.float64)
        
        # Initialize from ephemeris data
        self._initialize_bodies()
        
    def _initialize_bodies(self):
        """Initialize positions, velocities, and masses from the ephemeris data."""
        
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
        
        # Adjust Sun's velocity to conserve momentum (center of mass frame)
        total_momentum = np.sum(self.masses[:, np.newaxis] * self.velocities, axis=0)
        self.velocities[0] = -total_momentum / self.masses[0]
    
    def compute_accelerations(self):
        """Compute gravitational accelerations for all bodies using pairwise interactions."""
        accelerations = np.zeros((self.num_bodies, 3), dtype=np.float64)
        
        # Vectorized computation of all pairwise interactions
        for i in range(self.num_bodies):
            # Calculate differences in position
            delta_pos = self.positions - self.positions[i]
            
            # Calculate squared distances
            dist_sq = np.sum(delta_pos**2, axis=1)
            
            # Avoid division by zero for self-interaction
            dist_sq[i] = 1.0
            
            # Calculate distances
            dist = np.sqrt(dist_sq)
            
            # Calculate force magnitude: G * m_j / r^3
            force_mag = G * self.masses / (dist_sq * dist)
            
            # Sum accelerations from all other bodies
            # (Force on i from j is m_j * (r_j - r_i) / r^3)
            accelerations[i] = np.sum(force_mag[:, np.newaxis] * delta_pos, axis=0)
        
        return accelerations
    
    def euler_symplectic_step(self, dt):
        """Perform one step of Euler's symplectic integrator."""
        # Compute accelerations at current positions
        accelerations = self.compute_accelerations()
        
        # Update velocities: v_{n+1} = v_n + a_n * dt
        self.velocities += accelerations * dt
        
        # Update positions: x_{n+1} = x_n + v_{n+1} * dt
        self.positions += self.velocities * dt
    
    def compute_energy(self):
        """Compute total energy of the system (kinetic + potential)."""
        kinetic = 0.5 * np.sum(self.masses * np.sum(self.velocities**2, axis=1))
        
        potential = 0.0
        for i in range(self.num_bodies):
            for j in range(i + 1, self.num_bodies):
                delta_pos = self.positions[j] - self.positions[i]
                distance = np.sqrt(np.sum(delta_pos**2))
                potential -= G * self.masses[i] * self.masses[j] / distance
        
        return kinetic + potential
    
    def simulate(self, n_steps, dt=0.01):
        """Run the n-body simulation for n_steps with timestep dt."""
        start_time = time.time()
        
        for step in range(n_steps):
            self.euler_symplectic_step(dt)
            
            # Optional: Print progress for long runs
            if (step + 1) % (n_steps // 10) == 0 and n_steps >= 10:
                elapsed = time.time() - start_time
                print(f"Step {step + 1}/{n_steps} ({100*(step+1)/n_steps:.1f}%) "
                      f"Elapsed: {elapsed:.2f}s", flush=True)
        
        total_time = time.time() - start_time
        print(f"\nSimulation completed in {total_time:.2f} seconds")
        print(f"Final total energy: {self.compute_energy():.6f}")
        print(f"Average time per step: {total_time/n_steps*1e6:.2f} microseconds")
        
        return total_time


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number_of_steps>")
        print(f"Example: {sys.argv[0]} 50000000")
        sys.exit(1)
    
    try:
        n_steps = int(sys.argv[1])
        if n_steps <= 0:
            raise ValueError
    except ValueError:
        print("Error: Number of steps must be a positive integer")
        sys.exit(1)
    
    print(f"Starting n-body simulation with {n_steps} steps")
    print(f"Bodies: Sun, Jupiter, Saturn, Uranus, Neptune")
    
    # Create simulation
    simulation = NBodySimulation()
    
    # Compute initial energy
    initial_energy = simulation.compute_energy()
    print(f"Initial total energy: {initial_energy:.6f}")
    
    # Set timestep (small enough for stability with Euler's method)
    dt = 0.01  # years
    
    # Run simulation
    simulation.simulate(n_steps, dt)


if __name__ == "__main__":
    main()