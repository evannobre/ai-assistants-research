#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

// LCG Constants as per FASTA benchmark specifications
const int IM = 139968;
const int IA = 3877;
const int IC = 29573;
static int last_seed = 42;

// LCG arithmetic function
inline double my_random(int max_val) {
    last_seed = (last_seed * IA + IC) % IM;
    return max_val * (double)last_seed / IM;
}

struct Nucleotide {
    char c;
    double p;
};

// Cumulative distribution for faster lookup
void make_cumulative(std::vector<Nucleotide>& v) {
    double cp = 0.0;
    for (auto& n : v) {
        cp += n.p;
        n.p = cp;
    }
}

// Selects nucleotide based on a random value
inline char select_nucleotide(const std::vector<Nucleotide>& v) {
    double r = my_random(1);
    for (const auto& n : v) {
        if (r < n.p) return n.c;
    }
    return v.back().c;
}

void generate_fasta(const std::string& id, const std::string& desc, 
                    int n, std::vector<Nucleotide>& v) {
    std::cout << ">" << id << " " << desc << "\n";
    make_cumulative(v);
    
    int line_count = 0;
    for (int i = 0; i < n; ++i) {
        std::cout << select_nucleotide(v);
        if (++line_count == 60) {
            std::cout << "\n";
            line_count = 0;
        }
    }
    if (line_count > 0) std::cout << "\n";
}

int main(int argc, char** argv) {
    int n = (argc > 1) ? std::stoi(argv[1]) : 1000;

    // Example: IUB ambiguity codes
    std::vector<Nucleotide> iub = {
        {'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
        {'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
        {'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
        {'V', 0.02}, {'W', 0.02}, {'Y', 0.02}
    };

    generate_fasta("ONE", "Homo sapiens alu", n * 2, iub);
    return 0;
}