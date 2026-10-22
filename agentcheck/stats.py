import math


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - w) / d, (c + w) / d)


def mcnemar_exact(b, c):
    """Two-sided exact p for discordant pairs b (base pass->cand fail) and c (base fail->cand pass)."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)
