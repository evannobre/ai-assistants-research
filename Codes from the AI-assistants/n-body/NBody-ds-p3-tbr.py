import math
import sys
import array
import time
from itertools import combinations

# Constants
SOLAR_MASS = 4 * math.pi * math.pi
DAYS_PER_YEAR = 365.24
G = 1.0  # Gravitational constant (set to 1 in these units)

class Body:
    __slots__ = ('x', 'y', 'z', 'vx', 'vy', 'vz', 'mass')
    
    def __init__(self, pos, vel, mass):
        self.x, self.y, self.z = pos
        self.vx, self.vy, self.vz = vel
        self.mass = mass

def offset_momentum(bodies):
    """Adjust the Sun's velocity to offset system momentum"""
    px = py = pz = 0.0
    for b in bodies[1:]:  # All except Sun
        px += b.vx * b.mass
        py += b.vy * b.mass
        pz += b.vz * b.mass
    
    # Set Sun's velocity to offset total momentum
    sun = bodies[0]
    sun.vx = -px / SOLAR_MASS
    sun.vy = -py / SOLAR_MASS
    sun.vz = -pz / SOLAR_MASS

def compute_energy(bodies):
    """Compute total system energy"""
    e = 0.0
    n = len(bodies)
    
    # Kinetic energy
    for i in range(n):
        b = bodies[i]
        e += 0.5 * b.mass * (b.vx*b.vx + b.vy*b.vy + b.vz*b.vz)
    
    # Potential energy (avoid double counting with i<j)
    for i, j in combinations(range(n), 2):
        b1, b2 = bodies[i], bodies[j]
        dx = b1.x - b2.x
        dy = b1.y - b2.y
        dz = b1.z - b2.z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        e -= (G * b1.mass * b2.mass) / distance
    
    return e

def symplectic_euler(bodies, dt, steps):
    """Symplectic Euler integrator for n-body simulation"""
    n = len(bodies)
    
    # Pre-allocate acceleration arrays for better performance
    ax = array.array('d', [0.0] * n)
    ay = array.array('d', [0.0] * n)
    az = array.array('d', [0.0] * n)
    
    # Convert bodies to lists for faster indexing
    bodies_list = list(bodies)
    
    for _ in range(steps):
        # Reset accelerations
        for i in range(n):
            ax[i] = ay[i] = az[i] = 0.0
        
        # Compute pairwise accelerations (O(n²) but cache-friendly)
        for i in range(n):
            bi = bodies_list[i]
            for j in range(i + 1, n):
                bj = bodies_list[j]
                
                dx = bi.x - bj.x
                dy = bi.y - bj.y
                dz = bi.z - bj.z
                
                # Compute distance with softening to avoid singularities
                dist_sq = dx*dx + dy*dy + dz*dz + 1e-10
                dist = math.sqrt(dist_sq)
                inv_dist3 = G / (dist * dist_sq)
                
                # Mass-scaled factor for acceleration
                mj_inv_dist3 = bj.mass * inv_dist3
                mi_inv_dist3 = bi.mass * inv_dist3
                
                # Update accelerations
                ax_i = dx * mj_inv_dist3
                ay_i = dy * mj_inv_dist3
                az_i = dz * mj_inv_dist3
                
                ax_j = dx * mi_inv_dist3
                ay_j = dy * mi_inv_dist3
                az_j = dz * mi_inv_dist3
                
                ax[i] -= ax_i
                ay[i] -= ay_i
                az[i] -= az_i
                
                ax[j] += ax_j
                ay[j] += ay_j
                az[j] += az_j
        
        # Update velocities and positions using symplectic Euler
        for i in range(n):
            b = bodies_list[i]
            # Update velocities
            b.vx += ax[i] * dt
            b.vy += ay[i] * dt
            b.vz += az[i] * dt
            
            # Update positions using NEW velocities
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.z += b.vz * dt

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <number_of_steps>")
        sys.exit(1)
    
    steps = int(sys.argv[1])
    dt = 0.01  # Time step in years
    
    # Initialize bodies from ephemeris data
    bodies = [
        # Sun
        Body(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            SOLAR_MASS
        ),
        # Jupiter
        Body(
            (4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01),
            (1.66007664274403694e-03 * DAYS_PER_YEAR, 
             7.69901118419740425e-03 * DAYS_PER_YEAR, 
             -6.90460016972063023e-05 * DAYS_PER_YEAR),
            9.54791938424326609e-04 * SOLAR_MASS
        ),
        # Saturn
        Body(
            (8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01),
            (-2.76742510726862411e-03 * DAYS_PER_YEAR,
             4.99852801234917238e-03 * DAYS_PER_YEAR,
             2.30417297573763929e-05 * DAYS_PER_YEAR),
            2.85885980666130812e-04 * SOLAR_MASS
        ),
        # Uranus
        Body(
            (1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01),
            (2.96460137564761618e-03 * DAYS_PER_YEAR,
             2.37847173959480950e-03 * DAYS_PER_YEAR,
             -2.96589568540237556e-05 * DAYS_PER_YEAR),
            4.36624404335156298e-05 * SOLAR_MASS
        ),
        # Neptune
        Body(
            (1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01),
            (2.68067772490389322e-03 * DAYS_PER_YEAR,
             1.62824170038242295e-03 * DAYS_PER_YEAR,
             -9.51592254519715870e-05 * DAYS_PER_YEAR),
            5.15138902046611451e-05 * SOLAR_MASS
        )
    ]
    
    # Adjust Sun's velocity to conserve momentum
    offset_momentum(bodies)
    
    # Print initial energy
    print(f"Initial total energy: {compute_energy(bodies):.9f}")
    
    # Run simulation
    start_time = time.time()
    symplectic_euler(bodies, dt, steps)
    elapsed_time = time.time() - start_time
    
    # Print final energy and performance
    print(f"Final total energy: {compute_energy(bodies):.9f}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Steps per second: {steps/elapsed_time:.0f}")

if __name__ == "__main__":
    main()