"""Parse a spoken roll-call transcript and match it against the roster.

A student is matched when EITHER their roll number OR their name appears in
the transcript. Designed to tolerate speech-to-text noise:

* spoken number words ("five", "twenty one") are converted to digits
* names are matched with fuzzy comparison so minor mis-hearings still match
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

# Word -> value building blocks for spoken number parsing.
_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}


def extract_numbers(text: str) -> set[int]:
    """Return every integer mentioned in `text`, as digits or number words."""
    numbers: set[int] = set()

    # Raw digit groups, e.g. "12".
    for match in re.findall(r"\d+", text):
        numbers.add(int(match))

    # Number words, including simple compounds like "twenty one".
    tokens = re.findall(r"[a-z]+", text.lower())
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in _TENS:
            value = _TENS[tok]
            if i + 1 < len(tokens) and tokens[i + 1] in _UNITS and _UNITS[tokens[i + 1]] < 10:
                value += _UNITS[tokens[i + 1]]
                i += 1
            numbers.add(value)
        elif tok in _UNITS:
            numbers.add(_UNITS[tok])
        i += 1

    return numbers


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z\s]", "", name.lower()).strip()


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def name_matches(transcript: str, name: str, threshold: float = 0.82) -> bool:
    """True if `name` (or a distinctive part of it) appears in the transcript."""
    norm_name = _normalize(name)
    norm_tx = _normalize(transcript)
    if not norm_name or not norm_tx:
        return False

    # Direct substring hit on the full name.
    if norm_name in norm_tx:
        return True

    tx_tokens = norm_tx.split()
    name_tokens = [t for t in norm_name.split() if len(t) >= 3]

    # Each significant part of the name should appear (exactly or fuzzily)
    # somewhere in the transcript.
    if not name_tokens:
        return False
    for part in name_tokens:
        hit = any(part == t or _similar(part, t) >= threshold for t in tx_tokens)
        if not hit:
            return False
    return True


def match_transcript(transcript: str, students) -> list[int]:
    """Return roll numbers of students detected in the transcript.

    `students` is any iterable of objects with `.roll_number` and `.name`.
    A student matches on roll number OR name.
    """
    spoken_numbers = extract_numbers(transcript)
    matched: list[int] = []
    for s in students:
        if s.roll_number in spoken_numbers or name_matches(transcript, s.name):
            matched.append(s.roll_number)
    return matched
