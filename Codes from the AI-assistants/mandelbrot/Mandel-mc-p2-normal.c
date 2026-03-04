#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s N\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "N must be positive\n");
        return 1;
    }

    const int max_iter = 1000;

    // Complex plane bounds
    const double min_re = -1.5;
    const double max_re =  0.5;
    const double min_im = -1.0;
    const double max_im =  1.0;

    // Precompute scales
    const double re_scale = (max_re - min_re) / (N - 1);
    const double im_scale = (max_im - min_im) / (N - 1);

    // PBM P4 header
    printf("P4\n%d %d\n", N, N);

    int bytes_per_row = (N + 7) / 8;
    unsigned char *row = (unsigned char *)malloc(bytes_per_row);
    if (!row) {
        fprintf(stderr, "Failed to allocate row buffer\n");
        return 1;
    }

    for (int y = 0; y < N; ++y) {
        // Imaginary part for this row
        double c_im = min_im + y * im_scale;

        // Clear row buffer
        for (int i = 0; i < bytes_per_row; ++i) {
            row[i] = 0;
        }

        for (int x = 0; x < N; ++x) {
            double c_re = min_re + x * re_scale;

            double z_re = 0.0;
            double z_im = 0.0;
            int iter = 0;

            while (iter < max_iter) {
                double z_re2 = z_re * z_re;
                double z_im2 = z_im * z_im;

                if (z_re2 + z_im2 > 4.0) {
                    break; // escaped
                }

                double new_re = z_re2 - z_im2 + c_re;
                double new_im = 2.0 * z_re * z_im + c_im;

                z_re = new_re;
                z_im = new_im;
                ++iter;
            }

            int inside = (iter == max_iter); // 1 if inside, 0 if escaped

            // Set bit: 1 = black (inside), 0 = white (outside)
            if (inside) {
                int byte_index = x / 8;
                int bit_index  = 7 - (x % 8); // MSB first
                row[byte_index] |= (1u << bit_index);
            }
        }

        // Write row to stdout
        if (fwrite(row, 1, bytes_per_row, stdout) != (size_t)bytes_per_row) {
            fprintf(stderr, "Error writing output\n");
            free(row);
            return 1;
        }
    }

    free(row);
    return 0;
}
