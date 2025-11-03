#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/*---------------------------------------------------------------------------*/
/* (i)  Compute the infinite matrix element A(i,j), zero‐based indexing.    */
/*---------------------------------------------------------------------------*/
static double A(int i, int j) {
    /* pairing function: (i+j)*(i+j+1)/2 + i + 1 */
    int k = i + j;
    return 1.0 / ((k * (k + 1) / 2) + i + 1);
}

/*---------------------------------------------------------------------------*/
/* (ii) Compute y = A * x, for vectors of length n.                          */
/*---------------------------------------------------------------------------*/
static void multiply_A(const double *x, double *y, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(i, j) * x[j];
        }
        y[i] = sum;
    }
}

/*---------------------------------------------------------------------------*/
/* (iii) Compute y = Aᵗ * x, for vectors of length n.                        */
/*---------------------------------------------------------------------------*/
static void multiply_At(const double *x, double *y, int n) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        for (int j = 0; j < n; j++) {
            sum += A(j, i) * x[j];
        }
        y[i] = sum;
    }
}

/*---------------------------------------------------------------------------*/
/* (iv) Compute y = Aᵗ * (A * x)), via a temporary buffer of length n.      */
/*---------------------------------------------------------------------------*/
static void multiply_AtA(const double *x, double *y, int n) {
    double *tmp = (double*)malloc(sizeof(double) * n);
    if (!tmp) {
        fprintf(stderr, "Allocation failed\n");
        exit(1);
    }
    multiply_A(x, tmp, n);
    multiply_At(tmp, y, n);
    free(tmp);
}

/*---------------------------------------------------------------------------*/
/* Main: read n from argv (default 5500), run 10 iterations of the Power    */
/* Method on vector u, then estimate the spectral norm via the Rayleigh      */
/* quotient.                                                                 */
/*---------------------------------------------------------------------------*/
int main(int argc, char *argv[]) {
    int n = 5500;
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0) {
            fprintf(stderr, "Usage: %s [n]\n", argv[0]);
            return 1;
        }
    }

    double *u = (double*)malloc(sizeof(double) * n);
    double *v = (double*)malloc(sizeof(double) * n);
    if (!u || !v) {
        fprintf(stderr, "Allocation failed\n");
        return 1;
    }

    /* initialize u to all 1.0 */
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }

    /* 10 iterations: v = AᵗA * u; u = AᵗA * v */
    for (int iter = 0; iter < 10; iter++) {
        multiply_AtA(u, v, n);
        multiply_AtA(v, u, n);
    }

    /* compute Rayleigh quotient: (u·v) / (v·v) */
    double num = 0.0, den = 0.0;
    for (int i = 0; i < n; i++) {
        num += u[i] * v[i];
        den += v[i] * v[i];
    }

    double norm = sqrt(num / den);

    /* print with 9 digits after the decimal point */
    printf("%.9f\n", norm);

    free(u);
    free(v);
    return 0;
}
