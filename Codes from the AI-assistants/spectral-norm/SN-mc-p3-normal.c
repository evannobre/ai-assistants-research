#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* (i) A(i, j): infinite matrix element, using 1-based indices logically */
static inline double A(int i, int j) {
    int ij = i + j;
    int denom = (ij * (ij - 1)) / 2 + i;
    return 1.0 / denom;
}

/* (ii) out = A * v */
void Av(int n, const double *v, double *out) {
    for (int i = 0; i < n; i++) {
        double sum = 0.0;
        int ip1 = i + 1;  // convert to 1-based
        for (int j = 0; j < n; j++) {
            int jp1 = j + 1;
            sum += A(ip1, jp1) * v[j];
        }
        out[i] = sum;
    }
}

/* (iii) out = Aᵗ * v */
void Atv(int n, const double *v, double *out) {
    for (int j = 0; j < n; j++) {
        double sum = 0.0;
        int jp1 = j + 1;  // convert to 1-based
        for (int i = 0; i < n; i++) {
            int ip1 = i + 1;
            sum += A(ip1, jp1) * v[i];
        }
        out[j] = sum;
    }
}

/* (iv) out = Aᵗ * (A * v) */
void AtAv(int n, const double *v, double *out) {
    double *tmp = (double *)malloc(n * sizeof(double));
    if (!tmp) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    Av(n, v, tmp);
    Atv(n, tmp, out);

    free(tmp);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s n\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    if (n <= 0) {
        fprintf(stderr, "n must be positive\n");
        return 1;
    }

    double *u = (double *)malloc(n * sizeof(double));
    double *v = (double *)malloc(n * sizeof(double));
    if (!u || !v) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    /* Initialize u with 1s */
    for (int i = 0; i < n; i++) {
        u[i] = 1.0;
    }

    /* Power method iterations */
    for (int iter = 0; iter < 10; iter++) {
        AtAv(n, u, v);
        AtAv(n, v, u);
    }

    /* Rayleigh quotient: lambda ≈ (u·v)/(v·v) */
    double vBv = 0.0;
    double vv = 0.0;
    for (int i = 0; i < n; i++) {
        vBv += u[i] * v[i];
        vv  += v[i] * v[i];
    }

    double spectral_norm = sqrt(vBv / vv);
    printf("%.9f\n", spectral_norm);

    free(u);
    free(v);
    return 0;
}
