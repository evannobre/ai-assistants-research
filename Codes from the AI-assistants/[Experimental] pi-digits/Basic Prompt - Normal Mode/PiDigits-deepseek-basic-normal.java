import java.math.BigDecimal;
import java.math.MathContext;

public class PiCalculator {
    public static String computePiBBP(int digits) {
        MathContext mc = new MathContext(digits + 2); // extra precision
        BigDecimal pi = BigDecimal.ZERO;
        
        for (int k = 0; k <= digits; k++) {
            BigDecimal term1 = BigDecimal.valueOf(4).divide(
                BigDecimal.valueOf(8 * k + 1), mc);
            BigDecimal term2 = BigDecimal.valueOf(2).divide(
                BigDecimal.valueOf(8 * k + 4), mc);
            BigDecimal term3 = BigDecimal.valueOf(1).divide(
                BigDecimal.valueOf(8 * k + 5), mc);
            BigDecimal term4 = BigDecimal.valueOf(1).divide(
                BigDecimal.valueOf(8 * k + 6), mc);
            
            BigDecimal term = term1.subtract(term2)
                                 .subtract(term3)
                                 .subtract(term4)
                                 .divide(BigDecimal.valueOf(16).pow(k), mc);
            
            pi = pi.add(term);
        }
        
        return pi.toString().substring(0, digits + 2); // +2 for "3."
    }

    public static void main(String[] args) {
        int n = 100; // Number of digits
        String piDigits = computePiBBP(n);
        System.out.println("Pi to " + n + " digits: " + piDigits);
    }
}