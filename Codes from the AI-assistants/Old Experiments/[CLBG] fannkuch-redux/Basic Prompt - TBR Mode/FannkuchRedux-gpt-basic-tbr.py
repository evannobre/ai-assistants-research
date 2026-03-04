def fannkuch(n):
    perm1 = list(range(n))
    perm = [0]*n
    count = [0]*n
    checksum = 0
    maxflips = 0
    sign = 1

    while True:
        perm[:] = perm1[:]          # fast list copy
        flips = 0
        if perm[0] != 0:
            while True:
                k = perm[0]
                i, j = 0, k
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1; j -= 1
                flips += 1
                if perm[0] == 0:
                    break

        checksum += sign * flips
        if flips > maxflips:
            maxflips = flips

        # generate next permutation
        i = 1
        while i < n:
            count[i] += 1
            if count[i] <= i:
                # rotate left first i+1 elements
                first = perm1.pop(0)
                perm1.append(first)
                break
            count[i] = 0
            i += 1
        if i == n:
            break
        sign = -sign

    return checksum, maxflips
