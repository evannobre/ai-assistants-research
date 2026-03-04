/*
 * N-Body Simulation
 * Algorithm: Symplectic Euler Integrator
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>

// Mathematical Constants
constexpr double PI = 3.141592653589793;
constexpr double SOLAR_MASS = 4 * PI * PI;
constexpr double DAYS_PER_YEAR = 365.24;

struct Body {
    double x, y, z;       // Position
    double vx, vy, vz;    // Velocity
    double mass;          // Mass
};

class NBodySystem {
private:
    std::vector<Body> bodies;

public:
    NBodySystem() {
        // Initialize Solar System bodies based on the provided ephemeris
        
        // Sun
        bodies.push_back({
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            SOLAR_MASS
        });

        // Jupiter
        bodies.push_back({
            4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
            1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
            9.54791938424326609e-04 * SOLAR_MASS
        });

        // Saturn
        bodies.push_back({
            8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
            -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
            2.85885980666130812e-04 * SOLAR_MASS
        });

        // Uranus
        bodies.push_back({
            1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
            2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
            4.36624404335156298e-05 * SOLAR_MASS
        });

        // Neptune
        bodies.push_back({
            1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
            2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
            5.15138902046611451e-05 * SOLAR_MASS
        });

        offset_momentum();
    }

    // Offset the Sun's momentum to ensure the system's center of mass is static
    void offset_momentum() {
        double px = 0.0, py = 0.0, pz = 0.0;
        for (const auto& body : bodies) {
            px += body.vx * body.mass;
            py += body.vy * body.mass;
            pz += body.vz * body.mass;
        }
        bodies[0].vx = -px / SOLAR_MASS;
        bodies[0].vy = -py / SOLAR_MASS;
        bodies[0].vz = -pz / SOLAR_MASS;
    }

    // Advance the system by time step dt
    void advance(double dt) {
        const size_t n = bodies.size();
        
        // 1. Update Velocities using Newton's Law of Gravitation
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                double dx = bodies[i].x - bodies[j].x;
                double dy = bodies[i].y - bodies[j].y;
                double dz = bodies[i].z - bodies[j].z;

                double distance_sq = dx * dx + dy * dy + dz * dz;
                double distance = std::sqrt(distance_sq);
                double mag = dt / (distance_sq * distance);

                // Newton's 3rd Law: Apply equal and opposite forces
                double mass_j_mag = bodies[j].mass * mag;
                bodies[i].vx -= dx * mass_j_mag;
                bodies[i].vy -= dy * mass_j_mag;
                bodies[i].vz -= dz * mass_j_mag;

                double mass_i_mag = bodies[i].mass * mag;
                bodies[j].vx += dx * mass_i_mag;
                bodies[j].vy += dy * mass_i_mag;
                bodies[j].vz += dz * mass_i_mag;
            }
        }

        // 2. Update Positions (Symplectic Euler uses new velocity)
        for (auto& body : bodies) {
            body.x += dt * body.vx;
            body.y += dt * body.vy;
            body.z += dt * body.vz;
        }
    }

    // Calculate total system energy (Potential + Kinetic)
    double energy() {
        double e = 0.0;
        const size_t n = bodies.size();

        for (size_t i = 0; i < n; ++i) {
            // Kinetic Energy: 0.5 * m * v^2
            e += 0.5 * bodies[i].mass * (bodies[i].vx * bodies[i].vx +
                                         bodies[i].vy * bodies[i].vy +
                                         bodies[i].vz * bodies[i].vz);

            // Potential Energy: - (G * m1 * m2) / r
            for (size_t j = i + 1; j < n; ++j) {
                double dx = bodies[i].x - bodies[j].x;
                double dy = bodies[i].y - bodies[j].y;
                double dz = bodies[i].z - bodies[j].z;
                double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                e -= (bodies[i].mass * bodies[j].mass) / distance;
            }
        }
        return e;
    }
};

int main(int argc, char* argv[]) {
    // Parse command line argument for iterations
    int n = 1000;
    if (argc > 1) {
        n = std::stoi(argv[1]);
    }

    NBodySystem system;
    
    // Print initial energy
    std::cout << std::fixed << std::setprecision(9) << system.energy() << std::endl;

    // Run simulation
    double dt = 0.01;
    for (int i = 0; i < n; ++i) {
        system.advance(dt);
    }

    // Print final energy
    std::cout << std::fixed << std::setprecision(9) << system.energy() << std::endl;

    return 0;
}