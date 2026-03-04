// ... (Previous helper functions remain, but change them to RETURN string/results) ...

std::string format_frequencies(std::string_view sequence, int k) {
    auto counts = generate_frequencies(sequence, k);
    std::vector<std::pair<std::string_view, uint32_t>> sorted_counts(counts.begin(), counts.end());
    
    size_t total = 0;
    for (const auto& kv : counts) total += kv.second;

    std::sort(sorted_counts.begin(), sorted_counts.end(), 
        [](const auto& a, const auto& b) {
            if (a.second != b.second) return a.second > b.second;
            return a.first < b.first;
        });

    std::ostringstream oss;
    for (const auto& item : sorted_counts) {
        oss << item.first << " " << std::fixed << std::setprecision(3) << (100.0 * item.second / total) << '\n';
    }
    oss << '\n';
    return oss.str();
}

std::string format_count(std::string_view sequence, std::string target) {
    auto counts = generate_frequencies(sequence, target.length());
    std::ostringstream oss;
    oss << counts[target] << "\t" << target << '\n';
    return oss.str();
}

int main(int argc, char* argv[]) {
    // Disable sync with stdio for speed
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    std::string sequence = read_input(argc, argv);
    std::string_view seq_view(sequence);

    // Launch heavy computations in parallel
    auto f1 = std::async(std::launch::async, format_frequencies, seq_view, 1);
    auto f2 = std::async(std::launch::async, format_frequencies, seq_view, 2);
    
    auto c1 = std::async(std::launch::async, format_count, seq_view, "GGT");
    auto c2 = std::async(std::launch::async, format_count, seq_view, "GGTA");
    auto c3 = std::async(std::launch::async, format_count, seq_view, "GGTATT");
    auto c4 = std::async(std::launch::async, format_count, seq_view, "GGTATTTTAATT");
    auto c5 = std::async(std::launch::async, format_count, seq_view, "GGTATTTTAATTTATAGT");

    // Output in correct order
    std::cout << f1.get();
    std::cout << f2.get();
    std::cout << c1.get();
    std::cout << c2.get();
    std::cout << c3.get();
    std::cout << c4.get();
    std::cout << c5.get();

    return 0;
}