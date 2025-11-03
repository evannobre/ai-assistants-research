import sys
import struct

def mandelbrot(N, max_iter=50):
    # Output header for portable bitmap (PBM) format
    sys.stdout.buffer.write(b'P4\n%d %d\n' % (N, N))

    for y in range(N):
        row = bytearray()
        byte = 0
        bits = 0
        for x in range(N):
            # Map pixel to complex plane
            re = (x / N) * 2.0 - 1.5
            im = (y / N) * 2.0 - 1.0
            c = complex(re, im)
            z = 0j
            for i in range(max_iter):
                z = z*z + c
                if abs(z) > 2.0:
                    break
            # Set bit: 1 if inside Mandelbrot set
            byte = (byte << 1) | (i == max_iter - 1)
            bits += 1
            if bits == 8:
                row.append(byte)
                byte = 0
                bits = 0
        if bits:
            row.append(byte << (8 - bits))
        sys.stdout.buffer.write(row)

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 16000
    mandelbrot(N)