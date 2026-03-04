import numpy as np
import sys
from PIL import Image

def mandelbrot_numpy(size=16000, max_iter=255):
    # Create coordinate grids
    x = np.linspace(-2.0, 0.5, size, dtype=np.float32)
    y = np.linspace(-1.25, 1.25, size, dtype=np.float32)
    c = x[:, None] + 1j * y[None, :]
    
    # Vectorized Mandelbrot iteration
    z = np.zeros_like(c, dtype=np.complex64)
    mask = np.ones_like(c, dtype=bool)
    output = np.zeros((size, size), dtype=np.uint8)
    
    for i in range(max_iter):
        z[mask] = z[mask] * z[mask] + c[mask]
        mask = np.abs(z) <= 2.0
        output[~mask] = i
    
    # Create PBM image (binary: 0 inside, 255 outside)
    image = Image.fromarray(output)
    image.save('mandelbrot.pbm')
    
    return output

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 16000
    mandelbrot_numpy(size)