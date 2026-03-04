/**
 * mandelbrot.c
 * * Generates a Mandelbrot set visualization using the Escape Time algorithm.
 * Outputs a PGM (Portable Gray Map) binary file.
 * * Memory Complexity: O(N) - Row-by-row buffering to respect 8GB RAM.
 * Time Complexity: O(N^2 * MAX_ITER).
 */

#include <stdio.h>
#include <stdlib.h>
#include <complex.h> // Native complex number support
#include <stdint.h>

// Configuration
#define MAX_ITER 1000      // Precision of the set borders
#define ESCAPE_RADIUS 2.0  // Mathematically sufficient bound
#define CENTER_REAL -0.75  // Center of the view
#define CENTER_IMAG 0.0
#define VIEW_WIDTH 2.5     // Zoom level width

// Standard Mandelbrot bounds typically fit within -2.0 to 1.0 Real

void generate_mandelbrot(int n, const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Error opening output file");
        exit(EXIT_FAILURE);
    }

    // 1. Write PGM Header (P5 = Binary Grayscale)
    // Format: P5 <width> <height> <max_val>
    fprintf(fp, "P5\n%d %d\n255\n", n, n);

    // 2. Setup scaling factors
    // We map 0..N to (Center - Width/2) .. (Center + Width/2)
    double start_real = CENTER_REAL - (VIEW_WIDTH / 2.0);
    double start_imag = CENTER_IMAG - (VIEW_WIDTH / 2.0); // Square aspect ratio
    
    double step = VIEW_WIDTH / (double)n;

    // Allocate a single row buffer to minimize RAM usage
    // Using uint8_t for 0-255 grayscale values
    uint8_t *row_buffer = (uint8_t *)malloc(n * sizeof(uint8_t));
    if (!row_buffer) {
        fprintf(stderr, "Memory allocation failed for row buffer.\n");
        fclose(fp);
        exit(EXIT_FAILURE);
    }

    printf("Computing %dx%d Mandelbrot set to '%s'...\n", n, n, filename);

    // 3. Iterate rows (Imaginary axis)
    for (int y = 0; y < n; y++) {
        double imag = start_imag + (y * step);

        // Iterate columns (Real axis)
        for (int x = 0; x < n; x++) {
            double real = start_real + (x * step);
            
            // Mathematical definition: z_0 = 0, C = pixel_coord
            double complex c = real + imag * I;
            double complex z = 0 + 0 * I;
            
            int iter = 0;
            
            // Optimization: checking real^2 + imag^2 is faster than cabs(z) 
            // because cabs involves a square root.
            // We loop until escape or max iterations.
            while (iter < MAX_ITER && (creal(z)*creal(z) + cimag(z)*cimag(z)) < (ESCAPE_RADIUS * ESCAPE_RADIUS)) {
                z = z * z + c;
                iter++;
            }

            // Map iteration count to grayscale (0 = black/in-set, 255 = white/fast-escape)
            // We scale the iteration count to 0-255 for the image format.
            // Points inside the set (iter == MAX_ITER) are usually colored black (0).
            uint8_t pixel_value;
            if (iter == MAX_ITER) {
                pixel_value = 0; 
            } else {
                // Simple linear scaling for outer aura
                pixel_value = (uint8_t)(iter % 256);
            }
            
            row_buffer[x] = pixel_value;
        }

        // Write the completed row to disk immediately
        fwrite(row_buffer, sizeof(uint8_t), n, fp);
        
        // Optional: Progress indicator for large N
        if (y % 1000 == 0) {
            printf("Processed row %d/%d\r", y, n);
            fflush(stdout);
        }
    }

    printf("\nDone. Saved to %s\n", filename);

    // Cleanup
    free(row_buffer);
    fclose(fp);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <N> <output_filename.pgm>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int n = atoi(argv[1]);
    if (n <= 0) {
        fprintf(stderr, "N must be a positive integer.\n");
        return EXIT_FAILURE;
    }

    generate_mandelbrot(n, argv[2]);

    return EXIT_SUCCESS;
}