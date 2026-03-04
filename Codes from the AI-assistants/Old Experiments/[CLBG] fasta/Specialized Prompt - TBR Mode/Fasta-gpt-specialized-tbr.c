#include <stdio.h>
#include <stdlib.h>

/* LCG parameters */
#define IM   139968
#define IA   3877
#define IC   29573

/* wrap into a function returning double in [0,1) */
static long seed = 42;
double lcg_rand() {
    seed = (seed * IA + IC) % IM;
    return (double)seed / (double)IM;
}

/* emit fixed-width lines to stdout */
void emit_random(const char *alph, const double *probs, int n, long total, int width) {
    /* build cumulative */
    double *cum = malloc(sizeof(double)*n);
    cum[0] = probs[0];
    for (int i = 1; i < n; i++)
        cum[i] = cum[i-1] + probs[i];

    int col = 0;
    for (long i = 0; i < total; i++) {
        double r = lcg_rand();

        /* linear search */
        int idx = 0;
        while (r >= cum[idx]) idx++;

        putchar(alph[idx]);
        if (++col == width) {
            putchar('\n');
            col = 0;
        }
    }
    if (col) putchar('\n');
    free(cum);
}

int main(int argc, char **argv) {
    long n = 25000000;       /* default length */
    if (argc > 1) n = atol(argv[1]);

    /* Example alphabets & probabilities (IUB and Homo sapiens) */
    static const char *IUB = "acgtrykmwsbdhvACGTRYKMW SBDHV";
    static const double P_IUB[] = {
        0.27,0.12,0.12,0.27,0.02,0.02,0.02,0.02,
        0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,
        0.27,0.12,0.12,0.27,0.02,0.02,0.02,0.02,
        0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02
    };
    static const char *HOMO = "acgt";
    static const double P_HOMO[] = {0.3029549426680,
                                    0.1979883004921,
                                    0.1975473066391,
                                    0.3015094502008};

    /* 1) Print header */
    printf(">random_fasta %ld\n", n);

    /* 2) Generate with IUB alphabet */
    emit_random(IUB, P_IUB, 32, n, 60);

    /* 3) Generate with Homo sapiens alphabet */
    emit_random(HOMO, P_HOMO, 4, n, 60);

    return 0;
}
