#include <iostream>
#include <iomanip>
#include <cmath>
#include <gmpxx.h>

mpf_class calculate_pi(int digits) {
    mpf_set_default_prec(digits * 4); // Set precision in bits
    
    mpf_class pi(0.0, digits * 4);
    mpf_class term;
    mpf_class sixteen(16.0);
    mpf_class four(4.0);
    mpf_class two(2.0);
    mpf_class one(1.0);
    
    // Use Machin's formula: pi/4 = 4*arctan(1/5) - arctan(1/239)
    mpf_class a1 = 1.0 / 5.0;
    mpf_class a2 = 1.0 / 239.0;
    
    // arctan(x) = x - x^3/3 + x^5/5 - x^7/7 + ...
    for (int i = 0; i < digits; i++) {
        int k = 2 * i + 1;
        mpf_class power1 = 1.0;
        mpf_class power2 = 1.0;
        
        for (int j = 0; j < k; j++) {
            power1 *= a1;
            power2 *= a2;
        }
        
        term = power1 - power2;
        if (i % 2 == 1) {
            term = -term;
        }
        term /= k;
        
        pi += term;
    }
    
    pi *= 4;
    return pi;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <number_of_digits>" << std::endl;
        return 1;
    }
    
    try {
        int n = std::stoi(argv[1]);
        if (n <= 0) {
            std::cout << "Number of digits must be positive" << std::endl;
            return 1;
        }
        
        if (n <= 15) {
            std::cout << std::setprecision(n) << M_PI << std::endl;
        } else {
            mpf_class pi = calculate_pi(n);
            gmp_printf("%.*Ff\n", n, pi.get_mpf_t());
        }
    } catch (...) {
        std::cout << "Please provide a valid integer" << std::endl;
        return 1;
    }
    
    return 0;
}