import numpy as np

SOLAR_MASS = 4 * np.pi ** 2
DAYS_PER_YEAR = 365.24

class Body:
    def __init__(self, position, velocity, mass):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.mass = mass

def compute_forces(bodies):
    num_bodies = len(bodies)
    accelerations = [np.zeros(3) for _ in range(num_bodies)]

    for i in range(num_bodies):
        for j in range(i + 1, num_bodies):
            delta = bodies[j].position - bodies[i].position
            distance = np.linalg.norm(delta)
            force_mag = (bodies[i].mass * bodies[j].mass) / (distance ** 3)
            accelerations[i] += force_mag * delta
            accelerations[j] -= force_mag * delta

    return accelerations

def update_positions_and_velocities(bodies, dt):
    accelerations = compute_forces(bodies)
    for i, body in enumerate(bodies):
        body.velocity += accelerations[i] * dt
        body.position += body.velocity * dt

def simulate(bodies, num_steps, dt):
    for _ in range(num_steps):
        update_positions_and_velocities(bodies, dt)

# Define bodies with given ephemeris
bodies = [
    Body((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), SOLAR_MASS),
    Body((4.84143144246472090, -1.16032004402742839, -0.103622044471123109),
         (1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR),
         9.54791938424326609e-04 * SOLAR_MASS),
    Body((8.34336671824457987, 4.12479856412430479, -0.403523417114321381),
         (-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR),
         2.85885980666130812e-04 * SOLAR_MASS),
    Body((12.8943695621391310, -15.1111514016986312, -0.223307578892655734),
         (2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR),
         4.36624404335156298e-05 * SOLAR_MASS),
    Body((15.3796971148509165, -25.9193146099879641, 0.179258772950371181),
         (2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR),
         5.15138902046611451e-05 * SOLAR_MASS)
]

# Run simulation
num_steps = 50000000
dt = 0.01  # Adjust time step as needed
simulate(bodies, num_steps, dt)
