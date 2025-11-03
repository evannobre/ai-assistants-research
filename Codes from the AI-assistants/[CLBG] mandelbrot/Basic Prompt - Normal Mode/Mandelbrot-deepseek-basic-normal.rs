use std::io::{self, Write};

fn mandelbrot(size: usize, max_iter: usize) -> io::Result<()> {
    let mut stdout = io::stdout();
    
    // Write PBM header
    writeln!(stdout, "P4\n{} {}", size, size)?;
    
    let y_step = 2.0 / size as f64;
    let x_step = 2.0 / size as f64;
    
    for y in 0..size {
        let c_im = -1.0 + y as f64 * y_step;
        let mut byte: u8 = 0;
        let mut bit_pos: u8 = 0;
        
        for x in 0..size {
            let c_re = -1.5 + x as f64 * x_step;
            
            // Check main cardioid and period-2 bulb
            let q = (c_re - 0.25).powi(2) + c_im.powi(2);
            let iter = if q * (q + (c_re - 0.25)) <= 0.25 * c_im.powi(2) ||
                (c_re + 1.0).powi(2) + c_im.powi(2) <= 0.0625 {
                max_iter
            } else {
                // Standard iteration
                let (mut z_re, mut z_im) = (0.0, 0.0);
                let mut iter = 0;
                
                while iter < max_iter && z_re * z_re + z_im * z_im <= 4.0 {
                    let new_re = z_re * z_re - z_im * z_im + c_re;
                    let new_im = 2.0 * z_re * z_im + c_im;
                    z_re = new_re;
                    z_im = new_im;
                    iter += 1;
                }
                iter
            };
            
            // Set bit if in Mandelbrot set
            if iter == max_iter {
                byte |= 1 << (7 - bit_pos);
            }
            
            bit_pos += 1;
            if bit_pos == 8 || x == size - 1 {
                stdout.write_all(&[byte])?;
                byte = 0;
                bit_pos = 0;
            }
        }
    }
    Ok(())
}

fn main() -> io::Result<()> {
    let size = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1000);
    let max_iter = std::env::args()
        .nth(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1000);
    
    mandelbrot(size, max_iter)
}