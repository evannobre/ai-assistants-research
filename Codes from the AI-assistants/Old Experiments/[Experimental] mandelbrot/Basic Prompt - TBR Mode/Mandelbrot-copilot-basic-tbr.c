// mandelbrot.c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s N max_iter [xmin xmax ymin ymax]\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    int max_iter = atoi(argv[2]);
    if (N <= 0 || max_iter <= 0) {
        fprintf(stderr, "N and max_iter must be positive integers\n");
        return 1;
    }

    double xmin = -2.0, xmax = 1.0, ymin = -1.5, ymax = 1.5;
    if (argc >= 7) {
        xmin = atof(argv[3]); xmax = atof(argv[4]);
        ymin = atof(argv[5]); ymax = atof(argv[6]);
    } else {
        // adjust vertical aspect to preserve aspect ratio if N != N (here square)
        double aspect = (double)N / (double)N;
        double cy = 0.0;
        double h = (xmax - xmin) / 3.0;
        ymin = cy - h;
        ymax = cy + h;
    }

    double dx = (xmax - xmin) / (N - 1);
    double dy = (ymax - ymin) / (N - 1);
    double escape_sq = 4.0;

    // PBM header (binary P4)
    printf("P4\n%d %d\n", N, N);
    fflush(stdout);

    int bytes_per_row = (N + 7) / 8;
    unsigned char *row = (unsigned char*)malloc(bytes_per_row);
    if (!row) return 2;

    for (int j = 0; j < N; ++j) {
        double cy = ymax - j * dy; // top to bottom
        for (int b = 0; b < bytes_per_row; ++b) row[b] = 0;
        for (int i = 0; i < N; ++i) {
            double cx = xmin + i * dx;
            double x = 0.0, y = 0.0;
            double x2 = 0.0, y2 = 0.0;
            int iter = 0;
            while (iter < max_iter && (x2 + y2) <= escape_sq) {
                y = 2.0 * x * y + cy;
                x = x2 - y2 + cx;
                x2 = x * x;
                y2 = y * y;
                ++iter;
            }
            int is_member = (iter >= max_iter);
            if (is_member) {
                int byte_index = i >> 3;
                int bit_index = 7 - (i & 7); // MSB is leftmost pixel
                row[byte_index] |= (1u << bit_index);
            }
        }
        // write row
        if (fwrite(row, 1, bytes_per_row, stdout) != (size_t)bytes_per_row) {
            perror("fwrite");
            free(row);
            return 3;
        }
    }

    free(row);
    return 0;
}