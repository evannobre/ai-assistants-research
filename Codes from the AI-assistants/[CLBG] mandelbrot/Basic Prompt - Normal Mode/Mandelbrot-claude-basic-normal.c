#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ITER 50
#define LIMIT 2.0

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <size>\n", argv[0]);
        return 1;
    }
    
    int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "Size must be positive\n");
        return 1;
    }
    
    // Output PBM header
    printf("P4\n%d %d\n", N, N);
    
    // Allocate buffer for one row of bytes
    int bytes_per_row = (N + 7) / 8;
    unsigned char *row = (unsigned char *)calloc(bytes_per_row, sizeof(unsigned char));
    
    if (!row) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }
    
    double inv_N = 2.0 / N;
    
    // Iterate through each row
    for (int y = 0; y < N; y++) {
        double Ci = y * inv_N - 1.0;
        
        // Clear row buffer
        memset(row, 0, bytes_per_row);
        
        // Iterate through each column
        for (int x = 0; x < N; x++) {
            double Cr = x * inv_N - 1.5;
            
            // Mandelbrot iteration: z = z^2 + c
            double Zr = 0.0, Zi = 0.0;
            double Zr2 = 0.0, Zi2 = 0.0;
            
            int i;
            for (i = 0; i < ITER; i++) {
                // z = z^2 + c
                // (a + bi)^2 = a^2 - b^2 + 2abi
                Zi = 2.0 * Zr * Zi + Ci;
                Zr = Zr2 - Zi2 + Cr;
                
                Zr2 = Zr * Zr;
                Zi2 = Zi * Zi;
                
                // Check if |z|^2 > 4 (escaped)
                if (Zr2 + Zi2 > 4.0) {
                    break;
                }
            }
            
            // If didn't escape, set bit to 1 (black pixel)
            if (i == ITER) {
                int byte_index = x / 8;
                int bit_index = 7 - (x % 8);
                row[byte_index] |= (1 << bit_index);
            }
        }
        
        // Write row to stdout
        fwrite(row, 1, bytes_per_row, stdout);
    }
    
    free(row);
    return 0;
}