import json
import os
import re
from typing import List, Optional

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Words")

def load_words(mode: int) -> List[str]:
    size = {4: "four", 5: "five", 6: "six"}.get(mode, "five")
    # common words pehle try karenge
    common_path = os.path.join(BASE, f"common-{size}.json")
    all_path = os.path.join(BASE, f"all-{size}.json")
    with open(common_path) as f:
        common = json.load(f)
    with open(all_path) as f:
        all_words = json.load(f)
    # common first, then rest
    seen = set(common)
    rest = [w for w in all_words if w not in seen]
    return common + rest

def parse_grid(text: str, mode: int) -> Optional[List[tuple]]:
    """
    Parse WordSeek bot response.
    Returns list of (word, pattern) tuples.
    pattern: list of 'G'=green, 'Y'=yellow, 'R'=red/grey
    """
    lines = text.strip().split('\n')
    results = []
    for line in lines:
        # Find emoji pattern and word
        emojis = re.findall(r'[🟩🟨🟥]', line)
        words = re.findall(r'[A-Za-z]{' + str(mode) + r'}', line)
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

def filter_words(words: List[str], guesses: List[tuple]) -> List[str]:
    """Filter word list based on guess history."""
    filtered = words[:]
    
    for guess_word, pattern in guesses:
        new_filtered = []
        for word in filtered:
            if word == guess_word:
                continue
            valid = True
            
            # Count letter frequencies in guess
            grey_letters = {}
            for i, (letter, color) in enumerate(zip(guess_word, pattern)):
                if color == 'R':
                    grey_letters[letter] = grey_letters.get(letter, 0)
            
            for i, (letter, color) in enumerate(zip(guess_word, pattern)):
                if color == 'G':
                    # Must be this letter at this position
                    if word[i] != letter:
                        valid = False
                        break
                elif color == 'Y':
                    # Must contain letter but NOT at this position
                    if letter not in word or word[i] == letter:
                        valid = False
                        break
                elif color == 'R':
                    # Count greens and yellows of this letter
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

def best_guess(words: List[str], all_words: List[str], guesses: List[tuple]) -> str:
    """Pick best next guess from filtered words."""
    filtered = filter_words(words, guesses)
    if filtered:
        return filtered[0]
    # Fallback to all words
    filtered_all = filter_words(all_words, guesses)
    if filtered_all:
        return filtered_all[0]
    return words[0] if words else "crane"

# Starting words per mode
STARTERS = {
    4: "stare",
    5: "crane",
    6: "strong"
}
