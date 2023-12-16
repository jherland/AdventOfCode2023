from collections import deque
from collections.abc import Iterable
from functools import cache
from itertools import chain
from typing import NamedTuple, Self


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other: Self) -> Self:  # type: ignore[override]
        return self.__class__(self.y + other.y, self.x + other.x)


Direction = Coord
Directions = list[Direction]
DirMap = dict[Direction, Directions]

UP = Direction(-1, 0)
DOWN = Direction(1, 0)
LEFT = Direction(0, -1)
RIGHT = Direction(0, 1)
DIR_MAP: dict[str, DirMap] = {
    ".": {UP: [UP], DOWN: [DOWN], LEFT: [LEFT], RIGHT: [RIGHT]},
    "/": {UP: [RIGHT], RIGHT: [UP], DOWN: [LEFT], LEFT: [DOWN]},
    "\\": {UP: [LEFT], LEFT: [UP], DOWN: [RIGHT], RIGHT: [DOWN]},
    "-": {UP: [LEFT, RIGHT], DOWN: [LEFT, RIGHT], LEFT: [LEFT], RIGHT: [RIGHT]},
    "|": {UP: [UP], DOWN: [DOWN], LEFT: [UP, DOWN], RIGHT: [UP, DOWN]},
}


class Beam(NamedTuple):
    pos: Coord
    direction: Direction


class Grid(NamedTuple):
    chars: list[str]
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

    def at(self, pos: Coord) -> str:
        return self.chars[pos.y][pos.x]

    def contains(self, pos: Coord) -> bool:
        return (0 <= pos.y < self.height) and (0 <= pos.x < self.width)


with open("16.input") as f:
    grid = Grid.parse(f)


@cache
def follow(beam: Beam) -> list[Beam]:
    return [
        Beam(beam.pos + newdir, newdir)
        for newdir in DIR_MAP[grid.at(beam.pos)][beam.direction]
    ]


def count_energized(grid: Grid, start: Beam) -> int:
    seen: set[Beam] = set()
    queue = deque([start])
    while queue:
        beam = queue.pop()
        if not grid.contains(beam.pos) or beam in seen:
            continue
        seen.add(beam)
        queue.extend(follow(beam))
    return len({beam.pos for beam in seen})


# Part 1: How many tiles are energized when starting at (0,0) from the left?
print(count_energized(grid, Beam(Coord(0, 0), RIGHT)))

# Part 2: How many tiles are energized when starting at the best edge position?
start_alts = chain(
    (Beam(Coord(y, 0), RIGHT) for y in range(grid.height)),
    (Beam(Coord(y, grid.width - 1), LEFT) for y in range(grid.height)),
    (Beam(Coord(0, x), DOWN) for x in range(grid.width)),
    (Beam(Coord(grid.height - 1, x), UP) for x in range(grid.width)),
)
print(max(count_energized(grid, start) for start in start_alts))
