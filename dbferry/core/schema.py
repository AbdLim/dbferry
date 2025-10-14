from dataclasses import dataclass
from typing import List


@dataclass
class ColumnSchema:
    name: str
    type: str
    nullable: bool
    default: str | None = None


@dataclass
class TableSchema:
    name: str
    columns: List[ColumnSchema]
