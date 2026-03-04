#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <algorithm>
#include <iomanip>
#include <random>

void matvec_A(int D, const double* x, double* y) {
    std::fill(y, y + D, 0.0);
    for (long long k = 1; k <= 2 * static_cast<long long>(D) - 1; ++k) {
        int i_low = std::max(0, static_cast<int>(k - D));
        int i_high = std::min(D - 1, static_cast<int>(k - 1));
        double denom_base = (k - 1) * k / 2.0;
        for (int i = i_low; i <= i_high; ++i) {
            int j = k - i - 1;
            double denom = denom_base + (i + 1);
            y[i] += (1.0 / denom) * x[j];
        }
    }
}

void matvec_AT(int D, const double* x, double* y) {
    std::fill(y, y + D, 0.0);
    for (long long k = 1; k <= 2 * static_cast<long long>(D) - 1; ++k) {
        int j_low = std::max(0, static_cast<int>(k - D));
        int j_high = std::min(D - 1, static_cast<int>(k - 1));
        double denom_base = (k - 1) * k / 2.0;
        for (int j = j_low; j <= j_high; ++j) {
            int i = k - j - 1;
            double denom = denom_base + (j + 1);
            y[i] += (1.0 / denom) * x[j];
        }
    }
}

double power_method(int D, double tol, int max_iter) {
    std::vector<double> x(D);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> dist(-1.0, 1.0);
    double norm_x = 0.0;
    for (int i = 0; i < D; ++i) {
        x[i] = dist(gen);
        norm_x += x[i] * x[i];
    }
    norm_x = std::sqrt(norm_x);
    for (int i = 0; i < D; ++i) {
        x[i] /= norm_x;
    }

    std::vector<double> temp(D);
    std::vector<double> y(D);
    double lambda_prev = 0.0;

    for (int iter = 0; iter < max_iter; ++iter) {
        matvec_A(D, x.data(), temp.data());
        matvec_AT(D, temp.data(), y.data());

        double dot_product = 0.0;
        double norm_y = 0.0;
        for (int i = 0; i < D; ++i) {
            dot_product += x[i] * y[i];
            norm_y += y[i] * y[i];
        }
        norm_y = std::sqrt(norm_y);
        double lambda = dot_product;

        if (iter > 0 && std::abs(lambda - lambda_prev) < tol * std::abs(lambda)) {
            break;
        }
        lambda_prev = lambda;

        if (norm_y > 0) {
            for (int i = 0; i < D; ++i) {
                x[i] = y[i] / norm_y;
            }
        } else {
            break;
        }
    }
    return lambda_prev;
}

int main() {
    double tol_dim = 1e-8;
    int max_iter_power = 1000;
    int D = 100;
    double spectral_norm_prev = 0.0;

    while (true) {
        std::cout << "Computing for D = " << D << std::endl;
        double lambda = power_method(D, 1e-10, max_iter_power);
        double spectral_norm = std::sqrt(lambda);
        std::cout << "Spectral norm (D=" << D << ") = " << std::setprecision(15) << spectral_norm << std::endl;

        if (D > 100 && std::abs(spectral_norm - spectral_norm_prev) < tol_dim) {
            std::cout << "Converged with tolerance " << tol_dim << "." << std::endl;
            break;
        }

        spectral_norm_prev = spectral_norm;
        D *= 2;

        if (D > 1000000) {
            std::cout << "D exceeds maximum limit (1,000,000). Stopping." << std::endl;
            break;
        }
    }

    std::cout << "Final spectral norm: " << spectral_norm_prev << std::endl;
    return 0;
}