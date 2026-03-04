#include <stdio.h>
#include <stdlib.h>
#include <complex.h>

void mandelbrot(int size, int max_iter) {
    // Write PBM header
    printf("P4\n%d %d\n", size, size);
    
    double y_step = 2.0 / size;
    double x_step = 2.0 / size;
    int bytes_per_row = (size + 7) / 8;
    
    for (int y = 0; y < size; y++) {
        double complex c_im = -1.0 + y * y_step;
        unsigned char byte = 0;
        int bit_pos = 0;
        
        for (int x = 0; x < size; x++) {
            double complex c = (-1.5 + x * x_step) + c_im * I;
            double complex z = 0 + 0 * I;
            int iter = 0;
            
            // Check if point is in main cardioid or period-2 bulb
            double q = (creal(c) - 0.25) * (creal(c) - 0.25) + cimag(c) * cimag(c);
            if (q * (q + (creal(c) - 0.25)) <= 0.25 * cimag(c) * cimag(c) ||
                (creal(c) + 1) * (creal(c) + 1) + cimag(c) * cimag(c) <= 0.0625) {
                iter = max_iter;
            } else {
                // Standard iteration
                while (iter < max_iter && creal(z) * creal(z) + cimag(z) * cimag(z) <= 4.0) {
                    z = z * z + c;
                    iter++;
                }
            }
            
            // Set bit if point is in Mandelbrot set (iter == max_iter)
            if (iter == max_iter) {
                byte |= (1 << (7 - bit_pos));
            }
            
            bit_pos++;
            if (bit_pos == 8 || x == size - 1) {
                putchar(byte);
                byte = 0;
                bit_pos = 0;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    int size = argc > 1 ? atoi(argv[1]) : 1000;
    int max_iter = argc > 2 ? atoi(argv[2]) : 1000;
    
    mandelbrot(size, max_iter);
    return 0;
}