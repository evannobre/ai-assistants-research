#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>

class RegexReducer {
private:
    std::unordered_map<std::string, std::regex> patterns;
    
public:
    RegexReducer() {
        patterns["agggtaaa"] = std::regex("agggtaaa|tttaccct");
        // ... other patterns
    }
    
    void process(const char* data, size_t length) {
        std::string sequence = removeHeaders(data, length);
        
        // Pattern counting
        for (const auto& [name, pattern] : patterns) {
            auto count = std::distance(
                std::sregex_iterator(sequence.begin(), sequence.end(), pattern),
                std::sregex_iterator()
            );
            std::cout << name << " " << count << "\n";
        }
        
        // IUB replacements
        std::string replaced = applyIUBReplacements(sequence);
        
        std::cout << "\n" << sequence.length() << "\n";
        std::cout << replaced.length() << "\n";
    }
    
private:
    std::string removeHeaders(const char* data, size_t length) {
        std::regex header_pattern(">[^\\n]*\\n|\\n");
        std::string str_data(data, length);
        return std::regex_replace(str_data, header_pattern, "");
    }
    
    std::string applyIUBReplacements(const std::string& seq) {
        std::string result = seq;
        std::vector<std::pair<std::regex, std::string>> replacements = {
            {std::regex("B"), "(c|g|t)"},
            // ... other replacements
        };
        
        for (const auto& [pattern, replacement] : replacements) {
            result = std::regex_replace(result, pattern, replacement);
        }
        return result;
    }
};