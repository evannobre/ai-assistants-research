// compile: gcc -O2 -std=c11 tree_alloc_b.c -o tree_alloc_b
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

typedef struct Node {
    struct Node *left;
    struct Node *right;
} Node;

/* Compute node_count = 2^depth - 1, safely.
 * Return 0 on overflow or invalid depth.
 */
uint64_t perfect_node_count(unsigned depth) {
    if (depth == 0) return 0;
    if (depth >= 64) return 0; // shifting >=64 is UB for 64-bit
    uint64_t nodes = (1ULL << depth) - 1ULL;
    return nodes;
}

/* Create a perfect tree with `depth` levels using a single contiguous block.
 * Returns root pointer (which points into the block start), or NULL on error.
 */
Node *make_perfect_single_block(unsigned depth) {
    uint64_t node_count = perfect_node_count(depth);
    if (node_count == 0) {
        if (depth == 0) return NULL;
        return NULL; // overflow or too large
    }

    // allocate contiguous array of Node
    Node *arr = malloc((size_t)node_count * sizeof(Node));
    if (!arr) return NULL;

    // initialize pointers (iterating in index order)
    // children indices for index i: left = 2*i+1, right = 2*i+2 (if < node_count)
    for (uint64_t i = 0; i < node_count; ++i) {
        uint64_t li = 2*i + 1;
        uint64_t ri = 2*i + 2;
        arr[i].left  = (li < node_count) ? &arr[li] : NULL;
        arr[i].right = (ri < node_count) ? &arr[ri] : NULL;
    }

    return &arr[0]; // root
}

/* Because we used a single contiguous allocation, free must be done by freeing
 * the pointer to the original block. The root is arr[0] so we can free(root).
 */
void free_single_block(Node *root) {
    free(root);
}

/* Count nodes using recursion (safe because tree height may be moderate).
 * If depth is large, consider iterative traversal to avoid deep recursion.
 */
uint64_t count_nodes(const Node *root) {
    if (!root) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

int main(void) {
    unsigned depth = 20; // watch memory: 2^20 -1 nodes (~1,048,575 nodes)
    uint64_t needed = perfect_node_count(depth);
    if (needed == 0) {
        fprintf(stderr, "Depth too large or invalid\n");
        return 1;
    }
    printf("Will allocate %" PRIu64 " nodes\n", needed);

    Node *root = make_perfect_single_block(depth);
    if (!root) {
        fprintf(stderr, "Allocation failed\n");
        return 1;
    }
    printf("Allocated contiguous perfect tree; counted nodes = %" PRIu64 "\n", count_nodes(root));
    free_single_block(root);
    return 0;
}
