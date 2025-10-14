from dataclasses import dataclass, field
from pathlib import Path
import yaml
from typing import List, Optional, Dict, Any

from dbferry.core.console import Printer as p


# -----------------------------
# Dataclasses for structure
# -----------------------------


@dataclass
class DBConfig:
    type: str
    host: str
    port: Optional[int]
    database: str
    user: str
    password: str
    sslmode: str

    def normalized(self):
        """default ports depending on DB type."""
        defaults = {
            "postgres": 5432,
            "mysql": 3306,
            "sqlite": None,
        }
        if self.port is None:
            self.port = defaults.get(self.type)
        return self


@dataclass
class OptionsConfig:
    tables: List[str] = field(default_factory=lambda: ["*"])
    verify_after_migration: bool = True


@dataclass
class MigrationConfig:
    source: DBConfig
    target: DBConfig
    options: OptionsConfig


# -----------------------------
# Config loader logic
# -----------------------------


class ConfigLoader:
    """Responsible for loading, validating, and normalizing migration.yml"""

    @staticmethod
    def load(path: str | Path) -> MigrationConfig:
        path = Path(path)
        if not path.exists():
            p.error(f"Config file not found: {path}")
            raise FileNotFoundError(path)

        try:
            data = yaml.safe_load(path.read_text())
        except Exception as e:
            p.error(f"Failed to parse YAML: {e}")
            raise

        try:
            # Validate required structure
            source = ConfigLoader._validate_db_block(data.get("source"), "source")
            target = ConfigLoader._validate_db_block(data.get("target"), "target")

            options = data.get("options", {})
            opts = OptionsConfig(
                tables=options.get("tables", ["*"]),
                verify_after_migration=options.get("verify_after_migration", True),
            )

            return MigrationConfig(
                source=source.normalized(),
                target=target.normalized(),
                options=opts,
            )

        except Exception as e:
            p.error(f"Invalid configuration: {e}")
            raise

    @staticmethod
    def _validate_db_block(block: Dict[str, Any], label: str) -> DBConfig:
        if not block:
            raise ValueError(f"Missing '{label}' section in config")

        required = ["type", "host", "database", "user", "password"]
        missing = [k for k in required if k not in block]
        if missing:
            raise ValueError(f"Missing keys in {label}: {', '.join(missing)}")

        return DBConfig(
            type=block["type"],
            host=block["host"],
            port=block.get("port"),
            database=block["database"],
            user=block["user"],
            password=block["password"],
            sslmode=block["sslmode"],
        )
