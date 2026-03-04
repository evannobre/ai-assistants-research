#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct Node {
    struct Node* left;
    struct Node* right;
} Node;

static Node* new_node(Node* left, Node* right) {
    Node* n = (Node*)malloc(sizeof(Node));
    if (!n) { perror("malloc"); exit(1); }
    n->left = left;
    n->right = right;
    return n;
}

static Node* make_tree(int depth) {
    if (depth <= 0) return new_node(NULL, NULL);
    return new_node(make_tree(depth - 1), make_tree(depth - 1));
}

static int32_t check_tree(const Node* n) {
    if (!n->left) return 1;
    return 1 + check_tree(n->left) + check_tree(n->right);
}

static void free_tree(Node* n) {
    if (!n) return;
    free_tree(n->left);
    free_tree(n->right);
    free(n);
}

static int max_int(int a, int b) { return a > b ? a : b; }

static int pow2_int(int e) { return 1 << e; } // e small enough for typical benchmark ranges

int main(int argc, char** argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 10;

    const int minDepth = 4;
    const int maxDepth = max_int(minDepth + 2, N);
    const int stretchDepth = maxDepth + 1;

    // Stretch tree
    Node* stretch = make_tree(stretchDepth);
    int32_t stretchCheck = check_tree(stretch);
    printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck);
    free_tree(stretch);

    // Long-lived tree
    Node* longLived = make_tree(maxDepth);

    // Many short-lived trees
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        int iterations = pow2_int(maxDepth - depth + minDepth);
        int32_t sum = 0;

        for (int i = 0; i < iterations; i++) {
            Node* t = make_tree(depth);
            sum += check_tree(t);
            free_tree(t);
        }

        printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, sum);
    }

    int32_t longCheck = check_tree(longLived);
    printf("long lived tree of depth %d\t check: %d\n", maxDepth, longCheck);
    free_tree(longLived);

    return 0;
}
