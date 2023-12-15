from __future__ import annotations

import sys
from bisect import bisect_left
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import Enum, auto
from typing import Self


class Dir(Enum):
    N = auto()
    E = auto()
    S = auto()
    W = auto()

    def __str__(self) -> str:
        return self.name

    def opposite(self) -> Dir:
        return {Dir.N: Dir.S, Dir.E: Dir.W, Dir.S: Dir.N, Dir.W: Dir.E}[self]


PIPE_CHARS = {
    "|": (Dir.N, Dir.S),
    "-": (Dir.E, Dir.W),
    "L": (Dir.N, Dir.E),
    "F": (Dir.E, Dir.S),
    "7": (Dir.S, Dir.W),
    "J": (Dir.N, Dir.W),
}


@dataclass(frozen=True, order=True)
class Coord:
    y: int
    x: int

    def __str__(self) -> str:
        return f"({self.y}, {self.x})"

    __repr__ = __str__

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


@dataclass(frozen=True, order=True)
class Pipe:
    pos: Coord
    dirs: tuple[Dir, Dir]

    def __str__(self) -> str:
        return f"{self.pos} {self.dirs[0]}/{self.dirs[1]}"

    __repr__ = __str__

    def __contains__(self, dir: Dir) -> bool:
        return dir in self.dirs

    def out_dir(self, in_dir: Dir) -> Dir:
        assert in_dir in self.dirs
        return self.dirs[0] if in_dir == self.dirs[1] else self.dirs[1]

    def next_pos(self, in_dir: Dir) -> tuple[Coord, Dir]:
        """Return next pipe position, and in_dir from its POV."""
        out_dir = self.out_dir(in_dir)
        return self.pos.nbor(out_dir), out_dir.opposite()


def bbox(coords: Iterable[Coord]) -> tuple[Coord, Coord]:
    it = iter(coords)
    first = next(it)
    min_y, max_y = first.y, first.y
    min_x, max_x = first.x, first.x
    for pos in it:
        min_y = min(min_y, pos.y)
        max_y = max(max_y, pos.y)
        min_x = min(min_x, pos.x)
        max_x = max(max_x, pos.x)
    return Coord(min_y, min_x), Coord(max_y, max_x)


def render(pipes: dict[Coord, Pipe], extra: dict[Coord, str]) -> None:
    palette = {"|": "┃", "-": "━", "L": "┗", "F": "┏", "7": "┓", "J": "┛"}
    char_map = {d: palette[c] for c, d in PIPE_CHARS.items()}
    top_left, bottom_right = bbox(pipes.keys())
    for y in range(top_left.y, bottom_right.y + 1):
        for x in range(top_left.x, bottom_right.x + 1):
            pos = Coord(y, x)
            if pos in extra:
                print(extra[pos], end="")
            elif pos in pipes:
                print(char_map[pipes[pos].dirs], end="")
            else:
                print(".", end="")
        print()


def follow(pipes: dict[Coord, Pipe], start: Coord, dir: Dir) -> Iterator[Pipe]:
    assert start in pipes
    assert dir in pipes[start].dirs
    cur = start
    while True:
        yield pipes[cur]
        cur, dir = pipes[cur].next_pos(dir)


def distance_map(pipes: dict[Coord, Pipe], start: Coord) -> dict[Coord, int]:
    """Find distance to start point by following the pipe in both directions."""
    assert start in pipes
    ret: dict[Coord, int] = {}
    for dir in pipes[start].dirs:
        dist = 0
        for pipe in follow(pipes, start, dir):
            if ret.get(pipe.pos, sys.maxsize) < dist:
                break
            ret[pipe.pos] = dist
            dist += 1
    return ret


def enclosed(pipe_loop: set[Pipe]) -> Iterator[Coord]:
    top_left, bottom_right = bbox(p.pos for p in pipe_loop)
    for y in range(top_left.y + 1, bottom_right.y):
        # A point x along this row y, is _inside_ the loop if there are an _odd_
        # number of pipes going north AND an odd number of piped going south on
        # either side of point x.
        pipes_on_row = sorted([(p.pos.x, p) for p in pipe_loop if p.pos.y == y])
        north_pipes = [x for x, p in pipes_on_row if Dir.N in p.dirs]
        south_pipes = [x for x, p in pipes_on_row if Dir.S in p.dirs]
        assert len(north_pipes) % 2 == 0
        assert len(south_pipes) % 2 == 0
        for x in range(
            max(north_pipes[0], south_pipes[0]),
            min(north_pipes[-1], south_pipes[-1]),
        ):
            i_north = bisect_left(north_pipes, x)
            i_south = bisect_left(south_pipes, x)
            if (
                north_pipes[i_north] != x
                and i_north % 2 == 1
                and south_pipes[i_south] != x
                and i_south % 2 == 1
            ):
                yield Coord(y, x)


with open("10.input") as f:
    start: Coord | None = None
    pipes: dict[Coord, Pipe] = {}
    for y, line in enumerate(f):
        for x, c in enumerate(line.rstrip()):
            pos = Coord(y, x)
            if c == "S":
                start = pos
            elif c in PIPE_CHARS:
                pipes[pos] = Pipe(pos, PIPE_CHARS[c])

    # Fill in pipe at start
    assert start
    nbors = tuple(
        d
        for d in [Dir.N, Dir.E, Dir.S, Dir.W]
        if start.nbor(d) in pipes and d.opposite() in pipes[start.nbor(d)]
    )
    assert len(nbors) == 2
    pipes[start] = Pipe(start, nbors)

distmap = distance_map(pipes, start)
pipe_loop = {p for p in pipes.values() if p.pos in distmap}

# Part 1: How many steps along the loop from start to the farthest point?
print(max(distmap.values()))

# Part 2: How many tiles are enclosed by the loop?
print(len(list(enclosed(pipe_loop))))
