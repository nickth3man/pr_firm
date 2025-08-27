"""
Pytest configuration and fixtures for Virtual PR Firm tests.
"""
import pytest
import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_brand_bible():
    """Sample brand bible for testing."""
    return {
        "xml_raw": """
        <brand>
            <name>Test Brand</name>
            <voice>Professional yet approachable</voice>
            <values>Quality, Innovation, Customer Focus</values>
        </brand>
        """
    }

@pytest.fixture
def sample_task_requirements():
    """Sample task requirements for testing."""
    return {
        "platforms": ["email", "linkedin"],
        "topic_or_goal": "Test campaign announcement",
        "intents_by_platform": {
            "email": {"type": "preset", "value": "outreach"},
            "linkedin": {"type": "custom", "value": "thought leadership"}
        }
    }

@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock LLM response for testing."
                }
            }
        ]
    }
