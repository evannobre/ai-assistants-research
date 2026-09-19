#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>

int main() {
    // 1. Untie streams to maximize SSD read throughput
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    // 2. Build O(1) Lookup Table for complement mappings
    char comp[256];
    for (int i = 0; i < 256; ++i) {
        comp[i] = static_cast<char>(i);
    }
    
    auto set_comp = [&comp](char a, char b) {
        comp[static_cast<unsigned char>(a)] = b;
        comp[static_cast<unsigned char>(std::tolower(a))] = b;
    };
    
    // Standard IUPAC nucleotide code complements
    set_comp('A', 'T'); set_comp('C', 'G'); set_comp('G', 'C');
    set_comp('T', 'A'); set_comp('U', 'A'); set_comp('M', 'K');
    set_comp('R', 'Y'); set_comp('W', 'W'); set_comp('S', 'S');
    set_comp('Y', 'R'); set_comp('K', 'M'); set_comp('V', 'B');
    set_comp('H', 'D'); set_comp('D', 'H'); set_comp('B', 'V');
    set_comp('N', 'N');

    std::string line;
    std::string header;
    std::string sequence;
    
    // Reserve memory to prevent expensive runtime reallocations 
    sequence.reserve(25000000);

    auto process_sequence = [&]() {
        if (sequence.empty()) return;
        
        std::cout << header << '\n';
        
        // 3. Two-Pointer Approach: Reverse and complement in one pass
        size_t len = sequence.length();
        if (len > 0) {
            size_t left = 0;
            size_t right = len - 1;
            while (left < right) {
                char cl = comp[static_cast<unsigned char>(sequence[left])];
                char cr = comp[static_cast<unsigned char>(sequence[right])];
                sequence[left] = cr;
                sequence[right] = cl;
                left++;
                right--;
            }
            // Handle the exact middle character if length is odd
            if (left == right) {
                sequence[left] = comp[static_cast<unsigned char>(sequence[left])];
            }
        }
        
        // 4. Output enforcing the 60 characters per line rule
        for (size_t i = 0; i < len; i += 60) {
            size_t chunk = std::min<size_t>(60, len - i);
            std::cout.write(sequence.data() + i, chunk);
            std::cout << '\n';
        }
        
        // Clear size but keep capacity for the next block
        sequence.clear();
    };

    // 5. Read from stdin block by block
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (line[0] == '>') {
            process_sequence();
            header = line;
        } else {
            sequence.append(line);
        }
    }
    
    // Ensure the final block in the file is processed
    process_sequence();
    
    return 0;
}