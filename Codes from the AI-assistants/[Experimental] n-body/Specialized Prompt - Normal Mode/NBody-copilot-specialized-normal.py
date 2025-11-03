import numpy as np

# Gravitational constant (AU^3 / (Solar Mass * Day^2))
G = 39.478

class Body:
    def __init__(self, name, mass, position, velocity):
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)

def acceleration(bodies):
    """Compute acceleration due to gravity."""
    n = len(bodies)
    acc = np.zeros((n, 3), dtype=np.float64)
    
    for i in range(n):
        for j in range(n):
            if i != j:
                r_vec = bodies[j].position - bodies[i].position
                r_mag = np.linalg.norm(r_vec)
                acc[i] += G * bodies[j].mass * r_vec / (r_mag**3)
    return acc

def velocity_verlet(bodies, dt):
    """Velocity Verlet integration step."""
    acc = acceleration(bodies)

    for i, body in enumerate(bodies):
        body.position += body.velocity * dt + 0.5 * acc[i] * dt**2
    
    new_acc = acceleration(bodies)
    
    for i, body in enumerate(bodies):
        body.velocity += 0.5 * (acc[i] + new_acc[i]) * dt

# Define Sun and Jovian planets (masses in Solar Mass, positions in AU, velocities in AU/day)
bodies = [
    Body("Sun", 1.0, [0, 0, 0], [0, 0, 0]),
    Body("Jupiter", 0.0009543, [5.2, 0, 0], [0, 2.754, 0]),
    Body("Saturn", 0.0002857, [9.58, 0, 0], [0, 2.033, 0]),
    Body("Uranus", 0.0000436, [19.22, 0, 0], [0, 1.438, 0]),
    Body("Neptune", 0.0000515, [30.05, 0, 0], [0, 1.158, 0])
]

# Simulation parameters
dt = 1  # Time step in days
num_steps = 365 * 10  # 10 years

for _ in range(num_steps):
    velocity_verlet(bodies, dt)

# Print final positions
for body in bodies:
    print(f"{body.name}: {body.position}")
