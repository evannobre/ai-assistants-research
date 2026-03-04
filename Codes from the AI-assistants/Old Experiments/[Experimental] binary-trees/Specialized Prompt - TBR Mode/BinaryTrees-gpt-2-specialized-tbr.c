// mmap_tree.c
// Reserve virtual memory for a perfect balanced tree; do not write per-node values.
// Compile: cc -O2 -std=c11 -o mmap_tree mmap_tree.c

#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <errno.h>
#include <inttypes.h>

static int64_t total_nodes_from_height(unsigned int h) {
    if (h >= 63) return -1;
    return ((int64_t)1ULL << (h + 1)) - 1;
}

int main(int argc, char **argv) {
    unsigned int h = 24; // default
    if (argc >= 2) h = (unsigned int)atoi(argv[1]);

    int64_t N = total_nodes_from_height(h);
    if (N < 0) { fprintf(stderr, "height too large/overflow\n"); return 1; }

    // Reserve one byte per node (you can change node_size)
    size_t node_size = 1;
    unsigned long long bytes = (unsigned long long)N * node_size;

    printf("height=%u nodes=%" PRId64 " reserving %llu bytes (virtual)\n", h, N, bytes);

    // Try to mmap the space without committing physical memory
    void *addr = mmap(NULL, bytes,
                      PROT_NONE,                // don't make it accessible (no writes)
                      MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE,
                      -1, 0);

    if (addr == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("mmap reserved address=%p length=%llu\n", addr, bytes);
    printf("Note: PROT_NONE prevents access until mprotect; no per-node values are written.\n");

    // Use implicit indexing for traversal — we can compute offsets inside reserved memory
    // but we must mprotect ranges before touching them.
    // For demonstration we won't access data; we simply show the reservation.

    // Cleanup
    if (munmap(addr, bytes) != 0) {
        perror("munmap");
    }

    return 0;
}
