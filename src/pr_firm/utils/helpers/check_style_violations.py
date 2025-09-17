"""
Style Violation Checker

This module provides functionality to check text for style violations
based on brand guidelines and style rules.
"""

import re
from typing import List, NamedTuple, Optional
from dataclasses import dataclass

@dataclass
class StyleViolation:
    """Represents a single style violation"""
    violation_type: str
    message: str
    line_number: int
    context: str

    def __str__(self):
        return f"{self.violation_type}: {self.message} (line {self.line_number}) - {self.context[:50]}..."

class StyleViolationError(Exception):
    """Custom exception for style violation errors"""
    pass

def check_style_violations(text: str) -> List[StyleViolation]:
    """
    Check text for style violations based on brand guidelines.

    Args:
        text: The text to check for style violations

    Returns:
        List of StyleViolation objects found in the text
    """
    if not text or not text.strip():
        return []

    violations = []
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        # Check for passive voice
        passive_voice_violations = _check_passive_voice(line, line_num)
        violations.extend(passive_voice_violations)

        # Check for long sentences
        long_sentence_violations = _check_long_sentences(line, line_num)
        violations.extend(long_sentence_violations)

        # Check for Oxford comma violations
        oxford_comma_violations = _check_oxford_comma(line, line_num)
        violations.extend(oxford_comma_violations)

        # Check for em dash spacing
        em_dash_violations = _check_em_dash_spacing(line, line_num)
        violations.extend(em_dash_violations)

        # Check for double spaces
        double_space_violations = _check_double_spaces(line, line_num)
        violations.extend(double_space_violations)

        # Check for multiple spaces
        multiple_space_violations = _check_multiple_spaces(line, line_num)
        violations.extend(multiple_space_violations)

        # Check for inconsistent indentation
        indentation_violations = _check_indentation(line, line_num, lines)
        violations.extend(indentation_violations)

    return violations

def _check_passive_voice(line: str, line_num: int) -> List[StyleViolation]:
    """Check for passive voice constructions"""
    violations = []

    # Common passive voice patterns
    passive_patterns = [
        r'\bwas\s+\w+ed\b',          # "was created"
        r'\bwere\s+\w+ed\b',         # "were made"
        r'\bhas\s+been\s+\w+ed\b',   # "has been developed"
        r'\bhave\s+been\s+\w+ed\b',  # "have been implemented"
        r'\bis\s+\w+ed\b',           # "is written"
        r'\bare\s+\w+ed\b',          # "are processed"
        r'\bby\s+\w+\b',             # "by the team" (often indicates passive)
        r'\bto\s+be\s+\w+ed\b'       # "to be completed"
    ]

    for pattern in passive_patterns:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            context = line[max(0, match.start()-20):min(len(line), match.end()+20)]
            violations.append(StyleViolation(
                violation_type='passive_voice',
                message=f"Passive voice detected: '{match.group()}'",
                line_number=line_num,
                context=context
            ))

    return violations

def _check_long_sentences(line: str, line_num: int) -> List[StyleViolation]:
    """Check for sentences that are too long"""
    violations = []

    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]', line)
    sentences = [s.strip() for s in sentences if s.strip()]

    for sentence in sentences:
        word_count = len(re.findall(r'\w+', sentence))
        if word_count > 30:  # Threshold for long sentences
            violations.append(StyleViolation(
                violation_type='long_sentence',
                message=f"Sentence too long ({word_count} words, max 30 recommended)",
                line_number=line_num,
                context=sentence[:100] + ("..." if len(sentence) > 100 else "")
            ))

    return violations

def _check_oxford_comma(line: str, line_num: int) -> List[StyleViolation]:
    """Check for missing Oxford comma"""
    violations = []

    # Pattern for lists that should have Oxford comma
    # Example: "a, b and c" should be "a, b, and c"
    pattern = r'\b(\w+),\s*(\w+)\s+and\s+(\w+)\b'

    matches = re.finditer(pattern, line)
    for match in matches:
        violations.append(StyleViolation(
            violation_type='oxford_comma',
            message=f"Missing Oxford comma: should be '{match.group(1)}, {match.group(2)}, and {match.group(3)}'",
            line_number=line_num,
            context=match.group(0)
        ))

    return violations

def _check_em_dash_spacing(line: str, line_num: int) -> List[StyleViolation]:
    """Check for incorrect spacing around em dashes"""
    violations = []

    # Pattern for em dashes with spaces (should be no spaces)
    pattern = r'\s—\s'

    matches = re.finditer(pattern, line)
    for match in matches:
        violations.append(StyleViolation(
            violation_type='em_dash_spacing',
            message="Em dash should not have spaces around it",
            line_number=line_num,
            context=match.group(0)
        ))

    return violations

def _check_double_spaces(line: str, line_num: int) -> List[StyleViolation]:
    """Check for double spaces after periods"""
    violations = []

    # Pattern for double spaces after periods
    pattern = r'\.\s\s'

    matches = re.finditer(pattern, line)
    for match in matches:
        violations.append(StyleViolation(
            violation_type='double_space',
            message="Double space after period (should be single space)",
            line_number=line_num,
            context=match.group(0)
        ))

    return violations

def _check_multiple_spaces(line: str, line_num: int) -> List[StyleViolation]:
    """Check for multiple spaces between words"""
    violations = []

    # Pattern for multiple spaces between words
    pattern = r'(?<!\n)\s{3,}(?!\n)'

    matches = re.finditer(pattern, line)
    for match in matches:
        violations.append(StyleViolation(
            violation_type='multiple_spaces',
            message=f"Multiple spaces between words ({len(match.group())} spaces)",
            line_number=line_num,
            context=match.group(0)
        ))

    return violations

def _check_indentation(line: str, line_num: int, all_lines: List[str]) -> List[StyleViolation]:
    """Check for inconsistent indentation"""
    violations = []

    # Only check if this is part of a paragraph (not first line)
    if line_num == 1:
        return violations

    # Get previous non-empty line
    prev_line = None
    for i in range(line_num-2, -1, -1):
        if all_lines[i].strip():
            prev_line = all_lines[i]
            break

    if not prev_line:
        return violations

    # Check if current line has different indentation than previous
    current_indent = len(line) - len(line.lstrip())
    prev_indent = len(prev_line) - len(prev_line.lstrip())

    if current_indent != prev_indent and abs(current_indent - prev_indent) > 2:
        violations.append(StyleViolation(
            violation_type='inconsistent_indentation',
            message=f"Inconsistent indentation (current: {current_indent}, previous: {prev_indent})",
            line_number=line_num,
            context=line
        ))

    return violations
