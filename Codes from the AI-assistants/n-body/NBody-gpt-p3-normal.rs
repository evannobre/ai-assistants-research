use std::env;

const DAYS_PER_YEAR: f64 = 365.24;
const SOLAR_MASS: f64 = 4.0 * std::f64::consts::PI * std::f64::consts::PI;

#[derive(Clone, Copy)]
struct Vec3 {
    x: f64,
    y: f64,
    z: f64,
}

impl Vec3 {
    #[inline]
    fn zero() -> Self {
        Self { x: 0.0, y: 0.0, z: 0.0 }
    }

    #[inline]
    fn add_scaled(&mut self, v: Vec3, s: f64) {
        self.x += v.x * s;
        self.y += v.y * s;
        self.z += v.z * s;
    }

    #[inline]
    fn norm2(self) -> f64 {
        self.x * self.x + self.y * self.y + self.z * self.z
    }
}

#[derive(Clone, Copy)]
struct Body {
    r: Vec3,
    v: Vec3,
    m: f64,
}

fn offset_momentum(bodies: &mut [Body]) {
    // Set system momentum to zero by adjusting the Sun's velocity.
    let mut px = 0.0;
    let mut py = 0.0;
    let mut pz = 0.0;

    for b in bodies.iter() {
        px += b.v.x * b.m;
        py += b.v.y * b.m;
        pz += b.v.z * b.m;
    }

    // Sun is index 0 by our construction
    bodies[0].v.x = -px / SOLAR_MASS;
    bodies[0].v.y = -py / SOLAR_MASS;
    bodies[0].v.z = -pz / SOLAR_MASS;
}

fn energy(bodies: &[Body]) -> f64 {
    let mut e = 0.0;

    // kinetic
    for b in bodies.iter() {
        e += 0.5 * b.m * b.v.norm2();
    }

    // potential
    for i in 0..bodies.len() {
        for j in (i + 1)..bodies.len() {
            let dx = bodies[i].r.x - bodies[j].r.x;
            let dy = bodies[i].r.y - bodies[j].r.y;
            let dz = bodies[i].r.z - bodies[j].r.z;
            let r = (dx * dx + dy * dy + dz * dz).sqrt();
            e -= (bodies[i].m * bodies[j].m) / r;
        }
    }

    e
}

// Symplectic Euler: v(t+dt) from r(t), then r(t+dt) from v(t+dt)
fn advance(bodies: &mut [Body], dt: f64) {
    let n = bodies.len();

    // pairwise velocity updates
    for i in 0..n {
        for j in (i + 1)..n {
            let dx = bodies[i].r.x - bodies[j].r.x;
            let dy = bodies[i].r.y - bodies[j].r.y;
            let dz = bodies[i].r.z - bodies[j].r.z;

            let r2 = dx * dx + dy * dy + dz * dz;
            let inv_r = 1.0 / r2.sqrt();
            let inv_r3 = inv_r / r2; // 1/r^3

            let f = dt * inv_r3;

            let mi = bodies[i].m;
            let mj = bodies[j].m;

            // i loses momentum toward j
            bodies[i].v.x -= dx * mj * f;
            bodies[i].v.y -= dy * mj * f;
            bodies[i].v.z -= dz * mj * f;

            // j gains opposite
            bodies[j].v.x += dx * mi * f;
            bodies[j].v.y += dy * mi * f;
            bodies[j].v.z += dz * mi * f;
        }
    }

    // position updates using updated velocities
    for b in bodies.iter_mut() {
        b.r.add_scaled(b.v, dt);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let steps: usize = if args.len() >= 2 {
        args[1].parse().unwrap_or(0)
    } else {
        0
    };

    // Ephemeris (positions), (velocities), (mass)
    // Sun
    let sun = Body {
        r: Vec3 { x: 0.0, y: 0.0, z: 0.0 },
        v: Vec3 { x: 0.0, y: 0.0, z: 0.0 },
        m: SOLAR_MASS,
    };

    let jupiter = Body {
        r: Vec3 {
            x: 4.84143144246472090e+00,
            y: -1.16032004402742839e+00,
            z: -1.03622044471123109e-01,
        },
        v: Vec3 {
            x: 1.66007664274403694e-03 * DAYS_PER_YEAR,
            y: 7.69901118419740425e-03 * DAYS_PER_YEAR,
            z: -6.90460016972063023e-05 * DAYS_PER_YEAR,
        },
        m: 9.54791938424326609e-04 * SOLAR_MASS,
    };

    let saturn = Body {
        r: Vec3 {
            x: 8.34336671824457987e+00,
            y: 4.12479856412430479e+00,
            z: -4.03523417114321381e-01,
        },
        v: Vec3 {
            x: -2.76742510726862411e-03 * DAYS_PER_YEAR,
            y: 4.99852801234917238e-03 * DAYS_PER_YEAR,
            z: 2.30417297573763929e-05 * DAYS_PER_YEAR,
        },
        m: 2.85885980666130812e-04 * SOLAR_MASS,
    };

    let uranus = Body {
        r: Vec3 {
            x: 1.28943695621391310e+01,
            y: -1.51111514016986312e+01,
            z: -2.23307578892655734e-01,
        },
        v: Vec3 {
            x: 2.96460137564761618e-03 * DAYS_PER_YEAR,
            y: 2.37847173959480950e-03 * DAYS_PER_YEAR,
            z: -2.96589568540237556e-05 * DAYS_PER_YEAR,
        },
        m: 4.36624404335156298e-05 * SOLAR_MASS,
    };

    let neptune = Body {
        r: Vec3 {
            x: 1.53796971148509165e+01,
            y: -2.59193146099879641e+01,
            z: 1.79258772950371181e-01,
        },
        v: Vec3 {
            x: 2.68067772490389322e-03 * DAYS_PER_YEAR,
            y: 1.62824170038242295e-03 * DAYS_PER_YEAR,
            z: -9.51592254519715870e-05 * DAYS_PER_YEAR,
        },
        m: 5.15138902046611451e-05 * SOLAR_MASS,
    };

    let mut bodies = [sun, jupiter, saturn, uranus, neptune];

    offset_momentum(&mut bodies);

    // Typical benchmark dt is 0.01
    let dt = 0.01;

    println!("{:.9}", energy(&bodies));
    for _ in 0..steps {
        advance(&mut bodies, dt);
    }
    println!("{:.9}", energy(&bodies));
}
