from math import ceil, floor, prod, sqrt

def break_record(race_time: int, record: int) -> (int, int):
    """Return lower/upper bound for charge time that will break record.

    Find the range of charge times where the resulting distance > record.
    """
    root = sqrt(race_time ** 2 - 4 * (record + 1))
    return (ceil((race_time - root) / 2), floor((race_time + root) / 2))


def count_record_breaks(race_time: int, record: int) -> int:
    lower, upper = break_record(race_time, record)
    return upper + 1 - lower


with open("06.input") as f:
    first = f.readline()
    assert first.startswith("Time:")
    second = f.readline()
    assert second.startswith("Distance:")

# Part 1: Product of the number of ways to beat the record in each race
times = [int(num) for num in first.split(":")[1].split()]
records = [int(num) for num in second.split(":")[1].split()]
races = zip(times, records)
print(prod(count_record_breaks(race_time, record) for race_time, record in races))

# Part 2: One bug race
time = int(first.split(":")[1].replace(" ", ""))
record = int(second.split(":")[1].replace(" ", ""))
print(count_record_breaks(time, record))
