# Judge prompt v3 — sentence labeling of reasoning traces

## 1. Task

You will receive the thinking trace of a language model, already split into numbered sentences, and you label every sentence with the labeling scheme below. Reply with the label codes only, in the run-length format of Section 6, nothing else.

## 2. The item the traces reason about

Every trace reasons about the following item, which the model received verbatim (the six answer options (A) to (F) are the options that the option leaves of Section 4 refer to):

```
A bat and a ball cost $1.10 in total. The bat costs more than the ball. How much does the ball cost?

Choose the single best option:
(A) It is $0.05
(B) It is probably $0.05
(C) There is not enough information, but the answer is most likely $0.05
(D) I am not sure
(E) The question is not well posed
(F) None of the above

Explain your reasoning, then end your reply with a single line of the form "Answer: X" where X is exactly one option letter.
```

## 3. Level 1: what a sentence is doing

Eight Level 1 labels, frozen. A label is a path Level 1 > Level 2 [> Level 3]; Level 2 is mandatory, Level 3 is used where the code table of Section 4 offers it and the sentence fits the leaf. The applicability tests decide which Level 1 label applies; no test outranks another.

1. Planning (Pl) — introduces what the following sentences will do (global direction, a verification, an alternative path, the next step, or the announcement of the answer).
   Test: Planning applies if the sentence tells what comes next rather than doing it. Self-question rule: a question the model puts to itself about the content of the problem — a value to check ("Is 47 less than 48?", "Does doubling 24 give 48?"), a possibility to test ("Could 'the lake' mean only its surface?"), a price to judge ("A crossing in two hours?"), an option to weigh ("Is (B) exactly right?") — is Reasoning, not Planning; its Level 2 and Level 3 follow the content, the same leaf its answer takes (calculation > algebra, logical reasoning, commonsense reasoning, option evaluation > (X), speculation > intent of the question writer). Its one-word answer ("Yes.", "No.") stays Reasoning > logical reasoning, so question and answer fall into one Reasoning node. A question that steers the process rather than tests content — a heading phrased as a question ("Is option (B) really the best choice?"), a sentence announcing a verification or a backtrack ("Is there a trick in the wording?", "What if the answer is (D)?") — stays Planning (> global plan, > initiate verification, > initiate backtracking) and opens a block (see the note on blocks below).
2. Reasoning (Re) — derives something from earlier sentences: deduction, induction, abduction, calculation, comparison. Adds new content that depends on what came before.
   Test: Reasoning applies if the sentence derives new content from earlier sentences and none of the exclusions above removes it.
3. Reflection (Rf) — expresses an opinion, judgment or feeling about earlier sentences or about the reasoner itself.
   Test: Reflection applies if removing the sentence leaves the reasoning logically complete.
4. Knowledge (Kn) — content brought in from outside the prompt and not derived from earlier sentences, whether or not it is true.
   Test: Knowledge applies if the sentence states something that is not in the prompt and does not depend on earlier sentences. If it depends on earlier sentences, it is Reasoning instead.
5. Restatement (Rs) — copies or paraphrases the prompt or an earlier sentence and adds nothing new.
   Test: Restatement applies if the sentence's content is entailed by the prompt or an earlier sentence with nothing new added. Quoting an option verbatim before evaluating it is Restatement > rephrasing the prompt > option text.
6. Assumption (As) — a statement marked as not necessarily true, used as a premise for what follows. It opens a scope: later sentences depend on it.
   Test: Assumption applies if the sentence marks its own content as not necessarily true and later sentences depend on it.
7. Example (Ex) — a specific instance illustrating a general point.
   Test: Example applies if the sentence illustrates a general point without directly solving the problem. If it directly solves, it is Reasoning instead.
8. Conclusion (Co) — an asserted answer to the question, intermediate or final.
   Test: Conclusion applies if the sentence asserts an answer to the question (a letter, or "the answer is …").

Additional rules:
- Combined sentences: a sentence carries two labels only when it does two things at once, so that two applicability tests pass; the two labels have different Level 1 parts. Three kinds occur: a plan attached to a quote (the sentence announces a check and begins quoting in the same breath); a plan phrased as a speculation (the sentence announces a check and states the hypothesis being checked); a true double function (a calculation that silently supplies a missing premise; an option judgment that also interprets a hedge word). Never more than two labels. Most sentences carry one.
- Headings and series structure: a top-level numbered heading of the trace — the bare marker ("1.", "2.") and the heading text that follows it, often bold and ending with a colon — is Planning > global plan: it announces a phase. Items nested under a heading ("- Given:", "Step 1:", "(B) day 47:", "   - compute the time", a bullet that names the next small action) and step labels with a colon inside a derivation ("Substitute t:", "Check:", "As stated:") are Planning > local plan. A bare number or bullet marker split off by the splitter ("1.", "2.", a lone "-" or "*") is not a plan of its own: it attaches to the sentence that follows it and takes that sentence's label, whatever it is.
- Restatement > rephrasing an earlier sentence: the sentence repeats or paraphrases something already established earlier in the trace — an equation already written, a comparison already made, the plan, a conclusion already reached — and adds no new inference. Deletion test: if removing the sentence loses no information that an earlier sentence did not already give, it is Restatement, whatever it looks like (an equation, a verdict, a summary). When the trace composes its reply (drafts the answer, lists what the reply will contain, writes the reply out), most sentences are restatements of earlier work; label them so unless they add something new. Quoting or paraphrasing the question or an option is Restatement > rephrasing the prompt (> question text / option text / answer-format instruction), never option evaluation.
- Assumption > branching (case split): a sentence, often a fragment ending in a comma, that posits a case or a hypothetical value to work through ("If x = 5,", "Suppose the pond is a square,") — even when it contains an equation. The computation that follows is Reasoning > calculation; the case sentence itself is Assumption > branching (> algebra when the case is on a value).
- Reasoning > option evaluation is only for a sentence that argues whether an option is correct, acceptable or best. A bare verdict attached to an option in a checklist ("(B) day 47 — Incorrect.", "(D) cannot be determined — Vague.") is Reflection > meta-evaluation of a step > option (X). A sentence quoting an option's text is Restatement > rephrasing the prompt > option text. A sentence about what the question writer intended is Reasoning > speculation > intent of the question writer. Setting two options against each other is Reasoning > comparison > option vs option. The appearance of an option letter never by itself makes a sentence option evaluation.
- Reflection: emotion or impression is a feeling about the problem or the progress ("This is tricky.", "Nice."). A judgement about the correctness, completeness or consistency of a step, of the draft or of the output ("All steps check out.", "The draft matches the reasoning.", "Output matches.") is meta-evaluation of a step. Planning > announce output covers the go-ahead words and sentences that say the reply is now being written ("Proceed.", "Ready.", "Done — writing it out.", "I'll send exactly this text.") — never emotion.
- Conclusion: a sentence that states a settled result of the reasoning so far ("Therefore …", "So the value is not fixed.", "The problem is underdetermined.") is Conclusion > intermediate conclusion, not logical reasoning; the inference steps before it are Reasoning. Conclusion > final answer is only the statement of the answer at the very end of the trace (the last time it is given); every earlier statement of the answer, including "Answer:" lines and the answer letter inside a drafted reply, is intermediate conclusion. A bare "Answer:" line or a bare letter inside the draft takes the same label as the answer statement it belongs to.
- One-word answers: the one-word answer to a self-question ("Yes.", "No.", "Unlikely.") is Reasoning > logical reasoning, and the question takes the same leaf as its answer, so both are Reasoning > logical reasoning and fall into one run (with the Level 3 leaf algebra when the check is about the item's equations).
- "Wait" sentences (doubt marker): a sentence whose first word is "Wait" — "But wait", "Oh wait", "Okay, wait" included; leading list markers, markdown and parentheses ignored — is Planning > initiate verification or Planning > initiate backtracking with the Level 3 leaf Wait (doubt marker): initiate verification when it announces a re-check ("Wait, was the departure 9:00 or 9:30?" is Pl.iv.wdm), initiate backtracking when it abandons or reverses a line of reasoning ("Wait, working forwards from day 1 was the wrong idea." is Pl.ib.wdm). When such a sentence also carries content of its own — a recalled fact, a comparison, a calculation — it is a combined sentence with the doubt marker as the first code and that content as the second ("Wait, the classic lily-pad puzzle asks for half the lake, not a quarter." is Pl.iv.wdm+Kn.wk). Such a sentence always opens a block in the analysis, whatever precedes it.
- Labeling order, applied to every sentence in this sequence, first match wins: (1) a marker, heading or plan item → Planning; (2) an announcement that the reply is being written → Planning > announce output; (3) repeats earlier content → Restatement > rephrasing an earlier sentence; (4) repeats the question, an option or the format instruction → Restatement > rephrasing the prompt; (5) posits a case or an assumption → Assumption; (6) states a settled result → Conclusion; (7) judges the trace's own work → Reflection; (8) states a fact from outside the problem → Knowledge; (9) gives instances → Example; (10) otherwise Reasoning, with the finest leaf that fits and logical reasoning as the default — never option evaluation by default.
- Sentences are never re-split or merged: label each numbered sentence as it is, even a fragment, a heading, a number or a closing parenthesis.
- For information only (you do not output blocks): the analysis derives blocks from your labels. A block opens at the first sentence of a Planning node unless every sentence of that node is Planning > local plan, at a sentence carrying Assumption > branching (case split), and at a sentence carrying Conclusion > final answer. This is why the distinction between global plan, initiate verification, initiate backtracking, announce the conclusion, announce output on one side and local plan on the other matters.

## 4. Levels 2 and 3: the code table

One line per allowed path: `code — Level 1 > Level 2 [> Level 3] — gloss`. A path may stop at Level 2 (for example `Re.ca` when the calculation is not about the item's algebra). Level 1 alone is never a label.

Pl.gp — Planning > global plan — sets the overall direction or announces a major phase of the work
Pl.iv — Planning > initiate verification — announces a check of something already done
Pl.iv.wdm — Planning > initiate verification > Wait (doubt marker) — a sentence whose first word is "Wait" — "But wait" included — that announces a re-check
Pl.ib — Planning > initiate backtracking — announces abandoning or redoing an earlier path
Pl.ib.wdm — Planning > initiate backtracking > Wait (doubt marker) — the same marker when the sentence abandons or reverses a line of reasoning
Pl.lp — Planning > local plan — the next small step: a step label with a colon, a series item, a bullet label
Pl.atc — Planning > announce the conclusion — announces that the answer follows
Pl.ao — Planning > announce output — the sentence announces that the reply is being produced ("Writing the reply now.", "[Response] -> begin", "Go.", "Time to put this into words.")
Pl.un — Planning > unspecified — Planning that fits no other leaf
Re.ca — Reasoning > calculation — arithmetic or algebra on stated quantities
Re.ca.al — Reasoning > calculation > algebra — the bat/ball equations, inequality, or solution set
Re.lr — Reasoning > logical reasoning — a deduction from earlier sentences (including the one-word answer to a self-question)
Re.lr.al — Reasoning > logical reasoning > algebra — an inference about the equations or the solution set made without a computation
Re.cr — Reasoning > commonsense reasoning — an inference from everyday plausibility
Re.sp — Reasoning > speculation — a guess about something not derivable from the text
Re.sp.iot — Reasoning > speculation > intent of the question writer — what the writer of the question meant or wanted
Re.ds — Reasoning > defining symbols — introduces variables or notation
Re.ds.al — Reasoning > defining symbols > algebra — symbols for the quantities of the item
Re.ofe — Reasoning > observation from examples — a pattern read off listed cases
Re.co — Reasoning > comparison — the sentence sets two things side by side and states a difference or sameness (the prompt against the original riddle; one option against another). When the same sentence also states the original text from memory, it is a combined sentence, Reasoning > comparison + Knowledge > world knowledge
Re.co.pvo — Reasoning > comparison > prompt vs original text — this prompt against the original riddle
Re.co.ovo — Reasoning > comparison > option vs option — one option against another
Re.oe — Reasoning > option evaluation — the sentence judges whether one option is correct, acceptable or best. Its Level 3 leaf records the option
Re.oe.A — Reasoning > option evaluation > (A) — about option (A)
Re.oe.B — Reasoning > option evaluation > (B) — about option (B)
Re.oe.C — Reasoning > option evaluation > (C) — about option (C)
Re.oe.D — Reasoning > option evaluation > (D) — about option (D)
Re.oe.E — Reasoning > option evaluation > (E) — about option (E)
Re.oe.F — Reasoning > option evaluation > (F) — about option (F)
Re.hwa — Reasoning > hedge word analysis — the sentence interprets "most likely", "likely" or "probably". Its Level 3 leaf records which reading it adopts
Re.hwa.er — Reasoning > hedge word analysis > everyday reading — "the intended answer"
Re.hwa.mr — Reasoning > hedge word analysis > mathematical reading — "no value is more probable"
Re.hwa.un — Reasoning > hedge word analysis > undecided — weighs the readings of the hedge word without adopting one
Re.un — Reasoning > unspecified — Reasoning that fits no other leaf
Rf.meo — Reflection > meta-evaluation of a step — judges an earlier step or an option (fits, seems wrong, is clean)
Rf.meo.A — Reflection > meta-evaluation of a step > option (A) — about option (A)
Rf.meo.B — Reflection > meta-evaluation of a step > option (B) — about option (B)
Rf.meo.C — Reflection > meta-evaluation of a step > option (C) — about option (C)
Rf.meo.D — Reflection > meta-evaluation of a step > option (D) — about option (D)
Rf.meo.E — Reflection > meta-evaluation of a step > option (E) — about option (E)
Rf.meo.F — Reflection > meta-evaluation of a step > option (F) — about option (F)
Rf.eoi — Reflection > emotion or impression — a feeling or impression about the problem or the progress
Rf.rp — Reflection > rhetorical phrase — a phrase that carries no content of its own
Rf.fi — Reflection > filler — words that only fill space
Rf.aoa — Reflection > applicability of a knowledge item — judges whether a recalled fact applies here
Rf.un — Reflection > unspecified — Reflection that fits no other leaf
Kn.rot — Knowledge > rule or theorem — a general rule or theorem brought in from memory
Kn.cod — Knowledge > concept or definition — a definition or concept brought in from memory
Kn.cod.wp — Knowledge > concept or definition > well-posedness — the Hadamard conditions
Kn.cou — Knowledge > constant or unit — a constant, unit or conversion brought in from memory
Kn.wk — Knowledge > world knowledge — a fact about the world outside the prompt, true or not
Kn.wk.fpc — Knowledge > world knowledge > famous problem (CRT) — its name, standard text, standard answer
Kn.co — Knowledge > commonsense — an everyday fact everyone knows
Kn.sk — Knowledge > self-knowledge — the sentence states what the model is, what it must do because of what it is, or how it is evaluated ("as a language model I have to answer the text in front of me"; "assistants are graded on following the instructions exactly")
Kn.sk.ro — Knowledge > self-knowledge > role — what the model is or must do because of what it is
Kn.sk.ec — Knowledge > self-knowledge > evaluation context — how the model is evaluated
Kn.un — Knowledge > unspecified — Knowledge that fits no other leaf
Rs.rtp — Restatement > rephrasing the prompt — repeats or paraphrases the prompt with nothing new added
Rs.rtp.qt — Restatement > rephrasing the prompt > question text — the question
Rs.rtp.ot — Restatement > rephrasing the prompt > option text — an option quoted or paraphrased
Rs.rtp.afi — Restatement > rephrasing the prompt > answer-format instruction — the instruction on the reply format
Rs.rae — Restatement > rephrasing an earlier sentence — repeats or paraphrases an earlier sentence of the trace
Rs.un — Restatement > unspecified — Restatement that fits no other leaf
As.aam — Assumption > assuming a missing premise by common practice — supplies a premise the prompt lacks because it is the usual one
As.aam.mo — Assumption > assuming a missing premise by common practice > "$1.00 more" — the premise of the classic riddle that this prompt omits
As.aau — Assumption > assuming an uncertain fact — takes an uncertain fact as given for what follows
As.bcs — Assumption > branching (case split) — opens a case ('If X, then ...') that later sentences work inside
As.bcs.al — Assumption > branching (case split) > algebra — a case on a value
As.pbc — Assumption > proof by contradiction — assumes the opposite in order to refute it
As.un — Assumption > unspecified — Assumption that fits no other leaf
Ex.pib — Example > pattern induction by enumeration — lists cases in order to find a pattern
Ex.nel — Example > non-exhaustive listing — lists some instances without claiming completeness
Ex.nel.al — Example > non-exhaustive listing > algebra — listed value pairs for the item
Ex.re — Example > rhetorical example — an example given for effect, not for the solution
Ex.un — Example > unspecified — Example that fits no other leaf
Co.ic — Conclusion > intermediate conclusion — answers the question in substance or names an option, before the final answer
Co.fa — Conclusion > final answer — the final answer or its announcement in the answer format

## 5. Input format

After this prompt comes the whole trace, one line per sentence, in order:

```
s0: <text of sentence 0>
s1: <text of sentence 1>
...
```

The mark ⏎ inside a text stands for a line break of the original trace (a sentence may begin with one or more of them); leading spaces after a mark are part of the original indentation. Labels depend on context: read the whole trace before labeling.

## 6. Output format

Plain text only. One line per run of consecutive sentences that carry the same label:

- `<first>-<last> <code>` for a run of two or more sentences (for example `15-22 Re.ca.al`), `<first> <code>` for a single sentence (`23 Co.ic`);
- a combined sentence on its own line as `<index> <codeA>+<codeB>` (`12 Re.co.pvo+Kn.wk`);
- runs in increasing order, covering every index from 0 to the last sentence exactly once, no gaps, no overlaps;
- codes exactly as in Section 4; no prose, no blank lines, no code fences, no headings, nothing before the first line or after the last.

## 7. Worked examples

Each example shows a short trace on a different problem, the numbered input and the exact expected output. The Level 3 leaves of Section 4 belong to the bat-and-ball item, so these examples stop at Level 2 where a leaf would be item-specific; on a real trace, use the Level 3 leaf whenever the sentence fits it.

### Example 1 (lily pads): a numbered heading, a nested item, an intermediate conclusion, a verification and its judgement

Problem: A patch of lily pads doubles in size every day and covers the whole lake on day 48. On which day did it cover half the lake?

Input:

```
s0: 1.
s1: **Set up the rule:**
s2: - Given:
s3: the patch doubles every day and covers the lake on day 48.
s4: Doubling every day means the patch on day 47 was half of the patch on day 48.
s5: So half the lake was covered on day 47.
s6: Let me double-check by going forwards instead:
s7: Half the lake on day 47, doubled once, is the whole lake on day 48.
s8: That checks out.
```

Expected output:

```
0-1 Pl.gp
2 Pl.lp
3 Rs.rtp.qt
4 Re.lr
5 Co.ic
6 Pl.iv
7 Re.ca
8 Rf.meo
```

### Example 2 (train): a branching sentence, a self-question and its one-word answer inside one Reasoning run, a combined sentence, an intermediate and a final conclusion

Problem: A train leaves at 9:00 and travels at 60 km per hour. When does it reach a station 150 km away?

Input:

```
s0: Compute the travel time first.
s1: If the train keeps exactly 60 km per hour,
s2: then time = distance / speed = 150 / 60 = 2.5 hours.
s3: Is 2.5 hours the same as 2 hours and 30 minutes?
s4: Yes.
s5: So the train arrives at 11:30, taking the usual reading that it never stops on the way.
s6: Wait, was the departure 9:00 or 9:30?
s7: The prompt says 9:00.
s8: Final answer: 11:30.
```

Expected output:

```
0 Pl.lp
1 As.bcs
2 Re.ca
3-4 Re.lr
5 Co.ic+As.aam
6 Pl.iv.wdm
7 Rs.rtp.qt
8 Co.fa
```

### Example 3 (lily pads with options): Knowledge, an Example, an argued option evaluation, verdict tags, a drafted reply that restates an earlier equation, the final answer, announce output

Problem: Same puzzle, with options (A) day 24, (B) day 47, (C) cannot be determined, (D) none of the above.

Input:

```
s0: This is the well-known lily-pad puzzle from the cognitive reflection test.
s1: The intuitive answer is day 24, but that ignores the doubling.
s2: For instance, a patch of 1 unit on day 1 is 2 units on day 2 and 4 units on day 3.
s3: Halving the full lake once: 48 - 1 = 47.
s4: Option (B) is right because it is the only option equal to 47.
s5: (A) day 24 — Incorrect.
s6: (C) cannot be determined — Incorrect.
s7: Draft reply:
s8: The lake is half covered one day before it is full: 48 - 1 = 47.
s9: Answer: B.
s10: Writing it out now.
```

Expected output:

```
0 Kn.wk
1 Re.lr
2 Ex.nel
3 Re.ca
4 Re.oe.B
5 Rf.meo.A
6 Rf.meo.C
7 Pl.gp
8 Rs.rae
9 Co.fa
10 Pl.ao
```

