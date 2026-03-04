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

/* 
 * Function (i): Computes the infinite matrix element A(i,j)
 * Formula: A(i,j) = 1 / ((i+j-1)*(i+j-2)/2 + i)
 * This can be simplified to: 1 / (i+j-1 + i+j-2)
 * Which equals: 1 / (i+j) * (i+j-1)
 */
static inline double eval_A(int i, int j) {
    int ij = i + j;
    return 1.0 / (ij * (ij - 1));
}

/*
 * Function (ii): Computes A*v
 * Multiplies the matrix A by vector v and stores result in Av
 */
void multiply_A_v(int n, const double *v, double *Av) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += eval_A(i + 1, j + 1) * v[j];
        }
        Av[i] = sum;
    }
}

/*
 * Function (iii): Computes Aᵗ*v (transpose of A times v)
 * Since A is symmetric in structure, we compute the transpose multiplication
 */
void multiply_At_v(int n, const double *v, double *Atv) {
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += eval_A(j + 1, i + 1) * v[j];
        }
        Atv[i] = sum;
    }
}

/*
 * Function (iv): Computes Aᵗ*(A*v)
 * This is the core operation for the power iteration method
 */
void multiply_AtA_v(int n, const double *v, double *tmp, double *AtAv) {
    multiply_A_v(n, v, tmp);
    multiply_At_v(n, tmp, AtAv);
}

/*
 * Computes dot product of two vectors
 */
static double dot_product(int n, const double *u, const double *v) {
    double sum = 0.0;
    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < n; i++) {
        sum += u[i] * v[i];
    }
    return sum;
}

/*
 * Main spectral norm computation using Power Method
 */
double spectral_norm(int n) {
    // Allocate vectors
    double *u = (double *)malloc(n * sizeof(double));
    double *v = (double *)malloc(n * sizeof(double));
    double *tmp = (double *)malloc(n * sizeof(double));
    
    if (!u || !v || !tmp) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Initialize u with ones
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }
    
    // Power iteration: 10 iterations is sufficient for convergence
    for (int iter = 0; iter < 10; iter++) {
        multiply_AtA_v(n, u, tmp, v);  // v = Aᵗ(A*u)
        multiply_AtA_v(n, v, tmp, u);  // u = Aᵗ(A*v)
    }
    
    // Compute spectral norm: sqrt(u·v / v·v)
    double vBv = dot_product(n, u, v);
    double vv = dot_product(n, v, v);
    double norm = sqrt(vBv / vv);
    
    // Cleanup
    free(u);
    free(v);
    free(tmp);
    
    return norm;
}

int main(int argc, char *argv[]) {
    int n = 100; // Default value
    
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0) {
            fprintf(stderr, "Invalid argument: must be positive integer\n");
            return 1;
        }
    }
    
    // Check memory requirements (rough estimate)
    size_t required_memory = 3 * n * sizeof(double);
    if (required_memory > 7ULL * 1024 * 1024 * 1024) { // 7GB safety margin
        fprintf(stderr, "Warning: Matrix size may exceed available RAM\n");
    }
    
    double norm = spectral_norm(n);
    
    printf("%.9f\n", norm);
    
    return 0;
}
