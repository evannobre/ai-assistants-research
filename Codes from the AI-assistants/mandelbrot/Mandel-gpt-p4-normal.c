// mandelbrot_pbm.c
// Build: gcc -O2 -march=native -pipe -std=c11 mandelbrot_pbm.c -o mandelbrot
// Run:   ./mandelbrot 16000 > mandel.pbm

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef MAX_ITER
#define MAX_ITER 50
#endif

static void die(const char *msg) {
    perror(msg);
    exit(1);
}

static int parse_int(const char *s) {
    char *end = NULL;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v <= 0 || v > 200000) {
        fprintf(stderr, "Invalid N: %s\n", s);
        exit(1);
    }
    return (int)v;
}

int main(int argc, char **argv) {
    int N = 200; // default
    if (argc > 1) N = parse_int(argv[1]);

    // PBM P4 header
    // P4 = binary (packed bits), 1-bit per pixel
    if (printf("P4\n%d %d\n", N, N) < 0) die("printf");

    // Bytes per row (packed, 8 pixels per byte)
    const int row_bytes = (N + 7) / 8;
    uint8_t *row = (uint8_t *)malloc((size_t)row_bytes);
    if (!row) {
        fprintf(stderr, "Out of memory allocating %d bytes\n", row_bytes);
        return 1;
    }

    // Map pixel grid to complex plane:
    // real in [-1.5, 0.5] (width 2.0)
    // imag in [-1.0, 1.0] (height 2.0)
    const double invN = 1.0 / (double)N;
    const double scale = 2.0 * invN;

    for (int y = 0; y < N; y++) {
        // ci ranges from -1.0 to +1.0
        const double ci = (double)y * scale - 1.0;

        // Clear row buffer
        for (int i = 0; i < row_bytes; i++) row[i] = 0;

        int byte_index = 0;
        uint8_t bits = 0;
        int bit_count = 0;

        for (int x = 0; x < N; x++) {
            // cr ranges from -1.5 to +0.5
            const double cr = (double)x * scale - 1.5;

            // Iterate z_{n+1} = z_n^2 + c, starting from z0 = 0
            double zr = 0.0, zi = 0.0;
            int inside = 1; // assume inside unless it escapes

            for (int i = 0; i < MAX_ITER; i++) {
                const double zr2 = zr * zr;
                const double zi2 = zi * zi;
                if (zr2 + zi2 > 4.0) { // escaped
                    inside = 0;
                    break;
                }
                const double zri = zr * zi;
                zi = 2.0 * zri + ci;
                zr = zr2 - zi2 + cr;
            }

            // Pack bit: PBM convention: 1 = black, 0 = white
            bits = (uint8_t)((bits << 1) | (inside ? 1u : 0u));
            bit_count++;

            if (bit_count == 8) {
                row[byte_index++] = bits;
                bits = 0;
                bit_count = 0;
            }
        }

        // If N not multiple of 8, pad the last byte by shifting left
        if (bit_count != 0) {
            bits <<= (8 - bit_count);
            row[byte_index++] = bits;
        }

        // Write the packed row bytes to stdout
        ssize_t want = row_bytes;
        uint8_t *p = row;
        while (want > 0) {
            ssize_t n = write(STDOUT_FILENO, p, (size_t)want);
            if (n < 0) die("write");
            p += n;
            want -= n;
        }
    }

    free(row);
    return 0;
}
