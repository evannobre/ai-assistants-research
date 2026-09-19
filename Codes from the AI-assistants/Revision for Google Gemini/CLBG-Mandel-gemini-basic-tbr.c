#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>

// Standard maximum iterations for the benchmark
#define MAX_ITER 50

int main(int argc, char **argv) {
    // 1. Parse command line argument (default to 16000 if none provided)
    int N = (argc > 1) ? atoi(argv[1]) : 16000;
    if (N <= 0) {
        fprintf(stderr, "N must be a positive integer.\n");
        return 1;
    }

    // 2. Output the standard Portable Bitmap Format (P4 binary) header
    // P4 implies 1-bit per pixel (black and white), packed 8 pixels per byte.
    printf("P4\n%d %d\n", N, N);

    // 3. Allocate memory for the bitmap
    // Each row packs 8 pixels into 1 byte. We use ceil division.
    size_t bytes_per_row = (N + 7) / 8;
    uint8_t *bitmap = (uint8_t *)malloc(bytes_per_row * N);
    if (!bitmap) {
        fprintf(stderr, "Memory allocation failed.\n");
        return 1;
    }

    // 4. Parallelize the Y-axis loop using OpenMP native pragma
    #pragma omp parallel for schedule(dynamic, 1)
    for (int y = 0; y < N; y++) {
        // Map pixel y to the imaginary plane: [-1.0, 1.0] (from -i to +i)
        double cy = y * 2.0 / N - 1.0;
        
        // Pointer to the start of the current row in the bitmap
        uint8_t *row = bitmap + (y * bytes_per_row);

        for (int x = 0; x < N; x += 8) {
            uint8_t byte = 0;
            
            // Pack 8 pixels into a single byte
            for (int bit = 0; bit < 8 && (x + bit) < N; bit++) {
                // Map pixel x to the real plane: [-1.5, 0.5]
                double cx = (x + bit) * 2.0 / N - 1.5;
                
                double zx = 0.0;
                double zy = 0.0;
                double zx2 = 0.0;
                double zy2 = 0.0;
                
                int i;
                for (i = 0; i < MAX_ITER; i++) {
                    // Check if magnitude exceeds 2 (zx^2 + zy^2 > 4)
                    if (zx2 + zy2 > 4.0) break;
                    
                    // z_{n+1} = z_n^2 + C
                    zy = 2.0 * zx * zy + cy;
                    zx = zx2 - zy2 + cx;
                    
                    // Precalculate squares for the next iteration
                    zx2 = zx * zx;
                    zy2 = zy * zy;
                }
                
                // If we reached MAX_ITER, the point is inside the Mandelbrot set
                if (i == MAX_ITER) {
                    // Set the corresponding bit in the byte (MSB first)
                    byte |= (1 << (7 - bit));
                }
            }
            // Store the packed byte
            row[x / 8] = byte;
        }
    }

    // 5. Write the entire bitmap byte-by-byte to stdout
    fwrite(bitmap, 1, bytes_per_row * N, stdout);
    
    // Clean up
    free(bitmap);
    return 0;
}