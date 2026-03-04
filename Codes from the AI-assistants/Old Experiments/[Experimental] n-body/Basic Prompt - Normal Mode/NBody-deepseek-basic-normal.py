import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import sqrt

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
DAYS_TO_SECONDS = 86400

# Body data (mass in kg, initial positions/velocities in m and m/s)
# Using approximate values for the Jovian system (Sun + Galilean moons)
def get_bodies():
    return {
        'Sun': {
            'mass': 1.989e30,
            'position': [0, 0, 0],
            'velocity': [0, 0, 0],
            'color': 'yellow',
            'radius': 20
        },
        'Jupiter': {
            'mass': 1.898e27,
            'position': [7.785e11, 0, 0],  # ~5.2 AU
            'velocity': [0, 1.3e4, 0],     # Approx orbital velocity
            'color': 'orange',
            'radius': 10
        },
        'Io': {
            'mass': 8.932e22,
            'position': [7.785e11 + 4.217e8, 0, 0],
            'velocity': [0, 1.7e4, 0],
            'color': 'white',
            'radius': 5
        },
        'Europa': {
            'mass': 4.8e22,
            'position': [7.785e11 + 6.709e8, 0, 0],
            'velocity': [0, 1.4e4, 0],
            'color': 'blue',
            'radius': 4
        },
        'Ganymede': {
            'mass': 1.482e23,
            'position': [7.785e11 + 1.07e9, 0, 0],
            'velocity': [0, 1.1e4, 0],
            'color': 'green',
            'radius': 6
        },
        'Callisto': {
            'mass': 1.076e23,
            'position': [7.785e11 + 1.883e9, 0, 0],
            'velocity': [0, 8.2e3, 0],
            'color': 'gray',
            'radius': 5
        }
    }

def compute_accelerations(bodies, positions):
    n = len(bodies)
    accelerations = np.zeros((n, 3))
    body_names = list(bodies.keys())
    masses = [bodies[name]['mass'] for name in body_names]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                r = positions[j] - positions[i]
                distance = np.linalg.norm(r)
                accelerations[i] += G * masses[j] * r / (distance ** 3)
                
    return accelerations

def n_body_equations(t, y, bodies):
    n = len(bodies)
    body_names = list(bodies.keys())
    
    # Split y into positions and velocities
    positions = y[:3*n].reshape(n, 3)
    velocities = y[3*n:].reshape(n, 3)
    
    # Compute accelerations
    accelerations = compute_accelerations(bodies, positions)
    
    # Pack derivatives
    derivatives = np.zeros(6*n)
    derivatives[:3*n] = velocities.flatten()
    derivatives[3*n:] = accelerations.flatten()
    
    return derivatives

def run_simulation(days=365, dt=1):
    bodies = get_bodies()
    body_names = list(bodies.keys())
    n = len(bodies)
    
    # Initial conditions (positions and velocities concatenated)
    y0 = np.zeros(6*n)
    for i, name in enumerate(body_names):
        y0[3*i:3*i+3] = bodies[name]['position']
        y0[3*n + 3*i:3*n + 3*i+3] = bodies[name]['velocity']
    
    # Time span (convert days to seconds)
    t_span = (0, days * DAYS_TO_SECONDS)
    t_eval = np.arange(0, days * DAYS_TO_SECONDS, dt * DAYS_TO_SECONDS)
    
    # Solve the ODE
    solution = solve_ivp(
        fun=n_body_equations,
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        args=(bodies,),
        method='DOP853',
        rtol=1e-10,
        atol=1e-13
    )
    
    return solution, bodies

def plot_results(solution, bodies):
    body_names = list(bodies.keys())
    n = len(bodies)
    
    # Extract positions for each body
    positions = solution.y[:3*n].reshape(n, 3, -1)
    
    plt.figure(figsize=(10, 10))
    
    # Plot orbits
    for i, name in enumerate(body_names):
        plt.plot(positions[i, 0, :], positions[i, 1, :], 
                label=name, color=bodies[name]['color'])
    
    plt.xlabel('X position (m)')
    plt.ylabel('Y position (m)')
    plt.title('Orbits of Jovian System')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def animate_results(solution, bodies):
    body_names = list(bodies.keys())
    n = len(bodies)
    positions = solution.y[:3*n].reshape(n, 3, -1)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-2e12, 2e12)
    ax.set_ylim(-2e12, 2e12)
    
    # Create artists for each body
    artists = []
    for i, name in enumerate(body_names):
        artist = ax.scatter([], [], s=bodies[name]['radius'], 
                          color=bodies[name]['color'], label=name)
        artists.append(artist)
    
    def update(frame):
        for i in range(n):
            artists[i].set_offsets(positions[i, :2, frame])
        return artists
    
    ani = FuncAnimation(fig, update, frames=positions.shape[2], 
                        interval=50, blit=True)
    plt.legend()
    plt.title('Jovian System Simulation')
    plt.xlabel('X position (m)')
    plt.ylabel('Y position (m)')
    plt.show()
    
    return ani

# Run the simulation
if __name__ == "__main__":
    solution, bodies = run_simulation(days=30, dt=0.1)
    plot_results(solution, bodies)
    # animate_results(solution, bodies)  # Uncomment for animation