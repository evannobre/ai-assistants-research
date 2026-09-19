#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cstdlib>

// -- 1. Naive Linear Congruential Generator State --
constexpr int32_t IM = 139968;
constexpr int32_t IA = 3877;
constexpr int32_t IC = 29573;
int32_t current_seed = 42;

// Calculates random number each time a nucleotide needs to be selected
inline float get_random(float max) {
    current_seed = (current_seed * IA + IC) % IM;
    return max * current_seed / IM;
}

// -- 2. Alphabet Structures --
struct Nucleotide {
    char c;
    float p;
};

// -- 3. Convert Expected Probabilities to Cumulative --
void make_cumulative(std::vector<Nucleotide>& nucleotides) {
    float cumulative = 0.0f;
    for (auto& n : nucleotides) {
        cumulative += n.p;
        n.p = cumulative;
    }
}

// -- 4. Generate Sequence by Copying --
void make_repeat_fasta(std::string_view id, std::string_view seq, int n) {
    std::cout << id << '\n';
    
    int seq_len = seq.length();
    int pos = 0;
    
    // Using a fixed buffer minimizes heap allocations during high-throughput I/O
    char buffer[61]; 
    int buf_idx = 0;
    
    for (int i = 0; i < n; ++i) {
        buffer[buf_idx++] = seq[pos];
        pos = (pos + 1) % seq_len;
        
        if (buf_idx == 60) {
            buffer[60] = '\n';
            std::cout.write(buffer, 61);
            buf_idx = 0;
        }
    }
    
    // Flush remaining characters
    if (buf_idx > 0) {
        buffer[buf_idx] = '\n';
        std::cout.write(buffer, buf_idx + 1);
    }
}

// -- 5. Generate Sequence by Weighted Random Selection --
void make_random_fasta(std::string_view id, const std::vector<Nucleotide>& cumulative_probs, int n) {
    std::cout << id << '\n';
    
    char buffer[61];
    int buf_idx = 0;
    
    for (int i = 0; i < n; ++i) {
        float r = get_random(1.0f);
        char selected = cumulative_probs.back().c; // Default fallback
        
        // Match random number against cumulative probabilities (Linear Search)
        for (const auto& nuc : cumulative_probs) {
            if (r < nuc.p) {
                selected = nuc.c;
                break;
            }
        }
        
        buffer[buf_idx++] = selected;
        
        if (buf_idx == 60) {
            buffer[60] = '\n';
            std::cout.write(buffer, 61);
            buf_idx = 0;
        }
    }
    
    if (buf_idx > 0) {
        buffer[buf_idx] = '\n';
        std::cout.write(buffer, buf_idx + 1);
    }
}

int main(int argc, char** argv) {
    // Standard back-end optimization: Untie C/C++ streams for raw write throughput
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n = 1000;
    if (argc > 1) {
        n = std::atoi(argv[1]);
    }

    constexpr std::string_view alu =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGA"
        "TCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACT"
        "AAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAG"
        "GCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCG"
        "CCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    std::vector<Nucleotide> iub = {
        {'a', 0.27f}, {'c', 0.12f}, {'g', 0.12f}, {'t', 0.27f},
        {'B', 0.02f}, {'D', 0.02f}, {'H', 0.02f}, {'K', 0.02f},
        {'M', 0.02f}, {'N', 0.02f}, {'R', 0.02f}, {'S', 0.02f},
        {'V', 0.02f}, {'W', 0.02f}, {'Y', 0.02f}
    };

    std::vector<Nucleotide> homosapiens = {
        {'a', 0.3029549426680f},
        {'c', 0.1979883004921f},
        {'g', 0.1975473066391f},
        {'t', 0.3015094502008f}
    };

    // Calculate probabilities once at startup
    make_cumulative(iub);
    make_cumulative(homosapiens);

    // Sequence generation sequence specified by the FASTA rules
    make_repeat_fasta(">ONE Homo sapiens alu", alu, n * 2);
    make_random_fasta(">TWO IUB ambiguity codes", iub, n * 3);
    make_random_fasta(">THREE Homo sapiens frequency", homosapiens, n * 5);

    return 0;
}