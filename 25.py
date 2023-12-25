import random
from itertools import chain

Node = str
Edge = tuple[Node, Node]
Graph = tuple[set[Node], list[Edge]]


def contract(graph: Graph, t: int = 2) -> Graph:
    # Karger's algorithm
    nodes, edges = graph
    nodes = set(nodes)
    edges = list(edges)
    while len(nodes) > t:
        # Choose a random edge, and remove it
        e = edges.pop(random.randrange(len(edges) // 2))
        # Collapse nodes into a single, composite node
        a, b = e
        ab = f"{a}/{b}"
        nodes.remove(a)
        nodes.remove(b)
        nodes.add(ab)
        edges = [
            (ab if c in {a, b} else c, ab if d in {a, b} else d)
            for c, d in edges
            if not (c in {a, b} and d in {a, b})
        ]
        edges.sort(key=lambda e: len(str(e)))

    return nodes, edges


with open("25.input") as f:
    conns: dict[Node, set[Node]] = {}
    for line in f:
        first, seconds = line.split(":")
        conns[first] = set(seconds.split())

edges: list[Edge] = [(a, b) for a, bs in conns.items() for b in bs]
nodes: set[Node] = set(chain.from_iterable(edges))

# Part 1: What is the product of sizes of these two groups separated by 3 wires?
min_cut: list[Edge] = []
while len(min_cut) != 3:
    _, min_cut = contract((nodes, edges))
a, b = min_cut[0]
print(len(a.split("/")) * len(b.split("/")))
