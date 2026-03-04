use std::env;

#[inline(always)]
fn a(i: usize, j: usize) -> f64 {
    // A(i,j) = 1 / ( (i+j)(i+j+1)/2 + i + 1 )
    let ij = i + j;
    let denom = (ij * (ij + 1)) / 2 + i + 1;
    1.0 / (denom as f64)
}

fn mult_av(n: usize, v: &[f64], out: &mut [f64]) {
    // out[i] = sum_j A(i,j) * v[j]
    for i in 0..n {
        let mut sum = 0.0_f64;
        for j in 0..n {
            sum += a(i, j) * v[j];
        }
        out[i] = sum;
    }
}

fn mult_atv(n: usize, v: &[f64], out: &mut [f64]) {
    // out[i] = sum_j A(j,i) * v[j]  (i.e., A^T * v)
    for i in 0..n {
        let mut sum = 0.0_f64;
        for j in 0..n {
            sum += a(j, i) * v[j];
        }
        out[i] = sum;
    }
}

fn mult_at_a_v(n: usize, v: &[f64], tmp: &mut [f64], out: &mut [f64]) {
    // out = A^T * (A * v), using tmp as scratch
    mult_av(n, v, tmp);
    mult_atv(n, tmp, out);
}

fn dot(x: &[f64], y: &[f64]) -> f64 {
    let mut s = 0.0_f64;
    for i in 0..x.len() {
        s += x[i] * y[i];
    }
    s
}

fn main() {
    // Read n from CLI: cargo run --release -- 5500
    let n: usize = match env::args().nth(1) {
        Some(s) => s.parse().unwrap_or_else(|_| {
            eprintln!("Error: n must be a positive integer.");
            std::process::exit(2);
        }),
        None => {
            eprintln!("Usage: spectral_norm <n>");
            std::process::exit(2);
        }
    };

    if n == 0 {
        eprintln!("Error: n must be >= 1.");
        std::process::exit(2);
    }

    // u starts as all ones
    let mut u = vec![1.0_f64; n];
    let mut v = vec![0.0_f64; n];
    let mut tmp = vec![0.0_f64; n];

    // Power Method iterations
    // Common benchmark uses 10 iterations
    for _ in 0..10 {
        mult_at_a_v(n, &u, &mut tmp, &mut v);
        std::mem::swap(&mut u, &mut v);
    }

    // After loop, compute v = A^T(Au) one more time to form Rayleigh quotient cleanly:
    // This avoids depending on whether u/v were swapped last.
    mult_at_a_v(n, &u, &mut tmp, &mut v);

    let uv = dot(&u, &v);
    let vv = dot(&v, &v);

    let result = (uv / vv).sqrt();
    println!("{:.9}", result);
}
