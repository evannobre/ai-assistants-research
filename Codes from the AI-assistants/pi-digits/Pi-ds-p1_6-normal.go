// pi_generator.go
package main

import (
    "fmt"
    "math/big"
    "os"
    "strconv"
)

func chudnovskyPi(digits int64) *big.Float {
    precision := uint(digits + 10)
    
    // Constants
    C := new(big.Float).SetPrec(precision).SetFloat64(426880)
    sqrt10005 := new(big.Float).SetPrec(precision).SetFloat64(10005)
    sqrt10005.Sqrt(sqrt10005)
    C.Mul(C, sqrt10005)
    
    K := new(big.Float).SetPrec(precision).SetFloat64(6)
    M := new(big.Float).SetPrec(precision).SetFloat64(1)
    X := new(big.Float).SetPrec(precision).SetFloat64(1)
    L := new(big.Float).SetPrec(precision).SetFloat64(13591409)
    S := new(big.Float).SetPrec(precision).SetFloat64(13591409)
    
    iterations := int(digits/14 + 10)
    
    for i := 1; i <= iterations; i++ {
        // M = (K^3 - 16K) * M / i^3
        i3 := new(big.Float).SetPrec(precision).SetFloat64(float64(i * i * i))
        k3 := new(big.Float).SetPrec(precision).SetFloat64(0)
        k3.Mul(K, K).Mul(k3, K)
        k16 := new(big.Float).SetPrec(precision).SetFloat64(0)
        k16.Mul(K, new(big.Float).SetFloat64(16))
        temp := new(big.Float).SetPrec(precision).SetFloat64(0)
        temp.Sub(k3, k16).Mul(temp, M).Quo(temp, i3)
        M.Set(temp)
        
        // L += 545140134
        L.Add(L, new(big.Float).SetFloat64(545140134))
        
        // X *= -262537412640768000
        X.Mul(X, new(big.Float).SetFloat64(-262537412640768000))
        
        // S += M * L / X
        term := new(big.Float).SetPrec(precision).SetFloat64(0)
        term.Mul(M, L).Quo(term, X)
        S.Add(S, term)
        
        // K += 12
        K.Add(K, new(big.Float).SetFloat64(12))
    }
    
    // pi = C / S
    pi := new(big.Float).SetPrec(precision).SetFloat64(0)
    pi.Quo(C, S)
    return pi
}

func main() {
    if len(os.Args) != 2 {
        fmt.Println("Usage: go run pi_generator.go <digits>")
        os.Exit(1)
    }
    
    digits, err := strconv.ParseInt(os.Args[1], 10, 64)
    if err != nil || digits <= 0 {
        fmt.Println("Please provide a positive integer")
        os.Exit(1)
    }
    
    fmt.Printf("Generating %d digits of Pi...\n", digits)
    pi := chudnovskyPi(digits)
    fmt.Printf("%.*f\n", int(digits), pi)
}