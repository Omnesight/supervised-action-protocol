"""
Supervised Action Protocol (SAP) Open Reference Verifier
======================================================
Allows enterprise engineers and open-source contributors to define custom
industrial safety axioms, run deterministic guardrail checks, and emit
SHA-256 cryptographic provenance proofs compatible with action.schema.json.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


AxiomPredicate = Callable[[Dict[str, Any]], bool]


@dataclass(frozen=True)
class AxiomRule:
    """Formal deterministic safety invariant evaluated against action telemetry."""

    name: str
    description: str
    predicate: AxiomPredicate


@dataclass
class VerificationReport:
    """Result returned by SAPVerifier and verify_action_payload."""

    state: str
    is_valid: bool
    sat_verified: bool
    requires_human_escalation: bool
    axioms_checked: List[str]
    violations: List[str] = field(default_factory=list)
    proof_sha256: str = ""


DEFAULT_INDUSTRIAL_AXIOMS: List[AxiomRule] = [
    AxiomRule(
        name="AXIOM_POWER_CEILING",
        description="Ensures predicted actuation load stays below max_power_kw.",
        predicate=lambda p: float(p.get("power_kw", 0.0)) <= float(p.get("max_power_kw", 55.0)),
    ),
    AxiomRule(
        name="AXIOM_THERMAL_CEILING",
        description="Prevents conductor/node overheating above t_max_c.",
        predicate=lambda p: float(p.get("temp_c", 0.0)) <= float(p.get("t_max_c", 72.0)),
    ),
    AxiomRule(
        name="AXIOM_MUTEX_BYPASS_SHED",
        description="Mutual exclusion: forbids simultaneous auxiliary bypass and load shedding.",
        predicate=lambda p: not (int(p.get("aux_bypass", 0)) == 1 and int(p.get("load_shed", 0)) == 1),
    ),
]


class SAPVerifier:
    """Extensible deterministic SAP policy and SAT axiom verifier."""

    MAX_AUTONOMOUS_USD = 10_000.0
    MIN_CONFIDENCE = 0.92

    def __init__(self, axioms: Optional[List[AxiomRule]] = None) -> None:
        self.axioms: List[AxiomRule] = list(DEFAULT_INDUSTRIAL_AXIOMS if axioms is None else axioms)

    def register_axiom(self, rule: AxiomRule) -> None:
        """Register an additional domain-specific formal invariant."""
        self.axioms.append(rule)

    def verify(self, payload: Dict[str, Any], source_telemetry: str) -> VerificationReport:
        """Evaluate entity grounding, confidence/financial caps, and registered SAT axioms."""
        violations: List[str] = []
        requires_escalation = False

        target_entity = str(payload.get("target_entity_id", ""))
        if not target_entity or target_entity not in source_telemetry:
            violations.append(f"GROUNDING_FAILURE: '{target_entity}' not found in source_telemetry")

        confidence = float(payload.get("confidence_score", 0.0))
        if confidence < self.MIN_CONFIDENCE:
            requires_escalation = True
            violations.append(f"LOW_CONFIDENCE: {confidence:.2f} < {self.MIN_CONFIDENCE:.2f}")

        impact_usd = float(payload.get("financial_impact_usd", 0.0))
        if impact_usd > self.MAX_AUTONOMOUS_USD:
            requires_escalation = True
            violations.append(f"FINANCIAL_CAP_EXCEEDED: ${impact_usd:,.2f} > ${self.MAX_AUTONOMOUS_USD:,.2f}")

        params = payload.get("parameters", {})
        axioms_checked: List[str] = []
        sat_ok = True
        for rule in self.axioms:
            axioms_checked.append(rule.name)
            if not rule.predicate(params):
                sat_ok = False
                requires_escalation = True
                violations.append(f"SAT_VIOLATION:{rule.name}")

        is_valid = len(violations) == 0 and sat_ok
        state = "COMMITTED" if is_valid else "SUPERVISED_APPROVAL_MANDATED"

        telemetry_hash = hashlib.sha256(source_telemetry.encode("utf-8")).hexdigest()
        canonical_proof = json.dumps(
            {
                "action_id": payload.get("action_id", ""),
                "action_type": payload.get("action_type", ""),
                "target_entity_id": target_entity,
                "financial_impact_usd": impact_usd,
                "confidence_score": confidence,
                "axioms_checked": axioms_checked,
                "sat_verified": sat_ok,
                "source_telemetry_sha256": telemetry_hash,
            },
            sort_keys=True,
        )
        proof_sha = hashlib.sha256(canonical_proof.encode("utf-8")).hexdigest()

        return VerificationReport(
            state=state,
            is_valid=is_valid,
            sat_verified=sat_ok,
            requires_human_escalation=requires_escalation,
            axioms_checked=axioms_checked,
            violations=violations,
            proof_sha256=proof_sha,
        )


def verify_action_payload(
    payload: Dict[str, Any],
    source_telemetry: str,
    extra_axioms: Optional[List[AxiomRule]] = None,
) -> VerificationReport:
    """Convenience helper verifying an action dict with default + optional custom axioms."""
    verifier = SAPVerifier()
    for rule in extra_axioms or []:
        verifier.register_axiom(rule)
    return verifier.verify(payload, source_telemetry)


if __name__ == "__main__":
    # Reference verification self-check
    valid_action = {
        "action_id": "ACT-GRID901",
        "action_type": "GRID_THERMAL_CONTAINMENT",
        "target_system": "OMNESIGHT_SOVEREIGN_GRID",
        "target_entity_id": "NODE_2_ACTUATOR_CLUSTER",
        "confidence_score": 0.99,
        "financial_impact_usd": 4200.0,
        "parameters": {
            "power_kw": 49.0,
            "max_power_kw": 55.0,
            "temp_c": 66.5,
            "t_max_c": 72.0,
            "aux_bypass": 0,
            "load_shed": 1,
        },
    }
    telemetry = "target=NODE_2_ACTUATOR_CLUSTER | leak_node=2 | stress_z=0.91"
    report = verify_action_payload(valid_action, telemetry)
    assert report.is_valid and report.sat_verified and len(report.proof_sha256) == 64

    unsafe_action = {
        **valid_action,
        "parameters": {**valid_action["parameters"], "temp_c": 88.0, "aux_bypass": 1, "load_shed": 1},
    }
    unsafe_report = verify_action_payload(unsafe_action, telemetry)
    assert not unsafe_report.sat_verified
    assert unsafe_report.state == "SUPERVISED_APPROVAL_MANDATED"
    print(f"SAP Verifier OK | valid_sha={report.proof_sha256[:16]}... | unsafe_violations={unsafe_report.violations}")

