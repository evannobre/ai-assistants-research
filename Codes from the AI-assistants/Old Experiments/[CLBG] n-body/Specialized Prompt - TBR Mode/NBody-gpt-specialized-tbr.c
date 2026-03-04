#define N_BODIES 5

typedef struct {
    double x[3];    // position
    double v[3];    // velocity
    double m;       // mass
} Body;

Body bodies[N_BODIES];

const double PI = 3.141592653589793;
const double SOLAR_MASS   = 4.0 * PI * PI;
const double DAYS_PER_YEAR = 365.24;


void offset_momentum() {
    double px = 0.0, py = 0.0, pz = 0.0;
    for(int i = 1; i < N_BODIES; i++){
        px += bodies[i].v[0] * bodies[i].m;
        py += bodies[i].v[1] * bodies[i].m;
        pz += bodies[i].v[2] * bodies[i].m;
    }
    // give negative of that momentum to Sun
    bodies[0].v[0] = -px / SOLAR_MASS;
    bodies[0].v[1] = -py / SOLAR_MASS;
    bodies[0].v[2] = -pz / SOLAR_MASS;
}


void advance(double dt) {
    // 1) update velocities via pairwise forces (“kick”)
    for(int i = 0; i < N_BODIES; i++){
        for(int j = i+1; j < N_BODIES; j++){
            double dx = bodies[i].x[0] - bodies[j].x[0];
            double dy = bodies[i].x[1] - bodies[j].x[1];
            double dz = bodies[i].x[2] - bodies[j].x[2];
            double dist2 = dx*dx + dy*dy + dz*dz;
            double dist = sqrt(dist2);
            double mag = dt / (dist2 * dist);

            // force magnitude scaled by masses
            double m_j = bodies[j].m;
            double m_i = bodies[i].m;
            double f_i = -m_j * mag;
            double f_j =  m_i * mag;

            // kick i
            bodies[i].v[0] += dx * f_i;
            bodies[i].v[1] += dy * f_i;
            bodies[i].v[2] += dz * f_i;

            // kick j (equal & opposite)
            bodies[j].v[0] += dx * f_j;
            bodies[j].v[1] += dy * f_j;
            bodies[j].v[2] += dz * f_j;
        }
    }

    // 2) update positions (“drift”)
    for(int i = 0; i < N_BODIES; i++){
        bodies[i].x[0] += dt * bodies[i].v[0];
        bodies[i].x[1] += dt * bodies[i].v[1];
        bodies[i].x[2] += dt * bodies[i].v[2];
    }
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// … (definitions from above) …

int main(int argc, char *argv[]) {
    if(argc != 2) {
        fprintf(stderr, "Usage: %s <num_steps>\n", argv[0]);
        return 1;
    }
    long steps = atol(argv[1]);
    double dt = 0.01;  // you can tune this

    // 1) initialize bodies[...] with your ephemeris data (positions, velocities*DAYS_PER_YEAR, masses)
    //    e.g., bodies[1].v[0] = 1.66007664274403694e-03 * DAYS_PER_YEAR; etc.

    offset_momentum();

    // 2) run
    for(long i = 0; i < steps; i++){
        advance(dt);
    }

    // 3) optionally compute and print total energy to verify conservation
    double energy = 0.0;
    // … compute kinetic + potential …

    printf("Final energy: %.9f\n", energy);
    return 0;
}
