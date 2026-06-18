"""PPO v2 controlled retraining configuration scaffold.

v1.70 safety boundary:
- This module defines a non-executing configuration scaffold only.
- It does not fetch data.
- It does not generate datasets.
- It does not train a model.
- It does not create model artifacts.
- It does not submit paper or live orders.
- It does not unblock PPO + RF or PPO + XGBoost.

The goal is to make the future retraining path fail closed by default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


CANONICAL_PPO_V2_SYMBOLS: tuple[str, ...] = (
    "AAPL",
    "AMD",
    "MRK",
    "PFE",
    "UNH",
    "XOM",
)

FORBIDDEN_MODEL_INPUT_COLUMNS: tuple[str, ...] = (
    "Target",
    "Return",
    "Datetime",
    "Symbol",
)


@dataclass(frozen=True)
class PPOV2SafetyFlags:
    """Fail-closed safety flags for the PPO v2 scaffold."""

    training_execution_enabled: bool = False
    dataset_generation_enabled: bool = False
    model_artifact_creation_enabled: bool = False
    paper_order_submission_enabled: bool = False
    live_order_submission_enabled: bool = False
    controlled_submit_enabled: bool = False
    hybrid_deployment_enabled: bool = False

    def as_dict(self) -> dict[str, bool]:
        return {
            "training_execution_enabled": self.training_execution_enabled,
            "dataset_generation_enabled": self.dataset_generation_enabled,
            "model_artifact_creation_enabled": self.model_artifact_creation_enabled,
            "paper_order_submission_enabled": self.paper_order_submission_enabled,
            "live_order_submission_enabled": self.live_order_submission_enabled,
            "controlled_submit_enabled": self.controlled_submit_enabled,
            "hybrid_deployment_enabled": self.hybrid_deployment_enabled,
        }


@dataclass(frozen=True)
class PPOV2ControlledRetrainingConfig:
    """Non-executing PPO v2 controlled retraining configuration scaffold."""

    data_source: str = "alpaca_historical_1h_bars"
    bar_timeframe: str = "1Hour"
    symbols: tuple[str, ...] = CANONICAL_PPO_V2_SYMBOLS

    model_input_exclusion_columns: tuple[str, ...] = FORBIDDEN_MODEL_INPUT_COLUMNS

    raw_data_root: Path = Path("data/alpaca_historical")
    processed_data_root: Path = Path("data/alpaca_training")
    report_root: Path = Path("reports/ppo_v2_controlled_retraining")
    model_artifact_root: Path = Path("models/ppo_v2_controlled_retraining")

    legacy_artifact_roots: tuple[Path, ...] = (
        Path("models/ppo_models_master"),
        Path("models/alpaca_ppo_models_master"),
        Path("trained_models"),
    )

    random_seed: int = 42
    cost_rate: float = 0.0002
    slippage_rate: float = 0.0003

    train_split_name: str = "train_df"
    embargo_split_name: str = "embargo"
    eval_split_name: str = "eval_df"
    holdout_split_name: str = "holdout_df"
    holdout_usage: str = "final_validation_only"

    training_command: str | None = None
    dataset_generation_command: str | None = None
    model_artifact_command: str | None = None
    paper_order_command: str | None = None

    safety_flags: PPOV2SafetyFlags = field(default_factory=PPOV2SafetyFlags)

    def validate_safety(self) -> None:
        """Raise ValueError if the scaffold violates v1.70 safety boundaries."""

        errors = validate_config_safety(self)

        if errors:
            joined = "\n".join(f"- {error}" for error in errors)
            raise ValueError(f"PPO v2 scaffold safety validation failed:\n{joined}")


def build_default_ppo_v2_config() -> PPOV2ControlledRetrainingConfig:
    """Return the default fail-closed PPO v2 scaffold configuration."""

    return PPOV2ControlledRetrainingConfig()


def validate_config_safety(config: PPOV2ControlledRetrainingConfig) -> list[str]:
    """Return a list of safety validation errors.

    This validator is intentionally strict. v1.70 is allowed to create
    scaffold/config files and safety tests only; it is not allowed to execute
    retraining or create generated artifacts.
    """

    errors: list[str] = []

    enabled_flags = [
        name for name, enabled in config.safety_flags.as_dict().items() if enabled
    ]

    if enabled_flags:
        errors.append(
            "safety flags must fail closed; enabled flags found: "
            + ", ".join(enabled_flags)
        )

    command_fields = {
        "training_command": config.training_command,
        "dataset_generation_command": config.dataset_generation_command,
        "model_artifact_command": config.model_artifact_command,
        "paper_order_command": config.paper_order_command,
    }

    non_empty_commands = [
        name for name, command in command_fields.items() if command is not None
    ]

    if non_empty_commands:
        errors.append(
            "execution command fields must remain empty in v1.70; populated fields: "
            + ", ".join(non_empty_commands)
        )

    missing_forbidden_columns = set(FORBIDDEN_MODEL_INPUT_COLUMNS).difference(
        config.model_input_exclusion_columns
    )

    if missing_forbidden_columns:
        errors.append(
            "model input exclusions must include forbidden columns: "
            + ", ".join(sorted(missing_forbidden_columns))
        )

    if not config.symbols:
        errors.append("symbols must not be empty")

    if set(config.symbols) != set(CANONICAL_PPO_V2_SYMBOLS):
        errors.append(
            "v1.70 scaffold must remain on the six-ticker PPO v2 baseline universe"
        )

    if config.model_artifact_root in config.legacy_artifact_roots:
        errors.append("model_artifact_root must not point to legacy artifact roots")

    if config.report_root == config.model_artifact_root:
        errors.append("report_root and model_artifact_root must remain separate")

    if config.holdout_usage != "final_validation_only":
        errors.append("holdout usage must remain final_validation_only")

    return errors