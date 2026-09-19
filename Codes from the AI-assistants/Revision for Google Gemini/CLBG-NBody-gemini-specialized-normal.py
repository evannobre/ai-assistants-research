import math
from itertools import combinations
from dataclasses import dataclass
from typing import List, Tuple

# Constants derived from the standard N-body benchmark
PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

@dataclass
class Body:
    """Represents a celestial body with position, velocity, and mass."""
    name: str
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float

def get_jovian_system() -> List[Body]:
    """Initializes the Jovian planets and the Sun with the provided ephemeris."""
    return [
        Body("Sun", 
             0.0, 0.0, 0.0, 
             0.0, 0.0, 0.0, 
             SOLAR_MASS),
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

def offset_momentum(bodies: List[Body]) -> None:
    """
    Adjusts the Sun's velocity to ensure the center of mass of the entire system is stationary.
    This prevents the system from drifting across the coordinate space during the simulation.
    """
    px = py = pz = 0.0
    for body in bodies:
        px += body.vx * body.mass
        py += body.vy * body.mass
        pz += body.vz * body.mass
    
    # Assuming the Sun is at index 0
    sun = bodies[0]
    sun.vx = -px / SOLAR_MASS
    sun.vy = -py / SOLAR_MASS
    sun.vz = -pz / SOLAR_MASS

def advance(bodies: List[Body], pairs: List[Tuple[Body, Body]], dt: float) -> None:
    """
    Advances the simulation by a single time step `dt`.
    Calculates forces for all pairs, then updates velocities and positions.
    """
    # 1. Calculate interactions and update velocities
    for body1, body2 in pairs:
        dx = body1.x - body2.x
        dy = body1.y - body2.y
        dz = body1.z - body2.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        # mag combines the division by distance cubed with the time step
        mag = dt / (distance * distance * distance)
        
        # Action/Reaction: adjust velocities based on the pull of the other body
        body1.vx -= dx * body2.mass * mag
        body1.vy -= dy * body2.mass * mag
        body1.vz -= dz * body2.mass * mag
        
        body2.vx += dx * body1.mass * mag
        body2.vy += dy * body1.mass * mag
        body2.vz += dz * body1.mass * mag
        
    # 2. Update positions based on new velocities
    for body in bodies:
        body.x += dt * body.vx
        body.y += dt * body.vy
        body.z += dt * body.vz

def calculate_energy(bodies: List[Body], pairs: List[Tuple[Body, Body]]) -> float:
    """Calculates the total energy (Kinetic + Potential) of the system for validation."""
    energy = 0.0
    
    # Add kinetic energy: 0.5 * m * v^2
    for body in bodies:
        energy += 0.5 * body.mass * (body.vx**2 + body.vy**2 + body.vz**2)
        
    # Subtract potential energy: (G * m1 * m2) / r
    for body1, body2 in pairs:
        dx = body1.x - body2.x
        dy = body1.y - body2.y
        dz = body1.z - body2.z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        energy -= (body1.mass * body2.mass) / distance
        
    return energy

def simulate(steps: int, dt: float = 0.01) -> None:
    """Orchestrates the simulation setup and execution."""
    bodies = get_jovian_system()
    offset_momentum(bodies)
    
    # Pre-compute pairs (memory efficiency best practice for the loop)
    pairs = list(combinations(bodies, 2))
    
    print(f"Initial Energy: {calculate_energy(bodies, pairs):.9f}")
    
    for _ in range(steps):
        advance(bodies, pairs, dt)
        
    print(f"Final Energy:   {calculate_energy(bodies, pairs):.9f}")

if __name__ == "__main__":
    # Standard benchmark runs 50,000,000 steps with a step size of 0.01
    # We use a smaller step count here for immediate execution.
    simulate(1000)