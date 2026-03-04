#define IM 139968
#define IA 3877
#define IC 29573
static unsigned int seed = 42;

double random_lcg() {
    seed = (seed * IA + IC) % IM;
    return (double)seed / IM;
}

typedef struct {
    char c;
    double p;
} Nucleotide;

Nucleotide iub[] = {
    {'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
    {'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
    {'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
    {'V', 0.02}, {'W', 0.02}, {'Y', 0.02}
};

Nucleotide homosapiens[] = {
    {'a', 0.3029549426680},
    {'c', 0.1979883004921},
    {'g', 0.1975473066391},
    {'t', 0.3015094502008}
};

char select_nucleotide(Nucleotide *table, int size) {
    double r = random_lcg();
    double sum = 0.0;
    for (int i = 0; i < size; ++i) {
        sum += table[i].p;
        if (r < sum) return table[i].c;
    }
    return table[size - 1].c; // fallback
}

void repeat_fasta(const char *header, const char *seq, int n) {
    int len = strlen(seq);
    printf("%s\n", header);
    for (int i = 0; i < n; i += 60) {
        for (int j = 0; j < 60 && i + j < n; ++j)
            putchar(seq[(i + j) % len]);
        putchar('\n');
    }
}

void random_fasta(const char *header, Nucleotide *table, int size, int n) {
    printf("%s\n", header);
    for (int i = 0; i < n; i += 60) {
        for (int j = 0; j < 60 && i + j < n; ++j)
            putchar(select_nucleotide(table, size));
        putchar('\n');
    }
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IM 139968
#define IA 3877
#define IC 29573
static unsigned int seed = 42;

double random_lcg() {
    seed = (seed * IA + IC) % IM;
    return (double)seed / IM;
}

typedef struct {
    char c;
    double p;
} Nucleotide;

Nucleotide iub[] = {
    {'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
    {'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
    {'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
    {'V', 0.02}, {'W', 0.02}, {'Y', 0.02}
};

Nucleotide homosapiens[] = {
    {'a', 0.3029549426680},
    {'c', 0.1979883004921},
    {'g', 0.1975473066391},
    {'t', 0.3015094502008}
};

char select_nucleotide(Nucleotide *table, int size) {
    double r = random_lcg();
    double sum = 0.0;
    for (int i = 0; i < size; ++i) {
        sum += table[i].p;
        if (r < sum) return table[i].c;
    }
    return table[size - 1].c;
}

void repeat_fasta(const char *header, const char *seq, int n) {
    int len = strlen(seq);
    printf("%s\n", header);
    for (int i = 0; i < n; i += 60) {
        for (int j = 0; j < 60 && i + j < n; ++j)
            putchar(seq[(i + j) % len]);
        putchar('\n');
    }
}

void random_fasta(const char *header, Nucleotide *table, int size, int n) {
    printf("%s\n", header);
    for (int i = 0; i < n; i += 60) {
        for (int j = 0; j < 60 && i + j < n; ++j)
            putchar(select_nucleotide(table, size));
        putchar('\n');
    }
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 25000000;
    const char *alu =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    repeat_fasta(">ONE Homo sapiens alu", alu, n * 2);
    random_fasta(">TWO IUB ambiguity codes", iub, sizeof(iub)/sizeof(*iub), n * 3);
    random_fasta(">THREE Homo sapiens frequency", homosapiens, sizeof(homosapiens)/sizeof(*homosapiens), n * 5);

    return 0;
}
