# 11. Appendices

## A. Glossary

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

## B. Sample Brand Bible XML

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

## C. Platform Comparison Matrix

| Platform | Char Limit | Hashtags | Links | Markdown | Special Requirements |
|----------|-----------|----------|-------|----------|---------------------|
| Email | 500 body | No | Yes | No | Single CTA, signature |
| LinkedIn | 3000 | 3 (end) | Yes | No | Professional tone |
| Instagram | 2200 | 8-20 (end) | No | No | Emoji, line breaks |
| Twitter/X | 280 | 0-3 | Yes | No | Thread support |
| Reddit | 40000 | No | Yes | Yes | TL;DR, subreddit rules |
| Blog | ~6000 | No | Yes | Yes | H2/H3 structure |

## D. Error Codes

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
