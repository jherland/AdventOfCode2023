from bisect import bisect_left
from collections.abc import Iterator
from itertools import combinations
from typing import NamedTuple, Self


class Coord(NamedTuple):
    y: int
    x: int

    def mgdist(self, other: Self) -> int:
        return abs(self.y - other.y) + abs(self.x - other.x)


def parse(lines: list[str], expansion: int) -> Iterator[Coord]:
    xlen = max(len(line) for line in lines)
    empty_y = [i for i, line in enumerate(lines) if all(c == "." for c in line)]
    empty_x = [i for i in range(xlen) if all(line[i] == "." for line in lines)]
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "#":
                yield Coord(
                    y + bisect_left(empty_y, y) * (expansion - 1),
                    x + bisect_left(empty_x, x) * (expansion - 1),
                )


with open("11.input") as f:
    lines = [line.rstrip() for line in f]

# Part 1: What is the sum of shortest distances between all galaxies?
galaxies = list(parse(lines, expansion=2))
print(sum(a.mgdist(b) for a, b in combinations(galaxies, 2)))

# Part 2: What is the sum of shortest distances between all older galaxies?
galaxies = list(parse(lines, expansion=1_000_000))
print(sum(a.mgdist(b) for a, b in combinations(galaxies, 2)))
