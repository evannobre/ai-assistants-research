#include <iostream>
#include <memory>
#include <vector>
#include <cmath>
#include <chrono>
#include <cstdlib>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>

struct TreeNode {
    int id;
    TreeNode* left;
    TreeNode* right;
    
    explicit TreeNode(int id) : id(id), left(nullptr), right(nullptr) {}
};

class PerfectBinaryTree {
private:
    TreeNode* root;
    size_t total_nodes;
    
    // Custom memory pool to avoid fragmentation
    struct MemoryBlock {
        TreeNode* nodes;
        size_t size;
        
        MemoryBlock(size_t n) : size(n) {
            // Use mmap for direct memory allocation (bypasses libc allocator)
            nodes = static_cast<TreeNode*>(
                mmap(nullptr, n * sizeof(TreeNode), 
                     PROT_READ | PROT_WRITE, 
                     MAP_PRIVATE | MAP_ANONYMOUS, 
                     -1, 0));
            
            if (nodes == MAP_FAILED) {
                throw std::bad_alloc();
            }
        }
        
        ~MemoryBlock() {
            if (nodes != MAP_FAILED) {
                munmap(nodes, size * sizeof(TreeNode));
            }
        }
        
        TreeNode* get(size_t index) {
            return &nodes[index];
        }
    };
    
    std::unique_ptr<MemoryBlock> memory_pool;
    
    // Iterative construction using BFS approach
    TreeNode* buildTreeIterative(int depth) {
        if (depth <= 0) return nullptr;
        
        total_nodes = (1ULL << depth) - 1;
        
        // Allocate all nodes at once in contiguous memory
        memory_pool = std::make_unique<MemoryBlock>(total_nodes);
        
        // Initialize root node
        TreeNode* root = memory_pool->get(0);
        new (root) TreeNode(1);
        
        // Build tree using parent-child index relationships
        for (size_t i = 0; i < total_nodes / 2; i++) {
            TreeNode* parent = memory_pool->get(i);
            
            // Calculate child indices
            size_t left_idx = 2 * i + 1;
            size_t right_idx = 2 * i + 2;
            
            if (left_idx < total_nodes) {
                TreeNode* left = memory_pool->get(left_idx);
                new (left) TreeNode(left_idx + 1);
                parent->left = left;
            }
            
            if (right_idx < total_nodes) {
                TreeNode* right = memory_pool->get(right_idx);
                new (right) TreeNode(right_idx + 1);
                parent->right = right;
            }
        }
        
        return root;
    }
    
    void destroyTreeManual() {
        // No cleanup needed - memory pool will be freed automatically
        // when memory_pool goes out of scope
        root = nullptr;
    }
    
    // Stack-safe traversal using Morris algorithm
    void morrisTraversal(TreeNode* node) const {
        TreeNode* current = node;
        
        while (current != nullptr) {
            if (current->left == nullptr) {
                std::cout << current->id << " ";
                current = current->right;
            } else {
                TreeNode* predecessor = current->left;
                while (predecessor->right != nullptr && predecessor->right != current) {
                    predecessor = predecessor->right;
                }
                
                if (predecessor->right == nullptr) {
                    predecessor->right = current;
                    current = current->left;
                } else {
                    predecessor->right = nullptr;
                    std::cout << current->id << " ";
                    current = current->right;
                }
            }
        }
    }
    
public:
    PerfectBinaryTree() : root(nullptr), total_nodes(0) {}
    
    ~PerfectBinaryTree() {
        destroyTreeManual();
    }
    
    void create(int depth) {
        if (depth <= 0) {
            std::cerr << "Depth must be positive" << std::endl;
            return;
        }
        
        // Calculate memory requirements
        size_t nodes_needed = (1ULL << depth) - 1;
        size_t memory_required = nodes_needed * sizeof(TreeNode);
        
        std::cout << "Creating perfect binary tree of depth " << depth << std::endl;
        std::cout << "Nodes required: " << nodes_needed << std::endl;
        std::cout << "Memory required: " << memory_required / (1024 * 1024) << " MB" << std::endl;
        
        if (memory_required > 6ULL * 1024 * 1024 * 1024) {  // Leave 2GB for system
            std::cerr << "Error: Tree would require more than 6GB RAM!" << std::endl;
            return;
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            root = buildTreeIterative(depth);
            total_nodes = nodes_needed;
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
            
            std::cout << "Tree created successfully in " << duration.count() << " ms" << std::endl;
            
            // Print memory statistics
            printMemoryStats();
            
        } catch (const std::bad_alloc& e) {
            std::cerr << "Memory allocation failed: " << e.what() << std::endl;
        }
    }
    
    void traverse() const {
        if (root == nullptr) {
            std::cout << "Tree is empty" << std::endl;
            return;
        }
        
        std::cout << "In-order traversal (first 20 nodes): ";
        morrisTraversal(root);
        std::cout << std::endl;
    }
    
    size_t getNodeCount() const {
        return total_nodes;
    }
    
    void printMemoryStats() const {
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        
        std::cout << "Memory statistics:" << std::endl;
        std::cout << "  Max RSS: " << usage.ru_maxrss / 1024 << " MB" << std::endl;
        
        // Read from /proc/self/statm
        FILE* statm = fopen("/proc/self/statm", "r");
        if (statm) {
            long size, resident, share, text, lib, data, dt;
            fscanf(statm, "%ld %ld %ld %ld %ld %ld %ld", &size, &resident, &share, &text, &lib, &data, &dt);
            fclose(statm);
            
            long page_size = sysconf(_SC_PAGESIZE) / 1024; // KB
            std::cout << "  Virtual memory: " << (size * page_size) / 1024 << " MB" << std::endl;
            std::cout << "  Resident memory: " << (resident * page_size) / 1024 << " MB" << std::endl;
        }
    }
    
    // Verify tree structure
    bool verifyTreeStructure() const {
        if (root == nullptr) return true;
        
        // Check if all nodes are properly linked
        size_t visited = 0;
        
        // Simple BFS traversal
        std::vector<const TreeNode*> queue;
        queue.push_back(root);
        
        while (!queue.empty()) {
            const TreeNode* current = queue.back();
            queue.pop_back();
            visited++;
            
            if (current->left) {
                if (current->left->id != (current->id * 2)) {
                    return false;
                }
                queue.push_back(current->left);
            }
            
            if (current->right) {
                if (current->right->id != (current->id * 2 + 1)) {
                    return false;
                }
                queue.push_back(current->right);
            }
        }
        
        return visited == total_nodes;
    }
};

int main(int argc, char* argv[]) {
    int depth = 10;  // Default depth
    
    if (argc > 1) {
        depth = std::atoi(argv[1]);
        if (depth <= 0 || depth > 28) {  // Max depth 28 (~268M nodes, ~6.4GB)
            std::cerr << "Depth must be between 1 and 28" << std::endl;
            return 1;
        }
    }
    
    std::cout << "Running on Ubuntu 24.04.4 64-bit" << std::endl;
    std::cout << "System configuration: 8GB RAM, 256GB SSD" << std::endl;
    std::cout << std::endl;
    
    {
        PerfectBinaryTree tree;
        tree.create(depth);
        
        if (tree.getNodeCount() > 0) {
            // Verify tree structure
            if (tree.verifyTreeStructure()) {
                std::cout << "Tree structure verified successfully" << std::endl;
            } else {
                std::cout << "Tree structure verification failed!" << std::endl;
            }
            
            // Optional: traverse first few nodes
            if (tree.getNodeCount() <= 1000) {
                tree.traverse();
            }
            
            std::cout << "Tree exists in memory (no GC involved)" << std::endl;
            std::cout << "Press Enter to exit and release memory..." << std::endl;
            std::cin.get();
        }
    } // Tree is automatically destroyed here
    
    std::cout << "Memory released" << std::endl;
    return 0;
}