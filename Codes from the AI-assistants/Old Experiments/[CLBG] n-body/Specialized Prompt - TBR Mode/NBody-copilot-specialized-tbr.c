#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Define constants for the simulation.
#define PI 3.141592653589793
#define SOLAR_MASS (4 * PI * PI)
#define DAYS_PER_YEAR 365.24

// Data structure to represent a 3D vector.
typedef struct {
    double x, y, z;
} Vector;

// Data structure for a celestial body.
typedef struct {
    Vector pos;  // position
    Vector vel;  // velocity
    double mass;
} Body;

// Total number of bodies in our simulation.
#define N_BODIES 5

// Adjust the Sun's velocity to offset total momentum to zero,
// ensuring the center-of-mass remains at rest.
void offset_momentum(Body bodies[]) {
    double px = 0.0, py = 0.0, pz = 0.0;
    for (int i = 0; i < N_BODIES; ++i) {
        px += bodies[i].vel.x * bodies[i].mass;
        py += bodies[i].vel.y * bodies[i].mass;
        pz += bodies[i].vel.z * bodies[i].mass;
    }
    // For stability we adjust the Sun (index 0) so that total momentum is zero.
    bodies[0].vel.x = -px / SOLAR_MASS;
    bodies[0].vel.y = -py / SOLAR_MASS;
    bodies[0].vel.z = -pz / SOLAR_MASS;
}

// The advance() function performs the simulation over nSteps using dt as the timestep.
// It follows the Euler symplectic integration scheme by first updating velocities (the momentum)
// and then positions.
void advance(Body bodies[], double dt, int nSteps) {
    for (int step = 0; step < nSteps; ++step) {
        // Update velocities: compute pairwise interactions between bodies.
        for (int i = 0; i < N_BODIES; ++i) {
            for (int j = i + 1; j < N_BODIES; ++j) {
                double dx = bodies[i].pos.x - bodies[j].pos.x;
                double dy = bodies[i].pos.y - bodies[j].pos.y;
                double dz = bodies[i].pos.z - bodies[j].pos.z;
                double distanceSq = dx * dx + dy * dy + dz * dz;
                double distance = sqrt(distanceSq);
                // The magnitude factor dt / (distance^3) appears in the gravitational update.
                double mag = dt / (distanceSq * distance);

                // Update velocities with the contribution of each pair’s gravitational force.
                bodies[i].vel.x -= dx * bodies[j].mass * mag;
                bodies[i].vel.y -= dy * bodies[j].mass * mag;
                bodies[i].vel.z -= dz * bodies[j].mass * mag;
                bodies[j].vel.x += dx * bodies[i].mass * mag;
                bodies[j].vel.y += dy * bodies[i].mass * mag;
                bodies[j].vel.z += dz * bodies[i].mass * mag;
            }
        }
        // Update positions using the newly updated velocities.
        for (int i = 0; i < N_BODIES; ++i) {
            bodies[i].pos.x += dt * bodies[i].vel.x;
            bodies[i].pos.y += dt * bodies[i].vel.y;
            bodies[i].pos.z += dt * bodies[i].vel.z;
        }
    }
}

// Compute the system's total energy (kinetic + potential) to help verify conservation.
double compute_energy(Body bodies[]) {
    double energy = 0.0;
    for (int i = 0; i < N_BODIES; ++i) {
        // Kinetic energy: 1/2 m v^2.
        double vx = bodies[i].vel.x;
        double vy = bodies[i].vel.y;
        double vz = bodies[i].vel.z;
        energy += 0.5 * bodies[i].mass * (vx * vx + vy * vy + vz * vz);
        
        // Potential energy: gravitational potential energy.
        for (int j = i + 1; j < N_BODIES; ++j) {
            double dx = bodies[i].pos.x - bodies[j].pos.x;
            double dy = bodies[i].pos.y - bodies[j].pos.y;
            double dz = bodies[i].pos.z - bodies[j].pos.z;
            double distance = sqrt(dx * dx + dy * dy + dz * dz);
            energy -= (bodies[i].mass * bodies[j].mass) / distance;
        }
    }
    return energy;
}

// Main function where we initialize the simulation and run it.
// A command-line argument specifies the number of iterations (e.g., 50000000)
int main(int argc, char **argv) {
    // Default number of simulation steps.
    int nSteps = 50000000;
    if (argc > 1) {
        nSteps = atoi(argv[1]);
    }
    
    // Time step dt for the simulation.
    double dt = 0.01;
    
    // Define the five bodies with their initial positions, velocities, and masses.
    Body bodies[N_BODIES] = {
        // Sun
        {
            { 0.0, 0.0, 0.0 },
            { 0.0, 0.0, 0.0 },
            SOLAR_MASS
        },
        // Jupiter
        {
            { 4.84143144246472090e+00,  -1.16032004402742839e+00, -1.03622044471123109e-01 },
            { 1.66007664274403694e-03 * DAYS_PER_YEAR,  7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR },
            9.54791938424326609e-04 * SOLAR_MASS
        },
        // Saturn
        {
            { 8.34336671824457987e+00,  4.12479856412430479e+00, -4.03523417114321381e-01 },
            { -2.76742510726862411e-03 * DAYS_PER_YEAR,  4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR },
            2.85885980666130812e-04 * SOLAR_MASS
        },
        // Uranus
        {
            { 1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01 },
            { 2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR },
            4.36624404335156298e-05 * SOLAR_MASS
        },
        // Neptune
        {
            { 1.53796971148509165e+01, -2.59193146099879641e+01,  1.79258772950371181e-01 },
            { 2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR },
            5.15138902046611451e-05 * SOLAR_MASS
        }
    };
    
    // Adjust the momentum so that the system's center-of-mass is initially stationary.
    offset_momentum(bodies);
    
    // Run the simulation for the provided number of steps.
    advance(bodies, dt, nSteps);
    
    // Compute the final energy of the system as a simple check.
    double energy = compute_energy(bodies);
    printf("Final energy: %.9f\n", energy);
    
    return 0;
}
