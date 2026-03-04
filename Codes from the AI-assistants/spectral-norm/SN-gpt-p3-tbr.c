// Spectral Norm (infinite matrix / Hilbert-like) using Power Method
// Build:  cc -O3 -march=native -std=c11 spectralnorm.c -o spectralnorm -lm
// Run:    ./spectralnorm 5500

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

// (i) Infinite matrix element A(i, j), using 0-based indices in code.
// Math definition is 1-based; equivalently:
//
// A(i,j) = 1 / ( t + i + 1 )  where t = ( (i+j) * (i+j+1) / 2 )
//
static inline double A_ij(int i, int j) {
    int ij = i + j;
    int t  = (ij * (ij + 1)) / 2;
    return 1.0 / (double)(t + i + 1);
}

// (ii) Compute out = A * v
static void A_times_v(int n, const double *v, double *out) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A_ij(i, j) * v[j];
        }
        out[i] = sum;
    }
}

// (iii) Compute out = A^T * v
static void At_times_v(int n, const double *v, double *out) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A_ij(j, i) * v[j];
        }
        out[i] = sum;
    }
}

// (iv) Compute out = A^T * (A * v)
static void AtA_times_v(int n, const double *v, double *out, double *tmp) {
    A_times_v(n, v, tmp);      // tmp = A * v
    At_times_v(n, tmp, out);   // out = A^T * tmp
}

static double dot(int n, const double *x, const double *y) {
    double s = 0.0;
    for (int i = 0; i < n; i++) s += x[i] * y[i];
    return s;
}

int main(int argc, char **argv) {
    int n = (argc > 1) ? atoi(argv[1]) : 100;
    if (n <= 0) return 1;

    // vectors
    double *u   = (double*)malloc((size_t)n * sizeof(double));
    double *v   = (double*)malloc((size_t)n * sizeof(double));
    double *tmp = (double*)malloc((size_t)n * sizeof(double));
    if (!u || !v || !tmp) return 1;

    // u initialized to all 1s; v can be 0
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
        v[i] = 0.0;
    }

    // Power method iterations on AtA
    // Common benchmark loop: 10 times: v = AtA(u); u = AtA(v)
    for (int iter = 0; iter < 10; iter++) {
        AtA_times_v(n, u, v, tmp);
        AtA_times_v(n, v, u, tmp);
    }

    // Estimate spectral norm: sqrt((u·v)/(v·v))
    double vBv = dot(n, u, v);
    double vv  = dot(n, v, v);
    double norm = sqrt(vBv / vv);

    printf("%.9f\n", norm);

    free(u);
    free(v);
    free(tmp);
    return 0;
}
