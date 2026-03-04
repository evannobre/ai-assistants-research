#include <iostream>
#include <memory>
#include <cstdlib>

// Tree node structure - same for leaf and interior nodes
struct Node {
    Node* left;
    Node* right;
    
    Node(Node* l = nullptr, Node* r = nullptr) : left(l), right(r) {}
    
    ~Node() {
        delete left;
        delete right;
    }
};

// Create a tree of given depth
Node* createTree(int depth) {
    if (depth == 0) {
        return new Node();
    }
    return new Node(createTree(depth - 1), createTree(depth - 1));
}

// Check tree exists by counting nodes
int checkTree(Node* node) {
    if (node->left == nullptr) {
        return 1;
    }
    return 1 + checkTree(node->left) + checkTree(node->right);
}

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? std::atoi(argv[1]) : 10;
    int minDepth = 4;
    int maxDepth = (minDepth + 2 > n) ? minDepth + 2 : n;
    int stretchDepth = maxDepth + 1;
    
    // Stretch memory - allocate and deallocate
    {
        Node* stretchTree = createTree(stretchDepth);
        std::cout << "stretch tree of depth " << stretchDepth 
                  << "\t check: " << checkTree(stretchTree) << std::endl;
        delete stretchTree;
    }
    
    // Allocate long-lived tree
    Node* longLivedTree = createTree(maxDepth);
    
    // Allocate, walk, and deallocate many bottom-up trees
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        int iterations = 1 << (maxDepth - depth + minDepth);
        int check = 0;
        
        for (int i = 1; i <= iterations; i++) {
            Node* tree = createTree(depth);
            check += checkTree(tree);
            delete tree;
        }
        
        std::cout << iterations << "\t trees of depth " << depth 
                  << "\t check: " << check << std::endl;
    }
    
    // Check long-lived tree still exists
    std::cout << "long lived tree of depth " << maxDepth 
              << "\t check: " << checkTree(longLivedTree) << std::endl;
    
    delete longLivedTree;
    
    return 0;
}
