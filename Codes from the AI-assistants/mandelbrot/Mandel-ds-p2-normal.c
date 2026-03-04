/**
 * Mandelbrot Set Generator for Ubuntu 24.04.4
 * Uses native libraries and respects 8GB RAM constraint
 * Compile: gcc -O3 -march=native -fopenmp mandelbrot.c -lm -o mandelbrot
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <time.h>
#include <string.h>
#include <omp.h>

#define MAX_ITER 1000
#define ESCAPE_RADIUS 2.0
#define ESCAPE_RADIUS_SQ 4.0

typedef struct {
    double real;
    double imag;
} Complex;

typedef struct {
    int width;
    int height;
    double x_min;
    double x_max;
    double y_min;
    double y_max;
    uint8_t *pixels;
} FractalImage;

// Vectorized version for better performance
#ifdef __AVX__
#include <immintrin.h>

static inline __m256d complex_magnitude_sq_avx(__m256d z_real, __m256d z_imag) {
    return _mm256_add_pd(_mm256_mul_pd(z_real, z_real), 
                         _mm256_mul_pd(z_imag, z_imag));
}

static inline void mandelbrot_kernel_avx(__m256d c_real, __m256d c_imag, 
                                         int *iter_counts) {
    __m256d z_real = _mm256_setzero_pd();
    __m256d z_imag = _mm256_setzero_pd();
    
    __m256d escape_sq = _mm256_set1_pd(ESCAPE_RADIUS_SQ);
    __m256i iterations = _mm256_setzero_si256();
    __m256i ones = _mm256_set1_epi64x(1);
    __m256i mask;
    
    for (int i = 0; i < MAX_ITER; i++) {
        // Compute squared magnitude
        __m256d z_real_sq = _mm256_mul_pd(z_real, z_real);
        __m256d z_imag_sq = _mm256_mul_pd(z_imag, z_imag);
        __m256d magnitude_sq = _mm256_add_pd(z_real_sq, z_imag_sq);
        
        // Check escape condition
        mask = _mm256_castpd_si256(_mm256_cmp_pd(magnitude_sq, escape_sq, _CMP_LT_OQ));
        
        // Break if all points have escaped
        if (_mm256_testz_si256(mask, mask)) {
            // Add remaining iterations for points that haven't escaped
            __m256i active_mask = _mm256_cmpeq_epi64(mask, _mm256_setzero_si256());
            iterations = _mm256_add_epi64(iterations, _mm256_and_si256(active_mask, ones));
            break;
        }
        
        // Update iterations for active points
        iterations = _mm256_add_epi64(iterations, _mm256_and_si256(mask, ones));
        
        // Update z = z^2 + c using vector operations
        __m256d new_z_real = _mm256_add_pd(_mm256_sub_pd(z_real_sq, z_imag_sq), c_real);
        __m256d new_z_imag = _mm256_add_pd(_mm256_mul_pd(_mm256_set1_pd(2.0), 
                                                         _mm256_mul_pd(z_real, z_imag)), c_imag);
        
        // Only update points that haven't escaped
        z_real = _mm256_blendv_pd(new_z_real, z_real, _mm256_castsi256_pd(mask));
        z_imag = _mm256_blendv_pd(new_z_imag, z_imag, _mm256_castsi256_pd(mask));
    }
    
    // Store results
    _mm256_storeu_si256((__m256i*)iter_counts, iterations);
}
#endif

// Portable scalar version
static inline int mandelbrot_iteration(double cr, double ci) {
    double zr = 0.0, zi = 0.0;
    double zr2 = 0.0, zi2 = 0.0;
    int iter = 0;
    
    while (iter < MAX_ITER) {
        zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zr2 = zr * zr;
        zi2 = zi * zi;
        
        if (zr2 + zi2 > ESCAPE_RADIUS_SQ) {
            break;
        }
        iter++;
    }
    
    return iter;
}

// Initialize fractal parameters
void init_fractal(FractalImage *img, int size, double center_x, double center_y, double zoom) {
    img->width = size;
    img->height = size;
    
    double aspect_ratio = 1.0;
    double scale = 3.0 / zoom;
    
    img->x_min = center_x - scale / 2.0;
    img->x_max = center_x + scale / 2.0;
    img->y_min = center_y - scale / (2.0 * aspect_ratio);
    img->y_max = center_y + scale / (2.0 * aspect_ratio);
    
    // Allocate memory aligned for vector operations
    size_t total_pixels = (size_t)size * size;
    #ifdef _POSIX_C_SOURCE
    posix_memalign((void**)&img->pixels, 64, total_pixels);
    #else
    img->pixels = (uint8_t*)aligned_alloc(64, total_pixels);
    #endif
    
    if (!img->pixels) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    printf("Initialized fractal: %dx%d (%.2f MB)\n", 
           size, size, (double)total_pixels / (1024.0 * 1024.0));
    printf("Bounds: x=[%.6f, %.6f], y=[%.6f, %.6f]\n", 
           img->x_min, img->x_max, img->y_min, img->y_max);
}

// Generate Mandelbrot set with optional vectorization
void generate_mandelbrot(FractalImage *img) {
    double x_step = (img->x_max - img->x_min) / img->width;
    double y_step = (img->y_max - img->y_min) / img->height;
    
    printf("Generating with step sizes: dx=%.6e, dy=%.6e\n", x_step, y_step);
    
    #ifdef __AVX__
    printf("Using AVX vectorization\n");
    
    #pragma omp parallel for schedule(dynamic, 16)
    for (int y = 0; y < img->height; y++) {
        double ci = img->y_min + y * y_step;
        
        for (int x = 0; x < img->width; x += 4) {
            if (x + 4 <= img->width) {
                // Process 4 pixels at once with AVX
                double cr_vals[4];
                for (int i = 0; i < 4; i++) {
                    cr_vals[i] = img->x_min + (x + i) * x_step;
                }
                
                __m256d c_real = _mm256_loadu_pd(cr_vals);
                __m256d c_imag = _mm256_set1_pd(ci);
                int iter_counts[4];
                
                mandelbrot_kernel_avx(c_real, c_imag, iter_counts);
                
                for (int i = 0; i < 4; i++) {
                    int iter = iter_counts[i];
                    uint8_t color = (iter == MAX_ITER) ? 0 : (iter % 256);
                    img->pixels[y * img->width + (x + i)] = color;
                }
            } else {
                // Handle remaining pixels
                for (int i = 0; i < img->width - x; i++) {
                    double cr = img->x_min + (x + i) * x_step;
                    int iter = mandelbrot_iteration(cr, ci);
                    uint8_t color = (iter == MAX_ITER) ? 0 : (iter % 256);
                    img->pixels[y * img->width + (x + i)] = color;
                }
            }
        }
    }
    #else
    printf("Using scalar operations\n");
    
    #pragma omp parallel for schedule(dynamic, 16)
    for (int y = 0; y < img->height; y++) {
        double ci = img->y_min + y * y_step;
        
        for (int x = 0; x < img->width; x++) {
            double cr = img->x_min + x * x_step;
            int iter = mandelbrot_iteration(cr, ci);
            uint8_t color = (iter == MAX_ITER) ? 0 : (iter % 256);
            img->pixels[y * img->width + x] = color;
        }
    }
    #endif
}

// Save as PBM (Portable Bitmap) - binary format
void save_as_pbm(FractalImage *img, const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Failed to open file");
        return;
    }
    
    // Write PBM header
    fprintf(fp, "P4\n");
    fprintf(fp, "%d %d\n", img->width, img->height);
    
    // Convert grayscale to binary (threshold at 128)
    size_t row_bytes = (img->width + 7) / 8;
    uint8_t *row_buffer = (uint8_t*)malloc(row_bytes);
    
    for (int y = 0; y < img->height; y++) {
        memset(row_buffer, 0, row_bytes);
        
        for (int x = 0; x < img->width; x++) {
            uint8_t pixel = img->pixels[y * img->width + x];
            if (pixel > 128) {  // White for high iteration counts
                row_buffer[x / 8] |= (1 << (7 - (x % 8)));
            }
        }
        
        fwrite(row_buffer, 1, row_bytes, fp);
    }
    
    free(row_buffer);
    fclose(fp);
    
    printf("Saved to %s\n", filename);
}

// Save as PGM (Portable Graymap) for better visualization
void save_as_pgm(FractalImage *img, const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Failed to open file");
        return;
    }
    
    // Write PGM header
    fprintf(fp, "P5\n");
    fprintf(fp, "%d %d\n", img->width, img->height);
    fprintf(fp, "255\n");
    
    // Write pixel data
    fwrite(img->pixels, 1, img->width * img->height, fp);
    fclose(fp);
    
    printf("Saved grayscale to %s\n", filename);
}

// Clean up resources
void cleanup_fractal(FractalImage *img) {
    if (img->pixels) {
        free(img->pixels);
        img->pixels = NULL;
    }
}

int main(int argc, char *argv[]) {
    int size = 4096;  // Default size (fits in 8GB RAM)
    double zoom = 1.0;
    double center_x = -0.5;
    double center_y = 0.0;
    
    // Parse command line arguments
    if (argc > 1) size = atoi(argv[1]);
    if (argc > 2) zoom = atof(argv[2]);
    if (argc > 3) center_x = atof(argv[3]);
    if (argc > 4) center_y = atof(argv[4]);
    
    // Validate memory usage
    size_t memory_needed = (size_t)size * size;
    if (memory_needed > (7ULL * 1024 * 1024 * 1024)) {  // Leave 1GB for system
        fprintf(stderr, "Error: Requested size %dx%d requires too much memory\n", 
                size, size);
        fprintf(stderr, "Maximum recommended size for 8GB RAM: ~30000x30000\n");
        size = 4096;
    }
    
    FractalImage img;
    
    printf("Mandelbrot Set Generator\n");
    printf("System: Ubuntu 24.04.4, 8GB RAM\n");
    printf("Image size: %dx%d pixels\n", size, size);
    printf("Max iterations: %d\n", MAX_ITER);
    
    clock_t start = clock();
    
    // Initialize and generate
    init_fractal(&img, size, center_x, center_y, zoom);
    generate_mandelbrot(&img);
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Generation time: %.2f seconds\n", elapsed);
    printf("Performance: %.2f million pixels/second\n", 
           (size * size) / (elapsed * 1e6));
    
    // Save output files
    save_as_pbm(&img, "mandelbrot.pbm");
    save_as_pgm(&img, "mandelbrot.pgm");
    
    // Cleanup
    cleanup_fractal(&img);
    
    printf("Done!\n");
    printf("View with: display mandelbrot.pgm  # or use any image viewer\n");
    
    return 0;
}