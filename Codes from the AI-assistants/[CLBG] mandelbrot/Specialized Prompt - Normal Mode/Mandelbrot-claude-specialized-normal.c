#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <immintrin.h>

#define MAX_ITER 50

// SIMD-optimized Mandelbrot calculation for 8 pixels at once using AVX2
static inline __m256d mandelbrot_calc_avx2(__m256d cr, __m256d ci) {
    __m256d zr = _mm256_setzero_pd();
    __m256d zi = _mm256_setzero_pd();
    __m256d mask = _mm256_setzero_pd();
    __m256d one = _mm256_set1_pd(1.0);
    __m256d four = _mm256_set1_pd(4.0);
    
    for (int i = 0; i < MAX_ITER; i++) {
        // zr2 = zr * zr
        __m256d zr2 = _mm256_mul_pd(zr, zr);
        // zi2 = zi * zi
        __m256d zi2 = _mm256_mul_pd(zi, zi);
        
        // Check if zr2 + zi2 > 4.0
        __m256d mag = _mm256_add_pd(zr2, zi2);
        __m256d cmp = _mm256_cmp_pd(mag, four, _CMP_LE_OQ);
        
        // If all points escaped, break early
        if (_mm256_testz_pd(cmp, cmp)) break;
        
        // Accumulate mask where points haven't escaped
        mask = _mm256_add_pd(mask, _mm256_and_pd(cmp, one));
        
        // zi_new = 2 * zr * zi + ci
        __m256d zi_new = _mm256_mul_pd(zr, zi);
        zi_new = _mm256_add_pd(zi_new, zi_new);
        zi_new = _mm256_add_pd(zi_new, ci);
        
        // zr_new = zr2 - zi2 + cr
        __m256d zr_new = _mm256_sub_pd(zr2, zi2);
        zr_new = _mm256_add_pd(zr_new, cr);
        
        zr = zr_new;
        zi = zi_new;
    }
    
    return mask;
}

void calculate_mandelbrot(uint8_t *bitmap, int n) {
    double inv_n = 2.0 / n;
    int bytes_per_row = (n + 7) / 8;
    
    // Process rows in parallel would go here with OpenMP,
    // but keeping it simple with native C
    for (int y = 0; y < n; y++) {
        double ci = (y * inv_n) - 1.0;
        int byte_idx = y * bytes_per_row;
        
        for (int x = 0; x < n; x += 8) {
            // Process 4 pixels at a time with AVX2 (double precision)
            double cr[4];
            double ci_arr[4];
            
            for (int i = 0; i < 4 && (x + i) < n; i++) {
                cr[i] = ((x + i) * inv_n) - 1.5;
                ci_arr[i] = ci;
            }
            
            __m256d cr_vec = _mm256_loadu_pd(cr);
            __m256d ci_vec = _mm256_loadu_pd(ci_arr);
            __m256d result1 = mandelbrot_calc_avx2(cr_vec, ci_vec);
            
            // Second batch of 4 pixels
            for (int i = 0; i < 4 && (x + 4 + i) < n; i++) {
                cr[i] = ((x + 4 + i) * inv_n) - 1.5;
                ci_arr[i] = ci;
            }
            
            cr_vec = _mm256_loadu_pd(cr);
            ci_vec = _mm256_loadu_pd(ci_arr);
            __m256d result2 = mandelbrot_calc_avx2(cr_vec, ci_vec);
            
            // Convert results to bits
            double res1[4], res2[4];
            _mm256_storeu_pd(res1, result1);
            _mm256_storeu_pd(res2, result2);
            
            uint8_t byte_val = 0;
            for (int i = 0; i < 8 && (x + i) < n; i++) {
                double val = (i < 4) ? res1[i] : res2[i - 4];
                if (val >= MAX_ITER) {
                    byte_val |= (0x80 >> (i % 8));
                }
            }
            
            bitmap[byte_idx + (x / 8)] = byte_val;
        }
    }
}

void write_pbm(const char *filename, uint8_t *bitmap, int n) {
    FILE *f = fopen(filename, "wb");
    if (!f) {
        perror("Failed to open output file");
        exit(1);
    }
    
    // Write PBM header
    fprintf(f, "P4\n%d %d\n", n, n);
    
    // Write bitmap data
    int bytes_per_row = (n + 7) / 8;
    size_t total_bytes = bytes_per_row * n;
    
    if (fwrite(bitmap, 1, total_bytes, f) != total_bytes) {
        perror("Failed to write bitmap data");
        fclose(f);
        exit(1);
    }
    
    fclose(f);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        return 1;
    }
    
    int n = atoi(argv[1]);
    if (n <= 0 || n > 65536) {
        fprintf(stderr, "Size must be between 1 and 65536\n");
        return 1;
    }
    
    // Calculate memory requirements
    int bytes_per_row = (n + 7) / 8;
    size_t total_bytes = (size_t)bytes_per_row * n;
    
    // Check memory constraints (conservative estimate)
    if (total_bytes > 2ULL * 1024 * 1024 * 1024) { // 2GB limit
        fprintf(stderr, "Image size too large for available memory\n");
        return 1;
    }
    
    // Allocate bitmap
    uint8_t *bitmap = (uint8_t *)calloc(total_bytes, 1);
    if (!bitmap) {
        perror("Failed to allocate bitmap memory");
        return 1;
    }
    
    // Calculate Mandelbrot set
    calculate_mandelbrot(bitmap, n);
    
    // Write to stdout in PBM format
    printf("P4\n%d %d\n", n, n);
    fwrite(bitmap, 1, total_bytes, stdout);
    
    free(bitmap);
    return 0;
}