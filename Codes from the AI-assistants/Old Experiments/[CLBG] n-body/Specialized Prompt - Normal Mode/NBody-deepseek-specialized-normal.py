import numpy as np
import sys

# Constants
SOLAR_MASS = 4 * np.pi * np.pi
DAYS_PER_YEAR = 365.24

class Body:
    def __init__(self, position, velocity, mass):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.mass = mass

class NBodySystem:
    def __init__(self, bodies):
        self.bodies = bodies
        self.num_bodies = len(bodies)
        
        # Pre-allocate arrays for efficiency
        self.positions = np.zeros((self.num_bodies, 3), dtype=np.float64)
        self.velocities = np.zeros((self.num_bodies, 3), dtype=np.float64)
        self.masses = np.zeros(self.num_bodies, dtype=np.float64)
        
        for i, body in enumerate(self.bodies):
            self.positions[i] = body.position
            self.velocities[i] = body.velocity
            self.masses[i] = body.mass
    
    def compute_forces(self):
        forces = np.zeros((self.num_bodies, 3), dtype=np.float64)
        
        for i in range(self.num_bodies):
            for j in range(i + 1, self.num_bodies):
                r = self.positions[j] - self.positions[i]
                distance = np.sqrt(np.sum(r**2))
                magnitude = (self.masses[i] * self.masses[j]) / (distance * distance * distance)
                force = magnitude * r
                
                forces[i] += force
                forces[j] -= force
        
        return forces
    
    def symplectic_euler_step(self, dt):
        forces = self.compute_forces()
        
        # Update velocities (v_{n+1} = v_n + a_n * dt)
        for i in range(self.num_bodies):
            self.velocities[i] += forces[i] / self.masses[i] * dt
        
        # Update positions (x_{n+1} = x_n + v_{n+1} * dt)
        for i in range(self.num_bodies):
            self.positions[i] += self.velocities[i] * dt
        
        # Update the body objects (for consistency)
        for i, body in enumerate(self.bodies):
            body.position = self.positions[i]
            body.velocity = self.velocities[i]
    
    def energy(self):
        kinetic = 0.0
        potential = 0.0
        
        for i in range(self.num_bodies):
            kinetic += 0.5 * self.masses[i] * np.sum(self.velocities[i]**2)
            
            for j in range(i + 1, self.num_bodies):
                r = self.positions[j] - self.positions[i]
                distance = np.sqrt(np.sum(r**2))
                potential -= (self.masses[i] * self.masses[j]) / distance
        
        return kinetic + potential
    
    def simulate(self, steps, dt):
        for _ in range(steps):
            self.symplectic_euler_step(dt)

def initialize_system():
    sun = Body(
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        SOLAR_MASS
    )
    
    jupiter = Body(
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01],
        [1.66007664274403694e-03 * DAYS_PER_YEAR, 
         7.69901118419740425e-03 * DAYS_PER_YEAR, 
         -6.90460016972063023e-05 * DAYS_PER_YEAR],
        9.54791938424326609e-04 * SOLAR_MASS
    )
    
    saturn = Body(
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01],
        [-2.76742510726862411e-03 * DAYS_PER_YEAR,
         4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR],
        2.85885980666130812e-04 * SOLAR_MASS
    )
    
    uranus = Body(
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01],
        [2.96460137564761618e-03 * DAYS_PER_YEAR,
         2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR],
        4.36624404335156298e-05 * SOLAR_MASS
    )
    
    neptune = Body(
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01],
        [2.68067772490389322e-03 * DAYS_PER_YEAR,
         1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR],
        5.15138902046611451e-05 * SOLAR_MASS
    )
    
    return NBodySystem([sun, jupiter, saturn, uranus, neptune])

def main():
    if len(sys.argv) < 2:
        print("Usage: python nbody.py <steps>")
        sys.exit(1)
    
    steps = int(sys.argv[1])
    dt = 0.01  # Time step in years
    
    system = initialize_system()
    
    print(f"Initial energy: {system.energy()}")
    
    system.simulate(steps, dt)
    
    print(f"Final energy: {system.energy()}")
    
    # Print final positions (for verification)
    for i, body in enumerate(system.bodies):
        print(f"Body {i} final position: {body.position}")

if __name__ == "__main__":
    main()