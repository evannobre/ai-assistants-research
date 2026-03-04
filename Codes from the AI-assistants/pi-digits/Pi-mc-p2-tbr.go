// pi_chudnovsky.go
//
// Compute N decimal digits of Pi using Chudnovsky formula with binary splitting.
// Uses only Go standard library: math/big, flag, fmt, os.
// Build: go build -o pi_chudnovsky pi_chudnovsky.go
// Run: ./pi_chudnovsky -digits 1000 -out pi.txt

package main

import (
    "flag"
    "fmt"
    "log"
    "math"
    "math/big"
    "os"
    "time"
)

// Constants used by Chudnovsky
var (
    A = big.NewInt(13591409)
    B = big.NewInt(545140134)
    C = big.NewInt(640320) // base
    // C3 = 640320^3 used in denominators
)

func main() {
    digits := flag.Int("digits", 1000, "number of decimal digits of Pi to compute")
    outFile := flag.String("out", "", "output file (default stdout)")
    flag.Parse()

    if *digits <= 0 {
        log.Fatalf("digits must be > 0")
    }

    start := time.Now()

    // Estimate number of terms K needed: ~ digits / 14.181647...
    terms := int(math.Ceil(float64(*digits) / 14.181647462725477))
    // Add a small safety margin
    terms += 2

    fmt.Fprintf(os.Stderr, "Computing %d digits using %d terms\n", *digits, terms)

    // Binary splitting to compute P, Q, T for k in [0, terms)
    P, Q, T := binarySplit(0, terms)

    // Compute pi = (Q * 426880 * sqrt(10005)) / T
    // Convert Q and T to big.Float with sufficient precision
    // bits = digits * log2(10) + margin
    bits := uint(float64(*digits)*3.3219280948873626) + 64

    // Convert big.Int to big.Float
    Qf := new(big.Float).SetPrec(bits).SetInt(Q)
    Tf := new(big.Float).SetPrec(bits).SetInt(T)

    // sqrt(10005)
    sqrtArg := new(big.Float).SetPrec(bits).SetFloat64(10005.0)
    sqrtVal := new(big.Float).SetPrec(bits).Sqrt(sqrtArg)

    // numerator = Q * 426880 * sqrt(10005)
    numer := new(big.Float).SetPrec(bits).Mul(Qf, new(big.Float).SetPrec(bits).SetInt(big.NewInt(426880)))
    numer.Mul(numer, sqrtVal)

    piFloat := new(big.Float).SetPrec(bits).Quo(numer, Tf)

    // Format pi to decimal with N digits
    // big.Float.Text('f', n) prints n digits after decimal point.
    // We need 1 digit before decimal and N digits after decimal.
    // So request precision = digits
    // But Text('f', n) uses decimal places, so we ask for digits.
    piStr := piFloat.Text('f', *digits)

    // Output
    if *outFile == "" {
        fmt.Println(piStr)
    } else {
        f, err := os.Create(*outFile)
        if err != nil {
            log.Fatalf("failed to create output file: %v", err)
        }
        defer f.Close()
        _, err = f.WriteString(piStr + "\n")
        if err != nil {
            log.Fatalf("failed to write output: %v", err)
        }
        fmt.Fprintf(os.Stderr, "Wrote %d digits to %s\n", *digits, *outFile)
    }

    elapsed := time.Since(start)
    fmt.Fprintf(os.Stderr, "Done in %s\n", elapsed)
}

// binarySplit computes P(a,b), Q(a,b), T(a,b) for Chudnovsky series on interval [a,b).
// Returns pointers to big.Int: P, Q, T.
func binarySplit(a, b int) (*big.Int, *big.Int, *big.Int) {
    if b-a == 1 {
        // Base case: single term k = a
        k := int64(a)

        // Pk = (6k)! / ((3k)! * (k!)^3) * (-1)^k  but we compute Pk as integer factor used in combination
        // For binary splitting we use:
        // P = (6k-5)*(2k-1)*(6k-1) ... but simpler and robust: compute directly using factorials with big.Int
        // However computing factorials each base is expensive; instead use direct formula for term components:
        // For Chudnovsky, the term numerator components are:
        // a_k = ( (-1)^k * (6k)! * (13591409 + 545140134 k) )
        // b_k = (3k)! * (k!)^3 * 640320^{3k}
        // In binary splitting we set:
        // P = numerator multiplier (6k)! / ((3k)! * (k!)^3) * (-1)^k
        // Q = 640320^{3k}
        // T = P * (13591409 + 545140134 k)
        // We'll compute P, Q, T directly using big.Int arithmetic.

        // Compute P = (6k)! / ((3k)! * (k!)^3) * (-1)^k
        // We'll compute factorials using iterative multiplication for small k; for large k this base case is called many times but k is small per base.
        // Use big.Int factorials:
        sixk := 6 * k
        threek := 3 * k

        f6k := factorialBig(sixk)
        f3k := factorialBig(threek)
        fk := factorialBig(k)

        den := new(big.Int).Mul(f3k, new(big.Int).Mul(fk, new(big.Int).Mul(fk, fk))) // (3k)! * (k!)^3
        P := new(big.Int).Quo(f6k, den)

        // Apply sign (-1)^k
        if (k & 1) == 1 {
            P.Neg(P)
        }

        // Q = 640320^(3k)
        exp := 3 * k
        Q := new(big.Int).Exp(C, big.NewInt(exp), nil)

        // T = P * (13591409 + 545140134*k)
        coef := new(big.Int).Mul(B, big.NewInt(k))
        coef.Add(coef, A) // 13591409 + 545140134*k
        T := new(big.Int).Mul(P, coef)

        return P, Q, T
    }

    // Recursive split
    m := (a + b) / 2
    P1, Q1, T1 := binarySplit(a, m)
    P2, Q2, T2 := binarySplit(m, b)

    // P = P1 * P2
    P := new(big.Int).Mul(P1, P2)

    // Q = Q1 * Q2
    Q := new(big.Int).Mul(Q1, Q2)

    // T = T1 * Q2 + P1 * T2
    tmp1 := new(big.Int).Mul(T1, Q2)
    tmp2 := new(big.Int).Mul(P1, T2)
    T := new(big.Int).Add(tmp1, tmp2)

    return P, Q, T
}

// factorialBig computes n! as big.Int
// Note: naive multiplication; for large n this is expensive if called many times.
// In practice binary splitting base case count is small relative to overall cost.
// If you need extreme performance, replace with a cached factorial or prime-swing algorithm.
func factorialBig(n int64) *big.Int {
    if n < 2 {
        return big.NewInt(1)
    }
    res := big.NewInt(1)
    tmp := new(big.Int)
    for i := int64(2); i <= n; i++ {
        tmp.SetInt64(i)
        res.Mul(res, tmp)
    }
    return res
}
