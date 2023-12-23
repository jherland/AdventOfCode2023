from collections import defaultdict
from collections.abc import Callable, Iterator
from heapq import heappop, heappush
from sys import maxsize as infinity
from typing import NamedTuple, Self


class Coord(NamedTuple):
    y: int
    x: int

    def nbors(self) -> Iterator[Self]:
        cls = self.__class__
        yield cls(self.y - 1, self.x)  # N
        yield cls(self.y, self.x + 1)  # E
        yield cls(self.y + 1, self.x)  # S
        yield cls(self.y, self.x - 1)  # W

    # def mgdist(self, other: Self) -> int:
    #     return abs(self.y - other.y) + abs(self.x - other.x)


# def bbox(coords: Iterable[Coord]) -> tuple[Coord, Coord]:
#     it = iter(coords)
#     first = next(it)
#     min_y, max_y = first.y, first.y
#     min_x, max_x = first.x, first.x
#     for pos in it:
#         min_y = min(min_y, pos.y)
#         max_y = max(max_y, pos.y)
#         min_x = min(min_x, pos.x)
#         max_x = max(max_x, pos.x)
#     return Coord(min_y, min_x), Coord(max_y, max_x)


# def render(*thing_dicts: dict[Coord, str], default: str = " ") -> str:

#     def char(pos: Coord):
#         for things in thing_dicts:
#             if pos in things:
#                 return things[pos]
#         return default

#     top_left, bottom_right = bbox(
#         chain.from_iterable(things.keys() for things in thing_dicts)
#     )
#     return "\n".join(
#         [
#             "".join(
#                 [
#                     char(Coord(y, x))
#                     for x in range(top_left.x, bottom_right.x + 1)
#                 ]
#             ) for y in range(top_left.y, bottom_right.y + 1)
#         ]
#     )


def parse(lines: list[str]) -> Iterator[tuple[Coord, str]]:
    for y, line in enumerate(lines):
        for x, c in enumerate(line.rstrip()):
            yield Coord(y, x), c


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


with open("21.input") as f:
    map = list(parse(f))
    rocks = {coord for coord, c in map if c == "#"}
    garden = {coord for coord, c in map if c == "."}
    start = next(coord for coord, c in map if c == "S")

# print(start)
# print(render({r: "#" for r in rocks}, {g: "." for g in garden}, {start: "S"}))

def nbors(pos: Coord) -> Iterator[Coord]:
    for nbor in pos.nbors():
        if nbor in garden:
            yield nbor

# Part 1: How many garden plots could the Elf reach in exactly 64 steps?
dist = shortest_paths(nbors, start)
# from pprint import pprint
# pprint(dist)
# print(render(
#     {p: hex(n)[-1] for p, n in dist.items()},
#     {r: "#" for r in rocks},
#     {g: "." for g in garden},
#     {start: "S"},
# ))
max_steps = 64
reachable = {
    pos for pos, n in dist.items() if n <= max_steps and n % 2 == max_steps % 2
}
print(len(reachable))

# Part 2: How many garden plots could the Elf reach in exactly 26501365 steps?
