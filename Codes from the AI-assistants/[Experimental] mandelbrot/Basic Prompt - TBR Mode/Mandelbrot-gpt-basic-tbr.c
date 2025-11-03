#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Usage:
   gcc -O3 -std=c11 -o mandelbrot_pbm mandelbrot_pbm.c
   ./mandelbrot_pbm out.pbm N max_iter xmin xmax ymin ymax
   Example:
   ./mandelbrot_pbm mandelbrot.pbm 1024 1000 -2.0 1.0 -1.5 1.5
*/

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s out.pbm N max_iter [xmin xmax ymin ymax]\n", argv[0]);
        return 1;
    }
    const char *outname = argv[1];
    int N = atoi(argv[2]);
    int max_iter = atoi(argv[3]);

    double xmin = -2.0, xmax = 1.0, ymin = -1.5, ymax = 1.5;
    if (argc >= 8) {
        xmin = atof(argv[4]);
        xmax = atof(argv[5]);
        ymin = atof(argv[6]);
        ymax = atof(argv[7]);
    }

    FILE *f = fopen(outname, "wb");
    if (!f) { perror("fopen"); return 2; }

    // PBM binary header (P4)
    fprintf(f, "P4\n%d %d\n", N, N);

    int bytes_per_row = (N + 7) / 8;
    unsigned char *rowbuf = malloc(bytes_per_row);
    if (!rowbuf) { perror("malloc"); fclose(f); return 3; }

    for (int py = 0; py < N; ++py) {
        // prepare empty buffer
        for (int b = 0; b < bytes_per_row; ++b) rowbuf[b] = 0;

        double ci = ymin + (double)py * (ymax - ymin) / (N - 1);
        for (int px = 0; px < N; ++px) {
            double cr = xmin + (double)px * (xmax - xmin) / (N - 1);

            double zr = 0.0, zi = 0.0;
            int iter = 0;
            while (iter < max_iter) {
                double zr2 = zr*zr;
                double zi2 = zi*zi;
                if (zr2 + zi2 > 4.0) break;
                double tmp = zr2 - zi2 + cr;
                zi = 2.0*zr*zi + ci;
                zr = tmp;
                ++iter;
            }

            int bit = (iter >= max_iter) ? 1 : 0; // 1 = black = in set
            if (bit) {
                int byte_idx = px / 8;
                int bit_idx = 7 - (px % 8); // PBM: MSB first
                rowbuf[byte_idx] |= (1 << bit_idx);
            }
        }
        // write row
        fwrite(rowbuf, 1, bytes_per_row, f);
    }

    free(rowbuf);
    fclose(f);
    return 0;
}
