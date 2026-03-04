import numpy as np
from scipy.constants import G, astronomical_unit as AU
from scipy.integrate import solve_ivp
import multiprocessing as mp
from datetime import datetime
import pickle
import os

class NBodySimulator:
    def __init__(self):
        # Constants
        self.G = G  # gravitational constant (m^3 kg^-1 s^-2)
        self.days_to_seconds = 86400
        self.years_to_seconds = 365.25 * self.days_to_seconds
        
        # System parameters (Sun + 4 Jovian planets)
        self.bodies = ['Sun', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        self.num_bodies = len(self.bodies)
        
        # Masses (kg) - NASA planetary fact sheet values
        self.masses = np.array([
            1.9885e30,      # Sun
            1.8982e27,      # Jupiter
            5.6834e26,      # Saturn
            8.6810e25,      # Uranus
            1.0241e26        # Neptune
        ])
        
        # Initial conditions (position in m, velocity in m/s)
        # Data from JPL Horizons at J2000 epoch
        self.initial_positions = np.array([
            [0, 0, 0],                                      # Sun
            [4.8414314427 * AU, -1.1603200447 * AU, -0.1036220411 * AU],      # Jupiter
            [8.3433667182 * AU, 4.1247985644 * AU, -0.4035234171 * AU],        # Saturn
            [12.8943695628 * AU, -15.1111515359 * AU, -0.2233075789 * AU],     # Uranus
            [29.4703703709 * AU, -5.3632430029 * AU, -0.9107168024 * AU]       # Neptune
        ])
        
        self.initial_velocities = np.array([
            [0, 0, 0],                                      # Sun
            [1.6600766429e-3 * AU * self.days_to_seconds,   # Jupiter
             7.6990111846e-3 * AU * self.days_to_seconds,
             -1.6286037739e-4 * AU * self.days_to_seconds],
            [-2.7674251079e-3 * AU * self.days_to_seconds,  # Saturn
             4.9985280114e-3 * AU * self.days_to_seconds,
             2.3041729757e-5 * AU * self.days_to_seconds],
            [2.9646013753e-3 * AU * self.days_to_seconds,   # Uranus
             2.3784717399e-3 * AU * self.days_to_seconds,
             -2.9658956854e-5 * AU * self.days_to_seconds],
            [5.5102531796e-4 * AU * self.days_to_seconds,   # Neptune
             3.2170906161e-3 * AU * self.days_to_seconds,
             -7.8547054142e-5 * AU * self.days_to_seconds]
        ])
        
        # Simulation parameters
        self.timestep = 10 * self.days_to_seconds  # 10 days in seconds
        self.simulation_duration = 100 * self.years_to_seconds  # 100 years
        
        # Center of mass correction
        self._correct_center_of_mass()
        
    def _correct_center_of_mass(self):
        """Adjust initial conditions to ensure center of mass is at origin"""
        total_mass = np.sum(self.masses)
        com_pos = np.sum(self.masses[:, None] * self.initial_positions, axis=0) / total_mass
        com_vel = np.sum(self.masses[:, None] * self.initial_velocities, axis=0) / total_mass
        
        self.initial_positions -= com_pos
        self.initial_velocities -= com_vel
    
    def _calculate_accelerations(self, positions):
        """Calculate gravitational accelerations for all bodies"""
        accelerations = np.zeros((self.num_bodies, 3))
        
        # Vectorized computation of pairwise accelerations
        for i in range(self.num_bodies):
            # Vector from body i to all other bodies
            r_vectors = positions - positions[i]
            
            # Distances cubed (with softening to avoid singularities)
            distances = np.linalg.norm(r_vectors, axis=1)
            distances_cubed = distances**3 + 1e6  # Softening parameter (1km)
            
            # Acceleration contribution from each body (excluding self)
            mask = np.arange(self.num_bodies) != i
            accelerations[i] = np.sum(
                self.G * self.masses[mask, None] * r_vectors[mask] / distances_cubed[mask, None],
                axis=0
            )
        
        return accelerations
    
    def _compute_energy(self, positions, velocities):
        """Compute total energy (kinetic + potential) of the system"""
        kinetic = 0.5 * np.sum(self.masses * np.sum(velocities**2, axis=1))
        
        potential = 0
        for i in range(self.num_bodies):
            for j in range(i+1, self.num_bodies):
                r = np.linalg.norm(positions[i] - positions[j])
                potential -= self.G * self.masses[i] * self.masses[j] / r
        
        return kinetic + potential
    
    def velocity_verlet(self):
        """Velocity Verlet integration scheme"""
        # Initialize arrays
        positions = self.initial_positions.copy()
        velocities = self.initial_velocities.copy()
        
        # Initial acceleration
        accelerations = self._calculate_accelerations(positions)
        
        # Prepare storage for results
        num_steps = int(self.simulation_duration / self.timestep)
        stored_positions = np.zeros((num_steps, self.num_bodies, 3))
        stored_velocities = np.zeros((num_steps, self.num_bodies, 3))
        energies = np.zeros(num_steps)
        times = np.zeros(num_steps)
        
        # Store initial state
        stored_positions[0] = positions
        stored_velocities[0] = velocities
        energies[0] = self._compute_energy(positions, velocities)
        times[0] = 0
        
        # Main integration loop
        for step in range(1, num_steps):
            # Update positions
            positions += velocities * self.timestep + 0.5 * accelerations * self.timestep**2
            
            # Compute new accelerations
            new_accelerations = self._calculate_accelerations(positions)
            
            # Update velocities
            velocities += 0.5 * (accelerations + new_accelerations) * self.timestep
            accelerations = new_accelerations
            
            # Store results
            stored_positions[step] = positions
            stored_velocities[step] = velocities
            energies[step] = self._compute_energy(positions, velocities)
            times[step] = step * self.timestep
            
            # Progress reporting
            if step % 1000 == 0:
                print(f"Progress: {100 * step/num_steps:.1f}%")
        
        return stored_positions, stored_velocities, energies, times
    
    def run_simulation(self, method='verlet'):
        """Run the simulation with specified method"""
        start_time = datetime.now()
        print(f"Starting simulation at {start_time}")
        
        if method == 'verlet':
            positions, velocities, energies, times = self.velocity_verlet()
        else:
            # Alternative method using SciPy's ODE solver
            def derivatives(t, y):
                """ODE system for n-body problem"""
                # Reshape flat array into positions and velocities
                state = y.reshape(2, self.num_bodies, 3)
                positions, velocities = state
                
                # Compute derivatives
                dpos = velocities
                dvel = self._calculate_accelerations(positions)
                
                return np.vstack((dpos, dvel)).flatten()
            
            # Initial state
            y0 = np.vstack((self.initial_positions, self.initial_velocities)).flatten()
            
            # Time points
            t_span = (0, self.simulation_duration)
            t_eval = np.arange(0, self.simulation_duration, self.timestep)
            
            # Solve ODE
            solution = solve_ivp(derivatives, t_span, y0, t_eval=t_eval, method='DOP853', rtol=1e-10)
            
            # Process results
            num_steps = len(solution.t)
            positions = np.zeros((num_steps, self.num_bodies, 3))
            velocities = np.zeros((num_steps, self.num_bodies, 3))
            
            for i in range(num_steps):
                state = solution.y[:, i].reshape(2, self.num_bodies, 3)
                positions[i] = state[0]
                velocities[i] = state[1]
            
            # Compute energies
            energies = np.array([
                self._compute_energy(positions[i], velocities[i])
                for i in range(num_steps)
            ])
            times = solution.t
        
        end_time = datetime.now()
        print(f"Simulation completed in {end_time - start_time}")
        
        return {
            'positions': positions,
            'velocities': velocities,
            'energies': energies,
            'times': times,
            'bodies': self.bodies,
            'masses': self.masses
        }
    
    def save_results(self, results, filename):
        """Save simulation results to disk"""
        with open(filename, 'wb') as f:
            pickle.dump(results, f)
        print(f"Results saved to {filename} (size: {os.path.getsize(filename)/1e6:.2f} MB)")
    
    def visualize(self, results):
        """Simple 3D visualization using matplotlib"""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print("Visualization requires matplotlib")
            return
        
        positions = results['positions']
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        for i, body in enumerate(results['bodies']):
            ax.plot(positions[:, i, 0]/AU, positions[:, i, 1]/AU, positions[:, i, 2]/AU,
                    label=body, linewidth=1 if body == 'Sun' else 2)
        
        ax.set_xlabel('X (AU)')
        ax.set_ylabel('Y (AU)')
        ax.set_zlabel('Z (AU)')
        ax.set_title('Jovian System Orbits')
        ax.legend()
        
        # Equal aspect ratio
        max_range = np.max(np.abs(positions))/AU * 1.1
        ax.set_xlim(-max_range, max_range)
        ax.set_ylim(-max_range, max_range)
        ax.set_zlim(-max_range, max_range)
        
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    simulator = NBodySimulator()
    
    # Run simulation (choose 'verlet' or 'scipy')
    results = simulator.run_simulation(method='verlet')
    
    # Save results
    simulator.save_results(results, 'jovian_system_simulation.pkl')
    
    # Visualize
    simulator.visualize(results)