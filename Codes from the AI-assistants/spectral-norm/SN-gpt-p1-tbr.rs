use std::f64;

#[inline]
fn a(i: usize, j: usize) -> f64 {
    let k = i + j;
    let t = (k * (k + 1)) / 2;
    1.0 / (t + i + 1) as f64
}

fn mul_a(x: &[f64], y: &mut [f64]) {
    let n = x.len();
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += a(i, j) * x[j];
        }
        y[i] = sum;
    }
}

fn mul_at(x: &[f64], y: &mut [f64]) {
    let n = x.len();
    for j in 0..n {
        let mut sum = 0.0;
        for i in 0..n {
            sum += a(i, j) * x[i];
        }
        y[j] = sum;
    }
}

fn mul_ata(x: &[f64], tmp: &mut [f64], y: &mut [f64]) {
    // y = A^T (A x)
    mul_a(x, tmp);   // tmp = A x
    mul_at(tmp, y);  // y   = A^T tmp
}

#[inline]
fn dot(x: &[f64], y: &[f64]) -> f64 {
    x.iter().zip(y.iter()).map(|(a, b)| a * b).sum()
}

pub fn spectral_norm(n: usize) -> f64 {
    let mut u = vec![1.0; n];
    let mut v = vec![0.0; n];
    let mut tmp = vec![0.0; n];

    // Power iterations on A^T A
    for _ in 0..10 {
        mul_ata(&u, &mut tmp, &mut v); // v = A^T A u
        mul_ata(&v, &mut tmp, &mut u); // u = A^T A v
    }

    // u ≈ λ v  => ||A|| ≈ sqrt( (u·v)/(v·v) )
    let uv = dot(&u, &v);
    let vv = dot(&v, &v);
    (uv / vv).sqrt()
}
