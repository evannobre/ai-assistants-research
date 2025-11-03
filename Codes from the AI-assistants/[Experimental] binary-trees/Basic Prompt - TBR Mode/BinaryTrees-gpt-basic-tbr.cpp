// compile: g++ -O2 -std=c++17 tree_vector.cpp -o tree_vector
#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>

uint64_t perfect_count(unsigned depth) {
    if (depth == 0) return 0;
    if (depth >= 64) return 0;
    return (1ULL << depth) - 1ULL;
}

int main() {
    unsigned depth = 10;
    uint64_t nodes = perfect_count(depth);
    if (nodes == 0) { std::cerr << "invalid depth\n"; return 1; }
    std::vector<char> storage(nodes * sizeof(void*)); // just reserve memory; no payloads
    std::cout << "Reserved " << nodes << " slots in vector (no values stored)\n";

    // Traversal using implicit indices: left = 2*i+1, right = 2*i+2
    // Example: count nodes iteratively using a stack of indices:
    uint64_t count = 0;
    std::vector<uint64_t> stack;
    stack.push_back(0); // root index
    while (!stack.empty()) {
        uint64_t i = stack.back(); stack.pop_back();
        ++count;
        uint64_t li = 2*i + 1, ri = 2*i + 2;
        if (ri < nodes) stack.push_back(ri);
        if (li < nodes) stack.push_back(li);
    }
    std::cout << "Counted nodes = " << count << "\n";
    return 0;
}
