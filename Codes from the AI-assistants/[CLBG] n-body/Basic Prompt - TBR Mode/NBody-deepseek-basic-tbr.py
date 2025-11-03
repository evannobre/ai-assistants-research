import math
import sys

SOLAR_MASS = 4 * math.pi ** 2
DAYS_PER_YEAR = 365.24

class Body:
    __slots__ = ('x', 'y', 'z', 'vx', 'vy', 'vz', 'mass')
    def __init__(self, position, velocity, mass):
        self.x, self.y, self.z = position
        self.vx, self.vy, self.vz = velocity
        self.mass = mass

bodies = [
    Body(
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        SOLAR_MASS
    ),
    Body(
        (4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01),
        (1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR),
        9.54791938424326609e-04 * SOLAR_MASS
    ),
    Body(
        (8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01),
        (-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR),
        2.85885980666130812e-04 * SOLAR_MASS
    ),
    Body(
        (1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01),
        (2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR),
        4.36624404335156298e-05 * SOLAR_MASS
    ),
    Body(
        (1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01),
        (2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR),
        5.15138902046611451e-05 * SOLAR_MASS
    )
]

def compute_accelerations(bodies):
    n = len(bodies)
    accelerations = [[0.0, 0.0, 0.0] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = bodies[j].x - bodies[i].x
            dy = bodies[j].y - bodies[i].y
            dz = bodies[j].z - bodies[i].z
            r_squared = dx * dx + dy * dy + dz * dz
            r = math.sqrt(r_squared)
            inv_r_cubed = 1.0 / (r_squared * r)
            
            mj = bodies[j].mass
            a_ij_x = mj * dx * inv_r_cubed
            a_ij_y = mj * dy * inv_r_cubed
            a_ij_z = mj * dz * inv_r_cubed
            accelerations[i][0] += a_ij_x
            accelerations[i][1] += a_ij_y
            accelerations[i][2] += a_ij_z
            
            mi = bodies[i].mass
            a_ji_x = -mi * dx * inv_r_cubed
            a_ji_y = -mi * dy * inv_r_cubed
            a_ji_z = -mi * dz * inv_r_cubed
            accelerations[j][0] += a_ji_x
            accelerations[j][1] += a_ji_y
            accelerations[j][2] += a_ji_z
    return accelerations

def main(num_steps, dt):
    for _ in range(num_steps):
        accelerations = compute_accelerations(bodies)
        for i in range(len(bodies)):
            ax, ay, az = accelerations[i]
            bodies[i].vx += ax * dt
            bodies[i].vy += ay * dt
            bodies[i].vz += az * dt
            bodies[i].x += bodies[i].vx * dt
            bodies[i].y += bodies[i].vy * dt
            bodies[i].z += bodies[i].vz * dt

if __name__ == "__main__":
    num_steps = int(sys.argv[1])
    dt = 0.001  # Time step in years
    main(num_steps, dt)