// pi_chudnovsky.cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <chrono>
#include <gmpxx.h>
#include <vector>
#include <sstream>

class PiCalculator {
private:
    // Constants for Chudnovsky algorithm
    static constexpr const char* C = "426880";
    static constexpr const char* M = "10005";
    
    // Factorial using GMP
    static void factorial(mpz_class& result, unsigned long n) {
        mpz_fac_ui(result.get_mpz_t(), n);
    }
    
    // Binary splitting recursion for Chudnovsky series
    static void binary_split(mpq_class& P, mpq_class& Q, mpq_class& T, 
                            long a, long b) {
        if (b - a == 1) {
            if (a == 0) {
                P = 1;
                Q = 1;
            } else {
                // P(a, a+1) = -(6a-5)(2a-1)(6a-1)
                mpz_class p_num = (6*a - 5) * (2*a - 1) * (6*a - 1);
                P = mpq_class(-p_num, 1);
                
                // Q(a, a+1) = a³ * C³_24 / 24
                mpz_class q_den = a * a * a;
                q_den *= 10939058860032000L; // C³_24 / 24
                Q = mpq_class(1, q_den);
                
                // T(a, a+1) = P(a, a+1) * C
                T = P * mpq_class(13591409 + 545140134 * a, 1);
            }
        } else {
            long m = (a + b) / 2;
            mpq_class P_am, Q_am, T_am;
            mpq_class P_mb, Q_mb, T_mb;
            
            binary_split(P_am, Q_am, T_am, a, m);
            binary_split(P_mb, Q_mb, T_mb, m, b);
            
            P = P_am * P_mb;
            Q = Q_am * Q_mb;
            T = T_am * Q_mb + P_am * T_mb;
        }
    }

public:
    static std::string compute_pi_digits(int digits) {
        // Set precision (bits = digits * log2(10))
        mpf_set_default_prec(static_cast<mp_bitcnt_t>(digits * 3.322 + 100));
        
        // Calculate needed iterations
        // Chudnovsky algorithm: each term gives about 14.18 digits
        int terms = static_cast<int>(digits / 14.18) + 2;
        
        // Binary splitting
        mpq_class P, Q, T;
        binary_split(P, Q, T, 0, terms);
        
        // Final calculation: π = C / ( (√M) * T/Q )
        mpf_class pi, temp;
        
        // Convert T/Q to mpf
        mpf_class t_over_q(T / Q);
        
        // Calculate sqrt(10005)
        mpf_class sqrt_m;
        mpf_class m_val(10005);
        mpf_sqrt(sqrt_m.get_mpf_t(), m_val.get_mpf_t());
        
        // π = C / (sqrt(M) * T/Q)
        pi = mpf_class(426880) / (sqrt_m * t_over_q);
        
        // Convert to string with specified digits
        std::stringstream ss;
        ss << std::setprecision(digits + 10);
        ss << pi;
        
        std::string pi_str = ss.str();
        
        // Return only the requested digits (including "3.")
        return pi_str.substr(0, digits + 2);
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <number_of_digits>" << std::endl;
        std::cerr << "Example: " << argv[0] << " 100" << std::endl;
        return 1;
    }
    
    try {
        int digits = std::stoi(argv[1]);
        
        if (digits <= 0) {
            std::cerr << "Number of digits must be positive" << std::endl;
            return 1;
        }
        
        // Memory check: approximate memory usage ~ O(digits * log(digits))
        size_t estimated_memory = digits * digits / 1000000;
        if (estimated_memory > 6000) { // Leave 2GB for system
            std::cerr << "Warning: Requesting " << digits 
                     << " digits may require approximately " 
                     << estimated_memory << " MB of RAM." << std::endl;
            std::cerr << "Your system has 8GB RAM. Continue? (y/N): ";
            char response;
            std::cin >> response;
            if (response != 'y' && response != 'Y') {
                return 0;
            }
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        
        std::string pi = PiCalculator::compute_pi_digits(digits);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "π to " << digits << " digits:" << std::endl;
        std::cout << pi << std::endl;
        std::cerr << "\nComputation time: " << duration.count() / 1000.0 << " seconds" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}