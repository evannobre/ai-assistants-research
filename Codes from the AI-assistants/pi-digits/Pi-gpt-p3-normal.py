#!/usr/bin/env python3
"""
Spigot (LFT) algorithm for generating N digits of Pi (pidigits benchmark style).

Requirements satisfied:
- Native arbitrary precision arithmetic (Python built-in int).
- Sequential, single-threaded, step-by-step algorithm.
- Uses both extract(3) and extract(4) each digit decision.
- Prints 10 digits per line with running total of digits calculated.
- Does not optimize away the work (keeps the canonical LFT spigot steps).
"""

import sys


class LFT:
    # Represents the linear fractional transformation:
    #   x -> (q*x + r) / (s*x + t)
    __slots__ = ("q", "r", "s", "t")

    def __init__(self, q: int, r: int, s: int, t: int):
        self.q = q
        self.r = r
        self.s = s
        self.t = t

    def extract(self, j: int) -> int:
        # floor((q*j + r) / (s*j + t))
        return (self.q * j + self.r) // (self.s * j + self.t)

    def compose(self, other: "LFT") -> None:
        # self := self ∘ other  (apply other, then self)
        # If self(x) = (q1 x + r1)/(s1 x + t1)
        # and other(x) = (q2 x + r2)/(s2 x + t2)
        # then self(other(x)) is:
        #   ( (q1*q2 + r1*s2) x + (q1*r2 + r1*t2) ) /
        #   ( (s1*q2 + t1*s2) x + (s1*r2 + t1*t2) )
        q1, r1, s1, t1 = self.q, self.r, self.s, self.t
        q2, r2, s2, t2 = other.q, other.r, other.s, other.t

        self.q = q1 * q2 + r1 * s2
        self.r = q1 * r2 + r1 * t2
        self.s = s1 * q2 + t1 * s2
        self.t = s1 * r2 + t1 * t2

    def eliminate(self, digit: int) -> None:
        # After confirming the next digit, adjust transformation:
        # x -> 10*(x - digit)
        self.q *= 10
        self.r = 10 * (self.r - digit * self.t)
        # self.s, self.t unchanged


def term(k: int) -> LFT:
    # Next term in the continued fraction expansion used by this spigot:
    #   [ [k, 4k+2],
    #     [0, 2k+1] ]
    return LFT(k, 4 * k + 2, 0, 2 * k + 1)


def pidigits(n: int) -> None:
    z = LFT(1, 0, 0, 1)
    k = 1

    produced = 0
    line_digits = []

    out = sys.stdout.write

    while produced < n:
        # Must do both extract(3) and extract(4)
        y = z.extract(3)
        if y == z.extract(4):
            # Digit is safe to emit
            line_digits.append(chr(ord("0") + y))
            produced += 1
            z.eliminate(y)

            if len(line_digits) == 10:
                out("".join(line_digits) + "\t:" + str(produced) + "\n")
                line_digits.clear()
        else:
            # Advance transformation by composing with next term
            z.compose(term(k))
            k += 1

    # Flush partial last line (pad with spaces to 10 like the benchmark style)
    if line_digits:
        out("".join(line_digits) + " " * (10 - len(line_digits)) + "\t:" + str(produced) + "\n")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write(f"Usage: {argv[0]} N\n")
        return 2
    try:
        n = int(argv[1])
        if n < 0:
            raise ValueError
    except ValueError:
        sys.stderr.write("N must be a non-negative integer.\n")
        return 2

    pidigits(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
