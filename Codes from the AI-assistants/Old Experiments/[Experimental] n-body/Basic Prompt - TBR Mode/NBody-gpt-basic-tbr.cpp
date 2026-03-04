#include <vector>
#include <array>
#include <cmath>

// 3D vector for position, velocity, acceleration
struct Vec3 {
    double x, y, z;
    Vec3 operator+(const Vec3& o) const { return {x+o.x, y+o.y, z+o.z}; }
    Vec3 operator-(const Vec3& o) const { return {x-o.x, y-o.y, z-o.z}; }
    Vec3 operator*(double s)   const { return {x*s,   y*s,   z*s  }; }
    Vec3& operator+=(const Vec3& o) { x+=o.x; y+=o.y; z+=o.z; return *this; }
};

// Body holds mass, pos, vel, and a working accel
struct Body {
    double mass;
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;  // current acceleration
};

void compute_accelerations(std::vector<Body>& bodies) {
    const double G = 6.67430e-11;  // m^3 kg^-1 s^-2
    size_t N = bodies.size();
    // Zero out accelerations
    for (auto& b : bodies) b.acc = {0,0,0};

    // Pairwise force summation, O(N^2)
    for (size_t i = 0; i < N; ++i) {
        for (size_t j = i+1; j < N; ++j) {
            Vec3 r = bodies[j].pos - bodies[i].pos;
            double dist2 = r.x*r.x + r.y*r.y + r.z*r.z;
            double invDist3 = 1.0 / (std::sqrt(dist2) * dist2);
            Vec3 a = r * (G * invDist3 * bodies[j].mass);
            bodies[i].acc += a;
            // action = −reaction
            bodies[j].acc += r * (-G * invDist3 * bodies[i].mass);
        }
    }
}

void step_leapfrog(std::vector<Body>& bodies, double dt) {
    // 1) half-kick
    for (auto& b : bodies) {
        b.vel += b.acc * (0.5 * dt);
    }

    // 2) drift
    for (auto& b : bodies) {
        b.pos += b.vel * dt;
    }

    // 3) recompute accelerations
    compute_accelerations(bodies);

    // 4) half-kick
    for (auto& b : bodies) {
        b.vel += b.acc * (0.5 * dt);
    }
}

int main() {
    // 1) Initialize bodies: Sun + Jupiter, Saturn, Uranus, Neptune
    std::vector<Body> bodies = {
        {1.9885e30, {0,0,0},          {0,0,0},       {}},  // Sun
        {1.898e27,  {7.785e11,0,0},   {0,1.307e4,0}, {}},  // Jupiter
        {5.683e26,  {1.433e12,0,0},   {0,9.69e3,0},  {}},  // Saturn
        {8.681e25,  {2.872e12,0,0},   {0,6.81e3,0},  {}},  // Uranus
        {1.024e26,  {4.495e12,0,0},   {0,5.43e3,0},  {}},  // Neptune
    };

    // 2) Compute initial accelerations
    compute_accelerations(bodies);

    // 3) Time-loop
    const double dt = 60 * 60 * 6;  // 6-hour timestep
    const double t_end = 60.*60.*24.*365.25*12;  // simulate 12 years
    for (double t = 0; t < t_end; t += dt) {
        step_leapfrog(bodies, dt);
        // (optionally: write out positions for plotting)
    }

    return 0;
}
