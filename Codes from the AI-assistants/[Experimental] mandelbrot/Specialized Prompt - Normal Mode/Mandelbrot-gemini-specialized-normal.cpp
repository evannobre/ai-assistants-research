#include <iostream>
#include <vector>
#include <fstream>
#include <cmath>
#include <algorithm>
#include <thread> // Native C++ concurrency

// --- Configuration Constants ---
const int N = 4096;               // N x N resolution
const int MAX_ITER = 256;         // Maximum iterations
const double X_MIN = -2.0;        // Real-axis start
const double X_MAX = 1.0;         // Real-axis end
const double Y_MIN = -1.5;        // Imaginary-axis start
const double Y_MAX = 1.5;         // Imaginary-axis end
const double R_SQUARED = 4.0;     // Escape radius squared (2^2)

// --- Function to calculate the escape time for a single complex point C ---
int mandelbrot_iter(double c_real, double c_imag) {
    double z_real = 0.0;
    double z_imag = 0.0;
    double z_real_sq = 0.0;
    double z_imag_sq = 0.0;
    int iter = 0;

    // The core recurrence loop, optimized to avoid repeated squaring and sqrt
    while (z_real_sq + z_imag_sq <= R_SQUARED && iter < MAX_ITER) {
        // z_next_real = z_real^2 - z_imag^2 + c_real
        // z_next_imag = 2 * z_real * z_imag + c_imag
        double z_next_real = z_real_sq - z_imag_sq + c_real;
        double z_next_imag = 2.0 * z_real * z_imag + c_imag;

        z_real = z_next_real;
        z_imag = z_next_imag;

        // Recalculate squares for the next iteration (avoid power function)
        z_real_sq = z_real * z_real;
        z_imag_sq = z_imag * z_imag;
        
        iter++;
    }
    return iter;
}

// --- Worker function for multithreading (processes a range of rows) ---
void calculate_rows(std::vector<unsigned char>& image_data, int start_row, int end_row) {
    const double DX = (X_MAX - X_MIN) / N;
    const double DY = (Y_MAX - Y_MIN) / N;

    for (int y = start_row; y < end_row; ++y) {
        double c_imag = Y_MIN + y * DY;
        for (int x = 0; x < N; ++x) {
            double c_real = X_MIN + x * DX;
            int iter = mandelbrot_iter(c_real, c_imag);

            // Grayscale mapping: iter count is the pixel value. 
            // Clamp to unsigned char range (0-255).
            unsigned char color = (unsigned char)std::min(iter, 255); 
            
            // Store the result. Image_data is a flat array, row by row.
            image_data[y * N + x] = color;
        }
    }
}

// --- Main execution ---
int main() {
    // 1. Initialize data buffer
    // Using unsigned char array for 1 byte per pixel (P5 PGM requirement)
    // Check for large allocation is prudent, though 1GB is safe on 8GB machine.
    std::vector<unsigned char> image_data(N * N);

    // 2. Determine thread count and division of work
    const int num_threads = std::thread::hardware_concurrency();
    const int rows_per_thread = N / num_threads;
    std::vector<std::thread> threads;

    // 3. Launch threads for parallel computation
    for (int i = 0; i < num_threads; ++i) {
        int start_row = i * rows_per_thread;
        int end_row = (i == num_threads - 1) ? N : (i + 1) * rows_per_thread;
        
        // Pass the image data buffer and the row range for this thread
        threads.emplace_back(calculate_rows, std::ref(image_data), start_row, end_row);
    }

    // 4. Wait for all threads to complete
    for (auto& t : threads) {
        t.join();
    }

    // 5. Write PGM file using low-level C I/O for speed (native to the OS/compiler)
    const char* filename = "mandelbrot.pgm";
    FILE* fp = fopen(filename, "wb");

    if (!fp) {
        std::cerr << "Error: Could not open file for writing." << std::endl;
        return 1;
    }

    // PGM Header (P5: binary graymap)
    fprintf(fp, "P5\n%d %d\n255\n", N, N);

    // Write the raw pixel data
    fwrite(image_data.data(), 1, N * N, fp);

    fclose(fp);
    std::cout << "Mandelbrot image successfully generated to " << filename << std::endl;

    return 0;
}