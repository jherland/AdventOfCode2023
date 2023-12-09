from collections.abc import Iterable, Iterator


def derivative(seq: Iterable[int]) -> Iterator[int]:
    it = iter(seq)
    prev = next(it)
    for cur in it:
        yield cur - prev
        prev = cur


def next_value(seq: list[int]) -> int:
    if all(n == 0 for n in seq):
        return 0
    return seq[-1] + next_value(list(derivative(seq)))


with open("09.input") as f:
    sequences = [[int(n) for n in line.split()] for line in f]

# Part 1: What is the sum of these extrapolated values?
print(sum(next_value(seq) for seq in sequences))

# Part 2: What is the sum of these extrapolated values, going the other way?
print(sum(next_value(list(reversed(seq))) for seq in sequences))
