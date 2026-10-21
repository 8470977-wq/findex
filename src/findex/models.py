from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass(frozen=True, slots=True)
class Posting:
    doc_id: int
    tf: int  # Term Frequency (частота терміну у документі)
    positions: Optional[List[int]] = None  # Позиції токенів (опційно)

@dataclass(frozen=True, slots=True)
class DocMeta:
    doc_id: int
    path: str
    length: int  # Загальна кількість токенів у документі
