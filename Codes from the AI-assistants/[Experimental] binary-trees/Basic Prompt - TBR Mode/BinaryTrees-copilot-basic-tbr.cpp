#include <cstddef>
#include <new>
#include <memory>
#include <iostream>
#include <cassert>

// Node contains only left/right pointers, no payload value.
struct Node {
    Node* left;
    Node* right;
};

class PerfectTree {
public:
    // height: root at height H (H = 0 -> single node)
    explicit PerfectTree(std::size_t height)
        : height_(height), count_(calc_count(height)) 
    {
        // allocate raw memory for count_ Node objects without invoking constructors
        buffer_ = static_cast<Node*>(::operator new[](count_ * sizeof(Node)));
        build_tree();
    }

    ~PerfectTree() noexcept {
        // explicitly destroy pointer fields if needed (trivial here), then free memory
        ::operator delete[](buffer_);
    }

    Node* root() const noexcept { return (count_ > 0) ? &buffer_[0] : nullptr; }
    std::size_t size() const noexcept { return count_; }

private:
    std::size_t height_;
    std::size_t count_;
    Node* buffer_;

    static std::size_t calc_count(std::size_t h) {
        return (h < (sizeof(std::size_t) * 8)) ? ((std::size_t(1) << (h + 1)) - 1) : 0;
    }

    void build_tree() {
        if (count_ == 0) return;
        // Layout: treat buffer as array indexed in breadth-first order (heap-like).
        // For index i, left child index = 2*i + 1, right = 2*i + 2 if those indices < count_.
        for (std::size_t i = 0; i < count_; ++i) {
            std::size_t li = 2 * i + 1;
            std::size_t ri = 2 * i + 2;
            buffer_[i].left  = (li < count_) ? &buffer_[li] : nullptr;
            buffer_[i].right = (ri < count_) ? &buffer_[ri] : nullptr;
        }
    }
};

// Example traversal to verify structure without storing values
void print_structure(Node* root) {
    if (!root) return;
    // simple preorder printing of pointer addresses
    std::cout << root << " L=" << root->left << " R=" << root->right << "\n";
    print_structure(root->left);
    print_structure(root->right);
}

int main() {
    std::size_t H = 3; // change height as desired
    PerfectTree tree(H);
    assert(tree.size() == (std::size_t(1) << (H + 1)) - 1);
    std::cout << "Created perfect tree with nodes: " << tree.size() << "\n";
    print_structure(tree.root());
    return 0;
}