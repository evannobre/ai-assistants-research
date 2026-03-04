import numpy as np

def fannkuch_redux_numpy(n):
    perm = np.arange(n, dtype=np.int32)
    perm1 = np.arange(n, dtype=np.int32)
    count = np.arange(1, n+1, dtype=np.int32)
    
    max_flips = 0
    checksum = 0
    sign = 1
    
    while True:
        k = perm[0]
        
        if k != 0:
            np.copyto(perm1, perm)
            flips = 0
            
            while k != 0:
                perm1[:k+1] = perm1[k::-1]  # Reverse using NumPy slicing
                flips += 1
                k = perm1[0]
            
            max_flips = max(max_flips, flips)
            checksum += sign * flips
        
        sign = -sign
        
        i = 1
        while i < n:
            first = perm[0]
            perm[:i] = perm[1:i+1]
            perm[i] = first
            
            count[i] -= 1
            if count[i] > 0:
                break
            
            count[i] = i + 1
            i += 1
        else:
            break
    
    return checksum, max_flips