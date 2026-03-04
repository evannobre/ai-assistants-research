// mandelbrot_pbm.c
// Build: gcc -O3 -march=native -pipe -std=c11 -Wall -Wextra mandelbrot_pbm.c -o mandelbrot
// Run:   ./mandelbrot 16000 > out.pbm

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

#ifndef MAX_ITER
#define MAX_ITER 50
#endif

static void die(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s N > out.pbm\n", argv[0]);
        return 2;
    }

    errno = 0;
    char *end = NULL;
    long n_long = strtol(argv[1], &end, 10);
    if (errno != 0 || end == argv[1] || *end != '\0' || n_long <= 0 || n_long > 200000) {
        fprintf(stderr, "Invalid N: %s\n", argv[1]);
        return 2;
    }
    const int N = (int)n_long;

    // Make stdout fully buffered for speed (fits Ubuntu constraints easily)
    static unsigned char outbuf[1 << 20]; // 1 MiB
    if (setvbuf(stdout, (char*)outbuf, _IOFBF, sizeof(outbuf)) != 0) {
        // Not fatal; continue.
    }

    // PBM header
    // P4: binary bitmap; 1=black, 0=white
    if (printf("P4\n%d %d\n", N, N) < 0) die("printf");

    const int row_bytes = (N + 7) / 8;
    uint8_t *row = (uint8_t*)malloc((size_t)row_bytes);
    if (!row) die("malloc row");

    // Optional: precompute coordinates (small memory, reduces per-pixel FP ops)
    double *cr = (double*)malloc((size_t)N * sizeof(double));
    double *ci = (double*)malloc((size_t)N * sizeof(double));
    if (!cr || !ci) die("malloc coords");

    const double invN = 1.0 / (double)N;
    for (int x = 0; x < N; x++) {
        cr[x] = -1.5 + (2.0 * (double)x) * invN;
    }
    for (int y = 0; y < N; y++) {
        ci[y] = -1.0 + (2.0 * (double)y) * invN;
    }

    for (int y = 0; y < N; y++) {
        // Clear row bytes
        for (int i = 0; i < row_bytes; i++) row[i] = 0;

        const double c_im = ci[y];
        for (int x = 0; x < N; x++) {
            const double c_re = cr[x];

            double zr = 0.0, zi = 0.0;
            int iter = 0;

            // Escape-time iteration
            while (iter < MAX_ITER) {
                // z_{n+1} = z_n^2 + c
                // (zr + i*zi)^2 = (zr^2 - zi^2) + i*(2*zr*zi)
                const double zr2 = zr * zr;
                const double zi2 = zi * zi;
                if (zr2 + zi2 > 4.0) break;

                const double new_zr = zr2 - zi2 + c_re;
                const double new_zi = (2.0 * zr * zi) + c_im;
                zr = new_zr;
                zi = new_zi;

                iter++;
            }

            // Inside set if it didn't escape within MAX_ITER
            if (iter == MAX_ITER) {
                // Pack bit: MSB is leftmost pixel in the byte
                row[x >> 3] |= (uint8_t)(0x80u >> (x & 7));
            }
        }

        // Write row as bytes
        if (fwrite(row, 1, (size_t)row_bytes, stdout) != (size_t)row_bytes) die("fwrite");
    }

    free(ci);
    free(cr);
    free(row);

    // Flush explicitly (helps detect errors)
    if (fflush(stdout) != 0) die("fflush");
    return 0;
}
