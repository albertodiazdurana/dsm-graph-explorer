"""Configuration loader with Pydantic validation.

Loads and validates configuration from YAML files for DSM Graph Explorer.
Supports exclusion patterns, severity mappings, and validation options.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

# Default config file name
CONFIG_FILENAME = ".dsm-graph-explorer.yml"

# Severity levels
SeverityLevel = Literal["ERROR", "WARNING", "INFO"]


class SeverityMapping(BaseModel):
    """Maps a file pattern to a severity level."""

    pattern: str = Field(description="Glob pattern to match files")
    level: SeverityLevel = Field(description="Severity level for matched files")

    @field_validator("pattern")
    @classmethod
    def pattern_not_empty(cls, v: str) -> str:
        """Ensure pattern is not empty."""
        if not v.strip():
            raise ValueError("Pattern cannot be empty")
        return v


class Config(BaseModel):
    """Configuration for DSM Graph Explorer validation."""

    exclude: list[str] = Field(
        default_factory=list,
        description="List of glob patterns to exclude from validation",
    )
    severity: list[SeverityMapping] = Field(
        default_factory=list,
        description="Severity level mappings by file pattern",
    )
    strict: bool = Field(
        default=False,
        description="Exit with code 1 if any ERROR-level issues found",
    )
    default_severity: SeverityLevel = Field(
        default="WARNING",
        description="Default severity for files not matching any pattern",
    )

    @field_validator("exclude")
    @classmethod
    def exclude_patterns_not_empty(cls, v: list[str]) -> list[str]:
        """Filter out empty patterns."""
        return [p for p in v if p.strip()]


class ConfigError(Exception):
    """Raised when configuration loading or validation fails."""

    pass


def find_config_file(start_path: Path | None = None) -> Path | None:
    """Find config file by searching current directory and parents.

    Args:
        start_path: Directory to start search from. Defaults to current directory.

    Returns:
        Path to config file if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()

    start_path = Path(start_path).resolve()

    # If start_path is a file, start from its parent directory
    if start_path.is_file():
        start_path = start_path.parent

    # Search current directory and parents
    current = start_path
    while True:
        config_path = current / CONFIG_FILENAME
        if config_path.is_file():
            return config_path

        # Stop at filesystem root
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def load_config(
    config_path: Path | str | None = None,
    start_path: Path | None = None,
) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Explicit path to config file. If None, searches for
            CONFIG_FILENAME in start_path and parent directories.
        start_path: Directory to start search from. Only used if config_path is None.

    Returns:
        Config object with validated settings.

    Raises:
        ConfigError: If config file exists but is invalid YAML or fails validation.
    """
    # Explicit path takes precedence
    if config_path is not None:
        config_path = Path(config_path)
        if not config_path.is_file():
            raise ConfigError(f"Config file not found: {config_path}")
    else:
        # Search for config file
        config_path = find_config_file(start_path)

    # No config file found - return defaults
    if config_path is None:
        return Config()

    # Load and parse YAML
    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {config_path}: {e}") from e

    # Handle empty file
    if data is None:
        return Config()

    # Validate with Pydantic
    try:
        return Config(**data)
    except Exception as e:
        raise ConfigError(f"Invalid configuration in {config_path}: {e}") from e


def merge_config_with_cli(
    config: Config,
    cli_exclude: tuple[str, ...] | None = None,
    cli_strict: bool | None = None,
) -> Config:
    """Merge config file settings with CLI overrides.

    CLI options take precedence over config file settings.

    Args:
        config: Base configuration from file.
        cli_exclude: Exclusion patterns from CLI (added to config patterns).
        cli_strict: Strict mode from CLI (overrides config if True).

    Returns:
        New Config with merged settings.
    """
    # Start with config values
    exclude = list(config.exclude)
    strict = config.strict

    # CLI exclusions are added to config exclusions
    if cli_exclude:
        exclude.extend(cli_exclude)

    # CLI strict overrides config (only if explicitly set to True)
    if cli_strict is True:
        strict = True

    return Config(
        exclude=exclude,
        severity=config.severity,
        strict=strict,
        default_severity=config.default_severity,
    )
