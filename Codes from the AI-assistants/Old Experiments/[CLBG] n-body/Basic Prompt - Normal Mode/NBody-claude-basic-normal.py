#!/usr/bin/env python3
"""
N-Body Simulation using Symplectic Euler Integration
Simulates the Sun and four Jovian planets (Jupiter, Saturn, Uranus, Neptune)
"""

import math
import sys
import time

# Constants
SOLAR_MASS = 4 * math.pi * math.pi
DAYS_PER_YEAR = 365.24

class Body:
    """Represents a celestial body with position, velocity, and mass"""
    def __init__(self, x, y, z, vx, vy, vz, mass):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.mass = mass

def create_solar_system():
    """Initialize the solar system with Sun and Jovian planets"""
    bodies = []
    
    # Sun
    bodies.append(Body(
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        SOLAR_MASS
    ))
    
    # Jupiter
    bodies.append(Body(
        4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
        -6.90460016972063023e-05 * DAYS_PER_YEAR,
        9.54791938424326609e-04 * SOLAR_MASS
    ))
    
    # Saturn
    bodies.append(Body(
        8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
        -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        2.85885980666130812e-04 * SOLAR_MASS
    ))
    
    # Uranus
    bodies.append(Body(
        1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
        -2.96589568540237556e-05 * DAYS_PER_YEAR,
        4.36624404335156298e-05 * SOLAR_MASS
    ))
    
    # Neptune
    bodies.append(Body(
        1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
        -9.51592254519715870e-05 * DAYS_PER_YEAR,
        5.15138902046611451e-05 * SOLAR_MASS
    ))
    
    return bodies

def offset_momentum(bodies):
    """
    Offset momentum to ensure the center of mass remains stationary.
    This is important for energy conservation in the simulation.
    """
    px = py = pz = 0.0
    
    # Calculate total momentum
    for body in bodies:
        px += body.vx * body.mass
        py += body.vy * body.mass
        pz += body.vz * body.mass
    
    # Offset the Sun's velocity to make total momentum zero
    bodies[0].vx = -px / SOLAR_MASS
    bodies[0].vy = -py / SOLAR_MASS
    bodies[0].vz = -pz / SOLAR_MASS

def advance(bodies, dt):
    """
    Advance the simulation by one time step using symplectic Euler integration.
    
    Symplectic Euler method:
    1. Update velocities using current positions
    2. Update positions using new velocities
    
    This preserves energy better than standard Euler method for Hamiltonian systems.
    """
    n_bodies = len(bodies)
    
    # Step 1: Update velocities based on current positions
    for i in range(n_bodies):
        body_i = bodies[i]
        
        for j in range(i + 1, n_bodies):
            body_j = bodies[j]
            
            # Calculate distance vector
            dx = body_i.x - body_j.x
            dy = body_i.y - body_j.y
            dz = body_i.z - body_j.z
            
            # Calculate distance squared and distance
            dist_squared = dx*dx + dy*dy + dz*dz
            distance = math.sqrt(dist_squared)
            
            # Calculate gravitational force magnitude
            # F = G * m1 * m2 / r^2, but we use units where G = 1
            mag = dt / (dist_squared * distance)
            
            # Update velocities (Newton's third law: equal and opposite forces)
            body_i.vx -= dx * body_j.mass * mag
            body_i.vy -= dy * body_j.mass * mag
            body_i.vz -= dz * body_j.mass * mag
            
            body_j.vx += dx * body_i.mass * mag
            body_j.vy += dy * body_i.mass * mag
            body_j.vz += dz * body_i.mass * mag
    
    # Step 2: Update positions using new velocities
    for body in bodies:
        body.x += dt * body.vx
        body.y += dt * body.vy
        body.z += dt * body.vz

def energy(bodies):
    """Calculate total energy of the system (kinetic + potential)"""
    e = 0.0
    n_bodies = len(bodies)
    
    # Kinetic energy
    for body in bodies:
        e += 0.5 * body.mass * (body.vx*body.vx + body.vy*body.vy + body.vz*body.vz)
    
    # Potential energy
    for i in range(n_bodies):
        for j in range(i + 1, n_bodies):
            body_i = bodies[i]
            body_j = bodies[j]
            
            dx = body_i.x - body_j.x
            dy = body_i.y - body_j.y
            dz = body_i.z - body_j.z
            
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (body_i.mass * body_j.mass) / distance
    
    return e

def main():
    """Main simulation function"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        n_steps = int(sys.argv[1])
    else:
        n_steps = 50000000  # Default value for performance testing
    
    # Time step (in years)
    dt = 0.01
    
    print(f"N-Body Simulation")
    print(f"Bodies: Sun + 4 Jovian planets")
    print(f"Integration: Symplectic Euler")
    print(f"Time steps: {n_steps}")
    print(f"Time step size: {dt} years")
    print("-" * 40)
    
    # Initialize solar system
    bodies = create_solar_system()
    offset_momentum(bodies)
    
    # Calculate initial energy
    initial_energy = energy(bodies)
    print(f"Initial energy: {initial_energy:.9f}")
    
    # Run simulation
    start_time = time.time()
    
    for step in range(n_steps):
        advance(bodies, dt)
        
        # Print progress for long simulations
        if n_steps > 1000000 and step % (n_steps // 10) == 0:
            progress = (step / n_steps) * 100
            print(f"Progress: {progress:.1f}%")
    
    end_time = time.time()
    
    # Calculate final energy and energy drift
    final_energy = energy(bodies)
    energy_drift = abs((final_energy - initial_energy) / initial_energy)
    
    print("-" * 40)
    print(f"Final energy: {final_energy:.9f}")
    print(f"Energy drift: {energy_drift:.2e}")
    print(f"Simulation time: {end_time - start_time:.2f} seconds")
    print(f"Performance: {n_steps / (end_time - start_time):.0f} steps/second")
    
    # Print final positions
    print("\nFinal positions:")
    body_names = ["Sun", "Jupiter", "Saturn", "Uranus", "Neptune"]
    for i, body in enumerate(bodies):
        print(f"{body_names[i]}: ({body.x:.6f}, {body.y:.6f}, {body.z:.6f})")

if __name__ == "__main__":
    main()