#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <math.h>

#define N 800
#define MAX_ITER 256

// Color mapping function - maps iteration count to RGB
void get_color(int iter, int max_iter, unsigned char *r, unsigned char *g, unsigned char *b) {
    if (iter == max_iter) {
        *r = *g = *b = 0;  // Black for points in the set
    } else {
        // Smooth color gradient
        double t = (double)iter / max_iter;
        *r = (unsigned char)(9 * (1 - t) * t * t * t * 255);
        *g = (unsigned char)(15 * (1 - t) * (1 - t) * t * t * 255);
        *b = (unsigned char)(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255);
    }
}

// Mandelbrot iteration function
int mandelbrot(double complex c, int max_iter) {
    double complex z = 0;
    int n;
    
    for (n = 0; n < max_iter; n++) {
        if (cabs(z) > 2.0) {
            return n;
        }
        z = z * z + c;
    }
    
    return max_iter;
}

int main() {
    FILE *fp;
    int x, y;
    unsigned char r, g, b;
    
    // Define the complex plane bounds
    double x_min = -2.5;
    double x_max = 1.0;
    double y_min = -1.25;
    double y_max = 1.25;
    
    // Open file for writing
    fp = fopen("mandelbrot.ppm", "wb");
    if (!fp) {
        fprintf(stderr, "Error: Cannot open file for writing\n");
        return 1;
    }
    
    // Write PPM header (P6 format - binary)
    fprintf(fp, "P6\n%d %d\n255\n", N, N);
    
    // Generate Mandelbrot set
    printf("Generating %dx%d Mandelbrot set...\n", N, N);
    
    for (y = 0; y < N; y++) {
        for (x = 0; x < N; x++) {
            // Map pixel coordinates to complex plane
            double real = x_min + (x * (x_max - x_min) / N);
            double imag = y_min + (y * (y_max - y_min) / N);
            double complex c = real + imag * I;
            
            // Calculate iterations
            int iter = mandelbrot(c, MAX_ITER);
            
            // Get color for this iteration count
            get_color(iter, MAX_ITER, &r, &g, &b);
            
            // Write RGB values to file
            fputc(r, fp);
            fputc(g, fp);
            fputc(b, fp);
        }
        
        // Progress indicator
        if (y % 50 == 0) {
            printf("Progress: %.1f%%\n", (y * 100.0) / N);
        }
    }
    
    fclose(fp);
    printf("Done! Image saved as 'mandelbrot.ppm'\n");
    printf("You can convert to PNG using: convert mandelbrot.ppm mandelbrot.png\n");
    
    return 0;
}

/* 
Compilation and execution:
gcc -o mandelbrot mandelbrot.c -lm
./mandelbrot

The algorithm:
1. For each pixel (x,y) in the N×N grid
2. Map the pixel to a complex number C in the plane
3. Initialize z₀ = 0
4. Iterate z_{n+1} = z_n² + C
5. Count iterations until |z_n| > 2 or max iterations reached
6. Color the pixel based on iteration count
7. Write RGB values to PPM file

The PPM format is simple:
- Header: "P6" (binary), width, height, max color value
- Body: RGB triplets for each pixel (left-to-right, top-to-bottom)
*/