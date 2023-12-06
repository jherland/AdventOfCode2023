from math import ceil, floor, prod, sqrt

# d = t * v         # distance traveled
# t = T - x         # run time is total time minus charge time
# v = x             # speed == charge time
# d = (T - x) * x
# d = -x^2 + Tx     # travel distance as function of charge time
#
# Max travel distance is found where the d/dx derivative is crosses zero:
# d/dx(-x^2 + Tx) = 0
# -2x + T = 0
# x = T/2
#
# Lower/upper bound of record-breaking times is found by solving for x where
# d is fixed to the current record.
# - Start with the quadratic formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a
# - Our formula is: x^2 - Tx + d = 0, hence:
# 
# x = (T +/- sqrt(T^2 - 4d)) / 2
# x_lower = (T - sqrt(T^2 - 4d)) / 2
# x_upper = (T + sqrt(T^2 - 4d)) / 2


def dist(race_time: int, charge_time: int) -> int:
    """Evaluate distance formula: d = -x^2 + Tx."""
    return (race_time - charge_time) * charge_time


def max_dist(race_time: int) -> int:
    """Return charge time for max travel distance."""
    return race_time // 2


def break_record(race_time: int, record: int) -> (int, int):
    """Return lower/upper bound for charge time that will break record.

    Find the range of charge times where the distance formula yields results
    greater than the given record.
    """
    assert dist(race_time, max_dist(race_time)) > record  # We _can_ beat it
    # x = (T +/- sqrt(T^2 - 4d)) / 2
    root = sqrt(race_time ** 2 - 4 * (record + 1))  # We want at least record + 1
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
