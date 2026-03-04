import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

public class PiCalculator {
    public static String calculatePi(int digits) {
        MathContext mc = new MathContext(digits + 10, RoundingMode.HALF_UP);
        
        // Bailey-Borwein-Plouffe formula
        BigDecimal pi = BigDecimal.ZERO;
        BigDecimal sixteen = new BigDecimal(16);
        
        for (int k = 0; k < digits; k++) {
            BigDecimal term1 = BigDecimal.ONE.divide(
                new BigDecimal(16).pow(k), mc);
            BigDecimal term2 = new BigDecimal(4).divide(
                new BigDecimal(8 * k + 1), mc);
            BigDecimal term3 = new BigDecimal(2).divide(
                new BigDecimal(8 * k + 4), mc);
            BigDecimal term4 = BigDecimal.ONE.divide(
                new BigDecimal(8 * k + 5), mc);
            BigDecimal term5 = BigDecimal.ONE.divide(
                new BigDecimal(8 * k + 6), mc);
            
            BigDecimal term = term1.multiply(
                term2.subtract(term3).subtract(term4).subtract(term5));
            pi = pi.add(term);
        }
        
        return pi.setScale(digits, RoundingMode.DOWN).toString();
    }
    
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java PiCalculator <number_of_digits>");
            return;
        }
        
        try {
            int n = Integer.parseInt(args[0]);
            if (n <= 0) {
                System.out.println("Number of digits must be positive");
                return;
            }
            
            System.out.println(calculatePi(n));
        } catch (NumberFormatException e) {
            System.out.println("Please provide a valid integer");
        }
    }
}