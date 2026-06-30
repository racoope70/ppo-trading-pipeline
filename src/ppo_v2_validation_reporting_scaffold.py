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

# ---------------------------------------------------------------------------
# v2.59 PPO v2 validation reporting scaffold evidence contract implementation
# ---------------------------------------------------------------------------
#
# This section is intentionally read-only and non-executing.
#
# It does not train PPO.
# It does not fetch market data.
# It does not load broker clients.
# It does not create datasets.
# It does not write artifacts.
# It does not compute trading metrics.
# It does not authorize paper, live, or controlled-submit orders.
# It does not unblock PPO + Random Forest or PPO + XGBoost.
#
# The contract exists only to validate whether required post-run evidence is
# present in a supplied evidence manifest. Missing evidence fails closed.

from dataclasses import dataclass, field
from typing import Any, Mapping


EVIDENCE_CONTRACT_REQUIRED_KEYS = tuple(REQUIRED_EVIDENCE_KEYS)


class EvidenceDomainStatus:
    """Domain-level evidence state values."""

    PRESENT = "present"
    MISSING = "missing"


class EvidencePathStatus:
    """Path-level evidence state values."""

    PRESENT = "present"
    MISSING = "missing"


class EvidenceHashStatus:
    """Hash-level evidence state values."""

    PRESENT = "present"
    MISSING = "missing"


class EvidenceContractDecision:
    """Fail-closed evidence contract decisions."""

    PASS_READ_ONLY_NO_SUBMIT = "PASS_READ_ONLY_NO_SUBMIT"
    FAIL_CLOSED_MISSING_EVIDENCE = "FAIL_CLOSED_MISSING_EVIDENCE"
    FAIL_CLOSED_NO_SUBMIT_BOUNDARY = "FAIL_CLOSED_NO_SUBMIT_BOUNDARY"


@dataclass(frozen=True)
class EvidenceContract:
    """Read-only evidence contract for PPO v2 validation reporting."""

    required_evidence_keys: tuple[str, ...] = EVIDENCE_CONTRACT_REQUIRED_KEYS
    no_submit_required: bool = True
    controlled_submit_blocked: bool = True
    paper_orders_blocked: bool = True
    live_orders_blocked: bool = True
    model_promotion_blocked: bool = True
    hybrid_unblock_blocked: bool = True
    read_only: bool = True


@dataclass(frozen=True)
class EvidenceContractResult:
    """Result returned by the read-only evidence contract validator."""

    decision: str
    passed: bool
    missing_evidence_keys: tuple[str, ...] = field(default_factory=tuple)
    missing_path_keys: tuple[str, ...] = field(default_factory=tuple)
    missing_hash_keys: tuple[str, ...] = field(default_factory=tuple)
    domain_status: Mapping[str, str] = field(default_factory=dict)
    path_status: Mapping[str, str] = field(default_factory=dict)
    hash_status: Mapping[str, str] = field(default_factory=dict)
    no_submit_preserved: bool = True
    controlled_submit_blocked: bool = True
    paper_orders_blocked: bool = True
    live_orders_blocked: bool = True
    model_promotion_blocked: bool = True
    hybrid_unblock_blocked: bool = True
    read_only: bool = True


def build_evidence_contract() -> EvidenceContract:
    """Build the fail-closed PPO v2 reporting evidence contract."""

    return EvidenceContract()


def _evidence_value_has_path(evidence_value: Any) -> bool:
    if not isinstance(evidence_value, Mapping):
        return False

    path_value = evidence_value.get("path")
    return isinstance(path_value, str) and bool(path_value.strip())


def _evidence_value_has_hash(evidence_value: Any) -> bool:
    if not isinstance(evidence_value, Mapping):
        return False

    hash_value = evidence_value.get("sha256") or evidence_value.get("hash")
    return isinstance(hash_value, str) and bool(hash_value.strip())


def build_fail_closed_evidence_contract_result(
    *,
    contract: EvidenceContract | None = None,
    missing_evidence_keys: tuple[str, ...] = (),
    missing_path_keys: tuple[str, ...] = (),
    missing_hash_keys: tuple[str, ...] = (),
    decision: str = EvidenceContractDecision.FAIL_CLOSED_MISSING_EVIDENCE,
) -> EvidenceContractResult:
    """Build a fail-closed result without executing external work."""

    active_contract = contract or build_evidence_contract()

    domain_status = {
        key: (
            EvidenceDomainStatus.MISSING
            if key in missing_evidence_keys
            else EvidenceDomainStatus.PRESENT
        )
        for key in active_contract.required_evidence_keys
    }

    path_status = {
        key: (
            EvidencePathStatus.MISSING
            if key in missing_path_keys
            else EvidencePathStatus.PRESENT
        )
        for key in active_contract.required_evidence_keys
    }

    hash_status = {
        key: (
            EvidenceHashStatus.MISSING
            if key in missing_hash_keys
            else EvidenceHashStatus.PRESENT
        )
        for key in active_contract.required_evidence_keys
    }

    return EvidenceContractResult(
        decision=decision,
        passed=False,
        missing_evidence_keys=tuple(missing_evidence_keys),
        missing_path_keys=tuple(missing_path_keys),
        missing_hash_keys=tuple(missing_hash_keys),
        domain_status=domain_status,
        path_status=path_status,
        hash_status=hash_status,
        no_submit_preserved=active_contract.no_submit_required,
        controlled_submit_blocked=active_contract.controlled_submit_blocked,
        paper_orders_blocked=active_contract.paper_orders_blocked,
        live_orders_blocked=active_contract.live_orders_blocked,
        model_promotion_blocked=active_contract.model_promotion_blocked,
        hybrid_unblock_blocked=active_contract.hybrid_unblock_blocked,
        read_only=active_contract.read_only,
    )


def validate_evidence_contract_no_submit_boundary(
    contract: EvidenceContract | None = None,
) -> EvidenceContractResult:
    """Validate the no-submit safety boundary without executing any orders."""

    active_contract = contract or build_evidence_contract()

    no_submit_ok = (
        active_contract.no_submit_required
        and active_contract.controlled_submit_blocked
        and active_contract.paper_orders_blocked
        and active_contract.live_orders_blocked
        and active_contract.model_promotion_blocked
        and active_contract.hybrid_unblock_blocked
        and active_contract.read_only
    )

    if not no_submit_ok:
        return build_fail_closed_evidence_contract_result(
            contract=active_contract,
            decision=EvidenceContractDecision.FAIL_CLOSED_NO_SUBMIT_BOUNDARY,
        )

    return EvidenceContractResult(
        decision=EvidenceContractDecision.PASS_READ_ONLY_NO_SUBMIT,
        passed=True,
        missing_evidence_keys=(),
        missing_path_keys=(),
        missing_hash_keys=(),
        domain_status={
            key: EvidenceDomainStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        path_status={
            key: EvidencePathStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        hash_status={
            key: EvidenceHashStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        no_submit_preserved=True,
        controlled_submit_blocked=True,
        paper_orders_blocked=True,
        live_orders_blocked=True,
        model_promotion_blocked=True,
        hybrid_unblock_blocked=True,
        read_only=True,
    )


def validate_evidence_contract(
    evidence_manifest: Mapping[str, Mapping[str, Any]] | None,
    contract: EvidenceContract | None = None,
) -> EvidenceContractResult:
    """Validate required evidence metadata and fail closed on any gap.

    The supplied manifest is an in-memory mapping. This function intentionally
    does not read files from disk, write files, call a broker, fetch data, load
    a model, train a model, compute validation metrics, or submit orders.
    """

    active_contract = contract or build_evidence_contract()
    manifest = evidence_manifest or {}

    boundary_result = validate_evidence_contract_no_submit_boundary(active_contract)
    if not boundary_result.passed:
        return boundary_result

    missing_evidence_keys = tuple(
        key for key in active_contract.required_evidence_keys if key not in manifest
    )

    missing_path_keys = tuple(
        key
        for key in active_contract.required_evidence_keys
        if key in manifest and not _evidence_value_has_path(manifest[key])
    )

    missing_hash_keys = tuple(
        key
        for key in active_contract.required_evidence_keys
        if key in manifest and not _evidence_value_has_hash(manifest[key])
    )

    if missing_evidence_keys or missing_path_keys or missing_hash_keys:
        return build_fail_closed_evidence_contract_result(
            contract=active_contract,
            missing_evidence_keys=missing_evidence_keys,
            missing_path_keys=missing_path_keys,
            missing_hash_keys=missing_hash_keys,
        )

    return EvidenceContractResult(
        decision=EvidenceContractDecision.PASS_READ_ONLY_NO_SUBMIT,
        passed=True,
        missing_evidence_keys=(),
        missing_path_keys=(),
        missing_hash_keys=(),
        domain_status={
            key: EvidenceDomainStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        path_status={
            key: EvidencePathStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        hash_status={
            key: EvidenceHashStatus.PRESENT
            for key in active_contract.required_evidence_keys
        },
        no_submit_preserved=True,
        controlled_submit_blocked=True,
        paper_orders_blocked=True,
        live_orders_blocked=True,
        model_promotion_blocked=True,
        hybrid_unblock_blocked=True,
        read_only=True,
    )


# ---------------------------------------------------------------------------
# v2.79 PPO v2 validation reporting scaffold evidence contract usage adapter
# ---------------------------------------------------------------------------
#
# This adapter is intentionally read-only and non-executing.
#
# It accepts only an in-memory static evidence manifest.
# It returns only EvidenceContractResult.
# It delegates to the existing v2.59 evidence contract validator.
#
# It does not train PPO.
# It does not fetch market data.
# It does not load broker clients.
# It does not create datasets.
# It does not write artifacts.
# It does not compute trading metrics.
# It does not authorize paper, live, or controlled-submit orders.
# It does not unblock PPO + Random Forest or PPO + XGBoost.


def validate_evidence_contract_usage(
    evidence_manifest: Mapping[str, Mapping[str, Any]] | None,
    contract: EvidenceContract | None = None,
) -> EvidenceContractResult:
    """Apply the read-only evidence contract to a static evidence manifest.

    The usage adapter performs no external work. It only delegates to the
    existing fail-closed contract validator and returns the resulting
    EvidenceContractResult.
    """

    return validate_evidence_contract(
        evidence_manifest=evidence_manifest,
        contract=contract,
    )


def build_read_only_evidence_contract_usage_result(
    evidence_manifest: Mapping[str, Mapping[str, Any]] | None,
    contract: EvidenceContract | None = None,
) -> EvidenceContractResult:
    """Build the read-only usage result without generating reporting outputs."""

    return validate_evidence_contract_usage(
        evidence_manifest=evidence_manifest,
        contract=contract,
    )


__all__ += [
    "EVIDENCE_CONTRACT_REQUIRED_KEYS",
    "EvidenceContract",
    "EvidenceContractDecision",
    "EvidenceContractResult",
    "EvidenceDomainStatus",
    "EvidenceHashStatus",
    "EvidencePathStatus",
    "build_evidence_contract",
    "build_fail_closed_evidence_contract_result",
    "build_read_only_evidence_contract_usage_result",
    "validate_evidence_contract",
    "validate_evidence_contract_no_submit_boundary",
    "validate_evidence_contract_usage",
]
