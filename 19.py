import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from math import prod
from operator import gt, lt
from typing import Self, cast


@dataclass(frozen=True)
class Part:
    x: int
    m: int
    a: int
    s: int

    @classmethod
    def parse(cls, line: str) -> Self:
        assert line.startswith("{") and line.endswith("}")
        membs = line[1:-1].split(",")
        args = {name: int(val) for name, val in [mb.split("=") for mb in membs]}
        return cls(**args)

    def rating(self) -> int:
        return sum(getattr(self, member) for member in "xmas")


@dataclass(frozen=True)
class Rule:
    var: str | None
    op: Callable[[int, int], bool]
    val: int
    dst: str

    @classmethod
    def parse(cls, s: str) -> Self:
        if ":" not in s:  # unconditional rule
            return cls(None, lt, sys.maxsize, s)

        condition, dst = s.split(":")
        var = condition[0]
        op = {"<": lt, ">": gt}[condition[1]]
        val = int(condition[2:])
        return cls(var, op, val, dst)

    def match(self, part: Part) -> bool:
        return self.var is None or self.op(getattr(part, self.var), self.val)


@dataclass(frozen=True)
class Workflow:
    name: str
    rules: list[Rule]

    @classmethod
    def parse(cls, line: str) -> Self:
        assert line.endswith("}")
        name, rest = line[:-1].split("{", 1)
        rules = [Rule.parse(s) for s in rest.split(",")]
        return cls(name, rules)

    def __post_init__(self) -> None:
        assert self.rules[-1].var is None  # last rule is a catch-all

    def __call__(self, part: Part) -> str:
        for rule in self.rules:
            if rule.match(part):
                return rule.dst
        raise RuntimeError


def accepted(workflows: dict[str, Workflow], part: Part, start: str) -> bool:
    cur = start
    while cur not in {"R", "A"}:
        cur = workflows[cur](part)
    return cur == "A"


@dataclass(frozen=True)
class Span:
    start: int
    end: int  # exclusive

    def length(self) -> int:
        return self.end - self.start

    def split(self, val: int) -> tuple[Self | None, Self | None]:
        if val <= self.start:
            return None, self
        if val >= self.end:
            return self, None
        return self.__class__(self.start, val), self.__class__(val, self.end)


@dataclass
class QPart:
    """A "quantum" Part, keeping track of _ranges_ of member values."""

    x: Span
    m: Span
    a: Span
    s: Span

    @classmethod
    def new(cls) -> Self:
        return cls(*[Span(1, 4001) for _ in range(4)])

    def distinct(self) -> int:
        return cast(
            int, prod(getattr(self, member).length() for member in "xmas")
        )

    def process(
        self, workflows: dict[str, Workflow], start: str
    ) -> Iterator[Self]:
        if start == "R":  # rejected!
            return
        if start == "A":  # accepted!
            yield self
            return

        wflow = workflows[start]
        for rule in wflow.rules:
            if rule.var is None:  # Follow unconditionally
                yield from self.process(workflows, rule.dst)
                break
            span = getattr(self, rule.var)
            if rule.op is gt:
                false_span, true_span = span.split(rule.val + 1)
            else:
                assert rule.op is lt
                true_span, false_span = span.split(rule.val)
            true_qpart = replace(self, **{rule.var: true_span})
            yield from true_qpart.process(workflows, rule.dst)
            setattr(self, rule.var, false_span)


with open("19.input") as f:
    par1, par2 = f.read().split("\n\n")
    workflow_list = [Workflow.parse(line) for line in par1.splitlines()]
    workflows = {wf.name: wf for wf in workflow_list}
    parts = [Part.parse(line) for line in par2.splitlines()]

# Part 1: What is the sum of rating numbers for all parts that get accepted?
print(sum(part.rating() for part in parts if accepted(workflows, part, "in")))

# Part 2: How many distinct combinations of ratings will be accepted?
qparts = list(QPart.new().process(workflows, "in"))
print(sum(qpart.distinct() for qpart in qparts))
