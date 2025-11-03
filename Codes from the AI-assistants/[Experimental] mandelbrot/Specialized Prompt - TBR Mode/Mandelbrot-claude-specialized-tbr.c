#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

// Configuration constants
#define DEFAULT_N 1024
#define MAX_ITERATIONS 256
#define ESCAPE_RADIUS 2.0

// Complex number structure
typedef struct {
    double real;
    double imag;
} Complex;

// Color structure for RGB
typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} Color;

/**
 * Mandelbrot iteration function
 * Implements: z_(n+1) = (z_n)^2 + C
 * Returns: number of iterations before escape (or MAX_ITERATIONS)
 */
int mandelbrot_iterations(Complex c) {
    Complex z = {0.0, 0.0};
    int iterations = 0;
    double z_real_sq, z_imag_sq;
    
    while (iterations < MAX_ITERATIONS) {
        z_real_sq = z.real * z.real;
        z_imag_sq = z.imag * z.imag;
        
        // Check escape condition: |z|^2 > ESCAPE_RADIUS^2
        if (z_real_sq + z_imag_sq > ESCAPE_RADIUS * ESCAPE_RADIUS) {
            break;
        }
        
        // z_(n+1) = (z_n)^2 + C
        // (a + bi)^2 = a^2 - b^2 + 2abi
        double z_real_new = z_real_sq - z_imag_sq + c.real;
        z.imag = 2.0 * z.real * z.imag + c.imag;
        z.real = z_real_new;
        
        iterations++;
    }
    
    return iterations;
}

/**
 * Map iteration count to RGB color
 * Uses smooth coloring algorithm for aesthetic results
 */
Color map_color(int iterations) {
    Color color;
    
    if (iterations == MAX_ITERATIONS) {
        // Points in the set are black
        color.r = 0;
        color.g = 0;
        color.b = 0;
    } else {
        // Smooth color gradient for escaped points
        double t = (double)iterations / MAX_ITERATIONS;
        
        // RGB gradient: blue -> cyan -> green -> yellow -> red
        color.r = (uint8_t)(9 * (1 - t) * t * t * t * 255);
        color.g = (uint8_t)(15 * (1 - t) * (1 - t) * t * t * 255);
        color.b = (uint8_t)(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    }
    
    return color;
}

/**
 * Write PPM (Portable Pixmap) file
 * PPM is a simple bitmap format that doesn't require external libraries
 */
int write_ppm(const char *filename, Color *pixels, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Error opening file");
        return -1;
    }
    
    // Write PPM header (P6 = binary PPM)
    fprintf(fp, "P6\n%d %d\n255\n", width, height);
    
    // Write pixel data
    for (int i = 0; i < width * height; i++) {
        fputc(pixels[i].r, fp);
        fputc(pixels[i].g, fp);
        fputc(pixels[i].b, fp);
    }
    
    fclose(fp);
    return 0;
}

/**
 * Generate Mandelbrot set
 */
void generate_mandelbrot(Color *pixels, int n, double x_min, double x_max, 
                         double y_min, double y_max) {
    double x_scale = (x_max - x_min) / n;
    double y_scale = (y_max - y_min) / n;
    
    for (int py = 0; py < n; py++) {
        for (int px = 0; px < n; px++) {
            // Map pixel coordinates to complex plane
            Complex c;
            c.real = x_min + px * x_scale;
            c.imag = y_max - py * y_scale;  // Flip y-axis for image orientation
            
            // Calculate iterations
            int iterations = mandelbrot_iterations(c);
            
            // Map to color
            pixels[py * n + px] = map_color(iterations);
        }
        
        // Progress indicator
        if (py % (n / 10) == 0) {
            printf("Progress: %.1f%%\r", (double)py / n * 100);
            fflush(stdout);
        }
    }
    printf("Progress: 100.0%%\n");
}

/**
 * Calculate memory requirements
 */
size_t calculate_memory(int n) {
    // 3 bytes per pixel (RGB)
    return (size_t)n * n * sizeof(Color);
}

int main(int argc, char *argv[]) {
    int n = DEFAULT_N;
    const char *output_file = "mandelbrot.ppm";
    
    // Parse command line arguments
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0 || n > 16384) {
            fprintf(stderr, "Error: N must be between 1 and 16384\n");
            return 1;
        }
    }
    if (argc > 2) {
        output_file = argv[2];
    }
    
    // Check memory requirements
    size_t required_memory = calculate_memory(n);
    printf("Generating %dx%d Mandelbrot set\n", n, n);
    printf("Memory required: %.2f MB\n", required_memory / (1024.0 * 1024.0));
    
    // Safety check for available RAM (8 GB system)
    if (required_memory > 2ULL * 1024 * 1024 * 1024) {  // 2 GB limit for safety
        fprintf(stderr, "Error: Image too large for system memory\n");
        return 1;
    }
    
    // Allocate pixel buffer
    Color *pixels = (Color *)malloc(required_memory);
    if (!pixels) {
        perror("Memory allocation failed");
        return 1;
    }
    
    // Standard Mandelbrot viewing window
    double x_min = -2.5;
    double x_max = 1.0;
    double y_min = -1.25;
    double y_max = 1.25;
    
    printf("Computing Mandelbrot set...\n");
    generate_mandelbrot(pixels, n, x_min, x_max, y_min, y_max);
    
    printf("Writing to %s...\n", output_file);
    if (write_ppm(output_file, pixels, n, n) == 0) {
        printf("Successfully created %s\n", output_file);
    } else {
        fprintf(stderr, "Failed to write output file\n");
        free(pixels);
        return 1;
    }
    
    free(pixels);
    return 0;
}