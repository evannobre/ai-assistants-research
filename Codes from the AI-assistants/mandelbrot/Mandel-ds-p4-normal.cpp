#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <immintrin.h>
#include <memory>
#include <thread>
#include <vector>

// Configuration constants
constexpr double X_MIN = -2.0;
constexpr double X_MAX = 0.5;
constexpr double Y_MIN = -1.25;
constexpr double Y_MAX = 1.25;
constexpr int MAX_ITER = 1000;
constexpr double ESCAPE_RADIUS = 2.0;
constexpr double ESCAPE_RADIUS_SQ = ESCAPE_RADIUS * ESCAPE_RADIUS;

class MandelbrotRenderer {
private:
    int size_;
    std::unique_ptr<uint8_t[]> pixels_;
    int thread_count_;

public:
    MandelbrotRenderer(int size) 
        : size_(size), 
          pixels_(std::make_unique<uint8_t[]>(size * size)),
          thread_count_(std::thread::hardware_concurrency()) {
        if (thread_count_ == 0) thread_count_ = 1;
    }

    // AVX-512 optimized Mandelbrot calculation for 8 pixels at once
    void compute_block_avx512(int start_x, int end_x, int start_y, int end_y) {
        const double x_scale = (X_MAX - X_MIN) / (size_ - 1);
        const double y_scale = (Y_MAX - Y_MIN) / (size_ - 1);
        
        __m512d escape_radius_sq = _mm512_set1_pd(ESCAPE_RADIUS_SQ);
        __m512i max_iter_vec = _mm512_set1_epi64(MAX_ITER);
        __m512i ones = _mm512_set1_epi64(1);
        
        for (int y = start_y; y < end_y; y++) {
            double y0 = Y_MIN + y * y_scale;
            __m512d y0_vec = _mm512_set1_pd(y0);
            
            for (int x = start_x; x < end_x; x += 8) {
                if (x + 8 > end_x) break;
                
                // Calculate x coordinates for 8 pixels
                std::array<double, 8> x_vals;
                for (int i = 0; i < 8; i++) {
                    x_vals[i] = X_MIN + (x + i) * x_scale;
                }
                __m512d x0_vec = _mm512_loadu_pd(x_vals.data());
                
                // Initialize z = 0
                __m512d zx = _mm512_setzero_pd();
                __m512d zy = _mm512_setzero_pd();
                __m512i iteration = _mm512_setzero_si512();
                __mmask8 mask = _mm512_cmp_pd_mask(zx, zx, _CMP_EQ_OQ); // All true mask
                
                for (int n = 0; n < MAX_ITER; n++) {
                    // Check if any pixels still need processing
                    if (mask == 0) break;
                    
                    // Calculate zx^2 and zy^2
                    __m512d zx2 = _mm512_mul_pd(zx, zx);
                    __m512d zy2 = _mm512_mul_pd(zy, zy);
                    
                    // Check escape condition: zx^2 + zy^2 > ESCAPE_RADIUS_SQ
                    __m512d r2 = _mm512_add_pd(zx2, zy2);
                    __mmask8 escaped = _mm512_cmp_pd_mask(r2, escape_radius_sq, _CMP_GT_OQ);
                    
                    // Update mask for next iteration
                    mask &= ~escaped;
                    
                    // Update iteration count for escaped pixels
                    __m512i inc_mask = _mm512_maskz_set1_epi64(escaped, 1);
                    iteration = _mm512_add_epi64(iteration, 
                        _mm512_and_si512(inc_mask, _mm512_castpd_si512(_mm512_mask_blend_pd(mask, ones, _mm512_setzero_pd()))));
                    
                    // Calculate next z values: z = z^2 + c
                    // zx_new = zx^2 - zy^2 + x0
                    // zy_new = 2*zx*zy + y0
                    __m512d zx_new = _mm512_add_pd(_mm512_sub_pd(zx2, zy2), x0_vec);
                    __m512d zy_new = _mm512_add_pd(_mm512_mul_pd(_mm512_set1_pd(2.0), 
                        _mm512_mul_pd(zx, zy)), y0_vec);
                    
                    // Apply mask to update only non-escaped pixels
                    zx = _mm512_mask_blend_pd(mask, zx, zx_new);
                    zy = _mm512_mask_blend_pd(mask, zy, zy_new);
                    
                    // Increment iteration for non-escaped pixels
                    __m512i not_escaped_mask = _mm512_maskz_set1_epi64(mask, 1);
                    iteration = _mm512_add_epi64(iteration, not_escaped_mask);
                }
                
                // Store results
                alignas(64) std::array<int64_t, 8> iter_results;
                _mm512_store_epi64(iter_results.data(), iteration);
                
                for (int i = 0; i < 8; i++) {
                    int idx = (y * size_) + (x + i);
                    pixels_[idx] = static_cast<uint8_t>((iter_results[i] * 255) / MAX_ITER);
                }
            }
        }
    }

    // Fallback SSE2 implementation for non-AVX512 systems
    void compute_block_sse2(int start_x, int end_x, int start_y, int end_y) {
        const double x_scale = (X_MAX - X_MIN) / (size_ - 1);
        const double y_scale = (Y_MAX - Y_MIN) / (size_ - 1);
        
        for (int y = start_y; y < end_y; y++) {
            double y0 = Y_MIN + y * y_scale;
            
            for (int x = start_x; x < end_x; x++) {
                double x0 = X_MIN + x * x_scale;
                
                double zx = 0.0;
                double zy = 0.0;
                int iteration = 0;
                
                while (iteration < MAX_ITER) {
                    double zx2 = zx * zx;
                    double zy2 = zy * zy;
                    
                    if (zx2 + zy2 > ESCAPE_RADIUS_SQ) {
                        break;
                    }
                    
                    double zx_new = zx2 - zy2 + x0;
                    double zy_new = 2.0 * zx * zy + y0;
                    
                    zx = zx_new;
                    zy = zy_new;
                    iteration++;
                }
                
                pixels_[y * size_ + x] = static_cast<uint8_t>((iteration * 255) / MAX_ITER);
            }
        }
    }

    void render() {
        std::vector<std::thread> threads;
        int rows_per_thread = size_ / thread_count_;
        
        auto worker = [this](int thread_id, bool use_avx512) {
            int start_y = thread_id * (size_ / thread_count_);
            int end_y = (thread_id == thread_count_ - 1) ? size_ : start_y + (size_ / thread_count_);
            
            if (use_avx512) {
                compute_block_avx512(0, size_, start_y, end_y);
            } else {
                compute_block_sse2(0, size_, start_y, end_y);
            }
        };
        
        // Check for AVX-512 support
        bool has_avx512 = false;
        #ifdef __AVX512F__
        has_avx512 = true;
        #endif
        
        // Launch threads
        for (int i = 0; i < thread_count_; i++) {
            threads.emplace_back(worker, i, has_avx512);
        }
        
        // Wait for all threads
        for (auto& t : threads) {
            t.join();
        }
    }

    void write_pbm(const char* filename) {
        FILE* fp = fopen(filename, "wb");
        if (!fp) {
            perror("Failed to open file");
            return;
        }
        
        // Write PBM header
        fprintf(fp, "P5\n%d %d\n255\n", size_, size_);
        
        // Write pixel data
        fwrite(pixels_.get(), 1, size_ * size_, fp);
        
        fclose(fp);
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        fprintf(stderr, "Example: %s 16000\n", argv[0]);
        return 1;
    }
    
    int size = atoi(argv[1]);
    if (size <= 0) {
        fprintf(stderr, "Size must be positive integer\n");
        return 1;
    }
    
    // Check memory requirements (8GB max)
    size_t required_memory = size * size; // 1 byte per pixel
    if (required_memory > 8ULL * 1024 * 1024 * 1024) {
        fprintf(stderr, "Error: Required memory (%zu bytes) exceeds 8GB limit\n", 
                required_memory);
        return 1;
    }
    
    printf("Rendering Mandelbrot set %dx%d...\n", size, size);
    
    MandelbrotRenderer renderer(size);
    renderer.render();
    renderer.write_pbm("mandelbrot.pbm");
    
    printf("Done. Output written to mandelbrot.pbm\n");
    
    return 0;
}