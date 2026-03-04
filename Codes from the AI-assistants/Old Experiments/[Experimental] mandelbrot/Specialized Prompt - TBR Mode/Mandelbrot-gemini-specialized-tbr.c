// mandelbrot.c
//
// A program to generate the Mandelbrot set and save it as a PBM image.
// Uses native C99 libraries for complex number arithmetic.
//
// Author: Gemini AI
// Date:   October 5, 2025

#include <stdio.h>    // For file I/O (fopen, fprintf, fclose)
#include <stdlib.h>   // For string to integer conversion (atoi)
#include <complex.h>  // For C99 complex number support (_Complex)

int main(int argc, char *argv[]) {
    // --- 1. Argument Parsing and Variable Declaration ---
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <image_dimension> <output_filename.pbm>\n", argv[0]);
        fprintf(stderr, "Example: %s 800 mandelbrot.pbm\n", argv[0]);
        return 1;
    }

    const int N = atoi(argv[1]);
    const char *filename = argv[2];
    
    if (N <= 0) {
        fprintf(stderr, "Error: Image dimension must be a positive integer.\n");
        return 1;
    }

    // --- 2. Define Mandelbrot Parameters ---
    const int MAX_ITER = 1000;
    const double X_MIN = -2.0;
    const double X_MAX = 1.0;
    const double Y_MIN = -1.5;
    const double Y_MAX = 1.5;

    // --- 3. File Handling and PBM Header ---
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        perror("Error opening file");
        return 1;
    }

    // Write the PBM header for a P1 (ASCII black and white) image
    fprintf(fp, "P1\n");
    fprintf(fp, "%d %d\n", N, N);

    fprintf(stderr, "Generating a %dx%d Mandelbrot set into '%s'...\n", N, N, filename);

    // --- 4. Main Generation Loop ---
    for (int py = 0; py < N; py++) {
        for (int px = 0; px < N; px++) {
            // Map the pixel (px, py) to a point C in the complex plane
            double c_real = X_MIN + (double)px / (N - 1) * (X_MAX - X_MIN);
            double c_imag = Y_MIN + (double)py / (N - 1) * (Y_MAX - Y_MIN);
            
            double complex C = c_real + c_imag * I;
            double complex z = 0;
            
            int iter = 0;
            // The core iteration loop
            // We use creal/cimag and check magnitude squared to avoid sqrt()
            while (iter < MAX_ITER) {
                if ((creal(z) * creal(z) + cimag(z) * cimag(z)) > 4.0) {
                    break; // The point has escaped
                }
                z = z * z + C;
                iter++;
            }

            // Determine the pixel color and write to file
            if (iter == MAX_ITER) {
                fprintf(fp, "1 "); // Inside the set (black)
            } else {
                fprintf(fp, "0 "); // Outside the set (white)
            }
        }
        fprintf(fp, "\n"); // Newline for each row
    }

    // --- 5. Cleanup ---
    fclose(fp);
    fprintf(stderr, "Done. Image saved successfully.\n");

    return 0;
}