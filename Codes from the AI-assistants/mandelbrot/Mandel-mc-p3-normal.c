#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s N\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "N must be positive\n");
        return 1;
    }

    const int max_iter = 50;  // adjust for quality vs speed

    // PBM binary header
    printf("P4\n%d %d\n", N, N);

    for (int py = 0; py < N; ++py) {
        unsigned char byte = 0;
        int bit_count = 0;

        // Map y to imaginary part
        double ci = -1.0 + 2.0 * (double)py / (double)N;

        for (int px = 0; px < N; ++px) {
            // Map x to real part
            double cr = -1.5 + 2.0 * (double)px / (double)N;

            double zr = 0.0, zi = 0.0;
            int iter = 0;

            while (iter < max_iter) {
                double zr2 = zr * zr;
                double zi2 = zi * zi;

                if (zr2 + zi2 > 4.0) {
                    break;  // escaped
                }

                double new_zr = zr2 - zi2 + cr;
                double new_zi = 2.0 * zr * zi + ci;

                zr = new_zr;
                zi = new_zi;
                ++iter;
            }

            // Inside set if did not escape
            int inside = (iter == max_iter);

            // PBM: 1 = black (inside), 0 = white (outside)
            byte <<= 1;
            if (inside) {
                byte |= 1;
            }
            bit_count++;

            // When we have 8 bits, write the byte
            if (bit_count == 8) {
                putchar(byte);
                byte = 0;
                bit_count = 0;
            }
        }

        // If row width is not multiple of 8, pad remaining bits with 0
        if (bit_count != 0) {
            byte <<= (8 - bit_count);
            putchar(byte);
        }
    }

    return 0;
}
