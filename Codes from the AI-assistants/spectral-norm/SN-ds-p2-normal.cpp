#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <chrono>
#include <iomanip>
#include <algorithm>

class InfiniteMatrix {
private:
    // Get denominator for element (i,j) (1-indexed)
    static long long get_denominator(int i, int j) {
        long long k = i + j - 1;  // anti-diagonal number
        long long start_denom = 1 + k * (k - 1) / 2;
        return start_denom + (i - 1);
    }

public:
    // Compute y = A * x for n×n submatrix
    static void matvec(const std::vector<double>& x, std::vector<double>& y, int n) {
        std::fill(y.begin(), y.end(), 0.0);
        
        for (int i = 1; i <= n; ++i) {
            double sum = 0.0;
            for (int j = 1; j <= n; ++j) {
                sum += x[j-1] / get_denominator(i, j);
            }
            y[i-1] = sum;
        }
    }
    
    // Compute y = A^T * x for n×n submatrix
    static void matvec_transpose(const std::vector<double>& x, std::vector<double>& y, int n) {
        std::fill(y.begin(), y.end(), 0.0);
        
        for (int j = 1; j <= n; ++j) {
            double sum = 0.0;
            for (int i = 1; i <= n; ++i) {
                sum += x[i-1] / get_denominator(i, j);
            }
            y[j-1] = sum;
        }
    }
    
    // Power iteration for spectral norm
    static double power_iteration(int n, int max_iter = 1000, double tol = 1e-12) {
        // Initialize random vector
        std::vector<double> v(n), u(n), v_new(n);
        std::random_device rd;
        std::mt19937 gen(rd());
        std::normal_distribution<> dist(0.0, 1.0);
        
        double norm = 0.0;
        for (int i = 0; i < n; ++i) {
            v[i] = dist(gen);
            norm += v[i] * v[i];
        }
        norm = std::sqrt(norm);
        for (int i = 0; i < n; ++i) {
            v[i] /= norm;
        }
        
        double sigma = 0.0;
        double sigma_old = 0.0;
        
        for (int iter = 0; iter < max_iter; ++iter) {
            // u = A * v
            matvec(v, u, n);
            
            // Normalize u
            norm = 0.0;
            for (int i = 0; i < n; ++i) norm += u[i] * u[i];
            norm = std::sqrt(norm);
            if (norm < 1e-15) {
                // Regenerate random vector
                norm = 0.0;
                for (int i = 0; i < n; ++i) {
                    u[i] = dist(gen);
                    norm += u[i] * u[i];
                }
                norm = std::sqrt(norm);
            }
            for (int i = 0; i < n; ++i) u[i] /= norm;
            
            // v_new = A^T * u
            matvec_transpose(u, v_new, n);
            
            // Normalize v_new
            norm = 0.0;
            for (int i = 0; i < n; ++i) norm += v_new[i] * v_new[i];
            norm = std::sqrt(norm);
            if (norm < 1e-15) {
                norm = 0.0;
                for (int i = 0; i < n; ++i) {
                    v_new[i] = dist(gen);
                    norm += v_new[i] * v_new[i];
                }
                norm = std::sqrt(norm);
            }
            for (int i = 0; i < n; ++i) v_new[i] /= norm;
            
            // Estimate singular value
            matvec(v_new, u, n);
            sigma_old = sigma;
            sigma = 0.0;
            for (int i = 0; i < n; ++i) sigma += u[i] * u[i];
            sigma = std::sqrt(sigma);
            
            // Check convergence
            if (std::abs(sigma - sigma_old) < tol * sigma) {
                return sigma;
            }
            
            v.swap(v_new);
        }
        
        std::cerr << "Warning: Power iteration did not converge in " 
                  << max_iter << " iterations\n";
        return sigma;
    }
};

int main() {
    std::vector<int> dimensions = {10, 20, 50, 100, 200, 500, 1000, 2000};
    
    std::cout << std::setprecision(10);
    std::cout << "Spectral Norm of Infinite Matrix\n";
    std::cout << "================================\n\n";
    
    for (int n : dimensions) {
        auto start = std::chrono::high_resolution_clock::now();
        
        double sigma = InfiniteMatrix::power_iteration(n);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration<double>(end - start).count();
        
        std::cout << "n = " << std::setw(4) << n 
                  << ": σ = " << std::setw(12) << sigma
                  << ", time = " << std::setw(8) << duration << "s\n";
        
        // Memory estimate
        double memory_mb = (n * 8 * 2) / (1024.0 * 1024.0);
        if (memory_mb > 50) {
            std::cout << "       (Memory: " << std::setw(6) << memory_mb << " MB)\n";
        }
    }
    
    return 0;
}