// mandelbrot_pbm.c
// Build: gcc -O2 -std=c17 -Wall -Wextra -pedantic mandelbrot_pbm.c -o mandelbrot
// Run:   ./mandelbrot 16000 > mandel.pbm

#include <stdio.h>
#include <stdlib.h>

static int mandel_inside(double cr, double ci, int max_iter) {
    double zr = 0.0, zi = 0.0;

    for (int i = 0; i < max_iter; i++) {
        double zr2 = zr * zr;
        double zi2 = zi * zi;

        if (zr2 + zi2 > 4.0) return 0; // escaped => outside

        double new_zi = 2.0 * zr * zi + ci;
        double new_zr = zr2 - zi2 + cr;

        zr = new_zr;
        zi = new_zi;
    }
    return 1; // did not escape => inside
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s N\n", argv[0]);
        return 1;
    }

    char *end = NULL;
    long n_long = strtol(argv[1], &end, 10);
    if (!end || *end != '\0' || n_long <= 0 || n_long > 200000) {
        fprintf(stderr, "invalid N: %s\n", argv[1]);
        return 1;
    }
    const int N = (int)n_long;

    // Typical Benchmarks Game uses 50 iterations for Mandelbrot PBM.
    const int MAX_ITER = 50;

    // Buffer stdout to reduce syscall overhead when writing many bytes.
    setvbuf(stdout, NULL, _IOFBF, 1 << 20);

    // PBM binary header (P4)
    printf("P4\n%d %d\n", N, N);

    // Precompute real coordinates for each column (cheap O(N) memory).
    double *xcoords = (double *)malloc((size_t)N * sizeof(double));
    if (!xcoords) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    const double invN = 1.0 / (double)N;
    for (int x = 0; x < N; x++) {
        xcoords[x] = (2.0 * (double)x) * invN - 1.5; // [-1.5, 0.5]
    }

    const int row_bytes = (N + 7) / 8;

    for (int y = 0; y < N; y++) {
        const double ci = (2.0 * (double)y) * invN - 1.0; // [-1, 1]
        unsigned char out = 0;
        int bit = 0;

        for (int x = 0; x < N; x++) {
            int inside = mandel_inside(xcoords[x], ci, MAX_ITER);

            out = (unsigned char)((out << 1) | (inside ? 1u : 0u));
            bit++;

            if (bit == 8) {
                fputc(out, stdout);
                out = 0;
                bit = 0;
            }
        }

        // If N not divisible by 8, pad remaining bits with zeros on the right.
        if (bit != 0) {
            out = (unsigned char)(out << (8 - bit));
            fputc(out, stdout);
        }

        // (Optional) sanity: ensure row length; not necessary, but clarifies intent.
        (void)row_bytes;
    }

    free(xcoords);
    return 0;
}
