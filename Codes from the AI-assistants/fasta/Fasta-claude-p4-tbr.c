#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_WIDTH 60

/* Naïve LCG constants */
#define IM 139968
#define IA 3877
#define IC 29573

/* Global seed for LCG */
static int seed = 42;

/* Naïve LCG random number generator */
static inline double gen_random(double max) {
    seed = (seed * IA + IC) % IM;
    return max * seed / IM;
}

/* Nucleotide probability structure */
typedef struct {
    char c;
    double p;
} amino_acid;

/* IUB ambiguity codes */
static amino_acid iub[] = {
    {'a', 0.27},
    {'c', 0.12},
    {'g', 0.12},
    {'t', 0.27},
    {'B', 0.02},
    {'D', 0.02},
    {'H', 0.02},
    {'K', 0.02},
    {'M', 0.02},
    {'N', 0.02},
    {'R', 0.02},
    {'S', 0.02},
    {'V', 0.02},
    {'W', 0.02},
    {'Y', 0.02}
};
#define IUB_LEN (sizeof(iub) / sizeof(amino_acid))

/* Homo sapiens frequency */
static amino_acid homosapiens[] = {
    {'a', 0.3029549426680},
    {'c', 0.1979883004921},
    {'g', 0.1975473066391},
    {'t', 0.3015094502008}
};
#define HOMOSAPIENS_LEN (sizeof(homosapiens) / sizeof(amino_acid))

/* Convert probabilities to cumulative probabilities */
static void make_cumulative(amino_acid *aa, int len) {
    double cp = 0.0;
    for (int i = 0; i < len; i++) {
        cp += aa[i].p;
        aa[i].p = cp;
    }
}

/* Select nucleotide using linear search (naïve lookup) */
static inline char select_nucleotide(amino_acid *aa, int len, double r) {
    for (int i = 0; i < len; i++) {
        if (r < aa[i].p) {
            return aa[i].c;
        }
    }
    return aa[len - 1].c;
}

/* Repeat a sequence (for ALU) */
static void repeat_fasta(const char *header, const char *seq, int n) {
    int seq_len = strlen(seq);
    int pos = 0;
    int line_pos = 0;
    char line[LINE_WIDTH + 1];
    
    printf(">%s\n", header);
    
    for (int i = 0; i < n; i++) {
        line[line_pos++] = seq[pos];
        pos = (pos + 1) % seq_len;
        
        if (line_pos == LINE_WIDTH) {
            line[line_pos] = '\0';
            printf("%s\n", line);
            line_pos = 0;
        }
    }
    
    if (line_pos > 0) {
        line[line_pos] = '\0';
        printf("%s\n", line);
    }
}

/* Generate random sequence */
static void random_fasta(const char *header, amino_acid *aa, int len, int n) {
    char line[LINE_WIDTH + 1];
    int line_pos = 0;
    
    printf(">%s\n", header);
    
    for (int i = 0; i < n; i++) {
        double r = gen_random(1.0);
        line[line_pos++] = select_nucleotide(aa, len, r);
        
        if (line_pos == LINE_WIDTH) {
            line[line_pos] = '\0';
            printf("%s\n", line);
            line_pos = 0;
        }
    }
    
    if (line_pos > 0) {
        line[line_pos] = '\0';
        printf("%s\n", line);
    }
}

int main(int argc, char *argv[]) {
    int n = 1000;
    
    if (argc > 1) {
        n = atoi(argv[1]);
    }
    
    /* ALU sequence */
    static const char alu[] = 
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";
    
    /* Convert to cumulative probabilities */
    make_cumulative(iub, IUB_LEN);
    make_cumulative(homosapiens, HOMOSAPIENS_LEN);
    
    /* Generate sequences */
    repeat_fasta("ONE Homo sapiens alu", alu, n * 2);
    random_fasta("TWO IUB ambiguity codes", iub, IUB_LEN, n * 3);
    random_fasta("THREE Homo sapiens frequency", homosapiens, HOMOSAPIENS_LEN, n * 5);
    
    return 0;
}
