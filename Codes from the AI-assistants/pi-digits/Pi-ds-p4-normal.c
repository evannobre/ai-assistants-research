#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>
#include <string.h>
#include <time.h>

typedef struct {
    mpz_t* array;
    int size;
} BigIntArray;

void init_array(BigIntArray* arr, int size, unsigned long init_val) {
    arr->size = size;
    arr->array = (mpz_t*)malloc(size * sizeof(mpz_t));
    for (int i = 0; i < size; i++) {
        mpz_init_set_ui(arr->array[i], init_val);
    }
}

void free_array(BigIntArray* arr) {
    for (int i = 0; i < arr->size; i++) {
        mpz_clear(arr->array[i]);
    }
    free(arr->array);
}

void spigot_pi(int digits) {
    int len = (digits * 10) / 3 + 1;
    BigIntArray a;
    init_array(&a, len, 2);
    
    mpz_t predigit;
    mpz_init_set_ui(predigit, 0);
    
    mpz_t nines;
    mpz_init_set_ui(nines, 0);
    
    int print_count = 0;
    
    for (int i = 1; i <= digits; i++) {
        mpz_t q;
        mpz_init(q);
        
        mpz_t carry;
        mpz_init_set_ui(carry, 0);
        
        for (int j = len - 1; j >= 0; j--) {
            mpz_mul_ui(a.array[j], a.array[j], 10);
            mpz_add(a.array[j], a.array[j], carry);
            
            mpz_t denominator;
            mpz_init_set_ui(denominator, 2 * j + 1);
            
            mpz_fdiv_qr(a.array[j], carry, a.array[j], denominator);
            mpz_mul_ui(carry, carry, j);
            
            mpz_clear(denominator);
        }
        
        mpz_set_ui(a.array[0], mpz_get_ui(carry) % 10);
        mpz_fdiv_q_ui(carry, carry, 10);
        
        mpz_set(q, carry);
        
        if (mpz_cmp_ui(q, 9) == 0) {
            mpz_add_ui(nines, nines, 1);
        } else {
            mpz_t digit;
            mpz_init(digit);
            mpz_add(digit, predigit, q);
            
            printf("%lu", mpz_get_ui(digit));
            print_count++;
            
            for (unsigned long k = 0; k < mpz_get_ui(nines); k++) {
                printf("9");
                print_count++;
                if (print_count % 10 == 0) {
                    printf("\t:%d\n", print_count);
                }
            }
            
            mpz_set(predigit, q);
            mpz_set_ui(nines, 0);
            
            mpz_clear(digit);
        }
        
        if (print_count % 10 == 0 && print_count > 0) {
            if (mpz_get_ui(nines) == 0) {
                printf("\t:%d\n", print_count);
            }
        }
        
        mpz_clear(q);
        mpz_clear(carry);
    }
    
    if (print_count % 10 != 0) {
        int remaining = 10 - (print_count % 10);
        for (int i = 0; i < remaining; i++) {
            printf(" ");
        }
        printf("\t:%d\n", print_count);
    }
    
    free_array(&a);
    mpz_clear(predigit);
    mpz_clear(nines);
}

void spigot_pi_extract_3(int digits) {
    printf("\n=== Spigot Algorithm (extract 3) ===\n");
    printf("Calculating first %d digits of Pi:\n\n", digits);
    
    clock_t start = clock();
    spigot_pi(digits);
    clock_t end = clock();
    
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("\nTime taken: %.2f seconds\n", elapsed);
}

void spigot_pi_extract_4(int digits) {
    printf("\n=== Spigot Algorithm (extract 4) ===\n");
    printf("Calculating first %d digits of Pi:\n\n", digits);
    
    clock_t start = clock();
    
    int len = (digits * 10) / 3 + 1;
    BigIntArray a;
    init_array(&a, len, 2);
    
    mpz_t predigit;
    mpz_init_set_ui(predigit, 0);
    
    mpz_t nines;
    mpz_init_set_ui(nines, 0);
    
    int print_count = 0;
    
    for (int i = 1; i <= digits; i++) {
        mpz_t q;
        mpz_init(q);
        
        mpz_t carry;
        mpz_init_set_ui(carry, 0);
        
        for (int j = len - 1; j >= 0; j--) {
            mpz_mul_ui(a.array[j], a.array[j], 10);
            mpz_add(a.array[j], a.array[j], carry);
            
            mpz_t denominator;
            mpz_init_set_ui(denominator, 2 * j + 1);
            
            mpz_fdiv_qr(a.array[j], carry, a.array[j], denominator);
            mpz_mul_ui(carry, carry, j);
            
            mpz_clear(denominator);
        }
        
        mpz_set_ui(a.array[0], mpz_get_ui(carry) % 10);
        mpz_fdiv_q_ui(carry, carry, 10);
        
        mpz_set(q, carry);
        
        if (mpz_cmp_ui(q, 9) == 0) {
            mpz_add_ui(nines, nines, 1);
        } else if (mpz_cmp_ui(q, 10) == 0) {
            mpz_t digit;
            mpz_init(digit);
            mpz_add_ui(digit, predigit, 1);
            
            printf("%lu", mpz_get_ui(digit));
            print_count++;
            
            for (unsigned long k = 0; k < mpz_get_ui(nines); k++) {
                printf("0");
                print_count++;
                if (print_count % 10 == 0) {
                    printf("\t:%d\n", print_count);
                }
            }
            
            mpz_set_ui(predigit, 0);
            mpz_set_ui(nines, 0);
            
            mpz_clear(digit);
        } else {
            mpz_t digit;
            mpz_init(digit);
            mpz_add(digit, predigit, q);
            
            printf("%lu", mpz_get_ui(digit));
            print_count++;
            
            for (unsigned long k = 0; k < mpz_get_ui(nines); k++) {
                printf("9");
                print_count++;
                if (print_count % 10 == 0) {
                    printf("\t:%d\n", print_count);
                }
            }
            
            mpz_set(predigit, q);
            mpz_set_ui(nines, 0);
            
            mpz_clear(digit);
        }
        
        if (print_count % 10 == 0 && print_count > 0) {
            if (mpz_get_ui(nines) == 0) {
                printf("\t:%d\n", print_count);
            }
        }
        
        mpz_clear(q);
        mpz_clear(carry);
    }
    
    if (print_count % 10 != 0) {
        int remaining = 10 - (print_count % 10);
        for (int i = 0; i < remaining; i++) {
            printf(" ");
        }
        printf("\t:%d\n", print_count);
    }
    
    free_array(&a);
    mpz_clear(predigit);
    mpz_clear(nines);
    
    clock_t end = clock();
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("\nTime taken: %.2f seconds\n", elapsed);
}

int main(int argc, char* argv[]) {
    int digits = 100;
    
    if (argc > 1) {
        digits = atoi(argv[1]);
    }
    
    if (digits < 1) {
        digits = 100;
    }
    
    // Check if we have enough memory (conservative estimate)
    size_t estimated_memory = (digits * 10 / 3 + 1) * sizeof(mpz_t) * 2;
    if (estimated_memory > 6ULL * 1024 * 1024 * 1024) { // 6GB limit for safety
        printf("Warning: Requested %d digits may require too much memory (>6GB)\n", digits);
        printf("Reducing to 10000 digits for safety\n");
        digits = 10000;
    }
    
    printf("System: Ubuntu 24.04.4 64-bit\n");
    printf("Memory: 8 GB RAM, 256 GB SSD\n");
    printf("Calculating Pi to %d digits\n\n", digits);
    
    // Run extract(3) version
    spigot_pi_extract_3(digits > 1000 ? 1000 : digits);
    
    // Run extract(4) version
    spigot_pi_extract_4(digits > 1000 ? 1000 : digits);
    
    // For performance test with 10000 digits
    if (digits >= 10000) {
        printf("\n\n=== Performance Test (10000 digits) ===\n");
        
        printf("\nExtract(3) with 10000 digits:\n");
        clock_t start = clock();
        spigot_pi(10000);
        clock_t end = clock();
        printf("Time: %.2f seconds\n", ((double)(end - start)) / CLOCKS_PER_SEC);
    }
    
    return 0;
}