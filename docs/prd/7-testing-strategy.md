# 7. Testing Strategy

## 7.1 Test Levels

### Unit Testing
- **Coverage Target**: 80% for utilities, 70% for nodes
- **Focus Areas**: 
  - XML parsing edge cases
  - Style violation detection accuracy
  - Platform guideline generation
  - Constraint rewriting logic

### Integration Testing
- **Coverage Target**: Full pipeline execution paths
- **Focus Areas**:
  - Node-to-node data flow
  - Preset storage and retrieval
  - LLM integration with retry logic
  - Multi-platform batch processing

### End-to-End Testing
- **Coverage Target**: All user journeys
- **Test Scenarios**:
  - Happy path: 3 platforms, clean execution
  - Edge case: 5 revision cycles with report
  - Error case: LLM failure with circuit breaker
  - Performance: 6 platforms under 60 seconds

## 7.2 Test Data Requirements
- Sample Brand Bibles (5 variations)
- Platform-specific test content
- Known style violations for validation
- Performance benchmark datasets

## 7.3 Quality Gates
- No critical bugs in production
- <2% style violation false positives
- 100% forbidden pattern detection
- <5% LLM call failure rate

---
