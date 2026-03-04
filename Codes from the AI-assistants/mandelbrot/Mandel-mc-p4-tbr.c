// mandelbrot_p4.c
// Compile: gcc -O3 -march=native -o mandelbrot_p4 mandelbrot_p4.c
// Optional multithreading: gcc -O3 -march=native -fopenmp -o mandelbrot_p4 mandelbrot_p4.c

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s N [maxiter]\n", argv[0]);
        return 1;
    }

    const int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "N must be positive\n");
        return 1;
    }

    const int maxiter = (argc >= 3) ? atoi(argv[2]) : 1000;

    // Complex plane bounds: real [-1.5, 0.5], imag [-1.0, 1.0]
    const double re_min = -1.5;
    const double re_max =  0.5;
    const double im_min = -1.0;
    const double im_max =  1.0;

    const double re_scale = (re_max - re_min) / (N - 1);
    const double im_scale = (im_max - im_min) / (N - 1);

    // PBM P4 header (binary)
    // Write header to stdout
    printf("P4\n%d %d\n", N, N);
    fflush(stdout);

    // Buffer for one row: ceil(N/8) bytes
    const int row_bytes = (N + 7) / 8;
    unsigned char *rowbuf = (unsigned char*)malloc(row_bytes);
    if (!rowbuf) {
        fprintf(stderr, "Allocation failed\n");
        return 1;
    }
    memset(rowbuf, 0, row_bytes);

    // For each row (y from 0..N-1)
    for (int y = 0; y < N; ++y) {
        double c_im = im_max - y * im_scale; // top to bottom

        // Zero row buffer
        memset(rowbuf, 0, row_bytes);

        int bit_index = 0;      // 0..7 within current byte (MSB first)
        int byte_index = 0;
        unsigned char current_byte = 0;

        for (int x = 0; x < N; ++x) {
            double c_re = re_min + x * re_scale;

            // Mandelbrot iteration: z = 0 initially
            double z_re = 0.0, z_im = 0.0;
            double z_re2 = 0.0, z_im2 = 0.0;
            int iter = 0;

            // iterate
            while (iter < maxiter && (z_re2 + z_im2) <= 4.0) {
                // z = z^2 + c  => (z_re + i z_im)^2 = (z_re^2 - z_im^2) + i(2*z_re*z_im)
                z_im = 2.0 * z_re * z_im + c_im;
                z_re = z_re2 - z_im2 + c_re;

                z_re2 = z_re * z_re;
                z_im2 = z_im * z_im;

                ++iter;
            }

            // PBM: 1 bit = black pixel, 0 bit = white pixel.
            // Convention: inside set -> black (1), escaped -> white (0)
            int inside = (iter >= maxiter) ? 1 : 0;

            // Pack MSB-first
            current_byte <<= 1;
            current_byte |= (inside ? 0x1 : 0x0);
            ++bit_index;

            if (bit_index == 8) {
                rowbuf[byte_index++] = current_byte;
                bit_index = 0;
                current_byte = 0;
            }
        }

        // If row not multiple of 8, pad remaining bits on the right (LSB) with zeros.
        if (bit_index != 0) {
            // shift remaining bits to MSB positions
            current_byte <<= (8 - bit_index);
            rowbuf[byte_index++] = current_byte;
        }

        // Write the row bytes to stdout
        size_t written = fwrite(rowbuf, 1, row_bytes, stdout);
        if (written != (size_t)row_bytes) {
            fprintf(stderr, "Write error\n");
            free(rowbuf);
            return 1;
        }
    }

    free(rowbuf);
    return 0;
}
