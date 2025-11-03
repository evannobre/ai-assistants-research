#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define N 800  // N-by-N image size
#define MAX_ITER 256

// RGB color struct
typedef struct {
    unsigned char r, g, b;
} RGB;

// Map iteration count to color
RGB get_color(int iter, int max_iter) {
    RGB color;
    if (iter == max_iter) {
        // Point is in the set - black
        color.r = color.g = color.b = 0;
    } else {
        // Color based on iteration count
        double t = (double)iter / max_iter;
        color.r = (unsigned char)(9 * (1 - t) * t * t * t * 255);
        color.g = (unsigned char)(15 * (1 - t) * (1 - t) * t * t * 255);
        color.b = (unsigned char)(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    }
    return color;
}

// Check if point C is in Mandelbrot set
int mandelbrot(double complex C, int max_iter) {
    double complex z = 0;
    int n;
    
    for (n = 0; n < max_iter; n++) {
        if (cabs(z) > 2.0) {
            return n;
        }
        z = z * z + C;
    }
    return max_iter;
}

int main() {
    // Allocate image buffer
    RGB *image = (RGB *)malloc(N * N * sizeof(RGB));
    if (!image) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }
    
    // Mandelbrot set bounds
    double x_min = -2.5, x_max = 1.0;
    double y_min = -1.25, y_max = 1.25;
    
    // Generate Mandelbrot set
    printf("Generating %dx%d Mandelbrot set...\n", N, N);
    
    for (int py = 0; py < N; py++) {
        for (int px = 0; px < N; px++) {
            // Map pixel to complex plane
            double x = x_min + (x_max - x_min) * px / (N - 1);
            double y = y_min + (y_max - y_min) * py / (N - 1);
            double complex C = x + y * I;
            
            // Calculate iterations
            int iter = mandelbrot(C, MAX_ITER);
            
            // Store color
            image[py * N + px] = get_color(iter, MAX_ITER);
        }
        
        // Progress indicator
        if ((py + 1) % 50 == 0) {
            printf("Progress: %d%%\n", (py + 1) * 100 / N);
        }
    }
    
    // Write PPM file (Portable Pixmap)
    FILE *fp = fopen("mandelbrot.ppm", "wb");
    if (!fp) {
        fprintf(stderr, "Cannot open output file\n");
        free(image);
        return 1;
    }
    
    // PPM header
    fprintf(fp, "P6\n%d %d\n255\n", N, N);
    
    // Write pixel data
    for (int i = 0; i < N * N; i++) {
        fwrite(&image[i], sizeof(RGB), 1, fp);
    }
    
    fclose(fp);
    free(image);
    
    printf("Mandelbrot set saved to mandelbrot.ppm\n");
    printf("You can view it with image viewers or convert it using ImageMagick:\n");
    printf("  convert mandelbrot.ppm mandelbrot.png\n");
    
    return 0;
}