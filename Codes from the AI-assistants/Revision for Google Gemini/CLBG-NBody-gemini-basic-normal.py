import math

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

class Body:
    def __init__(self, name, position, velocity, mass):
        self.name = name
        self.x, self.y, self.z = position
        self.vx, self.vy, self.vz = velocity
        self.mass = mass

def offset_momentum(bodies):
    """
    Adjusts the Sun's initial velocity so that the total momentum 
    of the entire system is zero. This prevents the system from drifting.
    """
    px, py, pz = 0.0, 0.0, 0.0
    for body in bodies:
        px += body.vx * body.mass
        py += body.vy * body.mass
        pz += body.vz * body.mass
    
    # Assuming the Sun is the first body in the list
    sun = bodies[0]
    sun.vx = -px / SOLAR_MASS
    sun.vy = -py / SOLAR_MASS
    sun.vz = -pz / SOLAR_MASS

def advance(bodies, dt):
    """
    Advances the system by one time step (dt) using the Semi-implicit Euler method.
    """
    n = len(bodies)
    
    # 1. Update velocities based on gravitational forces between all pairs
    for i in range(n):
        for j in range(i + 1, n):
            dx = bodies[i].x - bodies[j].x
            dy = bodies[i].y - bodies[j].y
            dz = bodies[i].z - bodies[j].z
            
            distance_squared = dx*dx + dy*dy + dz*dz
            distance = math.sqrt(distance_squared)
            
            # magnitude = dt / d^3
            mag = dt / (distance_squared * distance)
            
            bodies[i].vx -= dx * bodies[j].mass * mag
            bodies[i].vy -= dy * bodies[j].mass * mag
            bodies[i].vz -= dz * bodies[j].mass * mag
            
            bodies[j].vx += dx * bodies[i].mass * mag
            bodies[j].vy += dy * bodies[i].mass * mag
            bodies[j].vz += dz * bodies[i].mass * mag
            
    # 2. Update positions using the newly calculated velocities
    for body in bodies:
        body.x += body.vx * dt
        body.y += body.vy * dt
        body.z += body.vz * dt

def calculate_energy(bodies):
    """
    Calculates the total energy (Kinetic + Potential) of the system.
    This is useful for verifying the stability of the simulation.
    """
    energy = 0.0
    n = len(bodies)
    
    for i in range(n):
        # Kinetic Energy: 0.5 * m * v^2
        energy += 0.5 * bodies[i].mass * (
            bodies[i].vx**2 + bodies[i].vy**2 + bodies[i].vz**2
        )
        
        # Potential Energy: - (m1 * m2) / distance
        for j in range(i + 1, n):
            dx = bodies[i].x - bodies[j].x
            dy = bodies[i].y - bodies[j].y
            dz = bodies[i].z - bodies[j].z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            energy -= (bodies[i].mass * bodies[j].mass) / distance
            
    return energy

def main():
    # Initialize bodies based on provided ephemeris data
    bodies = [
        Body("Sun", 
             (0.0, 0.0, 0.0), 
             (0.0, 0.0, 0.0), 
             SOLAR_MASS),
        Body("Jupiter", 
             (4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01), 
             (1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR), 
             9.54791938424326609e-04 * SOLAR_MASS),
        Body("Saturn", 
             (8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01), 
             (-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR), 
             2.85885980666130812e-04 * SOLAR_MASS),
        Body("Uranus", 
             (1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01), 
             (2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR), 
             4.36624404335156298e-05 * SOLAR_MASS),
        Body("Neptune", 
             (1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01), 
             (2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR), 
             5.15138902046611451e-05 * SOLAR_MASS)
    ]

    # Stabilize the initial center of mass
    offset_momentum(bodies)
    
    # Print initial system energy
    print(f"Initial Energy: {calculate_energy(bodies):.9f}")
    
    # Simulation parameters
    time_step = 0.01 # dt (in days)
    total_steps = 100_000 
    
    # Run simulation
    for _ in range(total_steps):
        advance(bodies, time_step)
        
    # Print final system energy to verify conservation
    print(f"Final Energy:   {calculate_energy(bodies):.9f}")

if __name__ == "__main__":
    main()