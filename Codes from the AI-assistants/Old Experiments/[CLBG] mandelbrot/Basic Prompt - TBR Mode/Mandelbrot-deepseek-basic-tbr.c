#include <stdio.h>
#include <stdlib.h>
#include <complex.h>

void mandelbrot(int N, const char* filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) return;
    
    // PBM header
    fprintf(fp, "P4\n%d %d\n", N, N);
    
    // Precompute constants
    double x_min = -1.5, x_max = 0.5;
    double y_min = -1.0, y_max = 1.0;
    double x_step = (x_max - x_min) / (N - 1);
    double y_step = (y_max - y_min) / (N - 1);
    
    const int max_iter = 1000;
    
    // Process image row by row
    for (int y = 0; y < N; y++) {
        double c_imag = y_min + y * y_step;
        
        // Process 8 pixels at a time (1 byte)
        for (int x = 0; x < N; x += 8) {
            unsigned char byte = 0;
            
            for (int bit = 0; bit < 8; bit++) {
                int x_pos = x + bit;
                if (x_pos >= N) {
                    byte <<= (8 - bit);
                    break;
                }
                
                double c_real = x_min + x_pos * x_step;
                double complex c = c_real + c_imag * I;
                double complex z = 0 + 0 * I;
                int iter;
                
                for (iter = 0; iter < max_iter; iter++) {
                    z = z * z + c;
                    if (creal(z) * creal(z) + cimag(z) * cimag(z) > 4.0) {
                        break;
                    }
                }
                
                byte <<= 1;
                if (iter == max_iter) {
                    byte |= 1;  // Inside Mandelbrot set (black)
                }
                // else: Outside (white) - bit remains 0
            }
            
            fputc(byte, fp);
        }
    }
    
    fclose(fp);
}

int main(int argc, char *argv[]) {
    int N = 16000;
    if (argc > 1) {
        N = atoi(argv[1]);
    }
    
    mandelbrot(N, "mandelbrot.pbm");
    return 0;
}