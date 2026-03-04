#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

int main(int argc, char *argv[]) {
    int N = 16000;
    if (argc > 1) {
        N = atoi(argv[1]);
        if (N <= 0) return 1;
    }

    const int max_iter = 50; // you can increase for finer boundary detail

    // PBM header (binary)
    // P4\n<width> <height>\n
    printf("P4\n%d %d\n", N, N);

    // Precompute mapping ranges
    const double re_min = -1.5;
    const double re_max =  0.5;
    const double im_min = -1.0;
    const double im_max =  1.0;

    for (int py = 0; py < N; ++py) {
        // compute imaginary coordinate (top to bottom)
        double im = im_max - ( (double)py / (N - 1) ) * (im_max - im_min);

        uint8_t out_byte = 0;
        int bit_count = 0;

        for (int px = 0; px < N; ++px) {
            double re = re_min + ( (double)px / (N - 1) ) * (re_max - re_min);

            // iterate z = x + i*y
            double x = 0.0;
            double y = 0.0;
            int iter = 0;
            while (iter < max_iter) {
                // z^2: (x+iy)^2 = (x^2 - y^2) + i(2xy)
                double x2 = x*x;
                double y2 = y*y;
                if (x2 + y2 > 4.0) break; // escape radius 2
                double two_xy = 2.0 * x * y;
                x = x2 - y2 + re;
                y = two_xy + im;
                ++iter;
            }

            // In PBM P4: 1 bits are black, 0 bits are white.
            // We set bit = 1 if point is inside (did not escape within max_iter).
            int inside = (iter == max_iter) ? 1 : 0;

            out_byte = (out_byte << 1) | (inside & 1);
            ++bit_count;

            if (bit_count == 8) {
                // write the completed byte
                if (fputc(out_byte, stdout) == EOF) return 1;
                out_byte = 0;
                bit_count = 0;
            }
        }

        if (bit_count != 0) {
            // pad remaining bits on the right with zeros (white)
            out_byte <<= (8 - bit_count);
            if (fputc(out_byte, stdout) == EOF) return 1;
        }
    }

    return 0;
}