"""
Unit tests for check_style_violations.py
"""

import pytest
import os
from src.pr_firm.utils.helpers.check_style_violations import (
    check_style_violations,
    StyleViolationError,
    StyleViolation
)

# Fixture paths
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../data/fixtures/style_violations')

def test_check_valid_text():
    """Test checking a text with no style violations"""
    file_path = os.path.join(FIXTURE_DIR, 'valid_text.txt')

    with open(file_path, 'r') as f:
        text = f.read()

    violations = check_style_violations(text)

    # Should return empty list for valid text
    assert len(violations) == 0

def test_check_invalid_text():
    """Test checking a text with multiple style violations"""
    file_path = os.path.join(FIXTURE_DIR, 'invalid_text.txt')

    with open(file_path, 'r') as f:
        text = f.read()

    violations = check_style_violations(text)

    # Should find multiple violations
    assert len(violations) > 0

    # Check for specific violation types
    violation_types = [v.violation_type for v in violations]
    assert 'passive_voice' in violation_types
    assert 'long_sentence' in violation_types
    assert 'double_space' in violation_types
    assert 'oxford_comma' in violation_types
    assert 'em_dash_spacing' in violation_types

def test_check_edge_cases():
    """Test checking text with edge cases"""
    file_path = os.path.join(FIXTURE_DIR, 'edge_case_text.txt')

    with open(file_path, 'r') as f:
        text = f.read()

    violations = check_style_violations(text)

    # Should find specific edge case violations
    assert len(violations) > 0

    violation_types = [v.violation_type for v in violations]
    assert 'long_sentence' in violation_types
    assert 'multiple_spaces' in violation_types
    assert 'inconsistent_indentation' in violation_types

def test_empty_text():
    """Test checking empty text"""
    violations = check_style_violations("")
    assert len(violations) == 0

def test_violation_details():
    """Test that violations contain proper details"""
    file_path = os.path.join(FIXTURE_DIR, 'invalid_text.txt')

    with open(file_path, 'r') as f:
        text = f.read()

    violations = check_style_violations(text)

    # Check that each violation has the required attributes
    for violation in violations:
        assert hasattr(violation, 'violation_type')
        assert hasattr(violation, 'message')
        assert hasattr(violation, 'line_number')
        assert hasattr(violation, 'context')

        # Verify attributes are not empty
        assert violation.violation_type
        assert violation.message
        assert violation.line_number >= 0
        assert violation.context

def test_passive_voice_detection():
    """Test specific detection of passive voice"""
    text = "The report was written by the team. Mistakes were made."

    violations = check_style_violations(text)

    passive_violations = [v for v in violations if v.violation_type == 'passive_voice']
    assert len(passive_violations) >= 2

    # Check specific messages
    messages = [v.message for v in passive_violations]
    assert any("was written" in msg for msg in messages)
    assert any("were made" in msg for msg in messages)

def test_long_sentence_detection():
    """Test specific detection of long sentences"""
    # Create a very long sentence (more than 30 words)
    long_sentence = "This is a very long sentence that goes on and on without any proper punctuation or breaks to test how the system handles very long input that might cause buffer overflows or performance issues in the parsing algorithm especially when dealing with complex natural language processing tasks."

    violations = check_style_violations(long_sentence)

    long_sentence_violations = [v for v in violations if v.violation_type == 'long_sentence']
    assert len(long_sentence_violations) >= 1

    # Check the message contains word count
    message = long_sentence_violations[0].message
    assert "word" in message.lower()
    assert "30" in message

def test_oxford_comma_detection():
    """Test specific detection of missing Oxford comma"""
    text = "I like red, white and blue."

    violations = check_style_violations(text)

    oxford_violations = [v for v in violations if v.violation_type == 'oxford_comma']
    assert len(oxford_violations) >= 1

    # Check the message
    message = oxford_violations[0].message
    assert "oxford comma" in message.lower()

def test_em_dash_spacing_detection():
    """Test specific detection of spaces around em dashes"""
    text = "This is a test - with spaces around em dashes - which is incorrect."

    violations = check_style_violations(text)

    em_dash_violations = [v for v in violations if v.violation_type == 'em_dash_spacing']
    assert len(em_dash_violations) >= 1

    # Check the message
    message = em_dash_violations[0].message
    assert "em dash" in message.lower()
    assert "spaces" in message.lower()

def test_double_space_detection():
    """Test specific detection of double spaces after periods"""
    text = "This has double spaces.  Like this.  And again."

    violations = check_style_violations(text)

    double_space_violations = [v for v in violations if v.violation_type == 'double_space']
    assert len(double_space_violations) >= 2

    # Check the message
    message = double_space_violations[0].message
    assert "double space" in message.lower()

def test_line_number_accuracy():
    """Test that line numbers are accurately reported"""
    text = """Line 1 is fine.
This is line 2 with a double space.  See?
Line 3 has passive voice: The report was written.
Line 4 is okay."""

    violations = check_style_violations(text)

    # Find double space violation
    double_space_violations = [v for v in violations if v.violation_type == 'double_space']
    assert len(double_space_violations) >= 1
    assert double_space_violations[0].line_number == 2

    # Find passive voice violation
    passive_violations = [v for v in violations if v.violation_type == 'passive_voice']
    assert len(passive_violations) >= 1
    assert passive_violations[0].line_number == 3

def test_context_provided():
    """Test that context is provided with violations"""
    text = """This is line 1.
Line 2 has a problem.  Double space here.
The report was written by someone on line 3."""

    violations = check_style_violations(text)

    for violation in violations:
        assert violation.context.strip()  # Context should not be empty
        # Context should contain the problematic text
        if violation.violation_type == 'double_space':
            assert "Double space" in violation.context
        elif violation.violation_type == 'passive_voice':
            assert "was written" in violation.context

def test_style_violation_class():
    """Test the StyleViolation class directly"""
    violation = StyleViolation(
        violation_type="test_type",
        message="Test message",
        line_number=5,
        context="Test context"
    )

    assert violation.violation_type == "test_type"
    assert violation.message == "Test message"
    assert violation.line_number == 5
    assert violation.context == "Test context"

    # Test string representation
    str_rep = str(violation)
    assert "test_type" in str_rep
    assert "Test message" in str_rep
    assert "5" in str_rep

def test_style_violation_error():
    """Test the StyleViolationError exception"""
    try:
        raise StyleViolationError("Test error message")
    except StyleViolationError as e:
        assert str(e) == "Test error message"
        assert isinstance(e, Exception)