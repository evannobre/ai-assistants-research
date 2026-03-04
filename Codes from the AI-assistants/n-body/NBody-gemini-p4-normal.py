import sys
import math

# Constants
PI = 3.141592653589793
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

def solve_nbody(n_steps, dt=0.01):
    # Data: [x, y, z, vx, vy, vz, mass]
    # Initialized with your provided ephemeris
    bodies = [
        # Sun
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS],
        # Jupiter
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
         9.54791938424326609e-04 * SOLAR_MASS],
        # Saturn
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
         2.85885980666130812e-04 * SOLAR_MASS],
        # Uranus
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
         4.36624404335156298e-05 * SOLAR_MASS],
        # Neptune
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
         5.15138902046611451e-05 * SOLAR_MASS]
    ]

    num_bodies = len(bodies)

    # Simulation Loop
    for _ in range(n_steps):
        # 1 & 2. Calculate Forces and Update Velocities
        for i in range(num_bodies):
            b1 = bodies[i]
            for j in range(i + 1, num_bodies):
                b2 = bodies[j]
                dx = b1[0] - b2[0]
                dy = b1[1] - b2[1]
                dz = b1[2] - b2[2]
                
                dist_sq = dx*dx + dy*dy + dz*dz
                mag = dt / (dist_sq * math.sqrt(dist_sq))
                
                # Update velocity of b1
                b1[3] -= dx * b2[6] * mag
                b1[4] -= dy * b2[6] * mag
                b1[5] -= dz * b2[6] * mag
                
                # Update velocity of b2 (Newton's 3rd Law)
                b2[3] += dx * b1[6] * mag
                b2[4] += dy * b1[6] * mag
                b2[5] += dz * b1[6] * mag

        # 3. Update Positions using new Velocities
        for b in bodies:
            b[0] += dt * b[3]
            b[1] += dt * b[4]
            b[2] += dt * b[5]

    return bodies

if __name__ == "__main__":
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 50000000
    print(f"Starting simulation for {iterations} iterations...")
    final_state = solve_nbody(iterations)
    print("Simulation Complete.")
    # Output Neptune's final position as a sanity check
    print(f"Neptune Pos: {final_state[4][:3]}")