from dataclasses import dataclass
from functools import reduce
from itertools import batched
from typing import Iterable, Iterator, Self


@dataclass(frozen=True, order=True)
class Range:
    start: int
    len: int

    @property
    def end(self) -> int:
        return self.start + self.len

    def __contains__(self, n: int) -> bool:
        return self.start <= n < self.end

    def is_inside(self, other: Self) -> bool:
        return other.start <= self.start and other.end >= self.end

    def intersection(self, other: Self) -> Self | None:
        if other < self:
            return other.intersection(self)
        elif other.start < self.start + self.len:
            return self.__class__(
                other.start, min(self.end, other.end) - other.start
            )
        else:
            return None

    def shift(self, offset: int) -> Self:
        return self.__class__(self.start + offset, self.len)

    def split(self, offset: int) -> (Self, Self):
        assert 0 < offset < self.len
        return (
            self.__class__(self.start, offset),
            self.__class__(self.start + offset, self.len - offset),
        )

    def fragment(self, other: Self) -> Iterator[Self]:
        """Split self into 1-3 Range objects, based on overlap with 'other'.

        Find overlap between [self.start, self.end) and [other.src, other.end),
        if any, and yield self split into chunks that never span _across_
        other.start or other.end.
        """

        if self.end <= other.start:  # other is fully after self
            yield self
        elif self.start < other.start:  # other starts somewhere in self
            # Split self on other.start
            left, right = self.split(other.start - self.start)
            yield left  # left side does not overlap with other
            yield from right.fragment(other)  # right side overlaps half/fully
        # other starts at or before self
        elif self.end <= other.end:  # self is fully inside other
            yield self
        elif self.start < other.end:  # other ends somewhere in self
            # Split self on other.end
            left, right = self.split(other.end - self.start)
            yield left  # left side is fully inside other
            yield right  # right side is fully outside other
        else:  # other is fully before self
            yield self


@dataclass(frozen=True, order=True)
class MapRange:
    src: Range
    dst: Range

    @classmethod
    def parse(cls, line: str):
        dst_start, src_start, length = [int(num) for num in line.split()]
        return cls(Range(src_start, length), Range(dst_start, length))

    @property
    def offset(self) -> int:
        return self.dst.start - self.src.start

    def __call__(self, n: int) -> int | None:
        return (n + self.offset) if n in self.src else None

    def reverse(self) -> Self:
        return self.__class__(self.dst, self.src)

    def src_intersect(self, limits: Iterable[Range]) -> Iterator[Self]:
        for limit in limits:
            if src := self.src.intersection(limit):
                yield self.__class__(src, src.shift(self.offset))


@dataclass(frozen=True)
class MapRanges:
    src_type: str
    dst_type: str
    ranges: list[MapRange]  # sorted

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        heading = next(lines).rstrip()
        assert heading.endswith(" map:")
        src_type, to, dst_type = heading[:-5].split("-")
        assert to == "to"
        ranges = []
        for line in lines:
            if not line.strip():
                break
            ranges.append(MapRange.parse(line))
        ranges.sort()
        for cur, nxt in zip(ranges, ranges[1:]):  # sanity check: no overlaps
            assert not cur.src.intersection(nxt.src)
        return cls(src_type, dst_type, ranges)

    def __call__(self, src: int) -> int:
        for mr in self.ranges:
            dst = mr(src)
            if dst is not None:
                return dst
        return src

    @classmethod
    def combine(cls, a: Self, b: Self) -> Self:
        # Fragment a's ranges to not overlap with b's range boundaries
        a_frags = []
        for a_range in a.ranges:
            for b_range in b.ranges:
                *a_done, a_range = [
                    MapRange(dst.shift(-a_range.offset), dst)
                    for dst in a_range.dst.fragment(b_range.src)
                ]
                a_frags.extend(a_done)
            a_frags.append(a_range)

        # Map each fragment through b
        remapped = [
            MapRange(frag.src, Range(b(frag.dst.start), frag.dst.len))
            for frag in a_frags
        ]
        assert remapped == sorted(remapped)

        # Also need to retain the ranges from b not covered by a's outputs
        b_frags = []
        for b_range in b.ranges:
            for r_range in remapped:
                *b_done, b_range = [
                    MapRange(src, src.shift(b_range.offset))
                    for src in b_range.src.fragment(r_range.dst)
                ]
                b_frags.extend(b_done)
            b_frags.append(b_range)
        for b_frag in b_frags:
            if not any(b_frag.src.intersection(frag.src) for frag in remapped):
                remapped.append(b_frag)
        remapped.sort()
        return cls(a.src_type, b.dst_type, remapped)

    def reverse(self) -> Self:
        return self.__class__(
            self.dst_type,
            self.src_type,
            sorted([mr.reverse() for mr in self.ranges]),
        )

    def src_intersect(self, limits: Iterable[Range]) -> Self:
        new_ranges = []
        for range in self.ranges:
            new_ranges.extend(range.src_intersect(limits))
        return self.__class__(self.src_type, self.dst_type, new_ranges)


with open("05.input") as f:
    first = f.readline()
    assert first.startswith("seeds: ")
    seeds = [int(num) for num in first.split(":")[1].split()]

    second = f.readline()
    assert second.strip() == ""
    maps = []
    while True:
        try:
            maps.append(MapRanges.parse(f))
        except StopIteration:
            break

all_ranges = reduce(MapRanges.combine, maps)

# Part 1: Lowest location number for any of the initial seed numbers?
print(min(all_ranges(seed) for seed in seeds))

# Part 2: Lowest location number for any of the seeds in initial seed ranges?
seed_ranges = [Range(start, length) for start, length in batched(seeds, 2)]
limited_ranges = all_ranges.src_intersect(seed_ranges)
reverse_map = limited_ranges.reverse()
print(reverse_map.ranges[0].src.start)
