from dataclasses import dataclass, field


@dataclass
class SimulationResults:
    empirical_p: list[int] = field(default_factory=list)
    busy_channels: int = field(default=0)
    Q: int = field(default=0)
    A1: int = field(default=0)
    A2: int = field(default=0)
    p_reject1: int = field(default=0)
    p_reject2: int = field(default=0)
    p_reject: int = field(default=0)