// perfect_tree_alloc.c
// Build a perfect balanced binary tree using a single contiguous allocation.
// Nodes contain only left/right pointers (no payload values).
// Compile: gcc -O2 -std=c11 -Wall -Wextra -o perfect_tree_alloc perfect_tree_alloc.c
// Run: ./perfect_tree_alloc [depth] [memory_limit_bytes]
// Example: ./perfect_tree_alloc 24

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <string.h>
#include <limits.h>

typedef struct Node {
    struct Node *left;
    struct Node *right;
} Node;

static inline int safe_mul_u128(uint64_t a, uint64_t b, uint64_t *out) {
    __uint128_t t = ( __uint128_t ) a * b;
    if (t > ( __uint128_t ) UINT64_MAX) return 0;
    *out = (uint64_t) t;
    return 1;
}

// compute number of nodes in a perfect tree of depth d:
// nodes = 2^(d+1) - 1
// returns 1 on success, nodes_out set. fails on overflow.
int compute_nodes_for_depth(unsigned depth, uint64_t *nodes_out) {
    if (depth >= 63) return 0; // 2^(64) would overflow 64-bit arithmetic
    uint64_t nodes = (1ULL << (depth + 1)) - 1ULL;
    *nodes_out = nodes;
    return 1;
}

// Try to allocate the node array. Align to page size for better behavior.
void *aligned_alloc_pages(size_t alignment, size_t size) {
    void *ptr = NULL;
    int err = posix_memalign(&ptr, alignment, size);
    if (err != 0) {
        // posix_memalign returns error code
        return NULL;
    }
    return ptr;
}

// Build tree by setting left/right pointers based on implicit array layout:
// for index i (0-based), left child index = 2*i+1, right = 2*i+2 if within bounds.
Node *build_perfect_tree(Node *base, uint64_t nodes) {
    for (uint64_t i = 0; i < nodes; ++i) {
        uint64_t l = 2*i + 1;
        uint64_t r = 2*i + 2;
        base[i].left = (l < nodes) ? &base[l] : NULL;
        base[i].right = (r < nodes) ? &base[r] : NULL;
    }
    return &base[0];
}

// Preorder traversal using explicit heap-allocated stack; counts nodes visited.
uint64_t preorder_count(Node *root, unsigned depth) {
    if (!root) return 0;
    // maximum stack depth is depth+1
    size_t max_stack = (size_t)depth + 2;
    Node **stack = malloc(max_stack * sizeof(Node*));
    if (!stack) {
        fprintf(stderr, "Failed to allocate traversal stack\n");
        return 0;
    }
    size_t sp = 0;
    stack[sp++] = root;
    uint64_t visited = 0;
    while (sp) {
        Node *n = stack[--sp];
        ++visited;
        // push right then left so left is processed first
        if (n->right) {
            if (sp >= max_stack) { // should not happen for perfect tree
                free(stack);
                return visited;
            }
            stack[sp++] = n->right;
        }
        if (n->left) {
            if (sp >= max_stack) {
                free(stack);
                return visited;
            }
            stack[sp++] = n->left;
        }
    }
    free(stack);
    return visited;
}

int main(int argc, char **argv) {
    unsigned depth = 20; // default depth
    uint64_t memory_limit = 6ULL * 1024ULL * 1024ULL * 1024ULL; // default 6GiB safe cap

    if (argc >= 2) {
        long v = strtol(argv[1], NULL, 10);
        if (v < 0) {
            fprintf(stderr, "Depth must be non-negative\n");
            return 1;
        }
        depth = (unsigned) v;
    }
    if (argc >= 3) {
        // allow specifying memory limit in bytes
        char *end;
        unsigned long long m = strtoull(argv[2], &end, 0);
        if (m == 0 && errno == EINVAL) {
            fprintf(stderr, "Invalid memory limit\n");
            return 1;
        }
        memory_limit = (uint64_t) m;
    }

    // Compute node count
    uint64_t nodes = 0;
    if (!compute_nodes_for_depth(depth, &nodes)) {
        fprintf(stderr, "Depth too large or would overflow (depth >= 63 unsupported)\n");
        return 1;
    }

    size_t node_size = sizeof(Node);
    uint64_t total_bytes;
    if (!safe_mul_u128(nodes, (uint64_t)node_size, &total_bytes)) {
        fprintf(stderr, "Requested allocation would overflow size calculation\n");
        return 1;
    }

    if (total_bytes > memory_limit) {
        fprintf(stderr, "Requested allocation %" PRIu64 " bytes exceeds memory limit %" PRIu64 " bytes.\n",
                total_bytes, memory_limit);
        fprintf(stderr, "Reduce depth (current depth=%u requires %" PRIu64 " nodes -> %" PRIu64 " bytes)\n",
                depth, nodes, total_bytes);
        return 1;
    }

    long pagesz = sysconf(_SC_PAGESIZE);
    if (pagesz <= 0) pagesz = 4096;

    void *mem = aligned_alloc_pages((size_t)pagesz, (size_t) total_bytes);
    if (!mem) {
        perror("Allocation failed");
        return 1;
    }

    // Zero the allocated memory to avoid uninitialized pointers (defensive).
    memset(mem, 0, (size_t) total_bytes);

    Node *base = (Node *) mem;
    Node *root = build_perfect_tree(base, nodes);

    printf("Built perfect tree depth=%u, nodes=%" PRIu64 ", node_size=%zu, total_bytes=%" PRIu64 " bytes\n",
           depth, nodes, node_size, total_bytes);

    // Do a traversal to verify and count nodes (no payload printed or stored)
    uint64_t visited = preorder_count(root, depth);
    printf("Preorder traversal visited %" PRIu64 " nodes (expected %" PRIu64 ")\n", visited, nodes);

    // Clean up
    free(mem);
    return 0;
}
