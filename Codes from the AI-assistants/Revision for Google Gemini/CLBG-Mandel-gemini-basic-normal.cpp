#include <iostream>
#include <vector>
#include <thread>
#include <cmath>
#include <cstdlib>

int main(int argc, char** argv) {
    // Default size is 200, but can be overridden by command line argument
    int N = 200;
    if (argc >= 2) {
        N = std::atoi(argv[1]);
    }

    // Number of bytes per row (padding with 0s if N is not a multiple of 8)
    int width_bytes = (N + 7) / 8;
    
    // Pre-allocate the entire image buffer
    std::vector<uint8_t> buffer(N * width_bytes, 0);

    // Determine number of threads based on hardware concurrency
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 4; // Fallback
    
    std::vector<std::thread> threads;

    // Lambda function for each thread to process a specific range of rows
    auto worker = [&](int start_y, int end_y) {
        for (int y = start_y; y < end_y; ++y) {
            double Ci = y * 2.0 / N - 1.0;
            uint8_t* row_ptr = &buffer[y * width_bytes];
            
            for (int x = 0; x < N; ++x) {
                double Cr = x * 2.0 / N - 1.5;
                
                double Zr = 0.0;
                double Zi = 0.0;
                double Tr = 0.0;
                double Ti = 0.0;
                
                int i = 0;
                // Unrolling loop slightly or keeping it standard; 
                // the limit is 50 iterations and bailout radius squared is 4.0
                for (; i < 50 && (Tr + Ti) <= 4.0; ++i) {
                    Zi = 2.0 * Zr * Zi + Ci;
                    Zr = Tr - Ti + Cr;
                    Tr = Zr * Zr;
                    Ti = Zi * Zi;
                }
                
                // If it reached 50 iterations, it's in the set. Set the bit to 1.
                // Bits are packed most-significant-bit first.
                if (Tr + Ti <= 4.0) {
                    row_ptr[x >> 3] |= (128 >> (x & 7));
                }
            }
        }
    };

    // Distribute rows evenly among threads
    int chunk_size = N / num_threads;
    for (unsigned int i = 0; i < num_threads; ++i) {
        int start_y = i * chunk_size;
        int end_y = (i == num_threads - 1) ? N : (start_y + chunk_size);
        threads.emplace_back(worker, start_y, end_y);
    }

    // Wait for all threads to finish execution
    for (auto& t : threads) {
        t.join();
    }

    // Output the PBM header
    // Use raw I/O for performance
    std::ios_base::sync_with_stdio(false);
    std::cout << "P4\n" << N << " " << N << "\n";
    
    // Write the binary data byte-by-byte
    std::cout.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());

    return 0;
}