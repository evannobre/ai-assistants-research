use std::env;

const PI: f64 = std::f64::consts::PI;
const SOLAR_MASS: f64 = 4.0 * PI * PI;
const DAYS_PER_YEAR: f64 = 365.24;
const G: f64 = 4.0 * PI * PI;

#[derive(Clone, Copy)]
struct Body {
    x: f64, y: f64, z: f64,
    vx: f64, vy: f64, vz: f64,
    mass: f64,
}

fn jupiter() -> Body {
    Body {
        x: 4.84143144246472090e+00,
        y: -1.16032004402742839e+00,
        z: -1.03622044471123109e-01,
        vx: 1.66007664274403694e-03 * DAYS_PER_YEAR,
        vy: 7.69901118419740425e-03 * DAYS_PER_YEAR,
        vz: -6.90460016972063023e-05 * DAYS_PER_YEAR,
        mass: 9.54791938424326609e-04 * SOLAR_MASS,
    }
}

fn saturn() -> Body {
    Body {
        x: 8.34336671824457987e+00,
        y: 4.12479856412430479e+00,
        z: -4.03523417114321381e-01,
        vx: -2.76742510726862411e-03 * DAYS_PER_YEAR,
        vy: 4.99852801234917238e-03 * DAYS_PER_YEAR,
        vz: 2.30417297573763929e-05 * DAYS_PER_YEAR,
        mass: 2.85885980666130812e-04 * SOLAR_MASS,
    }
}

fn uranus() -> Body {
    Body {
        x: 1.28943695621391310e+01,
        y: -1.51111514016986312e+01,
        z: -2.23307578892655734e-01,
        vx: 2.96460137564761618e-03 * DAYS_PER_YEAR,
        vy: 2.37847173959480950e-03 * DAYS_PER_YEAR,
        vz: -2.96589568540237556e-05 * DAYS_PER_YEAR,
        mass: 4.36624404335156298e-05 * SOLAR_MASS,
    }
}

fn neptune() -> Body {
    Body {
        x: 1.53796971148509165e+01,
        y: -2.59193146099879641e+01,
        z: 1.79258772950371181e-01,
        vx: 2.68067772490389322e-03 * DAYS_PER_YEAR,
        vy: 1.62824170038242295e-03 * DAYS_PER_YEAR,
        vz: -9.51592254519715870e-05 * DAYS_PER_YEAR,
        mass: 5.15138902046611451e-05 * SOLAR_MASS,
    }
}

fn sun() -> Body {
    Body {
        x: 0.0, y: 0.0, z: 0.0,
        vx: 0.0, vy: 0.0, vz: 0.0,
        mass: SOLAR_MASS,
    }
}

fn offset_momentum(bodies: &mut [Body]) {
    let mut px = 0.0;
    let mut py = 0.0;
    let mut pz = 0.0;

    for b in bodies.iter() {
        px += b.vx * b.mass;
        py += b.vy * b.mass;
        pz += b.vz * b.mass;
    }

    // Put the momentum into the Sun (assumed index 0 here)
    bodies[0].vx = -px / bodies[0].mass;
    bodies[0].vy = -py / bodies[0].mass;
    bodies[0].vz = -pz / bodies[0].mass;
}

fn compute_accels(bodies: &[Body], ax: &mut [f64], ay: &mut [f64], az: &mut [f64]) {
    ax.fill(0.0);
    ay.fill(0.0);
    az.fill(0.0);

    let n = bodies.len();
    for i in 0..n {
        for j in (i + 1)..n {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;

            let d2 = dx * dx + dy * dy + dz * dz;
            let inv_d = 1.0 / d2.sqrt();
            let inv_d3 = inv_d * inv_d * inv_d;

            let f = G * inv_d3;

            // a_i -= f * m_j * (r_i - r_j)
            ax[i] -= f * bodies[j].mass * dx;
            ay[i] -= f * bodies[j].mass * dy;
            az[i] -= f * bodies[j].mass * dz;

            // a_j += f * m_i * (r_i - r_j)
            ax[j] += f * bodies[i].mass * dx;
            ay[j] += f * bodies[i].mass * dy;
            az[j] += f * bodies[i].mass * dz;
        }
    }
}

fn advance(bodies: &mut [Body], dt: f64, ax: &mut [f64], ay: &mut [f64], az: &mut [f64]) {
    let half = 0.5 * dt;

    // a(t)
    compute_accels(bodies, ax, ay, az);

    // kick half
    for (i, b) in bodies.iter_mut().enumerate() {
        b.vx += ax[i] * half;
        b.vy += ay[i] * half;
        b.vz += az[i] * half;
    }

    // drift
    for b in bodies.iter_mut() {
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        b.z += b.vz * dt;
    }

    // a(t+dt)
    compute_accels(bodies, ax, ay, az);

    // kick half
    for (i, b) in bodies.iter_mut().enumerate() {
        b.vx += ax[i] * half;
        b.vy += ay[i] * half;
        b.vz += az[i] * half;
    }
}

fn energy(bodies: &[Body]) -> f64 {
    let mut e = 0.0;

    // kinetic
    for b in bodies.iter() {
        let v2 = b.vx * b.vx + b.vy * b.vy + b.vz * b.vz;
        e += 0.5 * b.mass * v2;
    }

    // potential
    let n = bodies.len();
    for i in 0..n {
        for j in (i + 1)..n {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;
            let dist = (dx * dx + dy * dy + dz * dz).sqrt();
            e -= (G * bodies[i].mass * bodies[j].mass) / dist;
        }
    }

    e
}

fn main() {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1000);

    let mut bodies = [
        sun(),
        jupiter(),
        saturn(),
        uranus(),
        neptune(),
    ];

    // keep reference frame stable
    offset_momentum(&mut bodies);

    // scratch arrays for acceleration
    let mut ax = vec![0.0; bodies.len()];
    let mut ay = vec![0.0; bodies.len()];
    let mut az = vec![0.0; bodies.len()];

    println!("{:.9}", energy(&bodies));

    let dt = 0.01;
    for _ in 0..n {
        advance(&mut bodies, dt, &mut ax, &mut ay, &mut az);
    }

    println!("{:.9}", energy(&bodies));
}
