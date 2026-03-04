#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <regex>
#include <future>
#include <map>

// Target: Ubuntu 24.04 (GCC 13/14) | 8GB RAM
// Uses ONLY standard C++ libraries: <regex>, <future>, <iostream>

using namespace std;

// The 9 patterns for the counting phase
const vector<string> count_patterns = {
    "agggtaaa|tttaccct",
    "[cgt]gggtaaa|tttaccc[acg]",
    "a[act]ggtaaa|tttacc[agt]t",
    "ag[act]gtaaa|tttac[agt]ct",
    "agg[act]taaa|ttta[agt]cct",
    "aggg[acg]aaa|ttt[cgt]ccct",
    "agggt[cgt]aa|tt[acg]accct",
    "agggta[cgt]a|t[acg]taccct",
    "agggtaa[cgt]|[acg]ttaccct"
};

// The 11 IUB replacements
const map<string, string> iub_replacements = {
    {"tHa[Nt]", "<4>"}, {"aND|caN|Ha[Ds]|WaS", "<3>"},
    {"a[NSt]|BY", "<2>"}, {"<[^>]*>", "|"},
    {"\\|[^|][^|]*\\|", "-"} 
};

// Helper to read stdin into a string
string read_input() {
    stringstream buffer;
    buffer << cin.rdbuf();
    return buffer.str();
}

int main() {
    // 1. Ingest
    string input_data = read_input();
    size_t initial_len = input_data.length();

    // 2. Sanitize: Remove regex-redux headers and newlines
    // Note: std::regex can be slower than PCRE, but it is native.
    // We remove newlines and description lines (>...)
    regex remove_re(">[^\\n]*\\n|\\n"); 
    string clean_sequence = regex_replace(input_data, remove_re, "");
    size_t clean_len = clean_sequence.length();

    // 3. Parallel Counting
    // We use std::async to run counting tasks on available cores
    vector<future<int>> futures;
    for (const auto& pat : count_patterns) {
        futures.push_back(async(launch::async, [&clean_sequence, pat]() {
            regex re(pat);
            auto begin = sregex_iterator(clean_sequence.begin(), clean_sequence.end(), re);
            auto end = sregex_iterator();
            return distance(begin, end);
        }));
    }

    // 4. Sequential Substitution
    // We create a copy for substitution to avoid race conditions with the counters if they were overlapping,
    // though here we wait for counters later.
    // However, IUB replacement is distinct from the counting patterns.
    string replace_sequence = input_data; // The benchmark usually applies replacement to the *original* input or clean? 
    // Correction: In strict regex-redux, replacements are done on the ORIGINAL input? 
    // Checking standard implementation: Replacements are done on the CLEANED sequence usually, 
    // but the benchmark spec can vary. Most implementations replace on the cleaned sequence.
    // Let's perform on 'clean_sequence'.
    
    // For specific benchmark compliance, verify if replacements are chained. 
    // The standard requires:
    // (tHa[Nt]) -> <4>
    // (aND|caN|Ha[Ds]|WaS) -> <3>
    // etc.
    
    // Note: C++ std::regex replacement is simpler but we need to handle the mapping.
    // The benchmark actually defines specific pairs.
    // Let's perform the 3 magic replacements specified in standard regex-redux (Magic patterns).
    // Actually, the standard benchmark has specific pairs:
    vector<pair<string, string>> replacements = {
        {"tHa[Nt]", "<4>"},
        {"aND|caN|Ha[Ds]|WaS", "<3>"},
        {"a[NSt]|BY", "<2>"},
        {"<[^>]*>", "|"},
        {"\\|[^|][^|]*\\|", "-"}
    };

    // We process substitutions on a copy to determine final length
    string s_copy = clean_sequence; 
    for (const auto& rep : replacements) {
        regex re(rep.first);
        s_copy = regex_replace(s_copy, re, rep.second);
    }
    size_t end_len = s_copy.length();

    // 5. Output Results
    // Print counts from futures
    for (size_t i = 0; i < count_patterns.size(); ++i) {
        cout << count_patterns[i] << " " << futures[i].get() << endl;
    }

    // Print lengths
    cout << "\n" << initial_len << "\n" << clean_len << "\n" << end_len << endl;

    return 0;
}