from dataclasses import dataclass
from typing import Self


@dataclass
class Cubes:
    red: int = 0
    green: int = 0
    blue: int = 0

    @classmethod
    def parse(cls, s: str) -> Self:
        """'6 red, 1 blue' -> Cubes(red=5, green=0, blue=1)."""
        ret = cls()
        for part in s.split(","):
            num, color = part.split()
            assert color in {"red", "green", "blue"}
            setattr(ret, color, int(num))
        return ret

    def possible(self, limit: Self) -> bool:
        """Test if this set of cubes is a subset of the given the limit."""
        return (
            self.red <= limit.red
            and self.green <= limit.green
            and self.blue <= limit.blue
        )

    def power(self) -> int:
        return self.red * self.green * self.blue


@dataclass
class Game:
    id: int  # noqa: A003
    draws: list[Cubes]

    @classmethod
    def parse(cls, line: str) -> Self:
        """Parse game from line.

        Input: "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"
        Output: Game(id=1, draws=[Cubes(4, 0, 3), Cubes(1, 2, 6), Cubes(0, 2)])
        """
        assert line.startswith("Game ")
        intro, draws = line.split(":", maxsplit=1)
        return cls(
            id=int(intro[5:]),
            draws=[Cubes.parse(s) for s in draws.split(";")],
        )

    def possible(self, limit: Cubes) -> bool:
        """Test if this game is possible, within the given the limit."""
        return all(draw.possible(limit) for draw in self.draws)

    def min_cubes(self) -> Cubes:
        """Least number of cubes needed for this game."""
        return Cubes(
            red=max(d.red for d in self.draws),
            green=max(d.green for d in self.draws),
            blue=max(d.blue for d in self.draws),
        )


with open("02.input") as f:
    games = [Game.parse(line) for line in f]

# Part 1: Sum of possible Game IDs
print(sum(game.id for game in games if game.possible(limit=Cubes(12, 13, 14))))

# Part 2: Sum of powers across all minimum sets of cubes in these games.
print(sum(game.min_cubes().power() for game in games))
