/*
 * Mandelbrot Set Generator (C++17)
 * Implements z_{n+1} = z_n^2 + C
 * Output: Portable Bitmap Format (PBM) to stdout
 */

#include <iostream>
#include <vector>
#include <complex>
#include <thread>
#include <future>
#include <algorithm>
#include <cstdint>

// Configuration Constants
const int MAX_ITERATIONS = 50;
const double LIMIT_SQUARED = 4.0;

// Function to calculate the byte for a specific group of 8 pixels
// y: The current row (imaginary part)
// N: The total size of the bitmap
uint8_t compute_byte(int x_start, int y, int N) {
    uint8_t byte_val = 0;
    
    // We process 8 pixels at a time to form 1 byte
    for (int i = 0; i < 8; ++i) {
        int x = x_start + i;
        
        // If we are past the image width, pad with 0 (though N usually aligns)
        if (x >= N) {
            // PBM standard requires padding the last byte if width is not divisible by 8
            // but we leave remaining bits 0.
            continue; 
        }

        // Map coordinates to the complex plane
        // Real part (Cr): [-1.5, 0.5]
        // Imaginary part (Ci): [-1.0, 1.0] (Wait, input says [-1.5-i, 0.5+i])
        // That implies Imaginary range is -1 to +1.
        
        double Cr = (double)x * 2.0 / N - 1.5;
        double Ci = (double)y * 2.0 / N - 1.0;
        
        double Zr = 0.0;
        double Zi = 0.0;
        double Tr = 0.0;
        double Ti = 0.0;
        
        bool is_in_set = true;

        for (int k = 0; k < MAX_ITERATIONS; ++k) {
            // z = z^2 + c
            // (Zr + Zi*i)^2 = (Zr^2 - Zi^2) + (2*Zr*Zi)*i
            Zi = 2.0 * Zr * Zi + Ci;
            Zr = Tr - Ti + Cr;
            
            Tr = Zr * Zr;
            Ti = Zi * Zi;
            
            if (Tr + Ti > LIMIT_SQUARED) {
                is_in_set = false;
                break;
            }
        }

        // PBM Format: 1 = Black (in set), 0 = White (not in set)
        // We set the bit at the correct position (7 - i)
        if (is_in_set) {
            byte_val |= (1 << (7 - i));
        }
    }
    return byte_val;
}

// Worker function to process a chunk of rows
void process_rows(int start_row, int end_row, int N, int width_in_bytes, std::vector<uint8_t>& buffer) {
    for (int y = start_row; y < end_row; ++y) {
        int row_offset = y * width_in_bytes;
        for (int x = 0; x < N; x += 8) {
            // Calculate byte index relative to the start of the buffer
            int byte_index = row_offset + (x / 8);
            buffer[byte_index] = compute_byte(x, y, N);
        }
    }
}

int main(int argc, char* argv[]) {
    // 1. Parse Command Line Argument
    int N = 200; // Default
    if (argc > 1) {
        N = std::atoi(argv[1]);
    }

    // 2. Setup PBM Header
    // P4 defines binary bitmap. Width Height follows.
    std::cout << "P4\n" << N << " " << N << "\n";

    // 3. Memory Allocation
    // Width in bytes: N pixels / 8 bits per byte. 
    // If N is not divisible by 8, we need an extra byte.
    int width_in_bytes = (N + 7) / 8;
    int total_bytes = width_in_bytes * N;
    
    // Allocate the contiguous memory block.
    // 32MB for N=16000. Fits easily in 8GB RAM.
    std::vector<uint8_t> buffer(total_bytes);

    // 4. Concurrency Setup
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 4; // Fallback
    
    std::vector<std::future<void>> futures;
    int rows_per_thread = N / num_threads;
    
    // 5. Dispatch Threads
    for (unsigned int i = 0; i < num_threads; ++i) {
        int start_row = i * rows_per_thread;
        int end_row = (i == num_threads - 1) ? N : start_row + rows_per_thread;
        
        futures.push_back(std::async(std::launch::async, process_rows, 
            start_row, end_row, N, width_in_bytes, std::ref(buffer)));
    }

    // 6. Synchronization
    // Wait for all threads to finish processing
    for (auto& f : futures) {
        f.get();
    }

    // 7. Binary Output
    // Write the entire buffer to stdout in one go for maximum I/O performance
    std::cout.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());

    return 0;
}