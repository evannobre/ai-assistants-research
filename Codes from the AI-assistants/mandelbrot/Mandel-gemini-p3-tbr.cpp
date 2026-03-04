#include <iostream>   // For std::cout, std::cerr
#include <complex>    // Native complex number support
#include <vector>     // For managing data buffers
#include <string>     // For std::stoi
#include <algorithm>  // For std::fill

// Use standard complex double type
using Complex = std::complex<double>;

int main(int argc, char* argv[]) {
    // 1. Parse Command Line Argument N
    // Default to 200 if not provided, to allow quick testing.
    int N = (argc > 1) ? std::stoi(argv[1]) : 200;

    // 2. Output PBM Header (P4 format)
    // P4 specifies a binary bitmap.
    std::cout << "P4\n" << N << " " << N << "\n";

    // 3. Define Constants
    const int max_iter = 50;           // Standard benchmark iteration limit
    const double limit_sq = 4.0;       // Escape threshold |Z|^2 >= 4.0
    
    // Width of the byte row (N pixels / 8 bits per byte).
    // If N is not divisible by 8, we need an extra byte for the remainder.
    int byte_width = (N + 7) / 8;
    
    // Buffer to store one row of data to maximize I/O efficiency
    std::vector<uint8_t> row_buffer(byte_width);

    // 4. Iterate over rows (Imaginary axis: 1.0 down to -1.0)
    // We iterate y from 0 to N-1
    for (int y = 0; y < N; ++y) {
        
        // Map y pixel to imaginary part (Im)
        // Range [-1, 1]. Top is 1.0, Bottom is -1.0
        // Formula: 1.0 - (y * 2.0 / N)
        double civ_val = 1.0 - (y * 2.0 / N);
        
        // Clear the buffer for the new row
        std::fill(row_buffer.begin(), row_buffer.end(), 0);

        // Iterate over columns (Real axis: -1.5 to 0.5)
        for (int x = 0; x < N; ++x) {
            
            // Map x pixel to real part (Re)
            // Range [-1.5, 0.5]. Left is -1.5, Width is 2.0
            // Formula: -1.5 + (x * 2.0 / N)
            double crv_val = -1.5 + (x * 2.0 / N);

            Complex C(crv_val, civ_val);
            Complex Z(0.0, 0.0);
            
            bool is_inside = true;

            // Recurrence Loop: Z = Z^2 + C
            // Using native std::complex operations
            for (int i = 0; i < max_iter; ++i) {
                // std::norm returns |Z|^2 (squared magnitude), which is faster than abs(Z)
                if (std::norm(Z) > limit_sq) {
                    is_inside = false;
                    break;
                }
                Z = Z * Z + C;
            }

            // 5. Bit Packing
            // If inside, set the corresponding bit to 1.
            // The bit index in the byte is (7 - (x % 8)).
            if (is_inside) {
                // Calculate which byte in the row this pixel belongs to
                int byte_index = x / 8;
                // Calculate the bit offset (MSB is index 0 in PBM)
                int bit_offset = 7 - (x % 8);
                
                row_buffer[byte_index] |= (1 << bit_offset);
            }
        }

        // 6. Write the full row to standard output
        // We look like we are casting char, but cout.write handles binary data correctly.
        std::cout.write(reinterpret_cast<char*>(row_buffer.data()), byte_width);
    }

    return 0;
}