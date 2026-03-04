#!/usr/bin/env python3
"""
N-Body simulation using symplectic Euler integrator.
Simulates the Sun and Jovian planets (Jupiter, Saturn, Uranus, Neptune).
"""

import sys
import numpy as np

# Constants
SOLAR_MASS = 4 * np.pi * np.pi
DAYS_PER_YEAR = 365.24

# Body data: [x, y, z, vx, vy, vz, mass]
def init_bodies():
    """Initialize the celestial bodies with their positions, velocities, and masses."""
    bodies = np.array([
        # Sun
        [0.0, 0.0, 0.0,
         0.0, 0.0, 0.0,
         SOLAR_MASS],
        
        # Jupiter
        [4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR,
         7.69901118419740425e-03 * DAYS_PER_YEAR,
         -6.90460016972063023e-05 * DAYS_PER_YEAR,
         9.54791938424326609e-04 * SOLAR_MASS],
        
        # Saturn
        [8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR,
         4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR,
         2.85885980666130812e-04 * SOLAR_MASS],
        
        # Uranus
        [1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR,
         2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR,
         4.36624404335156298e-05 * SOLAR_MASS],
        
        # Neptune
        [1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR,
         1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR,
         5.15138902046611451e-05 * SOLAR_MASS]
    ], dtype=np.float64)
    
    return bodies

def offset_momentum(bodies):
    """
    Offset the momentum of the system so that the total momentum is zero.
    This puts the center of mass at rest.
    """
    n = len(bodies)
    px = py = pz = 0.0
    
    for i in range(n):
        m = bodies[i, 6]  # mass
        px += bodies[i, 3] * m  # vx * mass
        py += bodies[i, 4] * m  # vy * mass
        pz += bodies[i, 5] * m  # vz * mass
    
    # Set Sun's velocity to offset total momentum
    bodies[0, 3] = -px / SOLAR_MASS
    bodies[0, 4] = -py / SOLAR_MASS
    bodies[0, 5] = -pz / SOLAR_MASS

def energy(bodies):
    """Calculate the total energy of the system (kinetic + potential)."""
    n = len(bodies)
    e = 0.0
    
    # Kinetic energy
    for i in range(n):
        vx, vy, vz = bodies[i, 3:6]
        m = bodies[i, 6]
        e += 0.5 * m * (vx*vx + vy*vy + vz*vz)
    
    # Potential energy
    for i in range(n):
        x1, y1, z1 = bodies[i, 0:3]
        m1 = bodies[i, 6]
        
        for j in range(i + 1, n):
            x2, y2, z2 = bodies[j, 0:3]
            m2 = bodies[j, 6]
            
            dx = x1 - x2
            dy = y1 - y2
            dz = z1 - z2
            
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            e -= (m1 * m2) / distance
    
    return e

def advance(bodies, dt):
    """
    Advance the simulation by one time step using symplectic Euler integration.
    This is a simple but stable integration method for Hamiltonian systems.
    """
    n = len(bodies)
    
    # Update velocities based on gravitational forces
    for i in range(n):
        x1, y1, z1 = bodies[i, 0:3]
        m1 = bodies[i, 6]
        
        for j in range(i + 1, n):
            x2, y2, z2 = bodies[j, 0:3]
            m2 = bodies[j, 6]
            
            dx = x1 - x2
            dy = y1 - y2
            dz = z1 - z2
            
            dist_sq = dx*dx + dy*dy + dz*dz
            distance = np.sqrt(dist_sq)
            mag = dt / (dist_sq * distance)
            
            # Update velocities (symplectic Euler: v += a*dt)
            bodies[i, 3] -= dx * m2 * mag
            bodies[i, 4] -= dy * m2 * mag
            bodies[i, 5] -= dz * m2 * mag
            
            bodies[j, 3] += dx * m1 * mag
            bodies[j, 4] += dy * m1 * mag
            bodies[j, 5] += dz * m1 * mag
    
    # Update positions based on new velocities
    for i in range(n):
        bodies[i, 0] += dt * bodies[i, 3]  # x += vx * dt
        bodies[i, 1] += dt * bodies[i, 4]  # y += vy * dt
        bodies[i, 2] += dt * bodies[i, 5]  # z += vz * dt

def simulate(n_steps):
    """Run the n-body simulation for the specified number of steps."""
    bodies = init_bodies()
    offset_momentum(bodies)
    
    print(f"Initial energy: {energy(bodies):.9f}")
    
    dt = 0.01  # Time step in days
    
    for _ in range(n_steps):
        advance(bodies, dt)
    
    print(f"Final energy:   {energy(bodies):.9f}")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    simulate(n)
