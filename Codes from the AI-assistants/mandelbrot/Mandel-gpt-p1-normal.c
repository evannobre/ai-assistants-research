// mandelbrot_pbm.c
// Outputs an N-by-N Mandelbrot image in PBM binary (P4) format to stdout.
// Usage: ./mandelbrot_pbm N max_iter
// Example: ./mandelbrot_pbm 2000 1000 > out.pbm

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

static long parse_long(const char *s, const char *name) {
    errno = 0;
    char *end = NULL;
    long v = strtol(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0') {
        fprintf(stderr, "Invalid %s: '%s'\n", name, s);
        exit(2);
    }
    return v;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s N max_iter > out.pbm\n", argv[0]);
        return 2;
    }

    const long N = parse_long(argv[1], "N");
    const long max_iter = parse_long(argv[2], "max_iter");

    if (N <= 0 || N > 200000) { // sanity guard
        fprintf(stderr, "N out of range: %ld\n", N);
        return 2;
    }
    if (max_iter <= 0 || max_iter > 100000000) { // sanity guard
        fprintf(stderr, "max_iter out of range: %ld\n", max_iter);
        return 2;
    }

    // Typical Mandelbrot view window.
    // Keep it square (N x N), so aspect ratio is 1:1.
    const double minRe = -2.0;
    const double maxRe =  1.0;
    const double minIm = -1.5;
    const double maxIm =  1.5;

    const double reScale = (maxRe - minRe) / (double)(N - 1);
    const double imScale = (maxIm - minIm) / (double)(N - 1);

    // PBM header (binary P4)
    // 1-bit: 1 = black, 0 = white
    printf("P4\n%ld %ld\n", N, N);

    const long row_bytes = (N + 7) / 8;

    // Stream row-by-row, no need to store the whole image.
    for (long y = 0; y < N; y++) {
        double Ci = maxIm - (double)y * imScale; // top row is +imag

        for (long bx = 0; bx < row_bytes; bx++) {
            uint8_t byte = 0;

            // Each output byte contains 8 pixels, MSB first.
            for (int bit = 0; bit < 8; bit++) {
                long x = bx * 8 + bit;

                // If we're beyond width (only possible in last byte), pad with 0 bits.
                byte <<= 1;
                if (x >= N) continue;

                double Cr = minRe + (double)x * reScale;

                // z0 = 0
                double zr = 0.0, zi = 0.0;

                // Iterate z_{n+1} = z_n^2 + C
                long iter = 0;
                for (; iter < max_iter; iter++) {
                    // zr^2 + zi^2
                    double zr2 = zr * zr;
                    double zi2 = zi * zi;

                    // Escape radius 2 => compare squared radius to 4
                    if (zr2 + zi2 > 4.0) break;

                    // z^2 + C:
                    // (zr + i zi)^2 = (zr^2 - zi^2) + i(2*zr*zi)
                    double new_zi = 2.0 * zr * zi + Ci;
                    double new_zr = (zr2 - zi2) + Cr;
                    zr = new_zr;
                    zi = new_zi;
                }

                // In set if it did NOT escape within max_iter.
                // PBM: 1 = black (inside), 0 = white (outside)
                if (iter == max_iter) {
                    byte |= 1;
                }
            }

            // Write one byte
            putchar((int)byte);
        }
    }

    return 0;
}
