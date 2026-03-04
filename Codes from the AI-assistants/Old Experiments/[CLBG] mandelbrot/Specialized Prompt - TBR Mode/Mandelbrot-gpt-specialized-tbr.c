// mandelbrot_p4.c
// Compile: gcc -O3 -march=native -std=c11 -pthread mandelbrot_p4.c -o mandelbrot_p4
// Usage: ./mandelbrot_p4 N [max_iter] [threads]
// Example: ./mandelbrot_p4 16000 50 8

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <pthread.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/sysinfo.h>

typedef struct {
    int fd;
    int N;
    int max_iter;
    int row_bytes;
    double dx;
    double dy;
    double x_min;
    double y_top;
    off_t data_offset;
} shared_t;

volatile int next_row = 0;
shared_t S;

static inline unsigned char compute_byte(int col_start, int row, int N, int max_iter, double dx, double dy, double x_min, double y_top) {
    unsigned char byte = 0;
    for (int bit = 0; bit < 8; ++bit) {
        int col = col_start + bit;
        unsigned char pixel = 0;
        if (col < N) {
            double cx = x_min + col * dx;
            double cy = y_top - row * dy;
            double zx = 0.0, zy = 0.0;
            double zx2 = 0.0, zy2 = 0.0;
            int iter = 0;
            while (iter < max_iter && (zx2 + zy2) <= 4.0) {
                zy = 2.0 * zx * zy + cy;
                zx = zx2 - zy2 + cx;
                zx2 = zx * zx;
                zy2 = zy * zy;
                ++iter;
            }
            // inside => black => bit = 1; outside => 0
            if ((zx2 + zy2) <= 4.0) pixel = 1;
        }
        byte = (byte << 1) | (pixel & 1);
    }
    return byte;
}

void *worker(void *arg) {
    (void)arg;
    int N = S.N;
    int max_iter = S.max_iter;
    int row_bytes = S.row_bytes;
    double dx = S.dx;
    double dy = S.dy;
    double x_min = S.x_min;
    double y_top = S.y_top;
    off_t base = S.data_offset;
    int fd = S.fd;

    unsigned char *rowbuf = malloc((size_t)row_bytes);
    if (!rowbuf) { perror("malloc"); pthread_exit(NULL); }

    while (1) {
        int row = __sync_fetch_and_add(&next_row, 1);
        if (row >= N) break;

        // compute row
        int byte_index = 0;
        for (int col = 0; col < N; col += 8) {
            unsigned char b = compute_byte(col, row, N, max_iter, dx, dy, x_min, y_top);
            rowbuf[byte_index++] = b;
        }
        // write the row at offset header_len + row * row_bytes
        off_t offset = base + (off_t)row * row_bytes;
        ssize_t written = pwrite(fd, rowbuf, (size_t)row_bytes, offset);
        if (written != row_bytes) {
            fprintf(stderr, "pwrite error row %d: wrote %zd expected %d (%s)\n", row, written, row_bytes, strerror(errno));
            free(rowbuf);
            pthread_exit(NULL);
        }
    }

    free(rowbuf);
    pthread_exit(NULL);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s N [max_iter] [threads]\n", argv[0]);
        return 1;
    }
    int N = atoi(argv[1]);
    if (N <= 0) {
        fprintf(stderr, "Invalid N\n");
        return 1;
    }
    int max_iter = (argc >= 3) ? atoi(argv[2]) : 50;
    if (max_iter <= 0) max_iter = 50;
    int threads = 0;
    if (argc >= 4) threads = atoi(argv[3]);
    if (threads <= 0) threads = (int)sysconf(_SC_NPROCESSORS_ONLN);
    if (threads <= 0) threads = 1;

    int row_bytes = (N + 7) / 8;

    // open output (stdout or file). We'll write to stdout for piping, else to "mandelbrot.pbm"
    const char *outname = "mandelbrot.pbm";
    int fd = open(outname, O_CREAT | O_TRUNC | O_WRONLY, 0644);
    if (fd < 0) { perror("open"); return 1; }

    // write header
    char header[64];
    int hdr_len = snprintf(header, sizeof(header), "P4\n%d %d\n", N, N);
    if (hdr_len < 0 || hdr_len >= (int)sizeof(header)) {
        fprintf(stderr, "Header snprintf failed\n");
        close(fd);
        return 1;
    }
    if (write(fd, header, (size_t)hdr_len) != hdr_len) {
        perror("write header");
        close(fd);
        return 1;
    }

    // prepare shared struct
    double x_min = -1.5;
    double x_max = 0.5;
    double y_top = 1.0;
    double y_bottom = -1.0;
    double dx = (x_max - x_min) / (double)(N - 1);
    double dy = (y_top - y_bottom) / (double)(N - 1);

    S.fd = fd;
    S.N = N;
    S.max_iter = max_iter;
    S.row_bytes = row_bytes;
    S.dx = dx;
    S.dy = dy;
    S.x_min = x_min;
    S.y_top = y_top;
    S.data_offset = hdr_len;

    // create threads
    pthread_t *tids = malloc(sizeof(pthread_t) * (size_t)threads);
    if (!tids) { perror("malloc tids"); close(fd); return 1; }

    next_row = 0;
    for (int i = 0; i < threads; ++i) {
        if (pthread_create(&tids[i], NULL, worker, NULL) != 0) {
            perror("pthread_create");
            // join already created
            for (int j = 0; j < i; ++j) pthread_join(tids[j], NULL);
            free(tids);
            close(fd);
            return 1;
        }
    }

    for (int i = 0; i < threads; ++i) pthread_join(tids[i], NULL);

    free(tids);
    close(fd);
    return 0;
}
