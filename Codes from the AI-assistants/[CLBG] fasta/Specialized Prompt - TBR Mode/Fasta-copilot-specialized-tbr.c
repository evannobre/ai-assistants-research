#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_WIDTH 60

/* LCG parameters */
static const int IM = 139968;
static const int IA = 3877;
static const int IC = 29573;

/* Seed state */
static int seed = 42;

/* Simple LCG: update seed and return a double in [0,1) */
static double lcg_rand()
{
    seed = (seed * IA + IC) % IM;
    return (double)seed / (double)IM;
}

/* Print 'len' characters from 'buffer', wrapping every LINE_WIDTH */
static void emit_wrapped(const char *buffer, size_t len)
{
    size_t pos = 0;
    while (pos < len) {
        size_t chunk = LINE_WIDTH;
        if (pos + chunk > len) 
            chunk = len - pos;
        fwrite(buffer + pos, 1, chunk, stdout);
        fputc('\n', stdout);
        pos += chunk;
    }
}

/* 1) REPEAT: copy a fixed template string up to 'n' chars */
static void fasta_repeat(const char *template, size_t n)
{
    size_t templen = strlen(template);
    char linebuf[LINE_WIDTH];
    size_t produced = 0;
    size_t tpl_pos = 0;

    while (produced < n) {
        size_t tocopy = LINE_WIDTH;
        if (produced + tocopy > n)
            tocopy = n - produced;

        for (size_t i = 0; i < tocopy; ++i) {
            linebuf[i] = template[tpl_pos++];
            if (tpl_pos >= templen) tpl_pos = 0;
        }
        fwrite(linebuf, 1, tocopy, stdout);
        fputc('\n', stdout);
        produced += tocopy;
    }
}

/* 2) RANDOM: generate 'n' chars from alphabet[] with weights[] of length 'm' */
static void fasta_random(const char *alph, const double *probs, int m, size_t n)
{
    /* build cumulative probs */
    double cum[m];
    cum[0] = probs[0];
    for (int i = 1; i < m; ++i)
        cum[i] = cum[i-1] + probs[i];

    /* sanity: last cum should be 1.0 */
    /* produce lines of width LINE_WIDTH */
    char line[LINE_WIDTH];
    size_t produced = 0;

    while (produced < n) {
        size_t togen = LINE_WIDTH;
        if (produced + togen > n)
            togen = n - produced;

        for (size_t i = 0; i < togen; ++i) {
            double r = lcg_rand();  /* in [0,1) */
            /* linear scan for the first cum[j] > r */
            int j = 0;
            while (j < m && r >= cum[j]) ++j;
            /* guard: if r >= cum[m-1], fall back to last char */
            if (j == m) j = m-1;
            line[i] = alph[j];
        }

        fwrite(line, 1, togen, stdout);
        fputc('\n', stdout);
        produced += togen;
    }
}

/* a small helper to parse argv[1] */
static size_t get_N(int argc, char **argv)
{
    if (argc > 1) {
        long v = atol(argv[1]);
        if (v > 0) return (size_t)v;
    }
    return 25000000;  /* default */
}

int main(int argc, char **argv)
{
    size_t N = get_N(argc, argv);

    /* 1) Repeat sequence (from the “Homo sapiens” example) */
    static const char *alu =
      "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
      "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
      "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
      "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
      "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
      "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
      "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    printf(">ONE Repeat ALU\n");
    fasta_repeat(alu, N);

    /* 2) Random sequence from IUB ambiguity codes */
    static const char IUB_alph[]    = "GATBSCUVMWRYKDHN";
    static const double IUB_probs[] = {
        0.27, 0.12, 0.12, 0.02, 0.02,
        0.02, 0.02, 0.02, 0.02, 0.02,
        0.02, 0.02, 0.02, 0.02, 0.02
    };
    printf(">TWO IUB ambiguity codes\n");
    fasta_random(IUB_alph, IUB_probs, (int)strlen(IUB_alph), N);

    /* 3) Random sequence from Homo sapiens frequencies */
    static const char HS_alph[]    = "acgt";
    static const double HS_probs[] = {
        0.3029549426680,  /* a */
        0.1979883004921,  /* c */
        0.1975473066391,  /* g */
        0.3015094502008   /* t */
    };
    printf(">THREE Homo sapiens frequency\n");
    fasta_random(HS_alph, HS_probs, (int)strlen(HS_alph), N);

    return 0;
}
