use std::env;
use std::f64::consts::PI;

const SOLAR_MASS: f64 = 4.0 * PI * PI;
const DAYS_PER_YEAR: f64 = 365.24;

#[derive(Clone, Copy)]
struct Body {
    x: f64,
    y: f64,
    z: f64,
    vx: f64,
    vy: f64,
    vz: f64,
    mass: f64,
}

fn jupiter() -> Body {
    Body {
        x: 4.841_431_442_464_720_90e+00,
        y: -1.160_320_044_027_428_39e+00,
        z: -1.036_220_444_711_231_09e-01,
        vx: 1.660_076_642_744_036_94e-03 * DAYS_PER_YEAR,
        vy: 7.699_011_184_197_404_25e-03 * DAYS_PER_YEAR,
        vz: -6.904_600_169_720_630_23e-05 * DAYS_PER_YEAR,
        mass: 9.547_919_384_243_266_09e-04 * SOLAR_MASS,
    }
}

fn saturn() -> Body {
    Body {
        x: 8.343_366_718_244_579_87e+00,
        y: 4.124_798_564_124_304_79e+00,
        z: -4.035_234_171_143_213_81e-01,
        vx: -2.767_425_107_268_624_11e-03 * DAYS_PER_YEAR,
        vy: 4.998_528_012_349_172_38e-03 * DAYS_PER_YEAR,
        vz: 2.304_172_975_737_639_29e-05 * DAYS_PER_YEAR,
        mass: 2.858_859_806_661_308_12e-04 * SOLAR_MASS,
    }
}

fn uranus() -> Body {
    Body {
        x: 1.289_436_956_213_913_10e+01,
        y: -1.511_115_140_169_863_12e+01,
        z: -2.233_075_788_926_557_34e-01,
        vx: 2.964_601_375_647_616_18e-03 * DAYS_PER_YEAR,
        vy: 2.378_471_739_594_809_50e-03 * DAYS_PER_YEAR,
        vz: -2.965_895_685_402_375_56e-05 * DAYS_PER_YEAR,
        mass: 4.366_244_043_351_562_98e-05 * SOLAR_MASS,
    }
}

fn neptune() -> Body {
    Body {
        x: 1.537_969_711_485_091_65e+01,
        y: -2.591_931_460_998_796_41e+01,
        z: 1.792_587_729_503_711_81e-01,
        vx: 2.680_677_724_903_893_22e-03 * DAYS_PER_YEAR,
        vy: 1.628_241_700_382_422_95e-03 * DAYS_PER_YEAR,
        vz: -9.515_922_545_197_158_70e-05 * DAYS_PER_YEAR,
        mass: 5.151_389_020_466_114_51e-05 * SOLAR_MASS,
    }
}

fn sun() -> Body {
    Body {
        x: 0.0,
        y: 0.0,
        z: 0.0,
        vx: 0.0,
        vy: 0.0,
        vz: 0.0,
        mass: SOLAR_MASS,
    }
}

fn offset_momentum(bodies: &mut [Body; 5]) {
    let mut px = 0.0;
    let mut py = 0.0;
    let mut pz = 0.0;

    for b in bodies.iter() {
        px += b.vx * b.mass;
        py += b.vy * b.mass;
        pz += b.vz * b.mass;
    }

    // Make the entire system have zero momentum by adjusting the Sun.
    bodies[0].vx -= px / bodies[0].mass;
    bodies[0].vy -= py / bodies[0].mass;
    bodies[0].vz -= pz / bodies[0].mass;
}

fn advance(bodies: &mut [Body; 5], dt: f64) {
    // Kick: update velocities from pairwise gravity interactions.
    for i in 0..bodies.len() {
        for j in (i + 1)..bodies.len() {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;

            let dist2 = dx * dx + dy * dy + dz * dz;
            let dist = dist2.sqrt();
            let mag = dt / (dist2 * dist); // dt * dist^-3

            let mi = bodies[i].mass;
            let mj = bodies[j].mass;

            // Equal and opposite impulses.
            bodies[i].vx -= dx * mj * mag;
            bodies[i].vy -= dy * mj * mag;
            bodies[i].vz -= dz * mj * mag;

            bodies[j].vx += dx * mi * mag;
            bodies[j].vy += dy * mi * mag;
            bodies[j].vz += dz * mi * mag;
        }
    }

    // Drift: update positions using updated velocities.
    for b in bodies.iter_mut() {
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        b.z += b.vz * dt;
    }
}

fn energy(bodies: &[Body; 5]) -> f64 {
    let mut e = 0.0;

    // Kinetic energy.
    for b in bodies.iter() {
        let v2 = b.vx * b.vx + b.vy * b.vy + b.vz * b.vz;
        e += 0.5 * b.mass * v2;
    }

    // Potential energy.
    for i in 0..bodies.len() {
        for j in (i + 1)..bodies.len() {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;
            let r = (dx * dx + dy * dy + dz * dz).sqrt();
            e -= (bodies[i].mass * bodies[j].mass) / r;
        }
    }

    e
}

fn parse_n() -> usize {
    let mut args = env::args();
    let _exe = args.next();
    match args.next() {
        Some(s) => s.parse::<usize>().unwrap_or(0),
        None => 0,
    }
}

fn main() {
    // CLI: n = number of iterations; default 0 if omitted (still prints energies).
    let n = parse_n();

    let mut bodies = [sun(), jupiter(), saturn(), uranus(), neptune()];

    offset_momentum(&mut bodies);

    // Common benchmark timestep.
    let dt = 0.01;

    println!("{:.9}", energy(&bodies));
    for _ in 0..n {
        advance(&mut bodies, dt);
    }
    println!("{:.9}", energy(&bodies));
}
