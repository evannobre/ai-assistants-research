#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct Node {
    int value;
    struct Node *left;
    struct Node *right;
} Node;

Node **allocate_node_array(int totalNodes) {
    Node **nodes = malloc(totalNodes * sizeof(Node *));
    if (!nodes) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    return nodes;
}

Node *build_perfect_tree(int depth) {
    if (depth < 0) return NULL;

    int totalNodes = (1 << (depth + 1)) - 1;

    // 1. Allocate array of pointers
    Node **nodes = allocate_node_array(totalNodes);

    // 2. Allocate each node
    for (int i = 0; i < totalNodes; ++i) {
        nodes[i] = malloc(sizeof(Node));
        if (!nodes[i]) {
            perror("malloc");
            exit(EXIT_FAILURE);
        }
        nodes[i]->value = i;
        nodes[i]->left = nodes[i]->right = NULL;
    }

    // 3. Link children
    for (int i = 0; i < totalNodes; ++i) {
        int leftIndex  = 2 * i + 1;
        int rightIndex = 2 * i + 2;

        if (leftIndex < totalNodes)
            nodes[i]->left = nodes[leftIndex];
        if (rightIndex < totalNodes)
            nodes[i]->right = nodes[rightIndex];
    }

    Node *root = nodes[0];

    // Optionally free the array of pointers (not the nodes themselves)
    free(nodes);

    return root;
}
