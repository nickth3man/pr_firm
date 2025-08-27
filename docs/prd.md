---
title: "pr_firm Brownfield Enhancement PRD"
---

Project: pr_firm

## 1. Intro — Project Analysis and Context

This PRD describes a substantial enhancement to the existing `pr_firm` platform: a robust, architecture-aware, platform-optimized content pipeline with 17 specialized nodes that ingests Brand Bibles, generates per-platform guidelines, scaffolds drafts via an LLM, iterates edits to remove AI fingerprints, validates claims and brand alignment, and packages final deliverables with a publishing schedule.

Document-project extraction was performed and is available at `docs/prd/document_project_output.md`.

**CRITICAL**: This PRD is for substantial brownfield enhancements. The implementation must preserve existing functionality and include integration verification for each story.

## 2. Goals

- **Deliver** platform-optimized content drafts (Email, LinkedIn, Instagram, Twitter/X, Reddit, Blog) that conform to brand voice and strict style bans.
- **Ensure** edits never introduce banned patterns (no em dash, no rhetorical contrasts).
- **Make** the pipeline robust for real-world projects (presets, missing docs, and IDE-based analysis).
- **Provide** an incremental story sequence minimizing risk to the existing codebase.

## 3. Background and Scope

- The repository already contains a working pipeline (`flow.py`, `nodes.py`) and utilities (`utils/`) used by the pipeline. This PRD scopes enhancements across multiple stories covering ingestion, guidelines, generation, compliance, validation, and packaging.

## 4. Epic & Story Structure

**Epic**: Platform-Optimized Content Pipeline Enhancements

**Stories (aligned with 17-node pipeline):**

### 1.1 — Engagement Management & Input Processing

- Tasks: enhance EngagementManagerNode for robust input validation, preset loading, and platform selection handling.
- Integration verification: test complete flow from user inputs through shared store initialization.

### 1.2 — Brand Bible Processing & Voice Alignment

- Tasks: improve BrandBibleIngestNode XML parsing tolerance and VoiceAlignmentNode persona_voice normalization.
- Verification: unit tests for XML parsing edge cases and persona_voice structure validation.

### 1.3 — Platform Guidelines Generation

- Tasks: enhance FormatGuidelinesRouter and 6 platform-specific nodes (Email, Instagram, Twitter, Reddit, LinkedIn, Blog) for robust guideline generation.
- Verification: automated tests validating Guidelines schema output for each platform.

### 1.4 — Content Generation & LLM Integration

- Tasks: improve ContentCraftsmanNode prompt engineering, section budgeting, and LLM error handling with retries.
- Verification: integration tests with mock LLM client validating section generation and placement rules.

### 1.5 — Style Compliance & Edit Loop

- Tasks: enhance StyleEditorNode and StyleComplianceNode for 5-cycle edit loop, violation detection, and EditCycleReportNode for max-revision handling.
- Verification: test edit cycles with injected violations and report generation.

### 1.6 — Validation & Quality Assurance

- Tasks: improve FactValidatorNode claim extraction, BrandGuardianNode alignment scoring, and AuthenticityAuditorNode hype detection.
- Verification: test validation outputs and integration with final packaging.

### 1.7 — Packaging & Final Delivery

- Tasks: enhance AgencyDirectorNode for schedule generation, performance predictions, and final_campaign packaging.
- Verification: end-to-end flow testing with complete output validation.

## 5. Requirements

**Functional:**

- **FR1**: System must ingest a Brand Bible XML or preset and produce a `persona_voice` mapping.
- **FR2**: For each requested platform, the system must produce a Guidelines object and a draft text composed section-by-section.
- **FR3**: The system must run an edit loop up to 5 times, generate an edit-cycle report on max revisions, and mark manual review required.

**Non-functional:**

- **NFR1**: No em dash (—) may appear in final drafts. Enforced automatically and reported as hard violation.
- **NFR2**: No rhetorical contrast phrasing like "not X but Y" in final drafts.
- **NFR3**: The pipeline must be robust to missing documentation (recommend running `document-project`).
- **NFR4**: Tests must exist for all critical parsing and guideline functions.

## 6. Technical Constraints & Integration

- LLM access is via OpenRouter-compatible client; environment variables `OPENROUTER_API_KEY` and optional `OPENROUTER_MODEL` must be configured.
- The PRD and brownfield process assume `document-project` outputs exist; if not, the flow must prompt the user and refuse to proceed for elicit:true sections.
- Integration points: presets storage (`utils/presets.py`), LLM client (`utils/openrouter_client.py`), and `docs/` outputs.

## 7. Risk Assessment

- **Risk**: LLM variability may produce banned patterns. **Mitigation**: conservative rewrite step and 5-cycle compliance loop with a final human review on max revisions.
- **Risk**: Missing technical docs may lead to incorrect assumptions. **Mitigation**: require `document-project` or user confirmation before requirements drafting.

## 8. Acceptance Criteria

- All FRs implemented and covered by automated tests.
- No hard violations in final drafts for sample runs across all selected platforms.
- End-to-end pipeline run produces `final_campaign` with packaging and schedule.

## 9. Next Steps

1. Proceed with Story 1.1 (Engagement Management) implementation and tests.
2. Complete Stories 1.2–1.7 sequentially, running integration tests after each story.
3. Schedule manual review once `style_compliance` hits `max_revisions` or after first full end-to-end run.
4. Validate that all 17 nodes work together seamlessly in the complete pipeline.
