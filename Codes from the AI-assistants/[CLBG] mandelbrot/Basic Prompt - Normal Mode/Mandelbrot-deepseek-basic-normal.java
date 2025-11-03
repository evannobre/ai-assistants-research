import java.io.*;

public class Mandelbrot {
    public static void mandelbrot(int size, int maxIter) throws IOException {
        BufferedOutputStream out = new BufferedOutputStream(System.out);
        
        // Write PBM header
        out.write(("P4\n" + size + " " + size + "\n").getBytes());
        
        double yStep = 2.0 / size;
        double xStep = 2.0 / size;
        int bytesPerRow = (size + 7) / 8;
        
        for (int y = 0; y < size; y++) {
            double cIm = -1.0 + y * yStep;
            byte currentByte = 0;
            int bitPos = 0;
            
            for (int x = 0; x < size; x++) {
                double cRe = -1.5 + x * xStep;
                
                // Check main cardioid and period-2 bulb
                double q = (cRe - 0.25) * (cRe - 0.25) + cIm * cIm;
                int iter;
                if (q * (q + (cRe - 0.25)) <= 0.25 * cIm * cIm ||
                    (cRe + 1) * (cRe + 1) + cIm * cIm <= 0.0625) {
                    iter = maxIter;
                } else {
                    // Standard iteration
                    double zRe = 0.0, zIm = 0.0;
                    iter = 0;
                    while (iter < maxIter && zRe * zRe + zIm * zIm <= 4.0) {
                        double newRe = zRe * zRe - zIm * zIm + cRe;
                        double newIm = 2 * zRe * zIm + cIm;
                        zRe = newRe;
                        zIm = newIm;
                        iter++;
                    }
                }
                
                // Set bit if in Mandelbrot set
                if (iter == maxIter) {
                    currentByte |= (1 << (7 - bitPos));
                }
                
                bitPos++;
                if (bitPos == 8 || x == size - 1) {
                    out.write(currentByte);
                    currentByte = 0;
                    bitPos = 0;
                }
            }
        }
        out.flush();
    }
    
    public static void main(String[] args) throws IOException {
        int size = args.length > 0 ? Integer.parseInt(args[0]) : 1000;
        int maxIter = args.length > 1 ? Integer.parseInt(args[1]) : 1000;
        mandelbrot(size, maxIter);
    }
}