std::string text = read_all(stdin);
std::vector<std::pair<std::regex, std::string>> rules = { … };
size_t total = 0;
bool changed = true;
while (changed) {
    changed = false;
    for (auto &r : rules) {
        std::smatch m;
        std::string out;
        size_t count = 0;
        std::string::const_iterator searchStart(text.cbegin());
        while (std::regex_search(searchStart, text.cend(), m, r.first)) {
            count++;
            out.append(searchStart, m[0].first);
            out.append(r.second);
            searchStart = m[0].second;
        }
        out.append(searchStart, text.cend());
        if (count) {
            total += count;
            text.swap(out);
            changed = true;
        }
    }
}
std::cout << total << "\n";
