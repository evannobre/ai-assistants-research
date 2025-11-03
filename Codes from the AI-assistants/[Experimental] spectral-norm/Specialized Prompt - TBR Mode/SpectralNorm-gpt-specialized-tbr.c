#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Compute A[i,j] = 1.0 / ( ((i+j-1)*(i+j))/2 + i ),
   where i,j are 1-based indices. */
static inline double A(int i, int j) {
    int ij = i + j;
    return 1.0 / ( (ij-1)*ij/2 + i );
}

/* out = A * in */
void multiply_A(const double *in, double *out, int n) {
    for(int i = 1; i <= n; i++) {
        double sum = 0.0;
        for(int j = 1; j <= n; j++) {
            sum += A(i,j) * in[j-1];
        }
        out[i-1] = sum;
    }
}

/* out = A^T * in */
void multiply_At(const double *in, double *out, int n) {
    for(int i = 1; i <= n; i++) {
        double sum = 0.0;
        for(int j = 1; j <= n; j++) {
            sum += A(j,i) * in[j-1];
        }
        out[i-1] = sum;
    }
}

/* out = A^T * (A * in) */
void multiply_AtA(const double *in, double *out, double *tmp, int n) {
    multiply_A(in, tmp, n);
    multiply_At(tmp, out, n);
}

int main(int argc, char **argv) {
    int n = 2000;               /* default size */
    if (argc > 1) n = atoi(argv[1]);
    if (n <= 0) {
        fprintf(stderr, "Usage: %s [n]\n", argv[0]);
        return 1;
    }

    double *u = malloc(sizeof(double)*n);
    double *v = malloc(sizeof(double)*n);
    double *t = malloc(sizeof(double)*n);
    if (!u||!v||!t) {
        perror("malloc");
        return 1;
    }

    /* Initialize u to all ones */
    for(int i = 0; i < n; i++) u[i] = 1.0;

    /* 10 iterations of the power method on A^T A */
    for(int iter = 0; iter < 10; iter++) {
        multiply_AtA(u, v, t, n);
        /* swap u<->v pointers */
        double *tmp = u; u = v; v = tmp;
    }

    /* Compute Au and then A^T(Au) */
    multiply_A(u, v, n);        /* v = A*u */
    multiply_At(v, t, n);       /* t = A^T*v */

    /* Rayleigh quotient: (u·t)/(u·u) */
    double num = 0.0, den = 0.0;
    for(int i = 0; i < n; i++) {
        num += u[i]*t[i];
        den += u[i]*u[i];
    }

    double sigma = sqrt(num/den);
    printf("%.9f\n", sigma);

    free(u); free(v); free(t);
    return 0;
}
