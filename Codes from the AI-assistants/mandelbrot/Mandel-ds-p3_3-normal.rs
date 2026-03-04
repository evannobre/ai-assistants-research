use std::io::{self, Write};
use std::time::Instant;

fn mandelbrot(n: usize, max_iter: usize) -> Vec<u8> {
    let mut pixels = vec![0u8; n * n];
    let xmin = -2.0f64;
    let xmax = 1.0f64;
    let ymin = -1.5f64;
    let ymax = 1.5f64;
    
    let dx = (xmax - xmin) / (n - 1) as f64;
    let dy = (ymax - ymin) / (n - 1) as f64;
    
    for row in 0..n {
        let y = ymin + row as f64 * dy;
        for col in 0..n {
            let x = xmin + col as f64 * dx;
            
            let mut zr = 0.0f64;
            let mut zi = 0.0f64;
            let cr = x;
            let ci = y;
            let mut k = 0;
            
            while k < max_iter {
                let zr2 = zr * zr;
                let zi2 = zi * zi;
                
                if zr2 + zi2 > 4.0 {
                    break;
                }
                
                let zr_new = zr2 - zi2 + cr;
                zi = 2.0 * zr * zi + ci;
                zr = zr_new;
                k += 1;
            }
            
            pixels[row * n + col] = if k == max_iter {
                0
            } else {
                ((k * 255) / max_iter) as u8
            };
        }
    }
    
    pixels
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: {} N", args[0]);
        std::process::exit(1);
    }
    
    let n: usize = args[1].parse().expect("Invalid N");
    let max_iter = 1000;
    
    let start = Instant::now();
    
    // Generate image
    let pixels = mandelbrot(n, max_iter);
    
    // Write PGM header
    let header = format!("P5\n{} {}\n255\n", n, n);
    io::stdout().write_all(header.as_bytes()).unwrap();
    io::stdout().write_all(&pixels).unwrap();
    
    let elapsed = start.elapsed();
    eprintln!("Time: {:.2} seconds", elapsed.as_secs_f64());
}