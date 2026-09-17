#!/usr/bin/env python3
"""s1a_make_prompt.py -- pipeline step (3/9): the judge prompt and the label codes.

Reads docs/shared/2026-09-16_labeling_scheme_v5.md (the source of everything the judge is told)
and docs/shared/2026-09-16_action_summary_v5.md (Section 4, the verbatim item prompt), and writes

  prompts/judge_prompt_v1.md        the prompt (Sections 1-7, see build_prompt)
  prompts/labels_v1.json            the inventory of allowed label paths with their codes
  prompts/judge_prompt_v1.meta.json character count, estimated tokens, hashes, timestamp

Inventory (pipeline v1, step 3d/9): every Level 1 > Level 2 path of scheme Section 3 and every
Level 1 > Level 2 > Level 3 path of Section 3a.  Level 2 is mandatory (Level 1 alone is not a
label); a path may stop at Level 2 even where Level 3 leaves exist.

Codes (step 3c'/9): Level 1 = Pl Re Rf Kn Rs As Ex Co.  A Level 2 or Level 3 code is two or three
lowercase letters generated from the leaf name: the first letters of its words (letters only,
hyphens split words, at most three words); a one-word name takes its first two letters; an
option leaf "(X)" or "option (X)" takes the capital letter X.  If a code collides with an
earlier sibling under the same parent, it is extended with the following consonants of the
leaf's words until unique (no leaf of scheme v4 needs this).  Codes join with dots: Re.ca.al.

Decision 6 of the pipeline: no sentence of the two source traces (c004, e036) appears in the
prompt.  Every quote the scheme takes from the traces is replaced by an invented sentence about
another problem (a lily-pad doubling puzzle, a train problem) or by a description; the
replacements are listed in SUBSTITUTIONS and asserted absent from the prompt.  The gate
scripts/tests/t3_prompt.py enforces it against sentences_source.jsonl.

Standard library only.  No network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEME = REPO / "docs" / "shared" / "2026-09-16_labeling_scheme_v5.md"
SUMMARY = REPO / "docs" / "shared" / "2026-09-16_action_summary_v5.md"
PROMPTS_DIR = REPO / "prompts"
OUT_PROMPT = PROMPTS_DIR / "judge_prompt_v1.md"
OUT_LABELS = PROMPTS_DIR / "labels_v1.json"
OUT_META = PROMPTS_DIR / "judge_prompt_v1.meta.json"
VERSION = "v1"
VERSIONS = ("v1", "v2")


def prompt_paths(version: str, out_dir: Path = PROMPTS_DIR) -> tuple[Path, Path, Path]:
    """(prompt, labels, meta) file paths of a prompt version."""
    if version not in VERSIONS:
        raise ValueError(f"unknown prompt version {version!r}; known: {VERSIONS}")
    return (out_dir / f"judge_prompt_{version}.md", out_dir / f"labels_{version}.json",
            out_dir / f"judge_prompt_{version}.meta.json")

LEVEL1 = [("Planning", "Pl"), ("Reasoning", "Re"), ("Reflection", "Rf"), ("Knowledge", "Kn"),
          ("Restatement", "Rs"), ("Assumption", "As"), ("Example", "Ex"), ("Conclusion", "Co")]
L1_CODE = dict(LEVEL1)
L1_NAMES = [n for n, _ in LEVEL1]
VOWELS = set("aeiou")
NEWLINE_MARK = "\u23ce"

SECTION_TITLES = [
    "## 1. Task",
    "## 2. The item the traces reason about",
    "## 3. Level 1: what a sentence is doing",
    "## 4. Levels 2 and 3: the code table",
    "## 5. Input format",
    "## 6. Output format",
    "## 7. Worked examples",
]


# ----------------------------------------------------------------------------
# Reading the scheme
# ----------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


def section(text: str, heading_start: str) -> str:
    """The body of the section whose heading line starts with heading_start (e.g. '## 3. '),
    up to the next line that starts with '## '."""
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(heading_start))
    body = []
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        body.append(l)
    return "\n".join(body)


def _clean_level2_leaf(item: str) -> str:
    item = re.sub(r"\s*\[item[^\]]*\]", "", item)          # [item] and [item; ...]
    item = re.sub(r"\s*\(ReasoningFlow's[^)]*\)", "", item)  # the renaming note on the Knowledge line
    return item.strip()


def parse_level2(sec3: str) -> tuple[dict[str, list[str]], dict[tuple[str, str], str]]:
    """Level 2 leaves per Level 1 label (scheme order) and the definitions of the item-specific
    leaves ('- Reasoning > comparison: ...')."""
    leaves: dict[str, list[str]] = {}
    definitions: dict[tuple[str, str], str] = {}
    for line in sec3.splitlines():
        if not line.startswith("- "):
            continue
        body = line[2:]
        m = re.match(r"^(%s) > (.+)$" % "|".join(L1_NAMES), body)
        if not m:
            continue
        l1, rest = m.group(1), m.group(2)
        if ":" in rest:  # a definition line: '- Reasoning > comparison: the sentence ...'
            leaf, definition = rest.split(":", 1)
            definitions[(l1, leaf.strip())] = definition.strip()
            continue
        leaves[l1] = [_clean_level2_leaf(x) for x in rest.split(" · ")]
    missing = [n for n in L1_NAMES if n not in leaves]
    if missing:
        raise RuntimeError(f"Section 3 has no leaf line for {missing}")
    return leaves, definitions


def _split_level3_item(item: str) -> tuple[str, str]:
    """A Section 3a item -> (leaf name, gloss).  '(A)' and 'option (A)' are names; 'famous
    problem (CRT: ...)' keeps the acronym; any other parenthetical is a gloss."""
    item = item.strip()
    if re.fullmatch(r"\([A-Z]\)", item) or re.fullmatch(r"option \([A-Z]\)", item):
        return item, ""
    m = re.fullmatch(r"(.+?) \(([A-Z]+): (.+)\)", item)
    if m:
        return f"{m.group(1)} ({m.group(2)})", m.group(3)
    m = re.fullmatch(r"(.+?) \((.+)\)", item)
    if m:
        return m.group(1), m.group(2)
    return item, ""


def parse_level3(sec3a: str) -> dict[tuple[str, str], list[tuple[str, str]]]:
    """(Level 1, Level 2) -> [(Level 3 leaf, gloss), ...] in scheme order."""
    out: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for line in sec3a.splitlines():
        if not line.startswith("- "):
            continue
        parts = line[2:].split(" > ")
        if len(parts) != 3 or parts[0] not in L1_NAMES:
            continue
        l1, l2, rest = parts[0], parts[1].strip(), parts[2]
        items = [x.strip() for x in rest.split(" · ")]
        expanded: list[str] = []
        for k, it in enumerate(items):
            if it in ("…", "..."):
                prev, nxt = items[k - 1], items[k + 1]
                mp = re.fullmatch(r"(.*)\(([A-Z])\)(.*)", prev)
                mn = re.fullmatch(r"(.*)\(([A-Z])\)(.*)", nxt)
                if not (mp and mn and mp.group(1) == mn.group(1)):
                    raise RuntimeError(f"cannot expand the ellipsis in: {line}")
                for c in range(ord(mp.group(2)) + 1, ord(mn.group(2))):
                    expanded.append(f"{mp.group(1)}({chr(c)}){mp.group(3)}")
            else:
                expanded.append(it)
        out[(l1, l2)] = [_split_level3_item(it) for it in expanded]
    return out


def parse_level1_definitions(sec2: str) -> dict[str, str]:
    """'1. Planning — introduces ...' -> {'Planning': 'introduces ...'} (first sentences only;
    the Knowledge item is cut before its naming discussion)."""
    defs: dict[str, str] = {}
    for line in sec2.splitlines():
        m = re.match(r"^\d+\. (%s) — (.+)$" % "|".join(L1_NAMES), line)
        if m:
            text = m.group(2)
            for marker in (" ReasoningFlow calls this label Fact", " Test:"):
                cut = text.find(marker)  # the naming discussion; the test (Section 4 gives it)
                if cut > 0:
                    text = text[:cut]
            defs[m.group(1)] = text.strip()
    if set(defs) != set(L1_NAMES):
        raise RuntimeError(f"Section 2 definitions found for {sorted(defs)} only")
    return defs


def parse_applicability_tests(sec4: str) -> dict[str, str]:
    """'- Conclusion applies if ...' -> {'Conclusion': 'Conclusion applies if ...'}"""
    tests: dict[str, str] = {}
    for line in sec4.splitlines():
        m = re.match(r"^- (%s) applies if .+$" % "|".join(L1_NAMES), line)
        if m:
            tests[m.group(1)] = line[2:].strip()
    if set(tests) != set(L1_NAMES):
        raise RuntimeError(f"Section 4 tests found for {sorted(tests)} only")
    return tests


def item_prompt(summary_text: str) -> str:
    """The verbatim item prompt: the first fenced block of action summary Section 4."""
    sec4 = section(summary_text, "## 4. ")
    m = re.search(r"```\n(.*?)\n```", sec4, re.S)
    if not m:
        raise RuntimeError("no fenced item prompt in action summary Section 4")
    return m.group(1).strip("\n")


# ----------------------------------------------------------------------------
# Codes
# ----------------------------------------------------------------------------

def _words(name: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Za-z]+", name)]


def base_code(name: str) -> str:
    m = re.fullmatch(r"(?:option )?\(([A-Z])\)", name)
    if m:
        return m.group(1)
    words = _words(name)
    if not words:
        raise ValueError(f"no letters in leaf name {name!r}")
    if len(words) == 1:
        return words[0][:2]
    return "".join(w[0] for w in words[:3])


def extension_letters(name: str) -> list[str]:
    """The consonants of the leaf's words after each word's first letter, word by word."""
    out = []
    for w in _words(name):
        out.extend(c for c in w[1:] if c not in VOWELS)
    return out


def assign_codes(names: list[str]) -> dict[str, str]:
    """Unique codes for sibling leaves, in the given (scheme) order."""
    taken: set[str] = set()
    codes: dict[str, str] = {}
    for name in names:
        code = base_code(name)
        if code in taken:
            for c in extension_letters(name):
                if code not in taken:
                    break
                code += c
            if code in taken:
                raise RuntimeError(f"cannot make a unique code for {name!r} among {sorted(taken)}")
        taken.add(code)
        codes[name] = code
    return codes


def build_inventory(scheme_text: str) -> list[dict]:
    """[{'code', 'path', 'gloss'}] for every allowed path, in scheme order."""
    sec3 = section(scheme_text, "## 3. ")
    sec3a = section(scheme_text, "## 3a. ")
    leaves2, defs2 = parse_level2(sec3)
    leaves3 = parse_level3(sec3a)
    for key in leaves3:
        if key[1] not in leaves2[key[0]]:
            raise RuntimeError(f"Section 3a leaf under unknown Level 2 leaf: {key}")
    inventory: list[dict] = []
    for l1 in L1_NAMES:
        codes2 = assign_codes(leaves2[l1])
        for l2 in leaves2[l1]:
            inventory.append({"code": f"{L1_CODE[l1]}.{codes2[l2]}", "path": [l1, l2],
                              "gloss": defs2.get((l1, l2), "")})
            if (l1, l2) in leaves3:
                names3 = [n for n, _ in leaves3[(l1, l2)]]
                codes3 = assign_codes(names3)
                for l3, gloss in leaves3[(l1, l2)]:
                    inventory.append({"code": f"{L1_CODE[l1]}.{codes2[l2]}.{codes3[l3]}",
                                      "path": [l1, l2, l3], "gloss": gloss})
    codes = [e["code"] for e in inventory]
    if len(set(codes)) != len(codes):
        raise RuntimeError("duplicate codes in the inventory")
    return inventory


# ----------------------------------------------------------------------------
# Decision 6: replacements of trace quotes (old text in the scheme -> new text)
# ----------------------------------------------------------------------------

SUBSTITUTIONS: list[tuple[str, str, str]] = [
    # (where, old, new)
    ("Section 4, Planning test", '("Does Bat > Ball?", "Is the sum $1.10?")',
     '("Is 47 less than 48?", "Does doubling 24 give 48?")'),
    ("Section 4, Planning test", "(\"Could 'A bat' mean a specific bat?\")",
     "(\"Could 'the lake' mean only its surface?\")"),
    ("Section 4, Planning test", '("A ball for $0.01?")', '("A crossing in two hours?")'),
    ("Section 4, Planning test", '("Is (C) technically correct?")', '("Is (B) exactly right?")'),
    ("Section 4, Planning test", "(\"Is Option (C) the 'Best' option?\")",
     '("Is option (B) really the best choice?")'),
    ("Section 4, Planning test", '("Is there a linguistic trick?", "What if the answer is (F)?")',
     '("Is there a trick in the wording?", "What if the answer is (D)?")'),
    ("Section 4, Planning test", " Self-question rule (Kian, 2026-09-15):", " Self-question rule:"),
    ("Section 4, Planning test",
     " Applied on 2026-09-15 to 21 C-trace and 4 E-trace sentences (listing v2, change record).", ""),
    ("Section 4, Planning test", " and opens a block by R1.", " and opens a block (see the note on blocks below)."),
    ("Section 3, self-knowledge definition",
     '("as an AI, I must address the prompt as written"; "LLMs are evaluated on their ability to follow instructions")',
     '("as a language model I have to answer the text in front of me"; "assistants are graded on following the instructions exactly")'),
    ("Section 3, self-knowledge definition",
     " Decided by Kian 2026-09-14 (item 4) in place of the earlier Reflection > self-role identification.", ""),
    ("Section 3, announce output definition",
     '("Output Generation.", "[Output] -> Proceeds", "Ready.", "I\'ll write it out clearly.")',
     '("Writing the reply now.", "[Response] -> begin", "Go.", "Time to put this into words.")'),
    ("Section 3, announce output definition", " Observed 16 times in the E-trace tail, never in the C-trace.", ""),
    ("Section 3, comparison definition", ' (Kian\'s "Reasoning + Knowledge > comparison")', ""),
    ("Section 3, hedge word analysis definition",
     "; these leaves are the two readings of direction (1/3) of the research plan", ""),
]


def apply_substitutions(text: str, where: str) -> str:
    for w, old, new in SUBSTITUTIONS:
        if w == where:
            if old not in text:
                raise RuntimeError(f"substitution source not found in {where}: {old!r}")
            text = text.replace(old, new)
    return text


# ----------------------------------------------------------------------------
# Glosses for leaves the scheme does not define in a sentence of its own (written here)
# ----------------------------------------------------------------------------

OWN_GLOSSES: dict[tuple[str, ...], str] = {
    ("Planning", "global plan"): "sets the overall direction or announces a major phase of the work",
    ("Planning", "initiate verification"): "announces a check of something already done",
    ("Planning", "initiate backtracking"): "announces abandoning or redoing an earlier path",
    ("Planning", "local plan"): "the next small step: a step label with a colon, a series item, a bullet label",
    ("Planning", "announce the conclusion"): "announces that the answer follows",
    ("Planning", "unspecified"): "Planning that fits no other leaf",
    ("Reasoning", "calculation"): "arithmetic or algebra on stated quantities",
    ("Reasoning", "logical reasoning"): "a deduction from earlier sentences (including the one-word answer to a self-question)",
    ("Reasoning", "commonsense reasoning"): "an inference from everyday plausibility",
    ("Reasoning", "speculation"): "a guess about something not derivable from the text",
    ("Reasoning", "defining symbols"): "introduces variables or notation",
    ("Reasoning", "observation from examples"): "a pattern read off listed cases",
    ("Reasoning", "unspecified"): "Reasoning that fits no other leaf",
    ("Reflection", "meta-evaluation of a step"): "judges an earlier step or an option (fits, seems wrong, is clean)",
    ("Reflection", "emotion or impression"): "a feeling or impression about the problem or the progress",
    ("Reflection", "rhetorical phrase"): "a phrase that carries no content of its own",
    ("Reflection", "filler"): "words that only fill space",
    ("Reflection", "applicability of a knowledge item"): "judges whether a recalled fact applies here",
    ("Reflection", "unspecified"): "Reflection that fits no other leaf",
    ("Knowledge", "rule or theorem"): "a general rule or theorem brought in from memory",
    ("Knowledge", "concept or definition"): "a definition or concept brought in from memory",
    ("Knowledge", "constant or unit"): "a constant, unit or conversion brought in from memory",
    ("Knowledge", "world knowledge"): "a fact about the world outside the prompt, true or not",
    ("Knowledge", "commonsense"): "an everyday fact everyone knows",
    ("Knowledge", "unspecified"): "Knowledge that fits no other leaf",
    ("Restatement", "rephrasing the prompt"): "repeats or paraphrases the prompt with nothing new added",
    ("Restatement", "rephrasing an earlier sentence"): "repeats or paraphrases an earlier sentence of the trace",
    ("Restatement", "unspecified"): "Restatement that fits no other leaf",
    ("Assumption", "assuming a missing premise by common practice"): "supplies a premise the prompt lacks because it is the usual one",
    ("Assumption", "assuming an uncertain fact"): "takes an uncertain fact as given for what follows",
    ("Assumption", "branching (case split)"): "opens a case ('If X, then ...') that later sentences work inside",
    ("Assumption", "proof by contradiction"): "assumes the opposite in order to refute it",
    ("Assumption", "unspecified"): "Assumption that fits no other leaf",
    ("Example", "pattern induction by enumeration"): "lists cases in order to find a pattern",
    ("Example", "non-exhaustive listing"): "lists some instances without claiming completeness",
    ("Example", "rhetorical example"): "an example given for effect, not for the solution",
    ("Example", "unspecified"): "Example that fits no other leaf",
    ("Conclusion", "intermediate conclusion"): "answers the question in substance or names an option, before the final answer",
    ("Conclusion", "final answer"): "the final answer or its announcement in the answer format",
    ("Reasoning", "defining symbols", "algebra"): "symbols for the quantities of the item",
    ("Reasoning", "comparison", "prompt vs original text"): "this prompt against the original riddle",
    ("Reasoning", "comparison", "option vs option"): "one option against another",
    ("Reasoning", "speculation", "intent of the question writer"): "what the writer of the question meant or wanted",
    ("Reasoning", "hedge word analysis", "undecided"): "weighs the readings of the hedge word without adopting one",
    ("Knowledge", "self-knowledge", "role"): "what the model is or must do because of what it is",
    ("Knowledge", "self-knowledge", "evaluation context"): "how the model is evaluated",
    ("Assumption", "assuming a missing premise by common practice", '"$1.00 more"'): "the premise of the classic riddle that this prompt omits",
    ("Example", "non-exhaustive listing", "algebra"): "listed value pairs for the item",
    ("Restatement", "rephrasing the prompt", "question text"): "the question",
    ("Restatement", "rephrasing the prompt", "option text"): "an option quoted or paraphrased",
    ("Restatement", "rephrasing the prompt", "answer-format instruction"): "the instruction on the reply format",
}


def gloss_for(entry: dict) -> str:
    """The one-line gloss: the scheme's definition or parenthetical (with decision-6 replacements),
    else a gloss of this script."""
    path = tuple(entry["path"])
    g = entry["gloss"]
    if len(path) == 2 and g:
        where = f"Section 3, {path[1]} definition"
        try:
            g = apply_substitutions(g, where)
        except RuntimeError:
            pass
        g = g[0].lower() + g[1:] if g else g
        return g.rstrip(".")
    if len(path) == 3 and g:
        # a Level 3 gloss is cut at its first semicolon or colon: what follows is an aside or a
        # list of trace examples (decision 6), e.g. the logical reasoning > algebra leaf of v5
        return re.split(r"[;:]", g)[0].strip()
    if len(path) == 3 and re.fullmatch(r"(?:option )?\([A-F]\)", path[2]):
        letter = re.search(r"\(([A-F])\)", path[2]).group(1)
        return f"about option ({letter})"
    if path in OWN_GLOSSES:
        return OWN_GLOSSES[path]
    raise RuntimeError(f"no gloss for {path}")


# ----------------------------------------------------------------------------
# Worked examples (different problems, never bat and ball)
# ----------------------------------------------------------------------------

EXAMPLES: list[dict] = [
    {
        "title": "Example 1 (lily pads): a Planning node followed by Reasoning, an intermediate conclusion, a verification",
        "context": "A patch of lily pads doubles in size every day and covers the whole lake on day 48. On which day did it cover half the lake?",
        "sentences": [
            "Here is my plan: restate the rule, then work backwards from day 48.",
            "Step 1: the doubling rule.",
            "Doubling every day means the patch on day 47 was half of the patch on day 48.",
            "So half the lake was covered on day 47.",
            "The answer is day 47.",
            "Let me double-check by going forwards instead:",
            "Half the lake on day 47, doubled once, is the whole lake on day 48.",
        ],
        "expected": "0 Pl.gp\n1 Pl.lp\n2-3 Re.lr\n4 Co.ic\n5 Pl.iv\n6 Re.ca",
    },
    {
        "title": "Example 2 (train): a self-question and its one-word answer inside one Reasoning run, a combined sentence, an intermediate and a final conclusion",
        "context": "A train leaves at 9:00 and travels at 60 km per hour. When does it reach a station 150 km away?",
        "sentences": [
            "Compute the travel time first.",
            "Time = distance / speed = 150 / 60 = 2.5 hours.",
            "Is 2.5 hours the same as 2 hours and 30 minutes?",
            "Yes.",
            "So the train arrives at 11:30, taking the usual reading that it never stops on the way.",
            "Wait, was the departure 9:00 or 9:30?",
            "The prompt says 9:00.",
            "Final answer: 11:30.",
        ],
        "expected": "0 Pl.lp\n1 Re.ca\n2-3 Re.lr\n4 Co.ic+As.aam\n5 Pl.iv\n6 Rs.rtp.qt\n7 Co.fa",
    },
    {
        "title": "Example 3 (lily pads with options): Knowledge, an Example, a Reflection, option evaluation, the final answer",
        "context": "Same puzzle, with options (A) day 24, (B) day 47, (C) cannot be determined, (D) none of the above.",
        "sentences": [
            "This is the well-known lily-pad puzzle from the cognitive reflection test.",
            "The intuitive answer is day 24, but that ignores the doubling.",
            "For instance, a patch of 1 unit on day 1 is 2 units on day 2 and 4 units on day 3.",
            "That checks out nicely.",
            "Option (A) is the trap answer.",
            "Option (B) matches the computation.",
            "Answer: B.",
        ],
        "expected": "0 Kn.wk\n1 Re.lr\n2 Ex.nel\n3 Rf.meo\n4 Re.oe.A\n5 Re.oe.B\n6 Co.fa",
    },
]


EXAMPLES_V2: list[dict] = [
    {
        "title": "Example 1 (lily pads): a numbered heading, a nested item, an intermediate conclusion, a verification and its judgement",
        "context": "A patch of lily pads doubles in size every day and covers the whole lake on day 48. On which day did it cover half the lake?",
        "sentences": [
            "1.",
            "**Set up the rule:**",
            "- Given:",
            "the patch doubles every day and covers the lake on day 48.",
            "Doubling every day means the patch on day 47 was half of the patch on day 48.",
            "So half the lake was covered on day 47.",
            "Let me double-check by going forwards instead:",
            "Half the lake on day 47, doubled once, is the whole lake on day 48.",
            "That checks out.",
        ],
        "expected": "0-1 Pl.gp\n2 Pl.lp\n3 Rs.rtp.qt\n4 Re.lr\n5 Co.ic\n6 Pl.iv\n7 Re.ca\n8 Rf.meo",
    },
    {
        "title": "Example 2 (train): a branching sentence, a self-question and its one-word answer inside one Reasoning run, a combined sentence, an intermediate and a final conclusion",
        "context": "A train leaves at 9:00 and travels at 60 km per hour. When does it reach a station 150 km away?",
        "sentences": [
            "Compute the travel time first.",
            "If the train keeps exactly 60 km per hour,",
            "then time = distance / speed = 150 / 60 = 2.5 hours.",
            "Is 2.5 hours the same as 2 hours and 30 minutes?",
            "Yes.",
            "So the train arrives at 11:30, taking the usual reading that it never stops on the way.",
            "Wait, was the departure 9:00 or 9:30?",
            "The prompt says 9:00.",
            "Final answer: 11:30.",
        ],
        "expected": "0 Pl.lp\n1 As.bcs\n2 Re.ca\n3-4 Re.lr\n5 Co.ic+As.aam\n6 Pl.iv\n7 Rs.rtp.qt\n8 Co.fa",
    },
    {
        "title": "Example 3 (lily pads with options): Knowledge, an Example, an argued option evaluation, verdict tags, a drafted reply that restates an earlier equation, the final answer, announce output",
        "context": "Same puzzle, with options (A) day 24, (B) day 47, (C) cannot be determined, (D) none of the above.",
        "sentences": [
            "This is the well-known lily-pad puzzle from the cognitive reflection test.",
            "The intuitive answer is day 24, but that ignores the doubling.",
            "For instance, a patch of 1 unit on day 1 is 2 units on day 2 and 4 units on day 3.",
            "Halving the full lake once: 48 - 1 = 47.",
            "Option (B) is right because it is the only option equal to 47.",
            "(A) day 24 — Incorrect.",
            "(C) cannot be determined — Incorrect.",
            "Draft reply:",
            "The lake is half covered one day before it is full: 48 - 1 = 47.",
            "Answer: B.",
            "Writing it out now.",
        ],
        "expected": "0 Kn.wk\n1 Re.lr\n2 Ex.nel\n3 Re.ca\n4 Re.oe.B\n5 Rf.meo.A\n6 Rf.meo.C\n7 Pl.gp\n8 Rs.rae\n9 Co.fa\n10 Pl.ao",
    },
]


def examples_for(version: str) -> list[dict]:
    return EXAMPLES if version == "v1" else EXAMPLES_V2


def example_input(ex: dict) -> str:
    return "\n".join(f"s{i}: {s}" for i, s in enumerate(ex["sentences"]))


def additional_rules_v2() -> list[str]:
    """The v2 rules (Kian, 2026-09-16), each a bullet of Section 3; illustrated only with
    sentences on other problems."""
    return [
        "- Combined sentences: a sentence carries two labels only when it does two things at once, so that two applicability tests pass; the two labels have different Level 1 parts. "
        "Three kinds occur: a plan attached to a quote (the sentence announces a check and begins quoting in the same breath); a plan phrased as a speculation (the sentence announces a check and states the hypothesis being checked); "
        "a true double function (a calculation that silently supplies a missing premise; an option judgment that also interprets a hedge word). Never more than two labels. Most sentences carry one.",
        "- Headings and series structure: a top-level numbered heading of the trace — the bare marker (\"1.\", \"2.\") and the heading text that follows it, often bold and ending with a colon — is Planning > global plan: it announces a phase. "
        "Items nested under a heading (\"- Given:\", \"Step 1:\", \"(B) day 47:\", \"   - compute the time\", a bullet that names the next small action) and step labels with a colon inside a derivation (\"Substitute t:\", \"Check:\", \"As stated:\") are Planning > local plan. "
        "A bare number or bullet marker split off by the splitter (\"1.\", \"2.\", a lone \"-\" or \"*\") is not a plan of its own: it attaches to the sentence that follows it and takes that sentence's label, whatever it is.",
        "- Restatement > rephrasing an earlier sentence: the sentence repeats or paraphrases something already established earlier in the trace — an equation already written, a comparison already made, the plan, a conclusion already reached — and adds no new inference. "
        "Deletion test: if removing the sentence loses no information that an earlier sentence did not already give, it is Restatement, whatever it looks like (an equation, a verdict, a summary). "
        "When the trace composes its reply (drafts the answer, lists what the reply will contain, writes the reply out), most sentences are restatements of earlier work; label them so unless they add something new. "
        "Quoting or paraphrasing the question or an option is Restatement > rephrasing the prompt (> question text / option text / answer-format instruction), never option evaluation.",
        "- Assumption > branching (case split): a sentence, often a fragment ending in a comma, that posits a case or a hypothetical value to work through (\"If x = 5,\", \"Suppose the pond is a square,\") — even when it contains an equation. "
        "The computation that follows is Reasoning > calculation; the case sentence itself is Assumption > branching (> algebra when the case is on a value).",
        "- Reasoning > option evaluation is only for a sentence that argues whether an option is correct, acceptable or best. A bare verdict attached to an option in a checklist (\"(B) day 47 — Incorrect.\", \"(D) cannot be determined — Vague.\") is Reflection > meta-evaluation of a step > option (X). "
        "A sentence quoting an option's text is Restatement > rephrasing the prompt > option text. A sentence about what the question writer intended is Reasoning > speculation > intent of the question writer. "
        "Setting two options against each other is Reasoning > comparison > option vs option. The appearance of an option letter never by itself makes a sentence option evaluation.",
        "- Reflection: emotion or impression is a feeling about the problem or the progress (\"This is tricky.\", \"Nice.\"). A judgement about the correctness, completeness or consistency of a step, of the draft or of the output (\"All steps check out.\", \"The draft matches the reasoning.\", \"Output matches.\") is meta-evaluation of a step. "
        "Planning > announce output covers the go-ahead words and sentences that say the reply is now being written (\"Proceed.\", \"Ready.\", \"Done — writing it out.\", \"I'll send exactly this text.\") — never emotion.",
        "- Conclusion: a sentence that states a settled result of the reasoning so far (\"Therefore …\", \"So the value is not fixed.\", \"The problem is underdetermined.\") is Conclusion > intermediate conclusion, not logical reasoning; the inference steps before it are Reasoning. "
        "Conclusion > final answer is only the statement of the answer at the very end of the trace (the last time it is given); every earlier statement of the answer, including \"Answer:\" lines and the answer letter inside a drafted reply, is intermediate conclusion. "
        "A bare \"Answer:\" line or a bare letter inside the draft takes the same label as the answer statement it belongs to.",
        "- One-word answers: the one-word answer to a self-question (\"Yes.\", \"No.\", \"Unlikely.\") is Reasoning > logical reasoning, and the question takes the same leaf as its answer, so both are Reasoning > logical reasoning and fall into one run (with the Level 3 leaf algebra when the check is about the item's equations).",
        "- Labeling order, applied to every sentence in this sequence, first match wins: (1) a marker, heading or plan item → Planning; (2) an announcement that the reply is being written → Planning > announce output; "
        "(3) repeats earlier content → Restatement > rephrasing an earlier sentence; (4) repeats the question, an option or the format instruction → Restatement > rephrasing the prompt; (5) posits a case or an assumption → Assumption; "
        "(6) states a settled result → Conclusion; (7) judges the trace's own work → Reflection; (8) states a fact from outside the problem → Knowledge; (9) gives instances → Example; "
        "(10) otherwise Reasoning, with the finest leaf that fits and logical reasoning as the default — never option evaluation by default.",
        "- Sentences are never re-split or merged: label each numbered sentence as it is, even a fragment, a heading, a number or a closing parenthesis.",
        "- For information only (you do not output blocks): the analysis derives blocks from your labels. A block opens at the first sentence of a Planning node unless every sentence of that node is Planning > local plan, at a sentence carrying Assumption > branching (case split), and at a sentence carrying Conclusion > final answer. "
        "This is why the distinction between global plan, initiate verification, initiate backtracking, announce the conclusion, announce output on one side and local plan on the other matters.",
    ]


# ----------------------------------------------------------------------------
# The prompt
# ----------------------------------------------------------------------------

def build_prompt(scheme_text: str, summary_text: str, inventory: list[dict], version: str = "v1") -> str:
    if version not in VERSIONS:
        raise ValueError(f"unknown prompt version {version!r}")
    defs1 = parse_level1_definitions(section(scheme_text, "## 2. "))
    tests = parse_applicability_tests(section(scheme_text, "## 4. "))
    tests["Planning"] = apply_substitutions(tests["Planning"], "Section 4, Planning test")
    codes = {e["code"] for e in inventory}
    for ex in examples_for(version):
        for line in ex["expected"].splitlines():
            for c in line.split()[1].split("+"):
                if c not in codes:
                    raise RuntimeError(f"worked example uses a code outside the inventory: {c}")
    item = item_prompt(summary_text)
    p: list[str] = []
    p.append(f"# Judge prompt {version} — sentence labeling of reasoning traces")
    p.append("")
    p.append(SECTION_TITLES[0])
    p.append("")
    p.append("You will receive the thinking trace of a language model, already split into numbered sentences, and you label every sentence with the labeling scheme below. "
             "Reply with the label codes only, in the run-length format of Section 6, nothing else.")
    p.append("")
    p.append(SECTION_TITLES[1])
    p.append("")
    p.append("Every trace reasons about the following item, which the model received verbatim (the six answer options (A) to (F) are the options that the option leaves of Section 4 refer to):")
    p.append("")
    p.append("```")
    p.append(item)
    p.append("```")
    p.append("")
    p.append(SECTION_TITLES[2])
    p.append("")
    p.append("Eight Level 1 labels, frozen. A label is a path Level 1 > Level 2 [> Level 3]; Level 2 is mandatory, Level 3 is used where the code table of Section 4 offers it and the sentence fits the leaf. "
             "The applicability tests decide which Level 1 label applies; no test outranks another.")
    p.append("")
    for k, (name, code) in enumerate(LEVEL1, start=1):
        p.append(f"{k}. {name} ({code}) — {defs1[name]}")
        p.append(f"   Test: {tests[name]}")
    p.append("")
    p.append("Additional rules:")
    if version == "v2":
        p.extend(additional_rules_v2())
    else:
        p.extend(additional_rules_v1())
    p.append("")
    p.append(SECTION_TITLES[3])
    p.append("")
    p.append("One line per allowed path: `code — Level 1 > Level 2 [> Level 3] — gloss`. A path may stop at Level 2 (for example `Re.ca` when the calculation is not about the item's algebra). Level 1 alone is never a label.")
    p.append("")
    for e in inventory:
        p.append(f"{e['code']} — {' > '.join(e['path'])} — {gloss_for(e)}")
    p.append("")
    p.append(SECTION_TITLES[4])
    p.append("")
    p.append("After this prompt comes the whole trace, one line per sentence, in order:")
    p.append("")
    p.append("```")
    p.append("s0: <text of sentence 0>")
    p.append("s1: <text of sentence 1>")
    p.append("...")
    p.append("```")
    p.append("")
    p.append(f"The mark {NEWLINE_MARK} inside a text stands for a line break of the original trace (a sentence may begin with one or more of them); leading spaces after a mark are part of the original indentation. "
             "Labels depend on context: read the whole trace before labeling.")
    p.append("")
    p.append(SECTION_TITLES[5])
    p.append("")
    p.append("Plain text only. One line per run of consecutive sentences that carry the same label:")
    p.append("")
    p.append("- `<first>-<last> <code>` for a run of two or more sentences (for example `15-22 Re.ca.al`), `<first> <code>` for a single sentence (`23 Co.ic`);")
    p.append("- a combined sentence on its own line as `<index> <codeA>+<codeB>` (`12 Re.co.pvo+Kn.wk`);")
    p.append("- runs in increasing order, covering every index from 0 to the last sentence exactly once, no gaps, no overlaps;")
    p.append("- codes exactly as in Section 4; no prose, no blank lines, no code fences, no headings, nothing before the first line or after the last.")
    p.append("")
    p.append(SECTION_TITLES[6])
    p.append("")
    p.append("Each example shows a short trace on a different problem, the numbered input and the exact expected output. "
             "The Level 3 leaves of Section 4 belong to the bat-and-ball item, so these examples stop at Level 2 where a leaf would be item-specific; on a real trace, use the Level 3 leaf whenever the sentence fits it.")
    for ex in examples_for(version):
        p.append("")
        p.append(f"### {ex['title']}")
        p.append("")
        p.append(f"Problem: {ex['context']}")
        p.append("")
        p.append("Input:")
        p.append("")
        p.append("```")
        p.append(example_input(ex))
        p.append("```")
        p.append("")
        p.append("Expected output:")
        p.append("")
        p.append("```")
        p.append(ex["expected"])
        p.append("```")
    p.append("")
    prompt = "\n".join(p)
    for _, old, _ in SUBSTITUTIONS:
        if old and old in prompt:
            raise RuntimeError(f"decision 6: replaced text still present in the prompt: {old!r}")
    return prompt


def additional_rules_v1() -> list[str]:
    """The v1 bullets of Section 3, byte for byte as first published."""
    p: list[str] = []
    p.append("- Combined sentences: a sentence carries two labels only when it does two things at once, so that two applicability tests pass; the two labels have different Level 1 parts. "
             "Three kinds occur: a plan attached to a quote (the sentence announces a check and begins quoting in the same breath); a plan phrased as a speculation (the sentence announces a check and states the hypothesis being checked); "
             "a true double function (a calculation that silently supplies a missing premise; an option judgment that also interprets a hedge word). Never more than two labels. Most sentences carry one.")
    p.append("- One-word answers: the one-word answer to a self-question (\"Yes.\", \"No.\", \"Unlikely.\") is Reasoning > logical reasoning, and the question takes the same leaf as its answer, so both are Reasoning > logical reasoning and fall into one run (with the Level 3 leaf algebra when the check is about the item's equations).")
    p.append("- Announce output: a sentence that announces that the reply is being produced (\"Writing the reply now.\", \"[Response] -> begin\", \"Go.\") is Planning > announce output, not Conclusion.")
    p.append("- Local plans: a step label with a colon inside a derivation (\"Step 1:\", \"Substitute t:\", \"Check:\", \"As stated:\") and an item of a labeled or bulleted series under a heading (\"(A) day 24:\", \"1. Define the variables:\", \"- Given:\", \"- Compare the two readings of the puzzle.\") are Planning > local plan. "
             "A bare number or bullet marker split off by the splitter (\"1.\", \"2.\", a lone \"-\" or \"*\") is not a plan of its own: it attaches to the sentence that follows it and takes that sentence's label, whatever it is.")
    p.append("- Restatement: quoting an option verbatim before evaluating it is Restatement > rephrasing the prompt > option text; quoting the question is > question text.")
    p.append("- Sentences are never re-split or merged: label each numbered sentence as it is, even a fragment, a heading, a number or a closing parenthesis.")
    p.append("- For information only (you do not output blocks): the analysis derives blocks from your labels. A block opens at the first sentence of a Planning node unless every sentence of that node is Planning > local plan, at a sentence carrying Assumption > branching (case split), and at a sentence carrying Conclusion > final answer. "
             "This is why the distinction between global plan, initiate verification, initiate backtracking, announce the conclusion, announce output on one side and local plan on the other matters.")
    return p


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pipeline step (3/9): generate the judge prompt and the label codes.")
    ap.add_argument("--out-dir", default=str(PROMPTS_DIR), help="folder for the three output files (default prompts/)")
    ap.add_argument("--version", default="v1", choices=VERSIONS, help="prompt version to write (default v1)")
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    version = args.version
    scheme_text = SCHEME.read_text(encoding="utf-8")
    summary_text = SUMMARY.read_text(encoding="utf-8")
    inventory = build_inventory(scheme_text)
    prompt = build_prompt(scheme_text, summary_text, inventory, version)
    scheme_sha = sha256_of_file(SCHEME)
    labels = {
        "version": version,
        "scheme": SCHEME.name,
        "scheme_sha256": scheme_sha,
        "level1": {code: name for name, code in LEVEL1},
        "paths": [{"code": e["code"], "path": e["path"]} for e in inventory],
    }
    prompt_path, labels_path, meta_path = prompt_paths(version, out_dir)
    prompt_path.write_text(prompt + "\n", encoding="utf-8", newline="\n")
    with open(labels_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(labels, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    meta = {
        "prompt_file": prompt_path.name,
        "labels_file": labels_path.name,
        "characters": len(prompt) + 1,
        "estimated_tokens": round((len(prompt) + 1) / 4),
        "paths": len(inventory),
        "scheme": SCHEME.name,
        "scheme_sha256": scheme_sha,
        "summary": SUMMARY.name,
        "summary_sha256": sha256_of_file(SUMMARY),
        "script": Path(__file__).resolve().relative_to(REPO).as_posix(),
        "script_sha256": sha256_of_file(Path(__file__).resolve()),
        "git_commit": git_head(),
        "generated": datetime.now().isoformat(timespec="seconds"),
    }
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"s1a_make_prompt: scheme={SCHEME.name} sha256={scheme_sha[:12]} paths={len(inventory)} "
          f"prompt={prompt_path} characters={meta['characters']} est_tokens={meta['estimated_tokens']} git={meta['git_commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
