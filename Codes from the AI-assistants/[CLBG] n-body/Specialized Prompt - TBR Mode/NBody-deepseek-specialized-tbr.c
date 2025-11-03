#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define SOLAR_MASS (4 * M_PI * M_PI)
#define DAYS_PER_YEAR 365.24
#define N_BODIES 5

typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double ax, ay, az;
    double mass;
} Body;

void initialize_bodies(Body *bodies) {
    // Sun
    bodies[0].x = 0.0; bodies[0].y = 0.0; bodies[0].z = 0.0;
    bodies[0].vx = 0.0; bodies[0].vy = 0.0; bodies[0].vz = 0.0;
    bodies[0].mass = SOLAR_MASS;

    // Jupiter
    bodies[1].x = 4.84143144246472090e+00;
    bodies[1].y = -1.16032004402742839e+00;
    bodies[1].z = -1.03622044471123109e-01;
    bodies[1].vx = 1.66007664274403694e-03 * DAYS_PER_YEAR;
    bodies[1].vy = 7.69901118419740425e-03 * DAYS_PER_YEAR;
    bodies[1].vz = -6.90460016972063023e-05 * DAYS_PER_YEAR;
    bodies[1].mass = 9.54791938424326609e-04 * SOLAR_MASS;

    // Saturn
    bodies[2].x = 8.34336671824457987e+00;
    bodies[2].y = 4.12479856412430479e+00;
    bodies[2].z = -4.03523417114321381e-01;
    bodies[2].vx = -2.76742510726862411e-03 * DAYS_PER_YEAR;
    bodies[2].vy = 4.99852801234917238e-03 * DAYS_PER_YEAR;
    bodies[2].vz = 2.30417297573763929e-05 * DAYS_PER_YEAR;
    bodies[2].mass = 2.85885980666130812e-04 * SOLAR_MASS;

    // Uranus
    bodies[3].x = 1.28943695621391310e+01;
    bodies[3].y = -1.51111514016986312e+01;
    bodies[3].z = -2.23307578892655734e-01;
    bodies[3].vx = 2.96460137564761618e-03 * DAYS_PER_YEAR;
    bodies[3].vy = 2.37847173959480950e-03 * DAYS_PER_YEAR;
    bodies[3].vz = -2.96589568540237556e-05 * DAYS_PER_YEAR;
    bodies[3].mass = 4.36624404335156298e-05 * SOLAR_MASS;

    // Neptune
    bodies[4].x = 1.53796971148509165e+01;
    bodies[4].y = -2.59193146099879641e+01;
    bodies[4].z = 1.79258772950371181e-01;
    bodies[4].vx = 2.68067772490389322e-03 * DAYS_PER_YEAR;
    bodies[4].vy = 1.62824170038242295e-03 * DAYS_PER_YEAR;
    bodies[4].vz = -9.51592254519715870e-05 * DAYS_PER_YEAR;
    bodies[4].mass = 5.15138902046611451e-05 * SOLAR_MASS;
}

void compute_accelerations(Body *bodies) {
    for (int i = 0; i < N_BODIES; i++) {
        bodies[i].ax = 0.0;
        bodies[i].ay = 0.0;
        bodies[i].az = 0.0;
    }

    for (int i = 0; i < N_BODIES; i++) {
        for (int j = i + 1; j < N_BODIES; j++) {
            double dx = bodies[j].x - bodies[i].x;
            double dy = bodies[j].y - bodies[i].y;
            double dz = bodies[j].z - bodies[i].z;

            double r_squared = dx*dx + dy*dy + dz*dz;
            double r = sqrt(r_squared);
            double r_cubed = r_squared * r;
            double factor = 1.0 / r_cubed;

            double temp_ax = dx * factor;
            double temp_ay = dy * factor;
            double temp_az = dz * factor;

            bodies[i].ax += bodies[j].mass * temp_ax;
            bodies[i].ay += bodies[j].mass * temp_ay;
            bodies[i].az += bodies[j].mass * temp_az;

            bodies[j].ax -= bodies[i].mass * temp_ax;
            bodies[j].ay -= bodies[i].mass * temp_ay;
            bodies[j].az -= bodies[i].mass * temp_az;
        }
    }
}

void update_velocities(Body *bodies, double dt) {
    for (int i = 0; i < N_BODIES; i++) {
        bodies[i].vx += bodies[i].ax * dt;
        bodies[i].vy += bodies[i].ay * dt;
        bodies[i].vz += bodies[i].az * dt;
    }
}

void update_positions(Body *bodies, double dt) {
    for (int i = 0; i < N_BODIES; i++) {
        bodies[i].x += bodies[i].vx * dt;
        bodies[i].y += bodies[i].vy * dt;
        bodies[i].z += bodies[i].vz * dt;
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number_of_steps>\n", argv[0]);
        return 1;
    }

    int num_steps = atoi(argv[1]);
    double dt = 0.001; // Time step in years

    Body bodies[N_BODIES];
    initialize_bodies(bodies);

    for (int step = 0; step < num_steps; step++) {
        compute_accelerations(bodies);
        update_velocities(bodies, dt);
        update_positions(bodies, dt);
    }

    // Output final positions and velocities
    for (int i = 0; i < N_BODIES; i++) {
        printf("%d: pos=(%e, %e, %e) vel=(%e, %e, %e)\n",
               i, bodies[i].x, bodies[i].y, bodies[i].z,
                  bodies[i].vx, bodies[i].vy, bodies[i].vz);
    }

    return 0;
}