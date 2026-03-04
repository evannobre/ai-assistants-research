#include <stdio.h>
#include <stdlib.h>

#define IM 139968
#define IA 3877
#define IC 29573

static unsigned int seed = 42;

/* Naïve LCG: generate random double in [0,1) */
static double gen_random(void) {
    seed = (seed * IA + IC) % IM;
    return (double)seed / (double)IM;
}

typedef struct {
    char c;
    double p;
} NucProb;

/* Build cumulative probabilities in-place */
static void build_cumulative(NucProb *a, size_t n) {
    double sum = 0.0;
    for (size_t i = 0; i < n; i++) {
        sum += a[i].p;
        a[i].p = sum;
    }
}

/* Pick a character based on cumulative probabilities using linear search */
static char pick_nuc(const NucProb *a, size_t n) {
    double r = gen_random();
    for (size_t i = 0; i < n; i++) {
        if (r < a[i].p) {
            return a[i].c;
        }
    }
    /* Fallback: return last if rounding pushes r == 1.0 (should be rare) */
    return a[n - 1].c;
}

/* Write a sequence in lines of up to 60 chars, from a repeating pattern */
static void repeat_fasta(const char *header, const char *seq, int n) {
    const int line_len = 60;
    int seq_len = 0;
    while (seq[seq_len] != '\0') seq_len++;

    fputs(header, stdout);

    int remaining = n;
    int pos = 0;
    char line[61];
    line[60] = '\0';

    while (remaining > 0) {
        int this_line = remaining < line_len ? remaining : line_len;
        for (int i = 0; i < this_line; i++) {
            line[i] = seq[pos];
            pos++;
            if (pos == seq_len) pos = 0;
        }
        line[this_line] = '\0';
        fputs(line, stdout);
        fputc('\n', stdout);
        remaining -= this_line;
    }
}

/* Write a random sequence using weighted nucleotides */
static void random_fasta(const char *header, NucProb *a, size_t n_probs, int n) {
    const int line_len = 60;
    char line[61];
    line[60] = '\0';

    build_cumulative(a, n_probs);

    fputs(header, stdout);

    int remaining = n;
    while (remaining > 0) {
        int this_line = remaining < line_len ? remaining : line_len;
        for (int i = 0; i < this_line; i++) {
            line[i] = pick_nuc(a, n_probs);
        }
        line[this_line] = '\0';
        fputs(line, stdout);
        fputc('\n', stdout);
        remaining -= this_line;
    }
}

int main(int argc, char **argv) {
    int n = 1000;
    if (argc > 1) {
        n = atoi(argv[1]);
        if (n <= 0) n = 1000;
    }

    /* ALU sequence (from Benchmarks Game FASTA) */
    const char *alu =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    /* IUB ambiguity codes */
    NucProb iub[] = {
        { 'a', 0.27 },
        { 'c', 0.12 },
        { 'g', 0.12 },
        { 't', 0.27 },
        { 'B', 0.02 },
        { 'D', 0.02 },
        { 'H', 0.02 },
        { 'K', 0.02 },
        { 'M', 0.02 },
        { 'N', 0.02 },
        { 'R', 0.02 },
        { 'S', 0.02 },
        { 'V', 0.02 },
        { 'W', 0.02 },
        { 'Y', 0.02 }
    };

    /* Homo sapiens frequency */
    NucProb homosapiens[] = {
        { 'a', 0.3029549426680 },
        { 'c', 0.1979883004921 },
        { 'g', 0.1975473066391 },
        { 't', 0.3015094502008 }
    };

    /* 1) ALU repeat: 2n */
    repeat_fasta(">ONE Homo sapiens alu\n", alu, 2 * n);

    /* 2) IUB random: 3n */
    random_fasta(">TWO IUB ambiguity codes\n", iub, sizeof(iub) / sizeof(iub[0]), 3 * n);

    /* 3) Homo sapiens random: 5n */
    random_fasta(">THREE Homo sapiens frequency\n",
                 homosapiens, sizeof(homosapiens) / sizeof(homosapiens[0]), 5 * n);

    return 0;
}
