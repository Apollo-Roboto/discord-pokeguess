from dataclasses import dataclass

@dataclass
class Status:
	ready: str
	cpu: float
	ram: float
