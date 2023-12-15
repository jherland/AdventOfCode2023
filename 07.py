from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from functools import total_ordering
from typing import Self


class Card(IntEnum):
    JOKER = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    T = 10
    J = 11
    Q = 12
    K = 13
    A = 14

    @classmethod
    def parse(cls, c: str) -> Self:
        try:
            return cls.__members__[c]
        except KeyError:
            return cls.__members__["_" + c]

    def __str__(self) -> str:
        return self.name.lstrip("_")


@total_ordering
@dataclass(frozen=True)
class Hand:
    cards: tuple[Card, ...]
    bid: int

    @classmethod
    def parse(cls, line: str) -> Self:
        cards, bid = line.split()
        return cls(tuple(Card.parse(c) for c in cards), int(bid))

    def with_jokers(self) -> Self:
        """Convert this hand from J -> JOKER."""
        return self.__class__(
            tuple(
                Card.JOKER if card == Card.J else card for card in self.cards
            ),
            self.bid,
        )

    def strength(self) -> int:
        c = Counter(self.cards)
        assert c.total() == 5
        jokers = c.pop(Card.JOKER, 0)
        # Look at two highest counts
        first, second, *_ = [count for _, count in c.most_common(2)] + [0, 0]
        first += jokers
        # Concatenate digits to get strength: f"{first}{second}"
        # Five of a kind -> 50
        # Four of a kind -> 41
        # Full house -> 32
        # Three of a kind -> 31
        # Two pair -> 22
        # One pair -> 21
        # High card -> 11
        return first * 10 + second

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.strength(), self.cards) < (other.strength(), other.cards)

    def __str__(self) -> str:
        return (
            "".join(str(card) for card in self.cards)
            + f" /{self.bid}*{self.strength()}"
        )


with open("07.input") as f:
    hands = [Hand.parse(line) for line in f]

# Part 1: What are the total winnings from the given hands?
hands.sort()
print(sum(hand.bid * rank for rank, hand in enumerate(hands, start=1)))

# Part 2: What are the total winnings from the given hands with J -> Joker?
hands = sorted(hand.with_jokers() for hand in hands)
print(sum(hand.bid * rank for rank, hand in enumerate(hands, start=1)))
