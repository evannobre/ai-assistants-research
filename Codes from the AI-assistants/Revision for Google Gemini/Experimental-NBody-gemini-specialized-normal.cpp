#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <iomanip>
#include <cstdlib>

const double PI = 3.141592653589793;
const double SOLAR_MASS = 4 * PI * PI;
const double DAYS_PER_YEAR = 365.24;

struct Body {
    double x, y, z;
    double vx, vy, vz;
    double mass;
};

// Standard benchmark orbital data for the Jovian planets and the Sun
std::vector<Body> get_initial_state() {
    return {
        // Sun
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS},
        // Jupiter
        {4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR,
         -6.90460016972063023e-05 * DAYS_PER_YEAR, 9.54791938424326609e-04 * SOLAR_MASS},
        // Saturn
        {8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR, 2.85885980666130812e-04 * SOLAR_MASS},
        // Uranus
        {1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR, 4.36624404335156298e-05 * SOLAR_MASS},
        // Neptune
        {1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR, 5.15138902046611451e-05 * SOLAR_MASS}
    };
}

// Offset the Sun's initial velocity to ensure the center of mass is stationary
void offset_momentum(std::vector<Body>& bodies) {
    double px = 0.0, py = 0.0, pz = 0.0;
    for (const auto& b : bodies) {
        px += b.vx * b.mass;
        py += b.vy * b.mass;
        pz += b.vz * b.mass;
    }
    bodies[0].vx = -px / SOLAR_MASS;
    bodies[0].vy = -py / SOLAR_MASS;
    bodies[0].vz = -pz / SOLAR_MASS;
}

// Compute the total orbital energy of the system to verify physics stability
double calculate_energy(const std::vector<Body>& bodies) {
    double e = 0.0;
    for (size_t i = 0; i < bodies.size(); ++i) {
        e += 0.5 * bodies[i].mass * (bodies[i].vx * bodies[i].vx + 
                                     bodies[i].vy * bodies[i].vy + 
                                     bodies[i].vz * bodies[i].vz);
        for (size_t j = i + 1; j < bodies.size(); ++j) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;
            double distance = std::sqrt(dx*dx + dy*dy + dz*dz);
            e -= (bodies[i].mass * bodies[j].mass) / distance;
        }
    }
    return e;
}

// Advance the system by dt using Symplectic Euler integration
void advance(std::vector<Body>& bodies, double dt) {
    size_t n = bodies.size();
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = i + 1; j < n; ++j) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;
            
            double dist_sq = dx*dx + dy*dy + dz*dz;
            double mag = dt / (dist_sq * std::sqrt(dist_sq));
            
            double i_mass_mag = bodies[i].mass * mag;
            double j_mass_mag = bodies[j].mass * mag;
            
            bodies[i].vx -= dx * j_mass_mag;
            bodies[i].vy -= dy * j_mass_mag;
            bodies[i].vz -= dz * j_mass_mag;
            
            bodies[j].vx += dx * i_mass_mag;
            bodies[j].vy += dy * i_mass_mag;
            bodies[j].vz += dz * i_mass_mag;
        }
    }
    
    for (size_t i = 0; i < n; ++i) {
        bodies[i].x += dt * bodies[i].vx;
        bodies[i].y += dt * bodies[i].vy;
        bodies[i].z += dt * bodies[i].vz;
    }
}

int main(int argc, char* argv[]) {
    // 1. Process command-line arguments for performance evaluation
    int iterations = 1000000; // Default to 1M iterations if no arg provided
    if (argc > 1) {
        iterations = std::atoi(argv[1]);
    }

    std::vector<Body> bodies = get_initial_state();
    offset_momentum(bodies);

    std::cout << std::fixed << std::setprecision(9);
    std::cout << "Initial Energy: " << calculate_energy(bodies) << "\n";

    // 2. Start Performance Timer
    auto start_time = std::chrono::high_resolution_clock::now();

    // 3. Core Algorithm Loop
    const double dt = 0.01;
    for (int i = 0; i < iterations; ++i) {
        advance(bodies, dt);
    }

    // 4. End Performance Timer
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    std::cout << "Final Energy:   " << calculate_energy(bodies) << "\n";
    std::cout << "Execution Time: " << elapsed.count() << " seconds for " 
              << iterations << " steps.\n";

    return 0;
}