// mandelbrot_pgm.c
// Build: gcc -O3 -march=native -std=c11 -pthread -o mandelbrot_pgm mandelbrot_pgm.c
// Usage: ./mandelbrot_pgm N max_iter xmin xmax ymin ymax out.pgm
// Example: ./mandelbrot_pgm 4096 1000 -2.0 1.0 -1.5 1.5 mandelbrot.pgm

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdint.h>
#include <errno.h>

typedef struct {
    int thread_id;
    int n;
    int max_iter;
    double xmin, xmax, ymin, ymax;
    int row_start, row_end;
    uint8_t *row_buffer;
    FILE *out;
    pthread_mutex_t *write_mutex;
} worker_args_t;

static inline uint8_t iter_to_byte(int iter, int max_iter) {
    if (iter >= max_iter) return 0; // interior -> black
    // map to 1..255 where larger iter -> brighter
    double t = (double)iter / (double)max_iter;
    int v = (int)(255.0 * t + 0.5);
    if (v < 1) v = 1;
    if (v > 255) v = 255;
    return (uint8_t)v;
}

static inline int mandelbrot_escape(double cx, double cy, int max_iter) {
    double zx = 0.0, zy = 0.0;
    int iter = 0;
    while (iter < max_iter) {
        // z = z^2 + c  -> (zx + i zy)^2 = (zx^2 - zy^2) + i(2*zx*zy)
        double zx2 = zx * zx;
        double zy2 = zy * zy;
        if (zx2 + zy2 > 4.0) break;
        double zy_new = 2.0 * zx * zy + cy;
        double zx_new = zx2 - zy2 + cx;
        zx = zx_new;
        zy = zy_new;
        ++iter;
    }
    return iter;
}

void *worker_func(void *arg) {
    worker_args_t *wa = (worker_args_t *)arg;
    int n = wa->n;
    for (int r = wa->row_start; r < wa->row_end; ++r) {
        // compute y coordinate (top row r=0 -> ymax)
        double y = wa->ymax - (double)r * (wa->ymax - wa->ymin) / (double)(n - 1);
        uint8_t *row = wa->row_buffer;
        for (int c = 0; c < n; ++c) {
            double x = wa->xmin + (double)c * (wa->xmax - wa->xmin) / (double)(n - 1);
            int iter = mandelbrot_escape(x, y, wa->max_iter);
            row[c] = iter_to_byte(iter, wa->max_iter);
        }
        // write row to file at correct offset: protect with mutex and fseek
        pthread_mutex_lock(wa->write_mutex);
        // PGM header size unknown here; output file is opened with append; ensure position
        // File layout: header then rows in order. We write rows sequentially so appending is safe.
        size_t written = fwrite(row, 1, n, wa->out);
        if (written != (size_t)n) {
            fprintf(stderr, "Write error thread %d row %d: %s\n", wa->thread_id, r, strerror(errno));
            pthread_mutex_unlock(wa->write_mutex);
            break;
        }
        pthread_mutex_unlock(wa->write_mutex);
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 8) {
        fprintf(stderr, "Usage: %s N max_iter xmin xmax ymin ymax out.pgm\n", argv[0]);
        return 2;
    }
    int n = atoi(argv[1]);
    int max_iter = atoi(argv[2]);
    double xmin = atof(argv[3]);
    double xmax = atof(argv[4]);
    double ymin = atof(argv[5]);
    double ymax = atof(argv[6]);
    const char *out_path = argv[7];

    if (n <= 0 || max_iter <= 0 || xmin >= xmax || ymin >= ymax) {
        fprintf(stderr, "Invalid arguments\n");
        return 3;
    }

    FILE *out = fopen(out_path, "wb");
    if (!out) {
        fprintf(stderr, "Cannot open output '%s': %s\n", out_path, strerror(errno));
        return 4;
    }

    // Write PGM header (P5 binary)
    // Max value 255
    if (fprintf(out, "P5\n%d %d\n255\n", n, n) < 0) {
        fprintf(stderr, "Header write failed\n");
        fclose(out);
        return 5;
    }
    fflush(out);

    // Determine number of threads using environment or hardware concurrency
    int num_threads = (int)sysconf(_SC_NPROCESSORS_ONLN);
    if (num_threads <= 0) num_threads = 1;
    if (num_threads > n) num_threads = n; // no need for more threads than rows

    pthread_t *threads = malloc(sizeof(pthread_t) * num_threads);
    worker_args_t *args = malloc(sizeof(worker_args_t) * num_threads);
    pthread_mutex_t write_mutex;
    pthread_mutex_init(&write_mutex, NULL);

    // We will write rows sequentially from top to bottom.
    // To keep writes ordered we assign contiguous row ranges to threads and write in that order.
    int rows_per_thread = n / num_threads;
    int rem = n % num_threads;
    for (int t = 0, r = 0; t < num_threads; ++t) {
        int rs = r;
        int re = r + rows_per_thread + (t < rem ? 1 : 0);
        r = re;
        args[t].thread_id = t;
        args[t].n = n;
        args[t].max_iter = max_iter;
        args[t].xmin = xmin;
        args[t].xmax = xmax;
        args[t].ymin = ymin;
        args[t].ymax = ymax;
        args[t].row_start = rs;
        args[t].row_end = re;
        args[t].row_buffer = malloc((size_t)n);
        args[t].out = out;
        args[t].write_mutex = &write_mutex;
        if (!args[t].row_buffer) {
            fprintf(stderr, "Out of memory allocating row buffer\n");
            // free previously allocated
            for (int i = 0; i < t; ++i) free(args[i].row_buffer);
            free(threads); free(args);
            fclose(out);
            return 6;
        }
    }

    // Launch threads
    for (int t = 0; t < num_threads; ++t) {
        if (pthread_create(&threads[t], NULL, worker_func, &args[t]) != 0) {
            fprintf(stderr, "Failed to create thread %d\n", t);
            // join already created threads
            for (int i = 0; i < t; ++i) pthread_join(threads[i], NULL);
            for (int i = 0; i < num_threads; ++i) free(args[i].row_buffer);
            free(threads); free(args);
            fclose(out);
            return 7;
        }
    }

    // Wait for threads
    for (int t = 0; t < num_threads; ++t) pthread_join(threads[t], NULL);

    // cleanup
    for (int t = 0; t < num_threads; ++t) free(args[t].row_buffer);
    free(threads); free(args);
    pthread_mutex_destroy(&write_mutex);
    fclose(out);

    return 0;
}