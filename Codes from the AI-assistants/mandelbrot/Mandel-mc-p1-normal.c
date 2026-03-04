#include <stdio.h>

int main(void) {
    const int N = 800;          // image size
    const int max_iter = 1000;  // iteration limit

    // View window in the complex plane
    const double x_min = -2.0;
    const double x_max =  1.0;
    const double y_min = -1.5;
    const double y_max =  1.5;

    // PBM header (ASCII)
    printf("P1\n");
    printf("%d %d\n", N, N);

    for (int py = 0; py < N; ++py) {
        for (int px = 0; px < N; ++px) {
            double x = x_min + (double)px * (x_max - x_min) / (N - 1);
            double y = y_max - (double)py * (y_max - y_min) / (N - 1);

            double zx = 0.0;
            double zy = 0.0;
            int iter = 0;

            while (iter < max_iter) {
                double zx2 = zx * zx - zy * zy;
                double zy2 = 2.0 * zx * zy;

                zx = zx2 + x;
                zy = zy2 + y;

                if (zx * zx + zy * zy > 4.0) {
                    break;
                }
                ++iter;
            }

            int pixel = (iter == max_iter) ? 1 : 0;
            printf("%d ", pixel);
        }
        printf("\n");
    }

    return 0;
}
