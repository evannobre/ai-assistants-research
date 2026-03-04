// pi_generator.cpp
#include <iostream>
#include <iomanip>
#include <string>
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/math/constants/constants.hpp>

using namespace boost::multiprecision;

cpp_dec_float_100 chudnovsky_pi(int digits) {
    cpp_dec_float_100::default_precision(digits + 10);
    
    cpp_dec_float_100 C = 426880 * sqrt(cpp_dec_float_100(10005));
    cpp_dec_float_100 K = 6;
    cpp_dec_float_100 M = 1;
    cpp_dec_float_100 X = 1;
    cpp_dec_float_100 L = 13591409;
    cpp_dec_float_100 S = 13591409;
    
    for (int i = 1; i < digits / 14 + 10; ++i) {
        M = (K * K * K - 16 * K) * M / (i * i * i);
        L += 545140134;
        X *= -262537412640768000;
        S += M * L / X;
        K += 12;
    }
    
    return C / S;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: ./pi_generator <digits>" << std::endl;
        return 1;
    }
    
    try {
        int digits = std::stoi(argv[1]);
        if (digits <= 0) {
            std::cout << "Please provide a positive integer" << std::endl;
            return 1;
        }
        
        std::cout << "Generating " << digits << " digits of Pi..." << std::endl;
        auto pi = chudnovsky_pi(digits);
        std::cout << std::setprecision(digits + 1) << pi << std::endl;
        
    } catch (...) {
        std::cout << "Invalid input" << std::endl;
        return 1;
    }
    
    return 0;
}