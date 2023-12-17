from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from heapq import heappop, heappush
from sys import maxsize
from typing import NamedTuple, Self


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other: Self) -> Self:  # type: ignore[override]
        return self.__class__(self.y + other.y, self.x + other.x)

    def __mul__(self, n: int) -> Self:  # type: ignore[override]
        return self.__class__(self.y * n, self.x * n)


Cost = int
Direction = Coord

NONE = Direction(0, 0)
UP = Direction(-1, 0)
DOWN = Direction(1, 0)
LEFT = Direction(0, -1)
RIGHT = Direction(0, 1)
TURNS = {
    NONE: [UP, DOWN, LEFT, RIGHT],
    UP: [LEFT, RIGHT],
    DOWN: [LEFT, RIGHT],
    LEFT: [UP, DOWN],
    RIGHT: [UP, DOWN],
}


@dataclass
class Grid:
    rows: list[list[Cost]]

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        return cls([[int(c) for c in line.rstrip()] for line in lines])

    @cached_property
    def height(self) -> int:
        return len(self.rows)

    @cached_property
    def width(self) -> int:
        line_lens = {len(row) for row in self.rows}
        assert len(line_lens) == 1
        return line_lens.pop()

    def __getitem__(self, pos: Coord) -> Cost:
        return self.rows[pos.y][pos.x]

    def __contains__(self, pos: Coord) -> bool:
        return 0 <= pos.y < self.height and 0 <= pos.x < self.width


class Path(NamedTuple):
    pos: Coord
    direction: Direction


class State(NamedTuple):
    cost: Cost
    path: Path

    def successors(self, grid: Grid, min_d: int, max_d: int) -> Iterator[Self]:
        for new_dir in TURNS[self.path.direction]:  # turn 90 degrees
            new_cost = self.cost
            for dist in range(1, max_d + 1):  # walk one or more steps
                new_pos = self.path.pos + new_dir * dist
                if new_pos not in grid:
                    break
                new_cost += grid[new_pos]
                if dist >= min_d:
                    yield self.__class__(new_cost, Path(new_pos, new_dir))


def shortest_path(
    grid: Grid, start: Coord, end: Coord, min_d: int, max_d: int
) -> Cost:
    dists: dict[Path, Cost] = defaultdict(lambda: maxsize)
    heap: list[State] = [State(0, Path(start, NONE))]
    while heap:
        cur = heappop(heap)
        if cur.path.pos == end:  # found end
            return cur.cost
        if cur.cost > dists[cur.path]:  # not the lowest cost for this path
            continue
        for state in cur.successors(grid, min_d, max_d):
            if state.cost < dists[state.path]:
                dists[state.path] = state.cost
                heappush(heap, state)
    raise RuntimeError


with open("17.input") as f:
    grid = Grid.parse(f)
start = Coord(0, 0)
end = Coord(grid.height - 1, grid.width - 1)

# Part 1: What is the least heat loss than can be incurred from start to end?
print(shortest_path(grid, start, end, 1, 3))

# Part 2: What is the least heat loss that can be incurred with ultra crucibles?
print(shortest_path(grid, start, end, 4, 10))
