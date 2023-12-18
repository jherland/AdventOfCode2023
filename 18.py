from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import batched, takewhile
from typing import NamedTuple, Self


def parse(line: str) -> tuple[tuple[str, int], tuple[str, int]]:
    dir1, amount, color = line.split()
    assert len(dir1) == 1 and dir1 in "UDLR"
    n1 = int(amount)
    assert len(color) == 9 and color.startswith("(#") and color.endswith(")")
    dir2 = {"0": "R", "1": "D", "2": "L", "3": "U"}[color[7]]
    n2 = int(color[2:7], 16)
    return (dir1, n1), (dir2, n2)


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other: Self) -> Self:  # type: ignore[override]
        return self.__class__(self.y + other.y, self.x + other.x)


@dataclass(frozen=True, order=True)
class Line:
    start: Coord
    end: Coord
    vertical: bool

    def __post_init__(self) -> None:
        if self.vertical:
            assert self.start.y < self.end.y
            assert self.start.x == self.end.x
        else:
            assert self.start.y == self.end.y
            assert self.start.x < self.end.x

    @classmethod
    def parse(cls, start: Coord, dir: str, steps: int) -> tuple[Self, Coord]:
        delta = {
            "U": Coord(-steps, 0),
            "D": Coord(steps, 0),
            "L": Coord(0, -steps),
            "R": Coord(0, steps),
        }
        end = start + delta[dir]
        return cls(min(start, end), max(start, end), dir in "UD"), end


class Span(NamedTuple):
    start: int
    end: int  # inclusive

    def union(self, other: Self) -> Iterator[Span]:
        assert other.start >= self.start
        if self.end < other.start:  # no overlap
            yield self
            yield other
        elif self.end >= other.start:  # overlap
            yield Span(self.start, max(self.end, other.end))
        else:
            raise RuntimeError

    @classmethod
    def spans_between_vlines(cls, vlines: Iterable[Line]) -> Iterator[Self]:
        for x_a, x_b in batched(sorted([line.start.x for line in vlines]), 2):
            yield cls(x_a, x_b)

    @staticmethod
    def merge(spans: list[Span]) -> Iterator[Span]:
        spans = sorted(spans)
        cur = spans.pop(0)
        while spans:
            cur, *nxt = list(cur.union(spans.pop(0)))
            if nxt:
                assert len(nxt) == 1
                yield cur
                cur = nxt[0]
        yield cur


def dig_trench(instructions: Iterable[tuple[str, int]]) -> Iterator[Line]:
    start = cur = Coord(0, 0)
    for dir, n in instructions:
        line, cur = Line.parse(cur, dir, n)
        if line.vertical:  # don't need horizontal lines below
            yield line
    assert cur == start


def measure_area_inside(vlines: Iterable[Line]) -> int:
    lines = sorted(vlines, key=lambda vline: vline.start.y)
    total_area = 0
    old_y = lines[0].start.y
    active_lines: list[Line] = []  # sorted by end.y
    while lines or active_lines:
        # find next corner in the y-direction
        new_y = min(
            [line.start.y for line in lines[:1]]
            + [line.end.y for line in active_lines[:1]]
        )
        # Add area covered between old_y + 1 and new_y
        assert len(active_lines) % 2 == 0
        x_spans_before = list(Span.spans_between_vlines(active_lines))
        width = sum(b + 1 - a for a, b in x_spans_before)
        height = new_y - (old_y + 1)
        total_area += height * width
        # Find lines that end here, and lines that start here
        olds = list(takewhile(lambda line: line.end.y == new_y, active_lines))
        news = list(takewhile(lambda line: line.start.y == new_y, lines))
        # Update active_lines and lines
        active_lines = active_lines[len(olds) :] + news
        active_lines.sort(key=lambda line: line.end.y)
        del lines[: len(news)]
        # Add area covered on new_y
        x_spans_after = list(Span.spans_between_vlines(active_lines))
        x_spans_merged = list(Span.merge(x_spans_before + x_spans_after))
        total_area += sum(b + 1 - a for a, b in x_spans_merged)
        # Update y
        old_y = new_y

    return total_area


with open("18.input") as f:
    p1_instr, p2_instr = zip(*[parse(line) for line in f], strict=True)

# Part 1: How many cubic meters of lava could the lagoon hold?
print(measure_area_inside(dig_trench(p1_instr)))

# Part 2: How many cubic meters of lava could the bigger lagoon hold?
print(measure_area_inside(dig_trench(p2_instr)))
