#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* LCG parameters */
#define IM 139968
#define IA 3877
#define IC 29573

/* Template sequence to copy from */
static const char *TEMPLATE =
    "GGTTTTGAGAGGAGGAGGAGGAGGAGGAGGAGGAGGAGGAGGAGGAGG";  // (example)

/* Weighted alphabet: bases + their probabilities */
typedef struct {
    char base;
    double weight;
} Alpha;

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <total_length> <copy_block>\n", argv[0]);
        return 1;
    }

    long total = atol(argv[1]);     // e.g. 25000000
    long copy_block = atol(argv[2]); // how many to copy at once
    long remaining = total;

    /* Setup weighted alphabet (must sum to 1.0) */
    Alpha alphabet[] = {
        {'A', 0.27},  {'C', 0.12},
        {'G', 0.12},  {'T', 0.27},
        {'a', 0.11},  {'c', 0.04},
        {'g', 0.04},  {'t', 0.03}
    };
    int alph_size = sizeof(alphabet) / sizeof(*alphabet);

    /* Build cumulative array */
    double *cum = malloc(sizeof(double) * alph_size);
    cum[0] = alphabet[0].weight;
    for (int i = 1; i < alph_size; i++) {
        cum[i] = cum[i-1] + alphabet[i].weight;
    }

    /* Header + copy from template */
    printf(">copy\n");
    while (remaining > 0) {
        long n = copy_block;
        if (n > remaining) n = remaining;
        if (n > (long)strlen(TEMPLATE)) n = strlen(TEMPLATE);

        fwrite(TEMPLATE, 1, n, stdout);
        putchar('\n');
        remaining -= n;
    }

    /* Header + random generation */
    printf(">random\n");
    long seed = 42;
    while (remaining > 0) {
        /* LCG step */
        seed = (seed * IA + IC) % IM;
        double r = (double)seed / IM;

        /* Linear search over cum[] */
        for (int i = 0; i < alph_size; i++) {
            if (r < cum[i]) {
                putchar(alphabet[i].base);
                break;
            }
        }

        if (--remaining % 60 == 0) putchar('\n');
    }
    putchar('\n');

    free(cum);
    return 0;
}
