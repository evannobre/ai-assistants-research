#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

// Configuration constants
#define DEFAULT_WIDTH 2048
#define DEFAULT_HEIGHT 2048
#define MAX_ITERATIONS 256
#define ESCAPE_RADIUS 2.0

// Complex number bounds for standard Mandelbrot view
#define RE_MIN -2.5
#define RE_MAX 1.0
#define IM_MIN -1.25
#define IM_MAX 1.25

// Color palette structure
typedef struct {
    uint8_t r, g, b;
} RGB;

/**
 * Mandelbrot iteration function
 * Implements: z_(n+1) = (z_n)^2 + C
 * Returns: number of iterations before escape
 */
static inline int mandelbrot_iterations(double c_re, double c_im) {
    double z_re = 0.0, z_im = 0.0;
    double z_re2 = 0.0, z_im2 = 0.0;
    int iter = 0;
    
    // Optimized escape condition: |z|^2 > 4
    while (z_re2 + z_im2 <= 4.0 && iter < MAX_ITERATIONS) {
        z_im = 2.0 * z_re * z_im + c_im;
        z_re = z_re2 - z_im2 + c_re;
        z_re2 = z_re * z_re;
        z_im2 = z_im * z_im;
        iter++;
    }
    
    return iter;
}

/**
 * Map iteration count to RGB color
 * Uses smooth color gradient for aesthetic visualization
 */
static RGB map_color(int iterations) {
    RGB color;
    
    if (iterations == MAX_ITERATIONS) {
        // Points in the set are black
        color.r = color.g = color.b = 0;
    } else {
        // Smooth color gradient based on iteration count
        double t = (double)iterations / MAX_ITERATIONS;
        
        // Multi-band coloring scheme
        color.r = (uint8_t)(9 * (1 - t) * t * t * t * 255);
        color.g = (uint8_t)(15 * (1 - t) * (1 - t) * t * t * 255);
        color.b = (uint8_t)(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    }
    
    return color;
}

/**
 * Write PBM P6 (binary) format
 * Efficient binary format with minimal overhead
 */
int write_pbm(const char *filename, RGB *pixels, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Error opening file");
        return -1;
    }
    
    // Write PBM header (P6 = binary RGB)
    fprintf(fp, "P6\n%d %d\n255\n", width, height);
    
    // Write pixel data in row-major order
    size_t total_pixels = (size_t)width * height;
    size_t written = fwrite(pixels, sizeof(RGB), total_pixels, fp);
    
    fclose(fp);
    
    if (written != total_pixels) {
        fprintf(stderr, "Error: incomplete write\n");
        return -1;
    }
    
    return 0;
}

/**
 * Generate Mandelbrot set
 */
int generate_mandelbrot(int width, int height, const char *output_file) {
    // Memory validation (8GB RAM constraint)
    size_t required_memory = (size_t)width * height * sizeof(RGB);
    size_t max_safe_memory = 1ULL << 30; // 1GB safety limit
    
    if (required_memory > max_safe_memory) {
        fprintf(stderr, "Error: image size too large (requires %.2f MB)\n", 
                required_memory / (1024.0 * 1024.0));
        fprintf(stderr, "Maximum safe size: %dx%d\n", 
                (int)sqrt(max_safe_memory / sizeof(RGB)),
                (int)sqrt(max_safe_memory / sizeof(RGB)));
        return -1;
    }
    
    // Allocate pixel buffer
    RGB *pixels = (RGB *)malloc(required_memory);
    if (!pixels) {
        perror("Memory allocation failed");
        return -1;
    }
    
    printf("Generating %dx%d Mandelbrot set...\n", width, height);
    printf("Memory allocated: %.2f MB\n", required_memory / (1024.0 * 1024.0));
    
    // Compute scaling factors
    double re_factor = (RE_MAX - RE_MIN) / (width - 1);
    double im_factor = (IM_MAX - IM_MIN) / (height - 1);
    
    // Generate Mandelbrot set
    for (int y = 0; y < height; y++) {
        double c_im = IM_MAX - y * im_factor;
        
        for (int x = 0; x < width; x++) {
            double c_re = RE_MIN + x * re_factor;
            
            // Compute iterations for point C = c_re + c_im*i
            int iter = mandelbrot_iterations(c_re, c_im);
            
            // Map to color and store
            pixels[y * width + x] = map_color(iter);
        }
        
        // Progress indicator every 10%
        if ((y + 1) % (height / 10) == 0) {
            printf("Progress: %d%%\n", (y + 1) * 100 / height);
        }
    }
    
    printf("Writing output to %s...\n", output_file);
    int result = write_pbm(output_file, pixels, width, height);
    
    free(pixels);
    
    if (result == 0) {
        printf("Successfully generated Mandelbrot set!\n");
    }
    
    return result;
}

int main(int argc, char *argv[]) {
    int width = DEFAULT_WIDTH;
    int height = DEFAULT_HEIGHT;
    const char *output = "mandelbrot.ppm";
    
    // Parse command-line arguments
    if (argc >= 2) {
        width = height = atoi(argv[1]);
        if (width <= 0 || width > 16384) {
            fprintf(stderr, "Invalid dimension. Must be 1-16384\n");
            return 1;
        }
    }
    if (argc >= 3) {
        output = argv[2];
    }
    
    printf("=== Mandelbrot Set Generator ===\n");
    printf("Quadratic Recurrence: z_(n+1) = z_n^2 + C\n");
    printf("Initial condition: z_0 = 0\n");
    printf("Complex plane: [%.2f, %.2f] x [%.2f, %.2f]i\n", 
           RE_MIN, RE_MAX, IM_MIN, IM_MAX);
    printf("Max iterations: %d\n", MAX_ITERATIONS);
    printf("================================\n\n");
    
    return generate_mandelbrot(width, height, output);
}