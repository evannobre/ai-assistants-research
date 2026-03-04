import math
import sys

# Constants
SOLAR_MASS = 4 * math.pi * math.pi
DAYS_PER_YEAR = 365.24

# Body data structure
class Body:
    def __init__(self, position, velocity, mass):
        self.x, self.y, self.z = position
        self.vx, self.vy, self.vz = velocity
        self.mass = mass

# Initialize the solar system
def init_solar_system():
    return [
        # Sun
        Body((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), SOLAR_MASS),
        # Jupiter
        Body(
            (4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01),
            (1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR),
            9.54791938424326609e-04 * SOLAR_MASS
        ),
        # Saturn
        Body(
            (8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01),
            (-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR),
            2.85885980666130812e-04 * SOLAR_MASS
        ),
        # Uranus
        Body(
            (1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01),
            (2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR),
            4.36624404335156298e-05 * SOLAR_MASS
        ),
        # Neptune
        Body(
            (1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01),
            (2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR),
            5.15138902046611451e-05 * SOLAR_MASS
        )
    ]

# Calculate acceleration for all bodies
def compute_accelerations(bodies):
    n = len(bodies)
    ax = [0.0] * n
    ay = [0.0] * n
    az = [0.0] * n
    
    for i in range(n):
        for j in range(i+1, n):
            dx = bodies[j].x - bodies[i].x
            dy = bodies[j].y - bodies[i].y
            dz = bodies[j].z - bodies[i].z
            
            dsq = dx*dx + dy*dy + dz*dz
            distance = math.sqrt(dsq)
            mag = 1.0 / (distance * dsq)
            
            # Update accelerations for both bodies
            ai_mag = bodies[j].mass * mag
            ax[i] += dx * ai_mag
            ay[i] += dy * ai_mag
            az[i] += dz * ai_mag
            
            aj_mag = bodies[i].mass * mag
            ax[j] -= dx * aj_mag
            ay[j] -= dy * aj_mag
            az[j] -= dz * aj_mag
    
    return ax, ay, az

# Symplectic Euler integrator
def symplectic_euler(bodies, dt, steps):
    for _ in range(steps):
        # Compute accelerations at current positions
        ax, ay, az = compute_accelerations(bodies)
        
        # Update velocities and positions
        for i in range(len(bodies)):
            bodies[i].vx += ax[i] * dt
            bodies[i].vy += ay[i] * dt
            bodies[i].vz += az[i] * dt
            
            bodies[i].x += bodies[i].vx * dt
            bodies[i].y += bodies[i].vy * dt
            bodies[i].z += bodies[i].vz * dt

# Calculate total energy of the system
def compute_energy(bodies):
    energy = 0.0
    n = len(bodies)
    
    # Kinetic energy
    for i in range(n):
        energy += 0.5 * bodies[i].mass * (
            bodies[i].vx**2 + bodies[i].vy**2 + bodies[i].vz**2
        )
    
    # Potential energy
    for i in range(n):
        for j in range(i+1, n):
            dx = bodies[i].x - bodies[j].x
            dy = bodies[i].y - bodies[j].y
            dz = bodies[i].z - bodies[j].z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            energy -= (bodies[i].mass * bodies[j].mass) / distance
    
    return energy

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <simulation_steps>")
        return
    
    steps = int(sys.argv[1])
    dt = 0.01  # Time step in years
    
    bodies = init_solar_system()
    
    # Offset momentum to keep the system stationary
    px = py = pz = 0.0
    for body in bodies:
        px += body.vx * body.mass
        py += body.vy * body.mass
        pz += body.vz * body.mass
    bodies[0].vx = -px / bodies[0].mass
    bodies[0].vy = -py / bodies[0].mass
    bodies[0].vz = -pz / bodies[0].mass
    
    # Print initial energy
    print(f"Initial energy: {compute_energy(bodies)}")
    
    # Run simulation
    symplectic_euler(bodies, dt, steps)
    
    # Print final energy
    print(f"Final energy: {compute_energy(bodies)}")

if __name__ == "__main__":
    main()