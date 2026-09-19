import math
import time
import argparse

# Constants mapped to Astronomical Units (AU) and days.
PI = 3.14159265358979323
SOLAR_MASS = 4 * PI * PI
DAYS_PER_YEAR = 365.24

# Initial states based on highly accurate ephemeris data.
# Format: [x, y, z, vx, vy, vz, mass]
BODIES = [
    # Sun
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS],
    # Jupiter
    [
        4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
        1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
        9.54791938424326609e-04 * SOLAR_MASS
    ],
    # Saturn
    [
        8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
        -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
        2.85885980666130812e-04 * SOLAR_MASS
    ],
    # Uranus
    [
        1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
        2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
        4.36624404335156298e-05 * SOLAR_MASS
    ],
    # Neptune
    [
        1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
        2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
        5.15138902046611451e-05 * SOLAR_MASS
    ]
]

def offset_momentum(bodies):
    """
    Ensures the system's center of mass doesn't drift through space.
    Calculates total momentum and offsets the Sun's initial velocity to balance it.
    """
    px = py = pz = 0.0
    for body in bodies:
        mass = body[6]
        px += body[3] * mass
        py += body[4] * mass
        pz += body[5] * mass
    
    # Apply opposite momentum to the Sun
    sun = bodies[0]
    sun[3] = -px / SOLAR_MASS
    sun[4] = -py / SOLAR_MASS
    sun[5] = -pz / SOLAR_MASS

def compute_energy(bodies):
    """
    Calculates total kinetic and potential energy of the system.
    Used to verify the stability of the numerical integration.
    """
    e = 0.0
    for i, body_i in enumerate(bodies):
        vx, vy, vz, mass_i = body_i[3], body_i[4], body_i[5], body_i[6]
        # Kinetic energy (1/2 m v^2)
        e += 0.5 * mass_i * (vx*vx + vy*vy + vz*vz)
        
        # Potential energy (-G m1 m2 / r)
        for j in range(i + 1, len(bodies)):
            body_j = bodies[j]
            dx = body_i[0] - body_j[0]
            dy = body_i[1] - body_j[1]
            dz = body_i[2] - body_j[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (mass_i * body_j[6]) / distance
    return e

def advance(bodies, dt, n_steps):
    """
    The core Symplectic Euler solver.
    """
    for _ in range(n_steps):
        # 1. Update velocities based on mutual gravitation
        for i in range(len(bodies)):
            body_i = bodies[i]
            for j in range(i + 1, len(bodies)):
                body_j = bodies[j]
                
                dx = body_i[0] - body_j[0]
                dy = body_i[1] - body_j[1]
                dz = body_i[2] - body_j[2]

                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                # mag = dt / r^3
                mag = dt / (distance * distance * distance)

                # Mass scales the acceleration (since G is baked into mass)
                body_i_mass_mag = body_i[6] * mag
                body_j_mass_mag = body_j[6] * mag

                body_i[3] -= dx * body_j_mass_mag
                body_i[4] -= dy * body_j_mass_mag
                body_i[5] -= dz * body_j_mass_mag

                body_j[3] += dx * body_i_mass_mag
                body_j[4] += dy * body_i_mass_mag
                body_j[5] += dz * body_i_mass_mag

        # 2. Update positions using the newly calculated velocities
        for body in bodies:
            body[0] += dt * body[3]
            body[1] += dt * body[4]
            body[2] += dt * body[5]

def main():
    parser = argparse.ArgumentParser(description="Jovian N-Body Simulation Benchmark")
    parser.add_argument("-n", "--steps", type=int, default=500000, 
                        help="Number of simulation steps (default: 500,000)")
    parser.add_argument("-dt", "--timestep", type=float, default=0.01, 
                        help="Time step delta per iteration in days (default: 0.01)")
    args = parser.parse_args()

    # Anchor the solar system center of mass
    offset_momentum(BODIES)

    print(f"Initial energy: {compute_energy(BODIES):.9f}")

    # Benchmark loop
    start_time = time.time()
    advance(BODIES, args.timestep, args.steps)
    end_time = time.time()

    print(f"Final energy:   {compute_energy(BODIES):.9f}")
    
    # Calculate performance metrics
    elapsed = end_time - start_time
    print("\n--- Performance Evaluation ---")
    print(f"Total Steps: {args.steps}")
    print(f"Time Taken:  {elapsed:.4f} seconds")
    if elapsed > 0:
        print(f"Throughput:  {args.steps / elapsed:,.0f} steps/second")

if __name__ == "__main__":
    main()