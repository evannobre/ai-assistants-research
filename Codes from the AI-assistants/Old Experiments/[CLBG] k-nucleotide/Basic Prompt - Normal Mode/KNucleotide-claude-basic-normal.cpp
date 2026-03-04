#include <iostream>
#include <unordered_map>
#include <string>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <sstream>

/**
 * K-nucleotide frequency analysis implementation
 * Reads FASTA format from stdin and analyzes DNA sequence THREE
 */

std::string readFastaSequenceThree() {
    std::unordered_map<std::string, std::string> sequences;
    std::string currentSeq;
    std::string currentData;
    std::string line;
    
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        
        if (line[0] == '>') {
            if (!currentSeq.empty()) {
                sequences[currentSeq] = currentData;
            }
            currentSeq = line.substr(1); // Remove '>' prefix
            currentData.clear();
        } else {
            // Convert to uppercase
            std::transform(line.begin(), line.end(), line.begin(), ::toupper);
            currentData += line;
        }
    }
    
    // Don't forget the last sequence
    if (!currentSeq.empty()) {
        sequences[currentSeq] = currentData;
    }
    
    // Extract sequence THREE
    for (const auto& pair : sequences) {
        std::string upperName = pair.first;
        std::transform(upperName.begin(), upperName.end(), upperName.begin(), ::toupper);
        if (upperName.find("THREE") != std::string::npos) {
            return pair.second;
        }
    }
    
    // If no sequence named THREE found, return the longest sequence
    if (!sequences.empty()) {
        auto maxSeq = std::max_element(sequences.begin(), sequences.end(),
            [](const auto& a, const auto& b) {
                return a.second.length() < b.second.length();
            });
        return maxSeq->second;
    }
    
    return "";
}

/**
 * Update hash table with k-nucleotide counts for all reading frames
 */
void updateHashTable(std::unordered_map<std::string, int>& hashTable, 
                    const std::string& dnaSequence, int k) {
    int seqLen = dnaSequence.length();
    
    // Process all possible k-nucleotides (all reading frames)
    for (int i = 0; i <= seqLen - k; i++) {
        std::string kNucleotide = dnaSequence.substr(i, k);
        hashTable[kNucleotide]++;
    }
}

void printFrequencyTable(const std::unordered_map<std::string, int>& hashTable) {
    int totalCount = 0;
    for (const auto& pair : hashTable) {
        totalCount += pair.second;
    }
    
    if (totalCount == 0) return;
    
    std::vector<std::pair<std::string, int>> entries(hashTable.begin(), hashTable.end());
    
    // Sort by descending frequency, then ascending nucleotide key
    std::sort(entries.begin(), entries.end(), 
        [totalCount](const auto& a, const auto& b) {
            double freqA = (a.second * 100.0) / totalCount;
            double freqB = (b.second * 100.0) / totalCount;
            if (freqA != freqB) return freqA > freqB; // Descending frequency
            return a.first < b.first; // Ascending key
        });
    
    for (const auto& entry : entries) {
        double percentage = (entry.second * 100.0) / totalCount;
        std::cout << entry.first << " " << std::fixed << std::setprecision(3) 
                  << percentage << std::endl;
    }
    std::cout << std::endl;
}

void printSpecificCounts(const std::unordered_map<std::string, int>& hashTable, 
                        const std::vector<std::string>& targets) {
    for (const std::string& target : targets) {
        auto it = hashTable.find(target);
        int count = (it != hashTable.end()) ? it->second : 0;
        std::cout << count << "\t" << target << std::endl;
    }
}

int main() {
    // Read DNA sequence THREE from stdin
    std::string dnaSequence = readFastaSequenceThree();
    
    if (dnaSequence.empty()) {
        std::cerr << "No DNA sequence found" << std::endl;
        return 1;
    }
    
    // Hash tables for different k-nucleotide lengths
    std::unordered_map<int, std::unordered_map<std::string, int>> hashTables;
    
    // Count 1-nucleotide and 2-nucleotide sequences
    for (int k : {1, 2}) {
        hashTables[k] = std::unordered_map<std::string, int>();
        updateHashTable(hashTables[k], dnaSequence, k);
        printFrequencyTable(hashTables[k]);
    }
    
    // Count 3, 4, 6, 12, and 18-nucleotide sequences for specific targets
    std::unordered_map<int, std::vector<std::string>> targetSequences = {
        {3, {"GGT"}},
        {4, {"GGTA"}},
        {6, {"GGTATT"}},
        {12, {"GGTATTTTAATT"}},
        {18, {"GGTATTTTAATTTATAGT"}}
    };
    
    for (int k : {3, 4, 6, 12, 18}) {
        hashTables[k] = std::unordered_map<std::string, int>();
        updateHashTable(hashTables[k], dnaSequence, k);
        
        if (targetSequences.find(k) != targetSequences.end()) {
            printSpecificCounts(hashTables[k], targetSequences[k]);
        }
    }
    
    return 0;
}