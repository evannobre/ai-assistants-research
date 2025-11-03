std::string read_all_input() {
    std::istreambuf_iterator<char> it(std::cin), end;
    std::string data(it, end);
    return data;
}

const std::vector<std::pair<std::string, std::string>> patterns = {
    {"agggtaaa|tttaccct",          ""},
    {"[cgt]gggtaaa|tttaccc[acg]",  ""},
    {"a[act]ggtaaa|tttacc[agt]t",  ""},
    {"ag[act]gtaaa|tttac[agt]ct",  ""},
    {"agg[act]taaa|ttta[agt]cct",  ""},
    {"aggg[acg]aaa|ttt[cgt]ccct",  ""},
    {"agggt[cgt]aa|tt[acg]accct",  ""},
    {"agggta[cgt]a|t[acg]taccct",  ""},
    {"agggtaa[cgt]|[acg]ttaccct",  ""}
};

std::vector<std::regex> compiled;
for (auto &p : patterns)
    compiled.emplace_back(p.first, std::regex::optimize);

size_t count_overlapping(const std::string &s, const std::regex &re) {
    size_t count = 0;
    auto begin = s.cbegin();
    while (begin != s.cend()) {
        std::smatch m;
        if (std::regex_search(begin, s.cend(), m, re)) {
            ++count;
            begin = m.first + 1;  // advance one past the match start
        } else {
            break;
        }
    }
    return count;
}

size_t count_non_overlapping(const std::string &s, const std::regex &re) {
    return std::distance(
        std::sregex_iterator(s.begin(), s.end(), re),
        std::sregex_iterator{}
    );
}

std::string apply_substitutions(const std::string &input) {
    static const std::vector<std::pair<std::regex, std::string>> subs = {
        {std::regex("AB|BC"), "@"},
        {std::regex("Name"),     "X"},
        // ... add as many as needed
    };

    std::string cur = input;
    for (auto &p : subs)
        cur = std::regex_replace(cur, p.first, p.second);
    return cur;
}

int main() {
    // 1. Read
    std::string data = read_all_input();

    // 2. Compile
    compile_all_patterns();

    // 3. Count matches
    for each regex re in compiled:
        print(count_overlapping(data, re));
        print(count_non_overlapping(data, re));

    // 4. Perform substitutions
    std::string mutated = apply_substitutions(data);
    std::cout << data.size() << "\n"        // original length
              << mutated.size() << "\n";    // after subs

    return 0;
}
