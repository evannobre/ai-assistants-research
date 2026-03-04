/*
 * FASTA Simulation using Linear Congruential Generator
 * Optimized for Ubuntu 24.04.4 64-bit with 8GB RAM
 * Compile: gcc -O3 -march=native -o fasta fasta.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define LINE_LENGTH 60
#define IM 139968
#define IA 3877
#define IC 29573
#define BUFFER_SIZE (1024 * 1024)  // 1MB buffer for efficient I/O

/* Amino acid structure */
typedef struct {
    char c;
    double p;
} amino_acid;

/* Global LCG seed */
static uint32_t last = 42;

/* Linear Congruential Generator */
static inline double gen_random(double max) {
    last = (last * IA + IC) % IM;
    return max * last / IM;
}

/* Make cumulative probability distribution */
static void make_cumulative(amino_acid *genelist, int count) {
    double cp = 0.0;
    for (int i = 0; i < count; i++) {
        cp += genelist[i].p;
        genelist[i].p = cp;
    }
}

/* Select random character based on cumulative probabilities */
static inline char select_random(amino_acid *genelist, int count) {
    double r = gen_random(1.0);
    
    /* Linear search through cumulative probabilities */
    for (int i = 0; i < count; i++) {
        if (r < genelist[i].p) {
            return genelist[i].c;
        }
    }
    return genelist[count - 1].c;
}

/* Repeat a sequence (for ALU) */
static void make_repeat_fasta(const char *id, const char *desc,
                              const char *s, int n) {
    int len = strlen(s);
    int pos = 0;
    int line_pos = 0;
    
    char *buffer = malloc(BUFFER_SIZE);
    int buf_pos = 0;
    
    printf(">%s %s\n", id, desc);
    
    for (int i = 0; i < n; i++) {
        buffer[buf_pos++] = s[pos];
        pos = (pos + 1) % len;
        line_pos++;
        
        if (line_pos == LINE_LENGTH) {
            buffer[buf_pos++] = '\n';
            line_pos = 0;
        }
        
        /* Flush buffer when nearly full */
        if (buf_pos > BUFFER_SIZE - 100) {
            fwrite(buffer, 1, buf_pos, stdout);
            buf_pos = 0;
        }
    }
    
    if (line_pos > 0) {
        buffer[buf_pos++] = '\n';
    }
    
    if (buf_pos > 0) {
        fwrite(buffer, 1, buf_pos, stdout);
    }
    
    free(buffer);
}

/* Generate random FASTA sequence */
static void make_random_fasta(const char *id, const char *desc,
                              amino_acid *genelist, int count, int n) {
    char *buffer = malloc(BUFFER_SIZE);
    int buf_pos = 0;
    int line_pos = 0;
    
    printf(">%s %s\n", id, desc);
    
    for (int i = 0; i < n; i++) {
        buffer[buf_pos++] = select_random(genelist, count);
        line_pos++;
        
        if (line_pos == LINE_LENGTH) {
            buffer[buf_pos++] = '\n';
            line_pos = 0;
        }
        
        /* Flush buffer when nearly full */
        if (buf_pos > BUFFER_SIZE - 100) {
            fwrite(buffer, 1, buf_pos, stdout);
            buf_pos = 0;
        }
    }
    
    if (line_pos > 0) {
        buffer[buf_pos++] = '\n';
    }
    
    if (buf_pos > 0) {
        fwrite(buffer, 1, buf_pos, stdout);
    }
    
    free(buffer);
}

int main(int argc, char *argv[]) {
    int n = (argc > 1) ? atoi(argv[1]) : 1000;
    
    /* IUB ambiguity codes */
    amino_acid iub[] = {
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
    
    /* Homo sapiens frequency */
    amino_acid homosapiens[] = {
        {'a', 0.3029549426680},
        {'c', 0.1979883004921},
        {'g', 0.1975473066391},
        {'t', 0.3015094502008}
    };
    
    /* ALU repeat sequence */
    const char *alu = 
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";
    
    /* Convert to cumulative probabilities */
    make_cumulative(iub, 15);
    make_cumulative(homosapiens, 4);
    
    /* Generate sequences */
    make_repeat_fasta("ONE", "Homo sapiens alu", alu, n * 2);
    make_random_fasta("TWO", "IUB ambiguity codes", iub, 15, n * 3);
    make_random_fasta("THREE", "Homo sapiens frequency", homosapiens, 4, n * 5);
    
    return 0;
}
