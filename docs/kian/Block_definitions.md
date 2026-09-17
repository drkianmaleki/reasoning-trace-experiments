## (9/13/26)
The previous method that I tried to define the blocks seemed to be so random and I did not like it. I believe a good and structured block definition is a research project on its own. If I now make up a block definition without any deep analysis, it can suffer from one of the following:
- It will not be generalizable to similar problems
- LLM as a judge and human as a judge may not agree on the block
- It will not be adoptable to any other case

So, I decided to look at the literature to see of someone has developed such block definition or not.

It has been done and it goes under the name of taxonomy,.

[Claude help to complete this list]
1- DeepSeek-R1 Thoughtology's four stages: the model restates the problem in its own words (Problem definition), derives an initial solution (Bloom), tries recomputation or alternative approaches to verify it (Reconstruction), and decides the final answer (Final decision), annotated at paragraph level, with Reconstruction repeating.

2- Venhoff, Thought Anchors, Schoenfeld, ReasonOps and the FSM paper each found independently. The fine level is where two recent papers go. "Probing the Psyche of Large Reasoning Models" (Nov 2025)

3- ReasoningFlow (Illinois, June 2026).

[ end of the summary of taxonomy]

After careful analysis, the taxonomy of Reason Flow is adopted



## (9/9/2026)
List of block names, definitions and examples 

1-
Block name: Problem statement
Definitions: Repeating the whole prompt or part of the prompt
Example: 
s3   **Problem:** "A bat and a ball cost \$1.10 in total.
s4   The bat costs more than the ball.
s5   How much does the ball cost?"
s6   **Options:** (A) \$0.05, (B) Probably \$0.05, (C) Not enough info, likely \$0.05, (D) Not sure, (E) Not well posed, (F) None of the above.
s7   **Task:** Explain reasoning and provide the final answer in a specific format.
Another example:
s40 *Check the text provided in the prompt again carefully:* "A bat and a ball cost \$1.10 in total.
s41  The bat costs more than the ball."
Care needed: When the text is analyzing a sentence, an option pr part of the prompt, this is not included in the problem statement.
Example of Care needed:
s53 *(A) It is \$0.05*:
s54  This assumes the standard version of the riddle where the bat costs \$1.00 *more* than the ball.
s55  However, strictly reading *this* text, \$0.05 is just one of many possibilities.



2- Block name: Algebra
Definitions: This block contains equations, mathematical conditions and mathematical statements. This block may have one or many results equations
Example:

s15  If Ball = \$0.05, then Bat = 1.10 - 0.05 = \$1.05.
s16  Does Bat > Ball?
s17  \$1.05 > \$0.05.
s18  Yes.
s19  Is the sum \$1.10?
s20  Yes.
s21  *Result:* \$0.05 is a *possible* solution.
s22  If Ball = \$0.01, then Bat = 1.10 - 0.01 = \$1.09.
s23  Does Bat > Ball?
s24  \$1.09 > \$0.01.
s25  Yes.
s26  Is the sum \$1.10?
s27  Yes.
s28  *Result:* \$0.01 is *also* a possible solution.
s29  If Ball = \$0.55, then Bat = 1.10 - 0.55 = \$0.55.
s30  Does Bat > Ball?
s31  \$0.55 is not greater than \$0.55 (it's equal).
s32  *Result:* \$0.55 is not a solution.

Another example:
*Implication:* Without the specific difference constraint (Bat = Ball + 1.00), there are infinite solutions.

3- Block name: Identifying the similar famous problem
Definition: In this block the model specifically mentions the famous problem. It may call it cognitive problem, or something related to Keith Stanovich or Shane Frederick.
Example:
s35  This is a classic cognitive reflection test question (often attributed to Keith Stanovich or Shane Frederick)
Another example: 
This is a classic cognitive reflection test (CRT) question by Shane Frederick.
Another example:
The problem you've presented is a well-known cognitive reflection puzzle.
Another example:
s35  This is a classic cognitive reflection test question (often attributed to Keith Stanovich or Shane Frederick).
s36  *The Trap:* Most people intuitively answer \$0.10 (Ball) and \$1.00 (Bat).
s37  Why?
s38  Because \$1.00 + \$0.10 = \$1.10.
Another example:
s76  It looks like the "Cognitive Reflection Test" (CRT) question.

4- Block name: Noticing the missing info
Definition: Identifying the missing information is one compares the prompt with the original problem
Example:
s39  But wait, the problem usually adds the constraint "The bat costs **\$1.00 more than the ball**.
Another example:
 *Observation:* The prompt **omits** the specific constraint "The bat costs \$1.00 more than the ball."

5- Block name: Confusing word
Definitions: where the text contains interpretation of confusing words. These words are "most likely", "likely" , and "probably"
Example:
s57 *(B) It is probably \$0.05*:
s58 "Probably" implies probability.
s59  Unless there's a distribution of prices given, we can't assign probability.
s60  However, in the context of riddles, this option acknowledges the likely intent of the user (referring to the famous riddle) while acknowledging the missing constraint.

6- Block name: Self awareness
Definitions: When the text says what its role is
Example:
s284 If I am an AI assistant, being helpful usually means spotting the typo.
Another example:
s51  But as an AI, I must address the prompt *as written*.

7- Block name: heading
Definitions: This line starts and ends with "**". it is the title of what comes next
Examples:
s2   **Analyze the Request:**
Another example:
s14  **Evaluate the Constraints & Ambiguity:**

8- 