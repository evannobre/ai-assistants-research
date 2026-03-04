#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct TreeNode {
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

TreeNode* createPerfectTree(int height) {
    if (height <= 0) return NULL;
    
    int nodeCount = (1 << height) - 1;
    TreeNode* nodes = malloc(nodeCount * sizeof(TreeNode));
    
    // Build complete binary tree structure
    for (int i = 0; i < nodeCount; i++) {
        int left_idx = 2 * i + 1;
        int right_idx = 2 * i + 2;
        
        nodes[i].left = (left_idx < nodeCount) ? &nodes[left_idx] : NULL;
        nodes[i].right = (right_idx < nodeCount) ? &nodes[right_idx] : NULL;
    }
    
    return nodes;
}