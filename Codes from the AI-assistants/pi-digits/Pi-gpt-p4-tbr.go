package main

import (
	"bufio"
	"fmt"
	"math/big"
	"os"
	"strconv"
)

// This implements the unbounded spigot algorithm for pi digits (base 10)
// in the style used by the Computer Language Benchmarks Game "pidigits":
// it performs both extract(3) and extract(4) to decide when a digit is safe.
//
// State: (q, r, t, k, n, l) as big.Int.
// extract(j) = floor((q*j + r) / t).
//
// If extract(3) == extract(4), emit that digit and "produce" transition.
// Else, "consume" transition.
//
// Output: 10 digits per line, then "\t:%d\n" with total digits emitted.

type spigot struct {
	q, r, t big.Int
	k, l    big.Int

	// Temporaries to avoid excessive allocations (does not change the algorithm).
	tmp1 big.Int
	tmp2 big.Int
	tmp3 big.Int
	tmp4 big.Int
	tmp5 big.Int
}

func newSpigot() *spigot {
	s := &spigot{}
	s.q.SetInt64(1)
	s.r.SetInt64(0)
	s.t.SetInt64(1)
	s.k.SetInt64(1)
	s.l.SetInt64(3)
	return s
}

// extract(j) = floor((q*j + r) / t)
func (s *spigot) extract(j int64) int64 {
	// tmp1 = q * j
	s.tmp1.Mul(&s.q, big.NewInt(j))
	// tmp1 = tmp1 + r
	s.tmp1.Add(&s.tmp1, &s.r)
	// tmp1 = tmp1 / t
	s.tmp1.Quo(&s.tmp1, &s.t)
	return s.tmp1.Int64()
}

// produce(d): transition after emitting digit d
// (q, r, t, k, n, l) -> (10*q, 10*(r - d*t), t, k, floor(10*(3*q+r)/t) - 10*d, l)
func (s *spigot) produce(d int64) {
	// Compute new_n = floor(10*(3*q + r)/t) - 10*d, using OLD q,r,t.
	// tmp1 = 3*q
	s.tmp1.Mul(&s.q, big.NewInt(3))
	// tmp1 = tmp1 + r
	s.tmp1.Add(&s.tmp1, &s.r)
	// tmp1 = tmp1 * 10
	s.tmp1.Mul(&s.tmp1, big.NewInt(10))
	// tmp1 = tmp1 / t
	s.tmp1.Quo(&s.tmp1, &s.t)
	// tmp1 = tmp1 - 10*d
	s.tmp1.Sub(&s.tmp1, big.NewInt(10*d))
	// store new_n in tmp2
	s.tmp2.Set(&s.tmp1)

	// Compute new_r = 10*(r - d*t), using OLD r,t.
	// tmp3 = d * t
	s.tmp3.Mul(&s.t, big.NewInt(d))
	// tmp3 = r - tmp3
	s.tmp3.Sub(&s.r, &s.tmp3)
	// tmp3 = tmp3 * 10
	s.tmp3.Mul(&s.tmp3, big.NewInt(10))

	// Update q = 10*q
	s.q.Mul(&s.q, big.NewInt(10))
	// Update r = new_r
	s.r.Set(&s.tmp3)
	// t,k,l unchanged
	// (We don't store n persistently; we always use extract(3)/extract(4) as required.)
	_ = s.tmp2 // kept to mirror the reference recurrence; extract() drives output.
}

// consume(): transition when digit is not yet safe
// (q, r, t, k, n, l) -> (q*k, (2*q+r)*l, t*l, k+1, floor((q*(7*k+2)+r*l)/(t*l)), l+2)
func (s *spigot) consume() {
	// We'll compute new_q, new_r, new_t, then increment k and l.
	// Need OLD values for all computations.

	// denom = t*l
	s.tmp1.Mul(&s.t, &s.l) // tmp1 = denom

	// numerator = q*(7*k+2) + r*l
	// tmp2 = 7*k + 2
	s.tmp2.Mul(&s.k, big.NewInt(7))
	s.tmp2.Add(&s.tmp2, big.NewInt(2))
	// tmp3 = q*(7*k+2)
	s.tmp3.Mul(&s.q, &s.tmp2)
	// tmp4 = r*l
	s.tmp4.Mul(&s.r, &s.l)
	// tmp3 = tmp3 + tmp4
	s.tmp3.Add(&s.tmp3, &s.tmp4)
	// new_n = numerator / denom (not stored; extract() drives output)
	s.tmp5.Quo(&s.tmp3, &s.tmp1)

	// new_r = (2*q + r)*l
	// tmp2 = 2*q
	s.tmp2.Mul(&s.q, big.NewInt(2))
	// tmp2 = 2*q + r
	s.tmp2.Add(&s.tmp2, &s.r)
	// tmp2 = tmp2 * l
	s.tmp2.Mul(&s.tmp2, &s.l) // tmp2 = new_r

	// new_q = q*k
	s.tmp3.Mul(&s.q, &s.k) // tmp3 = new_q

	// new_t = t*l (already in tmp1)
	// Apply updates:
	s.q.Set(&s.tmp3)
	s.r.Set(&s.tmp2)
	s.t.Set(&s.tmp1)

	// k = k + 1
	s.k.Add(&s.k, big.NewInt(1))
	// l = l + 2
	s.l.Add(&s.l, big.NewInt(2))
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: pidigits N")
		os.Exit(2)
	}
	N, err := strconv.Atoi(os.Args[1])
	if err != nil || N < 0 {
		fmt.Fprintln(os.Stderr, "N must be a non-negative integer")
		os.Exit(2)
	}

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer w.Flush()

	s := newSpigot()

	digitsEmitted := 0
	lineCount := 0
	line := make([]byte, 0, 10)

	for digitsEmitted < N {
		d3 := s.extract(3)
		d4 := s.extract(4)

		if d3 == d4 {
			// Emit digit d3
			line = append(line, byte('0'+d3))
			digitsEmitted++
			lineCount++

			// Update state using "produce" transition
			s.produce(d3)

			// Print 10 digits per line, with padding on last line.
			if lineCount == 10 || digitsEmitted == N {
				// pad with spaces if last line is short
				for len(line) < 10 {
					line = append(line, ' ')
				}
				fmt.Fprintf(w, "%s\t:%d\n", string(line), digitsEmitted)
				line = line[:0]
				lineCount = 0
			}
		} else {
			// Not safe yet; consume next term
			s.consume()
		}
	}
}
