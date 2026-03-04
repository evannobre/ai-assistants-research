#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <math.h>
#include <string.h>

#define DEFAULT_SIZE 800
#define MAX_ITERATIONS 1000
#define ESCAPE_RADIUS 2.0

typedef struct {
    int width;
    int height;
    unsigned char *data;
} Image;

Image *create_image(int width, int height) {
    Image *img = malloc(sizeof(Image));
    img->width = width;
    img->height = height;
    img->data = calloc(width * height, sizeof(unsigned char));
    return img;
}

void destroy_image(Image *img) {
    free(img->data);
    free(img);
}

int mandelbrot_iterations(double complex c, int max_iter) {
    double complex z = 0.0 + 0.0 * I;
    
    for (int n = 0; n < max_iter; n++) {
        z = z * z + c;
        
        // Check if escaped
        if (cabs(z) > ESCAPE_RADIUS) {
            return n;
        }
    }
    
    return max_iter;
}

void generate_mandelbrot(Image *img, 
                         double real_min, double real_max,
                         double imag_min, double imag_max) {
    
    double real_range = real_max - real_min;
    double imag_range = imag_max - imag_min;
    
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int y = 0; y < img->height; y++) {
        for (int x = 0; x < img->width; x++) {
            // Map pixel coordinates to complex plane
            double real = real_min + (x * real_range) / (img->width - 1);
            double imag = imag_min + (y * imag_range) / (img->height - 1);
            
            double complex c = real + imag * I;
            int iterations = mandelbrot_iterations(c, MAX_ITERATIONS);
            
            // Convert iterations to grayscale (0-255)
            // Points in the set (max_iterations) become black (0)
            // Escaped points get brighter based on escape time
            unsigned char value;
            if (iterations == MAX_ITERATIONS) {
                value = 0;  // Black for points in the set
            } else {
                // Smooth coloring
                double smooth_val = iterations + 1 - log(log(cabs(c))) / log(2.0);
                value = (unsigned char)(255 * (1.0 - smooth_val / MAX_ITERATIONS));
            }
            
            img->data[y * img->width + x] = value;
        }
    }
}

void save_as_pbm(Image *img, const char *filename) {
    FILE *file = fopen(filename, "wb");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file %s for writing\n", filename);
        return;
    }
    
    // Write PBM header (P5 = binary grayscale)
    fprintf(file, "P5\n");
    fprintf(file, "%d %d\n", img->width, img->height);
    fprintf(file, "255\n");  // Max pixel value
    
    // Write binary pixel data
    fwrite(img->data, sizeof(unsigned char), img->width * img->height, file);
    
    fclose(file);
    printf("Saved Mandelbrot set to %s\n", filename);
}

void print_usage() {
    printf("Mandelbrot Set Generator\n");
    printf("Usage: mandelbrot [options]\n");
    printf("Options:\n");
    printf("  -s N        Set image size (N x N pixels, default: %d)\n", DEFAULT_SIZE);
    printf("  -o FILE     Output filename (default: mandelbrot.pbm)\n");
    printf("  -x MIN MAX  Set real axis range (default: -2.0 1.0)\n");
    printf("  -y MIN MAX  Set imaginary axis range (default: -1.5 1.5)\n");
    printf("  -h          Show this help message\n");
}

int main(int argc, char *argv[]) {
    int size = DEFAULT_SIZE;
    char *output_file = "mandelbrot.pbm";
    double real_min = -2.0, real_max = 1.0;
    double imag_min = -1.5, imag_max = 1.5;
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-s") == 0 && i + 1 < argc) {
            size = atoi(argv[++i]);
            if (size <= 0) {
                fprintf(stderr, "Error: Invalid size\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            output_file = argv[++i];
        } else if (strcmp(argv[i], "-x") == 0 && i + 2 < argc) {
            real_min = atof(argv[++i]);
            real_max = atof(argv[++i]);
        } else if (strcmp(argv[i], "-y") == 0 && i + 2 < argc) {
            imag_min = atof(argv[++i]);
            imag_max = atof(argv[++i]);
        } else if (strcmp(argv[i], "-h") == 0) {
            print_usage();
            return 0;
        } else {
            fprintf(stderr, "Error: Unknown option %s\n", argv[i]);
            print_usage();
            return 1;
        }
    }
    
    printf("Generating Mandelbrot set...\n");
    printf("Size: %d x %d\n", size, size);
    printf("Region: Re[%f, %f], Im[%f, %f]\n", real_min, real_max, imag_min, imag_max);
    
    Image *img = create_image(size, size);
    
    generate_mandelbrot(img, real_min, real_max, imag_min, imag_max);
    
    save_as_pbm(img, output_file);
    
    destroy_image(img);
    
    return 0;
}