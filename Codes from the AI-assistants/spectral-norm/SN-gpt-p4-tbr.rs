use std::env;
use std::io::{self, Write};

/// (i) Compute the infinite matrix element A(i, j) for zero-based indices.
/// A(i,j) = 1 / ( (i+j)(i+j+1)/2 + i + 1 )
#[inline]
fn a(i: usize, j: usize) -> f64 {
    let ij = i + j;
    let denom = (ij * (ij + 1)) / 2 + i + 1;
    1.0 / (denom as f64)
}

/// (ii) Compute out = A * v
fn mul_av(out: &mut [f64], v: &[f64]) {
    let n = v.len();
    debug_assert_eq!(out.len(), n);

    for i in 0..n {
        let mut sum = 0.0f64;
        for j in 0..n {
            sum += a(i, j) * v[j];
        }
        out[i] = sum;
    }
}

/// (iii) Compute out = A^T * v
fn mul_atv(out: &mut [f64], v: &[f64]) {
    let n = v.len();
    debug_assert_eq!(out.len(), n);

    for i in 0..n {
        let mut sum = 0.0f64;
        for j in 0..n {
            sum += a(j, i) * v[j];
        }
        out[i] = sum;
    }
}

/// (iv) Compute out = A^T * (A * v)
fn mul_atav(out: &mut [f64], v: &[f64]) {
    let n = v.len();
    debug_assert_eq!(out.len(), n);

    // Temporary buffer for A*v (allocated once per call)
    let mut tmp = vec![0.0f64; n];
    mul_av(&mut tmp, v);
    mul_atv(out, &tmp);
}

fn dot(x: &[f64], y: &[f64]) -> f64 {
    debug_assert_eq!(x.len(), y.len());
    let mut s = 0.0f64;
    for i in 0..x.len() {
        s += x[i] * y[i];
    }
    s
}

fn main() -> io::Result<()> {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(100);

    // Power method on A^T A
    let mut u = vec![1.0f64; n];
    let mut v = vec![0.0f64; n];

    // Standard benchmark iteration count
    for _ in 0..10 {
        mul_atav(&mut v, &u);
        mul_atav(&mut u, &v);
    }

    let v_bv = dot(&v, &v);
    let u_bv = dot(&u, &v);
    let spectral_norm = (u_bv / v_bv).sqrt();

    let mut out = io::BufWriter::new(io::stdout().lock());
    writeln!(out, "{:.9}", spectral_norm)?;
    Ok(())
}
