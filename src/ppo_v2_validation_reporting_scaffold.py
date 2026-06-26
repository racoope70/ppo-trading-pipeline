"""Non-executing PPO v2 validation reporting scaffold.

This module defines read-only status objects and fail-closed evidence checks for
future PPO v2 validation reporting. It does not train models, load models,
fetch market data, call a broker, compute performance metrics, generate reports,
generate plots, or write artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


NO_SUBMIT_DEFAULT = "DEFAULT"
CONTROLLED_SUBMIT_STATUS = "BLOCKED"
PPO_RF_STATUS = "BLOCKED"
PPO_XGBOOST_STATUS = "BLOCKED"
MODEL_PROMOTION_STATUS = "NOT_AUTHORIZED"
PAPER_ORDERS_STATUS = "NOT_AUTHORIZED"
LIVE_ORDERS_STATUS = "NOT_AUTHORIZED"

REQUIRED_EVIDENCE_KEYS: tuple[str, ...] = (
    "training_outputs_inventory",
    "quarantine_output_manifest",
    "dataset_boundary_manifest",
    "leakage_control_evidence",
    "normalization_evidence",
    "locked_eval_stats_evidence",
    "untouched_holdout_evidence",
    "ppo_only_baseline_evidence",
    "post_run_audit",
)


@dataclass(frozen=True)
class EvidenceCheck:
    """Read-only result describing whether audited reporting inputs exist."""

    required_keys: tuple[str, ...]
    provided_keys: tuple[str, ...]
    present_keys: tuple[str, ...]
    missing_keys: tuple[str, ...]
    all_required_present: bool
    audited_outputs_available: bool

    def to_manifest(self) -> dict[str, Any]:
        """Return a plain manifest dictionary without writing anything."""
        return {
            "required_keys": list(self.required_keys),
            "provided_keys": list(self.provided_keys),
            "present_keys": list(self.present_keys),
            "missing_keys": list(self.missing_keys),
            "all_required_present": self.all_required_present,
            "audited_outputs_available": self.audited_outputs_available,
        }


@dataclass(frozen=True)
class ReportingScaffoldStatus:
    """Fail-closed status for the validation reporting scaffold."""

    scaffold_implemented: bool
    fail_closed: bool
    reason: str
    evidence_check: EvidenceCheck
    no_submit: str = NO_SUBMIT_DEFAULT
    controlled_submit: str = CONTROLLED_SUBMIT_STATUS
    ppo_rf: str = PPO_RF_STATUS
    ppo_xgboost: str = PPO_XGBOOST_STATUS
    model_promotion: str = MODEL_PROMOTION_STATUS
    paper_orders: str = PAPER_ORDERS_STATUS
    live_orders: str = LIVE_ORDERS_STATUS
    metrics_computed: bool = False
    reports_generated: bool = False
    plots_generated: bool = False
    dashboards_generated: bool = False

    def to_manifest(self) -> dict[str, Any]:
        """Return a plain manifest dictionary without generating reports."""
        return {
            "scaffold_implemented": self.scaffold_implemented,
            "fail_closed": self.fail_closed,
            "reason": self.reason,
            "evidence_check": self.evidence_check.to_manifest(),
            "no_submit": self.no_submit,
            "controlled_submit": self.controlled_submit,
            "ppo_rf": self.ppo_rf,
            "ppo_xgboost": self.ppo_xgboost,
            "model_promotion": self.model_promotion,
            "paper_orders": self.paper_orders,
            "live_orders": self.live_orders,
            "metrics_computed": self.metrics_computed,
            "reports_generated": self.reports_generated,
            "plots_generated": self.plots_generated,
            "dashboards_generated": self.dashboards_generated,
        }


def _normalize_evidence_paths(
    evidence_paths: Mapping[str, str | Path] | None,
) -> dict[str, Path]:
    """Normalize evidence paths without reading file contents."""
    if evidence_paths is None:
        return {}
    return {key: Path(value) for key, value in evidence_paths.items()}


def check_required_evidence(
    evidence_paths: Mapping[str, str | Path] | None = None,
) -> EvidenceCheck:
    """Check whether required audited evidence paths exist.

    This is intentionally limited to path-existence checks. It does not parse,
    load, transform, or compute over any evidence.
    """
    normalized_paths = _normalize_evidence_paths(evidence_paths)

    present_keys: list[str] = []
    missing_keys: list[str] = []

    for key in REQUIRED_EVIDENCE_KEYS:
        candidate = normalized_paths.get(key)
        if candidate is not None and candidate.exists():
            present_keys.append(key)
        else:
            missing_keys.append(key)

    all_required_present = not missing_keys

    return EvidenceCheck(
        required_keys=REQUIRED_EVIDENCE_KEYS,
        provided_keys=tuple(sorted(normalized_paths)),
        present_keys=tuple(present_keys),
        missing_keys=tuple(missing_keys),
        all_required_present=all_required_present,
        audited_outputs_available=all_required_present,
    )


def build_reporting_scaffold_status(
    evidence_paths: Mapping[str, str | Path] | None = None,
) -> ReportingScaffoldStatus:
    """Build the non-executing scaffold status.

    Missing audited outputs produce a fail-closed status. Even when all evidence
    paths are present, this scaffold still does not compute metrics or generate
    reporting outputs.
    """
    evidence_check = check_required_evidence(evidence_paths)

    if evidence_check.audited_outputs_available:
        fail_closed = False
        reason = (
            "Audited evidence paths are present; reporting remains non-executing "
            "until a separate report-generation checkpoint authorizes outputs."
        )
    else:
        fail_closed = True
        reason = (
            "Missing audited PPO v2 evidence; validation reporting scaffold "
            "failed closed without computing metrics or generating outputs."
        )

    return ReportingScaffoldStatus(
        scaffold_implemented=True,
        fail_closed=fail_closed,
        reason=reason,
        evidence_check=evidence_check,
    )


def validate_no_submit_boundary() -> dict[str, str]:
    """Return the preserved no-submit and blocked-deployment boundary."""
    return {
        "NO_SUBMIT": NO_SUBMIT_DEFAULT,
        "controlled_submit": CONTROLLED_SUBMIT_STATUS,
        "ppo_rf": PPO_RF_STATUS,
        "ppo_xgboost": PPO_XGBOOST_STATUS,
        "model_promotion": MODEL_PROMOTION_STATUS,
        "paper_orders": PAPER_ORDERS_STATUS,
        "live_orders": LIVE_ORDERS_STATUS,
    }


__all__ = [
    "CONTROLLED_SUBMIT_STATUS",
    "EvidenceCheck",
    "LIVE_ORDERS_STATUS",
    "MODEL_PROMOTION_STATUS",
    "NO_SUBMIT_DEFAULT",
    "PAPER_ORDERS_STATUS",
    "PPO_RF_STATUS",
    "PPO_XGBOOST_STATUS",
    "REQUIRED_EVIDENCE_KEYS",
    "ReportingScaffoldStatus",
    "build_reporting_scaffold_status",
    "check_required_evidence",
    "validate_no_submit_boundary",
]
