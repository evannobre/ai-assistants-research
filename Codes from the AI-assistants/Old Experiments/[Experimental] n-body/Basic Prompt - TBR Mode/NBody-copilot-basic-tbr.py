import math

# Gravitational constant in SI units [m^3 kg^-1 s^-2]
G = 6.67430e-11

class Body:
    def __init__(self, name, mass, pos, vel):
        """
        Initialize a celestial body.
        :param name: String name of the body.
        :param mass: Mass in kilograms.
        :param pos: 3D position as a list [x, y, z] in meters.
        :param vel: 3D velocity as a list [vx, vy, vz] in m/s.
        """
        self.name = name
        self.mass = mass
        self.pos = pos  # position: [x, y, z]
        self.vel = vel  # velocity: [vx, vy, vz]
        self.acc = [0.0, 0.0, 0.0]  # acceleration: [ax, ay, az]

def compute_accelerations(bodies):
    """
    Compute accelerations for all bodies due to the gravitational force exerted by every other body.
    Uses Newton's law of universal gravitation:
         F = G * m1 * m2 / r^2   with a corresponding acceleration a = F / m.
    A small softening factor 'epsilon' is also included to avoid singularities when distances get very small.
    """
    # Reset accelerations to zero
    for body in bodies:
        body.acc = [0.0, 0.0, 0.0]
    n = len(bodies)
    
    # Loop over each unique pair of bodies
    for i in range(n):
        for j in range(i + 1, n):
            # Compute displacement vector from body i to body j
            dx = bodies[j].pos[0] - bodies[i].pos[0]
            dy = bodies[j].pos[1] - bodies[i].pos[1]
            dz = bodies[j].pos[2] - bodies[i].pos[2]
            
            # Calculate the distance with a softening parameter to avoid division by zero
            epsilon = 1e-3
            distance = math.sqrt(dx**2 + dy**2 + dz**2 + epsilon**2)
            
            # Calculate the force magnitude divided by distance^3 (this includes the normalization of the displacement vector)
            force = G * bodies[i].mass * bodies[j].mass / (distance**3)
            
            # Get the acceleration components due to this pair interaction
            ax = force * dx
            ay = force * dy
            az = force * dz
            
            # Newton's third law: update acceleration on body i (F/m_i)
            bodies[i].acc[0] += ax / bodies[i].mass
            bodies[i].acc[1] += ay / bodies[i].mass
            bodies[i].acc[2] += az / bodies[i].mass
            
            # and on body j with the opposite sign (F/m_j)
            bodies[j].acc[0] -= ax / bodies[j].mass
            bodies[j].acc[1] -= ay / bodies[j].mass
            bodies[j].acc[2] -= az / bodies[j].mass

def update_positions_and_velocities(bodies, dt):
    """
    Update the positions and velocities of all bodies using the Velocity Verlet integration algorithm.
    
    The Velocity Verlet algorithm works in two steps:
      1. Update positions using the current velocity and acceleration.
      2. Re-compute the accelerations with the updated positions.
      3. Update the velocities using the average of the old and new accelerations.
    
    This integrator is known for its good energy conservation properties when simulating gravitational systems.
    """
    # Update positions and take a half-step for velocity
    for body in bodies:
        # New position: r_new = r_old + v_old * dt + 0.5 * a_old * dt^2
        body.pos[0] += body.vel[0] * dt + 0.5 * body.acc[0] * dt * dt
        body.pos[1] += body.vel[1] * dt + 0.5 * body.acc[1] * dt * dt
        body.pos[2] += body.vel[2] * dt + 0.5 * body.acc[2] * dt * dt
        
        # Half-step of velocity: v_half = v_old + 0.5 * a_old * dt
        body.vel[0] += 0.5 * body.acc[0] * dt
        body.vel[1] += 0.5 * body.acc[1] * dt
        body.vel[2] += 0.5 * body.acc[2] * dt
    
    # Re-compute accelerations with the updated positions
    compute_accelerations(bodies)
    
    # Complete the velocity update with the new accelerations:
    for body in bodies:
        body.vel[0] += 0.5 * body.acc[0] * dt
        body.vel[1] += 0.5 * body.acc[1] * dt
        body.vel[2] += 0.5 * body.acc[2] * dt

# ------------------------------------------------------------------------------
# Example: Setup initial conditions for the Sun and one Jovian planet (e.g., Jupiter)
# ------------------------------------------------------------------------------
# Sun: mass (kg), position (m), and velocity (m/s)
sun = Body("Sun", 1.989e30, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])

# Jupiter: approximate mass (kg), average orbital radius (m), and orbital speed (m/s)
jupiter = Body("Jupiter", 1.898e27, [7.78e11, 0.0, 0.0], [0.0, 1.3e4, 0.0])

# You can add additional Jovian planets (or any other bodies) with their respective initial conditions.
bodies = [sun, jupiter]

# Simulation parameters:
dt = 60 * 60  # Time step: 1 hour in seconds
total_time = 365.25 * 24 * 60 * 60  # Total simulation time: 1 year in seconds

# Initialize accelerations based on starting conditions.
compute_accelerations(bodies)

# Main simulation loop.
# Here, we update the positions and velocities of all bodies at each time step.
t = 0.0
while t < total_time:
    update_positions_and_velocities(bodies, dt)
    t += dt
    # Optionally, output or store the positions for plotting or further analysis:
    # print(f"Time: {t} seconds")
    # for body in bodies:
    #     print(f"{body.name}: Position = {body.pos}, Velocity = {body.vel}")
