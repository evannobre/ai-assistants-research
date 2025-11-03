#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

// Configuration constants
#define DEFAULT_N 2048
#define MAX_ITER 256
#define ESCAPE_RADIUS 4.0

// Mandelbrot set boundaries
#define X_MIN -2.5
#define X_MAX 1.0
#define Y_MIN -1.25
#define Y_MAX 1.25

// Color palette structure
typedef struct {
    uint8_t r, g, b;
} RGB;

// Generate smooth color palette using HSV to RGB conversion
void generate_palette(RGB *palette, int max_iter) {
    for (int i = 0; i < max_iter; i++) {
        double t = (double)i / (double)max_iter;
        double h = 360.0 * t;
        double s = 0.8;
        double v = (i < max_iter - 1) ? 1.0 : 0.0;
        
        double c = v * s;
        double x = c * (1.0 - fabs(fmod(h / 60.0, 2.0) - 1.0));
        double m = v - c;
        
        double r, g, b;
        if (h < 60) { r = c; g = x; b = 0; }
        else if (h < 120) { r = x; g = c; b = 0; }
        else if (h < 180) { r = 0; g = c; b = x; }
        else if (h < 240) { r = 0; g = x; b = c; }
        else if (h < 300) { r = x; g = 0; b = c; }
        else { r = c; g = 0; b = x; }
        
        palette[i].r = (uint8_t)((r + m) * 255);
        palette[i].g = (uint8_t)((g + m) * 255);
        palette[i].b = (uint8_t)((b + m) * 255);
    }
}

// Core Mandelbrot iteration function
// Uses the recurrence: z_(n+1) = z_n^2 + C, where z_0 = 0
int mandelbrot_iterations(double cr, double ci, int max_iter) {
    double zr = 0.0, zi = 0.0;
    double zr_sq = 0.0, zi_sq = 0.0;
    int iter;
    
    for (iter = 0; iter < max_iter; iter++) {
        // Check escape condition: |z|^2 > 4
        if (zr_sq + zi_sq > ESCAPE_RADIUS) {
            break;
        }
        
        // z_(n+1) = z_n^2 + C
        // (zr + zi*i)^2 = zr^2 - zi^2 + 2*zr*zi*i
        zi = 2.0 * zr * zi + ci;
        zr = zr_sq - zi_sq + cr;
        
        // Cache squares for next iteration
        zr_sq = zr * zr;
        zi_sq = zi * zi;
    }
    
    return iter;
}

// Write PPM (Portable PixMap) format - native bitmap format
int write_ppm(const char *filename, RGB *pixels, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Failed to open output file");
        return -1;
    }
    
    // PPM header: P6 (binary), width, height, max color value
    fprintf(fp, "P6\n%d %d\n255\n", width, height);
    
    // Write pixel data
    size_t pixels_written = fwrite(pixels, sizeof(RGB), width * height, fp);
    fclose(fp);
    
    if (pixels_written != (size_t)(width * height)) {
        fprintf(stderr, "Error: Incomplete write\n");
        return -1;
    }
    
    return 0;
}

// Main Mandelbrot computation and rendering
int generate_mandelbrot(int n, const char *output_file) {
    // Memory allocation check
    size_t required_memory = (size_t)n * n * sizeof(RGB);
    size_t max_memory = 1024UL * 1024UL * 1024UL * 6; // 6 GB limit (leaving 2GB for OS)
    
    if (required_memory > max_memory) {
        fprintf(stderr, "Error: Requested size %dx%d requires %.2f GB, exceeds memory limit\n",
                n, n, required_memory / (1024.0 * 1024.0 * 1024.0));
        return -1;
    }
    
    printf("Generating %dx%d Mandelbrot set...\n", n, n);
    printf("Memory required: %.2f MB\n", required_memory / (1024.0 * 1024.0));
    
    // Allocate pixel buffer
    RGB *pixels = (RGB*)malloc(required_memory);
    if (!pixels) {
        perror("Failed to allocate pixel buffer");
        return -1;
    }
    
    // Generate color palette
    RGB *palette = (RGB*)malloc(MAX_ITER * sizeof(RGB));
    if (!palette) {
        perror("Failed to allocate palette");
        free(pixels);
        return -1;
    }
    generate_palette(palette, MAX_ITER);
    
    // Compute scaling factors for complex plane mapping
    double dx = (X_MAX - X_MIN) / (double)n;
    double dy = (Y_MAX - Y_MIN) / (double)n;
    
    // Main computation loop
    printf("Computing fractal...\n");
    for (int py = 0; py < n; py++) {
        if (py % (n / 10) == 0) {
            printf("Progress: %.1f%%\n", 100.0 * py / n);
        }
        
        double ci = Y_MAX - py * dy; // Flip Y axis for correct orientation
        
        for (int px = 0; px < n; px++) {
            double cr = X_MIN + px * dx;
            
            // Apply quadratic recurrence equation
            int iter = mandelbrot_iterations(cr, ci, MAX_ITER);
            
            // Map iterations to color
            int idx = py * n + px;
            pixels[idx] = palette[iter % MAX_ITER];
        }
    }
    printf("Progress: 100.0%%\n");
    
    // Write output file
    printf("Writing to %s...\n", output_file);
    int result = write_ppm(output_file, pixels, n, n);
    
    // Cleanup
    free(palette);
    free(pixels);
    
    if (result == 0) {
        printf("Successfully generated Mandelbrot set!\n");
        printf("Output file: %s (%.2f MB)\n", output_file, 
               required_memory / (1024.0 * 1024.0));
    }
    
    return result;
}

int main(int argc, char *argv[]) {
    int n = DEFAULT_N;
    const char *output_file = "mandelbrot.ppm";
    
    // Parse command line arguments
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0 || n > 16384) {
            fprintf(stderr, "Error: Invalid size %d (must be 1-16384)\n", n);
            return 1;
        }
    }
    
    if (argc > 2) {
        output_file = argv[2];
    }
    
    printf("Mandelbrot Set Generator\n");
    printf("========================\n");
    printf("Resolution: %dx%d\n", n, n);
    printf("Max iterations: %d\n", MAX_ITER);
    printf("Complex plane: [%.2f, %.2f] x [%.2f, %.2f]\n", 
           X_MIN, X_MAX, Y_MIN, Y_MAX);
    printf("\n");
    
    int result = generate_mandelbrot(n, output_file);
    
    if (result == 0) {
        printf("\nTo view the image:\n");
        printf("  - Install ImageMagick: sudo apt install imagemagick\n");
        printf("  - Convert to PNG: convert %s mandelbrot.png\n", output_file);
        printf("  - Or view directly: display %s\n", output_file);
    }
    
    return result;
}