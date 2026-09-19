#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <string>

// Maximum iterations for the benchmark standard
const int MAX_ITER = 50;
const double LIMIT_SQ = 4.0;

int main(int argc, char** argv) {
    // Default to 16000, override via CLI
    int N = 16000; 
    if (argc > 1) {
        N = std::stoi(argv[1]);
    }

    // P4 format packs 8 pixels per byte.
    // Calculate bytes per row, padding if N isn't a multiple of 8.
    int width_bytes = (N + 7) / 8;
    
    // Allocate a flat buffer for the entire image.
    // For N=16000, this is exactly 32,000,000 bytes (~30.5 MB).
    // This respects the 8GB RAM constraint effortlessly.
    std::vector<uint8_t> buffer(N * width_bytes, 0);
    
    // Atomic counter for dynamic thread scheduling
    std::atomic<int> current_y{0};

    auto worker = [&]() {
        int y;
        while ((y = current_y.fetch_add(1, std::memory_order_relaxed)) < N) {
            // Map y to the imaginary plane [-1, 1]
            double cy = 2.0 * y / N - 1.0;
            uint8_t* row_ptr = buffer.data() + y * width_bytes;
            
            for (int x_byte = 0; x_byte < width_bytes; ++x_byte) {
                uint8_t byte_val = 0;
                
                // Calculate 8 pixels to pack into 1 byte
                for (int bit = 0; bit < 8; ++bit) {
                    int x = x_byte * 8 + bit;
                    if (x >= N) break; // Bounds check for non-multiples of 8
                    
                    // Map x to the real plane [-1.5, 0.5]
                    double cx = 2.0 * x / N - 1.5;
                    
                    double zx = 0.0, zy = 0.0;
                    double zx2 = 0.0, zy2 = 0.0;
                    
                    int i = 0;
                    for (; i < MAX_ITER && (zx2 + zy2 <= LIMIT_SQ); ++i) {
                        zy = 2.0 * zx * zy + cy;
                        zx = zx2 - zy2 + cx;
                        zx2 = zx * zx;
                        zy2 = zy * zy;
                    }
                    
                    // If it never escaped, it's inside the set. Set the bit to 1.
                    if (i == MAX_ITER) {
                        byte_val |= (1 << (7 - bit));
                    }
                }
                row_ptr[x_byte] = byte_val;
            }
        }
    };

    // Spin up one thread per logical CPU core
    int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 4; // Fallback
    
    std::vector<std::thread> threads;
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back(worker);
    }
    for (auto& t : threads) {
        t.join();
    }

    // Optimize standard output for binary writing
    std::ios_base::sync_with_stdio(false);
    std::cout.tie(NULL);

    // Write PBM P4 header
    std::cout << "P4\n" << N << " " << N << "\n";
    // Write the raw computed bytes
    std::cout.write(reinterpret_cast<char*>(buffer.data()), buffer.size());

    return 0;
}