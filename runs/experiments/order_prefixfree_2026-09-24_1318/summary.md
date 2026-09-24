# Order of algebra (A) and constraint import (K) in the 69 prefix-free texts

patterns: {'A first': 19, 'K first': 48, 'tie': 2, 'missing': 0}

| arm | n | C | E | ? | P(C) [Wilson 95%] |
|---|---|---|---|---|---|
| A first | 19 | 5 | 13 | 1 | 0.26 [0.12, 0.49] |
| K first, ties included | 50 | 2 | 44 | 4 | 0.04 [0.01, 0.13] |

difference +0.22 [0.05, 0.45]; Fisher (unresolved as not C) p = 0.0145; most adverse assignment of the unresolved p = 0.1606; answered only (5, 18) vs (2, 46) p = 0.0157

sensitivity: ties with A first {"A": {"n": 21, "C": 5, "E": 15, "?": 1, "other": 0}, "K": {"n": 48, "C": 2, "E": 42, "?": 4, "other": 0}} p = 0.0238
ties excluded {"A": {"n": 19, "C": 5, "E": 13, "?": 1, "other": 0}, "K": {"n": 48, "C": 2, "E": 42, "?": 4, "other": 0}} p = 0.0166
cut0 only {"A": {"n": 5, "C": 2, "E": 2, "?": 1, "other": 0}, "K": {"n": 20, "C": 1, "E": 16, "?": 3, "other": 0}} p = 0.0913
sweep44 only {"A": {"n": 14, "C": 3, "E": 11, "?": 0, "other": 0}, "K": {"n": 30, "C": 1, "E": 28, "?": 1, "other": 0}} p = 0.0878
without the two source traces {"A": {"n": 17, "C": 4, "E": 12, "?": 1, "other": 0}, "K": {"n": 50, "C": 2, "E": 44, "?": 4, "other": 0}} p = 0.0324

source traces: {"c004": {"first_A": 10, "first_K": 42, "pattern": "A first", "A_text": "\u23ce    *   *Equation 1:* Bat + Ball = 1.10", "K_text": "But wait, the problem usually adds the constraint \"The bat costs **\\$1.00 more than the ball**.\""}, "e036": {"first_A": 17, "first_K": 18, "pattern": "A first", "A_text": "Ball = $x$,", "K_text": "Bat = $x + 1.00$"}}
