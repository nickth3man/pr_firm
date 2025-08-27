# 3. Functional Requirements

## 3.1 Core Pipeline Features

### Input & Configuration
- **FR-001**: Accept Brand Bible in XML format with required fields (brand_name, voice, tone, forbiddens)
- **FR-002**: Support preset management for Brand Bibles, Email signatures, and Blog styles
- **FR-003**: Accept platform selection (Email, Instagram, Twitter/X, Reddit, LinkedIn, Blog)
- **FR-004**: Support custom intents per platform (preset/custom/auto-generated)
- **FR-005**: Accept topic/goal as primary content driver
- **FR-006**: Support Reddit-specific inputs (subreddit name, rules, description)

### Content Generation Pipeline
- **FR-007**: Parse and validate Brand Bible XML with error reporting
- **FR-008**: Map brand attributes to controlled vocabulary persona voice
- **FR-009**: Generate platform-specific guidelines from style sheets + persona + intent
- **FR-010**: Generate section-by-section content with character budgets
- **FR-011**: Enforce platform-specific hashtag and link placement rules
- **FR-012**: Apply conservative rewrites to remove forbidden patterns

### Style Enforcement
- **FR-013**: Detect hard violations (em dash, rhetorical contrasts) that block flow
- **FR-014**: Detect soft violations (AI fingerprints) that don't block but need fixing
- **FR-015**: Support up to 5 revision cycles for style compliance
- **FR-016**: Generate edit cycle report if max revisions reached
- **FR-017**: Maintain revision history and violation tracking

### Validation & Quality Control
- **FR-018**: Extract factual claims and flag those needing sources
- **FR-019**: Score brand alignment (0.0-1.0) with micro-edit suggestions
- **FR-020**: Flag authenticity issues (hype, over-claiming) with suggestions
- **FR-021**: Non-blocking validation that doesn't prevent completion

### Output & Packaging
- **FR-022**: Generate final approved content per platform
- **FR-023**: Create 7-day publishing schedule with optimal timing
- **FR-024**: Provide performance predictions (low/medium/high engagement)
- **FR-025**: Package all deliverables with guidelines and reports

## 3.2 Platform-Specific Requirements

### Email
- **FR-026**: Subject line target: 50-70 characters
- **FR-027**: Body limit: 500 characters
- **FR-028**: Structure: salutation, opening, value, CTA, signature
- **FR-029**: Single CTA requirement enforcement
- **FR-030**: Email signature preset integration

### LinkedIn
- **FR-031**: Character limit: 3000 with 210-char reveal cutoff
- **FR-032**: Hashtag placement at end (3 hashtags)
- **FR-033**: High whitespace density, short paragraphs
- **FR-034**: Professional tone adaptation

### Instagram
- **FR-035**: Character limit: 2200 with 125-char reveal cutoff
- **FR-036**: 8-20 hashtags placed at end
- **FR-037**: Liberal line breaks and moderate emoji frequency
- **FR-038**: Caption-only focus (no stories)

### Twitter/X
- **FR-039**: 280 character limit per tweet
- **FR-040**: Thread support for content >240 chars
- **FR-041**: 0-3 hashtags with flexible placement
- **FR-042**: Link placement at end

### Reddit
- **FR-043**: 40000 character limit
- **FR-044**: Markdown support (lists, bold)
- **FR-045**: TL;DR requirement at end
- **FR-046**: Subreddit rules and description integration

### Blog
- **FR-047**: 1200 word target (~6000 characters)
- **FR-048**: Deep H2/H3 heading structure
- **FR-049**: Medium link density throughout
- **FR-050**: Title case enforcement option

## 3.3 User Interface Requirements

### Command Line Interface
- **FR-051**: Simple execution via `python main.py`
- **FR-052**: Environment variable configuration support
- **FR-053**: Concise output summaries with drafts preview

### Gradio Web Interface (Optional)
- **FR-054**: Platform selection via comma-separated input
- **FR-055**: Topic/goal text input
- **FR-056**: Brand Bible XML text area
- **FR-057**: Milestone streaming display
- **FR-058**: JSON output of final drafts

### Progress & Feedback
- **FR-059**: Milestone-only streaming (no token-level)
- **FR-060**: Stage completion indicators
- **FR-061**: Revision cycle counter display
- **FR-062**: Clear error messages for failures

---
