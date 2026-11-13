# Contributing to Supervised Action Protocol (SAP)

We welcome contributions from systems engineers, formal methods researchers, and industrial control specialists.

## High-Value Contribution Tracks
1. **Sector-Specific SAT Axioms (`AxiomRule`)**:
   - Power utilities: IEEE thermal limits, transformer phase balance, ramp-rate caps.
   - Oil & Gas / Pipelines: Kirchhoff pressure conservation, compressor surge limits.
   - ERP & Treasury: Dual-currency ledger conservation, segregation-of-duties predicates.
2. **Adversarial & Red-Team Vectors**:
   - Edge cases that test hallucinated entity IDs, unit-mismatch spoofing, or simultaneous interlock bypasses (`aux_bypass && load_shed`).
3. **JSON Schema Extensions (`schemas/action.schema.json`)**:
   - Proposals for new standardized industrial targets and verifiable proof objects.

## Submission Guidelines
- Keep verification strictly deterministic (`O(1)` or bounded polynomial evaluation, no external network calls inside `AxiomRule`).
- Include self-contained pass/fail vectors demonstrating both `COMMITTED` and `SUPERVISED_APPROVAL_MANDATED` transitions.
- Run `python sap_verifier.py` before opening a Pull Request.

