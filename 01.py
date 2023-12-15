from collections.abc import Iterable, Iterator

WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def digits(s: str, *, spelled: bool = False) -> Iterator[int]:
    digits = {str(d): d for d in range(1, 10)}
    if spelled:
        digits |= {word: num for num, word in enumerate(WORDS, start=1)}
    while s:
        for k, v in digits.items():
            if s.startswith(k):
                yield v
        s = s[1:]


def first_and_last_digits(digits: Iterable[int]) -> int:
    it = iter(digits)
    first = last = next(it)
    for item in it:
        last = item
    return first * 10 + last


with open("01.input") as f:
    lines = list(f)

# Part 1: What is the sum of all of the calibration values?
print(sum(first_and_last_digits(digits(line)) for line in lines))

# Part 2: What is the sum of calibration values (incl. spelled-out digits)?
print(sum(first_and_last_digits(digits(line, spelled=True)) for line in lines))
