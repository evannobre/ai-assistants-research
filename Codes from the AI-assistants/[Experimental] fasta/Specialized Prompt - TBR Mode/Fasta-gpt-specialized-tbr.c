#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define MODULUS   2147483648u      // 2^31
#define MULTIPLIER 1103515245u
#define INCREMENT  12345u
#define LINE_WIDTH 60              // chars per line in FASTA

// Initialize LCG state
static uint32_t lcg_state;

// Seed the LCG (e.g. using time)
void lcg_seed(uint32_t seed) {
    lcg_state = seed;
}

// Return next pseudorandom uint32
uint32_t lcg_next(void) {
    lcg_state = (uint32_t)(
        (uint64_t)MULTIPLIER * lcg_state + INCREMENT
    ) % MODULUS;
    return lcg_state;
}

// Map to nucleotide
char to_base(uint32_t rnd) {
    switch (rnd & 3) {  // same as rnd % 4 but faster
        case 0: return 'A';
        case 1: return 'C';
        case 2: return 'G';
        default: return 'T';
    }
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr,
            "Usage: %s <sequence_length> <output.fasta>\n",
            argv[0]
        );
        return EXIT_FAILURE;
    }

    // Parse args
    uint64_t total_len = strtoull(argv[1], NULL, 10);
    const char *outpath = argv[2];

    // Seed from time (low entropy, but ok for simulation)
    lcg_seed((uint32_t)time(NULL));

    // Open output
    FILE *out = fopen(outpath, "w");
    if (!out) {
        perror("fopen");
        return EXIT_FAILURE;
    }

    // Write FASTA header
    fprintf(out, ">simulated_sequence length=%" PRIu64 "\n", total_len);

    // Buffer one line
    char buf[LINE_WIDTH];
    int bufpos = 0;

    for (uint64_t i = 0; i < total_len; i++) {
        uint32_t rnd = lcg_next();
        buf[bufpos++] = to_base(rnd);

        // Flush full line
        if (bufpos == LINE_WIDTH) {
            fwrite(buf, 1, LINE_WIDTH, out);
            fputc('\n', out);
            bufpos = 0;
        }
    }

    // Flush any remaining bases
    if (bufpos > 0) {
        fwrite(buf, 1, bufpos, out);
        fputc('\n', out);
    }

    fclose(out);
    return EXIT_SUCCESS;
}
