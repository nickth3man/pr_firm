---
title: "pr_firm Coding Standards"
---

This project applies pragmatic Python coding standards focused on readability and testability.

1. General

- Use descriptive names; avoid single-letter variables for non-iterators.
- Keep functions small and single-purpose.
- Use type hints for public APIs.

2. Imports

- Group standard library, third-party, local imports.

3. Logging & Errors

- Use exceptions for error conditions; don't swallow exceptions silently.

4. Tests

- Unit tests for parsing, formatting, and rewrite logic.
- Integration tests with a mocked LLM client.
