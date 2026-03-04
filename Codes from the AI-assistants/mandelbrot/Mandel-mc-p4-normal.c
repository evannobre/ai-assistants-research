#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s N\n", argv[0]);
        return 1;
    }

    char *endptr = NULL;
    long n_long = strtol(argv[1], &endptr, 10);
    if (*endptr != '\0' || n_long <= 0) {
        fprintf(stderr, "Invalid N: %s\n", argv[1]);
        return 1;
    }

    int N = (int)n_long;

    // Mandelbrot parameters
    const int MAX_ITER = 50;  // can be increased if you want more detail
    const double x_min = -1.5;
    const double x_max =  0.5;
    const double y_min = -1.0;
    const double y_max =  1.0;

    const double dx = (x_max - x_min) / (double)N;
    const double dy = (y_max - y_min) / (double)N;

    // PBM (binary) header: P4
    // P4\n<N> <N>\n
    printf("P4\n%d %d\n", N, N);

    for (int y = 0; y < N; ++y) {
        double c_im = y_min + dy * (double)y;

        unsigned char byte = 0;
        int bit_count = 0;

        for (int x = 0; x < N; ++x) {
            double c_re = x_min + dx * (double)x;

            double z_re = 0.0;
            double z_im = 0.0;
            int iter = 0;

            // Quadratic recurrence: z_{n+1} = z_n^2 + C
            while (iter < MAX_ITER) {
                double z_re2 = z_re * z_re;
                double z_im2 = z_im * z_im;

                if (z_re2 + z_im2 > 4.0) {
                    break; // escaped
                }

                double two_re_im = 2.0 * z_re * z_im;
                z_re = z_re2 - z_im2 + c_re;
                z_im = two_re_im + c_im;

                ++iter;
            }

            // Inside set if not escaped
            // PBM: 1 = black, 0 = white (convention)
            unsigned char bit = (iter == MAX_ITER) ? 1 : 0;

            byte = (byte << 1) | bit;
            ++bit_count;

            if (bit_count == 8) {
                putchar(byte);
                byte = 0;
                bit_count = 0;
            }
        }

        // Flush remaining bits in the row (pad with zeros on the right)
        if (bit_count > 0) {
            byte <<= (8 - bit_count);
            putchar(byte);
        }
    }

    return 0;
}
