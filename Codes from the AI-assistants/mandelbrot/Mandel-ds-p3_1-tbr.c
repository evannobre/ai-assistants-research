#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s N > out.pbm\n", argv[0]); return 1; }
    int N = atoi(argv[1]);
    const int max_iter = 50;
    const double xmin = -1.5, xmax = 0.5;
    const double ymin = -1.0, ymax = 1.0;
    printf("P4\n%d %d\n", N, N);

    for (int j = 0; j < N; ++j) {
        double y = ymin + (ymax - ymin) * j / (N - 1);
        unsigned char byte = 0;
        int bit = 0;
        for (int i = 0; i < N; ++i) {
            double x = xmin + (xmax - xmin) * i / (N - 1);
            double zr = 0.0, zi = 0.0;
            int iter = 0;
            while (iter < max_iter) {
                double zr2 = zr*zr, zi2 = zi*zi;
                if (zr2 + zi2 > 4.0) break;
                double tmp = zr2 - zi2 + x;
                zi = 2.0*zr*zi + y;
                zr = tmp;
                ++iter;
            }
            int inside = (iter == max_iter);
            byte = (byte << 1) | (inside ? 1 : 0);
            ++bit;
            if (bit == 8) { putchar(byte); byte = 0; bit = 0; }
        }
        if (bit) { byte <<= (8 - bit); putchar(byte); }
    }
    return 0;
}
