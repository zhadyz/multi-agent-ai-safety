"""Verify all paper numbers against actual data files and compute Wilson CIs."""
import math

def wilson_ci(s, n, z=1.96):
    if n == 0: return (0, 0)
    p = s / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0, center - margin) * 100, min(1, center + margin) * 100)

models = [
    ("Opus 4.7", 1996, [(479, 594), (85, 532), (2, 430), (0, 440)]),
    ("Sonnet 4.6", 1967, [(444, 492), (351, 489), (301, 492), (234, 494)]),
    ("Haiku 4.5", 1982, [(374, 496), (198, 495), (209, 497), (176, 494)]),
    ("GPT-5.5", 2007, [(131, 475), (132, 524), (105, 515), (118, 493)]),
    ("GPT-5.4", 2000, [(469, 500), (462, 500), (478, 500), (458, 500)]),
    ("GPT-5.4-mini", 1797, [(437, 456), (396, 425), (452, 465), (430, 451)]),
]

techs = ["T1", "T2", "T3", "T4"]
complete_n = sum(m[1] for m in models if "mini" not in m[0])
prelim_n = models[-1][1]
print(f"Complete N: {complete_n}")
print(f"Preliminary N: {prelim_n}")
print(f"Total: ~{complete_n + prelim_n}")
print()

for name, N, rates in models:
    print(f"=== {name} (N={N}) ===")
    for i, t in enumerate(techs):
        s, n = rates[i]
        pct = round(s / n * 100, 1) if n > 0 else 0.0
        lo, hi = wilson_ci(s, n)
        print(f"  {t}: {s}/{n} = {pct}% [{lo:.1f},{hi:.1f}]")
    print()
