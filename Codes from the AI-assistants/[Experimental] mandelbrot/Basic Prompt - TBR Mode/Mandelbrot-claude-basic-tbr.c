#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define N 800
#define MAX_ITER 256

// Check if point C is in Mandelbrot set
int mandelbrot(double complex C) {
    double complex z = 0.0 + 0.0 * I;
    int n;
    
    for (n = 0; n < MAX_ITER; n++) {
        // z_(n+1) = z_n^2 + C
        z = z * z + C;
        
        // Check if magnitude exceeds 2 (escapes to infinity)
        if (cabs(z) > 2.0) {
            return n;
        }
    }
    
    return MAX_ITER;
}

void generate_mandelbrot_pbm(const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    
    // Write PBM header (P1 = ASCII bitmap, P4 = binary bitmap)
    fprintf(fp, "P1\n%d %d\n", N, N);
    
    // Define viewing window in complex plane
    double re_min = -2.5, re_max = 1.0;
    double im_min = -1.25, im_max = 1.25;
    
    // Generate pixels
    for (int y = 0; y < N; y++) {
        for (int x = 0; x < N; x++) {
            // Map pixel to complex plane
            double re = re_min + (re_max - re_min) * x / (N - 1);
            double im = im_min + (im_max - im_min) * y / (N - 1);
            double complex C = re + im * I;
            
            // Calculate iterations
            int iter = mandelbrot(C);
            
            // Write pixel (1 = white/not in set, 0 = black/in set)
            fprintf(fp, "%d ", (iter < MAX_ITER) ? 1 : 0);
        }
        fprintf(fp, "\n");
    }
    
    fclose(fp);
    printf("Mandelbrot set saved to %s (%dx%d pixels)\n", filename, N, N);
}

void generate_mandelbrot_pgm(const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    
    // Write PGM header (P2 = ASCII grayscale, P5 = binary grayscale)
    fprintf(fp, "P2\n%d %d\n255\n", N, N);
    
    // Define viewing window
    double re_min = -2.5, re_max = 1.0;
    double im_min = -1.25, im_max = 1.25;
    
    // Generate grayscale pixels
    for (int y = 0; y < N; y++) {
        for (int x = 0; x < N; x++) {
            double re = re_min + (re_max - re_min) * x / (N - 1);
            double im = im_min + (im_max - im_min) * y / (N - 1);
            double complex C = re + im * I;
            
            int iter = mandelbrot(C);
            
            // Map iterations to grayscale (0=black, 255=white)
            int color = (iter == MAX_ITER) ? 0 : (int)(255.0 * iter / MAX_ITER);
            fprintf(fp, "%d ", color);
        }
        fprintf(fp, "\n");
    }
    
    fclose(fp);
    printf("Mandelbrot set (grayscale) saved to %s (%dx%d pixels)\n", filename, N, N);
}

int main(int argc, char *argv[]) {
    printf("Generating Mandelbrot set...\n");
    printf("Using quadratic recurrence: z_0 = 0, z_(n+1) = z_n^2 + C\n");
    printf("Max iterations: %d\n", MAX_ITER);
    printf("Image size: %dx%d pixels\n\n", N, N);
    
    // Generate both bitmap and grayscale versions
    generate_mandelbrot_pbm("mandelbrot.pbm");
    generate_mandelbrot_pgm("mandelbrot.pgm");
    
    printf("\nDone! View with image viewer or convert with ImageMagick:\n");
    printf("  convert mandelbrot.pgm mandelbrot.png\n");
    
    return EXIT_SUCCESS;
}