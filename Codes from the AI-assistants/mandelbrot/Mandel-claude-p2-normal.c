#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdint.h>
#include <string.h>

// Configuration constants
#define DEFAULT_N 2048
#define MAX_ITERATIONS 256
#define ESCAPE_RADIUS 2.0

// Mandelbrot domain bounds
#define XMIN -2.5
#define XMAX 1.0
#define YMIN -1.25
#define YMAX 1.25

// Color palette structure
typedef struct {
    uint8_t r, g, b;
} RGB;

/**
 * Compute the number of iterations before escape for point c
 * Uses the recurrence: z_(n+1) = z_n^2 + c, with z_0 = 0
 * 
 * @param c Complex constant for the point being tested
 * @param max_iter Maximum number of iterations
 * @return Number of iterations before escape (or max_iter if bounded)
 */
int mandelbrot_iterations(double complex c, int max_iter) {
    double complex z = 0.0 + 0.0 * I;
    int n;
    
    for (n = 0; n < max_iter; n++) {
        // Check escape condition: |z| > ESCAPE_RADIUS
        if (cabs(z) > ESCAPE_RADIUS) {
            return n;
        }
        
        // Apply recurrence: z_(n+1) = z_n^2 + c
        z = z * z + c;
    }
    
    return max_iter;
}

/**
 * Map iteration count to RGB color using smooth gradient
 * 
 * @param iter Number of iterations
 * @param max_iter Maximum iterations
 * @return RGB color structure
 */
RGB iter_to_color(int iter, int max_iter) {
    RGB color;
    
    if (iter == max_iter) {
        // Points in the Mandelbrot set are black
        color.r = 0;
        color.g = 0;
        color.b = 0;
    } else {
        // Create a smooth color gradient for escaped points
        double t = (double)iter / max_iter;
        
        // Use sinusoidal functions for smooth color transitions
        color.r = (uint8_t)(9 * (1 - t) * t * t * t * 255);
        color.g = (uint8_t)(15 * (1 - t) * (1 - t) * t * t * 255);
        color.b = (uint8_t)(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    }
    
    return color;
}

/**
 * Generate Mandelbrot set and write to PPM file
 * 
 * @param n Image dimension (n x n pixels)
 * @param filename Output filename
 * @return 0 on success, -1 on error
 */
int generate_mandelbrot(int n, const char *filename) {
    FILE *fp;
    RGB *buffer;
    double x_scale, y_scale;
    int i, j;
    
    // Calculate memory requirements
    size_t buffer_size = (size_t)n * n * sizeof(RGB);
    double mem_gb = buffer_size / (1024.0 * 1024.0 * 1024.0);
    
    printf("Generating %dx%d Mandelbrot set...\n", n, n);
    printf("Memory required: %.2f MB\n", mem_gb * 1024);
    
    // Check memory constraints (keep under 4GB for safety on 8GB system)
    if (mem_gb > 4.0) {
        fprintf(stderr, "Error: Image size too large (%.2f GB > 4 GB limit)\n", mem_gb);
        return -1;
    }
    
    // Allocate buffer for entire image
    buffer = (RGB *)malloc(buffer_size);
    if (!buffer) {
        fprintf(stderr, "Error: Failed to allocate memory\n");
        return -1;
    }
    
    // Calculate scaling factors for mapping pixels to complex plane
    x_scale = (XMAX - XMIN) / (n - 1);
    y_scale = (YMAX - YMIN) / (n - 1);
    
    // Compute Mandelbrot set
    printf("Computing iterations...\n");
    for (i = 0; i < n; i++) {
        if (i % (n / 10) == 0) {
            printf("Progress: %.0f%%\n", (100.0 * i) / n);
        }
        
        for (j = 0; j < n; j++) {
            // Map pixel (i, j) to complex plane coordinates
            double x = XMIN + j * x_scale;
            double y = YMAX - i * y_scale;  // Flip y-axis for correct orientation
            double complex c = x + y * I;
            
            // Compute iterations for this point
            int iter = mandelbrot_iterations(c, MAX_ITERATIONS);
            
            // Convert to color and store in buffer
            buffer[i * n + j] = iter_to_color(iter, MAX_ITERATIONS);
        }
    }
    printf("Progress: 100%%\n");
    
    // Write PPM file (P6 binary format)
    printf("Writing to %s...\n", filename);
    fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Error: Cannot open file %s\n", filename);
        free(buffer);
        return -1;
    }
    
    // Write PPM header
    fprintf(fp, "P6\n%d %d\n255\n", n, n);
    
    // Write pixel data
    fwrite(buffer, sizeof(RGB), (size_t)n * n, fp);
    
    fclose(fp);
    free(buffer);
    
    printf("Done! Image saved to %s\n", filename);
    return 0;
}

int main(int argc, char *argv[]) {
    int n = DEFAULT_N;
    char filename[256] = "mandelbrot.ppm";
    
    // Parse command line arguments
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0 || n > 16384) {
            fprintf(stderr, "Error: Invalid dimension. Use value between 1 and 16384\n");
            return 1;
        }
    }
    
    if (argc > 2) {
        strncpy(filename, argv[2], sizeof(filename) - 1);
        filename[sizeof(filename) - 1] = '\0';
    }
    
    printf("=== Mandelbrot Set Generator ===\n");
    printf("Recurrence: z_(n+1) = z_n^2 + c, z_0 = 0\n");
    printf("Domain: [%.2f, %.2f] x [%.2f, %.2f]\n", XMIN, XMAX, YMIN, YMAX);
    printf("Max iterations: %d\n", MAX_ITERATIONS);
    printf("Escape radius: %.1f\n\n", ESCAPE_RADIUS);
    
    if (generate_mandelbrot(n, filename) != 0) {
        return 1;
    }
    
    printf("\nTo view the image, you can use:\n");
    printf("  - eog %s (Eye of GNOME)\n", filename);
    printf("  - feh %s\n", filename);
    printf("  - convert %s mandelbrot.png (ImageMagick)\n", filename);
    
    return 0;
}
