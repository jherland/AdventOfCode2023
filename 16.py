from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain
from typing import Self


class Dir(Enum):
    N = auto()
    E = auto()
    S = auto()
    W = auto()


@dataclass(frozen=True, order=True)
class Coord:
    y: int
    x: int

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.y + other.y, self.x + other.x)

    def nbor(self, dir: Dir) -> Self:
        cls = self.__class__
        delta = {
            Dir.N: cls(-1, 0),
            Dir.E: cls(0, 1),
            Dir.S: cls(1, 0),
            Dir.W: cls(0, -1),
        }
        return self + delta[dir]


@dataclass
class Grid:
    lines: list[str]
    height: int
    width: int

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        lines = [line.rstrip() for line in lines]
        height = len(lines)
        line_lens = {len(line) for line in lines}
        assert len(line_lens) == 1
        width = line_lens.pop()
        assert all(all(c in ".|-/\\" for c in line) for line in lines)
        return cls(lines, height, width)

    def render(self) -> str:
        return "\n".join(self.lines)

    def __getitem__(self, pos: Coord) -> str:
        return self.lines[pos.y][pos.x]

    def get(self, pos: Coord) -> str | None:
        try:
            return self[pos]
        except IndexError:
            return None

    def __contains__(self, pos: Coord) -> bool:
        return (0 <= pos.y < self.height) and (0 <= pos.x < self.width)


@dataclass(frozen=True, order=True)
class Beam:
    pos: Coord
    dir: Dir  # noqa: A003

    def interact(self, c: str) -> Iterator[Self]:
        cls = self.__class__
        if c == ".":
            yield cls(self.pos.nbor(self.dir), self.dir)
        elif c == "/":
            dirmap = {Dir.N: Dir.E, Dir.E: Dir.N, Dir.S: Dir.W, Dir.W: Dir.S}
            newdir = dirmap[self.dir]
            yield cls(self.pos.nbor(newdir), newdir)
        elif c == "\\":
            dirmap = {Dir.N: Dir.W, Dir.E: Dir.S, Dir.S: Dir.E, Dir.W: Dir.N}
            newdir = dirmap[self.dir]
            yield cls(self.pos.nbor(newdir), newdir)
        elif c == "-" and self.dir in {Dir.E, Dir.W}:
            yield cls(self.pos.nbor(self.dir), self.dir)
        elif c == "-":
            yield cls(self.pos.nbor(Dir.E), Dir.E)
            yield cls(self.pos.nbor(Dir.W), Dir.W)
        elif c == "|" and self.dir in {Dir.N, Dir.S}:
            yield cls(self.pos.nbor(self.dir), self.dir)
        elif c == "|":
            yield cls(self.pos.nbor(Dir.N), Dir.N)
            yield cls(self.pos.nbor(Dir.S), Dir.S)
        else:
            raise RuntimeError(self, c)


def follow(grid: Grid, start: Beam) -> set[Beam]:
    seen: set[Beam] = set()
    queue = [start]
    while queue:
        beam = queue.pop(0)
        if beam.pos not in grid:
            continue
        if beam in seen:
            continue
        seen.add(beam)
        queue.extend(beam.interact(grid[beam.pos]))
    return seen


with open("16.input") as f:
    grid = Grid.parse(f)

# Part 1: How many tiles are energized when starting at (0,0) from the left?
print(len({beam.pos for beam in follow(grid, Beam(Coord(0, 0), Dir.E))}))

# Part 2: How many tiles are energized when starting at the best edge position?
start_alts = chain(
    (Beam(Coord(y, 0), Dir.E) for y in range(grid.height)),
    (Beam(Coord(y, grid.width - 1), Dir.W) for y in range(grid.height)),
    (Beam(Coord(0, x), Dir.S) for x in range(grid.width)),
    (Beam(Coord(grid.height - 1, x), Dir.N) for x in range(grid.width)),
)
print(max(len({b.pos for b in follow(grid, start)}) for start in start_alts))
