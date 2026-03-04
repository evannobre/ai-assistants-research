from decimal import Decimal, getcontext

def arctan_ap(x, precision):
    getcontext().prec = precision + 5 # Higher internal precision
    sum_val = Decimal(0)
    term = Decimal(x)
    power_x = Decimal(x * x)
    denominator = 1
    sign = 1
    while abs(term) > Decimal(10)**(-precision - 1):
        sum_val += sign * term / denominator
        term *= -power_x
        denominator += 2
        sign *= -1
    return sum_val

def pi_n_digits(n):
    getcontext().prec = n + 10 # Set working precision
    # Using Machin's formula: pi/4 = 4*arctan(1/5) - arctan(1/239)
    term1 = arctan_ap(Decimal(1)/Decimal(5), n)
    term2 = arctan_ap(Decimal(1)/Decimal(239), n)
    pi_val = 4 * (4 * term1 - term2)
    return format(pi_val, f".{n}f")

if __name__ == "__main__":
    num_digits = 100
    pi_hundred_digits = pi_n_digits(num_digits)
    print(f"First {num_digits} digits of Pi:\n{pi_hundred_digits}")