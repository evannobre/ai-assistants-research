import math
PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

class Body:
    def __init__(self, pos, vel, mass):
        self.x, self.y, self.z = pos
        self.vx, self.vy, self.vz = vel
        self.mass = mass

def get_bodies():
    return [
        Body((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), SOLAR_MASS),  # Sun
        Body(
            (4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01),
            (1.66007664274403694e-03 * DAYS_PER_YEAR, 
             7.69901118419740425e-03 * DAYS_PER_YEAR,
            -6.90460016972063023e-05 * DAYS_PER_YEAR),
            9.54791938424326609e-04 * SOLAR_MASS
        ),
        Body(
            (8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01),
            (-2.76742510726862411e-03 * DAYS_PER_YEAR,
              4.99852801234917238e-03 * DAYS_PER_YEAR,
              2.30417297573763929e-05 * DAYS_PER_YEAR),
            2.85885980666130812e-04 * SOLAR_MASS
        ),
        Body(
            (1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01),
            (2.96460137564761618e-03 * DAYS_PER_YEAR,
             2.37847173959480950e-03 * DAYS_PER_YEAR,
            -2.96589568540237556e-05 * DAYS_PER_YEAR),
            4.36624404335156298e-05 * SOLAR_MASS
        ),
        Body(
            (1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01),
            (2.68067772490389322e-03 * DAYS_PER_YEAR,
             1.62824170038242295e-03 * DAYS_PER_YEAR,
            -9.51592254519715870e-05 * DAYS_PER_YEAR),
            5.15138902046611451e-05 * SOLAR_MASS
        ),
    ]

def offset_momentum(bodies):
    px = py = pz = 0.0
    for b in bodies:
        px += b.vx * b.mass
        py += b.vy * b.mass
        pz += b.vz * b.mass

    sun = bodies[0]
    sun.vx = -px / SOLAR_MASS
    sun.vy = -py / SOLAR_MASS
    sun.vz = -pz / SOLAR_MASS

def advance(bodies, dt):
    pairs = [(bodies[i], bodies[j]) for i in range(len(bodies)) for j in range(i+1, len(bodies))]
    for b1, b2 in pairs:
        dx = b1.x - b2.x
        dy = b1.y - b2.y
        dz = b1.z - b2.z
        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq)
        mag = dt / (dist_sq * dist)

        b1_mass_mag = b2.mass * mag
        b2_mass_mag = b1.mass * mag

        b1.vx -= dx * b1_mass_mag
        b1.vy -= dy * b1_mass_mag
        b1.vz -= dz * b1_mass_mag
        b2.vx += dx * b2_mass_mag
        b2.vy += dy * b2_mass_mag
        b2.vz += dz * b2_mass_mag

    for b in bodies:
        b.x += dt * b.vx
        b.y += dt * b.vy
        b.z += dt * b.vz

def energy(bodies):
    e = 0.0
    for i in range(len(bodies)):
        b1 = bodies[i]
        e += 0.5 * b1.mass * (b1.vx**2 + b1.vy**2 + b1.vz**2)
        for j in range(i + 1, len(bodies)):
            b2 = bodies[j]
            dx = b1.x - b2.x
            dy = b1.y - b2.y
            dz = b1.z - b2.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (b1.mass * b2.mass) / dist
    return e

import sys
def main(steps, dt=0.01):
    bodies = get_bodies()
    offset_momentum(bodies)
    print(f"Initial energy: {energy(bodies):.9f}")
    for _ in range(steps):
        advance(bodies, dt)
    print(f"Final energy: {energy(bodies):.9f}")

if __name__ == '__main__':
    main(int(sys.argv[1]))  # e.g., python nbody.py 50000000