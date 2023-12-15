from functools import cache

Platform = tuple[str, ...]


@cache
def tilt_line(line: str) -> str:
    return "#".join(
        "".join(["O"] * word.count("O") + ["."] * word.count("."))
        for word in line.split("#")
    )


def tilt_left(platform: Platform) -> Platform:
    return tuple(tilt_line(line) for line in platform)


def rotate_ccw(platform: Platform) -> Platform:
    line_len = len(platform[0])
    return tuple(
        "".join(line[x] for line in platform) for x in reversed(range(line_len))
    )


def rotate_cw(platform: Platform) -> Platform:
    line_len = len(platform[0])
    return tuple(
        "".join(line[x] for line in reversed(platform)) for x in range(line_len)
    )


def rotate_180(platform: Platform) -> Platform:
    return tuple("".join(reversed(line)) for line in reversed(platform))


def tilt_north(platform: Platform) -> Platform:
    # Turn CCW to have N face left, tilt, and turn back again
    return rotate_cw(tilt_left(rotate_ccw(platform)))


def total_load_on_N_support_beam(platform: Platform) -> int:  # noqa: N802
    total = 0
    height = len(platform)
    for y, line in enumerate(platform):
        total += line.count("O") * (height - y)
    return total


def one_cycle(platform: Platform) -> Platform:
    platform = rotate_ccw(platform)  # N -> left
    platform = tilt_left(platform)
    platform = rotate_cw(platform)  # W -> left
    platform = tilt_left(platform)
    platform = rotate_cw(platform)  # S -> left
    platform = tilt_left(platform)
    platform = rotate_cw(platform)  # E -> left
    platform = tilt_left(platform)
    return rotate_180(platform)  # W -> left


def cycles(platform: Platform, n: int) -> Platform:
    seen = {platform: n}
    period = None
    while n > 0:
        platform = one_cycle(platform)
        n -= 1
        if platform not in seen:  # still searching
            seen[platform] = n
        elif period is None:  # found period
            period = seen[platform] - n
            n %= period
    return platform


with open("14.input") as f:
    platform = tuple(line.rstrip() for line in f)  # Lines go N->S, W faces left
    assert len({len(line) for line in platform}) == 1  # same length lines

# Part 1: What is the total load on the north support beams?
print(total_load_on_N_support_beam(tilt_north(platform)))

# Part 2: What is the total load on the north support beams after 1B cycles?
print(total_load_on_N_support_beam(cycles(platform, 1_000_000_000)))
