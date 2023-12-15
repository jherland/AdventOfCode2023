from collections.abc import Iterator
from contextlib import suppress
from functools import reduce


def hash(s: str) -> int:
    return reduce(lambda acc, c: ((acc + ord(c)) * 17) % 256, s, 0)


def process_init_sequence(init_sequence: list[str]) -> list[dict[str, int]]:
    ret: list[dict[str, int]] = [{} for _ in range(256)]
    for step in init_sequence:
        flen: int | None = None
        try:
            label, rest = step.split("=")
            flen = int(rest)
        except ValueError:
            assert step.endswith("-")
            label = step[:-1]
        box = hash(label)
        if flen is None:
            with suppress(KeyError):
                ret[box].pop(label)
        else:
            ret[box][label] = flen
    return ret


def focusing_powers(boxes: list[dict[str, int]]) -> Iterator[int]:
    for n, box in enumerate(boxes, start=1):
        for slot, flen in enumerate(box.values(), start=1):
            yield n * slot * flen


with open("15.input") as f:
    init_sequence = f.read().rstrip().split(",")

# Part 1: What is the sum of the hashes for each initialization step?
print(sum(hash(s) for s in init_sequence))

# Part 2: What is the focusing power of the resulting lens configuration?
print(sum(focusing_powers(process_init_sequence(init_sequence))))
