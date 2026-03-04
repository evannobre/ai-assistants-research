use std::env;
use std::time::Instant;

#[derive(Clone, Copy, Debug)]
struct Vec3 {
    x: f64,
    y: f64,
    z: f64,
}

impl Vec3 {
    fn zero() -> Self {
        Vec3 { x: 0.0, y: 0.0, z: 0.0 }
    }

    fn add(&self, other: &Vec3) -> Vec3 {
        Vec3 {
            x: self.x + other.x,
            y: self.y + other.y,
            z: self.z + other.z,
        }
    }

    fn sub(&self, other: &Vec3) -> Vec3 {
        Vec3 {
            x: self.x - other.x,
            y: self.y - other.y,
            z: self.z - other.z,
        }
    }

    fn scale(&self, s: f64) -> Vec3 {
        Vec3 {
            x: self.x * s,
            y: self.y * s,
            z: self.z * s,
        }
    }

    fn norm_sq(&self) -> f64 {
        self.x * self.x + self.y * self.y + self.z * self.z
    }
}

#[derive(Clone, Debug)]
struct Body {
    name: &'static str,
    mass: f64,      // in solar masses
    pos: Vec3,      // in AU
    vel: Vec3,      // in AU/year
    acc: Vec3,      // in AU/year^2
}

// Gravitational constant in units of AU^3 / (solar_mass * year^2)
const G: f64 = 4.0 * std::f64::consts::PI * std::f64::consts::PI;

// Initialize Sun + Jovian planets with rough circular orbits in the xy-plane.
// Distances in AU, periods in years, velocities from v = 2*pi*a / T.
fn init_bodies() -> Vec<Body> {
    let sun = Body {
        name: "Sun",
        mass: 1.0,
        pos: Vec3::zero(),
        vel: Vec3::zero(),
        acc: Vec3::zero(),
    };

    // (name, mass [solar], semi-major axis [AU], orbital period [years])
    let planets_data = [
        ("Jupiter", 0.0009543, 5.2044, 11.862),
        ("Saturn",  0.0002857, 9.5826, 29.457),
        ("Uranus",  0.00004365, 19.2184, 84.0205),
        ("Neptune", 0.00005149, 30.11, 164.8),
    ];

    let mut bodies = Vec::new();
    bodies.push(sun);

    for (name, mass, a, period) in planets_data {
        let v = 2.0 * std::f64::consts::PI * a / period;
        bodies.push(Body {
            name,
            mass,
            pos: Vec3 { x: a, y: 0.0, z: 0.0 },
            vel: Vec3 { x: 0.0, y: v, z: 0.0 },
            acc: Vec3::zero(),
        });
    }

    bodies
}

// Compute accelerations for all bodies (O(n^2)).
fn compute_accelerations(bodies: &mut [Body]) {
    let n = bodies.len();
    // Reset accelerations
    for b in bodies.iter_mut() {
        b.acc = Vec3::zero();
    }

    for i in 0..n {
        for j in (i + 1)..n {
            let rij = bodies[j].pos.sub(&bodies[i].pos);
            let dist_sq = rij.norm_sq();
            let dist = dist_sq.sqrt();
            let inv_dist3 = 1.0 / (dist_sq * dist + 1e-12); // small epsilon to avoid div by zero

            let factor_i = G * bodies[j].mass * inv_dist3;
            let factor_j = G * bodies[i].mass * inv_dist3;

            let a_i = rij.scale(factor_i);
            let a_j = rij.scale(-factor_j);

            bodies[i].acc = bodies[i].acc.add(&a_i);
            bodies[j].acc = bodies[j].acc.add(&a_j);
        }
    }
}

// One velocity-Verlet step.
fn step(bodies: &mut [Body], dt: f64) {
    // Half-step velocity update and full-step position update
    for b in bodies.iter_mut() {
        b.vel = b.vel.add(&b.acc.scale(0.5 * dt));
        b.pos = b.pos.add(&b.vel.scale(dt));
    }

    // Recompute accelerations at new positions
    compute_accelerations(bodies);

    // Second half-step velocity update
    for b in bodies.iter_mut() {
        b.vel = b.vel.add(&b.acc.scale(0.5 * dt));
    }
}

fn parse_args() -> (usize, f64, bool) {
    let args: Vec<String> = env::args().collect();
    let mut steps: usize = 10_000;
    let mut dt: f64 = 0.001; // years
    let mut bench = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--steps" => {
                if i + 1 < args.len() {
                    steps = args[i + 1].parse().unwrap_or(steps);
                    i += 1;
                }
            }
            "--dt" => {
                if i + 1 < args.len() {
                    dt = args[i + 1].parse().unwrap_or(dt);
                    i += 1;
                }
            }
            "--bench" => {
                bench = true;
            }
            "--help" | "-h" => {
                println!("Usage: {} [--steps N] [--dt value] [--bench]", args[0]);
                std::process::exit(0);
            }
            _ => {}
        }
        i += 1;
    }

    (steps, dt, bench)
}

fn main() {
    let (steps, dt, bench) = parse_args();

    let mut bodies = init_bodies();
    // Initial accelerations
    compute_accelerations(&mut bodies);

    let start = Instant::now();

    for step_idx in 0..steps {
        step(&mut bodies, dt);

        if !bench && step_idx % 1000 == 0 {
            println!("Step {} (t = {:.3} years):", step_idx, (step_idx as f64) * dt);
            for b in &bodies {
                println!(
                    "  {:8}: pos=({:>10.6}, {:>10.6}, {:>10.6}) AU  vel=({:>10.6}, {:>10.6}, {:>10.6}) AU/yr",
                    b.name, b.pos.x, b.pos.y, b.pos.z, b.vel.x, b.vel.y, b.vel.z
                );
            }
        }
    }

    let elapsed = start.elapsed();
    let secs = elapsed.as_secs_f64();

    println!("\nSimulation finished.");
    println!("  Steps: {}", steps);
    println!("  dt: {} years", dt);
    println!("  Elapsed: {:.6} s", secs);
    println!("  Steps/s: {:.2}", (steps as f64) / secs);
}
