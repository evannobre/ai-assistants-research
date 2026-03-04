import math
import sys

PI = math.pi
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

def nbody(steps, dt=0.01):
    # Structure of Arrays (SoA)
    x = [
        0.0,
        4.84143144246472090e+00,
        8.34336671824457987e+00,
        1.28943695621391310e+01,
        1.53796971148509165e+01,
    ]
    y = [
        0.0,
        -1.16032004402742839e+00,
        4.12479856412430479e+00,
        -1.51111514016986312e+01,
        -2.59193146099879641e+01,
    ]
    z = [
        0.0,
        -1.03622044471123109e-01,
        -4.03523417114321381e-01,
        -2.23307578892655734e-01,
        1.79258772950371181e-01,
    ]

    vx = [
        0.0,
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.68067772490389322e-03 * DAYS_PER_YEAR,
    ]
    vy = [
        0.0,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
    ]
    vz = [
        0.0,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
    ]

    mass = [
        SOLAR_MASS,
        9.54791938424326609e-04 * SOLAR_MASS,
        2.85885980666130812e-04 * SOLAR_MASS,
        4.36624404335156298e-05 * SOLAR_MASS,
        5.15138902046611451e-05 * SOLAR_MASS,
    ]

    n = 5

    for _ in range(steps):
        # Compute accelerations and update velocities
        for i in range(n):
            xi = x[i]; yi = y[i]; zi = z[i]
            axi = ayi = azi = 0.0

            for j in range(n):
                if i == j:
                    continue
                dx = x[j] - xi
                dy = y[j] - yi
                dz = z[j] - zi
                dist2 = dx*dx + dy*dy + dz*dz
                invDist = 1.0 / math.sqrt(dist2)
                invDist3 = invDist * invDist * invDist
                factor = mass[j] * invDist3
                axi += dx * factor
                ayi += dy * factor
                azi += dz * factor

            vx[i] += dt * axi
            vy[i] += dt * ayi
            vz[i] += dt * azi

        # Update positions
        for i in range(n):
            x[i] += dt * vx[i]
            y[i] += dt * vy[i]
            z[i] += dt * vz[i]

    return x, y, z, vx, vy, vz


if __name__ == "__main__":
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 50000000
    nbody(steps)
