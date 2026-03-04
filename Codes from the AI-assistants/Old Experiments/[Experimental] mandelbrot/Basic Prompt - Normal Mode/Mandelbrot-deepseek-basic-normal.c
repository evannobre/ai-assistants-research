#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double real;
    double imag;
} Complex;

int mandelbrot_iterations(Complex c, int max_iter) {
    Complex z = {0.0, 0.0};
    int iter = 0;
    
    while (iter < max_iter) {
        double z_real_sq = z.real * z.real;
        double z_imag_sq = z.imag * z.imag;
        
        if (z_real_sq + z_imag_sq > 4.0) {
            break;
        }
        
        double new_real = z_real_sq - z_imag_sq + c.real;
        double new_imag = 2.0 * z.real * z.imag + c.imag;
        
        z.real = new_real;
        z.imag = new_imag;
        iter++;
    }
    
    return iter;
}

void generate_mandelbrot_pbm(const char* filename, int width, int height, 
                            double x_min, double x_max, double y_min, double y_max, 
                            int max_iter) {
    FILE* file = fopen(filename, "wb");
    if (!file) {
        perror("Failed to open file");
        return;
    }
    
    // Write PBM header
    fprintf(file, "P1\n%d %d\n", width, height);
    
    // Generate Mandelbrot set
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            Complex c;
            c.real = x_min + (x_max - x_min) * x / (width - 1);
            c.imag = y_min + (y_max - y_min) * y / (height - 1);
            
            int iter = mandelbrot_iterations(c, max_iter);
            
            // Output 1 for points in Mandelbrot set, 0 for points outside
            fprintf(file, "%d ", (iter == max_iter) ? 1 : 0);
        }
        fprintf(file, "\n");
    }
    
    fclose(file);
}

int main() {
    int width = 800;
    int height = 600;
    int max_iter = 1000;
    
    // Define the region to plot
    double x_min = -2.0;
    double x_max = 1.0;
    double y_min = -1.0;
    double y_max = 1.0;
    
    generate_mandelbrot_pbm("mandelbrot.pbm", width, height, 
                           x_min, x_max, y_min, y_max, max_iter);
    
    printf("Mandelbrot set saved to mandelbrot.pbm\n");
    return 0;
}