#include <array>
#include <vector>

// 3D vector for position, velocity, force
struct Vec3 {
    double x, y, z;
    Vec3 operator+(Vec3 const& o) const noexcept { return {x+o.x, y+o.y, z+o.z}; }
    Vec3 operator-(Vec3 const& o) const noexcept { return {x-o.x, y-o.y, z-o.z}; }
    Vec3 operator*(double s) const noexcept { return {x*s, y*s, z*s}; }
    Vec3& operator+=(Vec3 const& o) noexcept { x+=o.x; y+=o.y; z+=o.z; return *this; }
    Vec3& operator*=(double s) noexcept { x*=s; y*=s; z*=s; return *this; }
};

// A celestial body: mass, current pos/vel, force accumulator
struct Body {
    double mass;
    Vec3 pos;
    Vec3 vel;
    Vec3 force;
};

const double G = 6.67430e-11;  // m^3 kg^-1 s^-2

// Zero all forces
void clear_forces(std::vector<Body>& bodies) {
    for(auto& b : bodies) b.force = {0,0,0};
}

// Compute pairwise gravitational forces
void compute_forces(std::vector<Body>& bodies) {
    clear_forces(bodies);
    size_t n = bodies.size();
    for(size_t i = 0; i < n; ++i) {
        for(size_t j = i+1; j < n; ++j) {
            Vec3 dr = bodies[j].pos - bodies[i].pos;
            double dist2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
            double dist = std::sqrt(dist2);
            double F = G * bodies[i].mass * bodies[j].mass / (dist2 * dist);
            Vec3 f = dr * F;  // direction built-in
            bodies[i].force += f;
            bodies[j].force -= f;
        }
    }
}

void velocity_verlet_step(std::vector<Body>& bodies, double dt) {
    // 1) compute initial forces
    compute_forces(bodies);
    
    // 2) update positions
    for(auto& b : bodies) {
        Vec3 accel = b.force * (1.0 / b.mass);
        b.pos += b.vel * dt + accel * (0.5 * dt*dt);
    }
    
    // 3) compute forces at new pos
    std::vector<Vec3> old_forces;
    old_forces.reserve(bodies.size());
    for(auto const& b : bodies) old_forces.push_back(b.force);
    compute_forces(bodies);
    
    // 4) update velocities
    for(size_t i = 0; i < bodies.size(); ++i) {
        Vec3 a_old = old_forces[i] * (1.0 / bodies[i].mass);
        Vec3 a_new = bodies[i].force * (1.0 / bodies[i].mass);
        bodies[i].vel += (a_old + a_new) * (0.5 * dt);
    }
}

#include <iostream>

// Example setup (masses in kg, positions in m, velocities in m/s)
int main() {
    std::vector<Body> bodies;
    bodies.reserve(5);
    
    // Sun
    bodies.push_back({1.9885e30, {0,0,0}, {0,0,0}});
    // Jupiter
    bodies.push_back({1.898e27, {7.785e11, 0, 0}, {0, 1.307e4, 0}});
    // Saturn
    bodies.push_back({5.683e26, {1.433e12, 0, 0}, {0, 9.69e3, 0}});
    // Uranus
    bodies.push_back({8.681e25, {2.877e12, 0, 0}, {0, 6.81e3, 0}});
    // Neptune
    bodies.push_back({1.024e26, {4.504e12, 0, 0}, {0, 5.43e3, 0}});

    double dt = 86400;               // one day in seconds
    int steps = 365 * 5;            // simulate 5 years
    
    for(int step = 0; step < steps; ++step) {
        velocity_verlet_step(bodies, dt);
        if(step % 30 == 0) {
            // print every ~month
            std::cout << "Day " << step << ":\n";
            for(auto const& b : bodies)
                std::cout << "  pos = (" << b.pos.x << ", " << b.pos.y << ", " << b.pos.z << ")\n";
        }
    }
    return 0;
}