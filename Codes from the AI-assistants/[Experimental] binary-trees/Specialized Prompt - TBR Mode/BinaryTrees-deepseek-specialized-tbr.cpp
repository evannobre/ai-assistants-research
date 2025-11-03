#include <iostream>
#include <memory>
#include <cmath>
#include <queue>
#include <vector>

class PerfectBalancedTree {
private:
    struct TreeNode {
        std::unique_ptr<TreeNode> left;
        std::unique_ptr<TreeNode> right;
        // No value stored - memory allocation only
    };

    std::unique_ptr<TreeNode> root;
    size_t node_count;

public:
    explicit PerfectBalancedTree(size_t height) : node_count(0) {
        if (height == 0) return;
        
        // Calculate total nodes for perfect tree: 2^height - 1
        node_count = (1ULL << height) - 1;
        
        // Build tree using level-order construction
        root = buildPerfectTree(height);
        
        std::cout << "Created perfect balanced tree with " << node_count 
                  << " nodes (height: " << height << ")\n";
        std::cout << "Memory allocated: ~" << (node_count * sizeof(TreeNode)) 
                  << " bytes\n";
    }

private:
    std::unique_ptr<TreeNode> buildPerfectTree(size_t height) {
        if (height == 0) return nullptr;

        std::queue<TreeNode*> queue;
        std::vector<std::unique_ptr<TreeNode>> nodes;
        
        // Pre-allocate all nodes
        for (size_t i = 0; i < node_count; ++i) {
            nodes.push_back(std::make_unique<TreeNode>());
        }
        
        // Build tree structure using level-order traversal
        root = std::move(nodes[0]);
        queue.push(root.get());
        
        size_t current_index = 1;
        
        while (!queue.empty() && current_index < node_count) {
            TreeNode* current = queue.front();
            queue.pop();
            
            // Assign left child
            if (current_index < node_count) {
                current->left = std::move(nodes[current_index]);
                queue.push(current->left.get());
                current_index++;
            }
            
            // Assign right child
            if (current_index < node_count) {
                current->right = std::move(nodes[current_index]);
                queue.push(current->right.get());
                current_index++;
            }
        }
        
        return std::move(root);
    }

    // Alternative recursive implementation (commented for reference)
    std::unique_ptr<TreeNode> buildPerfectTreeRecursive(size_t height) {
        if (height == 0) return nullptr;
        
        auto node = std::make_unique<TreeNode>();
        node->left = buildPerfectTreeRecursive(height - 1);
        node->right = buildPerfectTreeRecursive(height - 1);
        
        return node;
    }

public:
    // Memory-efficient traversal using Morris-like approach
    void traverseStructure() {
        std::cout << "Tree structure (L=Left, R=Right): ";
        traverseStructure(root.get());
        std::cout << "\n";
    }

private:
    void traverseStructure(TreeNode* node) {
        if (!node) return;
        
        std::cout << "N"; // Node marker
        if (node->left || node->right) {
            std::cout << "(";
            traverseStructure(node->left.get());
            if (node->left && node->right) std::cout << ",";
            traverseStructure(node->right.get());
            std::cout << ")";
        }
    }

public:
    // Calculate memory usage
    size_t getMemoryUsage() const {
        return node_count * sizeof(TreeNode);
    }
    
    size_t getNodeCount() const {
        return node_count;
    }
};

int main() {
    // System specification consideration
    const size_t MAX_RAM = 8ULL * 1024 * 1024 * 1024; // 8 GB
    const size_t NODE_SIZE = sizeof(PerfectBalancedTree::TreeNode);
    const size_t MAX_NODES = MAX_RAM / NODE_SIZE;
    
    std::cout << "System Specifications:\n";
    std::cout << "- RAM: 8 GB\n";
    std::cout << "- SSD: 256 GB\n";
    std::cout << "- Node size: " << NODE_SIZE << " bytes\n";
    std::cout << "- Theoretical max nodes: " << MAX_NODES << "\n\n";
    
    // Create trees of different sizes for demonstration
    std::vector<size_t> heights = {3, 4, 5, 10};
    
    for (size_t height : heights) {
        size_t node_count = (1ULL << height) - 1;
        size_t memory_usage = node_count * sizeof(PerfectBalancedTree::TreeNode);
        
        // Safety check - don't allocate more than 1GB for demo
        if (memory_usage > 1024 * 1024 * 1024) {
            std::cout << "Skipping height " << height << " (requires " 
                      << memory_usage / (1024 * 1024) << " MB)\n";
            continue;
        }
        
        PerfectBalancedTree tree(height);
        tree.traverseStructure();
        std::cout << "Memory used: " << tree.getMemoryUsage() / 1024 
                  << " KB\n\n";
    }
    
    return 0;
}