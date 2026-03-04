import java.io.*;
import java.nio.file.*;

public class Mandelbrot {
    private static final int WIDTH = 800;
    private static final int HEIGHT = 600;
    private static final int MAX_ITER = 256;
    
    private static double mapReal(int x) {
        return (x - WIDTH * 2.0 / 3.0) / (WIDTH * 0.4);
    }
    
    private static double mapImag(int y) {
        return (y - HEIGHT / 2.0) / (HEIGHT * 0.4);
    }
    
    private static int mandelbrotIterations(double cr, double ci) {
        double zr = 0.0, zi = 0.0;
        int iter = 0;
        
        while (zr * zr + zi * zi <= 4.0 && iter < MAX_ITER) {
            double zrNew = zr * zr - zi * zi + cr;
            zi = 2 * zr * zi + ci;
            zr = zrNew;
            iter++;
        }
        
        return iter;
    }
    
    private static byte[] generatePbm() {
        // PBM format: P4 width height binary_data
        StringBuilder header = new StringBuilder();
        header.append("P4\n").append(WIDTH).append(" ").append(HEIGHT).append("\n");
        byte[] headerBytes = header.toString().getBytes();
        
        // Calculate size needed for binary data
        int rowBytes = (WIDTH + 7) / 8;
        int totalSize = headerBytes.length + rowBytes * HEIGHT;
        byte[] result = new byte[totalSize];
        
        // Copy header
        System.arraycopy(headerBytes, 0, result, 0, headerBytes.length);
        
        int dataIndex = headerBytes.length;
        
        for (int y = 0; y < HEIGHT; y++) {
            double ci = mapImag(y);
            byte currentByte = 0;
            int bitPos = 7;
            
            for (int x = 0; x < WIDTH; x++) {
                double cr = mapReal(x);
                int iter = mandelbrotIterations(cr, ci);
                
                // Set bit if point is in Mandelbrot set
                if (iter == MAX_ITER) {
                    currentByte |= (1 << bitPos);
                }
                
                if (bitPos == 0) {
                    result[dataIndex++] = currentByte;
                    currentByte = 0;
                    bitPos = 7;
                } else {
                    bitPos--;
                }
            }
            
            // Write last byte of row if needed
            if (bitPos != 7) {
                result[dataIndex++] = currentByte;
            }
        }
        
        return result;
    }
    
    public static void main(String[] args) {
        try {
            System.out.println("Generating Mandelbrot set...");
            byte[] pbmData = generatePbm();
            
            Path outputPath = Paths.get("mandelbrot.pbm");
            Files.write(outputPath, pbmData);
            
            System.out.println("Saved to mandelbrot.pbm (" + WIDTH + "x" + HEIGHT + ")");
        } catch (IOException e) {
            System.err.println("Error writing file: " + e.getMessage());
        }
    }
}