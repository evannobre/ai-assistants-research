#include <iostream>
#include <fstream>
#include <complex>

void generate_mandelbrot(int N, int max_iter, const std::string& filename) {
    std::ofstream pbm(filename);
    pbm << "P1\n" << N << " " << N << "\n";
    
    for (int y = 0; y < N; ++y) {
        for (int x = 0; x < N; ++x) {
            double real = (x - N/2.0) * 4.0/N;
            double imag = (y - N/2.0) * 4.0/N;
            
            std::complex<double> c(real, imag);
            std::complex<double> z(0, 0);
            int iter = 0;
            
            while (std::norm(z) <= 4.0 && iter < max_iter) {
                z = z * z + c;
                ++iter;
            }
            
            pbm << (iter == max_iter ? "0 " : "1 ");
        }
        pbm << "\n";
    }
}

int main() {
    generate_mandelbrot(2048, 256, "simple_mandelbrot.pbm");
    return 0;
}