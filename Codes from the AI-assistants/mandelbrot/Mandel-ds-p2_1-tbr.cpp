#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <chrono>
#include <thread>
#include <future>
#include <algorithm>
#include <cmath>

class MandelbrotSimulator {
private:
    int image_size;
    int max_iterations;
    double escape_radius;
    std::vector<std::vector<int>> iteration_counts;
    
    // Viewport parameters
    double center_x = -0.5;
    double center_y = 0.0;
    double scale = 3.0;
    
public:
    MandelbrotSimulator(int size, int max_iter = 1000, double escape_radius = 2.0)
        : image_size(size), max_iterations(max_iter), escape_radius(escape_radius) {
        iteration_counts.resize(size, std::vector<int>(size, 0));
    }
    
    // Convert pixel coordinates to complex plane coordinates
    std::complex<double> pixel_to_complex(int x, int y) {
        double real = (x - image_size/2.0) * (scale/image_size) + center_x;
        double imag = (y - image_size/2.0) * (scale/image_size) + center_y;
        return std::complex<double>(real, imag);
    }
    
    // Calculate iterations for a single point using the recurrence equation
    int calculate_point(const std::complex<double>& c) {
        std::complex<double> z(0.0, 0.0);  // z_0 = 0
        int iterations = 0;
        
        while (std::norm(z) <= escape_radius * escape_radius && 
               iterations < max_iterations) {
            z = z * z + c;  // z_(n+1) = (z_n)^2 + C
            iterations++;
        }
        
        return iterations;
    }
    
    // Process a chunk of rows (for parallelization)
    void process_rows(int start_row, int end_row) {
        for (int y = start_row; y < end_row; ++y) {
            for (int x = 0; x < image_size; ++x) {
                std::complex<double> c = pixel_to_complex(x, y);
                iteration_counts[y][x] = calculate_point(c);
            }
        }
    }
    
    // Parallel computation using std::async
    void compute_parallel() {
        int num_threads = std::thread::hardware_concurrency();
        if (num_threads == 0) num_threads = 4;  // fallback
        
        std::vector<std::future<void>> futures;
        int rows_per_thread = image_size / num_threads;
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < num_threads; ++i) {
            int start_row = i * rows_per_thread;
            int end_row = (i == num_threads - 1) ? image_size : start_row + rows_per_thread;
            
            futures.push_back(std::async(std::launch::async,
                [this, start_row, end_row]() {
                    this->process_rows(start_row, end_row);
                }));
        }
        
        // Wait for all threads to complete
        for (auto& future : futures) {
            future.wait();
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "Computation time: " << duration.count() << " ms" << std::endl;
        std::cout << "Used " << num_threads << " threads" << std::endl;
    }
    
    // Generate PBM (Portable Bitmap) image
    void generate_pbm(const std::string& filename, bool smooth = true) {
        std::ofstream pbm_file(filename, std::ios::binary);
        if (!pbm_file) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }
        
        // PBM header (P1 for ASCII, P4 for binary)
        pbm_file << "P1\n";  // ASCII PBM
        pbm_file << "# Mandelbrot Set Simulation\n";
        pbm_file << image_size << " " << image_size << "\n";
        
        // Calculate max iteration for normalization
        int max_iter = 0;
        for (const auto& row : iteration_counts) {
            max_iter = std::max(max_iter, *std::max_element(row.begin(), row.end()));
        }
        
        // Generate image data
        for (int y = 0; y < image_size; ++y) {
            for (int x = 0; x < image_size; ++x) {
                int pixel_value;
                
                if (smooth) {
                    // Smooth coloring using normalized iteration count
                    double normalized = static_cast<double>(iteration_counts[y][x]) / max_iter;
                    pixel_value = (normalized > 0.5) ? 1 : 0;
                } else {
                    // Binary: inside/outside
                    pixel_value = (iteration_counts[y][x] == max_iterations) ? 0 : 1;
                }
                
                pbm_file << pixel_value << " ";
            }
            pbm_file << "\n";
        }
        
        std::cout << "PBM file saved as: " << filename << std::endl;
        std::cout << "Image size: " << image_size << "x" << image_size << std::endl;
    }
    
    // Memory usage estimation
    void print_memory_usage() {
        size_t memory_bytes = iteration_counts.size() * iteration_counts[0].size() * sizeof(int);
        double memory_mb = static_cast<double>(memory_bytes) / (1024 * 1024);
        
        std::cout << "Memory usage for " << image_size << "x" << image_size << " grid:" << std::endl;
        std::cout << "  - " << memory_mb << " MB for iteration counts" << std::endl;
        std::cout << "  - Total available: 8 GB RAM, 256 GB SSD" << std::endl;
    }
};

int main() {
    // Configuration
    const int N = 4096;  // Image size (N x N)
    const int MAX_ITERATIONS = 1000;
    const std::string OUTPUT_FILE = "mandelbrot.pbm";
    
    std::cout << "Mandelbrot Set Simulation" << std::endl;
    std::cout << "==========================" << std::endl;
    
    // Create simulator
    MandelbrotSimulator simulator(N, MAX_ITERATIONS);
    
    // Check memory usage
    simulator.print_memory_usage();
    
    // Perform computation
    std::cout << "\nStarting computation..." << std::endl;
    simulator.compute_parallel();
    
    // Generate PBM image
    std::cout << "\nGenerating PBM image..." << std::endl;
    simulator.generate_pbm(OUTPUT_FILE, true);
    
    std::cout << "\nDone! Image saved as " << OUTPUT_FILE << std::endl;
    std::cout << "To view the image, use:" << std::endl;
    std::cout << "  - display " << OUTPUT_FILE << "  (ImageMagick)" << std::endl;
    std::cout << "  - gimp " << OUTPUT_FILE << "      (GIMP)" << std::endl;
    std::cout << "  - eog " << OUTPUT_FILE << "       (Eye of GNOME)" << std::endl;
    
    return 0;
}