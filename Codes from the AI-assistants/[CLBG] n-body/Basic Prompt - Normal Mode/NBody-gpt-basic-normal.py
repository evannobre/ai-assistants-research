import sys
import math
from itertools import combinations

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# Each body is: [position: [x, y, z], velocity: [vx, vy, vz], mass]
bodies = {
    'sun': [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        SOLAR_MASS
    ],
    'jupiter': [
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01],
        [1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR],
        9.54791938424326609e-04 * SOLAR_MASS
    ],
    'saturn': [
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01],
        [-2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR],
        2.85885980666130812e-04 * SOLAR_MASS
    ],
    'uranus': [
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01],
        [2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR],
        4.36624404335156298e-05 * SOLAR_MASS
    ],
    'neptune': [
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01],
        [2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR],
        5.15138902046611451e-05 * SOLAR_MASS
    ]
}

def offset_momentum():
    px = py = pz = 0.0
    for body in bodies.values():
        r, v, m = body
        px += v[0] * m
        py += v[1] * m
        pz += v[2] * m
    sun = bodies['sun']
    sun[1][0] = -px / SOLAR_MASS
    sun[1][1] = -py / SOLAR_MASS
    sun[1][2] = -pz / SOLAR_MASS

def compute_energy():
    e = 0.0
    seen = list(bodies.values())
    for i, body1 in enumerate(seen):
        (r1, v1, m1) = body1
        e += 0.5 * m1 * sum(v * v for v in v1)
        for j in range(i+1, len(seen)):
            (r2, _, m2) = seen[j]
            dx = r1[0] - r2[0]
            dy = r1[1] - r2[1]
            dz = r1[2] - r2[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (m1 * m2) / dist
    return e

def advance(dt):
    pairs = list(combinations(bodies.values(), 2))

    for (body1, body2) in pairs:
        (r1, v1, m1) = body1
        (r2, v2, m2) = body2

        dx = r1[0] - r2[0]
        dy = r1[1] - r2[1]
        dz = r1[2] - r2[2]
        dist_sq = dx*dx + dy*dy + dz*dz
        dist = math.sqrt(dist_sq)
        mag = dt / (dist_sq * dist)

        m1mag = m2 * mag
        m2mag = m1 * mag

        v1[0] -= dx * m1mag
        v1[1] -= dy * m1mag
        v1[2] -= dz * m1mag

        v2[0] += dx * m2mag
        v2[1] += dy * m2mag
        v2[2] += dz * m2mag

    for body in bodies.values():
        r, v, _ = body
        r[0] += v[0] * dt
        r[1] += v[1] * dt
        r[2] += v[2] * dt

def main(n, dt=0.01):
    offset_momentum()
    print(f"Initial energy: {compute_energy():.9f}")
    for i in range(n):
        advance(dt)
    print(f"Final energy: {compute_energy():.9f}")

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50000000
    main(n)
