from dataclasses import dataclass, field


@dataclass
class TheoreticalResults:
    p: list[int] = field(default_factory=list)
    busy_channels: int = field(default=0)
    Q: int = field(default=0)
    A: int = field(default=0)