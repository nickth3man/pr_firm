# Product Requirements Document (PRD)
## Virtual PR Firm - Formatting-First Content System

---

## 1. Executive Summary

### Product Vision
Virtual PR Firm is a sophisticated AI-powered content generation system that produces platform-optimized, brand-consistent marketing copy across multiple channels (Email, Instagram, Twitter/X, Reddit, LinkedIn, Blog). It uses a formatting-first pipeline approach to ensure content adheres to strict brand guidelines and platform-specific requirements while maintaining authenticity and engagement.

### Problem Statement
Marketing teams struggle to maintain consistent brand voice across multiple platforms while adhering to each platform's unique formatting requirements and best practices. Manual content creation is time-consuming, often results in inconsistent messaging, and frequently produces content with "AI fingerprints" that reduce authenticity.

### Solution Overview
A workflow-based content generation system that:
- Ingests brand guidelines via XML format
- Generates platform-specific content following strict formatting rules
- Enforces brand voice consistency and style policies
- Removes AI fingerprints through iterative editing
- Validates content for brand alignment, facts, and authenticity
- Packages final deliverables with publishing schedules

### Success Metrics
- Content generation time reduced from hours to minutes
- 100% adherence to brand guidelines and style policies
- Zero instances of forbidden patterns (em dash, rhetorical contrasts)
- 95%+ brand alignment score across all generated content
- < 5 revision cycles needed for style compliance

---

## 2. User Personas & Use Cases

### Primary Personas

#### 1. Marketing Manager (Primary)
- **Goals**: Create consistent, on-brand content across multiple platforms quickly
- **Pain Points**: Time-consuming manual content creation, maintaining consistency
- **Technical Level**: Non-technical, comfortable with web interfaces
- **Use Cases**: 
  - Campaign announcements across all channels
  - Weekly content calendar generation
  - Product launch communications

#### 2. Brand Manager (Secondary)
- **Goals**: Ensure strict adherence to brand voice and guidelines
- **Pain Points**: Inconsistent brand representation, unauthorized messaging patterns
- **Technical Level**: Non-technical, focused on brand compliance
- **Use Cases**:
  - Brand guideline enforcement
  - Voice and tone consistency checks
  - Forbidden pattern detection and removal

#### 3. Content Creator (Tertiary)
- **Goals**: Generate high-quality drafts quickly for refinement
- **Pain Points**: Writer's block, platform-specific formatting requirements
- **Technical Level**: Basic technical skills
- **Use Cases**:
  - Quick draft generation for inspiration
  - Platform-specific formatting assistance
  - Content variation testing

### User Stories

#### Epic 1: Content Pipeline Setup & Ingestion
- As a marketing manager, I want to input my brand guidelines once and have them applied consistently across all content
- As a brand manager, I want to define forbidden patterns that should never appear in our content
- As a content creator, I want to save and reuse brand presets for different clients/projects

#### Epic 2: Platform-Specific Content Generation
- As a marketing manager, I want to generate content optimized for each platform's unique requirements
- As a content creator, I want the system to understand platform-specific best practices (hashtag placement, character limits, etc.)
- As a brand manager, I want platform guidelines to respect our brand voice while adapting to platform norms

#### Epic 3: Style Enforcement & Quality Control
- As a brand manager, I want automatic detection and removal of AI fingerprints
- As a marketing manager, I want iterative refinement until content meets quality standards
- As a content creator, I want clear feedback on why content needs revision

#### Epic 4: Validation & Packaging
- As a marketing manager, I want fact-checking flags for claims needing sources
- As a brand manager, I want brand alignment scoring and suggestions
- As a content creator, I want final packaged deliverables with publishing schedules

---

## 3. Functional Requirements

### 3.1 Core Pipeline Features

#### Input & Configuration
- **FR-001**: Accept Brand Bible in XML format with required fields (brand_name, voice, tone, forbiddens)
- **FR-002**: Support preset management for Brand Bibles, Email signatures, and Blog styles
- **FR-003**: Accept platform selection (Email, Instagram, Twitter/X, Reddit, LinkedIn, Blog)
- **FR-004**: Support custom intents per platform (preset/custom/auto-generated)
- **FR-005**: Accept topic/goal as primary content driver
- **FR-006**: Support Reddit-specific inputs (subreddit name, rules, description)

#### Content Generation Pipeline
- **FR-007**: Parse and validate Brand Bible XML with error reporting
- **FR-008**: Map brand attributes to controlled vocabulary persona voice
- **FR-009**: Generate platform-specific guidelines from style sheets + persona + intent
- **FR-010**: Generate section-by-section content with character budgets
- **FR-011**: Enforce platform-specific hashtag and link placement rules
- **FR-012**: Apply conservative rewrites to remove forbidden patterns

#### Style Enforcement
- **FR-013**: Detect hard violations (em dash, rhetorical contrasts) that block flow
- **FR-014**: Detect soft violations (AI fingerprints) that don't block but need fixing
- **FR-015**: Support up to 5 revision cycles for style compliance
- **FR-016**: Generate edit cycle report if max revisions reached
- **FR-017**: Maintain revision history and violation tracking

#### Validation & Quality Control
- **FR-018**: Extract factual claims and flag those needing sources
- **FR-019**: Score brand alignment (0.0-1.0) with micro-edit suggestions
- **FR-020**: Flag authenticity issues (hype, over-claiming) with suggestions
- **FR-021**: Non-blocking validation that doesn't prevent completion

#### Output & Packaging
- **FR-022**: Generate final approved content per platform
- **FR-023**: Create 7-day publishing schedule with optimal timing
- **FR-024**: Provide performance predictions (low/medium/high engagement)
- **FR-025**: Package all deliverables with guidelines and reports

### 3.2 Platform-Specific Requirements

#### Email
- **FR-026**: Subject line target: 50-70 characters
- **FR-027**: Body limit: 500 characters
- **FR-028**: Structure: salutation, opening, value, CTA, signature
- **FR-029**: Single CTA requirement enforcement
- **FR-030**: Email signature preset integration

#### LinkedIn
- **FR-031**: Character limit: 3000 with 210-char reveal cutoff
- **FR-032**: Hashtag placement at end (3 hashtags)
- **FR-033**: High whitespace density, short paragraphs
- **FR-034**: Professional tone adaptation

#### Instagram
- **FR-035**: Character limit: 2200 with 125-char reveal cutoff
- **FR-036**: 8-20 hashtags placed at end
- **FR-037**: Liberal line breaks and moderate emoji frequency
- **FR-038**: Caption-only focus (no stories)

#### Twitter/X
- **FR-039**: 280 character limit per tweet
- **FR-040**: Thread support for content >240 chars
- **FR-041**: 0-3 hashtags with flexible placement
- **FR-042**: Link placement at end

#### Reddit
- **FR-043**: 40000 character limit
- **FR-044**: Markdown support (lists, bold)
- **FR-045**: TL;DR requirement at end
- **FR-046**: Subreddit rules and description integration

#### Blog
- **FR-047**: 1200 word target (~6000 characters)
- **FR-048**: Deep H2/H3 heading structure
- **FR-049**: Medium link density throughout
- **FR-050**: Title case enforcement option

### 3.3 User Interface Requirements

#### Command Line Interface
- **FR-051**: Simple execution via `python main.py`
- **FR-052**: Environment variable configuration support
- **FR-053**: Concise output summaries with drafts preview

#### Gradio Web Interface (Optional)
- **FR-054**: Platform selection via comma-separated input
- **FR-055**: Topic/goal text input
- **FR-056**: Brand Bible XML text area
- **FR-057**: Milestone streaming display
- **FR-058**: JSON output of final drafts

#### Progress & Feedback
- **FR-059**: Milestone-only streaming (no token-level)
- **FR-060**: Stage completion indicators
- **FR-061**: Revision cycle counter display
- **FR-062**: Clear error messages for failures

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-001**: Complete end-to-end flow in <60 seconds for 3 platforms
- **NFR-002**: Support concurrent processing of multiple platforms
- **NFR-003**: Handle up to 40KB of input text (Reddit maximum)
- **NFR-004**: Process Brand Bible XML up to 10KB

### 4.2 Scalability
- **NFR-005**: Support addition of new platforms without core refactoring
- **NFR-006**: Handle up to 10 platforms in single execution
- **NFR-007**: Preset storage for 100+ brand configurations

### 4.3 Reliability
- **NFR-008**: Retry logic for LLM calls (max 2 retries, 5 second wait)
- **NFR-009**: Circuit breaker for LLM service (5 failures = 30 second cooldown)
- **NFR-010**: Rate limiting: 10 LLM calls per second maximum
- **NFR-011**: Graceful degradation if optional validators fail

### 4.4 Security
- **NFR-012**: Secure API key storage via environment variables
- **NFR-013**: No sensitive data in logs or error messages
- **NFR-014**: Input sanitization for XML parsing
- **NFR-015**: Safe file operations for preset storage

### 4.5 Usability
- **NFR-016**: Clear documentation with examples
- **NFR-017**: Intuitive preset naming conventions
- **NFR-018**: Self-explanatory error messages
- **NFR-019**: Progress indicators for long operations

### 4.6 Maintainability
- **NFR-020**: Modular node-based architecture
- **NFR-021**: Clear separation of concerns (nodes, utilities, flow)
- **NFR-022**: Comprehensive logging for debugging
- **NFR-023**: Type hints throughout Python codebase

---

## 5. Technical Architecture

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   CLI        │  │  Gradio UI   │  │   Future     │ │
│  │  (main.py)   │  │  (Optional)  │  │   Web App    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   WORKFLOW ENGINE                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │           PocketFlow Framework                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐│  │
│  │  │   Flows    │  │   Nodes    │  │   Router   ││  │
│  │  └────────────┘  └────────────┘  └────────────┘│  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   PROCESSING NODES                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Engagement │ Brand │ Voice │ Guidelines │ Content│  │
│  │  Manager   │ Bible │ Align │   Batch    │ Craft  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Style    │ Style │  Edit  │   Fact    │ Brand │  │
│  │   Editor   │ Check │ Report │ Validator │ Guard │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    UTILITY LAYER                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LLM Client │ Parser │ Mapper │ Format │ Check  │  │
│  │ (OpenRouter)│  (XML) │ (Voice)│ (Guide)│ (Style)│  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Presets   │ Stream │Progress│ Report │Rewrite│  │
│  │   Storage   │  (Log) │ (Track)│ (Build)│(Const)│  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │            OpenRouter LLM API                     │  │
│  │         (Claude 3.5 Sonnet Default)              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9+ | Core programming language |
| Framework | PocketFlow | 0.0.1+ | Workflow orchestration |
| LLM Client | OpenAI SDK | 1.30.0+ | OpenRouter integration |
| Config | python-dotenv | 1.0.0+ | Environment management |
| Parsing | PyYAML | 6.0+ | YAML parsing for LLM responses |
| UI (Optional) | Gradio | 4.31.0+ | Web interface |
| XML Parsing | ElementTree | Built-in | Brand Bible parsing |

### 5.3 Data Flow

1. **Input Stage**: User provides platforms, topic, brand bible, intents
2. **Parsing Stage**: XML parsing → Voice mapping → Guidelines generation
3. **Generation Stage**: Section-by-section content creation with constraints
4. **Refinement Stage**: Style editing → Compliance checking (≤5 cycles)
5. **Validation Stage**: Fact checking → Brand alignment → Authenticity
6. **Output Stage**: Packaging → Schedule creation → Performance prediction

### 5.4 Key Components

#### Nodes (nodes.py)
- **EngagementManagerNode**: Handles user input and presets
- **BrandBibleIngestNode**: Parses and validates brand XML
- **VoiceAlignmentNode**: Normalizes voice/tone axes
- **FormatGuidelinesBatch**: Generates platform-specific guidelines
- **ContentCraftsmanNode**: Creates initial content drafts
- **StyleEditorNode**: Removes AI fingerprints
- **StyleComplianceNode**: Validates style adherence
- **ValidationNodes**: Fact, Brand, Authenticity checking
- **AgencyDirectorNode**: Final packaging and scheduling

#### Utilities (utils/)
- **openrouter_client.py**: LLM API integration
- **brand_bible_parser.py**: XML parsing logic
- **format_platform.py**: Platform guideline generation
- **check_style_violations.py**: Pattern detection
- **rewrite_with_constraints.py**: Conservative text modification
- **presets.py**: Local storage management

---

## 6. Implementation Plan

### Phase 1: Foundation Enhancement (Week 1-2)
**Priority: HIGH**
- Add comprehensive test coverage for existing functionality
- Implement proper error handling and logging
- Add input validation for all user inputs
- Create developer documentation

**Deliverables:**
- Unit test suite (>80% coverage)
- Error handling framework
- API documentation
- Developer setup guide

### Phase 2: Platform Expansion (Week 3-4)
**Priority: MEDIUM**
- Add support for additional platforms (Facebook, TikTok)
- Enhance platform-specific formatting rules
- Implement platform template library
- Add A/B testing variations

**Deliverables:**
- 2+ new platform integrations
- Template management system
- A/B testing capability
- Platform best practices guide

### Phase 3: User Experience (Week 5-6)
**Priority: HIGH**
- Build proper web interface (beyond Gradio)
- Add user authentication and project management
- Implement draft history and versioning
- Create collaborative review workflow

**Deliverables:**
- Web application with auth
- Project/campaign management
- Version control for drafts
- Review and approval workflow

### Phase 4: Intelligence Enhancement (Week 7-8)
**Priority: MEDIUM**
- Implement learning from approved content
- Add competitor analysis integration
- Enhance performance prediction models
- Add content effectiveness tracking

**Deliverables:**
- Feedback loop implementation
- Competitor analysis tools
- Enhanced prediction algorithms
- Analytics dashboard

### Phase 5: Enterprise Features (Week 9-10)
**Priority: LOW**
- Multi-tenant architecture
- Role-based access control
- API for external integrations
- White-label capabilities

**Deliverables:**
- Multi-tenancy support
- RBAC implementation
- RESTful API
- White-label configuration

---

## 7. Testing Strategy

### 7.1 Test Levels

#### Unit Testing
- **Coverage Target**: 80% for utilities, 70% for nodes
- **Focus Areas**: 
  - XML parsing edge cases
  - Style violation detection accuracy
  - Platform guideline generation
  - Constraint rewriting logic

#### Integration Testing
- **Coverage Target**: Full pipeline execution paths
- **Focus Areas**:
  - Node-to-node data flow
  - Preset storage and retrieval
  - LLM integration with retry logic
  - Multi-platform batch processing

#### End-to-End Testing
- **Coverage Target**: All user journeys
- **Test Scenarios**:
  - Happy path: 3 platforms, clean execution
  - Edge case: 5 revision cycles with report
  - Error case: LLM failure with circuit breaker
  - Performance: 6 platforms under 60 seconds

### 7.2 Test Data Requirements
- Sample Brand Bibles (5 variations)
- Platform-specific test content
- Known style violations for validation
- Performance benchmark datasets

### 7.3 Quality Gates
- No critical bugs in production
- <2% style violation false positives
- 100% forbidden pattern detection
- <5% LLM call failure rate

---

## 8. Risks & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| LLM API unavailability | Medium | High | Circuit breaker, retry logic, fallback models |
| Style detection false positives | Medium | Medium | Tunable patterns, manual override option |
| Performance degradation at scale | Low | High | Caching, async processing, optimization |
| XML parsing vulnerabilities | Low | High | Input sanitization, schema validation |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Content quality concerns | Medium | High | Human review option, quality scores |
| Brand guideline violations | Low | High | Strict validation, audit trails |
| Platform API changes | Medium | Medium | Modular design, version tracking |
| Competitive pressure | High | Medium | Rapid iteration, unique features |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| API cost overruns | Medium | Medium | Usage monitoring, rate limiting |
| Preset data loss | Low | Medium | Backup strategy, version control |
| User adoption challenges | Medium | High | Training, documentation, support |
| Scaling issues | Low | High | Cloud deployment, load testing |

---

## 9. Success Metrics & KPIs

### Product Metrics
- **Adoption Rate**: 100+ active users within 3 months
- **Content Generation Speed**: <60 seconds for 5 platforms
- **Quality Score**: >90% brand alignment average
- **Error Rate**: <2% failed generations

### Technical Metrics
- **Uptime**: 99.9% availability
- **Response Time**: <2 seconds for UI interactions
- **API Success Rate**: >98% for LLM calls
- **Test Coverage**: >80% overall

### Business Metrics
- **User Satisfaction**: >4.5/5 rating
- **Time Savings**: 75% reduction in content creation time
- **Cost per Generation**: <$0.50 per platform
- **ROI**: 200% within 6 months

---

## 10. Dependencies & Constraints

### External Dependencies
- **OpenRouter API**: Critical dependency for LLM functionality
- **Python Runtime**: Required version 3.9+
- **Network Connectivity**: Required for API calls

### Technical Constraints
- **Character Limits**: Platform-specific (280-40000 chars)
- **API Rate Limits**: 10 calls/second maximum
- **Memory Usage**: <2GB for typical execution
- **Storage**: <100MB for presets

### Business Constraints
- **Budget**: LLM API costs at scale
- **Compliance**: GDPR for user data
- **Licensing**: Open source dependencies
- **Support**: Documentation and training needs

---

## 11. Appendices

### A. Glossary

| Term | Definition |
|------|------------|
| **Brand Bible** | XML document containing brand guidelines, voice, tone, and forbidden patterns |
| **Node** | Individual processing unit in the workflow pipeline |
| **Flow** | Orchestrated sequence of nodes |
| **Forbidden Patterns** | Text patterns that must never appear in content (em dash, rhetorical contrasts) |
| **AI Fingerprints** | Recognizable patterns indicating AI-generated content |
| **Preset** | Saved configuration for reuse (Brand Bible, signatures, styles) |
| **Style Compliance** | Adherence to brand guidelines and platform requirements |
| **Revision Cycle** | Iteration of editing and compliance checking |

### B. Sample Brand Bible XML

```xml
<brand>
  <brand_name>Acme Corporation</brand_name>
  <voice>professional</voice>
  <tone>confident</tone>
  <forbiddens>
    <item>em_dash</item>
    <item>rhetorical_contrast</item>
    <item>corporate_jargon</item>
  </forbiddens>
  <values>
    <item>innovation</item>
    <item>reliability</item>
    <item>customer_focus</item>
  </values>
  <personality>
    <trait>approachable</trait>
    <trait>knowledgeable</trait>
    <trait>solution-oriented</trait>
  </personality>
</brand>
```

### C. Platform Comparison Matrix

| Platform | Char Limit | Hashtags | Links | Markdown | Special Requirements |
|----------|-----------|----------|-------|----------|---------------------|
| Email | 500 body | No | Yes | No | Single CTA, signature |
| LinkedIn | 3000 | 3 (end) | Yes | No | Professional tone |
| Instagram | 2200 | 8-20 (end) | No | No | Emoji, line breaks |
| Twitter/X | 280 | 0-3 | Yes | No | Thread support |
| Reddit | 40000 | No | Yes | Yes | TL;DR, subreddit rules |
| Blog | ~6000 | No | Yes | Yes | H2/H3 structure |

### D. Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| E001 | LLM API timeout | Retry with exponential backoff |
| E002 | Invalid Brand Bible XML | Check XML syntax and required fields |
| E003 | Rate limit exceeded | Wait and retry with reduced frequency |
| E004 | Style compliance max iterations | Manual review required |
| E005 | Platform not supported | Check supported platforms list |
| E006 | Preset not found | Verify preset name or create new |
| E007 | Circuit breaker open | Wait 30 seconds for recovery |

---

## Document Information

- **Version**: 1.0.0
- **Created**: December 2024
- **Last Updated**: December 2024
- **Status**: APPROVED
- **Author**: PM Agent (BMad Method)
- **Owner**: Development Team
- **Review Cycle**: Quarterly

---

## Approval Sign-offs

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Manager | PM Agent | Dec 2024 | Auto-generated |
| Technical Lead | [Pending] | [Pending] | [Pending] |
| Engineering Manager | [Pending] | [Pending] | [Pending] |
| QA Lead | [Pending] | [Pending] | [Pending] |

---

*This PRD is a living document and will be updated as requirements evolve and new insights are gained through development and user feedback.*