#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IM 139968
#define IA 3877
#define IC 29573
#define LINE_LENGTH 60

static unsigned int seed = 42;

double random_number(double max) {
    seed = (seed * IA + IC) % IM;
    return max * seed / IM;
}

void make_cumulative(char *chars, double *probs, int count) {
    double cumulative = 0.0;
    for (int i = 0; i < count; i++) {
        cumulative += probs[i];
        probs[i] = cumulative;
    }
}

char select_random(char *chars, double *probs, int count) {
    double r = random_number(1.0);
    
    // Linear search
    for (int i = 0; i < count; i++) {
        if (r <= probs[i]) {
            return chars[i];
        }
    }
    return chars[count - 1];
}

void generate_repeat_fasta(const char *seq, int n) {
    int seq_len = strlen(seq);
    int pos = 0;
    char buffer[LINE_LENGTH + 1];
    
    while (n > 0) {
        int chunk = n < LINE_LENGTH ? n : LINE_LENGTH;
        if (seq_len - pos < chunk) {
            chunk = seq_len - pos;
        }
        
        strncpy(buffer, seq + pos, chunk);
        buffer[chunk] = '\0';
        printf("%s\n", buffer);
        
        pos += chunk;
        if (pos >= seq_len) {
            pos = 0;
        }
        n -= chunk;
    }
}

void generate_random_fasta(char *chars, double *probs, int count, int n) {
    make_cumulative(chars, probs, count);
    char buffer[LINE_LENGTH + 1];
    
    while (n > 0) {
        int chunk = n < LINE_LENGTH ? n : LINE_LENGTH;
        
        for (int i = 0; i < chunk; i++) {
            buffer[i] = select_random(chars, probs, count);
        }
        buffer[chunk] = '\0';
        printf("%s\n", buffer);
        
        n -= chunk;
    }
}

int main(int argc, char *argv[]) {
    int n = 1000;
    if (argc > 1) {
        n = atoi(argv[1]);
    }
    
    const char *alu =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";
    
    // IUB table
    char iub_chars[] = "acgtBDHKMNRSVWY";
    double iub_probs[] = {
        0.27, 0.12, 0.12, 0.27,
        0.02, 0.02, 0.02, 0.02,
        0.02, 0.02, 0.02, 0.02,
        0.02, 0.02, 0.02
    };
    
    // Homo sapiens table
    char homosapiens_chars[] = "acgt";
    double homosapiens_probs[] = {
        0.3029549426680,
        0.1979883004921,
        0.1975473066391,
        0.3015094502008
    };
    
    printf(">ONE Homo sapiens alu\n");
    generate_repeat_fasta(alu, n * 2);
    
    printf(">TWO IUB ambiguity codes\n");
    seed = 42;
    generate_random_fasta(iub_chars, iub_probs, 15, n * 3);
    
    printf(">THREE Homo sapiens frequency\n");
    seed = 42;
    generate_random_fasta(homosapiens_chars, homosapiens_probs, 4, n * 5);
    
    return 0;
}