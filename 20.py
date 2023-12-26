from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from math import prod
from typing import Self

DEBUG = False


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
        if DEBUG:
            print(pulse)
        return iter(())  # empty generator

    def _send(self, *, state: bool) -> Iterator[Pulse]:
        """Generate output pulses to all of self's outputs."""
        for out in self.outputs:
            yield Pulse(self.name, out, state)


@dataclass
class Broadcaster(Module):
    def __post_init__(self) -> None:
        assert self.name == "broadcaster"

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        yield from self._send(state=pulse.state)


@dataclass
class FlipFlop(Module):
    state: bool = False

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        if pulse.state is False:
            if DEBUG:
                transition = "high->low" if self.state else "low->high"
                print(f"  {self.name}[{transition}]")
            self.state = not self.state
            yield from self._send(state=self.state)


@dataclass
class Conjunction(Module):
    inputs: dict[str, bool]

    def pulse(self, pulse: Pulse) -> Iterator[Pulse]:
        super().pulse(pulse)
        self.inputs[pulse.src] = pulse.state
        out_pulse = not all(inp is True for inp in self.inputs.values())
        yield from self._send(state=out_pulse)


@dataclass
class Output(Module):
    def __post_init__(self) -> None:
        assert not self.outputs


@dataclass
class Circuit:
    modules: dict[str, Module]
    probes: dict[str, int] = field(default_factory=dict)
    high_pulses: int = 0
    low_pulses: int = 0

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
                if pulse.src in self.probes:
                    self.probes[pulse.src] += 1

    def push_button(self) -> None:
        self._process_pulses(Pulse("button", "broadcaster", state=False))

    def find_next_conjunction(self, module: str) -> str:
        if isinstance(self.modules[module], Conjunction):
            return module
        return self.find_next_conjunction(self.modules[module].outputs[0])

    def set_probe(self, probe: str) -> None:
        self.probes[probe] = 0

    def remove_probe(self, probe: str) -> None:
        del self.probes[probe]


with open("20.input") as f:
    lines = f.readlines()

# Part 1: What do you get if you multiply #LOW pulses and #HIGH pulses?
circuit = Circuit.parse(lines)
for _ in range(1000):
    circuit.push_button()
print(circuit.high_pulses * circuit.low_pulses)

# Part 2: What is the fewest number of button presses single LOW  pulse to "rx"?
#
# From analyzing the circuit in 20.analysis.svg, we see that we have 4 separate
# networks, each consisting of 12 FlipFlops feeding into each other, as well as
# connecting to and from a Conjunction. The four networks are fed LOW pulses
# from the "broadcaster", and the Conjunction at the end connect via another
# Conjunction (functioning as a NOT gate) before finally combining in a final
# Conjuctions connected to the "rx" output.
#
# Each network represent a 12-bit counter that will only emit a LOW pulse when
# the correct number of LOW pulses from the "broadcaster" have caused all
# FlipFlops in the network to reach their HIGH state and wrap around. Due to the
# various interconnections within each network, this happens BEFORE 2**12
# (=4096) is reached. Each network will count a prime(?) number of incoming LOW
# pulses before emitting a single LOW pulse and reset.
#
# The final combination of Conjunction modules cause the first LOW pulse to "rx"
# only to happen when ALL 4 networks are outputting a LOW pulse, i.e. after the
# least common multiple of each of their counters have been reached.
#
# We solve this by analyzing each of the 4 networks separately to determine
# these 4 12-bit counter values, and the end result is the product of these
# counters.
circuit = Circuit.parse(lines)

# Identify the 4 networks by following the connections from the "broadcaster"
# until we find a Conjunction node.
for module in circuit.modules["broadcaster"].outputs:
    circuit.set_probe(circuit.find_next_conjunction(module))

# Keep pushing button until each network has emitted one LOW pulse each
periods = []
n = 0
while circuit.probes:
    circuit.push_button()
    n += 1
    triggered = {name for name, count in circuit.probes.items() if count > 0}
    for name in triggered:
        periods.append(n)
        circuit.remove_probe(name)

# Multiply periods together to get overall answer
print(prod(periods))
