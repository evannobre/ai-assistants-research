import math

# Gravitational constant in SI units (m³ kg⁻¹ s⁻²)
G = 6.67430e-11

class Body:
    """
    Represents a celestial body.
    Attributes:
        name (str): The name of the body.
        mass (float): Mass of the body in kg.
        position (tuple): 3D position as (x,y,z) in meters.
        velocity (tuple): 3D velocity as (vx,vy,vz) in m/s.
    """
    def __init__(self, name, mass, position, velocity):
        self.name = name
        self.mass = mass
        self.position = position  # (x, y, z)
        self.velocity = velocity  # (vx, vy, vz)

def compute_acceleration(bodies, i):
    """
    For the body at index i in the list 'bodies', compute the acceleration due to gravity
    from all other bodies.
    Formula:
      a_i = Σ_{j ≠ i} G * m_j * (r_j - r_i) / |r_j - r_i|³
    """
    xi, yi, zi = bodies[i].position
    ax, ay, az = 0.0, 0.0, 0.0
    for j, body in enumerate(bodies):
        if i == j:
            continue
        xj, yj, zj = body.position
        dx = xj - xi
        dy = yj - yi
        dz = zj - zi
        # Compute squared distance and actual distance
        dist_sq = dx * dx + dy * dy + dz * dz
        dist = math.sqrt(dist_sq)
        # Use the formula for gravitational acceleration.
        # We divide by the cube of the distance to combine the direction (dx,dy,dz)
        factor = G * body.mass / (dist_sq * dist)
        ax += dx * factor
        ay += dy * factor
        az += dz * factor
    return (ax, ay, az)

def velocity_verlet_step(bodies, dt):
    """
    Advances the simulation by one time step (dt seconds) using the velocity Verlet integration.
    
    Steps:
      1. Compute the accelerations for each body.
      2. Update positions:
            r(t+dt) = r(t) + v(t)*dt + 0.5*a(t)*dt²
      3. Compute new accelerations with the updated positions.
      4. Update velocities:
            v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
    """
    # Compute current accelerations for all bodies
    accelerations = [compute_acceleration(bodies, i) for i in range(len(bodies))]
    
    # Update positions for each body
    for i, body in enumerate(bodies):
        new_position = tuple(
            body.position[k] + body.velocity[k] * dt + 0.5 * accelerations[i][k] * dt * dt
            for k in range(3)
        )
        body.position = new_position

    # Compute new accelerations after position update
    new_accelerations = [compute_acceleration(bodies, i) for i in range(len(bodies))]
    
    # Update velocities using the average of old and new accelerations
    for i, body in enumerate(bodies):
        new_velocity = tuple(
            body.velocity[k] + 0.5 * (accelerations[i][k] + new_accelerations[i][k]) * dt
            for k in range(3)
        )
        body.velocity = new_velocity

def main():
    """
    Sets up a simulation for the Sun and four Jovian planets using approximate initial conditions.
    The values below represent:
      - Masses in kg.
      - Positions (in meters) along the x-axis (for simplicity, positions are chosen assuming circular orbits).
      - Velocities (in m/s) are perpendicular to the position vector, yielding roughly circular motion.
    
    For example:
      - Sun at the origin.
      - Jupiter at ~7.785e11 m with ~1.307e4 m/s in the y-direction.
      - Saturn, Uranus, and Neptune with approximate orbital radii and speeds.
    """
    bodies = [
        Body("Sun", 1.98847e30, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        Body("Jupiter", 1.898e27, (7.785e11, 0.0, 0.0), (0.0, 1.307e4, 0.0)),
        Body("Saturn", 5.683e26, (1.433e12, 0.0, 0.0), (0.0, 9.68e3, 0.0)),
        Body("Uranus", 8.681e25, (2.87e12, 0.0, 0.0), (0.0, 6.80e3, 0.0)),
        Body("Neptune", 1.024e26, (4.5e12, 0.0, 0.0), (0.0, 5.43e3, 0.0))
    ]
    
    # Simulation parameters
    dt = 60.0   # time step in seconds (roughly 1 minute per iteration)
    simulation_duration = 10 * 365.25 * 24 * 3600  # simulate 10 years (in seconds)
    steps = int(simulation_duration / dt)

    print("Starting simulation...")
    # Main simulation loop
    for step in range(steps):
        velocity_verlet_step(bodies, dt)
        
        # To avoid extensive output, log positions every 10,000 steps.
        if step % 10000 == 0:
            print(f"Step {step}:")
            for body in bodies:
                pos = body.position  # Position is a tuple (x, y, z)
                vel = body.velocity  # Velocity is a tuple (vx, vy, vz)
                print(f"  {body.name}: Position = {pos}, Velocity = {vel}")
    
    print("Simulation complete.")

if __name__ == "__main__":
    main()
