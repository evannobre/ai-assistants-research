#include <iostream>
#include <string>
#include <regex>
#include <vector>

int main() {
    // Read all input from stdin
    std::string data;
    std::string line;
    while (std::getline(std::cin, line)) {
        data += line + "\n";
    }
    
    // Record original sequence length
    int initial_length = data.length();
    
    // 1. Remove FASTA sequence descriptions and all linefeed characters
    std::regex fasta_regex(R"(>.*\n|\n)");
    std::string cleaned = std::regex_replace(data, fasta_regex, "");
    int cleaned_length = cleaned.length();
    
    // Convert to lowercase for pattern matching
    std::string sequence_lower = cleaned;
    std::transform(sequence_lower.begin(), sequence_lower.end(), 
                   sequence_lower.begin(), ::tolower);
    
    // 2. Patterns to count
    std::vector<std::string> patterns = {
        R"(agggtaaa|tttaccct)",
        R"([cgt]gggtaaa|tttaccc[acg])",
        R"(a[act]ggtaaa|tttacc[agt]t)",
        R"(ag[act]gtaaa|tttac[agt]ct)",
        R"(agg[act]taaa|ttta[agt]cct)",
        R"(aggg[acg]aaa|ttt[cgt]ccct)",
        R"(agggt[cgt]aa|tt[acg]accct)",
        R"(agggta[cgt]a|t[acg]taccct)",
        R"(agggtaa[cgt]|[acg]ttaccct)"
    };
    
    // Count matches for each pattern
    for (const auto& pattern_str : patterns) {
        std::regex pattern(pattern_str);
        auto words_begin = std::sregex_iterator(
            sequence_lower.begin(), sequence_lower.end(), pattern);
        auto words_end = std::sregex_iterator();
        int count = std::distance(words_begin, words_end);
        std::cout << pattern_str << " " << count << std::endl;
    }
    
    // 3. Magic replacements
    std::vector<std::pair<std::string, std::string>> magic_replacements = {
        {R"(tHa[Nt])", "<4>"},
        {R"(aND|caN|Ha[DS]|WaS)", "<3>"},
        {R"(a[NSt]|BY)", "<2>"},
        {R"(<[^>]*>)", "|"},
        {R"(\\|[^|][^|]*\\|)", "-"}
    };
    
    // Apply replacements sequentially
    std::string replaced_data = data;
    for (const auto& [pattern_str, replacement] : magic_replacements) {
        std::regex pattern(pattern_str);
        replaced_data = std::regex_replace(replaced_data, pattern, replacement);
    }
    
    // Remove FASTA headers and newlines from replaced data
    std::string final_cleaned = std::regex_replace(replaced_data, fasta_regex, "");
    int final_length = final_cleaned.length();
    
    // 4. Output the three lengths
    std::cout << "\n" << initial_length << std::endl;
    std::cout << cleaned_length << std::endl;
    std::cout << final_length << std::endl;
    
    return 0;
}