#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define WIDTH 800
#define HEIGHT 800
#define MAX_ITER 256

double complex map_to_complex(int x, int y) {
    double real = (x - WIDTH * 2.0 / 3.0) / (WIDTH * 0.4);
    double imag = (y - HEIGHT / 2.0) / (HEIGHT * 0.4);
    return real + imag * I;
}

int mandelbrot_iterations(double complex c) {
    double complex z = 0 + 0 * I;
    int iter = 0;
    
    while (creal(z) * creal(z) + cimag(z) * cimag(z) <= 4.0 && iter < MAX_ITER) {
        z = z * z + c;
        iter++;
    }
    
    return iter;
}

int main() {
    FILE *fp = fopen("mandelbrot.pbm", "wb");
    if (!fp) {
        perror("Cannot open file");
        return 1;
    }
    
    // Write PBM header
    fprintf(fp, "P1\n%d %d\n", WIDTH, HEIGHT);
    
    // Generate Mandelbrot set
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            double complex c = map_to_complex(x, y);
            int iter = mandelbrot_iterations(c);
            
            // Write pixel: 1 for inside/black, 0 for outside/white
            fputc(iter == MAX_ITER ? '1' : '0', fp);
            fputc(' ', fp);
        }
        fputc('\n', fp);
    }
    
    fclose(fp);
    printf("Mandelbrot set saved to mandelbrot.pbm\n");
    
    return 0;
}