"""
solver.py — 𝐖ᴏʀᴅ𝐒ᴇᴇᴋ Smart Solver
Entropy-based algorithm: picks guess that splits remaining
candidates most evenly → wins in fewest attempts.
"""

import json
import os
import math
from typing import List, Tuple, Dict, Optional

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Words")

# ── Best opening words (pre-researched, high letter coverage) ──
STARTERS: Dict[int, str] = {
    4: "rate",    # R, A, T, E — 4 very common letters
    5: "slate",   # S, L, A, T, E — top 5-letter opener
    6: "clears",  # C, L, E, A, R, S — covers 6 common letters
}

# ── Second guess if starter gives little info ──
SECOND: Dict[int, str] = {
    4: "noun",
    5: "crony",
    6: "bounty",
}


# ═══════════════════════════════════════════════
#  Word Loading
# ═══════════════════════════════════════════════

def load_words(mode: int) -> Tuple[List[str], List[str]]:
    """
    Returns (common_words, all_words) for the given letter count.
    common_words = likely answers
    all_words    = valid guesses (much larger list)
    """
    size = {4: "four", 5: "five", 6: "six"}.get(mode, "five")
    with open(os.path.join(BASE, f"common-{size}.json")) as f:
        common = json.load(f)
    with open(os.path.join(BASE, f"all-{size}.json")) as f:
        all_w = json.load(f)
    return common, all_w


def load_candidates(mode: int) -> List[str]:
    """Returns just the common (likely answer) word list."""
    common, _ = load_words(mode)
    return common


# ═══════════════════════════════════════════════
#  Pattern Engine  (handles duplicate letters correctly)
# ═══════════════════════════════════════════════

def get_pattern(guess: str, answer: str) -> Tuple[str, ...]:
    """
    Simulate what pattern WordSeek would show for guess vs answer.
    G = green  (right letter, right position)
    Y = yellow (right letter, wrong position)
    R = grey   (letter not in remaining answer)

    Duplicate-letter aware — mirrors Wordle rules exactly.
    """
    n = len(guess)
    pattern = ["R"] * n
    pool = list(answer)  # tracks unmatched answer letters

    # Pass 1 — greens
    for i in range(n):
        if guess[i] == answer[i]:
            pattern[i] = "G"
            pool[i] = None          # consumed

    # Pass 2 — yellows
    for i in range(n):
        if pattern[i] == "G":
            continue
        if guess[i] in pool:
            pattern[i] = "Y"
            pool[pool.index(guess[i])] = None   # consume one

    return tuple(pattern)


# ═══════════════════════════════════════════════
#  Candidate Filter
# ═══════════════════════════════════════════════

def filter_words(words: List[str], guesses: List[Tuple]) -> List[str]:
    """
    Eliminate words that are inconsistent with guess history.
    guesses: list of (word, pattern)  — pattern is list/tuple of G/Y/R
    """
    remaining = words[:]
    for guess_word, pattern in guesses:
        pat = tuple(pattern)
        remaining = [w for w in remaining if get_pattern(guess_word, w) == pat]
    return remaining


# ═══════════════════════════════════════════════
#  Entropy Scorer  (core of the smart solver)
# ═══════════════════════════════════════════════

def entropy_score(guess: str, candidates: List[str]) -> float:
    """
    How much information does this guess give us?
    = Shannon entropy of the distribution of patterns it produces.

    Higher score → guess splits candidates more evenly → better guess.
    """
    if not candidates:
        return 0.0

    counts: Dict[tuple, int] = {}
    for c in candidates:
        pat = get_pattern(guess, c)
        counts[pat] = counts.get(pat, 0) + 1

    n = len(candidates)
    entropy = 0.0
    for cnt in counts.values():
        p = cnt / n
        entropy -= p * math.log2(p)

    return entropy


# ═══════════════════════════════════════════════
#  Best Guess Picker
# ═══════════════════════════════════════════════

def best_guess(
    common: List[str],
    all_words: List[str],
    guesses: List[Tuple],
    attempt: int = 0,
) -> str:
    """
    Pick optimal next word.

    Strategy:
      attempt 0 → use hardcoded STARTER (fast + pre-optimised)
      attempt 1 → if candidates still large, use SECOND starter
      otherwise → entropy-rank remaining candidates, pick best
                  (prefer candidates over non-candidates)
    """
    mode = len(common[0]) if common else 5

    # ── Attempt 0: always use the starter ──
    if attempt == 0:
        return STARTERS.get(mode, "slate")

    # ── Filter remaining candidates ──
    candidates = filter_words(common, guesses)

    # ── No candidates left? Try all_words ──
    if not candidates:
        candidates = filter_words(all_words, guesses)

    if not candidates:
        return STARTERS.get(mode, "slate")

    # ── 1 or 2 left: just guess the first one ──
    if len(candidates) <= 2:
        return candidates[0]

    # ── attempt 1 + big pool: sometimes better to use a diversity word ──
    if attempt == 1 and len(candidates) > 20:
        second = SECOND.get(mode)
        if second and second not in [g[0] for g in guesses]:
            return second

    # ── Entropy ranking ──
    # Score top candidates (cap at 100 for speed on first few guesses)
    score_pool = candidates[:100]
    best_word = candidates[0]
    best_score = -1.0

    for word in score_pool:
        score = entropy_score(word, candidates)
        # Tiny tiebreak: prefer candidates (could literally be the answer)
        score += 0.05
        if score > best_score:
            best_score = score
            best_word = word

    # Also check a few non-candidate "splitter" words if pool is still large
    if len(candidates) > 10:
        all_pool = all_words[:200]
        for word in all_pool:
            if word in candidates:
                continue
            score = entropy_score(word, candidates)
            if score > best_score:
                best_score = score
                best_word = word

    return best_word


# ═══════════════════════════════════════════════
#  Grid Parser  (reads WordSeek bot reply)
# ═══════════════════════════════════════════════

def _normalize_line(line: str) -> str:
    """Convert Unicode math bold/italic letters (like 𝗖𝗥𝗔𝗡𝗘) back to ASCII."""
    result = []
    for ch in line:
        cp = ord(ch)
        if 0x1D5D4 <= cp <= 0x1D5ED:
            result.append(chr(cp - 0x1D5D4 + ord('A')))
        elif 0x1D5EE <= cp <= 0x1D607:
            result.append(chr(cp - 0x1D5EE + ord('a')))
        elif 0x1D400 <= cp <= 0x1D419:
            result.append(chr(cp - 0x1D400 + ord('A')))
        elif 0x1D41A <= cp <= 0x1D433:
            result.append(chr(cp - 0x1D41A + ord('a')))
        elif 0x1D434 <= cp <= 0x1D44D:
            result.append(chr(cp - 0x1D434 + ord('A')))
        elif 0x1D44E <= cp <= 0x1D467:
            result.append(chr(cp - 0x1D44E + ord('a')))
        elif 0x1D468 <= cp <= 0x1D481:
            result.append(chr(cp - 0x1D468 + ord('A')))
        elif 0x1D482 <= cp <= 0x1D49B:
            result.append(chr(cp - 0x1D482 + ord('a')))
        elif 0x1D5A0 <= cp <= 0x1D5B9:
            result.append(chr(cp - 0x1D5A0 + ord('A')))
        elif 0x1D5BA <= cp <= 0x1D5D3:
            result.append(chr(cp - 0x1D5BA + ord('a')))
        elif 0x1D63C <= cp <= 0x1D655:
            result.append(chr(cp - 0x1D63C + ord('A')))
        elif 0x1D656 <= cp <= 0x1D66F:
            result.append(chr(cp - 0x1D656 + ord('a')))
        elif 0x1D670 <= cp <= 0x1D689:
            result.append(chr(cp - 0x1D670 + ord('A')))
        elif 0x1D68A <= cp <= 0x1D6A3:
            result.append(chr(cp - 0x1D68A + ord('a')))
        else:
            result.append(ch)
    return "".join(result)


def parse_grid(text: str, mode: int) -> Optional[List[Tuple[str, List[str]]]]:
    """
    Parse the emoji grid from a WordSeek bot message.
    Handles Unicode bold fonts like 𝗖𝗥𝗔𝗡𝗘 → CRANE via _normalize_line.
    Returns list of (word, pattern) or None if unparseable.
    """
    import re
    lines = text.strip().split("\n")
    results = []

    for line in lines:
        emojis = re.findall(r"[🟩🟨🟥⬛⬜]", line)
        norm = _normalize_line(line)
        words = re.findall(r"[A-Za-z]{" + str(mode) + r"}", norm)
        if len(emojis) == mode and words:
            pattern = []
            for e in emojis:
                if e == "🟩":
                    pattern.append("G")
                elif e == "🟨":
                    pattern.append("Y")
                else:
                    pattern.append("R")
            results.append((words[0].lower(), pattern))

    return results if results else None
    
