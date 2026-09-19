import math
from itertools import combinations

# --- Constants ---
PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# --- System Data ---
# Structure: [ [x, y, z], [vx, vy, vz], mass ]
system = [
    # Sun
    [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        SOLAR_MASS
    ],
    # Jupiter
    [
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01],
        [1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR],
        9.54791938424326609e-04 * SOLAR_MASS
    ],
    # Saturn
    [
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01],
        [-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR],
        2.85885980666130812e-04 * SOLAR_MASS
    ],
    # Uranus
    [
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01],
        [2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR],
        4.36624404335156298e-05 * SOLAR_MASS
    ],
    # Neptune
    [
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01],
        [2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR],
        5.15138902046611451e-05 * SOLAR_MASS
    ]
]


def offset_momentum(bodies):
    """
    Adjusts the Sun's initial velocity so that the total momentum of the 
    entire system equals zero, keeping the center of mass completely static.
    """
    px = py = pz = 0.0
    for body in bodies:
        v = body[1]
        m = body[2]
        px += v[0] * m
        py += v[1] * m
        pz += v[2] * m
    
    # Apply inverse momentum to the Sun (index 0)
    sun_v = bodies[0][1]
    sun_v[0] = -px / SOLAR_MASS
    sun_v[1] = -py / SOLAR_MASS
    sun_v[2] = -pz / SOLAR_MASS


def advance(bodies, dt):
    """
    Advances the simulation by 'dt' (fractions of a year) using the 
    Symplectic Euler integration method.
    """
    # Step 1: Compute pairwise gravitational forces and update velocities
    for body1, body2 in combinations(bodies, 2):
        pos1, v1, m1 = body1[0], body1[1], body1[2]
        pos2, v2, m2 = body2[0], body2[1], body2[2]
        
        # Distance vector
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        
        # Scalar distance mathematics
        distance_sq = dx*dx + dy*dy + dz*dz
        distance = math.sqrt(distance_sq)
        
        # The magnitude of the force vector (dt / r^3)
        mag = dt / (distance_sq * distance)
        
        # Mutate the velocities using Newton's laws
        v1[0] -= dx * m2 * mag
        v1[1] -= dy * m2 * mag
        v1[2] -= dz * m2 * mag
        
        v2[0] += dx * m1 * mag
        v2[1] += dy * m1 * mag
        v2[2] += dz * m1 * mag
        
    # Step 2: Use the newly calculated velocities to update positions
    for body in bodies:
        pos, v = body[0], body[1]
        pos[0] += v[0] * dt
        pos[1] += v[1] * dt
        pos[2] += v[2] * dt


def simulate(bodies, time_steps, dt=0.01):
    """
    Driver function to run the simulation loop.
    """
    # 1. Zero out system momentum
    offset_momentum(bodies)
    
    # 2. Run simulation loop
    for _ in range(time_steps):
        advance(bodies, dt)


if __name__ == "__main__":
    # Example: Run a simulation for 1,000 steps of 0.01 years (~3.6 days per step)
    simulate(system, 1000, dt=0.01)
    
    print("Final position of Jupiter after 10 simulated years:")
    print(f"X: {system[1][0][0]:.5f}")
    print(f"Y: {system[1][0][1]:.5f}")
    print(f"Z: {system[1][0][2]:.5f}")