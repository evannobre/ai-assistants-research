#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << (argv[0] ? argv[0] : "fasta_sim") 
                  << " num_sequences sequence_length [seed]" << std::endl;
        return 1;
    }

    long num_sequences = std::atol(argv[1]);
    long sequence_length = std::atol(argv[2]);
    uint64_t seed = (argc >= 4) ? std::strtoull(argv[3], nullptr, 10) : 123456789;

    const uint64_t a = 6364136223846793005ULL;
    const uint64_t c = 1442695040888963407ULL;

    char buffer[80];

    for (long seq_id = 0; seq_id < num_sequences; ++seq_id) {
        std::cout << ">seq" << seq_id << "\n";

        uint64_t state = seed + static_cast<uint64_t>(seq_id);
        long remaining = sequence_length;

        while (remaining > 0) {
            int chunk_size = (remaining < 80) ? remaining : 80;
            for (int j = 0; j < chunk_size; ++j) {
                state = state * a + c;
                buffer[j] = "ACGT"[state & 3];
            }
            std::cout.write(buffer, chunk_size);
            std::cout << '\n';
            remaining -= chunk_size;
        }
    }

    return 0;
}