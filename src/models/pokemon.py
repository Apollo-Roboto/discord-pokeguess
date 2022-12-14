from pathlib import Path
from dataclasses import dataclass

@dataclass
class Pokemon:
	name: str
	id: int
	hidden_img_path: Path
	revealed_img_path: Path
