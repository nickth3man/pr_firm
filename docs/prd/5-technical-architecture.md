# 5. Technical Architecture

## 5.1 System Architecture

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

## 5.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.9+ | Core programming language |
| Framework | PocketFlow | 0.0.1+ | Workflow orchestration |
| LLM Client | OpenAI SDK | 1.30.0+ | OpenRouter integration |
| Config | python-dotenv | 1.0.0+ | Environment management |
| Parsing | PyYAML | 6.0+ | YAML parsing for LLM responses |
| UI (Optional) | Gradio | 4.31.0+ | Web interface |
| XML Parsing | ElementTree | Built-in | Brand Bible parsing |

## 5.3 Data Flow

1. **Input Stage**: User provides platforms, topic, brand bible, intents
2. **Parsing Stage**: XML parsing → Voice mapping → Guidelines generation
3. **Generation Stage**: Section-by-section content creation with constraints
4. **Refinement Stage**: Style editing → Compliance checking (≤5 cycles)
5. **Validation Stage**: Fact checking → Brand alignment → Authenticity
6. **Output Stage**: Packaging → Schedule creation → Performance prediction

## 5.4 Key Components

### Nodes (nodes.py)
- **EngagementManagerNode**: Handles user input and presets
- **BrandBibleIngestNode**: Parses and validates brand XML
- **VoiceAlignmentNode**: Normalizes voice/tone axes
- **FormatGuidelinesBatch**: Generates platform-specific guidelines
- **ContentCraftsmanNode**: Creates initial content drafts
- **StyleEditorNode**: Removes AI fingerprints
- **StyleComplianceNode**: Validates style adherence
- **ValidationNodes**: Fact, Brand, Authenticity checking
- **AgencyDirectorNode**: Final packaging and scheduling

### Utilities (utils/)
- **openrouter_client.py**: LLM API integration
- **brand_bible_parser.py**: XML parsing logic
- **format_platform.py**: Platform guideline generation
- **check_style_violations.py**: Pattern detection
- **rewrite_with_constraints.py**: Conservative text modification
- **presets.py**: Local storage management

---
