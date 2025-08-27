# Design Doc: Virtual PR Firm – Formatting-First Content System

> Please DON'T remove notes for AI

## Requirements

> Notes for AI: Keep it simple and clear.
> If the requirements are abstract, write concrete user stories

User stories

- As a marketing manager, I want text-only, platform-optimized content (Email,
  Instagram captions, Twitter/X, Reddit, LinkedIn, Blog) that respects each
  medium’s structure and limits.
- As a brand manager, I want strict voice and tone from a Brand Bible (XML) and
  consistent results across channels.
- As a creator, I want simple intake (platforms, intents, topic), milestone
  progress in chat, and full drafts once each platform completes.
- As a reviewer, I want “AI fingerprints” removed and strict bans enforced
  (no em dash, no rhetorical contrasts) with a clear revision loop (max 5)
  and a final report if edits stall.

Scope and constraints

- Formatting-only platform nodes. No scraping or platform research.
- Instagram: captions only (no stories).
- Reddit: user supplies subreddit name/title, rules, and description/bio (paste).
- Strict style policy:
  - Never use em dash (—).
  - Never use rhetorical contrasts/antithesis/chiasmus/paradiastole/tagline
    framing (“not just X; it’s Y”, “not X, but Y”, etc.).
- Streaming: milestones and edit-cycle summaries only; full drafts appear per
  platform when complete.
- Presets stored locally in JSON (Brand Bible, Email signature, Blog style).

Success criteria

- All generated outputs adhere to platform guidelines and strict style policy.
- The system streams concise progress milestones and edit-loop summaries.
- Drafts publish per platform as complete (no token-level streaming).
- If the edit loop reaches 5, a concise report is streamed and the flow proceeds.

## Flow Design

> Notes for AI:
>
> 1. Consider the design patterns of agent, map-reduce, rag, and workflow. Apply them if they fit.
> 2. Present a concise, high-level description of the workflow.

### Applicable Design Pattern

1. Workflow with a Manager (agent-like intake) and a strict validation pipeline.
2. Batch over selected platforms to emit guidelines and drafts per platform.
3. Map-ish scaffolding for content: section-by-section generation then assembly.

- Agentic Manager
  - Context: user-provided topic/goal, Brand Bible (XML/preset), chosen platforms,
    per-platform intents, and (for Reddit) subreddit name/title, rules, description/bio.
  - Actions: collect/confirm inputs, propose auto-intents, save/load presets,
    stream milestones, then route execution.

### Flow high-level Design

1. EngagementManagerNode: Conversational intake; collects platforms, intents
   (preset/custom/auto with confirm), topic/goal, Reddit details, Brand Bible
   (paste/preset), Email signature and Blog house style (choose/paste/save).
2. BrandBibleIngestNode: Parse Brand Bible XML; validate; map to persona/voice.
3. VoiceAlignmentNode: Normalize final voice/tone constraints; enforce forbiddens.
4. FormatGuidelinesFlow (Batch): For each selected platform, emit rich Guidelines
   from the style sheet + persona_voice + intent + platform nuance knobs
   (Instagram captions only; Reddit includes pasted rules/description).
5. ContentCraftsmanNode: Scaffold-first generation (section budgets), assemble
   final text, and enforce hashtag/link placement rules.
6. ValidationFlow: StyleEditorNode → StyleComplianceNode loop (≤5) → FactValidator
   → BrandGuardian → AuthenticityAuditor.
7. AgencyDirectorNode: Final packaging and streaming completion.

```mermaid
flowchart TD
    M[EngagementManager] --> B[BrandBibleIngest]
    B --> V[VoiceAlignment]
    V --> FG[FormatGuidelinesFlow (Batch)]
    FG --> C[ContentCraftsman]
    C --> VAL[ValidationFlow]
    VAL --> D[AgencyDirector]

    subgraph ValidationFlow
      E[StyleEditor] --> SC[StyleCompliance]
      SC -->|pass| F[FactValidator]
      SC -->|revise (<5)| E
      SC -->|max_revisions| R[EditCycleReport] --> F
      F --> G[BrandGuardian] --> A[AuthenticityAuditor]
    end
```

## Utility Functions

> Notes for AI:
>
> 1. Understand the utility function definition thoroughly by reviewing the doc.
> 2. Include only the necessary utility functions, based on nodes in the flow.

1. OpenRouter Client (`utils/openrouter_client.py`)
   - Input: model (str), messages (list[dict]), kwargs (e.g., temperature)
   - Output: response (str), or generator of str for streaming (not used for tokens)
   - Necessity: LLM access via OpenRouter

2. Call LLM (`utils/call_llm.py`)
   - Input: messages (list[dict]), model (str), temperature (float)
   - Output: response (str)
   - Necessity: Standardized LLM calls for generation/edits/evaluations

3. Streaming (`utils/streaming.py`)
   - Input: emit(role: str, text: str)
   - Output: messages() generator for UI
   - Necessity: Milestone-only streaming into chat

4. Presets Store (`utils/presets.py`)
   - Input: save/get/list Brand Bible, Email signatures, Blog styles
   - Output: local JSON persistence
   - Necessity: Reusable presets by name

5. Brand Bible Parser (`utils/brand_bible_parser.py`)
   - Input: xml_str (str)
   - Output: parsed dict + _missing fields (list) if any
   - Necessity: Safe/tolerant XML parsing with validation

6. Brand Voice Mapper (`utils/brand_voice_mapper.py`)
   - Input: parsed Brand Bible (dict)
   - Output: persona_voice (tone axes/styles; strict forbiddens)
   - Necessity: Controlled-vocabulary tone mapping (“tone fix”)

7. Platform Formatter (`utils/format_platform.py`)
   - Input: platform (str), persona_voice (dict), intent (str), platform_nuance (dict),
     reddit.rules/description (optional)
   - Output: Guidelines (dict; unified schema)
   - Necessity: Deterministic, style-sheet-driven platform guidelines

8. Style Violations (`utils/check_style_violations.py`)
   - Input: text (str)
   - Output: {violations: list, score: float}
   - Necessity: Strict detection of 7 Deadly Sins + soft fingerprints

9. Constrained Rewrite (`utils/rewrite_with_constraints.py`)
   - Input: text (str), voice (dict), guidelines (dict)
   - Output: rewritten text (str)
   - Necessity: Editor removes AI fingerprints w/o introducing bans

10. Report Builder (`utils/report_builder.py`)
    - Input: violation history, last draft, platform
    - Output: concise user-facing summary (str)
    - Necessity: Max-revision (5) report clarity

11. Progress Mapper (`utils/progress.py`)
    - Input: stage events
    - Output: debounced percent + messages via stream
    - Necessity: Clean milestone updates (no token spam)

12. Subreddit Normalize (`utils/input_normalize.py`)
    - Input: subreddit URL or name (str)
    - Output: canonical subreddit name/title (str)
    - Necessity: Stable Reddit naming for guidelines

## Node Design

### Shared Store

> Notes for AI: Try to minimize data redundancy

The shared store structure is organized as follows:

```python
shared = {
  "config": {"style_policy": "strict"},
  "task_requirements": {
    "platforms": [],
    "intents_by_platform": {},  # {"linkedin": {"type": "preset|custom|auto", "value": "thought leadership"}}
    "topic_or_goal": "",
    "subreddit_name_or_title": None,
    "urgency_level": "normal",
  },
  "brand_bible": {
    "xml_raw": "",
    "parsed": {},
    "persona_voice": {},
    "preset_name": None,
  },
  "house_style": {
    "email_signature": {"name": None, "content": ""},
    "blog_style": {"name": None, "content": ""},
  },
  "platform_nuance": {
    "linkedin": {"whitespace_density": "high", "para_length": "short", "hashtag_placement": "end"},
    "twitter": {"thread_ok_above_chars": 240, "hashtag_count_range": [0, 3]},
    "instagram": {"emoji_freq": "moderate", "line_breaks": "liberal", "hashtag_count_range": [8, 20]},
    "reddit": {"markdown_blocks": ["lists", "bold"], "tl_dr_required": True},
    "email": {"subject_target_chars": 50, "single_cta_required": True},
    "blog": {"h2_h3_depth": "deep", "link_density": "medium"},
  },
  "reddit": {
    "rules_text": None,         # user-pasted rules
    "description_text": None,   # user-pasted subreddit description/bio
  },
  "platform_guidelines": {},    # {"linkedin": Guidelines, ...}
  "content_pieces": {},         # {"linkedin": {"sections": {...}, "text": "..."}}
  "style_compliance": {},       # per-platform violation reports
  "workflow_state": {
    "current_stage": "",
    "completed_stages": [],
    "revision_count": 0,
    "manual_review_required": False,
  },
  "final_campaign": {
    "approved_content": {},
    "publishing_schedule": {},
    "performance_predictions": {},
    "edit_cycle_report": None,
  },
  "stream": None,
  "llm": {"model": "openai/gpt-4o", "temperature": 0.7},
}
```

### Node Steps

> Notes for AI: Carefully decide whether to use Batch/Async Node/Flow.

1. EngagementManagerNode
   - Purpose: Centralize user I/O; collect platforms, per-platform intents
     (preset/custom/auto with confirm), topic/goal, Reddit details (name/title,
     rules, description), Brand Bible (paste/preset), and Email/Blog signatures
     (choose/paste/save). Stream milestones.
   - Type: Regular
   - Steps:
     - prep: Read task_requirements and presets; determine missing inputs.
     - exec: Ask, propose auto-intents, confirm, and capture choices; “save as
       preset” on request (via presets utility).
     - post: Write normalized inputs into shared (task_requirements, brand_bible,
       house_style, reddit.*). Stream confirmations/milestones.

2. BrandBibleIngestNode
   - Purpose: Parse Brand Bible XML, validate required fields, map to persona/voice
     with controlled vocabulary (“tone fix”).
   - Type: Regular
   - Steps:
     - prep: Read brand_bible.xml_raw or preset_name (load via presets).
     - exec: brand_bible_parser.parse → brand_voice_mapper.brand_bible_to_voice.
     - post: Store parsed + persona_voice; stream warnings for missing fields.

3. VoiceAlignmentNode
   - Purpose: Normalize final voice/tone; ensure strict forbiddens (no em dash,
     no rhetorical contrasts).
   - Type: Regular
   - Steps:
     - prep: Read brand_bible.persona_voice.
     - exec: Normalize tone axes/styles; assert forbiddens present.
     - post: Update brand_bible.persona_voice.

4. FormatGuidelinesFlow (Batch)
   - Purpose: For each selected platform, emit detailed Guidelines from the style
     sheet + persona_voice + intent + platform nuance (Instagram captions only;
     Reddit includes pasted rules/description).
   - Type: BatchFlow
   - Steps:
     - prep: Return [{"platform": p} for p in task_requirements.platforms].
     - exec: Run corresponding PlatformFormattingNode by params.platform.
     - post: Aggregate Guidelines in shared.platform_guidelines.

5. PlatformFormattingNodes (Email/Instagram/Twitter/Reddit/LinkedIn/Blog)
   - Purpose: Output a unified Guidelines schema (limits, structure, style,
     hashtags/mentions/links, markdown, CTA, notes; Reddit includes subreddit_name
     - rules/description notes).
   - Type: Regular
   - Steps:
     - prep: Read persona_voice, intent (for this platform), platform_nuance,
       and reddit.rules/description when platform == "reddit".
     - exec: format_platform.build_guidelines(...).
     - post: Write platform_guidelines[platform] = guidelines.

6. ContentCraftsmanNode
   - Purpose: Scaffold-first generation (section budgets), assemble final text,
     enforce placement rules (hashtags/links).
   - Type: Regular
   - Steps:
     - prep: Read platform_guidelines, persona_voice, intents_by_platform,
       house_style.
     - exec: For each platform, generate section-by-section (with budgets),
       assemble, enforce placement.
     - post: Write content_pieces[platform] = {"sections": {...}, "text": "..."}.
       Stream “Draft complete: <platform>”.

7. StyleEditorNode
   - Purpose: Remove “AI fingerprints” (stiff transitions, predictable lists,
     tidy wrap-ups, monotone rhythm, platitudes) without changing meaning/structure;
     never introduce bans; self-check after rewrite.
   - Type: Regular
   - Steps:
     - prep: Read content_pieces, persona_voice, guidelines.
     - exec: rewrite_with_constraints → re-check with check_style_violations.
     - post: Update content_pieces with edited drafts.

8. StyleComplianceNode
   - Purpose: Detect-only strict enforcement of 7 Deadly Sins; loop with editor
     up to 5; stream pass/fail summaries.
   - Type: Regular
   - Steps:
     - prep: Read content_pieces (per platform).
     - exec: check_style_violations on each; aggregate hard/soft issues.
     - post: Write style_compliance reports; if hard bans and
       revision_count < 5: increment and return "revise"; if >= 5: return
       "max_revisions"; else "pass". Stream “Style check k/5: …”.

9. EditCycleReportNode
   - Purpose: On 5th failure, produce a concise user-facing report; proceed.
   - Type: Regular
   - Steps:
     - prep: Read violations history and latest drafts.
     - exec: report_builder to summarize issues and snippets.
     - post: Save final_campaign.edit_cycle_report; set manual_review_required;
       stream summary.

10. FactValidatorNode
    - Purpose: Flag claims needing sources; non-blocking.
    - Type: Regular
    - Steps:
      - prep: Read content_pieces.
      - exec: LLM prompt to extract claims + needs_source flags.
      - post: Store validation notes.

11. BrandGuardianNode
    - Purpose: Score brand alignment vs persona voice; micro-edit suggestions;
      non-blocking.
    - Type: Regular
    - Steps:
      - prep: Read content_pieces + persona_voice.
      - exec: LLM scoring and suggestions.
      - post: Store scores/suggestions.

12. AuthenticityAuditorNode
    - Purpose: Flag over-claiming/hype; transparency risks.
    - Type: Regular
    - Steps:
      - prep: Read content_pieces.
      - exec: LLM evaluation for authenticity.
      - post: Store warnings.

13. AgencyDirectorNode
    - Purpose: Final packaging; include sectioned drafts, final texts, scores,
      and any edit-cycle report. Stream completion.
    - Type: Regular
    - Steps:
      - prep: Read all results.
      - exec: Collate deliverables.
      - post: Write final_campaign.*; stream “Packaging complete”.

Notes

- Retries: LLM-heavy nodes (ContentCraftsman, StyleEditor) may use
  max_retries=2, wait=5. Others default to 1.
- Streaming: Only EngagementManager, StyleCompliance, EditCycleReport, and
  AgencyDirector emit progress messages.
