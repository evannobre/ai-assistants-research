#include <fstream>
#include <complex>
#include <vector>

void mandelbrot(int N, const std::string& filename) {
    std::ofstream file(filename, std::ios::binary);
    if (!file) return;
    
    // PBM header
    file << "P4\n" << N << " " << N << "\n";
    
    const double x_min = -1.5, x_max = 0.5;
    const double y_min = -1.0, y_max = 1.0;
    const double x_step = (x_max - x_min) / (N - 1);
    const double y_step = (y_max - y_min) / (N - 1);
    
    const int max_iter = 1000;
    
    for (int y = 0; y < N; ++y) {
        const double c_imag = y_min + y * y_step;
        std::vector<unsigned char> row_bytes((N + 7) / 8, 0);
        
        for (int x = 0; x < N; ++x) {
            const double c_real = x_min + x * x_step;
            std::complex<double> z(0, 0);
            std::complex<double> c(c_real, c_imag);
            int iter = 0;
            
            // Quadratic recurrence
            while (iter < max_iter) {
                z = z * z + c;
                if (std::norm(z) > 4.0) break;
                ++iter;
            }
            
            if (iter == max_iter) {
                // Set bit for point in Mandelbrot set
                const int byte_index = x / 8;
                const int bit_index = 7 - (x % 8);
                row_bytes[byte_index] |= (1 << bit_index);
            }
        }
        
        file.write(reinterpret_cast<const char*>(row_bytes.data()), row_bytes.size());
    }
}

int main(int argc, char* argv[]) {
    int N = 16000;
    if (argc > 1) {
        N = std::atoi(argv[1]);
    }
    
    mandelbrot(N, "mandelbrot.pbm");
    return 0;
}