<div align="center">

# Supervised Action Protocol (SAP)

**An open enterprise standard for policy-governed autonomous decision execution and cryptographic auditability.**

[![Specification Version](https://img.shields.io/badge/spec-v1.0.0-blue.svg?style=flat-square)](spec/v1.0.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg?style=flat-square)](LICENSE)
[![Security Policy](https://img.shields.io/badge/security-SLA%20%3C24h-blueviolet.svg?style=flat-square)](https://github.com/Omnesight/.github/blob/main/SECURITY.md)

</div>

---

## The Enterprise Challenge

In mission-critical enterprise operations (heavy industry, supply chain, energy utilities), traditional AI suffers from two polar failures:
1. **Passive Dashboards:** Insights rot on business intelligence screens without closing the loop.
2. **Ungoverned Autonomy:** Unconstrained LLM autonomous agents risk catastrophic transactional write-backs, phantom purchase orders, and ledger corruption.

The **Supervised Action Protocol (SAP)** solves this by establishing a deterministic, cryptographically auditable state machine between cognitive intelligence engines and core enterprise systems (SAP, Oracle, SCADA).

---

## State Transition Machine

```mermaid
stateDiagram-v2
    [*] --> PROPOSED: AI Agent Identifies Operational Anomaly
    PROPOSED --> VALIDATING: Policy & Hallucination Check
    
    VALIDATING --> COMMITTED: Risk < Threshold & Confidence >= 95%
    VALIDATING --> SUPERVISED_APPROVAL: Risk >= Threshold OR Impact > Limit
    
    SUPERVISED_APPROVAL --> APPROVED: Human Supervisor Confirms Action
    SUPERVISED_APPROVAL --> REJECTED: Human Supervisor Declines Action
    
    APPROVED --> COMMITTED: Write-Back Executed in ERP
    COMMITTED --> REVERTED: Compensating Transaction (Rollback)
    
    REJECTED --> [*]
    COMMITTED --> [*]
    REVERTED --> [*]
```

---

## Core Guarantees

* **Zero Ungoverned Write-Backs:** No transaction with financial impact exceeding configured policy limits (e.g., $10,000 USD) can execute without an explicit cryptographic signature from an authorized human supervisor.
* **Cryptographic Provenance:** Every action generates a SHA-256 audit hash binding the raw telemetry trigger, model checkpoint, policy evaluations, and executor identity.
* **Idempotency & Rollback Guarantees:** Every state transition implements compensating transaction logic for deterministic rollbacks in enterprise ledgers.

---

## Repository Structure

```text
supervised-action-protocol/
├── schemas/
│   └── action.schema.json      # Formal JSON Schema draft 2020-12
├── spec/
│   └── v1.0.md                 # Full RFC-style protocol specification
├── LICENSE                     # Apache 2.0 License
└── README.md
```

---

## Reference Implementations

* **Python SDK:** [`omnesight-python`](https://github.com/Omnesight/omnesight-python)
* **Enterprise Cookbooks:** [`enterprise-cookbooks`](https://github.com/Omnesight/enterprise-cookbooks)

---

## License

Apache License 2.0. Copyright 2026 Omnesight.
