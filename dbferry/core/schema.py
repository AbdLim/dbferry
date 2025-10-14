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
    columns: list[ColumnSchema]
    primary_key: list[str] | None = None
    unique_keys: list["UniqueKeySchema"] | None = None
    foreign_keys: list["ForeignKeySchema"] | None = None


@dataclass
class ForeignKeySchema:
    column: str
    ref_table: str
    ref_column: str


@dataclass
class UniqueKeySchema:
    columns: list[str]


@dataclass
class EnumType:
    name: str
    values: list[str]
