// mandelbrot_pbm.c
// Build: gcc -O3 -std=c11 -march=native -pipe -o mandelbrot_pbm mandelbrot_pbm.c
// Run:   ./mandelbrot_pbm 16000 > out.pbm

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static inline int mandelbrot_inside(double cr, double ci, int max_iter) {
    // z = 0
    double zr = 0.0, zi = 0.0;

    // Iterate z_{n+1} = z_n^2 + c
    for (int i = 0; i < max_iter; i++) {
        // z^2 = (zr + i*zi)^2 = (zr^2 - zi^2) + i*(2*zr*zi)
        double zr2 = zr * zr;
        double zi2 = zi * zi;

        if (zr2 + zi2 > 4.0) return 0; // escaped

        double new_zr = zr2 - zi2 + cr;
        double new_zi = (zr + zr) * zi + ci; // 2*zr*zi + ci

        zr = new_zr;
        zi = new_zi;
    }
    return 1; // inside (did not escape within max_iter)
}

int main(int argc, char **argv) {
    int N = 200; // small default; performance tests use 16000
    if (argc > 1) {
        long v = strtol(argv[1], NULL, 10);
        if (v > 0 && v <= 200000) N = (int)v;
    }

    // PBM binary header (P4): "P4\n<width> <height>\n"
    // Output must be byte-by-byte. We'll use putc().
    printf("P4\n%d %d\n", N, N);

    const int max_iter = 50; // typical for benchmarks; keeps work non-trivial

    // Viewport: real in [-1.5, 0.5], imag in [-1.0, 1.0]
    const double real_min = -1.5;
    const double imag_max =  1.0;
    const double scale = 2.0 / (double)N; // both width and height are 2.0

    const int row_bytes = (N + 7) / 8;

    for (int y = 0; y < N; y++) {
        double ci = imag_max - (double)y * scale;

        uint8_t byte = 0;
        int bit_count = 0;

        for (int x = 0; x < N; x++) {
            double cr = real_min + (double)x * scale;

            int inside = mandelbrot_inside(cr, ci, max_iter);

            // PBM: 1-bit pixels; conventionally 1 = black, 0 = white.
            // We'll set bit to 1 if inside.
            byte = (uint8_t)((byte << 1) | (inside ? 1 : 0));
            bit_count++;

            if (bit_count == 8) {
                putc((int)byte, stdout);
                byte = 0;
                bit_count = 0;
            }
        }

        // If N not divisible by 8, pad remaining bits with zeros on the right
        if (bit_count != 0) {
            byte = (uint8_t)(byte << (8 - bit_count));
            putc((int)byte, stdout);
        }

        // Ensure we wrote exactly row_bytes bytes per row (for clarity).
        // The code above already does, but we keep the invariant explicit by structure.
        (void)row_bytes;
    }

    return 0;
}
