import math
from itertools import combinations

G = 6.67430e-11  # gravitational constant in m^3 kg^-1 s^-2

class Body:
    def __init__(self, name, mass, position, velocity):
        self.name = name
        self.mass = mass
        self.position = position  # [x, y, z]
        self.velocity = velocity  # [vx, vy, vz]
        self.acceleration = [0.0, 0.0, 0.0]

def compute_gravitational_acceleration(bodies):
    # Reset accelerations
    for body in bodies:
        body.acceleration = [0.0, 0.0, 0.0]

    for body1, body2 in combinations(bodies, 2):
        dx = [b2 - b1 for b1, b2 in zip(body1.position, body2.position)]
        dist_sq = sum(d**2 for d in dx)
        dist = math.sqrt(dist_sq) + 1e-10  # avoid divide by zero
        force_mag = G / dist_sq

        for i in range(3):
            acc = force_mag * dx[i] / dist
            body1.acceleration[i] += acc * body2.mass
            body2.acceleration[i] -= acc * body1.mass

def update_positions(bodies, dt):
    for body in bodies:
        for i in range(3):
            body.position[i] += body.velocity[i] * dt + 0.5 * body.acceleration[i] * dt * dt

def update_velocities(bodies, new_accelerations, dt):
    for body, new_a in zip(bodies, new_accelerations):
        for i in range(3):
            body.velocity[i] += 0.5 * (body.acceleration[i] + new_a[i]) * dt

def simulate(bodies, dt, steps):
    for step in range(steps):
        compute_gravitational_acceleration(bodies)
        # Save current accelerations for velocity update later
        old_accelerations = [body.acceleration[:] for body in bodies]
        update_positions(bodies, dt)
        compute_gravitational_acceleration(bodies)
        update_velocities(bodies, old_accelerations, dt)

        # Optional: print positions
        print(f"\nStep {step}")
        for body in bodies:
            print(f"{body.name}: pos={body.position}, vel={body.velocity}")

# Example masses (kg) and initial conditions (simplified and scaled)
sun = Body("Sun", 1.9885e30, [0, 0, 0], [0, 0, 0])
jupiter = Body("Jupiter", 1.898e27, [7.78e11, 0, 0], [0, 13070, 0])
saturn = Body("Saturn", 5.683e26, [1.43e12, 0, 0], [0, 9680, 0])
uranus = Body("Uranus", 8.681e25, [2.87e12, 0, 0], [0, 6800, 0])
neptune = Body("Neptune", 1.024e26, [4.5e12, 0, 0], [0, 5400, 0])

bodies = [sun, jupiter, saturn, uranus, neptune]

simulate(bodies, dt=60*60*24, steps=365)  # 1 year, 1-day steps

