#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <cstdlib>

// (i) computes the infinite matrix element A(i, j)
inline double eval_A(int i, int j) {
    return 1.0 / (((i + j) * (i + j + 1) / 2.0) + i + 1.0);
}

// (ii) computes A * v
std::vector<double> eval_A_times_v(const std::vector<double>& v) {
    int n = v.size();
    std::vector<double> u(n, 0.0);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            u[i] += eval_A(i, j) * v[j];
        }
    }
    return u;
}

// (iii) computes A^T * v
std::vector<double> eval_At_times_v(const std::vector<double>& v) {
    int n = v.size();
    std::vector<double> u(n, 0.0);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            u[i] += eval_A(j, i) * v[j];
        }
    }
    return u;
}

// (iv) computes A^T * (A * v)
std::vector<double> eval_AtA_times_v(const std::vector<double>& v) {
    return eval_At_times_v(eval_A_times_v(v));
}

int main(int argc, char** argv) {
    // Capture command-line argument for matrix size
    int n = 100;
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }

    std::vector<double> u(n, 1.0);
    std::vector<double> v(n, 0.0);

    // Power method: 10 iterations
    for (int i = 0; i < 10; ++i) {
        v = eval_AtA_times_v(u);
        u = eval_AtA_times_v(v);
    }

    // Compute final spectral norm elements
    double vBv = 0.0, vv = 0.0;
    for (int i = 0; i < n; ++i) {
        vBv += u[i] * v[i];
        vv += v[i] * v[i];
    }

    // Output precise to 9 decimal places
    std::cout << std::fixed << std::setprecision(9) << std::sqrt(vBv / vv) << '\n';
    return 0;
}