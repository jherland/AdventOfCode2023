from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple, Self

from bitsets import bitset


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other: Self) -> Self:  # type: ignore[override]
        return self.__class__(self.y + other.y, self.x + other.x)

    def nbors(self) -> Iterator[Self]:
        cls = self.__class__
        yield cls(self.y - 1, self.x)  # N
        yield cls(self.y, self.x + 1)  # E
        yield cls(self.y + 1, self.x)  # S
        yield cls(self.y, self.x - 1)  # W


Cost = int
Direction = Coord
Graph = dict[Coord, dict[Coord, Cost]]

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
    rows: list[str]
    steep_slopes: bool = True

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        return cls([line.rstrip() for line in lines])

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

    def start(self) -> Coord:
        ret = Coord(0, 1)
        assert self[ret] == "."
        return ret

    def end(self) -> Coord:
        ret = Coord(self.height - 1, self.width - 2)
        assert self[ret] == "."
        return ret

    def render(self, extra: dict[Coord, str] = {}) -> str:
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                pos = Coord(y, x)
                line.append(extra.get(pos, self[pos]))
            lines.append("".join(line))
        return "\n".join(lines)

    def nbors(self, pos: Coord) -> Iterator[Coord]:
        for dir, slope in [(UP, "^"), (DOWN, "v"), (LEFT, "<"), (RIGHT, ">")]:
            nbor = pos + dir
            if self.steep_slopes:
                if nbor in self and self[nbor] in {".", slope}:
                    yield nbor
            elif nbor in self and self[nbor] != "#":
                yield nbor

    def adjacencies(self) -> Graph:
        ret: Graph = {}
        dirs = {"^": UP, "v": DOWN, "<": LEFT, ">": RIGHT}
        for y in range(self.height):
            for x in range(self.width):
                pos = Coord(y, x)
                c = self[pos]
                if c == "#":
                    continue
                nbors = ret.setdefault(pos, {})
                if c == "." or not self.steep_slopes:
                    nbors.update(dict.fromkeys(self.nbors(pos), 1))
                elif c in dirs:
                    nbor = pos + dirs[c]
                    assert self[nbor] != "#"
                    nbors[nbor] = 1
                else:
                    raise RuntimeError
        return ret


def optimize(graph: Graph) -> Graph:
    """Remove all non-crossroads from the graph."""
    for pos in list(graph):
        nbors = graph[pos]
        if len(nbors) != 2:
            continue
        (apos, acost), (bpos, bcost) = nbors.items()
        # print(f"{pos=} has 2 {nbors=}")
        if pos in graph[apos]:  # replace graph[apos][pos] -> graph[apos][bpos]
            graph[apos][bpos] = graph[apos][pos] + bcost
            del graph[apos][pos]
        if pos in graph[bpos]:  # replace graph[bpos][pos] -> graph[bpos][apos]
            graph[bpos][apos] = graph[bpos][pos] + acost
            del graph[bpos][pos]
        if not any(pos in graph.get(nbor, []) for nbor in pos.nbors()):
            del graph[pos]
        # print(f"  -> graph[{apos}]={graph[apos]}")
        # print(f"   + graph[{bpos}]={graph[bpos]}")
    return graph


def longest_paths(graph: Graph, start: Coord, end: Coord) -> Cost:
    assert start in graph
    assert end in graph
    node_set = bitset("Nodes", tuple(graph.keys()))

    class Path(NamedTuple):
        last: Coord
        cost: Cost
        seen: node_set

        @classmethod
        def new(cls, start: Coord) -> Self:
            return cls(start, 0, node_set([start]))

        def followers(self) -> Iterator[Self]:
            for nbor, dcost in graph[self.last].items():
                if nbor not in self.seen:
                    yield self.__class__(
                        last=nbor,
                        cost=self.cost + dcost,
                        seen=self.seen.union(node_set([nbor])),
                    )

    queue = deque([Path.new(start)])
    longest = -1
    while queue:
        path = queue.pop()
        if path.last == end:
            if path.cost > longest:
                # print("   ", path.cost)
                longest = path.cost
        else:
            queue.extend(path.followers())
    assert longest >= 0
    return longest


with open("23.input") as f:
    grid = Grid.parse(f)

# print(f"Grid is {grid.height}x{grid.width} = {grid.height * grid.width}")
# print(f"  and has {len("".join(grid.rows).replace("#", ""))} nodes")

# Part 1: How many steps long is the longest hike?
graph = optimize(grid.adjacencies())
# print(f"Optimized graph has {len(graph)} nodes")
print(longest_paths(graph, grid.start(), grid.end()))

# Part 2: How many steps long is the longest hike after removing slopes?
grid.steep_slopes = False
graph = optimize(grid.adjacencies())
# print(f"Optimized, graph has {len(graph)} nodes")
print(longest_paths(graph, grid.start(), grid.end()))
