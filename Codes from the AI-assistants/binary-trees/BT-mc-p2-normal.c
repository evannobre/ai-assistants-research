#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <errno.h>

typedef struct Node {
    struct Node *left;
    struct Node *right;
    uint64_t value;
} Node;

static int compute_node_count(int N, uint64_t *out_count) {
    if (N < 0 || N > 60) { // avoid shifting into UB
        return -1;
    }
    // nodes = 2^(N+1) - 1
    uint64_t level_plus_one = (uint64_t)N + 1;
    if (level_plus_one >= 63) { // avoid overflow of 1ULL << 63
        return -1;
    }
    uint64_t nodes = (1ULL << level_plus_one) - 1ULL;
    *out_count = nodes;
    return 0;
}

static int check_memory_budget(uint64_t node_count, size_t node_size) {
    // Choose a conservative budget: 6 GiB
    const uint64_t BUDGET_BYTES = 6ULL * 1024ULL * 1024ULL * 1024ULL;

    // Check multiplication overflow: node_count * node_size
    if (node_count > 0 && node_size > 0) {
        uint64_t max_safe = BUDGET_BYTES / node_size;
        if (node_count > max_safe) {
            return -1;
        }
    }
    return 0;
}

static Node *build_perfect_binary_tree(int N, uint64_t *out_node_count) {
    uint64_t node_count;
    if (compute_node_count(N, &node_count) != 0) {
        fprintf(stderr, "Invalid depth N=%d (overflow or too large).\n", N);
        return NULL;
    }

    size_t node_size = sizeof(Node);
    if (check_memory_budget(node_count, node_size) != 0) {
        fprintf(stderr,
                "Requested tree too large: %" PRIu64 " nodes, each %zu bytes.\n",
                node_count, node_size);
        return NULL;
    }

    uint64_t total_bytes = node_count * (uint64_t)node_size;
    printf("Allocating %" PRIu64 " nodes (~%" PRIu64 " bytes).\n",
           node_count, total_bytes);

    Node *nodes = (Node *)malloc(total_bytes);
    if (!nodes) {
        perror("malloc");
        return NULL;
    }

    // Initialize and wire children using heap-like indexing
    for (uint64_t i = 0; i < node_count; ++i) {
        uint64_t left_idx  = 2 * i + 1;
        uint64_t right_idx = 2 * i + 2;

        nodes[i].left  = (left_idx  < node_count) ? &nodes[left_idx]  : NULL;
        nodes[i].right = (right_idx < node_count) ? &nodes[right_idx] : NULL;
        nodes[i].value = i; // or any other initialization
    }

    if (out_node_count) {
        *out_node_count = node_count;
    }
    return nodes; // root is nodes[0]
}

// Simple traversal to ensure the compiler doesn't optimize away the tree
static uint64_t sum_values_inorder(const Node *node) {
    if (!node) return 0;
    return sum_values_inorder(node->left) +
           node->value +
           sum_values_inorder(node->right);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <depth N>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *endptr = NULL;
    errno = 0;
    long N_long = strtol(argv[1], &endptr, 10);
    if (errno != 0 || endptr == argv[1] || *endptr != '\0') {
        fprintf(stderr, "Invalid integer for N: '%s'\n", argv[1]);
        return EXIT_FAILURE;
    }
    if (N_long < 0 || N_long > 60) {
        fprintf(stderr, "Depth N must be between 0 and 60.\n");
        return EXIT_FAILURE;
    }
    int N = (int)N_long;

    uint64_t node_count = 0;
    Node *root = build_perfect_binary_tree(N, &node_count);
    if (!root) {
        return EXIT_FAILURE;
    }

    printf("Perfect binary tree of depth %d created with %" PRIu64 " nodes.\n",
           N, node_count);

    // Example usage: compute sum of all node values
    uint64_t sum = sum_values_inorder(root);
    printf("In-order sum of node values: %" PRIu64 "\n", sum);

    free(root); // single free for the whole tree
    return EXIT_SUCCESS;
}
