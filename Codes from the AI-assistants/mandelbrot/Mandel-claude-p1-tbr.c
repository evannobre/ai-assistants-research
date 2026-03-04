#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    unsigned char r, g, b;
} RGB;

// Color mapping function using smooth coloring
RGB get_color(int iterations, int max_iter) {
    if (iterations == max_iter) {
        return (RGB){0, 0, 0}; // Black for points in the set
    }
    
    // Smooth color gradient
    double t = (double)iterations / max_iter;
    RGB color;
    
    // Blue to cyan to white to yellow to red gradient
    if (t < 0.16) {
        double local_t = t / 0.16;
        color.r = 0;
        color.g = (unsigned char)(local_t * 127);
        color.b = (unsigned char)(127 + local_t * 128);
    } else if (t < 0.42) {
        double local_t = (t - 0.16) / 0.26;
        color.r = 0;
        color.g = (unsigned char)(127 + local_t * 128);
        color.b = 255;
    } else if (t < 0.64) {
        double local_t = (t - 0.42) / 0.22;
        color.r = (unsigned char)(local_t * 255);
        color.g = 255;
        color.b = (unsigned char)(255 - local_t * 255);
    } else if (t < 0.86) {
        double local_t = (t - 0.64) / 0.22;
        color.r = 255;
        color.g = (unsigned char)(255 - local_t * 128);
        color.b = 0;
    } else {
        double local_t = (t - 0.86) / 0.14;
        color.r = (unsigned char)(255 - local_t * 128);
        color.g = (unsigned char)(127 - local_t * 127);
        color.b = 0;
    }
    
    return color;
}

// Mandelbrot iteration function
int mandelbrot(double c_re, double c_im, int max_iter) {
    double z_re = 0.0, z_im = 0.0;
    int iter = 0;
    
    while (z_re * z_re + z_im * z_im <= 4.0 && iter < max_iter) {
        double temp = z_re * z_re - z_im * z_im + c_re;
        z_im = 2.0 * z_re * z_im + c_im;
        z_re = temp;
        iter++;
    }
    
    return iter;
}

// Generate Mandelbrot set and save as PPM
void generate_mandelbrot(int N, const char* filename, int max_iter) {
    // Define the complex plane bounds
    double re_min = -2.5, re_max = 1.0;
    double im_min = -1.25, im_max = 1.25;
    
    // Allocate pixel buffer
    RGB* pixels = (RGB*)malloc(N * N * sizeof(RGB));
    if (!pixels) {
        fprintf(stderr, "Memory allocation failed\n");
        return;
    }
    
    // Calculate step sizes
    double re_step = (re_max - re_min) / N;
    double im_step = (im_max - im_min) / N;
    
    // Generate the set
    printf("Generating %dx%d Mandelbrot set...\n", N, N);
    for (int y = 0; y < N; y++) {
        double c_im = im_max - y * im_step;
        
        for (int x = 0; x < N; x++) {
            double c_re = re_min + x * re_step;
            
            int iterations = mandelbrot(c_re, c_im, max_iter);
            pixels[y * N + x] = get_color(iterations, max_iter);
        }
        
        if (y % (N / 10) == 0) {
            printf("Progress: %d%%\n", (y * 100) / N);
        }
    }
    
    // Write PPM file
    printf("Writing to %s...\n", filename);
    FILE* fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Failed to open file for writing\n");
        free(pixels);
        return;
    }
    
    // PPM header (P6 format - binary)
    fprintf(fp, "P6\n%d %d\n255\n", N, N);
    
    // Write pixel data
    fwrite(pixels, sizeof(RGB), N * N, fp);
    
    fclose(fp);
    free(pixels);
    printf("Done! Image saved to %s\n", filename);
}

int main(int argc, char* argv[]) {
    int N = 800;          // Default size
    int max_iter = 256;   // Maximum iterations
    const char* filename = "mandelbrot.ppm";
    
    if (argc > 1) {
        N = atoi(argv[1]);
        if (N <= 0 || N > 10000) {
            fprintf(stderr, "Invalid size. Using default: 800\n");
            N = 800;
        }
    }
    
    if (argc > 2) {
        max_iter = atoi(argv[2]);
        if (max_iter <= 0) {
            fprintf(stderr, "Invalid max iterations. Using default: 256\n");
            max_iter = 256;
        }
    }
    
    if (argc > 3) {
        filename = argv[3];
    }
    
    printf("Configuration:\n");
    printf("  Size: %dx%d pixels\n", N, N);
    printf("  Max iterations: %d\n", max_iter);
    printf("  Output file: %s\n\n", filename);
    
    generate_mandelbrot(N, filename, max_iter);
    
    return 0;
}
