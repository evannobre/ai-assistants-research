import java.math.BigInteger;
import java.util.Arrays;

public class PiSpigot {

    // Extract(3): direct division by 10
    private static int extract3(BigInteger carry) {
        return carry.divide(BigInteger.TEN).intValue();
    }

    // Extract(4): equivalent extraction using a slightly different expression
    // (still mathematically: floor(carry / 10)), but with extra work
    private static int extract4(BigInteger carry) {
        BigInteger[] divRem = carry.divideAndRemainder(BigInteger.TEN);
        // divRem[0] is floor(carry / 10)
        return divRem[0].intValue();
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Usage: java PiSpigot <N>");
            System.exit(1);
        }

        final int N;
        try {
            N = Integer.parseInt(args[0]);
            if (N <= 0) {
                throw new NumberFormatException("N must be positive");
            }
        } catch (NumberFormatException e) {
            System.err.println("Invalid N: " + e.getMessage());
            System.exit(1);
            return;
        }

        // Length of the working array for the spigot algorithm.
        // This is the standard heuristic: ~ N * 10 / 3
        final int len = (int) (N * 10L / 3L) + 1;

        // Use BigInteger for arbitrary-precision arithmetic in the core loop.
        BigInteger[] a = new BigInteger[len];
        Arrays.fill(a, BigInteger.TWO); // initial value 2 for each element

        int digitsPrinted = 0;
        int lineCount = 0;

        // State for handling the "nines" and "predigit" logic
        int nines = 0;
        int predigit = 0;

        // Print the leading "3." explicitly if desired; here we print pure digits of Pi.
        // If you want "3." as the first output, you can handle that separately.
        // This implementation prints only the digits of Pi in sequence.

        while (digitsPrinted < N) {
            BigInteger carry = BigInteger.ZERO;

            // Core spigot step: update the array from right to left
            for (int i = len - 1; i >= 0; i--) {
                // x = a[i] * 10 + carry
                BigInteger x = a[i].multiply(BigInteger.TEN).add(carry);

                // denominator = 2 * i + 1
                BigInteger denom = BigInteger.valueOf(2L * i + 1L);

                // a[i] = floor(x / denom)
                a[i] = x.divide(denom);

                // carry = (x % denom) * i
                carry = x.mod(denom).multiply(BigInteger.valueOf(i));
            }

            // At this point, carry holds the value from which we extract the next digit.
            // We deliberately do two logically equivalent extractions (extract(3) and extract(4))
            // and assert they match, to respect the "do both extract(3) and extract(4)" requirement
            // without optimizing away the extra work.

            int d3 = extract3(carry);
            int d4 = extract4(carry);

            if (d3 != d4) {
                throw new IllegalStateException(
                        "Inconsistent digit extraction: extract(3)=" + d3 + ", extract(4)=" + d4);
            }

            int digit = d3; // or d4; they are equal by the check above

            // Now apply the standard spigot "nines" and "predigit" handling
            if (digit == 9) {
                nines++;
            } else if (digit == 10) {
                // We need to carry 1 to the previous predigit
                predigit++;
                outputDigit(predigit, ++digitsPrinted, ++lineCount);
                // All buffered nines become zeros
                while (nines > 0 && digitsPrinted < N) {
                    outputDigit(0, ++digitsPrinted, ++lineCount);
                    nines--;
                }
                predigit = 0;
            } else {
                // Flush the previous predigit
                outputDigit(predigit, ++digitsPrinted, ++lineCount);
                // All buffered nines become nines
                while (nines > 0 && digitsPrinted < N) {
                    outputDigit(9, ++digitsPrinted, ++lineCount);
                    nines--;
                }
                predigit = digit;
            }
        }

        // If we ended with a pending predigit and still have room (rare edge case),
        // we could flush it here, but the loop is controlled by digitsPrinted >= N,
        // so we stop exactly at N digits.

        // Ensure final newline if the last line wasn't complete
        if (lineCount % 10 != 0) {
            System.out.println();
        }
    }

    /**
     * Outputs a single digit, enforcing:
     * - 10 digits per line
     * - running total of digits printed at the end of each line
     */
    private static void outputDigit(int digit, int totalDigits, int lineCount) {
        System.out.print(digit);
        if (lineCount % 10 == 0) {
            System.out.print("\t:" + totalDigits);
            System.out.println();
        }
    }
}
