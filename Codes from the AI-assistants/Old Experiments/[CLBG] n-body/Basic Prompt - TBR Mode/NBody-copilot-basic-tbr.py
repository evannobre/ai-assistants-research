import sys
import math

# Define the constants
PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# The ephemeris data for the system in the form:
# [position (x,y,z), velocity (vx,vy,vz), mass]
def init_bodies():
    return [
        # Sun
        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         SOLAR_MASS],
        # Jupiter
        [[4.84143144246472090e+00,
          -1.16032004402742839e+00,
          -1.03622044471123109e-01],
         [1.66007664274403694e-03 * DAYS_PER_YEAR,
          7.69901118419740425e-03 * DAYS_PER_YEAR,
          -6.90460016972063023e-05 * DAYS_PER_YEAR],
         9.54791938424326609e-04 * SOLAR_MASS],
        # Saturn
        [[8.34336671824457987e+00,
          4.12479856412430479e+00,
          -4.03523417114321381e-01],
         [-2.76742510726862411e-03 * DAYS_PER_YEAR,
          4.99852801234917238e-03 * DAYS_PER_YEAR,
          2.30417297573763929e-05 * DAYS_PER_YEAR],
         2.85885980666130812e-04 * SOLAR_MASS],
        # Uranus
        [[1.28943695621391310e+01,
          -1.51111514016986312e+01,
          -2.23307578892655734e-01],
         [2.96460137564761618e-03 * DAYS_PER_YEAR,
          2.37847173959480950e-03 * DAYS_PER_YEAR,
          -2.96589568540237556e-05 * DAYS_PER_YEAR],
         4.36624404335156298e-05 * SOLAR_MASS],
        # Neptune
        [[1.53796971148509165e+01,
          -2.59193146099879641e+01,
          1.79258772950371181e-01],
         [2.68067772490389322e-03 * DAYS_PER_YEAR,
          1.62824170038242295e-03 * DAYS_PER_YEAR,
          -9.51592254519715870e-05 * DAYS_PER_YEAR],
         5.15138902046611451e-05 * SOLAR_MASS]
    ]

def advance(bodies, dt):
    """Advance the system one time step using a symplectic Euler integrator."""
    nbodies = len(bodies)
    # For every unique pair, compute the gravitational interaction and update velocities.
    for i in range(nbodies):
        for j in range(i+1, nbodies):
            # Compute difference in positions:
            dx = bodies[j][0][0] - bodies[i][0][0]
            dy = bodies[j][0][1] - bodies[i][0][1]
            dz = bodies[j][0][2] - bodies[i][0][2]
            distance_sq = dx * dx + dy * dy + dz * dz
            distance = math.sqrt(distance_sq)
            mag = dt / (distance_sq * distance)

            m_i = bodies[i][2]
            m_j = bodies[j][2]

            # Update velocities for body i and j.
            bodies[i][1][0] += dx * m_j * mag
            bodies[i][1][1] += dy * m_j * mag
            bodies[i][1][2] += dz * m_j * mag

            bodies[j][1][0] -= dx * m_i * mag
            bodies[j][1][1] -= dy * m_i * mag
            bodies[j][1][2] -= dz * m_i * mag

    # Update positions using the newly updated velocities.
    for body in bodies:
        body[0][0] += dt * body[1][0]
        body[0][1] += dt * body[1][1]
        body[0][2] += dt * body[1][2]

def compute_energy(bodies):
    """Compute the total energy (kinetic + potential) of the system."""
    e = 0.0
    nbodies = len(bodies)
    # Sum over kinetic energy
    for body in bodies:
        vx, vy, vz = body[1]
        e += 0.5 * body[2] * (vx * vx + vy * vy + vz * vz)
    # Sum over potential energy for all unique body pairs.
    for i in range(nbodies):
        for j in range(i+1, nbodies):
            dx = bodies[i][0][0] - bodies[j][0][0]
            dy = bodies[i][0][1] - bodies[j][0][1]
            dz = bodies[i][0][2] - bodies[j][0][2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            e -= (bodies[i][2] * bodies[j][2]) / distance
    return e

def main():
    # Use the command line argument for the number of iterations or default to 50 million.
    n_steps = int(sys.argv[1]) if len(sys.argv) > 1 else 50000000
    dt = 0.01  # time step

    bodies = init_bodies()

    # Optionally, adjust the system momentum so that the center-of-mass is stationary.
    px = py = pz = 0.0
    for body in bodies:
        px += body[1][0] * body[2]
        py += body[1][1] * body[2]
        pz += body[1][2] * body[2]
    # Adjust the Sun's velocity to offset momentum.
    bodies[0][1][0] = -px / SOLAR_MASS
    bodies[0][1][1] = -py / SOLAR_MASS
    bodies[0][1][2] = -pz / SOLAR_MASS

    print("Initial energy:", compute_energy(bodies))
    for _ in range(n_steps):
        advance(bodies, dt)
    print("Final energy:", compute_energy(bodies))

if __name__ == '__main__':
    main()
