"""Tests for configuration loading and validation."""

import pytest
from pathlib import Path

from config.config_loader import (
    Config,
    ConfigError,
    SeverityMapping,
    find_config_file,
    load_config,
    merge_config_with_cli,
    CONFIG_FILENAME,
)


class TestSeverityMapping:
    """Tests for SeverityMapping model."""

    def test_valid_severity_mapping(self):
        """Valid pattern and level creates mapping."""
        mapping = SeverityMapping(pattern="*.md", level="ERROR")
        assert mapping.pattern == "*.md"
        assert mapping.level == "ERROR"

    def test_all_severity_levels(self):
        """All severity levels are accepted."""
        for level in ["ERROR", "WARNING", "INFO"]:
            mapping = SeverityMapping(pattern="test/*", level=level)
            assert mapping.level == level

    def test_empty_pattern_rejected(self):
        """Empty pattern raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SeverityMapping(pattern="", level="ERROR")

    def test_whitespace_pattern_rejected(self):
        """Whitespace-only pattern raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SeverityMapping(pattern="   ", level="ERROR")

    def test_invalid_severity_level_rejected(self):
        """Invalid severity level raises validation error."""
        with pytest.raises(ValueError):
            SeverityMapping(pattern="*.md", level="CRITICAL")


class TestConfig:
    """Tests for Config model."""

    def test_default_config(self):
        """Default config has sensible defaults."""
        config = Config()
        assert config.exclude == []
        assert config.severity == []
        assert config.strict is False
        assert config.default_severity == "WARNING"

    def test_config_with_exclude_patterns(self):
        """Config accepts exclude patterns."""
        config = Config(exclude=["plan/*", "CHANGELOG.md"])
        assert config.exclude == ["plan/*", "CHANGELOG.md"]

    def test_config_filters_empty_exclude_patterns(self):
        """Empty patterns are filtered from exclude list."""
        config = Config(exclude=["plan/*", "", "  ", "docs/*"])
        assert config.exclude == ["plan/*", "docs/*"]

    def test_config_with_severity_mappings(self):
        """Config accepts severity mappings."""
        config = Config(
            severity=[
                SeverityMapping(pattern="DSM_*.md", level="ERROR"),
                SeverityMapping(pattern="plan/*", level="INFO"),
            ]
        )
        assert len(config.severity) == 2
        assert config.severity[0].pattern == "DSM_*.md"
        assert config.severity[0].level == "ERROR"

    def test_config_strict_mode(self):
        """Config accepts strict mode."""
        config = Config(strict=True)
        assert config.strict is True

    def test_config_custom_default_severity(self):
        """Config accepts custom default severity."""
        config = Config(default_severity="ERROR")
        assert config.default_severity == "ERROR"


class TestFindConfigFile:
    """Tests for find_config_file function."""

    def test_finds_config_in_current_directory(self, tmp_path):
        """Finds config file in current directory."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("exclude: []")

        result = find_config_file(tmp_path)
        assert result == config_file

    def test_finds_config_in_parent_directory(self, tmp_path):
        """Finds config file in parent directory."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("exclude: []")

        child_dir = tmp_path / "subdir"
        child_dir.mkdir()

        result = find_config_file(child_dir)
        assert result == config_file

    def test_returns_none_when_no_config_found(self, tmp_path):
        """Returns None when no config file exists."""
        result = find_config_file(tmp_path)
        assert result is None

    def test_handles_file_path_as_start(self, tmp_path):
        """Handles file path as start_path by using its parent."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("exclude: []")

        some_file = tmp_path / "some_file.md"
        some_file.write_text("content")

        result = find_config_file(some_file)
        assert result == config_file


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path):
        """Loads valid YAML config file."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(
            """
exclude:
  - plan/*
  - CHANGELOG.md
severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "docs/*"
    level: WARNING
strict: true
"""
        )

        config = load_config(config_file)

        assert config.exclude == ["plan/*", "CHANGELOG.md"]
        assert len(config.severity) == 2
        assert config.severity[0].pattern == "DSM_*.md"
        assert config.severity[0].level == "ERROR"
        assert config.strict is True

    def test_load_empty_config_file(self, tmp_path):
        """Empty config file returns defaults."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("")

        config = load_config(config_file)

        assert config.exclude == []
        assert config.severity == []
        assert config.strict is False

    def test_load_partial_config(self, tmp_path):
        """Partial config uses defaults for missing fields."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("exclude:\n  - plan/*")

        config = load_config(config_file)

        assert config.exclude == ["plan/*"]
        assert config.severity == []
        assert config.strict is False

    def test_no_config_file_returns_defaults(self, tmp_path):
        """Returns defaults when no config file found."""
        config = load_config(start_path=tmp_path)

        assert config.exclude == []
        assert config.severity == []
        assert config.strict is False

    def test_explicit_missing_file_raises_error(self, tmp_path):
        """Explicit path to missing file raises ConfigError."""
        missing_file = tmp_path / "missing.yml"

        with pytest.raises(ConfigError, match="not found"):
            load_config(missing_file)

    def test_invalid_yaml_raises_error(self, tmp_path):
        """Invalid YAML raises ConfigError."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("exclude: [unclosed")

        with pytest.raises(ConfigError, match="Invalid YAML"):
            load_config(config_file)

    def test_invalid_config_values_raises_error(self, tmp_path):
        """Invalid config values raise ConfigError."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(
            """
severity:
  - pattern: ""
    level: ERROR
"""
        )

        with pytest.raises(ConfigError, match="Invalid configuration"):
            load_config(config_file)

    def test_invalid_severity_level_raises_error(self, tmp_path):
        """Invalid severity level raises ConfigError."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(
            """
severity:
  - pattern: "*.md"
    level: CRITICAL
"""
        )

        with pytest.raises(ConfigError, match="Invalid configuration"):
            load_config(config_file)

    def test_auto_discovers_config_file(self, tmp_path):
        """Auto-discovers config file from start_path."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text("strict: true")

        config = load_config(start_path=tmp_path)

        assert config.strict is True


class TestMergeConfigWithCli:
    """Tests for merge_config_with_cli function."""

    def test_cli_exclude_added_to_config_exclude(self):
        """CLI exclusions are added to config exclusions."""
        config = Config(exclude=["plan/*"])

        merged = merge_config_with_cli(config, cli_exclude=("docs/*", "*.bak"))

        assert "plan/*" in merged.exclude
        assert "docs/*" in merged.exclude
        assert "*.bak" in merged.exclude

    def test_cli_strict_true_overrides_config(self):
        """CLI --strict=True overrides config strict=False."""
        config = Config(strict=False)

        merged = merge_config_with_cli(config, cli_strict=True)

        assert merged.strict is True

    def test_cli_strict_false_does_not_override(self):
        """CLI --strict not set preserves config value."""
        config = Config(strict=True)

        merged = merge_config_with_cli(config, cli_strict=None)

        assert merged.strict is True

    def test_severity_preserved_from_config(self):
        """Severity mappings are preserved from config."""
        config = Config(
            severity=[SeverityMapping(pattern="*.md", level="ERROR")]
        )

        merged = merge_config_with_cli(config, cli_exclude=("test/*",))

        assert len(merged.severity) == 1
        assert merged.severity[0].pattern == "*.md"

    def test_no_cli_options_returns_unchanged(self):
        """No CLI options returns config unchanged."""
        config = Config(exclude=["plan/*"], strict=True)

        merged = merge_config_with_cli(config)

        assert merged.exclude == ["plan/*"]
        assert merged.strict is True

    def test_empty_cli_exclude_tuple(self):
        """Empty CLI exclude tuple doesn't affect config."""
        config = Config(exclude=["plan/*"])

        merged = merge_config_with_cli(config, cli_exclude=())

        assert merged.exclude == ["plan/*"]


class TestConfigIntegration:
    """Integration tests for config loading."""

    def test_full_config_example(self, tmp_path):
        """Test loading a complete config file like the one in docs."""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(
            """
# DSM Graph Explorer Configuration
exclude:
  - CHANGELOG.md           # Historical drift
  - docs/checkpoints/*     # Milestone snapshots
  - references/*           # Archive folder
  - plan/*                 # Planning docs with proposals
  - plan/archive/*         # Archived backlog items

severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "docs/checkpoints/*"
    level: INFO
  - pattern: "plan/*"
    level: INFO
  - pattern: "*.md"
    level: WARNING

strict: true
default_severity: WARNING
"""
        )

        config = load_config(config_file)

        assert len(config.exclude) == 5
        assert "CHANGELOG.md" in config.exclude
        assert "plan/*" in config.exclude
        assert len(config.severity) == 4
        assert config.strict is True
        assert config.default_severity == "WARNING"
