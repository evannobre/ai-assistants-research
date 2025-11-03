#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <complex.h>
#include <stdint.h>

// Configuration for memory management
#define MAX_DIMENSION 16000
#define MAX_ITERATIONS 1000
#define ESCAPE_RADIUS 2.0

typedef struct {
    uint8_t *data;
    size_t width;
    size_t height;
    size_t stride;
} bitmap_t;

// Memory-efficient bitmap initialization
bitmap_t* bitmap_create(size_t width, size_t height) {
    bitmap_t *bmp = malloc(sizeof(bitmap_t));
    if (!bmp) return NULL;
    
    bmp->width = width;
    bmp->height = height;
    bmp->stride = (width + 7) / 8; // Bits per row, rounded up to bytes
    
    bmp->data = calloc(bmp->stride * height, sizeof(uint8_t));
    if (!bmp->data) {
        free(bmp);
        return NULL;
    }
    
    return bmp;
}

void bitmap_destroy(bitmap_t *bmp) {
    if (bmp) {
        free(bmp->data);
        free(bmp);
    }
}

void bitmap_set_pixel(bitmap_t *bmp, size_t x, size_t y, int value) {
    if (x >= bmp->width || y >= bmp->height) return;
    
    size_t byte_index = y * bmp->stride + (x / 8);
    uint8_t bit_mask = 1 << (7 - (x % 8));
    
    if (value) {
        bmp->data[byte_index] |= bit_mask;
    } else {
        bmp->data[byte_index] &= ~bit_mask;
    }
}

// Optimized Mandelbrot calculation using the quadratic recurrence
int mandelbrot_point(double complex c, int max_iter) {
    double complex z = 0 + 0 * I;
    
    for (int i = 0; i < max_iter; i++) {
        // z_{n+1} = (z_n)^2 + c
        z = z * z + c;
        
        // Check escape condition: |z| > 2
        if (creal(z) * creal(z) + cimag(z) * cimag(z) > ESCAPE_RADIUS * ESCAPE_RADIUS) {
            return i;
        }
    }
    
    return max_iter;
}

// Generate Mandelbrot set with the specified parameters
void generate_mandelbrot(bitmap_t *bmp, 
                        double real_min, double real_max,
                        double imag_min, double imag_max,
                        int max_iter) {
    
    double real_step = (real_max - real_min) / (bmp->width - 1);
    double imag_step = (imag_max - imag_min) / (bmp->height - 1);
    
    #pragma omp parallel for schedule(dynamic)
    for (size_t y = 0; y < bmp->height; y++) {
        double imag = imag_min + y * imag_step;
        
        for (size_t x = 0; x < bmp->width; x++) {
            double real = real_min + x * real_step;
            double complex c = real + imag * I;
            
            int iterations = mandelbrot_point(c, max_iter);
            
            // Set pixel to 1 (black) if in Mandelbrot set, 0 (white) otherwise
            bitmap_set_pixel(bmp, x, y, (iterations == max_iter));
        }
    }
}

// Write PBM file in binary format (P4)
int write_pbm(const char *filename, const bitmap_t *bmp) {
    FILE *file = fopen(filename, "wb");
    if (!file) {
        return -1;
    }
    
    // Write PBM header
    fprintf(file, "P4\n%zu %zu\n", bmp->width, bmp->height);
    
    // Write bitmap data
    size_t data_size = bmp->stride * bmp->height;
    size_t written = fwrite(bmp->data, 1, data_size, file);
    
    fclose(file);
    return (written == data_size) ? 0 : -1;
}

// Memory usage estimation
void print_memory_usage(size_t width, size_t height) {
    size_t stride = (width + 7) / 8;
    size_t bitmap_memory = stride * height;
    size_t total_estimated = bitmap_memory + sizeof(bitmap_t);
    
    printf("Memory usage estimation:\n");
    printf("  Image dimensions: %zux%zu\n", width, height);
    printf("  Bitmap memory: %.2f MB\n", bitmap_memory / (1024.0 * 1024.0));
    printf("  Total estimated: %.2f MB\n", total_estimated / (1024.0 * 1024.0));
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <dimension>\n", argv[0]);
        fprintf(stderr, "Example: %s 16000\n", argv[0]);
        return 1;
    }
    
    size_t dimension = atol(argv[1]);
    if (dimension <= 0 || dimension > MAX_DIMENSION) {
        fprintf(stderr, "Error: Dimension must be between 1 and %d\n", MAX_DIMENSION);
        return 1;
    }
    
    printf("Generating Mandelbrot set %zux%zu...\n", dimension, dimension);
    print_memory_usage(dimension, dimension);
    
    // Create bitmap
    bitmap_t *bmp = bitmap_create(dimension, dimension);
    if (!bmp) {
        fprintf(stderr, "Error: Failed to allocate memory for bitmap\n");
        return 1;
    }
    
    // Mandelbrot set coordinates: [-1.5-i, 0.5+i]
    double real_min = -1.5;
    double real_max = 0.5;
    double imag_min = -1.0;
    double imag_max = 1.0;
    
    printf("Calculating Mandelbrot set...\n");
    generate_mandelbrot(bmp, real_min, real_max, imag_min, imag_max, MAX_ITERATIONS);
    
    printf("Writing PBM file...\n");
    if (write_pbm("mandelbrot.pbm", bmp) != 0) {
        fprintf(stderr, "Error: Failed to write PBM file\n");
        bitmap_destroy(bmp);
        return 1;
    }
    
    printf("Done! Output written to mandelbrot.pbm\n");
    
    bitmap_destroy(bmp);
    return 0;
}