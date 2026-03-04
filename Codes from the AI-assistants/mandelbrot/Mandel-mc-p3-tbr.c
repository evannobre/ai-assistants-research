#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    double real;
    double imag;
} Complex;

static inline Complex complex_square(Complex z) {
    Complex result;
    double real_temp = z.real * z.real - z.imag * z.imag;
    result.imag = 2.0 * z.real * z.imag;
    result.real = real_temp;
    return result;
}

static inline Complex complex_add(Complex a, Complex b) {
    Complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

static inline double complex_magnitude_squared(Complex z) {
    return z.real * z.real + z.imag * z.imag;
}

unsigned char mandelbrot_pixel(Complex c, int max_iter) {
    Complex z = {0.0, 0.0};
    int iter = 0;
    
    while (iter < max_iter && complex_magnitude_squared(z) <= 4.0) {
        z = complex_add(complex_square(z), c);
        iter++;
    }
    
    return (iter == max_iter) ? 0 : 255;
}

void write_pbm(const char* filename, unsigned char* pixels, int width, int height) {
    FILE* fp = fopen(filename, "wb");
    if (!fp) return;
    
    fprintf(fp, "P5\n%d %d\n255\n", width, height);
    fwrite(pixels, 1, width * height, fp);
    fclose(fp);
}

void generate_mandelbrot(unsigned char* pixels, int size, 
                         double x_min, double x_max, 
                         double y_min, double y_max, 
                         int max_iter) {
    double x_step = (x_max - x_min) / size;
    double y_step = (y_max - y_min) / size;
    
    #pragma omp parallel for schedule(dynamic)
    for (int row = 0; row < size; row++) {
        double y = y_min + row * y_step;
        for (int col = 0; col < size; col++) {
            double x = x_min + col * x_step;
            Complex c = {x, y};
            pixels[row * size + col] = mandelbrot_pixel(c, max_iter);
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        return 1;
    }
    
    int size = atoi(argv[1]);
    if (size <= 0) {
        fprintf(stderr, "Size must be positive\n");
        return 1;
    }
    
    // Allocate memory for pixels
    unsigned char* pixels = (unsigned char*)malloc(size * size);
    if (!pixels) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }
    
    // Define viewing window: [-1.5-i, 0.5+i]
    double x_min = -2.0;  // Extended slightly for better view
    double x_max = 0.5;
    double y_min = -1.25;
    double y_max = 1.25;
    
    // Generate Mandelbrot set
    printf("Generating Mandelbrot set of size %dx%d...\n", size, size);
    generate_mandelbrot(pixels, size, x_min, x_max, y_min, y_max, 255);
    
    // Write to file
    write_pbm("mandelbrot.pbm", pixels, size, size);
    
    // Clean up
    free(pixels);
    printf("Done. Output written to mandelbrot.pbm\n");
    
    return 0;
}