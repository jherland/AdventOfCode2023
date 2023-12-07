from typing import Iterable, Iterator

WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def digits(s: str, *, parse_spelled: bool = False) -> Iterator[int]:
    digits = {str(d): d for d in range(1, 10)}
    if parse_spelled:
        digits |= {word: num for num, word in enumerate(WORDS, start=1)}
    while s:
        for k, v in digits.items():
            if s.startswith(k):
                yield v
        s = s[1:]


def first_and_last[T](iterable: Iterable[T]) -> (T, T):
    it = iter(iterable)
    first = last = next(it)
    for item in it:
        last = item
    return first * 10 + last


with open("01.input") as f:
    lines = list(f)

# Part 1: What is the sum of all of the calibration values?
print(sum(first_and_last(digits(line)) for line in lines))

# Part 2: What is the sum of calibration values (incl. spelled-out digits)?
print(sum(first_and_last(digits(line, parse_spelled=True)) for line in lines))
