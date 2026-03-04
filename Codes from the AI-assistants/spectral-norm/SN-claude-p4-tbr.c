/*
 * Spectral Norm Calculation using Power Method
 * Computes the spectral norm of an infinite Hilbert-like matrix
 * 
 * Compile: gcc -O3 -march=native -ffast-math -fopenmp -o spectral_norm spectral_norm.c -lm
 * Run: ./spectral_norm 5500
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifdef _OPENMP
#include <omp.h>
#endif

/**
 * (i) Computes the infinite matrix element A(i, j)
 * Formula: A[i,j] = 1 / (i + j - 1)
 * This represents the Hilbert matrix pattern
 */
static inline double A(int i, int j) {
    return 1.0 / (double)(i + j - 1);
}

/**
 * (ii) Computes matrix-vector product: result = A * v
 * Where A is the Hilbert-like infinite matrix
 * 
 * @param n: dimension of vectors
 * @param v: input vector
 * @param result: output vector (A * v)
 */
void multiply_Av(int n, const double *v, double *result) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(i + 1, j + 1) * v[j];
        }
        result[i] = sum;
    }
}

/**
 * (iii) Computes transpose matrix-vector product: result = A^T * v
 * Since A is symmetric (A[i,j] = A[j,i]), A^T = A
 * But we implement it explicitly for clarity
 * 
 * @param n: dimension of vectors
 * @param v: input vector
 * @param result: output vector (A^T * v)
 */
void multiply_Atv(int n, const double *v, double *result) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(j + 1, i + 1) * v[j];
        }
        result[i] = sum;
    }
}

/**
 * (iv) Computes A^T * (A * v)
 * This is the key operation in the power method for computing spectral norm
 * 
 * @param n: dimension of vectors
 * @param v: input vector
 * @param temp: temporary storage for intermediate result
 * @param result: output vector (A^T * A * v)
 */
void multiply_AtAv(int n, const double *v, double *temp, double *result) {
    multiply_Av(n, v, temp);      // temp = A * v
    multiply_Atv(n, temp, result); // result = A^T * temp
}

/**
 * Computes the dot product of two vectors
 * Used to compute eigenvalue estimates in power method
 */
double dot_product(int n, const double *u, const double *v) {
    double sum = 0.0;
    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < n; i++) {
        sum += u[i] * v[i];
    }
    return sum;
}

/**
 * Power Method for computing spectral norm
 * Iteratively applies A^T * A to approximate the dominant eigenvalue
 * The spectral norm is the square root of this eigenvalue
 */
double spectral_norm(int n) {
    // Allocate vectors
    double *u = (double *)malloc(n * sizeof(double));
    double *v = (double *)malloc(n * sizeof(double));
    double *temp = (double *)malloc(n * sizeof(double));
    
    if (!u || !v || !temp) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Initialize v with ones (could be random, but ones work well)
    for (int i = 0; i < n; i++) {
        v[i] = 1.0;
    }
    
    // Power iteration: 10 iterations is typically sufficient
    for (int iter = 0; iter < 10; iter++) {
        multiply_AtAv(n, v, temp, u);  // u = A^T * A * v
        multiply_AtAv(n, u, temp, v);  // v = A^T * A * u
    }
    
    // Compute Rayleigh quotient: (v^T * A^T * A * v) / (v^T * v)
    multiply_AtAv(n, v, temp, u);
    double vAv = dot_product(n, v, u);
    double vv = dot_product(n, v, v);
    
    // Clean up
    free(u);
    free(v);
    free(temp);
    
    // Spectral norm is sqrt(eigenvalue)
    return sqrt(vAv / vv);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <n>\n", argv[0]);
        fprintf(stderr, "Example: %s 5500\n", argv[0]);
        return 1;
    }
    
    int n = atoi(argv[1]);
    
    if (n <= 0 || n > 100000) {
        fprintf(stderr, "Invalid n: must be between 1 and 100000\n");
        return 1;
    }
    
    #ifdef _OPENMP
    // Use all available cores for parallel processing
    int num_threads = omp_get_max_threads();
    printf("Using OpenMP with %d threads\n", num_threads);
    #endif
    
    double norm = spectral_norm(n);
    
    printf("%.9f\n", norm);
    
    return 0;
}
