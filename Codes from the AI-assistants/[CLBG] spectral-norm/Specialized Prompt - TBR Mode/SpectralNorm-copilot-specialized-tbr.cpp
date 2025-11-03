// (i) Infinite-matrix entry A(i,j)
static inline double A(int i, int j) {
    // zero-based indexing
    int ij = i + j;
    return 1.0 / ((ij*(ij + 1) >> 1) + i + 1);
}

// (ii) out = A * v
void multiplyAv(const std::vector<double>& v, std::vector<double>& out) {
    int n = v.size();
    std::fill(out.begin(), out.end(), 0.0);
    for (int i = 0; i < n; ++i) {
        double sum = 0.0;
        for (int j = 0; j < n; ++j)
            sum += A(i, j) * v[j];
        out[i] = sum;
    }
}

// (iii) out = A^T * v
void multiplyAtv(const std::vector<double>& v, std::vector<double>& out) {
    int n = v.size();
    std::fill(out.begin(), out.end(), 0.0);
    for (int i = 0; i < n; ++i) {
        double sum = 0.0;
        for (int j = 0; j < n; ++j)
            sum += A(j, i) * v[j];
        out[i] = sum;
    }
}

// (iv) out = A^T * (A * v)
void multiplyAtAv(const std::vector<double>& v, std::vector<double>& out) {
    static std::vector<double> tmp;
    int n = v.size();
    tmp.assign(n, 0.0);
    multiplyAv(v, tmp);
    multiplyAtv(tmp, out);
}

#include <vector>
#include <cmath>
#include <cstdio>
#include <cstdlib>

// Declare the four core functions here...

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? std::atoi(argv[1]) : 5500;
    std::vector<double> u(n, 1.0), v(n, 1.0);
    
    // Power iterations
    for (int iter = 0; iter < 10; ++iter) {
        multiplyAtAv(u, v);
        multiplyAtAv(v, u);
    }
    
    // Compute Rayleigh quotient
    double vBv = 0.0, vv = 0.0;
    for (int i = 0; i < n; ++i) {
        vBv += u[i] * v[i];
        vv  += v[i] * v[i];
    }
    double norm = std::sqrt(vBv / vv);
    
    std::printf("%.9f\n", norm);
    return 0;
}
