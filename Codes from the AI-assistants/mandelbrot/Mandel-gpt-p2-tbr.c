// mandelbrot_pbm.c
// Build: gcc -O2 -march=native -pipe -std=c11 mandelbrot_pbm.c -o mandelbrot
// Run:   ./mandelbrot 4000 100 > out.pbm

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

static int parse_int(const char *s, const char *name) {
    char *end = NULL;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v <= 0 || v > 200000) {
        fprintf(stderr, "Invalid %s: %s\n", name, s);
        exit(1);
    }
    return (int)v;
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s N [max_iter]\n", argv[0]);
        return 1;
    }

    const int N = parse_int(argv[1], "N");
    const int max_iter = (argc == 3) ? parse_int(argv[2], "max_iter") : 100;

    // PBM P4 header
    // (Binary bitmap, width height)
    printf("P4\n%d %d\n", N, N);

    // Viewport in complex plane
    const double x_min = -2.0, x_span = 3.0;   // [-2.0, 1.0]
    const double y_min = -1.5, y_span = 3.0;   // [-1.5, 1.5]
    const double invN = 1.0 / (double)N;

    for (int y = 0; y < N; y++) {
        const double ci = y_min + (double)y * (y_span * invN);

        unsigned char byte = 0;
        int bitcount = 0;

        for (int x = 0; x < N; x++) {
            const double cr = x_min + (double)x * (x_span * invN);

            double zr = 0.0, zi = 0.0;
            int inside = 1;

            for (int i = 0; i < max_iter; i++) {
                const double zr2 = zr * zr;
                const double zi2 = zi * zi;

                if (zr2 + zi2 > 4.0) { // escapes
                    inside = 0;
                    break;
                }

                // z = z^2 + c
                const double two_zr_zi = 2.0 * zr * zi;
                zi = two_zr_zi + ci;
                zr = (zr2 - zi2) + cr;
            }

            // Pack bit (MSB first). Convention: 1 = inside set (black).
            byte = (unsigned char)((byte << 1) | (inside ? 1 : 0));
            bitcount++;

            if (bitcount == 8) {
                putchar(byte);
                byte = 0;
                bitcount = 0;
            }
        }

        // If N not multiple of 8, pad remaining bits on the right (LSB side)
        if (bitcount != 0) {
            byte = (unsigned char)(byte << (8 - bitcount));
            putchar(byte);
        }
    }

    return 0;
}
