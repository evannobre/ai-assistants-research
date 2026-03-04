// implicit_tree.c
// Build / traverse a perfect balanced binary tree by implicit indexing.
// No per-node payload is stored; only a small stack is allocated for traversal.
// Compile: cc -O2 -std=c11 -o implicit_tree implicit_tree.c

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <limits.h>

static int64_t total_nodes_from_height(unsigned int h) {
    if (h >= 63) return -1; // overflow guard for 64-bit shift
    // N = 2^(h+1) - 1
    return ( (int64_t)1ULL << (h + 1) ) - 1;
}

void iterative_preorder(uint64_t N, unsigned int h) {
    // stack of indices (max depth = h+1)
    uint64_t max_depth = (uint64_t)h + 1;
    uint64_t *stack = malloc(sizeof(uint64_t) * (max_depth + 4));
    if (!stack) { perror("malloc"); exit(1); }
    uint64_t sp = 0;
    stack[sp++] = 0; // root index

    while (sp) {
        uint64_t idx = stack[--sp];
        if (idx >= N) continue;

        // "process" node idx (we do not store any value; just print index/depth)
        // For large trees avoid printing every node; here it's illustrative.
        printf("node index: %" PRIu64 "\n", idx);

        // push right then left so left is processed first
        uint64_t r = 2*idx + 2;
        uint64_t l = 2*idx + 1;
        if (r < N) stack[sp++] = r;
        if (l < N) stack[sp++] = l;
        // sp will not exceed max_depth for perfect tree traversal in DFS.
    }

    free(stack);
}

int main(int argc, char **argv) {
    unsigned int h = 20; // default height
    if (argc >= 2) h = (unsigned int)atoi(argv[1]);

    int64_t N = total_nodes_from_height(h);
    if (N < 0) {
        fprintf(stderr, "height too large or overflow\n");
        return 1;
    }

    // Safety check versus physical memory if you intended to allocate per-node storage:
    const unsigned long long bytes_if_one_per_node = (unsigned long long)N;
    const unsigned long long eight_gib = 8ULL * 1024ULL * 1024ULL * 1024ULL;
    if (bytes_if_one_per_node > eight_gib) {
        fprintf(stderr, "WARNING: tree of height %u would require >8GiB if storing 1 byte per node.\n", h);
    }

    printf("Perfect tree height=%u => nodes=%" PRId64 "\n", h, N);
    printf("Iterative preorder (printing indices). For huge N avoid printing everything.\n\n");

    iterative_preorder((uint64_t)N, h);

    return 0;
}
