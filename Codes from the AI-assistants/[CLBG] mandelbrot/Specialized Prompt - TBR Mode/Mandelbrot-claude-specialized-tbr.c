/*
 * Mandelbrot Set Generator - C with OpenMP
 * Optimized for multi-core performance
 * Compile: gcc -O3 -march=native -fopenmp -o mandelbrot mandelbrot.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAX_ITER 50

/*
 * Calculate Mandelbrot set for a single row
 * Returns bit-packed byte array where 1=not in set, 0=in set
 */
void calculate_row(uint8_t *row, int width, int y, int height) {
    const double x_min = -1.5, x_max = 0.5;
    const double y_min = -1.0, y_max = 1.0;
    
    const double x_scale = (x_max - x_min) / width;
    const double y_scale = (y_max - y_min) / height;
    
    // Calculate imaginary component for this row
    const double ci = y_min + y * y_scale;
    
    int bytes_per_row = (width + 7) / 8;
    memset(row, 0, bytes_per_row);
    
    for (int x = 0; x < width; x++) {
        // Calculate real component
        double cr = x_min + x * x_scale;
        
        // Initialize z₀ = 0
        double zr = 0.0, zi = 0.0;
        
        // Iterate recurrence relation
        int iter;
        for (iter = 0; iter < MAX_ITER; iter++) {
            // Calculate z² = (zr + zi*i)²
            double zr2 = zr * zr;
            double zi2 = zi * zi;
            
            // Check divergence: |z|² > 4
            if (zr2 + zi2 > 4.0) {
                break;
            }
            
            // z_{n+1} = z_n² + C
            zi = 2.0 * zr * zi + ci;
            zr = zr2 - zi2 + cr;
        }
        
        // Set bit if point diverged (not in set)
        if (iter < MAX_ITER) {
            int byte_idx = x / 8;
            int bit_idx = 7 - (x % 8);
            row[byte_idx] |= (1 << bit_idx);
        }
    }
}

/*
 * Generate complete Mandelbrot set
 */
void generate_mandelbrot(int size) {
    int bytes_per_row = (size + 7) / 8;
    
    // Write PBM header
    printf("P4\n%d %d\n", size, size);
    fflush(stdout);
    
    // Allocate buffer for parallel processing
    uint8_t *buffer = (uint8_t *)malloc(bytes_per_row * size);
    if (!buffer) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    // Process rows in parallel using OpenMP
    #pragma omp parallel for schedule(dynamic, 16)
    for (int y = 0; y < size; y++) {
        calculate_row(buffer + y * bytes_per_row, size, y, size);
    }
    
    // Write all data at once for performance
    size_t total_bytes = (size_t)bytes_per_row * size;
    size_t written = fwrite(buffer, 1, total_bytes, stdout);
    
    if (written != total_bytes) {
        fprintf(stderr, "Error: Write failed\n");
        exit(1);
    }
    
    fflush(stdout);
    free(buffer);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        fprintf(stderr, "Example: %s 16000\n", argv[0]);
        return 1;
    }
    
    int size = atoi(argv[1]);
    if (size <= 0 || size > 100000) {
        fprintf(stderr, "Error: Invalid size (must be 1-100000)\n");
        return 1;
    }
    
    generate_mandelbrot(size);
    
    return 0;
}