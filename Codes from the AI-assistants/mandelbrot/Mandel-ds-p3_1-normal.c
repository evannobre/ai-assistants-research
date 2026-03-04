#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <time.h>

void mandelbrot(int N, int max_iter, FILE *fp) {
    fprintf(fp, "P5\n%d %d\n255\n", N, N);
    
    double xmin = -2.0, xmax = 1.0;  // Real part range
    double ymin = -1.5, ymax = 1.5;  // Imaginary part range
    double dx = (xmax - xmin) / (N - 1);
    double dy = (ymax - ymin) / (N - 1);
    
    unsigned char *row = malloc(N);
    
    for (int j = 0; j < N; j++) {
        double y = ymin + j * dy;
        
        for (int i = 0; i < N; i++) {
            double x = xmin + i * dx;
            
            // Complex number C = x + yi
            double complex c = x + y * I;
            double complex z = 0;
            int k;
            
            for (k = 0; k < max_iter; k++) {
                z = z * z + c;
                if (creal(z) * creal(z) + cimag(z) * cimag(z) > 4.0) {
                    break;
                }
            }
            
            // Write grayscale pixel (0-255)
            row[i] = (k == max_iter) ? 0 : (255 * k) / max_iter;
        }
        fwrite(row, 1, N, fp);
    }
    
    free(row);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s N\n", argv[0]);
        return 1;
    }
    
    int N = atoi(argv[1]);
    int max_iter = 1000;
    
    clock_t start = clock();
    
    // Write to stdout
    mandelbrot(N, max_iter, stdout);
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    fprintf(stderr, "Time: %.2f seconds\n", elapsed);
    
    return 0;
}