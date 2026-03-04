// mandelbrot.c
// Build: gcc -O2 -march=native -std=c11 -Wall -Wextra -pedantic mandelbrot.c -lm -o mandelbrot
//
// Usage examples:
//   ./mandelbrot 1000 1000 mandelbrot.pgm
//   ./mandelbrot 2000 2000 out.pgm -2.0 1.0 -1.5 1.5
//   ./mandelbrot 4000 2000 out.pgm -0.75 -0.72 0.10 0.13   (zoom region)
//
// Args:
//   N max_iter output.pgm [xmin xmax ymin ymax]
//
// Notes:
// - Outputs PGM P5 (portable graymap) which is in the same "portable anymap" family as PBM.
// - Streams scanlines: O(N) memory; safe for 8 GB RAM even for large N.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include <math.h>

static int parse_int(const char *s, int *out) {
    errno = 0;
    char *end = NULL;
    long v = strtol(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0') return 0;
    if (v < 1 || v > 200000) return 0; // guardrail
    *out = (int)v;
    return 1;
}

static int parse_double(const char *s, double *out) {
    errno = 0;
    char *end = NULL;
    double v = strtod(s, &end);
    if (errno != 0 || end == s || *end != '\0') return 0;
    *out = v;
    return 1;
}

// Map iteration count to grayscale byte.
// Points inside the set (didn't escape) -> black (0).
// Escaped quickly -> lighter.
static inline uint8_t iter_to_gray(int iter, int max_iter) {
    if (iter >= max_iter) return 0;
    // Simple linear ramp. (You can swap to smooth coloring later.)
    double t = (double)iter / (double)max_iter; // 0..1
    int g = (int)lround(255.0 * t);
    if (g < 0) g = 0;
    if (g > 255) g = 255;
    return (uint8_t)g;
}

// Escape-time for Mandelbrot at point C = (cx, cy).
static inline int mandelbrot_escape(double cx, double cy, int max_iter) {
    double a = 0.0, b = 0.0; // z = a + i b
    // Iterate: z <- z^2 + c
    for (int i = 0; i < max_iter; i++) {
        // Compute z^2: (a+ib)^2 = (a^2 - b^2) + i(2ab)
        double aa = a * a;
        double bb = b * b;
        if (aa + bb > 4.0) return i; // escaped

        double twoab = 2.0 * a * b;
        a = aa - bb + cx;
        b = twoab + cy;
    }
    return max_iter; // did not escape
}

int main(int argc, char **argv) {
    if (argc != 4 && argc != 8) {
        fprintf(stderr,
            "Usage: %s N max_iter output.pgm [xmin xmax ymin ymax]\n"
            "Example: %s 1000 1000 mandelbrot.pgm\n"
            "Example: %s 2000 2000 out.pgm -2.0 1.0 -1.5 1.5\n",
            argv[0], argv[0], argv[0]);
        return 2;
    }

    int N = 0, max_iter = 0;
    if (!parse_int(argv[1], &N) || !parse_int(argv[2], &max_iter)) {
        fprintf(stderr, "Invalid N or max_iter.\n");
        return 2;
    }
    if (max_iter < 1 || max_iter > 100000000) {
        fprintf(stderr, "max_iter out of range.\n");
        return 2;
    }

    const char *out_path = argv[3];

    // Default viewport
    double xmin = -2.0, xmax = 1.0, ymin = -1.5, ymax = 1.5;

    if (argc == 8) {
        if (!parse_double(argv[4], &xmin) || !parse_double(argv[5], &xmax) ||
            !parse_double(argv[6], &ymin) || !parse_double(argv[7], &ymax)) {
            fprintf(stderr, "Invalid viewport bounds.\n");
            return 2;
        }
        if (!(xmin < xmax) || !(ymin < ymax)) {
            fprintf(stderr, "Viewport must satisfy xmin<xmax and ymin<ymax.\n");
            return 2;
        }
    }

    FILE *fp = fopen(out_path, "wb");
    if (!fp) {
        fprintf(stderr, "Failed to open output '%s': %s\n", out_path, strerror(errno));
        return 1;
    }

    // Write PGM header (P5)
    // width height maxval
    if (fprintf(fp, "P5\n%d %d\n255\n", N, N) < 0) {
        fprintf(stderr, "Failed writing header.\n");
        fclose(fp);
        return 1;
    }

    uint8_t *row = (uint8_t *)malloc((size_t)N);
    if (!row) {
        fprintf(stderr, "Out of memory allocating row.\n");
        fclose(fp);
        return 1;
    }

    // Precompute scale factors to avoid repeated divisions.
    const double dx = (xmax - xmin) / (double)(N - 1);
    const double dy = (ymax - ymin) / (double)(N - 1);

    // Render top to bottom (j=0 => y=ymax)
    for (int j = 0; j < N; j++) {
        double cy = ymax - (double)j * dy;

        for (int i = 0; i < N; i++) {
            double cx = xmin + (double)i * dx;
            int it = mandelbrot_escape(cx, cy, max_iter);
            row[i] = iter_to_gray(it, max_iter);
        }

        size_t written = fwrite(row, 1, (size_t)N, fp);
        if (written != (size_t)N) {
            fprintf(stderr, "Write error while writing pixels.\n");
            free(row);
            fclose(fp);
            return 1;
        }
    }

    free(row);
    if (fclose(fp) != 0) {
        fprintf(stderr, "Error closing output file.\n");
        return 1;
    }

    return 0;
}
