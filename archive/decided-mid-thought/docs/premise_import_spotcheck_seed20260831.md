# Premise-import spot-check — seed 20260831, 5 of 194 sweep traces
Criterion: first occurrence of '1.00 more' in the trace. For each excerpt,
confirm by eye: the model is importing the famous constraint ('the bat costs
$1.00 more than the ball'), not hitting 1.00 by numeric coincidence.

## eval1_multi0 / sample 2  (first '1.00' at 0.100 of trace)
... "Answer: X" |  | 2.  **Identify the Core Problem:** |    - This is a classic cognitive reflection test (CRT) problem by Shane Frederick. |    - The standard formulation is: "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?" |    - The *given* problem here is slightly different: "The bat costs *more than* the ball." (Not "$1.00 more than") |    - Let's...

## eval1_multi0 / sample 0  (first '1.00' at 0.062 of trace)
...- Task: Explain reasoning, then output "Answer: X" |  | 2.  **Identify the Core Problem:** |    - This is a classic cognitive reflection test (CRT) problem. |    - The standard version adds a crucial constraint: "The bat costs $1.00 more than the ball." |    - Let's check the exact wording provided: "A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?" |    - W...

## eval0_multi1 / sample 32  (first '1.00' at 0.065 of trace)
... is a famous cognitive psychology puzzle (the Cognitive Reflection Test, by Shane Frederick). |    - The intuitive/impulsive answer is $0.05 for the ball. |    - If the ball is $0.05, the bat would be $1.05 (since it costs $1.00 more than the ball, wait, the prompt says "The bat costs more than the ball." It does *not* say "The bat costs $1.00 more than the ball." Let me double-check the exact wording...

## eval1_multi0 / sample 27  (first '1.00' at 0.078 of trace)
...g, end with "Answer: X" |  | 2.  **Identify the Core Problem:** |    - This is a classic cognitive reflection test (CRT) problem by Shane Frederick. |    - Standard version: "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?" |    - Wait, the prompt says: "The bat costs more than the ball." It does *not* say "$1.00 more". It just says "more". |    - Let...

## eval0_multi1 / sample 18  (first '1.00' at 0.063 of trace)
... The intuitive answer is $0.05, but it's actually incorrect. |    - Let's solve it mathematically: |      Let $b$ = cost of ball, $B$ = cost of bat. |      $b + B = 1.10$ |      The standard version usually says "The bat costs $1.00 more than the ball." Wait, the prompt says: "The bat costs more than the ball." It does *not* specify how much more. |      Let me re-read carefully: "A bat and a ball cost $1.1...
