import math
from typing import List

# Astronomical constants
PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

class Body:
    # __slots__ prevents the creation of a dynamic __dict__ for each instance,
    # drastically reducing memory overhead and improving attribute access speed.
    __slots__ = ['name', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'mass']

    def __init__(self, name: str, x: float, y: float, z: float, 
                 vx: float, vy: float, vz: float, mass: float):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.mass = mass

def offset_momentum(bodies: List[Body]) -> None:
    """
    Adjusts the Sun's velocity so that the total momentum of the solar 
    system is strictly zero, anchoring the center of mass.
    """
    px, py, pz = 0.0, 0.0, 0.0
    for body in bodies:
        px += body.vx * body.mass
        py += body.vy * body.mass
        pz += body.vz * body.mass
    
    sun = bodies[0]
    sun.vx = -px / SOLAR_MASS
    sun.vy = -py / SOLAR_MASS
    sun.vz = -pz / SOLAR_MASS

def calculate_energy(bodies: List[Body]) -> float:
    """Calculates the total kinetic and potential energy of the system."""
    energy = 0.0
    size = len(bodies)
    
    for i in range(size):
        b1 = bodies[i]
        energy += 0.5 * b1.mass * (b1.vx**2 + b1.vy**2 + b1.vz**2)
        
        for j in range(i + 1, size):
            b2 = bodies[j]
            dx = b1.x - b2.x
            dy = b1.y - b2.y
            dz = b1.z - b2.z
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            energy -= (b1.mass * b2.mass) / distance
            
    return energy

def advance(bodies: List[Body], dt: float, steps: int) -> None:
    """
    Advances the simulation by dt for a given number of steps.
    Uses a semi-implicit Euler integration method.
    """
    size = len(bodies)
    
    for _ in range(steps):
        # Update velocities based on gravitational pull
        for i in range(size):
            b1 = bodies[i]
            for j in range(i + 1, size):
                b2 = bodies[j]
                
                dx = b1.x - b2.x
                dy = b1.y - b2.y
                dz = b1.z - b2.z
                
                distance_sq = dx**2 + dy**2 + dz**2
                distance = math.sqrt(distance_sq)
                mag = dt / (distance_sq * distance)
                
                b1.vx -= dx * b2.mass * mag
                b1.vy -= dy * b2.mass * mag
                b1.vz -= dz * b2.mass * mag
                
                b2.vx += dx * b1.mass * mag
                b2.vy += dy * b1.mass * mag
                b2.vz += dz * b1.mass * mag
                
        # Update positions based on the new velocities
        for i in range(size):
            b = bodies[i]
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.z += b.vz * dt

def run_simulation() -> None:
    # Initialize bodies based on provided ephemeris
    bodies = [
        Body("Sun", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS),
        Body("Jupiter", 
             4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
             1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
             9.54791938424326609e-04 * SOLAR_MASS),
        Body("Saturn", 
             8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
             -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
             2.85885980666130812e-04 * SOLAR_MASS),
        Body("Uranus", 
             1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
             2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
             4.36624404335156298e-05 * SOLAR_MASS),
        Body("Neptune", 
             1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
             2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
             5.15138902046611451e-05 * SOLAR_MASS)
    ]
    
    offset_momentum(bodies)
    
    # 0.01 days per tick is a common timestep for precision in this benchmark
    dt = 0.01 
    steps = 10000 
    
    print(f"Initial Energy: {calculate_energy(bodies):.9f}")
    advance(bodies, dt, steps)
    print(f"Final Energy:   {calculate_energy(bodies):.9f}")

if __name__ == "__main__":
    run_simulation()