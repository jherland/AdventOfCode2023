from functools import cache

Groups = tuple[int, ...]


def parse(line: str) -> tuple[str, Groups]:
    s, groups = line.split()
    return s, tuple(int(n) for n in groups.split(","))


@cache
def count_alternatives(clusters: tuple[str, ...], groups: Groups) -> int:
    if not groups:
        # We're out of required springs. This is only a valid alternative iff
        # there are no more springs in clusters
        return 0 if any("#" in cluster for cluster in clusters) else 1
    if not clusters:
        # We're out of clusters, but there are required springs left. Fail.
        return 0

    # Match first group against first cluster
    group = groups[0]
    cluster = clusters[0]

    if group > len(cluster) and "#" in cluster:
        # Cannot use this cluster, too few springs, and it cannot be skipped.
        return 0

    total = 0
    for i in range(len(cluster) - group + 1):
        # Try to isolate a sub-cluster that satisfies group. The part to the
        # left of the sub-cluster cannot have any "#", and the part to the right
        # cannot start with "#".
        left, right = cluster[:i], cluster[i + group :]
        if "#" in left or right.startswith("#"):
            continue
        # cluster[i:i + group] satisfies group, keep searching to the right
        total += count_alternatives(
            (right[1:], *clusters[1:]) if len(right) > 1 else clusters[1:],
            groups[1:],
        )

    if "#" not in cluster:
        # Entire cluster is optional, pretend it does not exist
        total += count_alternatives(clusters[1:], groups)

    return total


def num_matching_springs(input: str, groups: Groups) -> int:
    return count_alternatives(tuple(s for s in input.split(".") if s), groups)


def unfold(springs: tuple[str, Groups], times: int) -> tuple[str, Groups]:
    s, nums = springs
    return "?".join([s] * times), nums * times


with open("12.input") as f:
    springs = [parse(line) for line in f]

# Part 1: What is the sum of counts of all the different good arrangements?
print(sum(num_matching_springs(s, groups) for s, groups in springs))

# Part 2: What is the sum of counts of all the unfolded good arrangements?
springs = [unfold(s, 5) for s in springs]
print(sum(num_matching_springs(s, groups) for s, groups in springs))
