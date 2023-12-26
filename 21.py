from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from heapq import heappop, heappush
from sys import maxsize as infinity
from typing import NamedTuple, Self


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


def shortest_paths(
    nbors: Callable[[Coord], Iterator[Coord]], start: Coord
) -> dict[Coord, int]:
    dist: dict[Coord, int] = defaultdict(lambda: infinity)
    dist[start] = 0
    heap: list[tuple[Coord, int]] = [(start, 0)]
    while heap:
        pos, steps = heappop(heap)
        if steps > dist[pos]:  # not the lowest #steps for this path
            continue
        steps += 1
        for nxt in nbors(pos):
            if steps < dist[nxt]:
                dist[nxt] = steps
                heappush(heap, (nxt, steps))
    return dist


@dataclass(frozen=True)
class Garden:
    grass: set[Coord]
    start: Coord
    height: int
    width: int

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        garden = [
            (Coord(y, x), c)
            for y, line in enumerate(lines)
            for x, c in enumerate(line.rstrip())
        ]
        return cls(
            grass={coord for coord, c in garden if c in {".", "S"}},
            start=next(coord for coord, c in garden if c == "S"),
            height=max(coord.y for coord, _ in garden) + 1,
            width=max(coord.x for coord, _ in garden) + 1,
        )

    def count_paths(self, steps: int) -> int:
        def nbors(pos: Coord) -> Iterator[Coord]:
            for nbor in pos.nbors():
                if nbor in self.grass:
                    yield nbor

        dist = shortest_paths(nbors, self.start)
        reachable = {
            pos for pos, n in dist.items() if n <= steps and n % 2 == steps % 2
        }
        return len(reachable)

    def expand(self, n: int) -> Self:
        grass = set()
        for y in range(-n, n + 1):
            for x in range(-n, n + 1):
                offset = Coord(self.height * y, self.width * x)
                grass.update({coord + offset for coord in self.grass})
        return self.__class__(
            grass,
            self.start,
            self.height * (2 * n + 1),
            self.width * (2 * n + 1),
        )


with open("21.input") as f:
    garden = Garden.parse(f)

# Part 1: How many garden plots could the Elf reach in exactly 64 steps?
print(garden.count_paths(64))

# Part 2: How many garden plots could the Elf reach in exactly 26501365 steps?
# Quadratic magic...
expanded_garden = garden.expand(2)
steps = 26501365
n = steps // garden.width
a, b, c = (
    expanded_garden.count_paths(s * garden.width + (garden.width // 2))
    for s in range(3)
)
print(a + n * (b - a + (n - 1) * (c - b - b + a) // 2))
