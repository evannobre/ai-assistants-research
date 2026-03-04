import numpy as np

def fannkuch_redux_numpy(n):
    """Optimized version using NumPy."""
    perm = np.arange(n, dtype=np.int32)
    perm1 = np.arange(n, dtype=np.int32)
    count = np.arange(n, 0, -1, dtype=np.int32)
    
    maxflips = 0
    checksum = 0
    sign = 1
    
    while True:
        np.copyto(perm, perm1)
        flips = 0
        k = perm[0]
        
        while k != 0:
            perm[:k+1] = perm[k::-1]
            flips += 1
            k = perm[0]
        
        maxflips = max(maxflips, flips)
        checksum += flips * sign
        sign = -sign
        
        done = True
        k = n - 1
        while k > 0:
            count[k] -= 1
            if count[k] > 0:
                done = False
                break
            count[k] = k + 1
            k -= 1
        
        if done:
            break
        
        temp = perm1[0]
        perm1[:k+1] = perm1[1:k+2]
        perm1[k+1] = temp
    
    return int(maxflips), int(checksum)