#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <sstream>

/**
 * High-performance DNA Reverse Complement Processor
 * Optimized for speed and memory efficiency with SIMD-friendly operations
 */
class DNAReverseComplement {
private:
    // Fast lookup table using char array for O(1) access
    char complement_table[256];
    
    static constexpr size_t BUFFER_SIZE = 8192;
    static constexpr size_t LINE_WIDTH = 80;
    
public:
    DNAReverseComplement() {
        // Initialize complement table with default 'N'
        std::fill(complement_table, complement_table + 256, 'N');
        
        // Set up complement mappings (both upper and lower case)
        complement_table['A'] = complement_table['a'] = 'T';
        complement_table['T'] = complement_table['t'] = 'A';
        complement_table['U'] = complement_table['u'] = 'A';
        complement_table['C'] = complement_table['c'] = 'G';
        complement_table['G'] = complement_table['g'] = 'C';
        complement_table['M'] = complement_table['m'] = 'K';
        complement_table['R'] = complement_table['r'] = 'Y';
        complement_table['W'] = complement_table['w'] = 'W';
        complement_table['S'] = complement_table['s'] = 'S';
        complement_table['Y'] = complement_table['y'] = 'R';
        complement_table['K'] = complement_table['k'] = 'M';
        complement_table['V'] = complement_table['v'] = 'B';
        complement_table['H'] = complement_table['h'] = 'D';
        complement_table['D'] = complement_table['d'] = 'H';
        complement_table['B'] = complement_table['b'] = 'V';
        complement_table['N'] = complement_table['n'] = 'N';
    }
    
    /**
     * Generate reverse complement of DNA sequence
     * Optimized with in-place transformation and efficient iteration
     */
    std::string reverseComplement(const std::string& sequence) {
        std::string result;
        result.reserve(sequence.length());
        
        // Reverse iteration with complement lookup
        for (auto it = sequence.rbegin(); it != sequence.rend(); ++it) {
            if (*it != '\n' && *it != '\r' && *it != ' ') {
                result += complement_table[static_cast<unsigned char>(*it)];
            }
        }
        
        return result;
    }
    
    /**
     * Process FASTA format from stdin with optimized buffered reading
     */
    void processFASTAStream() {
        std::string line;
        std::string currentId;
        std::string currentDescription;
        std::vector<std::string> sequenceLines;
        
        // Reserve space to minimize reallocations
        line.reserve(256);
        sequenceLines.reserve(1000);
        
        try {
            while (std::getline(std::cin, line)) {
                if (line.empty()) continue;
                
                if (line[0] == '>') {
                    // Process previous sequence if exists
                    if (!currentId.empty()) {
                        writeReverseComplement(currentId, currentDescription, sequenceLines);
                    }
                    
                    // Parse new header
                    parseHeader(line, currentId, currentDescription);
                    sequenceLines.clear();
                    
                } else if (!currentId.empty()) {
                    // Accumulate sequence data
                    sequenceLines.emplace_back(std::move(line));
                }
            }
            
            // Process final sequence
            if (!currentId.empty()) {
                writeReverseComplement(currentId, currentDescription, sequenceLines);
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error processing FASTA file: " << e.what() << std::endl;
            std::exit(1);
        }
    }

private:
    /**
     * Parse FASTA header line to extract ID and description
     */
    void parseHeader(const std::string& headerLine, std::string& id, std::string& description) {
        size_t spacePos = headerLine.find(' ', 1);
        
        if (spacePos != std::string::npos) {
            id = headerLine.substr(1, spacePos - 1);
            description = headerLine.substr(spacePos + 1);
        } else {
            id = headerLine.substr(1);
            description.clear();
        }
    }
    
    /**
     * Write reverse complement sequence in FASTA format
     */
    void writeReverseComplement(const std::string& id, const std::string& description,
                               const std::vector<std::string>& sequenceLines) {
        // Combine all sequence lines efficiently
        std::string fullSequence;
        size_t totalLength = 0;
        
        // Calculate total length for reservation
        for (const auto& line : sequenceLines) {
            totalLength += line.length();
        }
        fullSequence.reserve(totalLength);
        
        // Concatenate sequence lines
        for (const auto& line : sequenceLines) {
            fullSequence += line;
        }
        
        // Generate reverse complement
        std::string revComp = reverseComplement(fullSequence);
        
        // Write header
        std::cout << '>' << id;
        if (!description.empty()) {
            std::cout << ' ' << description;
        }
        std::cout << '\n';
        
        // Write sequence in 80-character lines
        for (size_t i = 0; i < revComp.length(); i += LINE_WIDTH) {
            size_t lineEnd = std::min(i + LINE_WIDTH, revComp.length());
            std::cout.write(revComp.data() + i, lineEnd - i);
            std::cout << '\n';
        }
    }
};

/**
 * Main entry point
 */
int main() {
    // Optimize I/O performance
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    
    DNAReverseComplement processor;
    processor.processFASTAStream();
    
    return 0;
}