from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, replace
from itertools import cycle
from math import prod
from string import ascii_letters
from typing import NamedTuple, Self


class Coord(NamedTuple):
    z: int
    y: int
    x: int

    @classmethod
    def parse(cls, s: str) -> Self:
        x, y, z = (int(n) for n in s.split(","))
        return cls(z, y, x)

    def __add__(self, other: Self) -> Self:  # type: ignore[override]
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
        other += self.__class__(1, 1, 1)
        for z in range(self.z, other.z):
            for y in range(self.y, other.y):
                for x in range(self.x, other.x):
                    yield self.__class__(z, y, x)


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


def settle(bricks: list[Brick]) -> list[Brick]:
    bricks.sort()

    def fall() -> int:
        """Do one iteration of settling, return the number of falling bricks."""
        stable_coords: set[Coord] = set()
        falling = 0
        for i, brick in enumerate(bricks):
            if brick.is_supported(stable_coords):
                stable_coords |= set(brick.coords())
            else:  # brick is falling
                bricks[i] = brick.fall()
                falling += 1
        return falling

    while fall():
        pass
    return sorted(bricks)


def support_pairs(bricks: list[Brick]) -> Iterator[tuple[Brick, Brick]]:
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


def can_be_disintegrated(bricks: list[Brick]) -> Iterator[Brick]:
    """Yield the bricks that can be removed without causing others to fall."""
    supporters = find_supporters(bricks)
    supportees = find_supportees(bricks)
    for brick in bricks:
        if brick not in supportees:  # brick is not supporting any other bricks
            yield brick
            continue
        if not any(len(supporters[child]) == 1 for child in supportees[brick]):
            yield brick
            continue


def traverse(
    supportees: dict[Brick, set[Brick]], grounded: list[Brick]
) -> Iterator[Brick]:
    queue = deque(grounded)
    while queue:
        current = queue.popleft()
        yield current
        queue.extend(supportees.get(current, []))


def fallout(bricks: list[Brick]) -> Iterator[tuple[Brick, int]]:
    """For each brick, find how many other bricks would fall when it is removed.

    Yield (brick, fallout) pairs associating a brick with the number of other
    bricks that would fall if that first brick is removed.
    """
    # Using a dict mapping supporters to supportees, we can traverse this dict
    # starting from the supporters on the ground to find all supported bricks.
    # To find how many bricks would fall when removing one brick (X), we remove
    # brick X from this dict, and re-traverse to see how many bricks remain
    # supported. The number of bricks that will fall is found by subtracting
    # this number from the total number of bricks.
    num_bricks = len(bricks)
    supportees = find_supportees(bricks)
    grounded = [brick for brick in bricks if brick.on_ground()]
    assert len(set(traverse(supportees, grounded))) == num_bricks

    for supporter in supportees:
        without_supporter = supportees.copy()
        del without_supporter[supporter]
        remain_supported = len(set(traverse(without_supporter, grounded)))
        yield supporter, num_bricks - remain_supported


with open("22.input") as f:
    bricks = [
        Brick.parse(line, name) for line, name in zip(f, cycle(ascii_letters))
    ]
settled = settle(bricks)

# # Part 1: How many bricks could be safely chosen as the one to disintegrate?
print(len(list(can_be_disintegrated(settled))))

# Part 2: What is the sum of the number of other bricks that would fall?
print(sum(num_falling for _, num_falling in fallout(settled)))
