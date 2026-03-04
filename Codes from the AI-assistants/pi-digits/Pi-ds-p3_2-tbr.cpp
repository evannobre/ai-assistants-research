#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>
#include <gmpxx.h>  // GNU Multiple Precision Arithmetic Library

class SpigotPi {
private:
    int digits;
    std::vector<int> a;
    
public:
    SpigotPi(int n) : digits(n) {
        int len = (10 * n) / 3 + 1;
        a.resize(len, 2);
    }
    
    void compute() {
        int nines = 0;
        int predigit = 0;
        int count = 0;
        std::string line = "";
        
        std::cout << "Computing first " << digits << " digits of pi..." << std::endl;
        std::cout << std::string(60, '=') << std::endl;
        
        for (int j = 1; j <= digits; j++) {
            int carry = 0;
            
            // Multiply by 10
            for (int i = a.size() - 1; i >= 0; i--) {
                a[i] *= 10;
            }
            
            // Calculate q and propagate carries
            for (int i = a.size() - 1; i >= 0; i--) {
                a[i] += carry;
                int denom = (i == 0) ? 10 : (2 * i + 1);
                int q = a[i] / denom;
                int r = a[i] % denom;
                a[i] = r;
                if (i > 0) {
                    carry = q * i;
                } else {
                    a[0] = q % 10;
                    q = q / 10;
                    
                    if (q == 9) {
                        nines++;
                    } else if (q == 10) {
                        // Handle overflow
                        int digit = predigit + 1;
                        if (digit == 10) digit = 0;
                        printDigit(digit, count, line);
                        
                        for (int k = 0; k < nines; k++) {
                            printDigit(0, count, line);
                        }
                        
                        predigit = 0;
                        nines = 0;
                    } else {
                        // Normal case
                        if (predigit != 0) {
                            printDigit(predigit, count, line);
                        }
                        
                        for (int k = 0; k < nines; k++) {
                            printDigit(9, count, line);
                        }
                        
                        predigit = q;
                        nines = 0;
                    }
                }
            }
        }
        
        // Print any remaining digits
        if (predigit != 0) {
            printDigit(predigit, count, line);
        }
        
        // Print final line if not empty
        if (!line.empty()) {
            std::cout << line << " : " << count << std::endl;
        }
    }
    
private:
    void printDigit(int digit, int& count, std::string& line) {
        line += std::to_string(digit);
        count++;
        
        if (line.length() == 10) {
            std::cout << line << " : " << count << std::endl;
            line.clear();
        }
    }
};

int main(int argc, char* argv[]) {
    int n = 100;
    
    if (argc > 1) {
        n = std::stoi(argv[1]);
    }
    
    std::cout << "Running spigot algorithm for pi with n = " << n << std::endl;
    std::cout << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    SpigotPi spigot(n);
    spigot.compute();
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << std::string(60, '=') << std::endl;
    std::cout << "Time taken: " << duration.count() / 1000.0 << " seconds" << std::endl;
    
    return 0;
}