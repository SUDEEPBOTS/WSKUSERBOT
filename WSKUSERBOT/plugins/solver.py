import json
import os
import re
from collections import Counter
from typing import List, Optional, Tuple

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Words")
WORD_CACHE = {}

VOWELS = set("aeiou")
VOWEL_WEIGHT = 1.8
POSITION_WEIGHT = 0.6
UNIQUE_BONUS = 10
DUPLICATE_PENALTY = 50


def load_words(mode: int) -> List[str]:
    if mode in WORD_CACHE:
        return WORD_CACHE[mode][:]
    size = {4: "four", 5: "five", 6: "six"}.get(mode, "five")
    common_path = os.path.join(BASE, f"common-{size}.json")
    all_path = os.path.join(BASE, f"all-{size}.json")
    with open(common_path) as f:
        common = json.load(f)
    with open(all_path) as f:
        all_words = json.load(f)
    seen = set(common)
    rest = [w for w in all_words if w not in seen]
    result = common + rest
    WORD_CACHE[mode] = result
    return result[:]


def get_word_stats():
    sizes = {4: "four", 5: "five", 6: "six"}
    result = {}
    for mode, size in sizes.items():
        common_path = os.path.join(BASE, f"common-{size}.json")
        all_path = os.path.join(BASE, f"all-{size}.json")
        with open(common_path) as f:
            common = len(json.load(f))
        with open(all_path) as f:
            all_words = len(json.load(f))
        result[mode] = {"common": common, "all": all_words}
    return result


def _normalize_line(line: str) -> str:
    """Convert Unicode math bold/italic letters back to ASCII."""
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
    lines = text.strip().split('\n')
    results = []
    for line in lines:
        emojis = re.findall(r'[🟩🟨🟥]', line)
        norm = _normalize_line(line)
        words = re.findall(r'[A-Za-z]{' + str(mode) + r'}', norm)
        if len(emojis) == mode and words:
            pattern = []
            for e in emojis:
                if e == '🟩':
                    pattern.append('G')
                elif e == '🟨':
                    pattern.append('Y')
                else:
                    pattern.append('R')
            results.append((words[0].lower(), pattern))
    return results if results else None


def filter_words(words: List[str], guesses: List[Tuple[str, List[str]]]) -> List[str]:
    filtered = words[:]
    for guess_word, pattern in guesses:
        new_filtered = []
        for word in filtered:
            if word == guess_word:
                continue
            valid = True
            for i, (letter, color) in enumerate(zip(guess_word, pattern)):
                if color == 'G':
                    if word[i] != letter:
                        valid = False
                        break
                elif color == 'Y':
                    if letter not in word or word[i] == letter:
                        valid = False
                        break
                elif color == 'R':
                    confirmed = sum(
                        1 for j, (l, c) in enumerate(zip(guess_word, pattern))
                        if l == letter and c in ('G', 'Y')
                    )
                    if word.count(letter) > confirmed:
                        valid = False
                        break
            if valid:
                new_filtered.append(word)
        filtered = new_filtered
    return filtered


def letter_freq_score(word: str, candidates: List[str]) -> float:
    if not candidates:
        return 0

    freq = Counter()
    pos_freq = [Counter() for _ in range(len(candidates[0]))]
    for c in candidates:
        for i, l in enumerate(c):
            freq[l] += 1
            pos_freq[i][l] += 1

    total = len(candidates)
    score = 0.0
    seen = set()
    for i, l in enumerate(word):
        if l in seen:
            score -= DUPLICATE_PENALTY
            continue
        seen.add(l)
        lf = freq.get(l, 0) / total
        pf = pos_freq[i].get(l, 0) / total
        score += lf * (VOWEL_WEIGHT if l in VOWELS else 1.0)
        score += pf * POSITION_WEIGHT
        score += UNIQUE_BONUS

    return score


def best_guess(words: List[str], all_words: List[str], guesses: List[Tuple[str, List[str]]]) -> str:
    filtered = filter_words(words, guesses)
    if not filtered:
        filtered = filter_words(all_words, guesses)
    if not filtered:
        return words[0] if words else "crane"
    if len(filtered) <= 2:
        return filtered[0]

    guessed_words = {g[0] for g in guesses}
    candidate_set = set(filtered)

    if len(guesses) == 1:
        guess_word, pattern = guesses[0]
        if all(c == 'R' for c in pattern):
            unique = set(guess_word)
            alt_words = [w for w in all_words if not any(l in w for l in unique) and w not in guessed_words]
            if alt_words:
                return max(alt_words[:200], key=lambda w: letter_freq_score(w, list(candidate_set)))

    candidates = []
    seen_candidates = set()
    for w in all_words:
        if w in candidate_set and w not in seen_candidates:
            candidates.append(w)
            seen_candidates.add(w)
        elif w not in guessed_words and w not in seen_candidates:
            candidates.append(w)
            seen_candidates.add(w)

    if len(candidates) > 500:
        candidates = candidates[:500]

    best_word = None
    best_score = -float('inf')
    for w in candidates:
        base = letter_freq_score(w, list(candidate_set))
        if w in candidate_set:
            base *= 1.3
        base += len(set(w)) * 5
        if base > best_score:
            best_score = base
            best_word = w

    return best_word if best_word else filtered[0]


def best_guesses(words: List[str], all_words: List[str], guesses: List[Tuple[str, List[str]]], n: int = 5) -> List[str]:
    filtered = filter_words(words, guesses)
    if not filtered:
        filtered = filter_words(all_words, guesses)
    if not filtered:
        return (words[:n] if words else ["crane"])

    guessed_words = {g[0] for g in guesses}
    candidate_set = set(filtered)

    candidates = []
    seen_candidates = set()
    for w in all_words:
        if w in candidate_set and w not in seen_candidates:
            candidates.append(w)
            seen_candidates.add(w)
        elif w not in guessed_words and w not in seen_candidates:
            candidates.append(w)
            seen_candidates.add(w)

    if len(candidates) > 500:
        candidates = candidates[:500]

    scored = []
    for w in candidates:
        base = letter_freq_score(w, list(candidate_set))
        if w in candidate_set:
            base *= 1.3
        base += len(set(w)) * 5
        scored.append((base, w))

    scored.sort(key=lambda x: -x[0])
    return [w for _, w in scored[:n]]


STARTERS = {
    4: "star",
    5: "crane",
    6: "strain",
}
