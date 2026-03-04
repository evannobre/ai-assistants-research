// mandelbrot.c
// Compile: gcc -std=c99 -O3 mandelbrot.c -o mandelbrot -lm

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {
    if (argc != 8) {
        fprintf(stderr, "Usage: %s N xmin xmax ymin ymax maxiter out.pgm\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    double xmin = atof(argv[2]);
    double xmax = atof(argv[3]);
    double ymin = atof(argv[4]);
    double ymax = atof(argv[5]);
    int maxiter = atoi(argv[6]);
    const char *outname = argv[7];

    if (N <= 0 || maxiter <= 0) {
        fprintf(stderr, "N and maxiter must be positive.\n");
        return 1;
    }

    FILE *f = fopen(outname, "wb");
    if (!f) {
        perror("fopen");
        return 1;
    }

    // Write PGM header (P5 = binary grayscale)
    fprintf(f, "P5\n%d %d\n255\n", N, N);

    unsigned char *row = (unsigned char*)malloc(N);
    if (!row) {
        perror("malloc");
        fclose(f);
        return 1;
    }

    // Precompute increments
    double dx = (xmax - xmin) / (N - 1);
    double dy = (ymax - ymin) / (N - 1);

    for (int j = 0; j < N; ++j) {
        double y = ymax - j * dy; // top to bottom
        for (int i = 0; i < N; ++i) {
            double x = xmin + i * dx;
            // iterate z_{n+1} = z_n^2 + C, with z = a + ib, C = x + i y
            double a = 0.0;
            double b = 0.0;
            int iter = 0;
            double a2 = 0.0;
            double b2 = 0.0;
            // bailout radius squared = 4
            while (iter < maxiter) {
                // (a + ib)^2 = (a^2 - b^2) + i(2ab)
                b = 2.0 * a * b + y;
                a = a2 - b2 + x;
                a2 = a * a;
                b2 = b * b;
                if (a2 + b2 > 4.0) break;
                ++iter;
            }

            unsigned char color;
            if (iter >= maxiter) {
                color = 0; // inside set -> black
            } else {
                // simple linear mapping to 1..255 (avoid 0 to keep inside black)
                double t = (double)iter / (double)maxiter;
                // optional gamma-like scaling for better contrast
                t = sqrt(t);
                int v = (int)(1 + t * 254.0);
                if (v < 1) v = 1;
                if (v > 255) v = 255;
                color = (unsigned char)v;
            }
            row[i] = color;
        }
        // write row
        if (fwrite(row, 1, N, f) != (size_t)N) {
            perror("fwrite");
            free(row);
            fclose(f);
            return 1;
        }
    }

    free(row);
    fclose(f);
    return 0;
}
