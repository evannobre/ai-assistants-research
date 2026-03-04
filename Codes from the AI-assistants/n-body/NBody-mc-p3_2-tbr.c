/* nbody.c */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DAYS_PER_YEAR 365.24
#define SOLAR_MASS (4.0 * M_PI * M_PI)

typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double m;
} Body;

double total_energy(Body *b, int n) {
    double e = 0.0;
    for (int i = 0; i < n; ++i) {
        e += 0.5 * b[i].m * (b[i].vx*b[i].vx + b[i].vy*b[i].vy + b[i].vz*b[i].vz);
        for (int j = i + 1; j < n; ++j) {
            double dx = b[i].x - b[j].x;
            double dy = b[i].y - b[j].y;
            double dz = b[i].z - b[j].z;
            double dist = sqrt(dx*dx + dy*dy + dz*dz);
            e -= (b[i].m * b[j].m) / dist;
        }
    }
    return e;
}

int main(int argc, char **argv) {
    long steps = 50000000;
    if (argc > 1) steps = atol(argv[1]);
    const double dt = 0.01;

    Body bodies[5] = {
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS},
        {4.84143144246472090e+00, -1.16032004402742839e+00, -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR, 7.69901118419740425e-03 * DAYS_PER_YEAR, -6.90460016972063023e-05 * DAYS_PER_YEAR,
         9.54791938424326609e-04 * SOLAR_MASS},
        {8.34336671824457987e+00, 4.12479856412430479e+00, -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR, 4.99852801234917238e-03 * DAYS_PER_YEAR, 2.30417297573763929e-05 * DAYS_PER_YEAR,
         2.85885980666130812e-04 * SOLAR_MASS},
        {1.28943695621391310e+01, -1.51111514016986312e+01, -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR, 2.37847173959480950e-03 * DAYS_PER_YEAR, -2.96589568540237556e-05 * DAYS_PER_YEAR,
         4.36624404335156298e-05 * SOLAR_MASS},
        {1.53796971148509165e+01, -2.59193146099879641e+01, 1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR, 1.62824170038242295e-03 * DAYS_PER_YEAR, -9.51592254519715870e-05 * DAYS_PER_YEAR,
         5.15138902046611451e-05 * SOLAR_MASS}
    };

    // offset momentum
    double px = 0.0, py = 0.0, pz = 0.0;
    for (int i = 0; i < 5; ++i) {
        px += bodies[i].vx * bodies[i].m;
        py += bodies[i].vy * bodies[i].m;
        pz += bodies[i].vz * bodies[i].m;
    }
    bodies[0].vx = -px / bodies[0].m;
    bodies[0].vy = -py / bodies[0].m;
    bodies[0].vz = -pz / bodies[0].m;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (long step = 0; step < steps; ++step) {
        // pairwise velocity updates
        for (int i = 0; i < 5; ++i) {
            for (int j = i + 1; j < 5; ++j) {
                double dx = bodies[i].x - bodies[j].x;
                double dy = bodies[i].y - bodies[j].y;
                double dz = bodies[i].z - bodies[j].z;
                double dist2 = dx*dx + dy*dy + dz*dz;
                double dist = sqrt(dist2);
                double mag = dt / (dist * dist2);
                double mi = bodies[i].m;
                double mj = bodies[j].m;

                bodies[i].vx -= dx * mj * mag;
                bodies[i].vy -= dy * mj * mag;
                bodies[i].vz -= dz * mj * mag;

                bodies[j].vx += dx * mi * mag;
                bodies[j].vy += dy * mi * mag;
                bodies[j].vz += dz * mi * mag;
            }
        }
        // position updates
        for (int i = 0; i < 5; ++i) {
            bodies[i].x += dt * bodies[i].vx;
            bodies[i].y += dt * bodies[i].vy;
            bodies[i].z += dt * bodies[i].vz;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double elapsed = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;
    printf("Steps: %ld, elapsed: %.6f s\n", steps, elapsed);
    printf("Energy: %.12f\n", total_energy(bodies, 5));
    return 0;
}
