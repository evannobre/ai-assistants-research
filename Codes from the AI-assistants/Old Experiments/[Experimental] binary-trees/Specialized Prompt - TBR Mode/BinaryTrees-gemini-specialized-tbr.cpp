#include <iostream> // For std::cout, std::endl
#include <memory>   // For std::unique_ptr
#include <cmath>    // For std::pow
#include <cstdint>  // For uintptr_t

// The Node structure. It stores NO value, only pointers to its children.
// The unique_ptr manages the memory of the child nodes automatically.
struct Node {
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;

    // A simple constructor to show when a node is created.
    Node() {
        // This is just for demonstration; in a real scenario, it could be empty.
        // std::cout << "Node allocated at address: " << this << std::endl;
    }

    // The destructor will be called automatically by unique_ptr,
    // triggering a chain reaction that deallocates the entire tree.
    ~Node() {
        // std::cout << "Node deallocated at address: " << this << std::endl;
    }
};

/**
 * @brief Recursively creates a perfect binary tree of a given height.
 *
 * @param height The desired height of the tree. A height of 0 is an empty tree,
 * a height of 1 is a single node.
 * @return A std::unique_ptr to the root of the newly created tree.
 */
std::unique_ptr<Node> createPerfectTree(int height) {
    // Base case: If height is 0 or less, we've reached a leaf's child, so return null.
    if (height <= 0) {
        return nullptr;
    }

    // Recursive step:
    // 1. Allocate a new node. This will be the root of the current subtree.
    auto node = std::make_unique<Node>();

    // 2. Recursively build the left and right subtrees with decremented height.
    node->left = createPerfectTree(height - 1);
    node->right = createPerfectTree(height - 1);

    // 3. Return the newly created node (and ownership of it).
    return node;
}

/**
 * @brief Performs an in-order traversal of the tree and prints each node's memory address.
 *
 * This function demonstrates that the tree structure exists by printing the unique
 * identifier of each node (its address in memory).
 *
 * @param node A reference to the unique_ptr of the current node.
 */
void printInOrder(const std::unique_ptr<Node>& node) {
    if (!node) {
        return;
    }
    printInOrder(node->left);
    // We cast the pointer to an integer type (uintptr_t) for printing.
    std::cout << "Node Address: 0x" << std::hex << reinterpret_cast<uintptr_t>(node.get()) << std::endl;
    printInOrder(node->right);
}


int main() {
    // Define the height of the perfect binary tree.
    int treeHeight = 4;

    std::cout << "Creating a perfect binary tree of height " << treeHeight << "..." << std::endl;

    // Create the tree. The 'root' variable now owns the entire tree structure.
    auto root = createPerfectTree(treeHeight);

    long long totalNodes = static_cast<long long>(std::pow(2, treeHeight)) - 1;
    std::cout << "Tree created successfully with " << totalNodes << " nodes." << std::endl;
    std::cout << "------------------------------------------" << std::endl;

    std::cout << "Performing in-order traversal and printing node addresses:" << std::endl;
    printInOrder(root);
    std::cout << "------------------------------------------" << std::endl;

    std::cout << "Program finished. Memory will be deallocated automatically as 'root' goes out of scope." << std::endl;
    
    // When main exits, `root` is destroyed, which automatically deallocates the entire tree.
    return 0;
}