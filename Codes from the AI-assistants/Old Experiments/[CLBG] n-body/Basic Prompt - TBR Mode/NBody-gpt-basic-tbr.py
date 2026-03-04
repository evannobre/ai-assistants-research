import sys
from math import pi, sqrt

# Physical constants
DAYS_PER_YEAR = 365.24
SOLAR_MASS   = 4 * pi * pi

# Body struct
class Body:
    def __init__(self, pos, vel, mass):
        self.pos  = list(pos)   # [x, y, z]
        self.vel  = list(vel)   # [vx, vy, vz]
        self.mass = mass

bodies = [
    Body(( 0.0,  0.0,  0.0),
         ( 0.0,  0.0,  0.0),
         SOLAR_MASS),
    Body(( 4.84143144246472090, -1.16032004402742839, -0.103622044471123109),
         ( 1.66007664274403694e-3 * DAYS_PER_YEAR,
           7.69901118419740425e-3 * DAYS_PER_YEAR,
          -6.90460016972063023e-5 * DAYS_PER_YEAR),
         9.54791938424326609e-4 * SOLAR_MASS),
    Body(( 8.34336671824457987,  4.12479856412430479, -0.403523417114321381),
         (-2.76742510726862411e-3 * DAYS_PER_YEAR,
           4.99852801234917238e-3 * DAYS_PER_YEAR,
           2.30417297573763929e-5 * DAYS_PER_YEAR),
         2.85885980666130812e-4 * SOLAR_MASS),
    Body((12.8943695621391310, -15.1111514016986312, -0.223307578892655734),
         ( 2.96460137564761618e-3 * DAYS_PER_YEAR,
           2.37847173959480950e-3 * DAYS_PER_YEAR,
          -2.96589568540237556e-5 * DAYS_PER_YEAR),
         4.36624404335156298e-5 * SOLAR_MASS),
    Body((15.37969711485091091, -25.9193146099879621,  0.179258772950371181),
         ( 2.68067772490389322e-3 * DAYS_PER_YEAR,
           1.62824170038242295e-3 * DAYS_PER_YEAR,
          -9.51592254519715870e-5 * DAYS_PER_YEAR),
         5.15138902046611451e-5 * SOLAR_MASS)
]

px = py = pz = 0.0
for b in bodies:
    px += b.vel[0] * b.mass
    py += b.vel[1] * b.mass
    pz += b.vel[2] * b.mass

# subtract from Sun’s velocity
sun = bodies[0]
sun.vel[0] -= px / SOLAR_MASS
sun.vel[1] -= py / SOLAR_MASS
sun.vel[2] -= pz / SOLAR_MASS

def advance(bodies, dt):
    n = len(bodies)
    # --- Kick: compute pairwise accelerations and update velocities ---
    for i in range(n):
        bi = bodies[i]
        for j in range(i+1, n):
            bj = bodies[j]
            dx = bi.pos[0] - bj.pos[0]
            dy = bi.pos[1] - bj.pos[1]
            dz = bi.pos[2] - bj.pos[2]
            dist2 = dx*dx + dy*dy + dz*dz
            dist  = sqrt(dist2)
            # magnitude of force per unit mass
            mag = dt / (dist2 * dist)
            bi_vel_factor = bj.mass * mag
            bj_vel_factor = bi.mass * mag
            # update velocities
            bi.vel[0] -= dx * bi_vel_factor
            bi.vel[1] -= dy * bi_vel_factor
            bi.vel[2] -= dz * bi_vel_factor
            bj.vel[0] += dx * bj_vel_factor
            bj.vel[1] += dy * bj_vel_factor
            bj.vel[2] += dz * bj_vel_factor

    # --- Drift: update positions using new velocities ---
    for b in bodies:
        b.pos[0] += dt * b.vel[0]
        b.pos[1] += dt * b.vel[1]
        b.pos[2] += dt * b.vel[2]

def main():
    if len(sys.argv) != 2:
        print("Usage: nbody <num_steps>")
        sys.exit(1)
    n_steps = int(sys.argv[1])
    dt      = 0.01  # time-step in years (tune for accuracy/perf)

    # initialize bodies and zero momentum as above…

    for i in range(n_steps):
        advance(bodies, dt)

    # (optional) compute and print total energy for sanity check
    print("Final positions and velocities:")
    for b in bodies:
        print(f"pos={b.pos}, vel={b.vel}")

if __name__ == "__main__":
    main()
