// PiGenerator.java
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

public class PiGenerator {
    
    public static BigDecimal chudnovskyPi(int digits) {
        MathContext mc = new MathContext(digits + 10);
        
        BigDecimal C = new BigDecimal("426880")
            .multiply(sqrt(new BigDecimal("10005"), mc), mc);
        
        BigDecimal K = new BigDecimal("6");
        BigDecimal M = BigDecimal.ONE;
        BigDecimal X = BigDecimal.ONE;
        BigDecimal L = new BigDecimal("13591409");
        BigDecimal S = new BigDecimal("13591409");
        
        int iterations = digits / 14 + 10;
        
        for (int i = 1; i <= iterations; i++) {
            BigDecimal i3 = new BigDecimal(i).pow(3);
            M = K.pow(3).subtract(K.multiply(new BigDecimal("16")))
                .multiply(M).divide(i3, mc);
            L = L.add(new BigDecimal("545140134"));
            X = X.multiply(new BigDecimal("-262537412640768000"));
            S = S.add(M.multiply(L, mc).divide(X, mc), mc);
            K = K.add(new BigDecimal("12"));
        }
        
        return C.divide(S, mc).setScale(digits, RoundingMode.DOWN);
    }
    
    private static BigDecimal sqrt(BigDecimal A, MathContext mc) {
        // Newton's method for square root
        BigDecimal x0 = new BigDecimal("0");
        BigDecimal x1 = new BigDecimal(Math.sqrt(A.doubleValue()));
        
        while (!x0.equals(x1)) {
            x0 = x1;
            x1 = A.divide(x0, mc);
            x1 = x1.add(x0, mc);
            x1 = x1.divide(BigDecimal.valueOf(2), mc);
        }
        
        return x1;
    }
    
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java PiGenerator <digits>");
            System.exit(1);
        }
        
        try {
            int digits = Integer.parseInt(args[0]);
            if (digits <= 0) {
                System.out.println("Please provide a positive integer");
                System.exit(1);
            }
            
            System.out.println("Generating " + digits + " digits of Pi...");
            BigDecimal pi = chudnovskyPi(digits);
            System.out.println(pi.toString());
            
        } catch (NumberFormatException e) {
            System.out.println("Invalid number format");
            System.exit(1);
        }
    }
}