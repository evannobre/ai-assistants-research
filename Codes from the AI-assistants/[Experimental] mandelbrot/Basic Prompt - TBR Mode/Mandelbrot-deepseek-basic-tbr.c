#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_square(Complex c) {
    Complex result;
    result.real = c.real * c.real - c.imag * c.imag;
    result.imag = 2 * c.real * c.imag;
    return result;
}

Complex complex_add(Complex a, Complex b) {
    Complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

double complex_magnitude(Complex c) {
    return sqrt(c.real * c.real + c.imag * c.imag);
}

int mandelbrot_iterations(Complex c, int max_iter) {
    Complex z = {0.0, 0.0};
    int iter = 0;
    
    while (complex_magnitude(z) <= 2.0 && iter < max_iter) {
        z = complex_add(complex_square(z), c);
        iter++;
    }
    
    return iter;
}

void generate_mandelbrot_pbm(int N, int max_iter, const char* filename) {
    FILE *file = fopen(filename, "wb");
    if (!file) {
        perror("Failed to open file");
        return;
    }
    
    // Write PBM header
    fprintf(file, "P1\n");
    fprintf(file, "%d %d\n", N, N);
    
    double x_min = -2.0, x_max = 1.0;
    double y_min = -1.5, y_max = 1.5;
    double x_step = (x_max - x_min) / (N - 1);
    double y_step = (y_max - y_min) / (N - 1);
    
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            Complex c;
            c.real = x_min + j * x_step;
            c.imag = y_min + i * y_step;
            
            int iter = mandelbrot_iterations(c, max_iter);
            
            // 1 for in set (black), 0 for out of set (white)
            int pixel = (iter == max_iter) ? 1 : 0;
            fprintf(file, "%d ", pixel);
        }
        fprintf(file, "\n");
    }
    
    fclose(file);
    printf("Mandelbrot set saved to %s\n", filename);
}

int main() {
    int N = 800;  // Image size
    int max_iter = 1000;
    
    generate_mandelbrot_pbm(N, max_iter, "mandelbrot.pbm");
    return 0;
}