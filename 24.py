from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from fractions import Fraction as Frac
from functools import cached_property
from itertools import combinations, zip_longest
from typing import NamedTuple, Self

from sympy import Symbol, solve_poly_system


class Coord(NamedTuple):
    """Point in 3D space."""

    x: Frac
    y: Frac
    z: Frac

    @classmethod
    def parse(cls, s: str) -> Self:
        return cls(*[Frac(word.strip()) for word in s.split(",")])

    def __add__(self, o: Self) -> Self:  # type: ignore[override]
        return self.__class__(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: Self) -> Self:
        return self.__class__(self.x - o.x, self.y - o.y, self.z - o.z)

    def within(self, lower: Self, upper: Self) -> bool:
        assert upper >= lower
        return (
            lower.x <= self.x <= upper.x
            and lower.y <= self.y <= upper.y
            and lower.z <= self.z <= upper.z
        )


class Line2DFormula(NamedTuple):
    """Encapsulate f(X) = aX + b."""

    a: Frac
    b: Frac

    def intersection(self, other: Self) -> bool | tuple[Frac, Frac]:
        """Solve for self == other.

        Return:
            - True if lines are equal (parallel, and always intersect)
            - False if lines are parallel, and never intersect
            - Otherwise, the intersection point (X, f(X))
        """
        if self.a == other.a:  # parallel
            return self.b == other.b
        x = (other.b - self.b) / (self.a - other.a)
        y = self.a * x + self.b
        assert y == other.a * x + other.b
        return x, y


@dataclass(frozen=True, order=True)
class Line3D:
    """Encapsulate a line in 3D space.

    Vector form:
        (x, y, z) = (x0, y0, z0) + t(a, b, c)
    Parametric form:
        x = x0 + ta, y = y0 + tb, z = z0 + tc
    Symmetric form:
        (x - x0) / a = (y - y0) / b = (z - z0) / c
    """

    pos: Coord  # (x0, y0, z0)
    vel: Coord  # (a, b, c)

    @classmethod
    def parse(cls, line: str) -> Self:
        pos, vel = line.split("@")
        return cls(Coord.parse(pos), Coord.parse(vel))

    @cached_property
    def xy_formula(self) -> Line2DFormula:
        """Find `y = ax + b` for self and return it."""
        a = Frac(self.vel.y, self.vel.x)
        b = self.pos.y - a * self.pos.x
        return Line2DFormula(a, b)

    @cached_property
    def xz_formula(self) -> Line2DFormula:
        """Find `z = cx + d` for self and return it."""
        c = Frac(self.vel.z, self.vel.x)
        d = self.pos.z - c * self.pos.x
        return Line2DFormula(c, d)

    def project(self, **kw: Frac) -> Self:
        """Set the given dimension(s) to the given value."""
        return self.__class__(self.pos._replace(**kw), self.vel._replace(**kw))

    def time(self, pos: Coord) -> Frac:
        """Return time at which self is at given 'pos'."""
        assert self.xy_formula.a * pos.x + self.xy_formula.b == pos.y
        assert self.xz_formula.a * pos.x + self.xz_formula.b == pos.z
        delta = pos - self.pos
        ratios: set[Frac] = {
            getattr(delta, c) / getattr(self.vel, c)
            for c in "xyz"
            if getattr(self.vel, c) != 0
        }
        assert len(ratios) == 1
        return next(iter(ratios))


def intersections(
    lines: Iterable[Line3D],
) -> Iterator[tuple[Line3D, Line3D, Coord]]:
    for h1, h2 in combinations(lines, 2):
        xy_cross = h1.xy_formula.intersection(h2.xy_formula)
        xz_cross = h1.xz_formula.intersection(h2.xz_formula)
        if xy_cross is False or xz_cross is False:  # No intersection point
            continue
        if xy_cross is True and xz_cross is True:
            raise ValueError(h1, h2, "are the same line")
        else:
            if xz_cross is True:  # h1 and h2 share the XZ plane
                assert isinstance(xy_cross, tuple)
                x, y = xy_cross
                z = h1.xz_formula.a * x + h1.xz_formula.b
            elif xy_cross is True:  # h1 and h2 share the XY plane
                assert isinstance(xz_cross, tuple)
                x, z = xz_cross
                y = h1.xy_formula.a * x + h1.xy_formula.b
            else:
                x, y = xy_cross
                x2, z = xz_cross
                if x != x2:
                    continue
            yield h1, h2, Coord(x, y, z)


with open("24.input") as f:
    hailstones = [Line3D.parse(line) for line in f]

# Part 1: How many of these intersections occur within the test area?
lower, upper = 200_000_000_000_000, 400_000_000_000_000  # Example: 7, 27
test_area = (
    Coord(Frac(lower), Frac(lower), Frac(0)),
    Coord(Frac(upper), Frac(upper), Frac(0)),
)
crossings = [
    cross
    for h1, h2, cross in intersections(h.project(z=Frac(0)) for h in hailstones)
    if cross.within(*test_area) and h1.time(cross) >= 0 and h2.time(cross) >= 0
]
print(len(crossings))

# Part 2: What is the sum(X, Y, Z) of the initial position of your throw?
# Set up a system of equations to solve for the position + velocity of our throw
syms = list(map(Symbol, "x y z vx vy vz".split()))
X, Y, Z, VX, VY, VZ = syms
eqs = []
for i, line in enumerate(hailstones[:3]):  # only look at the first 3 lines
    # A different time variable for each intersection
    T = Symbol(f"t{i}")  # type: ignore[no-untyped-call]

    # (x + vx * t) is the x-coordinate of our throw,
    # (line.pos.x + line.vel.x * t) is the x-coordinate of the hailstone,
    # set these equal, and subtract to get:
    #   x + vx * t - line.pos.x + line.vel.x * t = 0
    # similarly for y and z
    eqs += [X + VX * T - line.pos.x - line.vel.x * T]
    eqs += [Y + VY * T - line.pos.y - line.vel.y * T]
    eqs += [Z + VZ * T - line.pos.z - line.vel.z * T]
    syms.append(T)

results = solve_poly_system(eqs, *syms)  # type: ignore[no-untyped-call]
assert len(results) == 1
x, y, z, vx, vy, vz, *ts = next(iter(results))
throw = Line3D(Coord(x, y, z), Coord(vx, vy, vz))
print(sum([throw.pos.x, throw.pos.y, throw.pos.z]))

# Sanity checks
for hs, t in zip_longest(hailstones, ts):
    h1, h2, cross = next(iter(intersections([throw, hs])))
    assert h1 == throw
    assert h2 == hs
    assert throw.time(cross) == hs.time(cross)
    if t is not None:
        assert throw.time(cross) == t
