#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Max line length we will support (FASTA standard lines are usually 60-80 chars)
#define INITIAL_BUF_SIZE 4096
#define LINE_BUF_SIZE 1024

// Complement lookup table
char complement_table[256];

// Initialize the complement table
void init_complement_table() {
    for (int i = 0; i < 256; ++i)
        complement_table[i] = i;  // default: identity
    complement_table['A'] = 'T';
    complement_table['C'] = 'G';
    complement_table['G'] = 'C';
    complement_table['T'] = 'A';
    complement_table['U'] = 'A';
    complement_table['M'] = 'K';
    complement_table['R'] = 'Y';
    complement_table['W'] = 'W';
    complement_table['S'] = 'S';
    complement_table['Y'] = 'R';
    complement_table['K'] = 'M';
    complement_table['V'] = 'B';
    complement_table['H'] = 'D';
    complement_table['D'] = 'H';
    complement_table['B'] = 'V';
    complement_table['N'] = 'N';
}

// Append to a growing buffer
void append(char **buffer, size_t *len, size_t *cap, const char *line, size_t line_len) {
    if (*len + line_len + 1 >= *cap) {
        *cap = (*cap + line_len + 1) * 2;
        *buffer = realloc(*buffer, *cap);
        if (!*buffer) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(1);
        }
    }
    memcpy(*buffer + *len, line, line_len);
    *len += line_len;
    (*buffer)[*len] = '\0';
}

// Print the reverse complement, wrapped at 60 chars per line
void print_reverse_complement(const char *header, const char *sequence, size_t length) {
    printf("%s\n", header);
    for (ssize_t i = length - 1, col = 0; i >= 0; --i, ++col) {
        if (col == 60) {
            putchar('\n');
            col = 0;
        }
        putchar(complement_table[(unsigned char)sequence[i]]);
    }
    if (length > 0) putchar('\n');
}

int main() {
    init_complement_table();

    char line[LINE_BUF_SIZE];
    char *seq_buf = NULL;
    size_t seq_len = 0, seq_cap = 0;
    char current_header[LINE_BUF_SIZE] = {0};

    while (fgets(line, sizeof(line), stdin)) {
        size_t linelen = strcspn(line, "\r\n");  // Remove trailing newline
        line[linelen] = '\0';

        if (line[0] == '>') {
            if (current_header[0] != '\0') {
                // Process and print the previous sequence
                print_reverse_complement(current_header, seq_buf, seq_len);
                seq_len = 0;
            }
            strncpy(current_header, line, sizeof(current_header) - 1);
            current_header[sizeof(current_header) - 1] = '\0';
        } else {
            append(&seq_buf, &seq_len, &seq_cap, line, linelen);
        }
    }

    // Print last sequence
    if (current_header[0] != '\0') {
        print_reverse_complement(current_header, seq_buf, seq_len);
    }

    free(seq_buf);
    return 0;
}