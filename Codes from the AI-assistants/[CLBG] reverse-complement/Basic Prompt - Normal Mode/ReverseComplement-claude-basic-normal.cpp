#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cctype>

class ReverseComplement {
private:
    // Complement lookup table for fast O(1) lookups
    char complement_table[256];
    
    void initialize_complement_table() {
        // Initialize all positions to identity
        for (int i = 0; i < 256; i++) {
            complement_table[i] = static_cast<char>(i);
        }
        
        // Set complement mappings (both upper and lower case)
        complement_table['A'] = complement_table['a'] = 'T';
        complement_table['T'] = complement_table['t'] = 'A';
        complement_table['U'] = complement_table['u'] = 'A';  // RNA
        complement_table['C'] = complement_table['c'] = 'G';
        complement_table['G'] = complement_table['g'] = 'C';
        
        // Ambiguous nucleotides
        complement_table['M'] = complement_table['m'] = 'K';  // A/C -> G/T
        complement_table['K'] = complement_table['k'] = 'M';  // G/T -> A/C
        complement_table['R'] = complement_table['r'] = 'Y';  // A/G -> C/T
        complement_table['Y'] = complement_table['y'] = 'R';  // C/T -> A/G
        complement_table['W'] = complement_table['w'] = 'W';  // A/T -> A/T
        complement_table['S'] = complement_table['s'] = 'S';  // C/G -> C/G
        complement_table['V'] = complement_table['v'] = 'B';  // A/C/G -> C/G/T
        complement_table['B'] = complement_table['b'] = 'V';  // C/G/T -> A/C/G
        complement_table['H'] = complement_table['h'] = 'D';  // A/C/T -> A/G/T
        complement_table['D'] = complement_table['d'] = 'H';  // A/G/T -> A/C/T
        complement_table['N'] = complement_table['n'] = 'N';  // Any -> Any
    }
    
    std::string reverse_complement_sequence(const std::string& sequence) {
        std::string result;
        result.reserve(sequence.length());  // Pre-allocate memory
        
        // Process sequence from end to beginning
        for (int i = sequence.length() - 1; i >= 0; i--) {
            result += complement_table[static_cast<unsigned char>(sequence[i])];
        }
        
        return result;
    }
    
    void output_sequence_lines(const std::string& sequence, int line_width = 80) {
        for (size_t i = 0; i < sequence.length(); i += line_width) {
            std::cout << sequence.substr(i, line_width) << '\n';
        }
    }

public:
    ReverseComplement() {
        initialize_complement_table();
    }
    
    void process_fasta_stream() {
        std::string line;
        std::string current_header;
        std::string current_sequence;
        
        // Use faster I/O
        std::ios_base::sync_with_stdio(false);
        std::cin.tie(nullptr);
        
        while (std::getline(std::cin, line)) {
            if (line.empty()) continue;
            
            if (line[0] == '>') {
                // Process previous sequence if exists
                if (!current_header.empty()) {
                    std::string rev_comp = reverse_complement_sequence(current_sequence);
                    std::cout << current_header << '\n';
                    output_sequence_lines(rev_comp);
                }
                
                // Start new sequence
                current_header = line;
                current_sequence.clear();
                current_sequence.reserve(10000);  // Reserve space for efficiency
            } else {
                // Remove whitespace and accumulate sequence
                for (char c : line) {
                    if (!std::isspace(c)) {
                        current_sequence += c;
                    }
                }
            }
        }
        
        // Process final sequence
        if (!current_header.empty()) {
            std::string rev_comp = reverse_complement_sequence(current_sequence);
            std::cout << current_header << '\n';
            output_sequence_lines(rev_comp);
        }
    }
    
    void generate_test_file(int target_size, const std::string& filename) {
        const std::vector<char> nucleotides = {
            'A', 'T', 'G', 'C', 'M', 'R', 'W', 'S', 
            'Y', 'K', 'V', 'H', 'D', 'B', 'N'
        };
        
        const int seq_length = 1000;
        const int num_sequences = target_size / seq_length;
        
        // Use C-style file I/O for better performance
        FILE* file = fopen(filename.c_str(), "w");
        if (!file) {
            std::cerr << "Error: Cannot create file " << filename << std::endl;
            return;
        }
        
        srand(time(nullptr));  // Seed random number generator
        
        for (int seq_num = 0; seq_num < num_sequences; seq_num++) {
            // Write header
            fprintf(file, ">sequence_%d Test sequence %d\n", seq_num + 1, seq_num + 1);
            
            // Generate and write sequence
            for (int pos = 0; pos < seq_length; pos++) {
                if (pos > 0 && pos % 80 == 0) {
                    fputc('\n', file);
                }
                char nucleotide = nucleotides[rand() % nucleotides.size()];
                fputc(nucleotide, file);
            }
            fputc('\n', file);
        }
        
        fclose(file);
        std::cout << "Generated " << filename << " with " << num_sequences 
                  << " sequences of " << seq_length << " bases each." << std::endl;
    }
};

int main(int argc, char* argv[]) {
    ReverseComplement processor;
    
    if (argc > 1) {
        // Generate test file
        try {
            int size = std::stoi(argv[1]);
            std::string filename = "input" + std::string(argv[1]) + ".txt";
            processor.generate_test_file(size, filename);
        } catch (const std::exception& e) {
            std::cerr << "Error: Invalid size argument" << std::endl;
            return 1;
        }
    } else {
        // Process FASTA from stdin
        try {
            processor.process_fasta_stream();
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
            return 1;
        }
    }
    
    return 0;
}

/*
COMPILATION AND USAGE:

Compile:
g++ -O3 -std=c++11 reverse_complement.cpp -o reverse_complement

Usage:
1. Generate test file:
   ./reverse_complement 25000000

2. Process FASTA file:
   ./reverse_complement < input.fasta > output.fasta

3. Performance test:
   ./reverse_complement 25000000 && time ./reverse_complement < input25000000.txt > /dev/null

ALGORITHM FEATURES:

1. **Optimized I/O**: 
   - Disabled C++ stream synchronization with C stdio
   - Untied cin from cout for faster input
   - Used C-style file I/O for test file generation

2. **Memory Efficiency**:
   - Pre-allocated string capacity to avoid reallocations
   - Streaming processing (no full file loading)
   - Minimal memory copying

3. **Lookup Table**:
   - 256-element array for O(1) complement lookup
   - Handles both uppercase and lowercase
   - Supports all IUPAC nucleotide codes

4. **Performance Optimizations**:
   - Single-pass reverse complement calculation
   - Efficient string operations with reserve()
   - Fast random number generation for test data

Expected performance: Can process ~100MB/second on modern hardware
*/