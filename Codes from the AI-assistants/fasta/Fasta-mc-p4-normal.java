import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.OutputStream;

public class FastaNaive {

    private static final int IM = 139968;
    private static final int IA = 3877;
    private static final int IC = 29573;
    private static int seed = 42;

    private static double random(double max) {
        seed = (seed * IA + IC) % IM;
        return max * seed / IM;
    }

    private static class NucProb {
        final char nuc;
        final double p;
        NucProb(char nuc, double p) {
            this.nuc = nuc;
            this.p = p;
        }
    }

    private static NucProb[] cumulative(NucProb[] base) {
        double sum = 0.0;
        NucProb[] cum = new NucProb[base.length];
        for (int i = 0; i < base.length; i++) {
            sum += base[i].p;
            cum[i] = new NucProb(base[i].nuc, sum);
        }
        return cum;
    }

    private static void writeHeader(OutputStream out, String header) throws IOException {
        out.write('>');
        out.write(header.getBytes());
        out.write('\n');
    }

    private static void writeRepeated(OutputStream out, String seq, int n) throws IOException {
        final int width = 60;
        char[] line = new char[width];
        int len = seq.length();
        int pos = 0;

        while (n > 0) {
            int lineLen = Math.min(width, n);
            for (int i = 0; i < lineLen; i++) {
                line[i] = seq.charAt(pos);
                pos++;
                if (pos == len) pos = 0;
            }
            out.write(new String(line, 0, lineLen).getBytes());
            out.write('\n');
            n -= lineLen;
        }
    }

    private static void writeRandom(OutputStream out, NucProb[] cum, int n) throws IOException {
        final int width = 60;
        char[] line = new char[width];

        while (n > 0) {
            int lineLen = Math.min(width, n);
            for (int i = 0; i < lineLen; i++) {
                double r = random(1.0);
                char c = 'N';
                for (int j = 0; j < cum.length; j++) {
                    if (r < cum[j].p) {
                        c = cum[j].nuc;
                        break;
                    }
                }
                line[i] = c;
            }
            out.write(new String(line, 0, lineLen).getBytes());
            out.write('\n');
            n -= lineLen;
        }
    }

    public static void main(String[] args) throws Exception {
        int n = 25000000;
        if (args.length > 0) {
            n = Integer.parseInt(args[0]);
        }

        String alu =
            "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG"
          + "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA"
          + "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT"
          + "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA"
          + "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG"
          + "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC"
          + "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

        NucProb[] iub = new NucProb[] {
            new NucProb('a', 0.27),
            new NucProb('c', 0.12),
            new NucProb('g', 0.12),
            new NucProb('t', 0.27),
            new NucProb('B', 0.02),
            new NucProb('D', 0.02),
            new NucProb('H', 0.02),
            new NucProb('K', 0.02),
            new NucProb('M', 0.02),
            new NucProb('N', 0.02),
            new NucProb('R', 0.02),
            new NucProb('S', 0.02),
            new NucProb('V', 0.02),
            new NucProb('W', 0.02),
            new NucProb('Y', 0.02)
        };

        NucProb[] homosapiens = new NucProb[] {
            new NucProb('a', 0.3029549426680),
            new NucProb('c', 0.1979883004921),
            new NucProb('g', 0.1975473066391),
            new NucProb('t', 0.3015094502008)
        };

        NucProb[] iubCum = cumulative(iub);
        NucProb[] hsCum = cumulative(homosapiens);

        try (BufferedOutputStream out = new BufferedOutputStream(System.out)) {
            writeHeader(out, "ONE Homo sapiens alu");
            writeRepeated(out, alu, 2 * n);

            writeHeader(out, "TWO IUB ambiguity codes");
            writeRandom(out, iubCum, 3 * n);

            writeHeader(out, "THREE Homo sapiens frequency");
            writeRandom(out, hsCum, 5 * n);
        }
    }
}
