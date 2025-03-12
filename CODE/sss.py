import random
from sympy import mod_inverse

PRIME = 208351617316091241234326746312124448251235562226470491514186331217050270460481

def eval_polynomial(coeffs, x, prime=PRIME):
    """Evaluate polynomial at x using modular arithmetic."""
    return sum([coeff * (x ** i) % prime for i, coeff in enumerate(coeffs)]) % prime

def generate_shares(secret, k, n):
    """Generate `n` shares with `k` required to reconstruct."""
    coeffs = [secret] + [random.randint(1, PRIME - 1) for _ in range(k - 1)]
    shares = [(x, eval_polynomial(coeffs, x)) for x in range(1, n + 1)]
    return shares

def reconstruct_secret(shares, prime=PRIME):
    """Reconstruct the secret using Lagrange Interpolation."""
    def lagrange_interpolate(x, x_s, y_s, p):
        total = 0
        for i in range(len(x_s)):
            num, den = 1, 1
            for j in range(len(x_s)):
                if i != j:
                    num = (num * (x - x_s[j])) % p
                    den = (den * (x_s[i] - x_s[j])) % p
            total += (y_s[i] * num * mod_inverse(den, p)) % p
        return total % p

    x_s, y_s = zip(*shares)
    return lagrange_interpolate(0, x_s, y_s, prime)

# Define a secret (numeric)
secret = 123456789  # Secret to split

# Split into 5 shares, requiring any 3 to reconstruct
shares = generate_shares(secret, 3, 5)
print("Generated Shares:", shares)

# Use any 3 shares to reconstruct
subset_of_shares = shares[:1]
recovered_secret = reconstruct_secret(subset_of_shares)
print("\nRecovered Secret:", recovered_secret)
