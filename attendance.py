"""Roster and attendance logic.

Pure data logic with no Streamlit or audio dependencies so it can be
unit-tested in isolation.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

PRESENT = "Present"
ABSENT = "Absent"


@dataclass
class Student:
    roll_number: int
    name: str
    status: str = ABSENT


@dataclass
class Roster:
    """A list of students plus their current attendance status."""

    students: list[Student] = field(default_factory=list)

    # -- construction -------------------------------------------------------

    @classmethod
    def from_rows(cls, rows: list[dict]) -> "Roster":
        students = []
        for row in rows:
            roll = str(row.get("roll_number", "")).strip()
            name = str(row.get("name", "")).strip()
            if not roll or not name:
                continue
            students.append(Student(roll_number=int(roll), name=name))
        return cls(students=students)

    # -- queries ------------------------------------------------------------

    def get(self, roll_number: int) -> Student | None:
        for s in self.students:
            if s.roll_number == roll_number:
                return s
        return None

    @property
    def present(self) -> list[Student]:
        return [s for s in self.students if s.status == PRESENT]

    @property
    def absent(self) -> list[Student]:
        return [s for s in self.students if s.status == ABSENT]

    # -- mutation -----------------------------------------------------------

    def reset(self) -> None:
        """Auto-fill everyone as Absent (the default state before roll call)."""
        for s in self.students:
            s.status = ABSENT

    def mark_present(self, roll_numbers) -> list[Student]:
        """Flip the given roll numbers to Present. Returns the students changed."""
        changed = []
        for roll in roll_numbers:
            s = self.get(roll)
            if s is not None and s.status != PRESENT:
                s.status = PRESENT
                changed.append(s)
        return changed

    def set_status(self, roll_number: int, status: str) -> None:
        s = self.get(roll_number)
        if s is not None:
            s.status = status

    def add_student(self, roll_number: int, name: str) -> None:
        if self.get(roll_number) is None:
            self.students.append(Student(roll_number=roll_number, name=name.strip()))

    def remove_student(self, roll_number: int) -> None:
        self.students = [s for s in self.students if s.roll_number != roll_number]


# -- CSV persistence --------------------------------------------------------


def load_roster(path: str) -> Roster:
    if not os.path.exists(path):
        return Roster()
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return Roster.from_rows(rows)


def save_roster(roster: Roster, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ordered = sorted(roster.students, key=lambda s: s.roll_number)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_number", "name"])
        for s in ordered:
            writer.writerow([s.roll_number, s.name])


def attendance_rows(roster: Roster) -> list[dict]:
    """Export-friendly rows for the current attendance state."""
    return [
        {"roll_number": s.roll_number, "name": s.name, "status": s.status}
        for s in sorted(roster.students, key=lambda s: s.roll_number)
    ]
