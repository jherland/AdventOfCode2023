from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Pulse:
    src: str
    dst: str
    state: bool

    def __str__(self) -> str:
        return f"{self.src} -{"high" if self.state else "low"}-> {self.dst}"


@dataclass
class Module:
    name: str
    outputs: list[str]

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        """Receive/process an incoming pulse."""
        assert pulse.dst == self.name
        # print(pulse)
        return iter(())  # empty generator

    def _send(self, state: bool) -> Iterator[Pulse]:
        """Generate output pulses to all of self's outputs."""
        for out in self.outputs:
            yield Pulse(self.name, out, state)


@dataclass
class Broadcaster(Module):
    def __post_init__(self) -> None:
        assert self.name == "broadcaster"

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        yield from self._send(pulse.state)


@dataclass
class FlipFlop(Module):
    state: bool = False

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        if pulse.state is False:
            self.state = not self.state
            yield from self._send(self.state)


@dataclass
class Conjunction(Module):
    inputs: dict[str, bool]

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        self.inputs[pulse.src] = pulse.state
        out_pulse = not all(inp is True for inp in self.inputs.values())
        yield from self._send(out_pulse)


@dataclass
class Output(Module):
    def __post_init__(self) -> None:
        assert not self.outputs


@dataclass
class Circuit:
    modules: dict[str, Module]
    high_pulses: int = 0
    low_pulses: int = 0
    rx_low_pulses: int = 0

    @staticmethod
    def parse_one(line: str) -> Module:
        mod_name, connections = line.rstrip().split(" -> ")
        out_modules = connections.split(", ")
        if mod_name == "broadcaster":
            return Broadcaster(mod_name, out_modules)
        if mod_name.startswith("%"):  # flip-flop
            return FlipFlop(mod_name[1:], out_modules)
        if mod_name.startswith("&"):  # conjunction
            return Conjunction(mod_name[1:], out_modules, {})  # no inputs yet
        raise ValueError(line)

    @classmethod
    def parse(cls, lines: Iterable[str]) -> Self:
        modules = {m.name: m for m in (cls.parse_one(line) for line in lines)}
        for mod_name in list(modules.keys()):
            module = modules[mod_name]
            for out_name in module.outputs:
                target = modules.get(out_name)
                if target is None:  # auto-create Output module
                    modules[out_name] = Output(out_name, [])
                elif isinstance(target, Conjunction):
                    target.inputs[module.name] = False  # supply inputs here
        return cls(modules)

    def _process_pulses(self, pulse: Pulse) -> None:
        pulses = deque([pulse])
        while pulses:
            pulse = pulses.popleft()
            pulses.extend(self.modules[pulse.dst].pulse(pulse))
            if pulse.state:
                self.high_pulses += 1
            else:
                self.low_pulses += 1
                if pulse.dst == "rx":
                    self.rx_low_pulses += 1

    def push_button(self) -> None:
        self._process_pulses(Pulse("button", "broadcaster", False))


with open("20.input") as f:
    lines = f.readlines()

# Part 1: What do you get if you multiply #LOW pulses and #HIGH pulses?
circuit = Circuit.parse(lines)
for _ in range(1000):
    circuit.push_button()
print(circuit.high_pulses * circuit.low_pulses)

# Part 2: What is the fewest number of button presses single LOW  pulse to "rx"?
print(circuit.rx_low_pulses)
circuit = Circuit.parse(lines)
n = 0
while circuit.rx_low_pulses == 0:
    circuit.push_button()
    n += 1
assert circuit.rx_low_pulses == 1
print(n)
