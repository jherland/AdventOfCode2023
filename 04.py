from dataclasses import dataclass
from typing import Self


@dataclass
class Card:
    id: int  # noqa: A003
    winning: set[int]
    have: set[int]
    instances: int = 1

    @classmethod
    def parse(cls, line: str) -> Self:
        assert line.startswith("Card ")
        intro, rest = line.split(":")
        winning, have = rest.split("|")
        return cls(
            id=int(intro.split()[-1]),
            winning={int(word) for word in winning.split()},
            have={int(word) for word in have.split()},
        )

    def wins(self) -> set[int]:
        return self.winning & self.have

    def points(self) -> int:
        num_wins = len(self.wins())
        return int(2 ** (num_wins - 1)) if num_wins else 0


with open("04.input") as f:
    cards = [Card.parse(line) for line in f]

# Part 1: How many points are the cards worth in total?
print(sum(card.points() for card in cards))

# Part 2: How many total scratchcards do you end up with?
for card in cards:
    for ncard in cards[card.id : card.id + len(card.wins())]:
        ncard.instances += card.instances
print(sum(card.instances for card in cards))
