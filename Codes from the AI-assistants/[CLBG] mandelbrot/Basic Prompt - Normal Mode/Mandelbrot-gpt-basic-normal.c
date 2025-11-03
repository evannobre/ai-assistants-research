// mandelbrot.c
// Build: gcc -O3 -march=native -std=c11 -Wall -Wextra -o mandelbrot mandelbrot.c -lpthread
// Usage: ./mandelbrot N > mandelbrot.pbm
// Optionally set OMP_NUM_THREADS or leave to auto-detect cores.

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    int thread_id;
    int start_row;
    int end_row; // exclusive
    int N;
    int maxiter;
    double real_min, real_max, imag_min, imag_max;
    uint8_t *buffer; // pointer to the packed bitmap buffer
    int bytes_per_row;
} thread_arg_t;

static inline int mandelbrot_escape(double cx, double cy, int maxiter) {
    double zx = 0.0, zy = 0.0;
    double zx2 = 0.0, zy2 = 0.0;
    int iter = 0;
    while (iter < maxiter && (zx2 + zy2) <= 4.0) {
        // z = z^2 + c  => (zx+ i zy)^2 = (zx^2 - zy^2) + i (2*zx*zy)
        zy = 2.0 * zx * zy + cy;
        zx = zx2 - zy2 + cx;
        zx2 = zx * zx;
        zy2 = zy * zy;
        ++iter;
    }
    return iter;
}

void *worker(void *argp) {
    thread_arg_t *arg = (thread_arg_t*)argp;
    int N = arg->N;
    int bpr = arg->bytes_per_row;
    double real_min = arg->real_min, real_max = arg->real_max;
    double imag_min = arg->imag_min, imag_max = arg->imag_max;
    int maxiter = arg->maxiter;
    uint8_t *buf = arg->buffer;

    for (int y = arg->start_row; y < arg->end_row; ++y) {
        double imag = imag_max - ( (double)y / (N - 1) ) * (imag_max - imag_min);
        uint8_t *rowptr = buf + (size_t)y * bpr;
        int bitpos = 0;
        uint8_t acc = 0;
        int byte_index = 0;
        for (int x = 0; x < N; ++x) {
            double real = real_min + ( (double)x / (N - 1) ) * (real_max - real_min);
            int iter = mandelbrot_escape(real, imag, maxiter);
            // For PBM: 1 = black, 0 = white. Points inside set (didn't escape) -> black (1).
            int inside = (iter >= maxiter) ? 1 : 0;

            acc = (acc << 1) | (inside & 1);
            ++bitpos;

            if (bitpos == 8) {
                rowptr[byte_index++] = acc;
                acc = 0;
                bitpos = 0;
            }
        }
        if (bitpos != 0) {
            // pad remaining lower bits with zeros on right (LSBs)
            acc <<= (8 - bitpos);
            rowptr[byte_index++] = acc;
        }
        // If N % 8 == 0, byte_index == bpr. Otherwise padded to bpr.
        // Ensure any remaining padding bytes (shouldn't be necessary but safe)
        while (byte_index < bpr) rowptr[byte_index++] = 0;
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s N [maxiter]\n", argv[0]);
        return 1;
    }
    int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "Invalid N: %s\n", argv[1]);
        return 1;
    }
    int maxiter = 50; // default; user can set second arg
    if (argc >= 3) {
        int m = atoi(argv[2]);
        if (m > 0) maxiter = m;
    }

    // Plot rectangle Re ∈ [-1.5, 0.5], Im ∈ [-1, 1]
    double real_min = -1.5, real_max = 0.5;
    double imag_min = -1.0, imag_max = 1.0;

    int bytes_per_row = (N + 7) / 8;
    size_t total_bytes = (size_t)bytes_per_row * (size_t)N;

    uint8_t *buffer = (uint8_t*) malloc(total_bytes);
    if (!buffer) {
        fprintf(stderr, "Allocation failed for %zu bytes\n", total_bytes);
        return 1;
    }
    memset(buffer, 0, total_bytes);

    // Threading: use number of online processors unless OMP_NUM_THREADS set (we honor env optionally)
    int nthreads = (int)sysconf(_SC_NPROCESSORS_ONLN);
    char *env_threads = getenv("OMP_NUM_THREADS");
    if (env_threads) {
        int t = atoi(env_threads);
        if (t > 0) nthreads = t;
    }
    if (nthreads < 1) nthreads = 1;

    pthread_t *threads = malloc(sizeof(pthread_t) * nthreads);
    thread_arg_t *targs = malloc(sizeof(thread_arg_t) * nthreads);
    if (!threads || !targs) {
        fprintf(stderr, "Thread struct allocation failed\n");
        free(buffer);
        return 1;
    }

    // Partition rows evenly
    int rows_per = N / nthreads;
    int extra = N % nthreads;
    int row = 0;
    for (int i = 0; i < nthreads; ++i) {
        int start = row;
        int cnt = rows_per + (i < extra ? 1 : 0);
        int end = start + cnt;
        row = end;

        targs[i].thread_id = i;
        targs[i].start_row = start;
        targs[i].end_row = end;
        targs[i].N = N;
        targs[i].maxiter = maxiter;
        targs[i].real_min = real_min;
        targs[i].real_max = real_max;
        targs[i].imag_min = imag_min;
        targs[i].imag_max = imag_max;
        targs[i].buffer = buffer;
        targs[i].bytes_per_row = bytes_per_row;

        if (pthread_create(&threads[i], NULL, worker, &targs[i]) != 0) {
            fprintf(stderr, "Failed to create thread %d\n", i);
            // fall back to sequential for remaining work
            for (int j = i; j < nthreads; ++j) {
                targs[j].start_row = 0;
                targs[j].end_row = 0;
            }
            nthreads = i;
            break;
        }
    }

    // join
    for (int i = 0; i < nthreads; ++i) pthread_join(threads[i], NULL);

    // Write PBM P4 header then data to stdout (binary)
    // Using setvbuf to ensure unbuffered or large buffer for speed
    setvbuf(stdout, NULL, _IOFBF, 1 << 20);
    printf("P4\n%d %d\n", N, N);
    size_t written = fwrite(buffer, 1, total_bytes, stdout);
    if (written != total_bytes) {
        fprintf(stderr, "Warning: wrote %zu of %zu bytes\n", written, total_bytes);
    }
    // cleanup
    free(buffer);
    free(threads);
    free(targs);
    return 0;
}
