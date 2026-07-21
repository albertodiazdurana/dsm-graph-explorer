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


class LintConfig(BaseModel):
    """Configuration for convention linting rules."""

    severity_overrides: dict[str, SeverityLevel] = Field(
        default_factory=dict,
        description="Per-rule severity overrides, e.g. {'W001': 'ERROR'}",
    )

    @field_validator("severity_overrides")
    @classmethod
    def validate_rule_keys(cls, v: dict[str, SeverityLevel]) -> dict[str, SeverityLevel]:
        """Ensure rule keys look like valid lint rule codes."""
        valid_prefixes = ("E", "W")
        for key in v:
            if not (len(key) == 4 and key[0] in valid_prefixes and key[1:].isdigit()):
                raise ValueError(f"Invalid lint rule code: {key}")
        return v


DEFAULT_EXCLUDES: list[str] = [
    "**/.venv/**",
    "**/site-packages/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/.pytest_cache/**",
    "**/.claude/transcripts/**",
]
"""Directories excluded from validation and graph building by default.

These are dependency, cache, and agent-session directories whose markdown is
not project knowledge. Without them, `--knowledge-summary` on this repository
emitted 16 of 57 directories from `.venv/` and `.pytest_cache/`, so clustering
(BL-302 Phase 2) would have grouped dependency license files as project
concepts.

Every entry uses the `**/X/**` form deliberately. `should_exclude` matches
segment-by-segment via `_match_segments`, which requires an equal segment
count, so a bare `.venv` matches nothing nested and `.venv/*` matches only
direct children. The short forms would silently exclude nothing.

`build/` and `dist/` are intentionally absent: they are plausible dependency
directories but equally plausible project directories, and a false exclusion
loses content silently. `.claude/` is excluded narrowly, transcripts are
dropped while `.claude/CLAUDE.md` stays indexed.

Disable with `use_default_excludes: false` in config, or `--no-default-excludes`.
"""


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
    semantic_threshold: float = Field(
        default=0.08,
        description="Minimum TF-IDF cosine similarity for semantic alignment (DEC-005)",
    )
    semantic_min_tokens: int = Field(
        default=3,
        description="Minimum meaningful tokens required for semantic comparison",
    )
    lint: LintConfig = Field(
        default_factory=LintConfig,
        description="Convention linting configuration",
    )
    use_default_excludes: bool = Field(
        default=True,
        description="Apply DEFAULT_EXCLUDES (dependency/cache/transcript dirs) on top of `exclude`",
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
    cli_no_default_excludes: bool = False,
) -> Config:
    """Merge config file settings with CLI overrides.

    CLI options take precedence over config file settings.

    Args:
        config: Base configuration from file.
        cli_exclude: Exclusion patterns from CLI (added to config patterns).
        cli_strict: Strict mode from CLI (overrides config if True).
        cli_no_default_excludes: If True, suppress DEFAULT_EXCLUDES
            (overrides the config's ``use_default_excludes``).

    Returns:
        New Config with merged settings.
    """
    # Start with config values
    exclude = list(config.exclude)
    strict = config.strict
    use_defaults = config.use_default_excludes and not cli_no_default_excludes

    # CLI exclusions are added to config exclusions
    if cli_exclude:
        exclude.extend(cli_exclude)

    # Default exclusions are added last so user patterns stay visible first.
    # Applied here rather than at the call site so every consumer of a merged
    # Config (validation, graph build, knowledge summary) gets them.
    if use_defaults:
        exclude.extend(p for p in DEFAULT_EXCLUDES if p not in exclude)

    # CLI strict overrides config (only if explicitly set to True)
    if cli_strict is True:
        strict = True

    return Config(
        exclude=exclude,
        severity=config.severity,
        strict=strict,
        default_severity=config.default_severity,
        semantic_threshold=config.semantic_threshold,
        semantic_min_tokens=config.semantic_min_tokens,
        lint=config.lint,
        use_default_excludes=use_defaults,
    )
