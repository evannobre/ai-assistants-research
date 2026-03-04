import java.math.BigInteger;
import java.util.ArrayList;

public class PiSpigot {
    
    public static ArrayList<Integer> spigotPiDigits(int n) {
        // Implementation of extract(3) algorithm
        ArrayList<Integer> digits = new ArrayList<>();
        
        // Calculate array length
        int len = (10 * n) / 3 + 2;
        int[] a = new int[len];
        
        // Initialize array with 2's
        for (int i = 0; i < len; i++) {
            a[i] = 2;
        }
        
        int predigit = 0;
        
        for (int j = 1; j <= n; j++) {
            int carry = 0;
            
            // Process from right to left
            for (int i = len - 1; i >= 0; i--) {
                int numerator = i;
                int denominator = 2 * i + 1;
                int temp = a[i] * 10 + carry;
                
                if (i > 0) {
                    a[i] = temp % denominator;
                    carry = temp / denominator;
                } else {
                    a[i] = temp % 10;
                    carry = temp / 10;
                }
            }
            
            int q = carry / 10;
            int r = carry % 10;
            
            if (q == 9) {
                predigit++;
            } else {
                if (predigit > 0) {
                    digits.add(predigit);
                    if (q == 10) {
                        digits.add(0);
                    }
                } else if (q == 10) {
                    digits.add(1);
                    q = 0;
                }
                
                digits.add(q);
                predigit = (q == 10) ? 0 : r;
            }
        }
        
        // Add final predigit if any
        if (predigit > 0) {
            digits.add(predigit);
        }
        
        return digits;
    }
    
    public static void printPiDigits(ArrayList<Integer> digits) {
        System.out.print("3.");
        
        // Print first digit after decimal
        if (!digits.isEmpty()) {
            System.out.print(digits.get(0));
        }
        
        // Print remaining digits 10 per line
        for (int i = 1; i < digits.size(); i += 10) {
            System.out.println();
            int end = Math.min(i + 10, digits.size());
            for (int j = i; j < end; j++) {
                System.out.print(digits.get(j));
            }
            System.out.print("   : " + end);
        }
        System.out.println();
    }
    
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java PiSpigot <number_of_digits>");
            System.exit(1);
        }
        
        int n;
        try {
            n = Integer.parseInt(args[0]);
        } catch (NumberFormatException e) {
            System.out.println("Please provide a valid integer");
            System.exit(1);
            return;
        }
        
        System.out.println("Calculating " + n + " digits of π using Spigot algorithm...");
        long startTime = System.currentTimeMillis();
        
        ArrayList<Integer> digits = spigotPiDigits(n);
        
        long endTime = System.currentTimeMillis();
        
        System.out.println("\nFirst " + digits.size() + " digits of π:");
        printPiDigits(digits);
        
        System.out.println("\nTime taken: " + (endTime - startTime) / 1000.0 + " seconds");
        System.out.println("Digits calculated: " + digits.size());
    }
}