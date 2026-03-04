import math
import numpy as np

# Constants
SOLAR_MASS = 4 * math.pi**2
DAYS_PER_YEAR = 365.24
DT = 0.01  # Time step

# Initial conditions: (positions, velocities, mass)
bodies = {
    "Sun": ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], SOLAR_MASS),
    "Jupiter": ([4.84143144246472, -1.1603200440274284, -0.1036220444711231],
                [1.660076642744037e-3 * DAYS_PER_YEAR, 7.699011184197404e-3 * DAYS_PER_YEAR, -6.90460016972063e-5 * DAYS_PER_YEAR],
                9.547919384243266e-4 * SOLAR_MASS),
    "Saturn": ([8.34336671824458, 4.124798564124305, -0.4035234171143214],
               [-2.767425107268624e-3 * DAYS_PER_YEAR, 4.998528012349172e-3 * DAYS_PER_YEAR, 2.304172975737639e-5 * DAYS_PER_YEAR],
               2.858859806661308e-4 * SOLAR_MASS),
    "Uranus": ([12.894369562139131, -15.111151401698631, -0.22330757889265573],
               [2.964601375647616e-3 * DAYS_PER_YEAR, 2.3784717395948095e-3 * DAYS_PER_YEAR, -2.965895685402375e-5 * DAYS_PER_YEAR],
               4.366244043351563e-5 * SOLAR_MASS),
    "Neptune": ([15.379697114850916, -25.919314609987964, 0.17925877295037118],
                [2.6806777249038932e-3 * DAYS_PER_YEAR, 1.628241700382423e-3 * DAYS_PER_YEAR, -9.515922545197159e-5 * DAYS_PER_YEAR],
                5.151389020466114e-5 * SOLAR_MASS),
}

def advance(bodies, dt):
    """Perform one step of the simulation using Euler's symplectic-integrator."""
    for body1 in bodies:
        pos1, vel1, mass1 = bodies[body1]
        for body2 in bodies:
            if body1 != body2:
                pos2, _, mass2 = bodies[body2]
                dx, dy, dz = np.subtract(pos2, pos1)
                dist = math.sqrt(dx**2 + dy**2 + dz**2)
                force_mag = (mass1 * mass2) / dist**3
                vel1[0] += force_mag * dx * dt
                vel1[1] += force_mag * dy * dt
                vel1[2] += force_mag * dz * dt

    for body in bodies:
        pos, vel, _ = bodies[body]
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt
        pos[2] += vel[2] * dt

def simulate(n_steps):
    """Run the n-body simulation for a given number of steps."""
    for _ in range(n_steps):
        advance(bodies, DT)

if __name__ == "__main__":
    simulate(50000000)
