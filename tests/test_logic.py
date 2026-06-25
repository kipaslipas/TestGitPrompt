"""Unit tests for the pure logic: number parsing, matching, attendance."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import attendance as att  # noqa: E402
from matcher import extract_numbers, name_matches, match_transcript  # noqa: E402


def make_roster():
    return att.Roster.from_rows(
        [
            {"roll_number": "1", "name": "Aisha Rahman"},
            {"roll_number": "5", "name": "Priya Sharma"},
            {"roll_number": "12", "name": "Daniel Carter"},
            {"roll_number": "21", "name": "Noah Williams"},
        ]
    )


# -- number parsing ---------------------------------------------------------


def test_extract_digits():
    assert extract_numbers("roll number 12 and 5") == {12, 5}


def test_extract_number_words():
    assert extract_numbers("roll number five") == {5}


def test_extract_compound_number_words():
    nums = extract_numbers("number twenty one present")
    assert 21 in nums


# -- name matching ----------------------------------------------------------


def test_name_exact_match():
    assert name_matches("priya sharma is here", "Priya Sharma")


def test_name_fuzzy_match_handles_stt_noise():
    # Whisper might mis-hear the surname slightly.
    assert name_matches("aisha rahmaan", "Aisha Rahman")


def test_name_no_false_match():
    assert not name_matches("completely different words", "Priya Sharma")


# -- end-to-end matching ----------------------------------------------------


def test_match_by_roll_or_name():
    roster = make_roster()
    transcript = "number five, and Daniel Carter, also twenty one"
    matched = sorted(match_transcript(transcript, roster.students))
    assert matched == [5, 12, 21]


# -- attendance logic -------------------------------------------------------


def test_reset_marks_all_absent():
    roster = make_roster()
    roster.mark_present([1, 5])
    roster.reset()
    assert all(s.status == att.ABSENT for s in roster.students)


def test_mark_present_and_absent_autofill():
    roster = make_roster()
    roster.reset()
    roster.mark_present([5, 12])
    assert {s.roll_number for s in roster.present} == {5, 12}
    # Everyone not called is auto-filled Absent.
    assert {s.roll_number for s in roster.absent} == {1, 21}


def test_mark_present_returns_only_new_changes():
    roster = make_roster()
    roster.reset()
    first = roster.mark_present([5])
    second = roster.mark_present([5, 12])
    assert [s.roll_number for s in first] == [5]
    assert [s.roll_number for s in second] == [12]
