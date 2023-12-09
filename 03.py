from collections.abc import Iterator
from itertools import takewhile
from typing import NamedTuple, Self


class Point(NamedTuple):
    y: int
    x: int

    def left(self) -> Self:
        return self.__class__(self.y, self.x - 1)

    def nbors(self) -> set[Self]:
        return {
            self.__class__(y, x)
            for y in [self.y - 1, self.y, self.y + 1]
            for x in [self.x - 1, self.x, self.x + 1]
            if not (y == self.y and x == self.x)
        }


class Part(NamedTuple):
    p: Point
    digits: str

    def points(self) -> set[Point]:
        return {Point(self.p.y, self.p.x + x) for x in range(len(self.digits))}

    def number(self) -> int:
        return int(self.digits)


symbols: dict[Point, str] = {}
pmap: dict[Point, Part] = {}
with open("03.input") as f:
    digits: set[Point] = set()
    for y, line in enumerate(f):
        for x, c in enumerate(line.rstrip()):
            p = Point(y, x)
            if c.isdigit():
                digits.add(p)
                if p.left() not in digits:
                    adj_digits = takewhile(lambda c: c.isdigit(), line[x:])
                    part = Part(p, "".join(adj_digits))
                    for pp in part.points():
                        pmap[pp] = part
            elif c != ".":
                symbols[p] = c


# Part 1: Sum of all of the part numbers in the engine schematic?
parts = {pmap[p] for sym in symbols for p in sym.nbors() if p in pmap}
print(sum(part.number() for part in parts))


# Part 2: Sum of all of the gear ratios in your engine schematic?
def geared_parts() -> Iterator[Part]:
    for gear in {p for p, c in symbols.items() if c == "*"}:
        connected = {pmap[nb] for nb in gear.nbors() if nb in pmap}
        if len(connected) == 2:
            yield tuple(connected)


print(sum(a.number() * b.number() for a, b in geared_parts()))
