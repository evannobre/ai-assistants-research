#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ============================
   Function 1: A(i, j) element
   ============================ */
static inline double A(int i, int j) {
    /* 
     * The Hilbert matrix is defined such that:
     * Row-major traversal of upper triangular matrix
     * The (i,j) element (0-based indices) is 1/(i+j+1)
     */
    return 1.0 / (i + j + 1);
}

/* ============================
   Function 2: Multiply A * v
   ============================ */
static void multiply_A_v(int n, const double* v, double* result) {
    /*
     * Computes result = A * v for the first n elements
     * A is an infinite matrix, we compute up to size n
     */
    #pragma omp parallel for if (n > 1000)
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(i, j) * v[j];
        }
        result[i] = sum;
    }
}

/* ============================
   Function 3: Multiply Aᵗ * v
   ============================ */
static void multiply_At_v(int n, const double* v, double* result) {
    /*
     * Computes result = Aᵗ * v
     * Since A is symmetric (Hilbert matrix), Aᵗ = A
     * But we implement it as a separate function as per requirements
     */
    #pragma omp parallel for if (n > 1000)
    for (int j = 0; j < n; j++) {
        double sum = 0.0;
        for (int i = 0; i < n; i++) {
            sum += A(i, j) * v[i];
        }
        result[j] = sum;
    }
}

/* ============================
   Function 4: Multiply Aᵗ * (A * v)
   ============================ */
static void multiply_At_A_v(int n, const double* v, double* result) {
    /*
     * Efficient computation: Aᵗ * (A * v)
     * Equivalent to (Aᵗ * A) * v
     */
    double* temp = (double*)malloc(n * sizeof(double));
    if (!temp) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Compute A * v
    multiply_A_v(n, v, temp);
    
    // Compute Aᵗ * temp
    multiply_At_v(n, temp, result);
    
    free(temp);
}

/* ============================
   Power Method for Spectral Norm
   ============================ */
static double spectral_norm(int n) {
    /*
     * Power method to compute the largest singular value of A
     * which is the spectral norm ||A||₂ = sqrt(λ_max(AᵗA))
     */
    
    // Allocate memory with alignment for better cache performance
    double* u = (double*)aligned_alloc(64, n * sizeof(double));
    double* v = (double*)aligned_alloc(64, n * sizeof(double));
    double* w = (double*)aligned_alloc(64, n * sizeof(double));
    
    if (!u || !v || !w) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Initialize u with 1.0
    #pragma omp parallel for if (n > 1000)
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }
    
    double vBv, vv;
    int iterations = 10;  // Power method iterations
    
    for (int k = 0; k < iterations; k++) {
        // v = Aᵗ * (A * u)
        multiply_At_A_v(n, u, v);
        
        // Normalize v
        vv = 0.0;
        #pragma omp parallel for reduction(+:vv) if (n > 1000)
        for (int i = 0; i < n; i++) {
            vv += v[i] * v[i];
        }
        vv = sqrt(vv);
        
        #pragma omp parallel for if (n > 1000)
        for (int i = 0; i < n; i++) {
            v[i] /= vv;
        }
        
        // w = Aᵗ * (A * v)
        multiply_At_A_v(n, v, w);
        
        // Compute Rayleigh quotient: vᵗ * w
        vBv = 0.0;
        #pragma omp parallel for reduction(+:vBv) if (n > 1000)
        for (int i = 0; i < n; i++) {
            vBv += v[i] * w[i];
        }
        
        // Prepare for next iteration
        #pragma omp parallel for if (n > 1000)
        for (int i = 0; i < n; i++) {
            u[i] = v[i];
        }
    }
    
    double norm = sqrt(vBv);
    
    free(u);
    free(v);
    free(w);
    
    return norm;
}

/* ============================
   Optimized Version (for n=5500)
   ============================ */
static double spectral_norm_optimized(int n) {
    /*
     * Optimized version that precomputes matrix elements
     * and uses blocked matrix multiplication
     */
    
    // For very large n, use single precision and blocking
    const int BLOCK_SIZE = 256;  // L1 cache friendly
    
    double* u = (double*)aligned_alloc(64, n * sizeof(double));
    double* v = (double*)aligned_alloc(64, n * sizeof(double));
    double* temp = (double*)aligned_alloc(64, n * sizeof(double));
    
    if (!u || !v || !temp) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }
    
    // Initialize
    #pragma omp parallel for if (n > 1000)
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }
    
    double vBv, vv;
    int iterations = 10;
    
    for (int k = 0; k < iterations; k++) {
        // Compute A * u using blocking
        #pragma omp parallel for if (n > 1000)
        for (int i = 0; i < n; i++) {
            temp[i] = 0.0;
        }
        
        for (int ii = 0; ii < n; ii += BLOCK_SIZE) {
            int i_end = (ii + BLOCK_SIZE < n) ? ii + BLOCK_SIZE : n;
            for (int jj = 0; jj < n; jj += BLOCK_SIZE) {
                int j_end = (jj + BLOCK_SIZE < n) ? jj + BLOCK_SIZE : n;
                #pragma omp parallel for if (n > 1000)
                for (int i = ii; i < i_end; i++) {
                    double sum = temp[i];
                    for (int j = jj; j < j_end; j++) {
                        sum += A(i, j) * u[j];
                    }
                    temp[i] = sum;
                }
            }
        }
        
        // Compute Aᵗ * temp
        #pragma omp parallel for if (n > 1000)
        for (int j = 0; j < n; j++) {
            v[j] = 0.0;
            for (int i = 0; i < n; i++) {
                v[j] += A(i, j) * temp[i];
            }
        }
        
        // Normalize v
        vv = 0.0;
        #pragma omp parallel for reduction(+:vv) if (n > 1000)
        for (int i = 0; i < n; i++) {
            vv += v[i] * v[i];
        }
        vv = sqrt(vv);
        
        #pragma omp parallel for if (n > 1000)
        for (int i = 0; i < n; i++) {
            v[i] /= vv;
        }
        
        // Update u for next iteration
        #pragma omp parallel for if (n > 1000)
        for (int i = 0; i < n; i++) {
            u[i] = v[i];
        }
    }
    
    // Final computation of spectral norm
    multiply_At_A_v(n, v, temp);
    
    vBv = 0.0;
    #pragma omp parallel for reduction(+:vBv) if (n > 1000)
    for (int i = 0; i < n; i++) {
        vBv += v[i] * temp[i];
    }
    
    double norm = sqrt(vBv);
    
    free(u);
    free(v);
    free(temp);
    
    return norm;
}

/* ============================
   Main Function
   ============================ */
int main(int argc, char* argv[]) {
    int n = 100;  // Default value
    
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0) {
            fprintf(stderr, "Invalid size. Using default n=100\n");
            n = 100;
        }
    }
    
    // For large n, use optimized version
    double norm;
    if (n >= 1000) {
        printf("Computing spectral norm of %dx%d Hilbert matrix (optimized)...\n", n, n);
        norm = spectral_norm_optimized(n);
    } else {
        printf("Computing spectral norm of %dx%d Hilbert matrix...\n", n, n);
        norm = spectral_norm(n);
    }
    
    printf("Spectral norm: %.12f\n", norm);
    
    return 0;
}