use std::env;

const PI: f64 = std::f64::consts::PI;
const SOLAR_MASS: f64 = 4.0 * PI * PI;
const DAYS_PER_YEAR: f64 = 365.24;

#[derive(Clone, Copy)]
struct Body {
    x: f64, y: f64, z: f64,
    vx: f64, vy: f64, vz: f64,
    m: f64,
}

fn offset_momentum(bodies: &mut [Body]) {
    // Make total momentum zero by adjusting the Sun.
    let mut px = 0.0;
    let mut py = 0.0;
    let mut pz = 0.0;

    for b in bodies.iter() {
        px += b.vx * b.m;
        py += b.vy * b.m;
        pz += b.vz * b.m;
    }

    bodies[0].vx = -px / bodies[0].m;
    bodies[0].vy = -py / bodies[0].m;
    bodies[0].vz = -pz / bodies[0].m;
}

fn energy(bodies: &[Body]) -> f64 {
    let mut e = 0.0;

    // Kinetic energy
    for b in bodies.iter() {
        let v2 = b.vx * b.vx + b.vy * b.vy + b.vz * b.vz;
        e += 0.5 * b.m * v2;
    }

    // Potential energy
    for i in 0..bodies.len() {
        for j in (i + 1)..bodies.len() {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;
            let dist = (dx * dx + dy * dy + dz * dz).sqrt();
            e -= bodies[i].m * bodies[j].m / dist;
        }
    }

    e
}

/// One symplectic-Euler advance over `steps` iterations with fixed dt.
/// Symplectic Euler: update v using x(t), then update x using v(t+dt).
fn advance(bodies: &mut [Body], dt: f64, steps: usize) {
    let n = bodies.len();

    for _ in 0..steps {
        // Velocity updates from pairwise interactions
        for i in 0..n {
            for j in (i + 1)..n {
                let dx = bodies[i].x - bodies[j].x;
                let dy = bodies[i].y - bodies[j].y;
                let dz = bodies[i].z - bodies[j].z;

                let dist2 = dx * dx + dy * dy + dz * dz;
                let dist = dist2.sqrt();
                let mag = dt / (dist2 * dist); // dt / dist^3

                let mi = bodies[i].m;
                let mj = bodies[j].m;

                // i loses velocity proportional to mj
                bodies[i].vx -= dx * mj * mag;
                bodies[i].vy -= dy * mj * mag;
                bodies[i].vz -= dz * mj * mag;

                // j gains velocity proportional to mi
                bodies[j].vx += dx * mi * mag;
                bodies[j].vy += dy * mi * mag;
                bodies[j].vz += dz * mi * mag;
            }
        }

        // Position updates using updated velocities
        for b in bodies.iter_mut() {
            b.x += dt * b.vx;
            b.y += dt * b.vy;
            b.z += dt * b.vz;
        }
    }
}

fn initial_bodies() -> [Body; 5] {
    // Sun, Jupiter, Saturn, Uranus, Neptune
    // Ephemeris exactly as provided, with velocity factors applied.
    let sun = Body {
        x: 0.0, y: 0.0, z: 0.0,
        vx: 0.0, vy: 0.0, vz: 0.0,
        m: SOLAR_MASS,
    };

    let jupiter = Body {
        x: 4.84143144246472090e+00,
        y: -1.16032004402742839e+00,
        z: -1.03622044471123109e-01,
        vx: 1.66007664274403694e-03 * DAYS_PER_YEAR,
        vy: 7.69901118419740425e-03 * DAYS_PER_YEAR,
        vz: -6.90460016972063023e-05 * DAYS_PER_YEAR,
        m: 9.54791938424326609e-04 * SOLAR_MASS,
    };

    let saturn = Body {
        x: 8.34336671824457987e+00,
        y: 4.12479856412430479e+00,
        z: -4.03523417114321381e-01,
        vx: -2.76742510726862411e-03 * DAYS_PER_YEAR,
        vy: 4.99852801234917238e-03 * DAYS_PER_YEAR,
        vz: 2.30417297573763929e-05 * DAYS_PER_YEAR,
        m: 2.85885980666130812e-04 * SOLAR_MASS,
    };

    let uranus = Body {
        x: 1.28943695621391310e+01,
        y: -1.51111514016986312e+01,
        z: -2.23307578892655734e-01,
        vx: 2.96460137564761618e-03 * DAYS_PER_YEAR,
        vy: 2.37847173959480950e-03 * DAYS_PER_YEAR,
        vz: -2.96589568540237556e-05 * DAYS_PER_YEAR,
        m: 4.36624404335156298e-05 * SOLAR_MASS,
    };

    let neptune = Body {
        x: 1.53796971148509165e+01,
        y: -2.59193146099879641e+01,
        z: 1.79258772950371181e-01,
        vx: 2.68067772490389322e-03 * DAYS_PER_YEAR,
        vy: 1.62824170038242295e-03 * DAYS_PER_YEAR,
        vz: -9.51592254519715870e-05 * DAYS_PER_YEAR,
        m: 5.15138902046611451e-05 * SOLAR_MASS,
    };

    [sun, jupiter, saturn, uranus, neptune]
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let n: usize = args.get(1)
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(1000);

    let dt = 0.01;

    let mut bodies = initial_bodies();
    offset_momentum(&mut bodies);

    println!("{:.9}", energy(&bodies));
    advance(&mut bodies, dt, n);
    println!("{:.9}", energy(&bodies));
}
