from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from itertools import chain, combinations
from typing import Self


def find_reflections(strings: list[str], start: int = 1) -> Iterator[int]:
    if start == len(strings):
        return  # no reflection found
    reflection = zip(reversed(strings[:start]), strings[start:], strict=False)
    if all(a == b for a, b in reflection):  # found it!
        yield start  # number of strings preceding reflection
    yield from find_reflections(strings, start + 1)  # try next line


def find_smudged_reflection(strings: list[str]) -> Iterator[int]:
    # Find a pair of strings that differ by only one char
    for (_, a), (i, b) in combinations(enumerate(strings), 2):
        if sum(ca != cb for ca, cb in zip(a, b, strict=True)) == 1:
            # Generate new reflections after flipping smudged char
            new_strings = [a if i == j else c for j, c in enumerate(strings)]
            yield from find_reflections(new_strings)


@dataclass
class Pattern:
    lines: list[str]

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        return cls([line.rstrip() for line in lines])

    def __post_init__(self) -> None:
        # All lines have the same length
        assert len({len(line) for line in self.lines}) == 1

    @cached_property
    def columns(self) -> list[str]:
        return ["".join(chars) for chars in zip(*self.lines, strict=True)]

    def find_reflection(self) -> int:
        reflection_lines = find_reflections(self.lines)
        reflection_cols = find_reflections(self.columns)
        return next(chain((100 * n for n in reflection_lines), reflection_cols))

    def find_smudged_reflection(self) -> int:
        """Find smudge that causes a _different_ reflection line to be valid."""
        without_smudge = self.find_reflection()
        assert without_smudge > 0
        reflection_lines = find_smudged_reflection(self.lines)
        reflection_cols = find_smudged_reflection(self.columns)
        results = chain((100 * n for n in reflection_lines), reflection_cols)
        return next(r for r in results if r != without_smudge)


with open("13.input") as f:
    patterns = [Pattern.parse(b.splitlines()) for b in f.read().split("\n\n")]

# Part 1: Sum of reflection lines in each pattern?
print(sum(pattern.find_reflection() for pattern in patterns))

# Part 2: Sum of reflection lines in each pattern after finding smudges?
print(sum(pattern.find_smudged_reflection() for pattern in patterns))
