#!/usr/bin/env python3
import sys
import math
import time

PI = 3.14159265358979323
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

class Body:
    __slots__ = ("x", "y", "z", "vx", "vy", "vz", "mass")

    def __init__(self, x, y, z, vx, vy, vz, mass):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.mass = mass

def make_bodies():
    # Data adapted from the classic n-body benchmark
    sun = Body(
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        SOLAR_MASS
    )

    jupiter = Body(
        4.84143144246472090e+00,
        -1.16032004402742839e+00,
        -1.03622044471123109e-01,
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
        9.54791938424326609e-04 * SOLAR_MASS
    )

    saturn = Body(
        8.34336671824457987e+00,
        4.12479856412430479e+00,
        -4.03523417114321381e-01,
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        2.85885980666130812e-04 * SOLAR_MASS
    )

    uranus = Body(
        1.28943695621391310e+01,
        -1.51111514016986312e+01,
        -2.23307578892655734e-01,
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
        4.36624404335156298e-05 * SOLAR_MASS
    )

    neptune = Body(
        1.53796971148509165e+01,
        -2.59193146099879641e+01,
        1.79258772950371181e-01,
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
        5.15138902046611451e-05 * SOLAR_MASS
    )

    bodies = [sun, jupiter, saturn, uranus, neptune]
    offset_momentum(bodies)
    return bodies

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
    n = len(bodies)
    for i in range(n):
        bi = bodies[i]
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bj.x - bi.x
            dy = bj.y - bi.y
            dz = bj.z - bi.z

            dist2 = dx*dx + dy*dy + dz*dz
            dist = math.sqrt(dist2)
            mag = dt / (dist2 * dist)

            bi_mass_mag = bj.mass * mag
            bj_mass_mag = bi.mass * mag

            bi.vx += dx * bi_mass_mag
            bi.vy += dy * bi_mass_mag
            bi.vz += dz * bi_mass_mag

            bj.vx -= dx * bj_mass_mag
            bj.vy -= dy * bj_mass_mag
            bj.vz -= dz * bj_mass_mag

    for b in bodies:
        b.x += dt * b.vx
        b.y += dt * b.vy
        b.z += dt * b.vz

def energy(bodies):
    e = 0.0
    n = len(bodies)
    for i in range(n):
        bi = bodies[i]
        v2 = bi.vx*bi.vx + bi.vy*bi.vy + bi.vz*bi.vz
        e += 0.5 * bi.mass * v2
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi.x - bj.x
            dy = bi.y - bj.y
            dz = bi.z - bj.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (bi.mass * bj.mass) / dist
    return e

def main(argv):
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <iterations>")
        sys.exit(1)

    iterations = int(argv[1])
    dt = 0.01  # time step in years

    bodies = make_bodies()

    print("Initial energy:", f"{energy(bodies):.9f}")

    start = time.perf_counter()
    for _ in range(iterations):
        advance(bodies, dt)
    elapsed = time.perf_counter() - start

    print("Final energy:  ", f"{energy(bodies):.9f}")
    print("Iterations:", iterations)
    print("Elapsed time (s):", f"{elapsed:.6f}")

if __name__ == "__main__":
    main(sys.argv)
