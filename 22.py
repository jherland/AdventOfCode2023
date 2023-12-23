import heapq
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, replace
from functools import cache
from itertools import cycle
from math import prod
from string import ascii_letters
from sys import maxsize as infinity
from typing import NamedTuple, Self


class Coord(NamedTuple):
    z: int
    y: int
    x: int

    @classmethod
    def parse(cls, s: str) -> Self:
        x, y, z = [int(n) for n in s.split(",")]
        return cls(z, y, x)

    def __add__(self, other: Self) -> Self:
        cls = self.__class__
        return cls(self.z + other.z, self.y + other.y, self.x + other.x)

    def __sub__(self, other: Self) -> Self:
        cls = self.__class__
        return cls(self.z - other.z, self.y - other.y, self.x - other.x)

    def below(self) -> Self:
        return self - self.__class__(1, 0, 0)

    def span(self, other: Self) -> Iterator[Self]:
        """Return coords between self and other, inclusive."""
        if other < self:
            return other.span(self)
        other += Coord(1, 1, 1)
        for z in range(self.z, other.z):
            for y in range(self.y, other.y):
                for x in range(self.x, other.x):
                    yield Coord(z, y, x)


@dataclass(frozen=True, order=True)
class Brick:
    start: Coord
    end: Coord  # inclusive
    name: str

    @classmethod
    def parse(cls, line: str, name: str) -> Self:
        start, end = line.rstrip().split("~")
        return cls(Coord.parse(start), Coord.parse(end), name)

    def __post_init__(self) -> None:
        assert self.start <= self.end  # sorted
        # start/end differ in at most one dimension
        diffs = [len({a, b}) for a, b in zip(self.start, self.end, strict=True)]
        assert sorted(diffs) in [[1, 1, 2], [1, 1, 1]]

    def coords(self) -> Iterator[Coord]:
        yield from self.start.span(self.end)

    def volume(self) -> int:
        return prod(self.end + Coord(1, 1, 1) - self.start)

    def fall(self) -> Self:
        return replace(self, start=self.start.below(), end=self.end.below())

    def underneath(self) -> Self:
        fallen = self.fall()
        z = min(fallen.start.z, fallen.end.z)
        return replace(
            self, start=fallen.start._replace(z=z), end=fallen.end._replace(z=z)
        )

    def on_ground(self) -> bool:
        return self.start.z <= 1 or self.end.z <= 1

    def is_supported(self, supports: set[Coord]) -> bool:
        if self.on_ground():
            return True
        return any(b in supports for b in self.underneath().coords())

    def overlaps(self, occupancy: dict[Coord, Self]) -> Iterator[Self]:
        for pos in self.coords():
            if pos in occupancy:
                yield occupancy[pos]


def falling(bricks: list[Brick]) -> Iterator[Brick]:
    """Yield all falling bricks in the given situation."""
    stable_coords = set()
    for brick in sorted(bricks):
        debug = False
        # debug = (
        #         (brick.start.y == 7 and brick.start.x == 2 and brick.name == "z")
        #     or (brick.end.y == 8 and brick.end.x == 2 and brick.name == "E")
        # )
        if debug:
            print(f"  {brick} is above __{brick.underneath()}__")
        if brick.is_supported(stable_coords):
            stable_coords |= set(brick.coords())
            if debug:
                print("    is supported")
                # for other in brick.underneath().overlaps(occupancy):
                    # print(f"    by {other}")
        else:  # brick is falling
            yield brick
            if debug:
                print("    is falling")


def fall(brick_heap: list[Brick]) -> tuple[list[Brick], int]:
    """Do one iteration of settling, and return the number of falling bricks."""
    stable_coords = set()
    falling = 0
    new_heap = []
    while brick_heap:
        brick = heapq.heappop(brick_heap)
        debug = False
        # debug = (
        #         (brick.start.y == 7 and brick.start.x == 2 and brick.name == "z")
        #     or (brick.end.y == 8 and brick.end.x == 2 and brick.name == "E")
        # )
        if debug:
            print(f"  {brick} is above __{brick.underneath()}__")
        if brick.is_supported(stable_coords):
            stable_coords |= set(brick.coords())
            heapq.heappush(new_heap, brick)
            if debug:
                print("    is supported")
                # for other in brick.underneath().overlaps(occupancy):
                    # print(f"    by {other}")
        else:  # brick is falling
            heapq.heappush(new_heap, brick.fall())
            falling += 1
            if debug:
                print("    is falling")
    return new_heap, falling


def fall_inplace(bricks: list[Brick]) -> int:
    """Do one iteration of settling, and return the number of falling bricks."""
    stable_coords = set()
    falling = 0
    for i, brick in enumerate(bricks):
        debug = False
        # debug = (
        #         (brick.start.y == 7 and brick.start.x == 2 and brick.name == "z")
        #     or (brick.end.y == 8 and brick.end.x == 2 and brick.name == "E")
        # )
        if debug:
            print(f"  {brick} is above __{brick.underneath()}__")
        if brick.is_supported(stable_coords):
            stable_coords |= set(brick.coords())
            if debug:
                print("    is supported")
                # for other in brick.underneath().overlaps(occupancy):
                    # print(f"    by {other}")
        else:  # brick is falling
            bricks[i] = brick.fall()
            falling += 1
            if debug:
                print("    is falling")
    return falling


def settle_old(bricks: list[Brick]) -> list[Brick]:
    heapq.heapify(bricks)
    round = 0
    while True:
        # occupancy = {pos: brick for brick in bricks for pos in brick.coords()}
        # assert all(
        #     set(brick.overlaps(occupancy)) == {brick}
        #     for brick in bricks
        # ), f"{brick} overlaps with {list(brick.overlaps(occupancy))}"
        falling_bricks = set(falling(bricks))
        if not falling_bricks:
            return bricks
        bricks = [b.fall() if b in falling_bricks else b for b in bricks]
        round += 1
        # print(f"{round=}, {len(falling_bricks)=}")


def settle_heap(bricks: list[Brick]) -> list[Brick]:
    heapq.heapify(bricks)
    round = 0
    while True:
        # occupancy = {pos: brick for brick in bricks for pos in brick.coords()}
        # assert all(
        #     set(brick.overlaps(occupancy)) == {brick}
        #     for brick in bricks
        # ), f"{brick} overlaps with {list(brick.overlaps(occupancy))}"
        new_bricks, falling = fall(bricks)
        if not falling:
            return new_bricks
        bricks = new_bricks
        round += 1
        # print(f"{round=}, {len(falling_bricks)=}")


def settle_inplace(bricks: list[Brick]) -> list[Brick]:
    bricks.sort()
    while True:
        if not fall_inplace(bricks):
            return sorted(bricks)


settle = settle_inplace


def support_pairs(bricks: list[Brick]) -> tuple[Brick, Brick]:
    """Find (supporter, supportee) pairs in given bricks."""
    occupancy = {pos: brick for brick in bricks for pos in brick.coords()}
    for brick in bricks:
        for under in brick.underneath().overlaps(occupancy):
            yield under, brick


def find_supporters(bricks: list[Brick]) -> dict[Brick, set[Brick]]:
    """Map supportee -> set of supporters."""
    ret: dict[Brick, set[Brick]] = {}  # C -> {B, A}: C is supported by B and A
    for under, over in support_pairs(bricks):
        ret.setdefault(over, set()).add(under)
    return ret


def find_supportees(bricks: list[Brick]) -> dict[Brick, set[Brick]]:
    """Map supporter -> set of supportees."""
    ret: dict[Brick, set[Brick]] = {}  # A -> {B, C}: A supports B and C
    for under, over in support_pairs(bricks):
        ret.setdefault(under, set()).add(over)
    return ret


def fallout(bricks: list[Brick]) -> dict[Brick, int]:
    """Yield each brick and #other bricks that would fall if this is removed."""
    supporters = find_supporters(bricks)
    supportees = find_supportees(bricks)

    brick_fallout: dict[Brick, int] = {}

    for brick in reversed(bricks):
        print(f"  fallout from {brick=}...")
        cur_fallout = 0
        for child in supportees.get(brick, []):
            assert child in brick_fallout
            num_supporters = len(supporters[child])
            print(f"    {child=} has {num_supporters=}")
            assert brick in supporters[child]
            if num_supporters < 2:  # child + grandchildren will fall
                cur_fallout += 1 + brick_fallout[child]
        print(f"    fallout -> {cur_fallout}")
        brick_fallout[brick] = cur_fallout
    return brick_fallout


def can_be_disintegrated(bricks: list[Brick]) -> Iterator[Brick]:
    """Yield the bricks that can be removed without causing others to fall."""
    # for brick, n in fallout(bricks):
    #     if n == 0:
    #         yield brick
    supporters = find_supporters(bricks)
    supportees = find_supportees(bricks)
    for brick in bricks:
        # print(f"Looking at {brick}")
        if brick not in supportees:  # brick is not supporting any other bricks
            # print("  not supporting anything!")
            yield brick
            continue
        if not any(len(supporters[child]) == 1 for child in supportees[brick]):
            # print(f"  no supportee has this as sole supporter")
            yield brick
            continue


with open("22.input") as f:
    bricks = [Brick.parse(line, name) for line, name in zip(f, cycle(ascii_letters))]
settled = settle(bricks)

# # Part 1: How many bricks could be safely chosen as the one to disintegrate?
print(len(list(can_be_disintegrated(settled))))

# Part 2: What is the sum of the number of other bricks that would fall?
print(sum(fallout(settled).values()))
