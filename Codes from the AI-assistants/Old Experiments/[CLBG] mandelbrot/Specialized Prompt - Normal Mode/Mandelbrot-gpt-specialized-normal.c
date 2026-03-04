#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <N>  (writes PBM P4 to stdout)\n", argv[0]);
        return 1;
    }

    char *endptr = NULL;
    long Nlong = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || Nlong <= 0) {
        fprintf(stderr, "Invalid N: %s\n", argv[1]);
        return 1;
    }
    int N = (int)Nlong;

    const double re_min = -1.5;
    const double re_max =  0.5;
    const double im_min = -1.0;
    const double im_max =  1.0;

    const int MAX_ITER = 50; /* change to higher for more detail, slower */
    const int row_bytes = (N + 7) / 8;
    uint8_t *row = (uint8_t*) malloc((size_t)row_bytes);
    if (!row) {
        fprintf(stderr, "Allocation failed for row buffer (%d bytes)\n", row_bytes);
        return 1;
    }

    /* Print PBM header (P4) */
    /* Note: printing to stdout is fine on Unix (binary output). */
    printf("P4\n%d %d\n", N, N);
    fflush(stdout);

    /* Precompute increments to avoid repeated division inside loops */
    const double re_scale = (re_max - re_min) / (N - 1);
    const double im_scale = (im_max - im_min) / (N - 1);

    for (int y = 0; y < N; ++y) {
        /* clear row buffer */
        for (int i = 0; i < row_bytes; ++i) row[i] = 0;

        double cy = im_max - y * im_scale; /* top row -> largest imaginary */

        for (int x = 0; x < N; ++x) {
            double cx = re_min + x * re_scale;

            double zx = 0.0, zy = 0.0;
            int iter = 0;
            double zx2 = 0.0, zy2 = 0.0;

            while (iter < MAX_ITER) {
                zy = 2.0 * zx * zy + cy;
                zx = zx2 - zy2 + cx;
                zx2 = zx * zx;
                zy2 = zy * zy;
                if (zx2 + zy2 > 4.0) break;
                ++iter;
            }

            /* If the point did NOT escape within MAX_ITER, mark it black (1) */
            if (iter == MAX_ITER) {
                int byte_idx = x >> 3;            /* x / 8 */
                int bit_idx  = x & 7;             /* x % 8 */
                row[byte_idx] |= (uint8_t)(0x80 >> bit_idx); /* MSB-first */
            }
        }

        /* write this row to stdout */
        size_t written = fwrite(row, 1, row_bytes, stdout);
        if (written != (size_t)row_bytes) {
            fprintf(stderr, "Write error\n");
            free(row);
            return 1;
        }
    }

    free(row);
    return 0;
}
