// mandelbrot_pbm.c
// Build: gcc -O2 -std=c11 -Wall -Wextra -pedantic mandelbrot_pbm.c -o mandelbrot -lm
// Run:   ./mandelbrot 2000 1000 > out.pbm
//
// Output is PBM binary (P4): view with ImageMagick (display out.pbm) or convert to PNG.

#include <errno.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static void die(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

static long parse_long(const char *s, const char *name) {
    errno = 0;
    char *end = NULL;
    long v = strtol(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v <= 0) {
        fprintf(stderr, "Invalid %s: %s\n", name, s);
        exit(EXIT_FAILURE);
    }
    return v;
}

// Escape-time test: returns 1 if point is in the set (didn't escape), else 0.
static inline int mandelbrot_member(double cr, double ci, int max_iters) {
    double zr = 0.0, zi = 0.0;
    // Iterate: z = z^2 + c
    for (int i = 0; i < max_iters; i++) {
        // z^2 = (zr + i*zi)^2 = (zr^2 - zi^2) + i*(2*zr*zi)
        double zr2 = zr * zr;
        double zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) return 0; // escaped
        double new_zr = zr2 - zi2 + cr;
        double new_zi = 2.0 * zr * zi + ci;
        zr = new_zr;
        zi = new_zi;
    }
    return 1; // likely in set
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s N [MAX_ITERS]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const long N = parse_long(argv[1], "N");
    const int max_iters = (argc == 3) ? (int)parse_long(argv[2], "MAX_ITERS") : 1000;

    // Complex plane window (common default)
    const double re_min = -2.0, re_max = 1.0;
    const double im_min = -1.5, im_max = 1.5;

    const long row_bytes = (N + 7) / 8;

    // PBM header
    if (printf("P4\n%ld %ld\n", N, N) < 0) die("write header");

    // Render row by row, packing 8 pixels per byte (MSB first)
    for (long y = 0; y < N; y++) {
        // Map pixel center to imaginary coordinate
        double ci = im_max - (im_max - im_min) * ((double)y + 0.5) / (double)N;

        for (long xb = 0; xb < row_bytes; xb++) {
            uint8_t byte = 0;

            for (int bit = 0; bit < 8; bit++) {
                long x = xb * 8 + bit;
                byte <<= 1;

                if (x < N) {
                    double cr = re_min + (re_max - re_min) * ((double)x + 0.5) / (double)N;
                    int in_set = mandelbrot_member(cr, ci, max_iters);
                    // PBM: 1 = black, 0 = white
                    if (in_set) byte |= 1;
                } else {
                    // Pad bits past N with 0 (white)
                }
            }

            if (putchar(byte) == EOF) die("write pixel data");
        }
    }

    if (fflush(stdout) != 0) die("fflush");
    return EXIT_SUCCESS;
}
