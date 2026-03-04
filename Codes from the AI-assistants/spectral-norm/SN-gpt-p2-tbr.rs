use std::env;

fn eval_a(i: usize, j: usize) -> f64 {
    // 0-based formula:
    // A[i,j] = 1 / ( (s*(s+1))/2 + i + 1 ), where s = i + j
    let s = (i + j) as u64;
    let denom = (s * (s + 1)) / 2 + (i as u64) + 1;
    1.0 / (denom as f64)
}

fn mult_a(u: &[f64], out: &mut [f64]) {
    let n = u.len();
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += eval_a(i, j) * u[j];
        }
        out[i] = sum;
    }
}

fn mult_at(u: &[f64], out: &mut [f64]) {
    let n = u.len();
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += eval_a(j, i) * u[j];
        }
        out[i] = sum;
    }
}

fn mult_ata(u: &[f64], tmp: &mut [f64], out: &mut [f64]) {
    // out = A^T (A u)
    mult_a(u, tmp);
    mult_at(tmp, out);
}

fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b.iter()).map(|(x, y)| x * y).sum()
}

fn main() {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1000);

    let iters = 10;

    let mut u = vec![1.0f64; n];
    let mut v = vec![0.0f64; n];
    let mut tmp = vec![0.0f64; n];

    for _ in 0..iters {
        mult_ata(&u, &mut tmp, &mut v);
        mult_ata(&v, &mut tmp, &mut u);
    }

    // Rayleigh quotient-like estimate:
    // After the loop, v is not necessarily the last A^T(Au),
    // but the standard benchmark computes using u and v as below.
    let num = dot(&u, &v);
    let den = dot(&v, &v);
    let norm = (num / den).sqrt();

    println!("{:.9}", norm);
}
