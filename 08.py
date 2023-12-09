from collections.abc import Callable, Iterator
from itertools import cycle
from math import lcm

with open("08.input") as f:
    recipe = [{"L": 0, "R": 1}[c] for c in f.readline().strip()]
    nodes = {}
    for line in f:
        if not line.strip():
            continue
        node, children = line.split("=")
        child1, child2 = children.strip().split(",")
        assert child1.startswith("(")
        assert child2.endswith(")")
        nodes[node.strip()] = (child1[1:].strip(), child2[:-1].strip())


def steps_until(
    instructions: Iterator[int], start: str, pred: Callable[[str], bool]
) -> (str, int):
    """Traverse nodes from start following instructions until pred is True."""
    current = start
    steps = 0
    while not pred(current):
        steps += 1
        current = nodes[current][next(instructions)]
    return current, steps


def period(start: str, pred: Callable[[str], bool]) -> Iterator[int]:
    instructions = cycle(recipe)
    current = start
    total = 0
    while True:
        current, steps = steps_until(instructions, current, pred)
        total += steps
        yield total
        if total % len(recipe) == 0:  # found period
            return


# Part 1: How many steps are required to reach ZZZ?
print(steps_until(cycle(recipe), "AAA", lambda node: node == "ZZZ")[1])

# Part 2: How many steps before you're only on nodes that end with Z?
a_nodes = {node for node in nodes if node.endswith("A")}
periods = {
    a_node: list(period(a_node, lambda node: node.endswith("Z")))
    for a_node in a_nodes
}
assert all(len(p) == 1 for p in periods.values())
print(lcm(*[p[0] for p in periods.values()]))
