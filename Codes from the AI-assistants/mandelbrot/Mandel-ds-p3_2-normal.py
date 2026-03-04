import sys
import numpy as np
import time

def mandelbrot(N, max_iter=1000):
    """Generate Mandelbrot set as grayscale PGM image."""
    
    # Complex grid
    x = np.linspace(-2.0, 1.0, N, dtype=np.float64)
    y = np.linspace(-1.5, 1.5, N, dtype=np.float64)
    X, Y = np.meshgrid(x, y)
    C = X + Y * 1j
    
    # Initialize arrays
    Z = np.zeros_like(C, dtype=np.complex128)
    M = np.full(C.shape, True, dtype=bool)
    I = np.zeros(C.shape, dtype=int)
    
    # Vectorized iteration
    for i in range(max_iter):
        Z[M] = Z[M] * Z[M] + C[M]
        mask = np.abs(Z) > 2.0
        I[mask & M] = i
        M[mask] = False
        
        if not np.any(M):
            break
    
    # Set interior points to max_iter
    I[M] = max_iter
    
    # Convert to grayscale (0-255)
    image = np.uint8(255 * I / max_iter)
    return image

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} N")
        sys.exit(1)
    
    N = int(sys.argv[1])
    max_iter = 1000
    
    start = time.time()
    
    # Generate image
    image = mandelbrot(N, max_iter)
    
    # Write PGM (P5 format)
    sys.stdout.buffer.write(f"P5\n{N} {N}\n255\n".encode())
    sys.stdout.buffer.write(image.tobytes())
    
    elapsed = time.time() - start
    sys.stderr.write(f"Time: {elapsed:.2f} seconds\n")

if __name__ == "__main__":
    main()