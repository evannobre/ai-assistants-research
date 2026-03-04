use std::env;

#[inline(always)]
fn a(i: usize, j: usize) -> f64 {
    // 1 / (i+j+1) but with i,j as 0-based indices:
    // a(0,0)=1, a(0,1)=1/2, a(1,0)=1/3, ...
    1.0 / ((i + j + 1) as f64)
}

// (ii) out = A * v
fn mult_av(v: &[f64], out: &mut [f64]) {
    let n = v.len();
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += a(i, j) * v[j];
        }
        out[i] = sum;
    }
}

// (iii) out = A^T * v
fn mult_atv(v: &[f64], out: &mut [f64]) {
    let n = v.len();
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += a(j, i) * v[j];
        }
        out[i] = sum;
    }
}

// (iv) out = A^T * (A * v)
fn mult_atav(v: &[f64], out: &mut [f64], tmp: &mut [f64]) {
    mult_av(v, tmp);
    mult_atv(tmp, out);
}

fn dot(x: &[f64], y: &[f64]) -> f64 {
    x.iter().zip(y.iter()).map(|(a, b)| a * b).sum()
}

fn main() {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(100);

    let mut u = vec![1.0_f64; n];
    let mut v = vec![0.0_f64; n];
    let mut tmp = vec![0.0_f64; n];

    // Power method iterations (benchmark typically uses 10)
    for _ in 0..10 {
        mult_atav(&u, &mut v, &mut tmp);
        mult_atav(&v, &mut u, &mut tmp);
    }

    let v_b_v = dot(&u, &v);
    let v_v = dot(&v, &v);
    let norm = (v_b_v / v_v).sqrt();

    println!("{:.9}", norm);
}
