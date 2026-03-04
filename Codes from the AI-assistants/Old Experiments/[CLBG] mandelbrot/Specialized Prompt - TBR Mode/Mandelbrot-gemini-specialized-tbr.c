/**
 * @file mandelbrot.c
 * @brief A high-performance, parallel Mandelbrot set generator.
 *
 * This program generates a square bitmap image of the Mandelbrot set
 * for the complex region [-1.5-i, 0.5+i]. It uses OpenMP to parallelize
 * the computation for significant speed improvements on multi-core systems.
 *
 * The output is in the Portable Bitmap (PBM) P4 raw format, which is
 * written to standard output.
 *
 * Compilation:
 * gcc -o mandelbrot -O3 -fopenmp mandelbrot.c
 *
 * Usage:
 * ./mandelbrot [N] > mandelbrot.pbm
 * (e.g., ./mandelbrot 16000 > mandelbrot_16k.pbm)
 *
 * Where [N] is the width and height of the desired square image.
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h> // Required for OpenMP parallelization

int main(int argc, char *argv[]) {
    // --- 1. Process Command-Line Arguments ---
    if (argc < 2) {
        fprintf(stderr, "Error: Missing command-line argument for image size.\n");
        fprintf(stderr, "Usage: %s <N>\n", argv[0]);
        return 1;
    }
    const int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "Error: N must be a positive integer.\n");
        return 1;
    }

    // --- 2. Setup Bitmap Buffer and Constants ---
    // Calculate the number of bytes needed for each row.
    // Each pixel is 1 bit. We round up to the nearest full byte.
    const int row_size_bytes = (N + 7) / 8;
    const size_t bitmap_size = (size_t)N * row_size_bytes;

    // Allocate a single contiguous block of memory for the entire bitmap.
    // This allows parallel threads to write to different rows without conflict.
    unsigned char *bitmap = (unsigned char *)malloc(bitmap_size);
    if (!bitmap) {
        fprintf(stderr, "Error: Failed to allocate memory for the bitmap.\n");
        return 1;
    }

    const int max_iter = 50;      // Iteration limit to determine if a point is in the set.
    const double limit_sq = 4.0;  // Escape radius squared (more efficient than sqrt).

    // --- 3. Parallel Computation of the Mandelbrot Set ---
    // The #pragma directive tells OpenMP to parallelize this for-loop.
    // Each thread will be assigned a set of rows (py) to compute.
    // 'schedule(guided)' is used for dynamic load balancing, as some rows
    // may be more computationally expensive than others.
    #pragma omp parallel for schedule(guided)
    for (int py = 0; py < N; py++) {
        // Get a pointer to the beginning of the current row's data in the bitmap buffer.
        unsigned char *row_ptr = bitmap + (size_t)py * row_size_bytes;
        
        // Initialize the row data to all zeros (all pixels white).
        for (int i = 0; i < row_size_bytes; i++) {
            row_ptr[i] = 0;
        }

        // Iterate through each pixel (px) in the current row.
        for (int px = 0; px < N; px++) {
            // Map the pixel coordinates (px, py) to a complex number C = cr + ci*i.
            const double cr = -1.5 + (double)px * 2.0 / (double)N;
            const double ci = -1.0 + (double)py * 2.0 / (double)N;

            double zr = 0.0, zi = 0.0;
            int iter = 0;

            // Apply the Mandelbrot recurrence: z(n+1) = z(n)^2 + C
            while (iter < max_iter) {
                const double zr_sq = zr * zr;
                const double zi_sq = zi * zi;

                // Check if the point has "escaped" the radius of 2.
                if (zr_sq + zi_sq > limit_sq) {
                    break;
                }

                // Calculate the next z value.
                const double zr_new = zr_sq - zi_sq + cr;
                zi = 2.0 * zr * zi + ci;
                zr = zr_new;
                iter++;
            }

            // If 'iter' reached 'max_iter', the point is considered inside the set.
            // We set the corresponding bit in our bitmap buffer to 1 (black).
            if (iter == max_iter) {
                const int byte_index = px / 8;
                // PBM format specifies MSB first, so we calculate the bit position from the left.
                const int bit_index = 7 - (px % 8);
                row_ptr[byte_index] |= (1 << bit_index);
            }
        }
    }

    // --- 4. Write Output ---
    // This part is executed by a single thread after all parallel computations are complete.
    // Write the PBM header to standard output.
    printf("P4\n%d %d\n", N, N);

    // Write the entire bitmap buffer to standard output in one operation.
    fwrite(bitmap, 1, bitmap_size, stdout);

    // --- 5. Cleanup ---
    free(bitmap);
    return 0;
}
