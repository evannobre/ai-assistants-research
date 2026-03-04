#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <thread>
#include <chrono>
#include <immintrin.h>  // For AVX/SSE intrinsics

class MandelbrotGenerator {
private:
    int width;
    int height;
    int max_iterations;
    double x_min, x_max, y_min, y_max;
    
    // Calculate if a single point belongs to Mandelbrot set
    int mandelbrot_pixel(double cx, double cy) {
        double zx = 0.0;
        double zy = 0.0;
        double zx2 = 0.0;
        double zy2 = 0.0;
        
        int iteration = 0;
        while (iteration < max_iterations && (zx2 + zy2) < 4.0) {
            zy = 2.0 * zx * zy + cy;
            zx = zx2 - zy2 + cx;
            zx2 = zx * zx;
            zy2 = zy * zy;
            iteration++;
        }
        return iteration;
    }
    
    // Vectorized version using AVX (8 points simultaneously)
    void mandelbrot_avx(__m256d cx_vec, __m256d cy_vec, int* results) {
        __m256d zx = _mm256_setzero_pd();
        __m256d zy = _mm256_setzero_pd();
        __m256d zx2 = _mm256_setzero_pd();
        __m256d zy2 = _mm256_setzero_pd();
        
        __m256d four = _mm256_set1_pd(4.0);
        __m256i iterations = _mm256_setzero_si256();
        __m256i ones = _mm256_set1_epi64x(1);
        __m256i mask;
        
        for (int i = 0; i < max_iterations; i++) {
            // Check escape condition
            __m256d distance = _mm256_add_pd(zx2, zy2);
            __m256d cmp = _mm256_cmp_pd(distance, four, _CMP_LT_OQ);
            mask = _mm256_castpd_si256(cmp);
            
            // Break if all points have escaped
            if (_mm256_testz_si256(mask, mask)) break;
            
            // Increment iterations for points still in set
            iterations = _mm256_add_epi64(iterations, _mm256_and_si256(ones, mask));
            
            // Update z values: zy = 2*zx*zy + cy
            __m256d temp = _mm256_mul_pd(zx, zy);
            zy = _mm256_add_pd(_mm256_add_pd(temp, temp), cy_vec);
            
            // Update zx: zx = zx^2 - zy^2 + cx
            zx = _mm256_add_pd(_mm256_sub_pd(zx2, zy2), cx_vec);
            
            // Update squares
            zx2 = _mm256_mul_pd(zx, zx);
            zy2 = _mm256_mul_pd(zy, zy);
        }
        
        // Store results
        alignas(32) int64_t iter_arr[4];
        _mm256_store_si256((__m256i*)iter_arr, iterations);
        
        for (int i = 0; i < 4; i++) {
            results[i] = (int)iter_arr[i];
        }
    }
    
public:
    MandelbrotGenerator(int n, int max_iter = 1000) 
        : width(n), height(n), max_iterations(max_iter) {
        // Set bounds: [-1.5-i, 0.5+i]
        x_min = -1.5;
        x_max = 0.5;
        y_min = -1.0;
        y_max = 1.0;
    }
    
    // Generate Mandelbrot set using multiple threads
    std::vector<unsigned char> generate_parallel(int num_threads) {
        std::vector<unsigned char> image(width * height);
        std::vector<std::thread> threads;
        
        int rows_per_thread = height / num_threads;
        
        for (int t = 0; t < num_threads; t++) {
            int start_row = t * rows_per_thread;
            int end_row = (t == num_threads - 1) ? height : (t + 1) * rows_per_thread;
            
            threads.emplace_back([this, start_row, end_row, &image]() {
                this->generate_rows(start_row, end_row, image);
            });
        }
        
        for (auto& thread : threads) {
            thread.join();
        }
        
        return image;
    }
    
    // Generate specific rows of the image
    void generate_rows(int start_row, int end_row, std::vector<unsigned char>& image) {
        for (int y = start_row; y < end_row; y++) {
            double cy = y_min + (y_max - y_min) * y / (height - 1);
            
            // Process 4 pixels at a time using AVX
            int x = 0;
            for (; x + 3 < width; x += 4) {
                double cx_vals[4];
                for (int i = 0; i < 4; i++) {
                    cx_vals[i] = x_min + (x_max - x_min) * (x + i) / (width - 1);
                }
                
                __m256d cx_vec = _mm256_loadu_pd(cx_vals);
                __m256d cy_vec = _mm256_set1_pd(cy);
                int results[4];
                
                mandelbrot_avx(cx_vec, cy_vec, results);
                
                for (int i = 0; i < 4; i++) {
                    int idx = y * width + (x + i);
                    // Map iteration count to grayscale (0-255)
                    image[idx] = (unsigned char)((results[i] * 255) / max_iterations);
                }
            }
            
            // Process remaining pixels
            for (; x < width; x++) {
                double cx = x_min + (x_max - x_min) * x / (width - 1);
                int iterations = mandelbrot_pixel(cx, cy);
                image[y * width + x] = (unsigned char)((iterations * 255) / max_iterations);
            }
        }
    }
    
    // Write image in PBM (P4 binary) format
    void write_pbm(const std::vector<unsigned char>& image, const std::string& filename) {
        std::ofstream file(filename, std::ios::binary);
        if (!file) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }
        
        // Write PBM header (P4 for binary portable bitmap)
        file << "P4\n" << width << " " << height << "\n";
        
        // Convert grayscale to binary (1-bit) using threshold
        int row_bytes = (width + 7) / 8;  // Bytes per row, rounded up
        std::vector<unsigned char> binary_row(row_bytes);
        
        for (int y = 0; y < height; y++) {
            std::fill(binary_row.begin(), binary_row.end(), 0);
            
            for (int x = 0; x < width; x++) {
                // Threshold: black if pixel value < 128
                if (image[y * width + x] < 128) {
                    int byte_idx = x / 8;
                    int bit_idx = 7 - (x % 8);  // PBM: MSB first
                    binary_row[byte_idx] |= (1 << bit_idx);
                }
            }
            
            file.write(reinterpret_cast<char*>(binary_row.data()), row_bytes);
        }
        
        file.close();
    }
    
    // Write image in PGM (P5 binary) format for grayscale
    void write_pgm(const std::vector<unsigned char>& image, const std::string& filename) {
        std::ofstream file(filename, std::ios::binary);
        if (!file) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }
        
        // Write PGM header
        file << "P5\n" << width << " " << height << "\n255\n";
        
        // Write image data
        file.write(reinterpret_cast<const char*>(image.data()), image.size());
        
        file.close();
    }
};

int main(int argc, char* argv[]) {
    // Parse command line argument
    int n = 1000;  // Default size
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }
    
    // Performance optimization: adjust iterations based on image size
    int max_iterations = (n > 10000) ? 200 : 1000;
    
    // Determine optimal number of threads
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 4;  // Fallback
    
    std::cout << "Generating Mandelbrot set (" << n << "x" << n << ") using "
              << num_threads << " threads..." << std::endl;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Generate Mandelbrot set
    MandelbrotGenerator generator(n, max_iterations);
    auto image = generator.generate_parallel(num_threads);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::cout << "Generation time: " << duration.count() << " ms" << std::endl;
    
    // Write output
    std::string filename = "mandelbrot_" + std::to_string(n) + ".pbm";
    generator.write_pbm(image, filename);
    
    std::cout << "Output written to: " << filename << std::endl;
    
    // Memory usage report
    size_t image_memory = image.size();
    size_t total_memory = image_memory + sizeof(MandelbrotGenerator);
    std::cout << "Memory usage: " << (total_memory / (1024 * 1024)) << " MB" << std::endl;
    
    return 0;
}