#define _POSIX_C_SOURCE 200112L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <sys/sysinfo.h>

typedef struct {
    int tid;
    int n;
    int start_row;
    int end_row; // exclusive
    int max_iter;
    double re_min, re_max, im_min, im_max;
    uint8_t *buffer;
    int row_bytes;
} worker_arg_t;

static inline int cpu_count(void) {
    int n = (int)sysconf(_SC_NPROCESSORS_ONLN);
    return n > 0 ? n : 1;
}

void *worker(void *argp) {
    worker_arg_t *arg = (worker_arg_t *)argp;
    int n = arg->n;
    int rb = arg->row_bytes;
    int max_iter = arg->max_iter;
    double re_min = arg->re_min, re_max = arg->re_max;
    double im_min = arg->im_min, im_max = arg->im_max;
    uint8_t *buf = arg->buffer;

    for (int y = arg->start_row; y < arg->end_row; ++y) {
        double im = im_max - ( (double)y * (im_max - im_min) ) / (n - 1);
        uint8_t *rowptr = buf + (size_t)y * rb;
        int bitpos = 7;
        uint8_t curbyte = 0;
        int x = 0;
        for (; x < n; ++x) {
            double re = re_min + ( (double)x * (re_max - re_min) ) / (n - 1);
            double zr = 0.0, zi = 0.0;
            int iter = 0;
            while (iter < max_iter) {
                double zr2 = zr*zr, zi2 = zi*zi;
                if (zr2 + zi2 > 4.0) break;
                double newzr = zr2 - zi2 + re;
                double newzi = 2.0*zr*zi + im;
                zr = newzr; zi = newzi;
                ++iter;
            }
            if (iter == max_iter) {
                curbyte |= (1u << bitpos);
            }
            --bitpos;
            if (bitpos < 0) {
                *rowptr++ = curbyte;
                curbyte = 0;
                bitpos = 7;
            }
        }
        if (bitpos != 7) {
            *rowptr++ = curbyte;
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s N [max_iter] > output.pbm\n", argv[0]);
        return 1;
    }
    int n = atoi(argv[1]);
    if (n <= 0) {
        fprintf(stderr, "N must be positive\n");
        return 1;
    }
    int max_iter = 50;
    if (argc >= 3) max_iter = atoi(argv[2]);
    if (max_iter <= 0) max_iter = 50;

    int row_bytes = (n + 7) / 8;
    size_t total_bytes = (size_t)row_bytes * n;
    uint8_t *buffer = malloc(total_bytes);
    if (!buffer) {
        perror("malloc");
        return 1;
    }
    memset(buffer, 0, total_bytes);

    int threads = cpu_count();
    if (threads > n) threads = n;
    pthread_t *tids = malloc(sizeof(pthread_t) * threads);
    worker_arg_t *args = malloc(sizeof(worker_arg_t) * threads);
    if (!tids || !args) {
        perror("malloc");
        free(buffer);
        return 1;
    }

    double re_min = -1.5, re_max = 0.5;
    double im_min = -1.0, im_max = 1.0;

    int rows_per = n / threads;
    int extra = n % threads;
    int row = 0;
    for (int i = 0; i < threads; ++i) {
        int start = row;
        int cnt = rows_per + (i < extra ? 1 : 0);
        int end = start + cnt;
        args[i].tid = i;
        args[i].n = n;
        args[i].start_row = start;
        args[i].end_row = end;
        args[i].max_iter = max_iter;
        args[i].re_min = re_min;
        args[i].re_max = re_max;
        args[i].im_min = im_min;
        args[i].im_max = im_max;
        args[i].buffer = buffer;
        args[i].row_bytes = row_bytes;
        row = end;
        pthread_create(&tids[i], NULL, worker, &args[i]);
    }
    for (int i = 0; i < threads; ++i) pthread_join(tids[i], NULL);

    // Write PBM header then data to stdout
    // Use setvbuf to get large buffered output
    setvbuf(stdout, NULL, _IOFBF, 1 << 20);
    printf("P4\n%d %d\n", n, n);
    size_t written = fwrite(buffer, 1, total_bytes, stdout);
    if (written != total_bytes) {
        fprintf(stderr, "short write: %zu != %zu\n", written, total_bytes);
        free(buffer);
        free(tids);
        free(args);
        return 1;
    }

    free(buffer);
    free(tids);
    free(args);
    return 0;
}