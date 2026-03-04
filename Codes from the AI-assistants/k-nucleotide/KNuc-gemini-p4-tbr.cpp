/**
 * k-nucleotide.cpp
 * * Compile with: 
 * g++ -std=c++20 -O3 -march=native -pthread knucleotide.cpp -o knucleotide
 *
 * Usage:
 * ./knucleotide < input.txt
 */

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <algorithm>
#include <iomanip>
#include <future>
#include <thread>
#include <cstring>
#include <array>

// Mapping char to 2-bit integers: A=0, C=1, G=2, T=3
// Using a 256-array for fast O(1) lookups
static const std::array<uint8_t, 256> to_code = [] {
    std::array<uint8_t, 256> t{};
    t.fill(0); // Default
    t['A'] = 0; t['a'] = 0;
    t['C'] = 1; t['c'] = 1;
    t['G'] = 2; t['g'] = 2;
    t['T'] = 3; t['t'] = 3;
    return t;
}();

static const char to_char[] = {'A', 'C', 'G', 'T'};

// Helper to reverse map a packed integer back to string
std::string decode(uint64_t key, int k) {
    std::string s;
    s.resize(k);
    for (int i = 0; i < k; ++i) {
        // Extract 2 bits from the left (most significant for our packing logic)
        // Actually, we usually pack shifting left, so MSB is first char.
        // Let's decode from LSB to match the packing logic below.
        s[k - 1 - i] = to_char[key & 3];
        key >>= 2;
    }
    return s;
}

// Custom Hash for uint64_t to ensure 'std::unordered_map' is efficient
// Identity hash is usually fine for dense packed integers, but mixing helps collision resistance.
struct UInt64Hash {
    std::size_t operator()(uint64_t k) const {
        return std::hash<uint64_t>{}(k);
    }
};

using CountMap = std::unordered_map<uint64_t, uint32_t, UInt64Hash>;

// Task to process a chunk of the buffer
CountMap count_chunk(const std::vector<uint8_t>& buffer, size_t start, size_t end, int k) {
    CountMap counts;
    uint64_t mask = (k == 32) ? ~0ULL : (1ULL << (2 * k)) - 1;
    uint64_t key = 0;

    // Pre-load the first k-1 characters for the sliding window
    // We need to be careful with boundary conditions if start > 0
    size_t i = start;
    
    // Initialize window
    for (; i < start + k - 1 && i < end; ++i) {
        key = (key << 2) | buffer[i];
    }

    // Slide window
    for (; i < end; ++i) {
        key = ((key << 2) & mask) | buffer[i];
        counts[key]++;
    }

    return counts;
}

// Function to calculate counts for a specific k
// Uses parallelism to split the buffer
CountMap calculate_frequencies(const std::vector<uint8_t>& buffer, int k) {
    size_t total_len = buffer.size();
    if (total_len < k) return {};

    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 2;
    
    std::vector<std::future<CountMap>> futures;
    size_t chunk_size = total_len / num_threads;

    for (unsigned int t = 0; t < num_threads; ++t) {
        size_t start = t * chunk_size;
        size_t end = (t == num_threads - 1) ? total_len : start + chunk_size;
        
        // Ensure overlap for sliding window: 
        // The next chunk must theoretically re-read k-1 characters from the end of this chunk.
        // Instead, we just let this chunk run slightly into the next one's territory 
        // OR simpler: let this chunk run strictly [start, end).
        // BUT, k-mers starting at 'end-1' need data from 'end'.
        // Standard approach: chunk processes k-mers starting at [start, end).
        // This requires access to buffer up to end + k - 1.
        
        // Adjust end for loop logic inside task
        size_t process_limit = end; 
        if (t != num_threads - 1) {
             // For all but last thread, we process k-mers starting up to chunk boundary.
             // Access requires buffer[process_limit + k - 1] to be valid.
             // Since we pass the whole buffer reference, this is safe.
        } else {
             // Last thread stops at actual buffer end
             process_limit = total_len; // effectively stops processing at total_len
        }

        // We define the task to count k-mers starting at indices [start, process_limit)
        // However, the helper `count_chunk` iterates `i` as the *end* of the k-mer.
        // So `i` goes from `start + k - 1` to `process_limit + k - 1`?
        // Let's simplify: Pass exact range of *indices* to start k-mers at.
        // We will refactor count_chunk slightly to be clearer.
        
        futures.push_back(std::async(std::launch::async, [start, process_limit, k, &buffer]() {
            CountMap local_map;
            uint64_t mask = (k == 32) ? ~0ULL : (1ULL << (2 * k)) - 1;
            uint64_t key = 0;

            // Prime the rolling hash at 'start'
            // We need the k-mer ending at start+k-1
            if (start + k > buffer.size()) return local_map;

            for (size_t i = 0; i < k - 1; ++i) {
                key = (key << 2) | buffer[start + i];
            }

            // Iterate such that 'i' is the last character of the k-mer
            // The k-mer starts at (i - k + 1)
            // We want k-mers starting at [start, process_limit)
            // So last k-mer starts at process_limit - 1
            // Its last character is at (process_limit - 1) + k - 1 = process_limit + k - 2
            
            size_t loop_end = process_limit + k - 1;
            if (loop_end > buffer.size()) loop_end = buffer.size();

            for (size_t i = k - 1; i < (loop_end - start); ++i) {
                // i is relative to start in this loop logic for simplicity? 
                // No, let's use absolute index from buffer
                size_t buf_idx = start + i;
                key = ((key << 2) & mask) | buffer[buf_idx];
                local_map[key]++;
            }
            return local_map;
        }));
    }

    // Merge results
    CountMap global_map;
    for (auto& f : futures) {
        CountMap local = f.get();
        for (auto& pair : local) {
            global_map[pair.first] += pair.second;
        }
    }
    return global_map;
}

// 1. Write frequencies for len=1, 2
void write_frequencies(const std::vector<uint8_t>& buffer, int k) {
    CountMap map = calculate_frequencies(buffer, k);
    
    // Sort logic: Descending frequency, then Ascending key (alphabetical)
    // Convert to vector for sorting
    std::vector<std::pair<std::string, uint32_t>> items;
    uint32_t total = 0;
    for (auto& p : map) {
        items.push_back({decode(p.first, k), p.second});
        total += p.second;
    }

    std::sort(items.begin(), items.end(), [](const auto& a, const auto& b) {
        if (a.second != b.second) return a.second > b.second; // Desc frequency
        return a.first < b.first; // Asc key
    });

    std::cout << std::fixed << std::setprecision(3);
    for (const auto& item : items) {
        double percent = 100.0 * item.second / total;
        std::cout << item.first << " " << percent << '\n';
    }
    std::cout << '\n';
}

// 2. Write specific counts
void write_count(const std::vector<uint8_t>& buffer, const std::string& seq) {
    int k = seq.length();
    // Calculate full map (expensive but requested algorithm requires using same procedure)
    CountMap map = calculate_frequencies(buffer, k);
    
    // Encode the query sequence to find it
    uint64_t key = 0;
    for (char c : seq) {
        key = (key << 2) | to_code[(uint8_t)c];
    }
    
    std::cout << map[key] << "\t" << seq << '\n';
}

int main() {
    // Fast I/O
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    std::string line;
    std::vector<uint8_t> sequence;
    
    // 1. Read input until >THREE
    while (std::getline(std::cin, line)) {
        if (line.substr(0, 6) == ">THREE") break;
    }

    // 2. Read Sequence THREE
    // Reserve memory to prevent reallocation overhead. 
    // We expect large input, so we might guess or just let vector grow exponentially.
    sequence.reserve(25000000); 

    while (std::getline(std::cin, line)) {
        if (line.empty() || line[0] == '>') break; // End of sequence or next section
        // Transform and append
        for (char c : line) {
            if (c != '\n' && c != '\r') {
                sequence.push_back(to_code[(uint8_t)c]);
            }
        }
    }

    // 3. Execute Tasks
    
    // Count 1-nucleotide and 2-nucleotide sequences
    write_frequencies(sequence, 1);
    write_frequencies(sequence, 2);

    // Count specific sequences
    std::vector<std::string> targets = {
        "GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"
    };

    for (const auto& t : targets) {
        write_count(sequence, t);
    }

    return 0;
}