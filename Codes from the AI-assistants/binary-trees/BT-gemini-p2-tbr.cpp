#include <iostream>
#include <sys/mman.h> // Native Linux Memory Management
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdint>
#include <cmath>
#include <stdexcept>

// ---------------------------------------------------------
// 1. Define the Node
// On 64-bit Ubuntu, pointers are 8 bytes.
// Struct size: 16 bytes.
// ---------------------------------------------------------
struct Node {
    Node* left;
    Node* right;
};

// ---------------------------------------------------------
// 2. The Linear Arena Allocator
// Manages a contiguous block of memory.
// ---------------------------------------------------------
class ArenaAllocator {
private:
    uint8_t* memory_block;
    size_t offset;
    size_t total_size;

public:
    ArenaAllocator(size_t size_in_bytes) : offset(0), total_size(size_in_bytes) {
        // Use native Linux mmap for large allocation.
        // MAP_ANONYMOUS | MAP_PRIVATE: Allocates memory not backed by a file, private to this process.
        // PROT_READ | PROT_WRITE: We can read and write to this memory.
        void* ptr = mmap(nullptr, total_size, 
                         PROT_READ | PROT_WRITE, 
                         MAP_PRIVATE | MAP_ANONYMOUS, 
                         -1, 0);

        if (ptr == MAP_FAILED) {
            throw std::runtime_error("mmap failed: Not enough memory available.");
        }

        memory_block = static_cast<uint8_t*>(ptr);
    }

    ~ArenaAllocator() {
        // Return memory to OS
        munmap(memory_block, total_size);
    }

    // The "Bump Pointer" allocation - Extremely fast O(1)
    Node* allocate() {
        if (offset + sizeof(Node) > total_size) {
            throw std::runtime_error("Arena Out of Memory!");
        }
        Node* node = reinterpret_cast<Node*>(memory_block + offset);
        offset += sizeof(Node);
        return node;
    }
    
    size_t get_used_memory() const {
        return offset;
    }
};

// ---------------------------------------------------------
// 3. Tree Generation Logic
// ---------------------------------------------------------
Node* create_tree(ArenaAllocator& arena, int depth) {
    Node* node = arena.allocate();
    
    if (depth > 0) {
        node->left = create_tree(arena, depth - 1);
        node->right = create_tree(arena, depth - 1);
    } else {
        node->left = nullptr;
        node->right = nullptr;
    }
    
    return node;
}

// ---------------------------------------------------------
// 4. Main Execution
// ---------------------------------------------------------
int main() {
    // Calculated Max Depth for 8GB RAM (approx 4.3 GB usage)
    const int N = 27; 
    
    // Calculate exact nodes: 2^(N+1) - 1
    // We use size_t to prevent integer overflow
    size_t num_nodes = (static_cast<size_t>(1) << (N + 1)) - 1;
    size_t required_memory = num_nodes * sizeof(Node);

    // Convert to Gigabytes for display
    double size_gb = required_memory / (1024.0 * 1024.0 * 1024.0);

    std::cout << "--- Binary Tree Memory Allocator ---" << std::endl;
    std::cout << "Target Depth: " << N << std::endl;
    std::cout << "Total Nodes:  " << num_nodes << std::endl;
    std::cout << "Node Size:    " << sizeof(Node) << " bytes" << std::endl;
    std::cout << "Required RAM: " << size_gb << " GB" << std::endl;
    std::cout << "Allocating Arena via mmap..." << std::endl;

    try {
        ArenaAllocator arena(required_memory);
        
        std::cout << "Arena allocated. Building tree..." << std::endl;
        
        // Build the tree
        // Note: Recursion depth of 27 is fine for stack (default is usually 8MB)
        Node* root = create_tree(arena, N);

        std::cout << "Tree successfully built in memory." << std::endl;
        std::cout << "Root Node Address: " << root << std::endl;
        std::cout << "Total Memory Used: " << arena.get_used_memory() << " bytes" << std::endl;
        
        // Accessing a deep node to prove structure integrity
        // Just traversing Left -> Left -> ...
        Node* current = root;
        int depth_check = 0;
        while(current->left != nullptr) {
            current = current->left;
            depth_check++;
        }
        std::cout << "Traversal Check - Depth reached: " << depth_check << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}