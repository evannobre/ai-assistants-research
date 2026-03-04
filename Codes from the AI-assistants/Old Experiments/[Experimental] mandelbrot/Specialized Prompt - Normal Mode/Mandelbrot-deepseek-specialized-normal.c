#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

// Configuration constants optimized for your hardware
#define N 4096  // Max resolution that fits in 8GB RAM (4096x4096x4 bytes ≈ 67MB)
#define MAX_ITERATIONS 256
#define ESCAPE_RADIUS_SQ 4.0

// Complex number structure for clarity
typedef struct {
    double real;
    double imag;
} complex_t;

// Optimized Mandelbrot calculation using iterative method
static inline int calculate_mandelbrot(const complex_t c) {
    double z_real = 0.0, z_imag = 0.0;
    double z_real_sq = 0.0, z_imag_sq = 0.0;
    
    for (int i = 0; i < MAX_ITERATIONS; i++) {
        // Check escape condition early
        if (z_real_sq + z_imag_sq > ESCAPE_RADIUS_SQ) {
            return i;
        }
        
        // Calculate next iteration: z = z^2 + c
        z_imag = 2.0 * z_real * z_imag + c.imag;
        z_real = z_real_sq - z_imag_sq + c.real;
        
        // Update squares for next iteration
        z_real_sq = z_real * z_real;
        z_imag_sq = z_imag * z_imag;
    }
    
    return MAX_ITERATIONS; // Point is in Mandelbrot set
}

// Generate PBM header
void write_pbm_header(FILE *file, int width, int height) {
    fprintf(file, "P1\n%d %d\n", width, height);
}

// Generate the Mandelbrot set and save as PBM
void generate_mandelbrot_pbm(const char *filename, int width, int height, 
                            double center_x, double center_y, double zoom) {
    // Allocate memory for the image (1 bit per pixel)
    uint8_t *image = calloc((width * height + 7) / 8, sizeof(uint8_t));
    if (!image) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Calculate viewport boundaries
    double scale = 3.0 / zoom;
    double x_min = center_x - scale;
    double x_max = center_x + scale;
    double y_min = center_y - scale * height / width;
    double y_max = center_y + scale * height / width;
    
    // Pixel step sizes
    double x_step = (x_max - x_min) / width;
    double y_step = (y_max - y_min) / height;
    
    printf("Generating Mandelbrot set %dx%d (zoom: %.2f)\n", width, height, zoom);
    printf("Viewport: [%.6f, %.6f] x [%.6f, %.6f]\n", x_min, x_max, y_min, y_max);
    
    clock_t start_time = clock();
    
    // Generate Mandelbrot set
    #pragma omp parallel for schedule(dynamic)  // Parallelize for performance
    for (int y = 0; y < height; y++) {
        double c_imag = y_min + y * y_step;
        
        for (int x = 0; x < width; x++) {
            double c_real = x_min + x * x_step;
            
            complex_t c = {c_real, c_imag};
            int iterations = calculate_mandelbrot(c);
            
            // Set pixel to 1 if in Mandelbrot set (black), 0 otherwise (white)
            if (iterations == MAX_ITERATIONS) {
                int bit_index = y * width + x;
                image[bit_index / 8] |= (1 << (7 - (bit_index % 8)));
            }
        }
        
        // Progress indicator
        if (y % (height / 10) == 0) {
            printf("Progress: %.0f%%\n", (double)y / height * 100);
        }
    }
    
    clock_t end_time = clock();
    double elapsed = (double)(end_time - start_time) / CLOCKS_PER_SEC;
    printf("Calculation time: %.2f seconds\n", elapsed);
    
    // Write PBM file
    FILE *file = fopen(filename, "wb");
    if (!file) {
        fprintf(stderr, "Cannot open file: %s\n", filename);
        free(image);
        exit(1);
    }
    
    write_pbm_header(file, width, height);
    
    // Write image data
    size_t data_size = (width * height + 7) / 8;
    for (size_t i = 0; i < data_size; i++) {
        // Write each byte as ASCII '0' and '1' characters
        for (int bit = 7; bit >= 0; bit--) {
            int pixel_index = i * 8 + (7 - bit);
            if (pixel_index < width * height) {
                fprintf(file, "%c ", (image[i] & (1 << bit)) ? '1' : '0');
                
                // Add newlines for readability (optional)
                if ((pixel_index + 1) % width == 0) {
                    fprintf(file, "\n");
                }
            }
        }
    }
    
    fclose(file);
    free(image);
    
    printf("Mandelbrot set saved to: %s\n", filename);
}

// Memory usage estimation
void print_memory_usage(int width, int height) {
    size_t image_memory = (width * height + 7) / 8;  // PBM uses 1 bit per pixel
    size_t total_estimated = image_memory + sizeof(uint8_t*) + 1024; // Add overhead
    
    printf("Memory usage estimation:\n");
    printf("  Image data: %.2f MB\n", (double)image_memory / (1024 * 1024));
    printf("  Total estimated: %.2f MB\n", (double)total_estimated / (1024 * 1024));
    printf("  Available RAM: 8192 MB\n");
}

int main(int argc, char *argv[]) {
    // Default parameters
    int width = 2048;
    int height = 2048;
    double center_x = -0.5;
    double center_y = 0.0;
    double zoom = 1.0;
    const char *filename = "mandelbrot.pbm";
    
    // Parse command line arguments
    if (argc > 1) width = atoi(argv[1]);
    if (argc > 2) height = atoi(argv[2]);
    if (argc > 3) center_x = atof(argv[3]);
    if (argc > 4) center_y = atof(argv[4]);
    if (argc > 5) zoom = atof(argv[5]);
    if (argc > 6) filename = argv[6];
    
    // Validate input parameters
    if (width <= 0 || height <= 0) {
        fprintf(stderr, "Error: Width and height must be positive integers\n");
        return 1;
    }
    
    if (width > N || height > N) {
        fprintf(stderr, "Error: Maximum resolution exceeded (%dx%d > %dx%d)\n", 
                width, height, N, N);
        fprintf(stderr, "Please use dimensions <= %d to respect memory constraints\n", N);
        return 1;
    }
    
    printf("Mandelbrot Set Generator\n");
    printf("========================\n");
    printf("Resolution: %dx%d pixels\n", width, height);
    printf("Center: (%.6f, %.6f)\n", center_x, center_y);
    printf("Zoom: %.2fx\n", zoom);
    printf("Max iterations: %d\n", MAX_ITERATIONS);
    
    print_memory_usage(width, height);
    
    // Generate the Mandelbrot set
    generate_mandelbrot_pbm(filename, width, height, center_x, center_y, zoom);
    
    printf("\nTo view the result:\n");
    printf("  display %s  # If ImageMagick is installed\n", filename);
    printf("  Or convert to PNG: convert %s mandelbrot.png\n", filename);
    
    return 0;
}