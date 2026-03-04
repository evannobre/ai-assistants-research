/*
 * N-Body Simulation - Symplectic Euler Integrator
 * Backend Best Practices:
 * 1. Stack allocation for small, fixed-size data sets to avoid heap fragmentation.
 * 2. Pass-by-reference to reduce copying.
 * 3. Constants calculated at compile-time where possible.
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

// Constants
const double PI = 3.141592653589793;
const double SOLAR_MASS = 4 * PI * PI;
const double DAYS_PER_YEAR = 365.24;

struct Body {
    double x, y, z;
    double vx, vy, vz;
    double mass;
};

class NBodySystem {
private:
    std::vector<Body> bodies;

public:
    NBodySystem() {
        // Initialize bodies based on the provided ephemeris
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

    // Backend Best Practice: Ensure the system is balanced relative to the center of mass
    // to prevent the coordinate system from drifting.
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

    // The Symplectic Euler Step
    void advance(double dt) {
        const size_t n = bodies.size();

        // 1. Update Velocities based on Forces (pairwise)
        // We iterate unique pairs to save 50% of distance calculations
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                double dx = bodies[i].x - bodies[j].x;
                double dy = bodies[i].y - bodies[j].y;
                double dz = bodies[i].z - bodies[j].z;

                double distance_sq = dx * dx + dy * dy + dz * dz;
                double distance = std::sqrt(distance_sq);
                double mag = dt / (distance_sq * distance);

                // Force on body i
                bodies[i].vx -= dx * bodies[j].mass * mag;
                bodies[i].vy -= dy * bodies[j].mass * mag;
                bodies[i].vz -= dz * bodies[j].mass * mag;

                // Newton's 3rd Law: Force on body j is equal and opposite
                bodies[j].vx += dx * bodies[i].mass * mag;
                bodies[j].vy += dy * bodies[i].mass * mag;
                bodies[j].vz += dz * bodies[i].mass * mag;
            }
        }

        // 2. Update Positions based on NEW Velocities (Symplectic)
        for (size_t i = 0; i < n; ++i) {
            bodies[i].x += bodies[i].vx * dt;
            bodies[i].y += bodies[i].vy * dt;
            bodies[i].z += bodies[i].vz * dt;
        }
    }

    // Calculate total system energy (Kinetic + Potential) for verification
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

int main(int argc, char *argv[]) {
    // Parse command line argument for N steps
    int n = (argc > 1) ? std::stoi(argv[1]) : 1000;
    
    NBodySystem system;

    std::cout << std::fixed << std::setprecision(9);
    
    // Print Initial Energy
    std::cout << system.energy() << std::endl;

    // Simulation Loop
    double dt = 0.01;
    for (int i = 0; i < n; ++i) {
        system.advance(dt);
    }

    // Print Final Energy
    std::cout << system.energy() << std::endl;

    return 0;
}