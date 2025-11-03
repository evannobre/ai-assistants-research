#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <complex.h>

#define MAX_ITERATIONS 1000

typedef struct {
    int width;
    int height;
    unsigned char *data;
} Bitmap;

Bitmap* create_bitmap(int width, int height) {
    Bitmap *bmp = malloc(sizeof(Bitmap));
    bmp->width = width;
    bmp->height = height;
    bmp->data = calloc(width * height, sizeof(unsigned char));
    return bmp;
}

void free_bitmap(Bitmap *bmp) {
    free(bmp->data);
    free(bmp);
}

int mandelbrot_iterations(double complex c, int max_iter) {
    double complex z = 0.0 + 0.0 * I;
    int iter = 0;
    
    while (creal(z) * creal(z) + cimag(z) * cimag(z) <= 4.0 && iter < max_iter) {
        z = z * z + c;
        iter++;
    }
    
    return iter;
}

void generate_mandelbrot(Bitmap *bmp, double x_min, double x_max, double y_min, double y_max) {
    double x_step = (x_max - x_min) / bmp->width;
    double y_step = (y_max - y_min) / bmp->height;
    
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int y = 0; y < bmp->height; y++) {
        for (int x = 0; x < bmp->width; x++) {
            double real = x_min + x * x_step;
            double imag = y_min + y * y_step;
            double complex c = real + imag * I;
            
            int iterations = mandelbrot_iterations(c, MAX_ITERATIONS);
            
            if (iterations == MAX_ITERATIONS) {
                bmp->data[y * bmp->width + x] = 0; // Black for inside set
            } else {
                bmp->data[y * bmp->width + x] = 1; // White for outside set
            }
        }
    }
}

void write_pbm(Bitmap *bmp, const char *filename) {
    FILE *file = fopen(filename, "wb");
    if (!file) {
        perror("Failed to open file");
        return;
    }
    
    // Write PBM header
    fprintf(file, "P4\n%d %d\n", bmp->width, bmp->height);
    
    // Calculate bytes per row (PBM format uses 1 bit per pixel)
    int bytes_per_row = (bmp->width + 7) / 8;
    
    // Write bitmap data
    for (int y = 0; y < bmp->height; y++) {
        for (int byte = 0; byte < bytes_per_row; byte++) {
            unsigned char data_byte = 0;
            int bits_in_byte = (byte == bytes_per_row - 1) ? 
                              bmp->width % 8 : 8;
            if (bits_in_byte == 0) bits_in_byte = 8;
            
            for (int bit = 0; bit < bits_in_byte; bit++) {
                int x = byte * 8 + bit;
                if (x < bmp->width) {
                    // Invert since PBM: 0=white, 1=black, but we want black for inside set
                    if (bmp->data[y * bmp->width + x] == 0) {
                        data_byte |= (1 << (7 - bit)); // Set bit for black
                    }
                }
            }
            fwrite(&data_byte, 1, 1, file);
        }
    }
    
    fclose(file);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        return 1;
    }
    
    int size = atoi(argv[1]);
    if (size <= 0) {
        fprintf(stderr, "Size must be positive integer\n");
        return 1;
    }
    
    // Memory check for large sizes
    size_t estimated_memory = (size_t)size * size * sizeof(unsigned char) + 
                             (size_t)((size + 7) / 8) * size;
    if (estimated_memory > 6ULL * 1024 * 1024 * 1024) { // 6GB threshold
        fprintf(stderr, "Error: Estimated memory usage (%zu MB) exceeds safe limits\n", 
                estimated_memory / (1024 * 1024));
        return 1;
    }
    
    printf("Generating Mandelbrot set %dx%d...\n", size, size);
    
    Bitmap *bmp = create_bitmap(size, size);
    
    // Mandelbrot set coordinates: [-1.5-i, 0.5+i]
    double x_min = -2.0;
    double x_max = 0.5;
    double y_min = -1.25;
    double y_max = 1.25;
    
    generate_mandelbrot(bmp, x_min, x_max, y_min, y_max);
    
    char filename[256];
    snprintf(filename, sizeof(filename), "mandelbrot_%d.pbm", size);
    write_pbm(bmp, filename);
    
    printf("Mandelbrot set written to %s\n", filename);
    
    free_bitmap(bmp);
    return 0;
}