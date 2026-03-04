// nbody_symplectic_euler.c
// Single-threaded symplectic Euler N-body for Sun + Jovians (N=5).
// Build: gcc -O3 -march=native -std=c11 -Wall -Wextra -pedantic nbody_symplectic_euler.c -lm
// Run:   ./a.out 50000000

#include <errno.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define N 5
#define PI 3.141592653589793238462643383279502884
#define SOLAR_MASS (4.0 * PI * PI)
#define DAYS_PER_YEAR 365.24

typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double mass;
} Body;

static void init_sun_and_jovians(Body b[N]) {
    // Sun
    b[0] = (Body){0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0,
                 SOLAR_MASS};

    // Jupiter
    b[1] = (Body){
        4.84143144246472090e+00,  -1.16032004402742839e+00,  -1.03622044471123109e-01,
        1.66007664274403694e-03 * DAYS_PER_YEAR,
        7.69901118419740425e-03 * DAYS_PER_YEAR,
       -6.90460016972063023e-05 * DAYS_PER_YEAR,
        9.54791938424326609e-04 * SOLAR_MASS
    };

    // Saturn
    b[2] = (Body){
        8.34336671824457987e+00,   4.12479856412430479e+00,  -4.03523417114321381e-01,
       -2.76742510726862411e-03 * DAYS_PER_YEAR,
        4.99852801234917238e-03 * DAYS_PER_YEAR,
        2.30417297573763929e-05 * DAYS_PER_YEAR,
        2.85885980666130812e-04 * SOLAR_MASS
    };

    // Uranus
    b[3] = (Body){
        1.28943695621391310e+01,  -1.51111514016986312e+01,  -2.23307578892655734e-01,
        2.96460137564761618e-03 * DAYS_PER_YEAR,
        2.37847173959480950e-03 * DAYS_PER_YEAR,
       -2.96589568540237556e-05 * DAYS_PER_YEAR,
        4.36624404335156298e-05 * SOLAR_MASS
    };

    // Neptune
    b[4] = (Body){
        1.53796971148509165e+01,  -2.59193146099879641e+01,   1.79258772950371181e-01,
        2.68067772490389322e-03 * DAYS_PER_YEAR,
        1.62824170038242295e-03 * DAYS_PER_YEAR,
       -9.51592254519715870e-05 * DAYS_PER_YEAR,
        5.15138902046611451e-05 * SOLAR_MASS
    };
}

static void offset_momentum(Body b[N]) {
    // Adjust Sun velocity so that total momentum is 0.
    double px = 0.0, py = 0.0, pz = 0.0;
    for (int i = 0; i < N; i++) {
        px += b[i].vx * b[i].mass;
        py += b[i].vy * b[i].mass;
        pz += b[i].vz * b[i].mass;
    }
    b[0].vx = -px / b[0].mass;
    b[0].vy = -py / b[0].mass;
    b[0].vz = -pz / b[0].mass;
}

static double energy(const Body b[N]) {
    // Total energy = kinetic + potential (pairwise).
    double e = 0.0;

    // Kinetic
    for (int i = 0; i < N; i++) {
        const double v2 = b[i].vx * b[i].vx + b[i].vy * b[i].vy + b[i].vz * b[i].vz;
        e += 0.5 * b[i].mass * v2;
    }

    // Potential
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            const double dx = b[i].x - b[j].x;
            const double dy = b[i].y - b[j].y;
            const double dz = b[i].z - b[j].z;
            const double r = sqrt(dx * dx + dy * dy + dz * dz);
            e -= (b[i].mass * b[j].mass) / r;
        }
    }

    return e;
}

static void advance_symplectic_euler(Body b[N], double dt) {
    // Compute accelerations a(t) from positions at time t,
    // then update v(t+dt) = v(t) + a(t)*dt,
    // then x(t+dt) = x(t) + v(t+dt)*dt.

    double ax[N] = {0}, ay[N] = {0}, az[N] = {0};

    // Pairwise contributions
    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            const double dx = b[j].x - b[i].x;
            const double dy = b[j].y - b[i].y;
            const double dz = b[j].z - b[i].z;

            const double r2 = dx * dx + dy * dy + dz * dz;
            const double inv_r = 1.0 / sqrt(r2);
            const double inv_r3 = inv_r * inv_r * inv_r;

            // Acceleration on i due to j: + m_j * (r_ij) / |r_ij|^3
            // Acceleration on j due to i: - m_i * (r_ij) / |r_ij|^3
            const double s_i = b[j].mass * inv_r3;
            const double s_j = b[i].mass * inv_r3;

            ax[i] += dx * s_i;
            ay[i] += dy * s_i;
            az[i] += dz * s_i;

            ax[j] -= dx * s_j;
            ay[j] -= dy * s_j;
            az[j] -= dz * s_j;
        }
    }

    // Velocity update
    for (int i = 0; i < N; i++) {
        b[i].vx += dt * ax[i];
        b[i].vy += dt * ay[i];
        b[i].vz += dt * az[i];
    }

    // Position update with updated velocities (symplectic Euler)
    for (int i = 0; i < N; i++) {
        b[i].x += dt * b[i].vx;
        b[i].y += dt * b[i].vy;
        b[i].z += dt * b[i].vz;
    }
}

static uint64_t parse_u64_or_die(const char *s) {
    errno = 0;
    char *end = NULL;
    unsigned long long v = strtoull(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0') {
        fprintf(stderr, "Invalid steps: '%s'\n", s);
        exit(2);
    }
    return (uint64_t)v;
}

int main(int argc, char **argv) {
    const uint64_t steps = (argc > 1) ? parse_u64_or_die(argv[1]) : 1000ULL;
    const double dt = 0.01;

    Body bodies[N];
    init_sun_and_jovians(bodies);
    offset_momentum(bodies);

    printf("%.9f\n", energy(bodies));

    for (uint64_t i = 0; i < steps; i++) {
        advance_symplectic_euler(bodies, dt);
    }

    printf("%.9f\n", energy(bodies));
    return 0;
}
