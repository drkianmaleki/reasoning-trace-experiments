# Labeling scheme (ReasoningFlow-based) — 2026-09-14 v3

File: 2026-09-14_labeling_scheme_v3.md (local version 3 = chat version 3 of the 2026-09-14 evening chat). Supersedes 2026-09-14_labeling_scheme_v2.md (→ archive/). Status: content release, confirmed by Kian on 2026-09-14. No label, boundary or count changed; the additions are notation (Section 0d) and the definitions of the resampling design agreed with Kian on 2026-09-14 (Section 0e), with Section 12 items 9 and 12–16 decided.

Status: WORKING DOCUMENT, versioned (Option A, 2026-09-14): each confirmed revision is a new file with the next consecutive local version number; superseded versions move to archive/. Rules and labels in this version are those Kian confirmed in v1 on 2026-09-14; the v2 corrections were bookkeeping; the v3 additions (Sections 0d, 0e, 12) were confirmed by Kian on 2026-09-14. Claude drafts, Kian decides; nothing here is frozen except where marked.

Provenance of labels: every label, boundary and count in this document is Claude's provisional labeling of both traces, complete at the sentence level, for Kian's review of the structure. Kian has decided (2026-09-14) not to blind-label; he checks the outputs for sense instead. Nothing here is a finding.

Numbering: all sentence indices in this document follow the v2 listing (`2026-09-14_source_traces_sentences_v1.md`), which uses the splitting rule of Section 0c, approved by Kian on 2026-09-14. The complete sentence-by-sentence labeling with nodes and blocks is in `2026-09-14_source_traces_labeled_v1.md`.

## 0. Purpose and working assumption

Purpose: a labeling scheme for reasoning traces that (a) reuses the best-validated published schema so results are comparable, (b) is expandable without ambiguity, and (c) carries the item-specific distinctions that the published schemas lack, as leaves of the same tree.

Working assumption A1 (Kian, 2026-09-13): the narrated reasoning and the actual reasoning are close at the coarse level and may diverge at the fine level. Consequences: Level 1 and 2 labels are treated as approximate descriptions of the process; no ordering is imposed inside a sentence, because the order in which the narration mentions two functions is not evidence about the process.

## 0a. Terms

Text units
- Trace: the full thinking text of one generation (the C-trace, the E-trace).
- Sentence: one unit of the splitter (Section 0c), written s0, s1, … Sentences are never re-split by a labeler. The sentence is the unit that receives labels.
- Interval notation: [s10, s13] = s10, s11, s12, s13 (both ends included); [s10, s13) = s10, s11, s12 (right end excluded). So [s10, s12] = [s10, s13). A single sentence is [s10, s10].
- Node: a maximal run of consecutive sentences that carry the same label at a given level. A Level 1 node is a maximal run with the same Level 1 label; inside it, Level 2 nodes are maximal runs with the same Level 2 label; a Level 3 node is a maximal run inside a Level 2 node with the same Level 3 label. A node at Level n+1 is a sub-node of the Level n node that contains it. A node is written as its label and interval, e.g. Planning [s10, s13]. A block boundary also ends a node (Section 6), so no node crosses two blocks.
- Abbreviations for the Level 1 labels, used in node names and tables: Pl Planning, Re Reasoning, Rf Reflection, Kn Knowledge, Rs Restatement, As Assumption, Ex Example, Co Conclusion. A combined sentence is written with both, in brackets: [Pl+Rs].
- Node name: X_m^k(n), read as follows. X is the abbreviation. The subscript m is the number of the block the node sits in. The superscript k is a running index used only when the same Level 1 label forms more than one node inside block m; it is omitted otherwise. The number in parentheses, n, is the node's sentence count, omitted when it is 1. So Re₃²(2) is the second Reasoning node of block 3 and has two sentences; Pl₀(3) is the only Planning node of block 0 and has three sentences. Parentheses always mean sentence count and never identify a node; identification is by the subscript and superscript. Example from the C-trace: block 0 = [s0, s7] = Pl₀(3) → Rs₀(5), i.e. s0–s2 are Planning and s3–s7 are Restatement; block 3 = [s15, s22] = As₃ → Re₃¹ → Pl₃¹ → Re₃²(2) → Pl₃² → Re₃³(2).
- Opener: a sentence that satisfies at least one of the opener rules R1–R3 in Section 6. The rules refer only to the sentence's own labels, so "opener" is defined without reference to blocks.
- Block: the run of sentences from an opener up to, but not including, the next opener; the last block runs to the end of the trace. Written [s_open, s_next_open). Blocks are defined from openers, openers from labels; there is no circle.
- Combined sentence: a sentence carrying two labels whose Level 1 parts differ.
- Residue: sentences whose finest label is `unspecified`.

Label units (the taxonomy is a tree)
- Level n: depth in the tree. Level 1 is the coarsest. Levels are numbered so that Level 3, Level 4, … can be added below without renaming anything.
- Parent / child: a Level n label is the parent of the Level n+1 labels under it; those are its children.
- Leaf: a label with no children; the finest label in use on that branch. `unspecified` is always a leaf.
- Label: the path from Level 1 down to the finest level in use, written with ">", e.g. Reasoning > option evaluation > (C).

Worked example of nodes (Kian, 2026-09-14), given these labels:

- s10 = Planning > global plan
- s11 = Planning > global plan
- s12 = Planning > initiate verification
- s13 = Planning > initiate verification
- s14 = Reasoning > calculation

Then:

- [s10, s13] is one Level 1 node (Planning).
- It has two Level 2 sub-nodes: [s10, s11] (global plan) and [s12, s13] (initiate verification).
- [s14, s14] begins a new Level 1 node (Reasoning).

The same, from the E-trace (Claude's provisional labels, 2026-09-09 numbering):

- s1 "1." + s2 "**Analyze the User Input:**" = Planning > global plan
- s3 "- Question:" = Planning > local plan
- s4, s5, s6 (the quoted question) = Restatement > rephrasing the prompt > question text
- s7 "- Options:" = Planning > local plan
- s8 (the quoted options) = Restatement > rephrasing the prompt > option text

Then:

- Level 1 nodes: Planning [s1, s3], Restatement [s4, s6], Planning [s7, s7], Restatement [s8, s8].
- Level 2 sub-nodes of Planning [s1, s3]: [s1, s2] (global plan), [s3, s3] (local plan).

Rule for combined sentences in node formation: a combined sentence is its own node at Level 1 (it breaks the runs on both sides) and carries both labels. It is flagged (Section 1).

## 0b. Reference conventions

- C-trace = record with `condition` = eval0_multi0 and `sample` = 2 in `sweep_items_batball_2026-08-19_1623.jsonl` (row 4 of that condition; resampling IDs carry c004; source_id s0819_eval0multi0_004). Final answer C. Uploaded to this chat on 2026-09-09; the archived copy lives in the reasoning-trace-experiments repository under archive/decided-mid-thought/ (exact subfolder not recorded in this document).
- E-trace = record with `condition` = eval0_multi0 and `sample` = 40 in the same file (row 36; IDs carry e036; source_id s0819_eval0multi0_036). Final answer E.
- Current numbering: `2026-09-14_source_traces_sentences_v1.md` (the v2 listing; Section 0c). It prints the old index next to every sentence, so anything written under the 2026-09-09 numbering can be translated.
- Archive numbering: `source_traces_c004_e036_sentence_indexed_2026-09-09.md`, verified against the prefix hashes of `resample_cuts_2026-08-25_1503.jsonl` through old s69 (C) and old s65 (E). All old boundaries are preserved in v2.
- Complete labels: `2026-09-14_source_traces_labeled_v1.md` (Claude's provisional labels, every sentence of both traces, with Level 1 node ids and block boundaries).

"C s60" means: C-trace, sentence 60, verbatim text as in the listing named in the same sentence or section.

## 0c. Sentence splitting rule (approved by Kian, 2026-09-14)

The reconstructed run splitter: a sentence ends after `.` `?` `!` `:` when the next character is whitespace or the end of the text, and at a line break.

Added rule (Kian, 2026-09-14: the end of each math equation counts as a period), in a form a script can apply:
- (a) A comma that closes a segment containing a relation symbol (`=`, `<`, `>`, `≤`, `≥`, `≠`; not the arrows `->`, `=>`, `>=`, `<=`) acts as a period. Segments are delimited by `, ; : ( )` and the sentence start. Commas inside parentheses do not split.
- (b) An opening parenthesis that follows a segment containing a relation symbol starts a new sentence if the parenthesis opens a capitalized clause ("(Wait, …", "(Identity)"). A lowercase clause ("(where $B$ is bat …") stays attached.

Measured effect: C-trace 366 → 375 sentences (+9), E-trace 247 → 254 (+7). Every old boundary is kept, so every archived cut still ends exactly at a sentence boundary and no archived data is invalidated; only the numbering changes. Old C s60, the registered s*, is C s67 under the current numbering, and the old cuts map as listed in the v2 file (old cut-15 → [s0, s16], …, old cut-69 → [s0, s76]; old E cut-60 → [s0, s66], …). Kian accepted the redefinition of s* under the new numbering on 2026-09-14 because the new scheme contains the old finding; the glossary entry for s* is to be updated accordingly.

Why the rule is worth its cost: the sentence "If Ball = $0.05, then Bat = 1.10 - 0.05 = $1.05." was one combined sentence (Assumption + Reasoning); it is now "If Ball = $0.05," (Assumption > branching) and "then Bat = 1.10 - 0.05 = $1.05." (Reasoning > calculation). E's three-function sentence "Ball = $x$, Bat = $x + 1.00$ (Wait, …)" becomes three sentences with at most two labels each.

Cut notation going forward: cut-k = [s0, s_k), exactly k sentences, so cut-0 = [s0, s0) is the empty prefix with no exception. The old run's cut-k was [s0, s_k] with k+1 sentences.

## 0d. Notation for probabilities over node sequences (revised 2026-09-14, v6)

The quantities this project measures are probabilities over what comes next in a trace and over the final answer. This version replaces the "X(n) = n-th occurrence" notation of v4–v5, because parentheses now mean sentence counts (Section 0a); a node is identified by its block-indexed name instead.

Objects
- X, Y, W stand for labels at any level: Pl, Pl > initiate verification, Re > option evaluation > (C), and so on. Bare labels are used for patterns and for "next = …".
- X_m^k is a specific node of a source trace, named as in Section 0a (block m, k-th node of that label in the block). In a probability the sentence count is dropped: write Pl₃¹, not Pl₃¹(1).
- cut(X_m^k) is the prefix that ends with the last sentence of node X_m^k, written as a half-open interval: cut(Pl₃¹) = [s0, s18) in the C-trace, i.e. sentences s0 to s17. When a probability is conditioned on a node, the cut is at the end of that node.
- -> means "immediately followed by" (adjacent nodes). --> means "followed later by": W --> X says that W occurs and X occurs after it, with any number of nodes in between, and those nodes do not matter. Both arrows are typed on a plain keyboard; → and ⇢ are their rendered forms in tables and figures and mean exactly the same thing (the ⇝ of v2 is retired). --> includes the adjacent case: zero or more nodes between, so -> is a special case of --> (decided by Kian, 2026-09-14; Section 12, item 12). The reason: the history conditions of Section 0e pool "W somewhere earlier than X", and the inclusive form names that set directly.
- cut(B_m) is the prefix that ends with the last sentence of block B_m — the same convention as for nodes: a cut named by an object sits at the end of that object. Blocks are numbered from 0, as the block subscripts of the node names already are (Pl₀ sits in B_0), so cut(B_0) = [s0, s8) in the C-trace and cut(B_45) is the whole C-trace. The empty prefix keeps its name, cut-0.
- Pattern brackets ⟨ ⟩ are kept (Kian, 2026-09-14): they are the one non-keyboard symbol of the notation and are copied from this document when typed.
- ⟨ W → X ⟩ is a pattern: the sequence occurs somewhere in the text under consideration. Angle brackets, so that [ ] stays reserved for intervals.
- The population is a subscript when not obvious: P_k for continuations resampled from a stated cut; P_corpus for the sweep traces read as they are; P_source for the two source traces themselves (a count, not a resampling).

Quantities
- Transition from a node (a resampling quantity): P(next = Y | X_m^k) is the fraction of continuations from cut(X_m^k) whose first new node carries label Y.
- Transition with history: P(next = Y | W_m^j → X_m^k) is the same quantity when the two nodes before the cut are W_m^j then X_m^k. It is what the Markov-order test compares against P(next = Y | X_m^k).
- Final answer given a node: P(answer = C | X_m^k) is the fraction of continuations from cut(X_m^k) that end in C. This is the old P(C | cut-k) written with a node name.
- Final answer given a pattern: P(answer = C | ⟨ W → X ⟩) is the fraction of continuations (from a stated cut) in which the pattern occurs and which end in C. Patterns use bare labels; node names do not apply inside ⟨ ⟩ because each continuation has its own nodes.
- Corpus transition: P_corpus(Y | X) is the count-based probability that a node labeled X is followed by a node labeled Y across the sweep traces, with no position and no resampling. Comparing it with P(next = Y | X_m^k) across positions is the observational-versus-resampled test.
- Source count: P_source(next = Y | X_m^k) is 1 for the label that actually follows in the source trace and 0 otherwise; it is the trace's own path, useful as the reference row.

Kian's four examples (2026-09-14) in this notation, using real nodes of the C-trace
- P(Assumption | Planning(1)) becomes P(next = As | Pl₀). Pl₀(3) = [s0, s2] is the opening heading node; cut(Pl₀) = [s0, s3). In the source the next node is Rs₀(5), so P_source(next = Rs | Pl₀) = 1; the resampled value is what the experiment measures.
- P(Planning > initiate verification | Planning > global plan (2)) becomes P(next = Pl > initiate verification | Pl₂). Pl₂(2) = [s13, s14] is the heading "3. Evaluate the Constraints & Ambiguity"; in the source the next node is As₃.
- P(Reasoning | Planning > initiate verification (1) | Planning > global plan (2)) is a history condition; with real nodes: P(next = Re | Re₃² → Pl₃²), the cut sitting after Pl₃² ("Is the sum $1.10?"), which itself follows Re₃²(2). In the source the next node is Re₃³(2).
- P(C | [Planning > initiate verification (1) | Planning > global plan (2)]) becomes P_k(answer = C | ⟨ Pl > global plan → Pl > initiate verification ⟩): continuations from cut-k in which a global plan is immediately followed by an initiate-verification node, anywhere, end in C with this probability. If the intended condition is that two specific source nodes precede the cut, it is the history form above.

Open: whether "→" requires adjacency at Level 1 only or at the finest level written; proposal: at the level of the labels written.

## 0e. Block-level quantities for the resampling run (added 2026-09-14, v3; agreed with Kian in the evening chat of 2026-09-14)

Estimates
- Every probability below is estimated from the n continuations of one cut: P̂ = (number of continuations whose final reply scores as the stated answer) / n, with n the attempted count. A continuation that resolves to no letter (the "?" of the archived run, mostly continuations that hit the 16,000-token cap) stays in the denominator, as in the submitted study: the denominator is always n, and unfinished continuations are data, not discards (decided by Kian, 2026-09-14; Section 12, item 15). The count of "?" is reported for every cut, since it is informative in itself (long, C-style continuations are the ones that hit the cap). Example from the archived run: at C-trace old cut-15 the 25 continuations were 9 C, 7 E, 1 B and 8 "?", so P̂(C) = 9/25 = 0.36 (dropping the "?" would give 9/17 = 0.53); at old cut-63 they were 23 C and 2 "?", so P̂(C) = 0.92 and the stopping rule does not fire there. Estimates are reported with a 95% interval (Wilson or Clopper–Pearson); no estimate is written as a bare 1 or 0.

Mediation quantities (the answer tree)
- a_T is the source trace's own final answer: C for the C-trace, E for the E-trace.
- P_m := P(answer = a_T | cut(B_m)), the fraction of continuations from the end of block B_m that end in a_T. The condition is the whole prefix through B_m, never the block alone; that is the anti-Markov point written into the notation (Kian, 2026-09-14). P(a_T | cut-0) is the no-thinking baseline (0.12 for C, 0.80 for E in the submitted study).
- Δ_m := P_m − P_{m−1} for m ≥ 1, and Δ_0 := P_0 − P(a_T | cut-0): the signed shift of the answer across block B_m. Negative values are reported as they are; absolute values are not used (Kian, 2026-09-14).
- Trivial block: B_m is trivial when P_m = P_{m−1}, i.e. Δ_m = 0 (Kian's definition, 2026-09-14). The definition applies to the estimates. A trivial block is trivial for the answer only; it remains active in the transition tree (Section 0d).
- Stopping rule (Kian, 2026-09-14): cuts are resampled in order m = 0, 1, 2, …; at the first m with P̂_m = 1 (all n continuations end in a_T) set M := m and stop. No cut with m > M is resampled, and every block with m > M is trivial by this assumption, not by measurement; the pre-registration states the rule as an assumption. The submitted run shows why the later cuts add little: the C-arm read 25/25 at old cut-62 and then 0.92, 0.84, 0.96, 1.00, 0.92 at the following cuts. Two facts about the stop: with n = 25, P̂ = 1 bounds the true P only at 0.887 (one-sided 95%), and 25/25 is observed with probability 0.28 when the true P is 0.95 and 0.07 when it is 0.90; with n = 50 the bound is 0.942. Consequence, accepted by Kian (2026-09-14; Section 12, item 13): after M there are no resampled transitions, so the transition tree of the tail rests on P_corpus and P_source alone; saving the E-arm's resampling is acceptable, since the submitted study learned nothing new from the E resampling and its results concern the C-trace. With n = 40, the candidate for the pre-registration (Kian, 2026-09-14; budget raised to about $100), P̂ = 1 bounds the true P at 0.928, and 40/40 is observed with probability 0.13 when the true P is 0.95 and 0.015 when it is 0.90.

Localization, measured in tokens
- Tk(x) := the number of tokens in x, where x is a block, a node, a cluster of blocks or a chain of nodes (Kian's definition, 2026-09-14). Tokens are the studied model's own (the tokenizer of Qwen 3.6-27B): the one unit that does not depend on this scheme's conventions (splitter, labels, opener rules). Tk is computed by tokenizing the whole trace once and assigning each token to the block or node that contains the token's first character. A block's span runs from the first character of its first sentence to the character before the first character of the next block's first sentence (the last block runs to the end of the trace), so the spans partition the trace and Σ_m Tk(B_m) = Tk(trace). Tokenizing sentences one at a time is not allowed: token boundaries at the seams differ from those of the whole text.
- What stage one reports, all descriptive, no thresholds (Kian, 2026-09-14): P_m and Δ_m for every resampled block, with intervals; the block B_top with the largest Δ_m; Tk(B_top) next to Tk(trace); the gap Δ_(1) − Δ_(2) between the largest and the second-largest Δ_m; the plot of Δ_m against m and of P_m against m. "Localized" and "diffuse" are readings of these numbers, not verdicts. Precision at the candidate n = 40: the standard error of P̂ at P = 0.5 is 0.079, so shifts below about 0.1 are within noise; n is fixed in the pre-registration. The submitted study's Δ_jump = 0.4 is the cautionary case: the threshold turned "+0.28" into "fails" and was arbitrary among its neighbours.

Two-stage design (closes Section 12, item 9)
- Stage one: resample at every block-end cut, m = 0, 1, …, under the stopping rule. This is the registered run. Blocks are always the first unit.
- Stage two, optional: node-level cuts inside the single block with the largest Δ_m of stage one (Kian: "only the block with the largest shift"), decided after reading the stage-one plot and subject to time and budget; if it happens it gets its own registration. Near-tie rule (decided by Kian, 2026-09-14; Section 12, item 14): the gap Δ_(1) − Δ_(2) is reported with its 95% interval; if the interval excludes zero, stage two targets the top block alone; otherwise it targets both blocks; the reason is recorded in stage two's registration. At n = 40 the standard error of the gap is up to about 0.16, so gaps below roughly 0.3 count as ties. A fraction of the average Δ_m was considered and rejected as the reference: the Δ_m telescope to P_M − P(a_T | cut-0), so their average is about 0.1 for the C-trace and a tenth of it lies far below the noise of a single Δ_m.
- Cluster of blocks: several blocks read as one unit when the shift is spread over neighbours; whether a cluster must be contiguous is left open until stage one is read.

History conditions with --> (the transition tree)
- P(next = Y | W_m^j --> X_m^k) is the fraction of continuations from cut(X_m^k) whose first new node carries label Y, recorded for a cut whose prefix contains node W_m^j somewhere before X_m^k. With node names the condition picks out one cut of one source trace. With bare labels, P(next = Y | W --> X), it pools every cut that ends in an X node with a W node earlier in the prefix; the pooled form is what the Markov comparison uses, against P(next = Y | X) pooled without regard to W, and against P_corpus(Y | X).
- Order comparison (Kian, 2026-09-14): P(next = Y | W --> X) against P(next = Y | X --> W), the cut sitting at the end of the later of the two nodes in each case. A difference says that the order in which the two moves occurred changes what follows.
- Fragmentation: transitions are reported at Level 1 by default (eight labels); finer levels only where the mass concentrates (Kian, 2026-09-14).
- The transition tree and the mediation tree are built over the same spine of blocks and are complementary: after M the mediation tree is flat while the transition tree keeps branching. The submitted study already shows the shape: 84.6% of the C-trace's characters come after s*, where P(C) ≥ 0.88 and never falls.

## 1. Unit of labeling

- The sentence is the unit that receives labels. Nodes and blocks are derived from sentence labels; they are never labeled directly.
- A sentence may carry MORE THAN ONE label (a combined sentence). Each label is a full path; labels in a set are unordered. Cap: two labels per sentence; a third is flagged for review.
- Combined sentences are ALLOWED BUT FLAGGED (marked * in the labeled listing). Observed in Claude's full labeling: 9 of 375 sentences in the C-trace and 5 of 254 in the E-trace (Section 1b). Whether to keep them as they are, restrict them to listed pairs, or drop them is Kian's decision after review (Section 12, item 2).

### 1b. Combined sentences, explained

A combined sentence is one sentence that does two jobs at once, so two applicability tests pass. Three kinds appear in the two traces, and each has a different remedy if Kian wants fewer of them.

Kind 1, a plan attached to a quote: "Check the text provided in the prompt again carefully: 'A bat and a ball cost $1.10 in total.'" (C s43) is Planning > initiate verification and Restatement > rephrasing the prompt in one sentence, because the model announces the check and begins quoting in the same breath. C s114, C s227, E s193 are the same kind. Remedy if unwanted: the splitter could break the sentence at the opening quotation mark; then the plan and the quote become two sentences with one label each, as the equation rule did for algebra.

Kind 2, a plan phrased as a speculation: "Alternative interpretation check: Did the user intend to write the standard riddle and just forgot the '1.00 more'?" (C s160) announces a check and states the hypothesis being checked. C s291 and C s295 are similar. Remedy if unwanted: a convention that a question which opens a check is Planning only, with its content labeled on the answer that follows.

Kind 3, a true double function that no splitting removes: "However, in the context of riddles, this option acknowledges the likely intent of the user … while acknowledging the missing constraint." (C s67, the old s*) both interprets the hedge word and judges option B. E s18 ("Bat = $x + 1.00$") both calculates and silently assumes the missing premise; E s46 both evaluates option C and reads its hedge mathematically. These are the interesting ones: they are the sentences where two moves coincide, and dropping double labels would hide exactly that.

Consequences of keeping them: a combined sentence is a node by itself, so it breaks runs on both sides and can open a block when one of its labels is a non-local Planning leaf (C-B07, C-B12, C-B19, C-B29, E-B03, E-B26 open on combined sentences). Agreement with a judge is measured per label (Section 1a). In transition counts a combined sentence contributes to both rows.

What the numbers say so far: 14 combined sentences in 629, about 2%. Kind 1 (splittable), 5: C s43, C s114, C s227, E s58, E s193. Kind 2 (conventional), 4: C s160, C s291, C s295, E s19. Kind 3 (real), 5: C s67, C s75, C s111, E s18, E s46. Claude's labels, unverified.

### 1a. Agreement metrics, explained

Agreement rate: the share of sentences where two labelers gave the same label. Its weakness is chance: with one dominant label (Reasoning will be common), two labelers agree often by accident.

Cohen's kappa (κ): the agreement rate corrected for chance. κ = (observed agreement − agreement expected by chance) / (1 − agreement expected by chance), where the chance term is computed from how often each labeler uses each label. κ = 1 is perfect agreement, κ = 0 is chance level, negative is worse than chance. Rule of thumb: above 0.8 excellent, 0.6–0.8 good. Krippendorff's alpha (α) is the generalization to more than two labelers and missing data; ReasoningFlow reports α, and the two are comparable in scale.

Why kappa does not apply to combined sentences directly: kappa assumes each labeler gives one label per sentence, so "same or different" is a yes/no question. When a sentence carries a SET of labels, two labelers can agree partially (both say Reasoning, one adds Reflection). Two standard ways around it:
- Per-label yes/no: for each label X separately, ask "does this sentence carry X?" (yes/no) and compute kappa on those yes/no decisions. Report one kappa per label, then their average. This is the usual practice for multi-label annotation.
- Jaccard overlap: for each sentence, |A ∩ B| / |A ∪ B|, the number of shared labels divided by the number of labels either labeler used. Example: Kian {Reasoning, Reflection}, judge {Reasoning} → 1/2 = 0.5; both {Reasoning} → 1. Average over sentences. Simple to read, but not chance-corrected.
We report both. (A chance-corrected set-valued measure exists, Krippendorff's α with the MASI distance; to be verified before use.)

## 2. Level 1 — what the sentence is doing

Source: Lee et al., "ReasoningFlow: Discourse Structures for Understanding LLM Reasoning Traces", arXiv 2606.05402 (June 2026), Table 3. One label renamed (Knowledge).

1. Planning — introduces what the following sentences will do (global direction, a verification, an alternative path, the next step, or the announcement of the answer).
2. Reasoning — derives something from earlier sentences: deduction, induction, abduction, calculation, comparison. Adds new content that depends on what came before.
3. Reflection — expresses an opinion, judgment or feeling about earlier sentences or about the reasoner itself. Test: the sentence can be removed and the reasoning is still logically complete.
4. Knowledge — content brought in from outside the prompt and not derived from earlier sentences, whether or not it is true. ReasoningFlow calls this label Fact; renamed because "fact" asserts truth and recalled knowledge can be wrong (Kian, 2026-09-14). Mapping to ReasoningFlow is one-to-one, so comparability is kept. Alternative name considered: Recall. Precedent check (item 3): Bloom's original taxonomy (1956) called its first level Knowledge, and the 2001 revision renamed it Remember; Thought Anchors uses "fact retrieval", Venhoff et al. "Knowledge Augmentation", and Psyche uses "Analogy Recall" only for one specific move. No LLM-trace scheme uses Recall as a top-level label. Knowledge has the strongest precedent and is kept.
5. Restatement — copies or paraphrases the prompt or an earlier sentence and adds nothing new. Test: the content is entailed by its source.
6. Assumption — a statement marked as not necessarily true, used as a premise for what follows. It opens a scope: later sentences depend on it.
7. Example — a specific instance illustrating a general point. Test: it does not itself solve the problem; if it does, it is Reasoning.
8. Conclusion — an asserted answer to the question, intermediate or final.

Context (the prompt itself) is ReasoningFlow's ninth label. It is not model output and is not labeled here.

Frozen: yes, as a set of eight.

## 3. Level 2 — which kind, nested under Level 1

Two kinds of Level 2 leaves live side by side: the general leaves taken from ReasoningFlow Table 3, and item-specific leaves added for this item, marked [item]. Item-specific leaves are children of the frozen Level 1 labels, so Level 1 stays comparable; Section 5 gives the mapping used when our labels are compared with ReasoningFlow's. `unspecified` under each Level 1 label is ours.

- Planning > global plan · initiate verification · initiate backtracking · local plan · announce the conclusion · announce output [item; 16 sentences in the E-trace, none in the C-trace] · unspecified
- Reasoning > calculation · logical reasoning · commonsense reasoning · speculation · defining symbols · observation from examples · comparison [item] · option evaluation [item] · hedge word analysis [item] · unspecified
- Reflection > meta-evaluation of a step · emotion or impression · rhetorical phrase · filler · applicability of a knowledge item · unspecified
- Knowledge > rule or theorem · concept or definition · constant or unit · world knowledge · commonsense · self-knowledge [item] · unspecified (ReasoningFlow's "factual knowledge" is renamed "world knowledge")
- Restatement > rephrasing the prompt · rephrasing an earlier sentence · unspecified
- Assumption > assuming a missing premise by common practice · assuming an uncertain fact · branching (case split) · proof by contradiction · unspecified
- Example > pattern induction by enumeration · non-exhaustive listing · rhetorical example · unspecified
- Conclusion > intermediate conclusion · final answer

Definitions of the item-specific Level 2 leaves:
- Reasoning > comparison: the sentence sets two things side by side and states a difference or sameness (the prompt against the original riddle; one option against another). When the same sentence also states the original text from memory, it is a combined sentence, Reasoning > comparison + Knowledge > world knowledge (Kian's "Reasoning + Knowledge > comparison").
- Reasoning > option evaluation: the sentence judges whether one option is correct, acceptable or best. Its Level 3 leaf records the option.
- Reasoning > hedge word analysis: the sentence interprets "most likely", "likely" or "probably". Its Level 3 leaf records which reading it adopts; these leaves are the two readings of direction (1/3) of the research plan.
- Knowledge > self-knowledge: the sentence states what the model is, what it must do because of what it is, or how it is evaluated ("as an AI, I must address the prompt as written"; "LLMs are evaluated on their ability to follow instructions"). Decided by Kian 2026-09-14 (item 4) in place of the earlier Reflection > self-role identification.
- Planning > announce output: the sentence announces that the reply is being produced ("Output Generation.", "[Output] -> Proceeds", "Ready.", "I'll write it out clearly."). Observed 16 times in the E-trace tail, never in the C-trace.

Frozen: no. Open at the leaf level, and open to Level 3 below.

## 3a. Level 3 — item-specific leaves under Level 2

Level 3 exists only where a Level 2 leaf needs an item-specific distinction. A Level 2 leaf without children is still a leaf.

- Reasoning > calculation > algebra (the bat/ball equations, inequality, or solution set)
- Reasoning > defining symbols > algebra
- Reasoning > comparison > prompt vs original text · option vs option
- Reasoning > option evaluation > (A) · (B) · (C) · (D) · (E) · (F)
- Reasoning > hedge word analysis > everyday reading ("the intended answer") · mathematical reading ("no value is more probable") · undecided
- Reasoning > speculation > intent of the question writer
- Knowledge > world knowledge > famous problem (CRT: its name, standard text, standard answer)
- Knowledge > concept or definition > well-posedness (the Hadamard conditions; this is where the old "not well posed" topic lives, not as a label of its own)
- Knowledge > self-knowledge > role · evaluation context
- Assumption > assuming a missing premise by common practice > "$1.00 more"
- Assumption > branching (case split) > algebra (a case on a value)
- Reflection > meta-evaluation of a step > option (A) · … · option (F)
- Example > non-exhaustive listing > algebra
- Restatement > rephrasing the prompt > question text · option text · answer-format instruction

Expansion at Level 3 follows Section 9.

## 4. Applicability tests (no order among them)

Yes/no tests that decide whether a Level 1 label APPLIES to a sentence. Several may pass at once; the sentence then carries all labels that pass, up to the cap in Section 1. No test outranks another. Adapted from ReasoningFlow Table 3.

- Conclusion applies if the sentence asserts an answer to the question (a letter, or "the answer is …").
- Assumption applies if the sentence marks its own content as not necessarily true and later sentences depend on it.
- Planning applies if the sentence tells what comes next rather than doing it. A question that sets up an immediate check ("Does Bat > Ball?", "Is there a linguistic trick?") is Planning > local plan or > initiate verification; its one-word answer ("Yes.", "No.") is Reasoning > logical reasoning.
- Restatement applies if the sentence's content is entailed by the prompt or an earlier sentence with nothing new added. Quoting an option verbatim before evaluating it is Restatement > rephrasing the prompt > option text.
- Knowledge applies if the sentence states something that is not in the prompt and does not depend on earlier sentences. If it depends on earlier sentences, it is Reasoning instead.
- Example applies if the sentence illustrates a general point without directly solving the problem. If it directly solves, it is Reasoning instead.
- Reflection applies if removing the sentence leaves the reasoning logically complete.
- Reasoning applies if the sentence derives new content from earlier sentences and none of the exclusions above removes it.

### 4a. Worked cases (full references; Claude's provisional labels; v2 numbering)

Case 1. C-trace (eval0_multi0, sample 2, c004), s67 (old s60); the registered s* of the submitted study.
- Text: "However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint."
- Labels:
  - Reasoning > hedge word analysis > everyday reading
  - Reflection > meta-evaluation of a step > option (B)
- Combined sentence (Kind 3, Section 1b).

Case 2. E-trace (eval0_multi0, sample 40, e036), s17, s18, s19 (old s17, one sentence before the equation rule).
- s17: "Ball = $x$,"
  - Reasoning > defining symbols > algebra
- s18: "Bat = $x + 1.00$"
  - Reasoning > calculation > algebra
  - Assumption > assuming a missing premise by common practice > "$1.00 more"
- Combined sentence (Kind 3).
- s19: "(Wait, the classic problem says "The bat costs $1.00 *more* than the ball." But this prompt says "The bat costs more than the ball." It does not say "$1.00 more".)"
  - Planning > initiate verification
  - Reasoning > comparison > prompt vs original text
- Combined sentence (Kind 2). Before the equation rule, one sentence held all five labels.

Case 3. C-trace, s189 (old s182).
- Text: "This fits perfectly."
  - Reflection > meta-evaluation of a step > option (C)

Case 4. C-trace, s38 (old s35).
- Text: "This is a classic cognitive reflection test question (often attributed to Keith Stanovich or Shane Frederick)."
  - Knowledge > world knowledge > famous problem (CRT)
- Whether the attribution is correct does not matter for the label; that is why the Level 1 label is Knowledge, not Fact.

Case 5. C-trace, [s48, s57] (old [s45, s50], before the list pairs were split).
- Text: "Ball = $0.01," "Bat = $1.09." … "Ball = $0.54," "Bat = $0.56."
  - Example > non-exhaustive listing > algebra
- Ten sentences with the same label form one Level 1 node, Example [s48, s57], named Ex₇(10) in the labeled listing.

Case 6. E-trace, s102 (old s96).
- Text: "This seems like a distractor."
  - Reflection > meta-evaluation of a step > option (C)

Case 7. C-trace, s15 and s16 (old s15, one sentence before the equation rule).
- s15: "If Ball = $0.05,"
  - Assumption > branching (case split) > algebra
- s16: "then Bat = 1.10 - 0.05 = $1.05."
  - Reasoning > calculation > algebra
- No longer a combined sentence; s15 opens block C-B03 by rule R2.

Case 8. E-trace, s56 (old s51).
- Text: "But as an AI, I must address the prompt *as written*."
  - Knowledge > self-knowledge > role

Case 9. C-trace, s204 (old s197).
- Text: "But usually, LLMs are evaluated on their ability to follow instructions and analyze text accurately."
  - Knowledge > self-knowledge > evaluation context

## 5. Item-specific labels and comparability with ReasoningFlow

What used to be called the "content axis" in earlier versions (the topic a sentence is about, kept separately from its function) is gone. Topics are now leaves of the same tree: Level 3 leaves under a general Level 2 leaf where one fits (algebra under calculation; famous problem under world knowledge), and new Level 2 leaves marked [item] where no general leaf fits (option evaluation, comparison, hedge word analysis, self-knowledge, announce output).

For comparison with ReasoningFlow's corpus, item-specific leaves collapse to the nearest general leaf: comparison → logical reasoning; option evaluation → logical reasoning; hedge word analysis → speculation; self-knowledge → Knowledge (Fact) with no leaf; announce output → local plan. Level 3 leaves are dropped in the comparison. Level 1 needs no mapping.

## 6. Nodes and blocks (derived from sentence labels)

### 6a. Nodes

Nodes follow from the labels by the definition in Section 0a and need no further rules. Node boundaries are the finest natural cut positions of a trace.

### 6b. Openers, then blocks

Opener rules. A sentence is an opener if at least one holds:
- R1. It is the first sentence of a Planning node, and not every sentence of that node is Planning > local plan.
- R2. It carries Assumption > branching (a case opener): "If Ball = $0.05,", "But with text 'The bat costs more than the ball':".
- R3. It carries Conclusion > final answer.

Planning > local plan forms, which never make a sentence an opener:
- N1. A step label with a colon inside a derivation: "Constraint:", "Part 1:", "Substitute y:", "Original:", "For example:", "System:", "As written:", "The classic says:".
- N2. A check-question and its short answer: "Does Bat > Ball?" / "Yes.", "Is it a fact?" / "No.", "A ball for $0.01?" / "Unlikely.".
- N3. An item of a labeled or bulleted series under a heading: option headers "(A) It is $0.05:", drafting steps "1. Define variables:", bullet labels "- Question:", plan-list bullets "- State the classic version vs. this version.".
- N4. A number marker split off by the splitter ("1.", "2.") attaches to the sentence that follows.

Block. Given the openers, a block is [s_open, s_next_open); the last block runs to the end of the trace. Blocks are the default unit for resampling cuts and for the block-to-block transition analysis; node boundaries serve dense passes.

Two consequences: an opener owns everything until the next opener, so a topic change without a plan sentence stays inside the block (C-B14 = [s120, s132) opens with "Let's re-read the prompt carefully." and ends with sentences that infer the writer's intent); and series items (N3) remain visible as Planning > local plan nodes, so a finer cut inside a block is always available, as the old run's cuts (old s58–s64, now [s0, s65] to [s0, s71]) were inside C-B08.

### 6c. C-trace blocks (Claude's provisional labels; v2 numbering)

Reading the table: rows are blocks in order; the block number is the subscript of every node in the row, so it has no column of its own. The last column is the block's composition as a sequence of Level 1 nodes, named as in Section 0a (abbreviation, block subscript, running superscript when needed, sentence count in parentheses). The full sentence-by-sentence labels behind this table are in the labeled listing file.

C-trace: 375 sentences, 220 Level 1 nodes (219 if runs are not cut at block boundaries; the Conclusion node [s373, s374] is cut by the final-answer opener at s374, per Section 0a), 46 blocks, 9 combined sentences, 0 `unspecified`. Level 1 counts (label occurrences): Reasoning 142, Planning 112, Restatement 66, Knowledge 16, Example 16, Conclusion 14, Reflection 12, Assumption 6. Combined pairs: Planning+Restatement 3, Planning+Reasoning 2, Reasoning+Reflection 1, Reasoning+Knowledge 1, Assumption+Reasoning 1, Reasoning+Planning 1. Combined sentences at: s43, s67, s75, s111, s114, s160, s227, s291, s295.

| sentences | opening sentence | Level 1 nodes inside |
|---|---|---|
| [s0, s7] | Here's a thinking process that leads to the suggested answer: | Pl₀(3) → Rs₀(5) |
| [s8, s12] | ⏎⏎2. | Pl₁(2) → Re₁(2) → Rs₁ |
| [s13, s14] | ⏎⏎3. | Pl₂(2) |
| [s15, s22] | ⏎    *   If Ball = \$0.05, | As₃ → Re₃¹ → Pl₃¹ → Re₃²(2) → Pl₃² → Re₃³(2) |
| [s23, s30] | ⏎    *   If Ball = \$0.01, | As₄ → Re₄¹ → Pl₄¹ → Re₄²(2) → Pl₄² → Re₄³(2) |
| [s31, s35] | ⏎    *   If Ball = \$0.55, | As₅ → Re₅¹ → Pl₅ → Re₅²(2) |
| [s36, s42] | ⏎⏎4. | Pl₆¹(2) → Kn₆¹(2) → Pl₆² → Re₆ → Kn₆² |
| [s43, s57] | ⏎    *   *Check the text provided in the prompt again carefully:* "A b | [Pl+Rs]₇ → Rs₇ → Re₇(3) → Ex₇(10) |
| [s58, s78] | ⏎⏎5. | Pl₈¹(3) → Re₈¹(3) → Pl₈² → Re₈²(2) → [Re+Rf]₈ → Pl₈³ → Rf₈¹ → Re₈³(2) → Pl₈⁴ → Rf₈² → Pl₈⁵ → [Re+Kn]₈ → Re₈⁴ → Pl₈⁶ → Rf₈³ |
| [s79, s97] | ⏎⏎6. | Pl₉¹(3) → Re₉¹ → Kn₉¹ → Pl₉² → Kn₉²(4) → Re₉²(2) → Pl₉³ → Re₉³(4) → Rs₉ → Re₉⁴ |
| [s98, s106] | ⏎⏎7. | Pl₁₀(3) → Re₁₀(6) |
| [s107, s113] | ⏎⏎    *Self-Correction/Refinement:* Is there a hidden constraint I'm m | Pl₁₁ → Re₁₁¹(3) → [As+Re]₁₁ → Re₁₁² → Co₁₁ |
| [s114, s115] | ⏎⏎    *Let's look at the wording of (C) again:* "There is not enough i | [Pl+Rs]₁₂ → Re₁₂ |
| [s116, s119] | ⏎⏎    *However*, let's look at the wording of (A). | Pl₁₃ → Rs₁₃ → Re₁₃(2) |
| [s120, s131] | ⏎⏎    Let's re-read the prompt carefully. | Pl₁₄ → Rs₁₄(3) → Re₁₄(8) |
| [s132, s136] | ⏎⏎    Let's check Option (B) vs (C). | Pl₁₅ → Rs₁₅(2) → Re₁₅ → Rf₁₅ |
| [s137, s143] | ⏎⏎    **Wait, let's look at Option (F) "None of the above".** | Pl₁₆¹(2) → Re₁₆¹(2) → Pl₁₆² → Re₁₆²(2) |
| [s144, s147] | ⏎⏎    Let's compare (C) and (E). | Pl₁₇ → Rs₁₇ → Re₁₇(2) |
| [s148, s159] | ⏎⏎    **Decision Logic:** | Pl₁₈ → Re₁₈¹(4) → Kn₁₈(2) → Re₁₈²(4) → Co₁₈ |
| [s160, s165] | ⏎⏎    *Alternative interpretation check:* Did the user *intend* to wri | [Pl+Re]₁₉ → Re₁₉(4) → Co₁₉ |
| [s166, s170] | ⏎⏎    **Let's double check the prompt text provided in the chat interf | Pl₂₀ → Rs₂₀(3) → Re₂₀ |
| [s171, s186] | ⏎⏎    **Reasoning Summary:** | Pl₂₁ → Rs₂₁(15) |
| [s187, s189] | ⏎⏎    **Let's verify Option (C) syntax.** | Pl₂₂ → Rs₂₂ → Rf₂₂ |
| [s190, s192] | ⏎⏎    **What if the answer is (F)?** | Pl₂₃ → Re₂₃(2) |
| [s193, s198] | ⏎⏎    **Let's check if there is a linguistic trick.** | Pl₂₄¹ → Rs₂₄ → Pl₂₄² → Re₂₄¹ → Pl₂₄³ → Re₂₄² |
| [s199, s201] | ⏎⏎    **Conclusion:** | Pl₂₅ → Co₂₅(2) |
| [s202, s208] | ⏎⏎    *Self-Correction on "Best Option":* | Pl₂₆ → Re₂₆¹ → Kn₂₆ → Re₂₆²(4) |
| [s209, s215] | ⏎⏎    Let's confirm the math for the standard riddle just to be sure. | Pl₂₇ → Re₂₇(6) |
| [s216, s226] | ⏎⏎    But with text "The bat costs more than the ball": | As₂₈ → Re₂₈¹(2) → Pl₂₈¹ → Re₂₈² → Rf₂₈ → Pl₂₈² → Re₂₈³(3) → Co₂₈ |
| [s227, s228] | ⏎⏎    **Final check of the Prompt:** "Choose the single best option". | [Pl+Rs]₂₉ → Co₂₉ |
| [s229, s253] | ⏎⏎    **Drafting the Explanation:** | Pl₃₀¹(3) → Re₃₀ → Pl₃₀²(2) → Rs₃₀¹(2) → Pl₃₀³(2) → Rs₃₀²(4) → Pl₃₀⁴(2) → Rs₃₀³(2) → Pl₃₀⁵(2) → Rs₃₀⁴(2) → Pl₃₀⁶(2) → Co₃₀ |
| [s254, s262] | ⏎⏎    Wait, is there an argument for (E)? | Pl₃₁ → Rs₃₁ → Kn₃₁ → Re₃₁(6) |
| [s263, s265] | ⏎⏎    Let's check if (F) is a trap. | Pl₃₂ → Re₃₂(2) |
| [s266, s276] | ⏎⏎    Let's look at the wording of (C) again. | Pl₃₃¹ → Rs₃₃ → Re₃₃¹ → Pl₃₃² → Re₃₃² → Pl₃₃³ → Re₃₃³(4) → Rf₃₃ |
| [s277, s287] | ⏎⏎    Let's consider if "A bat" and "A ball" implies standard merchand | Pl₃₄¹(2) → Re₃₄¹ → Pl₃₄² → Re₃₄² → Pl₃₄³ → Re₃₄³ → Pl₃₄⁴ → Re₃₄⁴(2) → Co₃₄ |
| [s288, s301] | ⏎⏎    **Wait, hold on.** | Pl₃₅(2) → Re₃₅¹ → [Pl+Re]₃₅ → Kn₃₅(2) → Re₃₅² → [Re+Pl]₃₅ → Ex₃₅ → Re₃₅³(4) → Co₃₅ |
| [s302, s324] | ⏎⏎    **Step-by-step derivation for the final output:** | Pl₃₆¹(3) → Rs₃₆¹ → Pl₃₆² → Rs₃₆² → Pl₃₆³(2) → Rs₃₆³(2) → Pl₃₆⁴(2) → Rs₃₆⁴ → Pl₃₆⁵(2) → Rs₃₆⁵(2) → Pl₃₆⁶(2) → Rs₃₆⁶ → Pl₃₆⁷(2) → Co₃₆ |
| [s325, s329] | ⏎⏎    One distinct possibility: | Pl₃₇¹(2) → Re₃₇¹ → Pl₃₇² → Re₃₇² |
| [s330, s339] | ⏎⏎    **Final Answer Formulation:** | Pl₃₈¹ → Rs₃₈¹ → Pl₃₈² → Rs₃₈² → Pl₃₈³ → Rs₃₈³(5) |
| [s340, s341] | ⏎⏎    Wait, I should check if there's any weird interpretation of "A b | Pl₃₉ → Re₃₉ |
| [s342, s343] | ⏎⏎    Let's double check if "more than" in some dialects implies "sign | Pl₄₀ → Re₄₀ |
| [s344, s351] | ⏎⏎    Final check on options. | Pl₄₁ → Re₄₁¹ → Rf₄₁¹ → Re₄₁² → Rf₄₁² → Re₄₁³ → Rf₄₁³ → Co₄₁ |
| [s352, s355] | ⏎⏎    **Wait, looking at the options again.** | Pl₄₂ → Rs₄₂ → Rf₄₂ → Kn₄₂ |
| [s356, s361] | ⏎⏎    If the question was the standard riddle, the options would likel | As₄₃ → Ex₄₃(4) → Re₄₃ |
| [s362, s373] | ⏎⏎    **One final sanity check:** | Pl₄₄¹(3) → Re₄₄¹ → Pl₄₄² → Re₄₄²(3) → Pl₄₄³ → Ex₄₄ → Re₄₄³ → Co₄₄ |
| [s374, s374] | ⏎⏎    Therefore, Answer is (C). | Co₄₅ |

### 6d. E-trace blocks (Claude's provisional labels; v2 numbering)

E-trace: 254 sentences, 148 Level 1 nodes (147 if runs are not cut at block boundaries; the Conclusion node [s244, s246] is cut by the final-answer opener at s245), 37 blocks, 5 combined sentences, 0 `unspecified`. Level 1 counts (label occurrences): Planning 90, Restatement 57, Reasoning 41, Conclusion 26, Reflection 24, Knowledge 14, Example 6, Assumption 1. Combined pairs: Reasoning+Assumption 1, Planning+Reasoning 1, Reasoning+Reasoning 1, Restatement+Reasoning 1, Planning+Restatement 1. Combined sentences at: s18, s19, s46, s58, s193.

| sentences | opening sentence | Level 1 nodes inside |
|---|---|---|
| [s0, s11] | Here's a thinking process: | Pl₀¹(4) → Rs₀¹(3) → Pl₀² → Rs₀² → Pl₀³ → Rs₀³(2) |
| [s12, s15] | ⏎⏎2. | Pl₁(2) → Kn₁(2) |
| [s16, s18] | ⏎   - Let's verify: | Pl₂ → Re₂ → [Re+As]₂ |
| [s19, s19] | (Wait, the classic problem says "The bat costs $1.00 *more* than the b | [Pl+Re]₃ |
| [s20, s41] | ⏎   - Let's re-read carefully: | Pl₄¹ → Rs₄¹(3) → Re₄¹ → Pl₄² → Kn₄ → Re₄² → Pl₄³ → Re₄³(2) → Rs₄² → Re₄⁴ → Pl₄⁴ → Ex₄(6) → Re₄⁵ → Co₄ |
| [s42, s52] | ⏎⏎3. | Pl₅(2) → Re₅¹ → Rf₅¹ → [Re+Re]₅ → Re₅² → Rf₅² → Re₅³ → Kn₅ → Re₅⁴ → Rf₅³ |
| [s53, s70] | ⏎⏎   Let's reconsider the exact wording. | Pl₆¹ → Kn₆¹ → Re₆¹ → Kn₆² → Pl₆² → [Rs+Re]₆ → Pl₆³ → Re₆²(2) → Pl₆⁴ → Re₆³(2) → Co₆(2) → Re₆⁴ → Rs₆ → Re₆⁵(2) |
| [s71, s74] | ⏎   Wait, let's think about how these questions are typically framed i | Pl₇ → Kn₇ → Re₇ → Rf₇ |
| [s75, s76] | But let's check if there's a standard interpretation. | Pl₈ → Kn₈ |
| [s77, s92] | ⏎   Let's look at the options again: | Pl₉¹ → Rs₉(6) → Re₉¹(4) → Kn₉ → Re₉² → Co₉ → Pl₉² → Re₉³ |
| [s93, s95] | ⏎   Let's consider if the prompt is a direct quote from a known puzzle | Pl₁₀ → Re₁₀ → Rf₁₀ |
| [s96, s99] | ⏎   I will explain that the classic problem specifies "$1.00 more", wh | Pl₁₁(3) → Co₁₁ |
| [s100, s104] | ⏎⏎   Wait, let's double check option (C): | Pl₁₂ → Rs₁₂ → Rf₁₂(2) → Co₁₂ |
| [s105, s116] | ⏎⏎   Let's structure the reasoning: | Pl₁₃¹(4) → Rs₁₃(2) → Pl₁₃²(4) → Re₁₃ → Co₁₃ |
| [s117, s119] | ⏎⏎   One caveat: | Pl₁₄ → Re₁₄ → Co₁₄ |
| [s120, s133] | ⏎⏎   Let's draft the response carefully. | Pl₁₅¹(9) → Re₁₅¹ → Pl₁₅² → Re₁₅² → Kn₁₅ → Co₁₅ |
| [s134, s143] | ⏎   Structure: | Pl₁₆(7) → Co₁₆(2) → Rf₁₆ |
| [s144, s151] | Proceed. | Pl₁₇(2) → Rs₁₇ → Re₁₇(2) → Co₁₇¹ → Kn₁₇ → Co₁₇² |
| [s152, s153] | ⏎   Final decision: | Pl₁₈ → Co₁₈ |
| [s154, s165] | ⏎   Draft response: | Pl₁₉ → Rs₁₉(9) → Co₁₉(2) |
| [s166, s167] | ⏎   Checks: | Pl₂₀ → Rf₂₀ |
| [s168, s173] | Ready. | Pl₂₁(3) → Kn₂₁ → Re₂₁ → Rf₂₁ |
| [s174, s176] | ⏎   I'll output exactly this. | Pl₂₂(2) → Co₂₂ |
| [s177, s181] | ⏎   Proceeds. | Pl₂₃(3) → Re₂₃ → Rf₂₃ |
| [s182, s186] | ⏎   What if the prompt actually *meant* the classic question and it's  | Pl₂₄ → Kn₂₄ → Rf₂₄¹ → Co₂₄ → Rf₂₄² |
| [s187, s192] | ⏎   Proceeds. | Pl₂₅(2) → Rs₂₅(2) → Rf₂₅(2) |
| [s193, s198] | ⏎   [Final Check of the Prompt] "Choose the single best option: | [Pl+Rs]₂₆ → Rs₂₆(4) → Rf₂₆ |
| [s199, s203] | ⏎   Output Generation. | Pl₂₇(3) → Rs₂₇ → Co₂₇ |
| [s204, s206] | I'll write it out clearly. | Pl₂₈ → Rf₂₈(2) |
| [s207, s212] | ⏎   [Done.] ⏎   *Self-Correction/Refinement during generation prep*: | Pl₂₉(2) → Rs₂₉ → Rf₂₉(2) → Co₂₉ |
| [s213, s214] | ⏎   Final Answer: | Pl₃₀ → Co₃₀ |
| [s215, s219] | ⏎   Proceeds. | Pl₃₁(2) → Rs₃₁(3) |
| [s220, s227] | ⏎   [Output] -> *Proceeds* (Note: | Pl₃₂(3) → Re₃₂ → Kn₃₂ → Co₃₂(2) → Rf₃₂ |
| [s228, s244] | ⏎   Output Generation. | Pl₃₃(2) → Rs₃₃(14) → Co₃₃ |
| [s245, s246] | ⏎⏎   Answer: | Co₃₄(2) |
| [s247, s250] | ⏎   [Done.] ⏎   *Self-Correction/Verification during output prep*: | Pl₃₅ → Rf₃₅(3) |
| [s251, s253] | Ready. | Pl₃₆(3) |

### 6e. What the tables show (provisional)

- Two things merge that a reader might expect apart. Consecutive global plans form one Planning node, so C-B00 opens at "Here's a thinking process" and swallows the "1. Analyze the Request" heading (Pl₀(3)). And an announce-output sentence immediately followed by a verification opener forms one Planning node, so E-B17 opens at "Proceed." although the block's work is "One minor check:" (E-B21, E-B23, E-B25, E-B28 likewise). Item 7 discusses the second.
- From C-B11 on, the C-trace is a run of verification and backtracking blocks (C-B11 to C-B45), and from E-B06 on the E-trace is the same (E-B06 to E-B36); its three drafting blocks (C-B21, C-B30, C-B36) and its Final Answer Formulation (C-B38) are almost entirely Restatement, which is what a draft is.
- The E-trace has 16 announce-output sentences and 26 Conclusion sentences against 41 Reasoning sentences; its second half is announcing, restating and re-deciding, with little new derivation. Both traces contain zero `unspecified` labels, so the tree covered every sentence, with two item leaves doing the work the general leaves could not (Reasoning > option evaluation: 36 label occurrences in C, 6 in E; Planning > announce output: 16 in E, none in C).
- Block sizes run from 1 sentence (C-B45, E-B03) to 25 (C-B30); the median is 7 sentences in the C-trace and 5 in the E-trace.

## 7. Edges

ReasoningFlow's edge labels (its Table 4) are not part of this document. Decision (Kian, 2026-09-14): analysis of the edges does not reveal anything useful for this project. What the edges would record about verification and backtracking is carried here by the Planning leaves initiate verification and initiate backtracking.

## 8. Derived phases (not labeled)

Source: Marjanovic et al., "DeepSeek-R1 Thoughtology", arXiv 2504.07128. Bloom = everything before the first Conclusion > intermediate conclusion. Reconstruction = everything after it. Final decision = Conclusion > final answer.

Under the current labels (v1 listing), each trace has two candidates for the first intermediate conclusion, and the same decision settles both traces:
- C-trace: s113 "Still, no unique solution." (block C-B11) answers the question in substance without naming an option; s159 "Therefore, (C) is the most logical choice." (C-B18) is the first that names an option.
- E-trace: s41 "Therefore, there is not enough information to determine a unique price for the ball." (E-B04) answers in substance; s99 "Option (E) best captures this." (E-B11) is the first that names an option.
Reading A (substance counts): Bloom = C [s0, s113], E [s0, s41]. Reading B (only a named option counts): Bloom = C [s0, s159], E [s0, s99]. Decision pending (Section 12, item 8). Whichever is chosen also fixes the Level 2 rule: under Reading B, "no unique solution" sentences are Reasoning > logical reasoning, not Conclusion, and the labeling is re-run accordingly.

## 9. Expansion rules

- Level 1 is frozen as a set of eight labels.
- A new Level 2 leaf is created either from residue (when `unspecified` under a Level 1 label accumulates cases that share a describable feature) or as an item-specific leaf marked [item]. Either way it comes with a one-line rule separating it from its siblings, two example sentences with full references, its parent, and its mapping to the nearest ReasoningFlow leaf (Section 5).
- A Level 3 leaf may be added under any Level 2 leaf by the same procedure; nodes at Level 3 follow Section 0a without change.
- Every change is dated in the changelog. Labels on already-labeled data are re-run after a change, never patched by hand.

## 10. Crosswalk to other schemes

The mapping of Venhoff et al., Thought Anchors, Gandhi et al., the FSM paper, Schoenfeld episodes, Thoughtology, Psyche, ReasonOps (partial) and Bloom's taxonomy onto Levels 1 and 2 is in the chat record of 2026-09-13; it is to be moved into this document once the levels are final. Two points from it matter here: every scheme's "deduction / computation / implement" lands on Reasoning and every scheme's "backtracking" lands on Planning > initiate backtracking; and no scheme has a label for comparing options, which is why option evaluation is an [item] leaf here.

## 11. Validation

Blind labeling by Kian is skipped for lack of time (Kian, 2026-09-14, item 5). Validation is therefore face validity: Kian reads the full labeled listing and the block tables and marks what does not make sense; disagreements are logged with the sentence index and the label he would give. When the judge runs, its labels are compared against Claude's labels with the per-label kappa and Jaccard of Section 1a, reported as judge-versus-Claude agreement, not as accuracy against a human ground truth. ReasoningFlow's α > 0.8 and F1 0.865 remain the reference points for what a well-behaved scheme achieves, with the caveat that we cannot claim either without a human-labeled subset.

## 12. Open items, with Kian's decisions of 2026-09-14

1. Splitting rule. APPROVED and closed. The v2 numbering is adopted; every index in this document and both block tables use it; s* is C s67. The glossary entry for s* lives in 2026-09-14_action_summary_v2.md (confirmed); findings_summary.md is archived.

2. Combined sentences. EXPLAINED in Section 1b, with the 14 observed cases sorted into three kinds. Decision pending Kian's review of the listing: keep all; keep Kind 3 only and remove Kinds 1–2 by a quote-splitting rule and a question convention; or drop double labels.

3. Knowledge vs. Recall. ANSWERED in Section 2: Recall has no precedent as a top-level label in the trace schemes; Knowledge is Bloom's original first level. Knowledge kept.

4. Self as AI. DECIDED: Knowledge > self-knowledge, with Level 3 leaves role and evaluation context. Applied to C s204, C s292–s293, E s56, E s183.

5. Blind labeling. SKIPPED (Kian). Replaced by the face-validity review described in Section 11.

6. Rule R1 vs N2, explained with an example. A check-question is Planning > local plan and never opens a block, whatever its scope. Example: C s138 "Is (C) technically correct?" governs five sentences (s139–s143) but stays inside C-B16, which opened at s137 "Wait, let's look at Option (F)". So C-B16 = [s137, s143] contains both the F-check and the C-check. Same for C s291 "Is it possible the user made a typo and wants me to correct it and answer (A)?", which governs ten sentences inside C-B35 "Wait, hold on.". Alternative: a scope threshold, "a local plan whose scope is at least k sentences opens a block". Effect measured on Claude's labels: with k = 3, 15 local plans in the C-trace and 7 in the E-trace would become openers (among them the six option headers, "The CRT question reads:", "Strictly logically:", "It covers both bases:", "Part 2:", "For example:", "This defines a range for b:"); with k = 5, 6 and 2. Note that the threshold promotes step labels as readily as check-questions, so it changes the meaning of "block" from "a move" to "any labeled stretch". Decision: (a) no threshold, as now; (b) k = 5; (c) k = 3.

7. The E-trace tail, explained with an example. Under the current rules Planning > announce output can open a block. Because the model writes "Proceeds." or "Ready." and then immediately a verification opener, the two sentences form one Planning node and the block opens on the announcement: E-B21 = [s168, s173] opens at "Ready." although its work is "One thing: could 'not well posed' be too strong?". Variant (c), "announce output never opens", gives 33 blocks instead of 37 for the E-trace and leaves the C-trace unchanged at 46; under it the tail reads [s169, s174] "One thing:", [s175, s177] "Final Answer:", [s178, s181] "[Self-Correction/Verification during drafting]", [s182, s192] "What if the prompt actually meant the classic question", [s193, s199] "[Final Check of the Prompt]", [s200, s206] "[Output] -> See response", [s207, s212] "[Done.] Self-Correction", [s213, s221] "Final Answer:", [s222, s228] "[Final Check]:", [s229, s244] "[Response Text]", [s245, s246] "Answer: E", [s247, s253] "[Done.] Self-Correction/Verification during output prep" (the trailing announcements join it). Decision: (a) as now; (c) announce output never opens.

8. First intermediate conclusion, both traces. "Intermediate conclusion" means a sentence that states the answer to the posed question (which option, or whether the price is determinable) as the result of the reasoning before it, without being the final answer line. Each trace has two candidates, and one decision settles both (Section 8): Reading A, a sentence that answers in substance counts (C s113 "Still, no unique solution."; E s41 "Therefore, there is not enough information to determine a unique price for the ball."); Reading B, only a sentence naming an option counts (C s159 "Therefore, (C) is the most logical choice."; E s99 "Option (E) best captures this."). The current labels follow Reading A. The E-trace passages, with Claude's labels:

   E [s40, s45]:
   - s40 "All satisfy B + b = 1.10 and B > b." — Reasoning > logical reasoning > algebra
   - s41 "Therefore, there is not enough information to determine a unique price for the ball." — Conclusion > intermediate conclusion
   - s42–s43 "3. Evaluate Options based on the actual text:" — Planning > global plan
   - s44 "(A) It is $0.05 - Incorrect, assumes the classic '$1.00 more' constraint." — Reasoning > option evaluation > (A)
   - s45 "(B) It is probably $0.05 - Incorrect." — Reflection > meta-evaluation of a step > option (B)

   E [s95, s107]:
   - s95 "This omission changes everything." — Reflection > emotion or impression
   - s96 "I will explain that the classic problem specifies '$1.00 more', which yields $0.05." — Planning > global plan
   - s97 "As written, it only says 'more', which gives a range of valid answers ($0.00 < ball < $0.55)." — Planning > global plan
   - s98 "Therefore, the question lacks sufficient constraints for a unique solution, making it not well-posed (or underdetermined)." — Planning > global plan
   - s99 "Option (E) best captures this." — Conclusion > intermediate conclusion
   - s100 "Wait, let's double check option (C):" — Planning > initiate verification
   - s101 "'There is not enough information, but the answer is most likely $0.05'." — Restatement > rephrasing the prompt > option text
   - s102 "This seems like a distractor." — Reflection > meta-evaluation of a step > option (C)
   - s103 "Option (E) is clean." — Reflection > meta-evaluation of a step > option (E)
   - s104 "I'll go with (E)." — Conclusion > intermediate conclusion
   - s105 "Let's structure the reasoning:" — Planning > global plan
   - s106–s107 "- State the classic version vs. this version." — Planning > local plan

   The C-trace passage, with Claude's labels:
   - s107 "Self-Correction/Refinement: Is there a hidden constraint I'm missing?" — Planning > initiate verification
   - s108–s110 "'A bat and a ball…' implies discrete items." / "…cost $1.10…" implies currency." / "…bat costs more…" implies inequality." — Reasoning > logical reasoning
   - s111 "If the currency has a smallest unit (cents), then b can be 0.01, 0.02, …" — Assumption > assuming an uncertain fact + Reasoning > calculation > algebra
   - s112 "0.54." — Reasoning > calculation > algebra
   - s113 "Still, no unique solution." — Conclusion > intermediate conclusion
   - s159 "Therefore, (C) is the most logical choice." — Conclusion > intermediate conclusion (first to name an option)

   Decision: Reading A or Reading B.

9. Cut placement (blocks, nodes, or both). DECIDED by Kian, 2026-09-14 (evening): blocks first, always. Stage one resamples at every block-end cut under the stopping rule; stage two, optional, puts node-level cuts inside the single block with the largest Δ_m, is decided after the stage-one plot and registered separately (Section 0e).

10. Transition counts P_source and the analysis columns. NOT YET.

11. Probability notation of Sections 0d and 0e. CONFIRMED by Kian with v3 on 2026-09-14 (typed arrows -> and -->, cut(B_m), the block-level quantities of Section 0e).

12. Whether --> includes the adjacent case. DECIDED by Kian, 2026-09-14: inclusive; -> is a special case of -->.

13. The stopping rule and the transition tree. DECIDED by Kian, 2026-09-14: option (a), accept as drafted. After M no cut is resampled; resampled transitions exist only for m ≤ M; for the tail, transitions come from P_corpus (the 44 sweep traces) and P_source. The E-trace may stop at the first or second cut (E is the default answer and P(E | cut-0) = 0.80 already); Kian accepts the saving — the submitted study learned nothing new from the E resampling.

14. Near-tie rule for stage two. DECIDED by Kian, 2026-09-14: if the 95% interval of the gap Δ_(1) − Δ_(2) excludes zero, the top block alone; otherwise both blocks; reason recorded in stage two's registration (Section 0e).

15. Unresolved continuations ("?"). DECIDED by Kian, 2026-09-14: they stay in the denominator, which is always n, as in the submitted run; their count is reported per cut. One "?" prevents the stop, so the stopping rule is conservative (Section 0e, with the archived examples).

16. Pattern brackets. CLOSED (Kian, 2026-09-14): ⟨ ⟩ kept.

## Changelog

- 2026-09-14 v3 (= chat3 of the 2026-09-14 evening chat; confirmed by Kian 2026-09-14) — Typed arrows -> and --> replace → and ⇝ in Section 0d (the rendered forms stay allowed in tables and figures; confirmed by Kian; --> inclusive, item 12 decided); pattern brackets ⟨ ⟩ kept (item 16 closed); near-tie rule by the interval of the gap (item 14 decided); unresolved continuations always in the denominator n, reported per cut (item 15 decided); stopping rule accepted with its consequence for the tail transitions and the E-arm (item 13 decided); n = 40 and a budget of about $100 recorded as the candidates for the pre-registration; cut(B_m) defined with blocks numbered from 0; new Section 0e with the block-level quantities agreed with Kian: P̂ with unresolved continuations in the denominator, a_T, P_m, Δ_m, trivial block, the stopping rule and M with its binomial facts, Tk and the localization report, the two-stage design, history conditions with --> and the order comparison, Level 1 as the default for transitions. Section 12: item 9 decided, item 11 restated, items 12–16 added. No label, boundary or count changed.
- 2026-09-14 v2 (= chat8) — Correction release, no rule changes. Node counts corrected to 220 (C) and 148 (E) under the stated rule that a block boundary ends a node (the earlier 219/147 counted runs across block boundaries; one Conclusion node per trace is cut by the final-answer opener). Section 8 regenerated from the current labels: both traces have a substance-versus-named-option pair (C s113/s159, E s41/s99) and one decision settles both; old-numbering indices removed. Section 12 item 1 closed (glossary now in the action summary v2), item 8 restated for both traces. Stale block references fixed (C-B14, C-B08, E-B06 to E-B36, one-sentence blocks C-B45 and E-B03, medians 7 and 5). Option-evaluation occurrence counts corrected to 36 (C) and 6 (E). Combined-sentence kinds listed explicitly (5 / 4 / 5). Case 5 refers to the node by its name Ex₇(10).
- 2026-09-14 v1 (local) — Renamed to 2026-09-14_labeling_scheme_v1.md under the Option A versioning convention; content identical to chat version 7 except for file names in cross-references (the sentence listing is now 2026-09-14_source_traces_sentences_v1.md, the labeled listing 2026-09-14_source_traces_labeled_v1.md).
- 2026-09-14 v7 — Node names changed to X_m^k(n): running index as a superscript (Re₃²) instead of a dotted subscript; Block column removed from the tables, the block number being carried by the subscripts; listing regenerated (file v3).
- 2026-09-14 v6 — Abbreviations defined in Section 0a; node names X_m.k(n) with block subscript, running index and sentence count; parentheses now mean sentence count only, and the probability notation of Section 0d is revised to identify nodes by name instead of by an occurrence counter; opener-label column removed from the block tables; labeled listing regenerated with node names (file v2).
- 2026-09-14 v5 — Splitting rule approved and the v2 numbering adopted throughout; complete sentence-level labeling of both traces by Claude (separate file), from which nodes and blocks are derived; block tables regenerated with the Level 1 node sequence inside each block; combined sentences explained with the 14 observed cases (Section 1b); Fact→Knowledge kept with the Recall precedent check; Reflection > self-role identification replaced by Knowledge > self-knowledge with Level 3 leaves; worked cases rewritten under the v2 numbering; validation changed to face-validity review; open items rewritten with Kian's decisions and the requested examples (items 6, 7, 8).
- 2026-09-14 v4 — Worked examples and worked cases reformatted as lists so that each sentence and each label is on its own line; probability notation proposed (Section 0d) with Kian's four examples translated; block-table columns renamed to "opener Level 1 / opener Level 2" and the reason the column is mostly Planning explained; open items 10 and 11 added.
- 2026-09-14 v3 — Opener defined from labels and block from openers (no circle); worked examples reformatted one label per line; the separate content axis removed and its topics placed as [item] Level 2 leaves and Level 3 leaves of the same tree, with a comparability mapping to ReasoningFlow; edges dropped from the document with Kian's decision noted; the equation-end splitting rule proposed in script-ready form with measured effect, a v2 listing, and the s* relocation (old C s60 → new C s67); worked cases redone under the proposed numbering where the rule changes them; open items updated.
- 2026-09-14 v2 — Levels numbered; node redefined as a same-label run; interval notation; provenance line. Superseded.
- 2026-09-14 v1 — Combined sentences flagged; agreement metrics; Fact → Knowledge; single-tier blocks with tables. Superseded.
- 2026-09-13 — Two-tier blocks, precedence order. Superseded.
