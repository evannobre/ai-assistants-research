#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char complement(char c) {
    switch(c) {
        case 'A': return 'T';
        case 'T': return 'A';
        case 'C': return 'G';
        case 'G': return 'C';
        case 'a': return 't';
        case 't': return 'a';
        case 'c': return 'g';
        case 'g': return 'c';
        default:  return 'N';
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <dna_file>\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror("File error");
        return 1;
    }

    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    rewind(fp);

    char *seq = malloc(size + 1);
    fread(seq, 1, size, fp);
    seq[size] = '\0';
    fclose(fp);

    for (long i = size - 1; i >= 0; i--) {
        putchar(complement(seq[i]));
    }
    putchar('\n');

    free(seq);
    return 0;
}
