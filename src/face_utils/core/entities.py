from dataclasses import asdict
from dataclasses import dataclass
from typing import Dict


@dataclass
class Entity:
    @property
    def as_dict(self) -> Dict:
        return asdict(self)
