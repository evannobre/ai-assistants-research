#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>
#include <future>
#include <thread>
#include <cstring>

// Mapping char to 2-bit values: A=0, C=1, T=2, G=3
// using a lookup array for speed.
static const int8_t to_code[256] = {
    ['A'] = 0, ['a'] = 0,
    ['C'] = 1, ['c'] = 1,
    ['T'] = 2, ['t'] = 2,
    ['G'] = 3, ['g'] = 3
};

static const char from_code[] = "ACTG";

// Function to convert a compressed key back to string
std::string decode(uint64_t key, int k) {
    std::string s(k, ' ');
    for (int i = 0; i < k; ++i) {
        s[k - 1 - i] = from_code[key & 3];
        key >>= 2;
    }
    return s;
}

// Function to convert string key to compressed uint64
uint64_t encode(const std::string& s) {
    uint64_t key = 0;
    for (char c : s) {
        key = (key << 2) | to_code[(unsigned char)c];
    }
    return key;
}

// ----------------------------------------------------------------------------
// Core Algorithm: Update Hash Table
// ----------------------------------------------------------------------------
// Reads the input string with a specific offset (reading-frame).
// Updates a local hash table with counts.
using CountMap = std::unordered_map<uint64_t, uint32_t>;

CountMap count_nucleotides(const std::string& input, int k, int frame) {
    CountMap counts;
    
    // Mask to keep only the bits relevant for k nucleotides (2 bits per char)
    // Example: for k=2, mask is 1111 binary (15 decimal)
    uint64_t mask = (k == 32) ? ~0ULL : ((1ULL << (2 * k)) - 1);
    uint64_t key = 0;

    const size_t size = input.size();
    
    // Pre-load the first k-1 nucleotides into the rolling key
    // We start at 'frame' offset.
    if (frame + k > size) return counts;

    for (int i = frame; i < frame + k - 1; ++i) {
        key = (key << 2) | to_code[(unsigned char)input[i]];
    }

    // Rolling hash loop
    for (int i = frame + k - 1; i < size; i += k) {
        // Shift left, add new char, mask to size
        key = ((key << 2) | to_code[(unsigned char)input[i]]) & mask;
        
        // Native hash map lookup and update
        counts[key]++;
    }
    
    return counts;
}

// Helper to aggregate results from multiple reading frames
CountMap calculate_total_counts(const std::string& input, int k) {
    std::vector<std::future<CountMap>> futures;
    
    // Launch a task for each reading frame (0 to k-1)
    for (int i = 0; i < k; ++i) {
        futures.push_back(std::async(std::launch::async, count_nucleotides, std::cref(input), k, i));
    }

    CountMap total_counts;
    for (auto& f : futures) {
        CountMap part = f.get();
        for (const auto& [key, count] : part) {
            total_counts[key] += count;
        }
    }
    return total_counts;
}

// ----------------------------------------------------------------------------
// Output Formatting
// ----------------------------------------------------------------------------

void write_frequencies(const std::string& input, int k) {
    CountMap counts = calculate_total_counts(input, k);
    
    uint64_t total = 0;
    std::vector<std::pair<uint64_t, uint32_t>> sorted_list;
    
    for (const auto& entry : counts) {
        total += entry.second;
        sorted_list.push_back(entry);
    }

    // Sort: Descending frequency, then Ascending key (alphabetical)
    std::sort(sorted_list.begin(), sorted_list.end(), [](const auto& a, const auto& b) {
        if (a.second != b.second) return a.second > b.second;
        // Since we mapped A=0, C=1... numerical order of key equals alphabetical order of string
        return a.first < b.first; 
    });

    std::cout << std::fixed << std::setprecision(3);
    for (const auto& p : sorted_list) {
        std::cout << decode(p.first, k) << " " << (100.0 * p.second / total) << "\n";
    }
    std::cout << "\n";
}

void write_count(const std::string& input, const std::string& sequence) {
    int k = sequence.length();
    CountMap counts = calculate_total_counts(input, k);
    
    uint64_t key = encode(sequence);
    std::cout << counts[key] << "\t" << sequence << "\n";
}

// ----------------------------------------------------------------------------
// Main Driver
// ----------------------------------------------------------------------------
int main() {
    // 1. Optimize I/O
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    // 2. Read Input (Extract sequence THREE)
    std::string line;
    std::string sequence;
    
    // We reserve a large buffer to minimize reallocations
    sequence.reserve(25000000); 

    bool reading_three = false;
    while (std::getline(std::cin, line)) {
        if (line[0] == '>') {
            if (line.substr(1, 5) == "THREE") {
                reading_three = true;
                continue;
            } else if (reading_three) {
                // If we were reading THREE and hit another header, we are done
                break;
            }
        }
        
        if (reading_three && line[0] != ';') {
            // Append line, stripping newline (getline does this automatically)
            // But we must convert to uppercase to be safe, though benchmark input is usually clean.
            // Using logic from standard implementations: simply append.
            sequence.append(line);
        }
    }
    
    // Transform to uppercase just in case
    std::transform(sequence.begin(), sequence.end(), sequence.begin(), ::toupper);

    // 3. Execute Tasks
    
    // Frequencies for 1-mer and 2-mer
    write_frequencies(sequence, 1);
    write_frequencies(sequence, 2);

    // Specific counts
    std::vector<std::string> targets = {
        "GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"
    };

    for (const auto& target : targets) {
        write_count(sequence, target);
    }

    return 0;
}