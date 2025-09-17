"""
Pytest configuration and fixtures for Virtual PR Firm tests.
"""
import pytest
import os
import sys
from pathlib import Path

# Add the project root and src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

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

@pytest.fixture
def mock_llm_call():
    """Mock LLM call function."""
    def _mock_call(messages, **kwargs):
        if isinstance(messages, str):
            prompt = messages
        elif isinstance(messages, list):
            prompt = messages[-1]["content"] if messages else ""
        else:
            prompt = str(messages)

        # Return different responses based on prompt content
        if "summarize" in prompt.lower():
            return "This is a summary of the content."
        elif "rewrite" in prompt.lower():
            return "This is the rewritten content."
        elif "analyze" in prompt.lower():
            return "claims:\n  - text: 'Test claim'\n    needs_source: false"
        elif "brand voice" in prompt.lower():
            return "Professional yet approachable voice guidelines."
        else:
            return "This is a mock LLM response for testing."

    return _mock_call

@pytest.fixture
def mock_brand_bible_parsed():
    """Mock parsed brand bible data."""
    return {
        "metadata": {
            "company_name": "Test Corp",
            "version": "1.0",
            "last_updated": "2023-11-15"
        },
        "brand_voice": {
            "description": "Professional yet approachable",
            "characteristics": ["knowledgeable", "helpful"],
            "tone": {"formal": "70%", "friendly": "30%"}
        },
        "platforms": {
            "twitter": {
                "characteristics": {"concise": True, "engaging": True},
                "style_rules": ["Use 280 characters or less"],
                "content_types": {
                    "announcement": {
                        "description": "Product announcements",
                        "examples": ["New feature launched!"],
                        "structure": {}
                    }
                }
            },
            "linkedin": {
                "characteristics": {"professional": True, "insightful": True},
                "style_rules": ["Use professional language"],
                "content_types": {
                    "thought_leadership": {
                        "description": "Industry insights",
                        "examples": ["Industry trends analysis"],
                        "structure": {}
                    }
                }
            }
        },
        "style_guide": {
            "grammar": ["Use active voice"],
            "punctuation": ["Oxford comma required"],
            "formatting": ["One space after periods"]
        }
    }

@pytest.fixture
def mock_brand_voice():
    """Mock brand voice data."""
    return {
        "description": "Professional yet approachable, knowledgeable but not condescending",
        "characteristics": ["knowledgeable", "helpful", "slightly humorous", "concise"],
        "axes": {"formality": "medium", "vividness": "balanced"},
        "styles": {"voice": "clear"},
        "forbiddens": {"em_dash": True, "rhetorical_contrast": True}
    }

@pytest.fixture
def mock_platform_guidelines():
    """Mock platform guidelines."""
    return {
        "twitter": {
            "structure": ["hook", "body", "cta"],
            "limits": {"chars": 280},
            "section_budgets": {"hook": 50, "body": 150, "cta": 30},
            "hashtags": {"count": 2, "placement": "end"}
        },
        "linkedin": {
            "structure": ["introduction", "insight", "conclusion"],
            "limits": {"chars": 3000},
            "section_budgets": {"introduction": 300, "insight": 2000, "conclusion": 200},
            "hashtags": {"count": 3, "placement": "end"}
        }
    }

@pytest.fixture
def mock_content_pieces():
    """Mock content pieces."""
    return {
        "twitter": {
            "sections": {
                "hook": "Exciting news!",
                "body": "We've launched a new feature that will revolutionize your workflow.",
                "cta": "Check it out now!"
            },
            "text": "Exciting news! We've launched a new feature that will revolutionize your workflow. Check it out now! #innovation #tech"
        },
        "linkedin": {
            "sections": {
                "introduction": "I'm excited to share some insights about the future of technology.",
                "insight": "The key trend we're seeing is the convergence of AI and human creativity.",
                "conclusion": "The future is bright for those who embrace these changes."
            },
            "text": "I'm excited to share some insights about the future of technology. The key trend we're seeing is the convergence of AI and human creativity. The future is bright for those who embrace these changes. #technology #innovation #future"
        }
    }

@pytest.fixture
def mock_workflow_state():
    """Mock workflow state."""
    return {
        "current_stage": "engagement",
        "completed_stages": ["engagement"],
        "revision_count": 0,
        "manual_review_required": False
    }

@pytest.fixture
def mock_shared_store(mock_brand_bible_parsed, mock_brand_voice, mock_platform_guidelines, mock_content_pieces, mock_workflow_state):
    """Mock complete shared store."""
    return {
        "config": {"style_policy": "strict"},
        "task_requirements": {
            "platforms": ["twitter", "linkedin"],
            "topic_or_goal": "Announce our new AI feature",
            "intents_by_platform": {
                "twitter": {"type": "preset", "value": "announcement"},
                "linkedin": {"type": "custom", "value": "thought leadership"}
            }
        },
        "brand_bible": {
            "xml_raw": "<brand_bible><brand_voice><description>Test</description></brand_voice></brand_bible>",
            "parsed": mock_brand_bible_parsed,
            "persona_voice": mock_brand_voice
        },
        "platform_guidelines": mock_platform_guidelines,
        "content_pieces": mock_content_pieces,
        "style_compliance": {},
        "workflow_state": mock_workflow_state,
        "final_campaign": {},
        "stream": type('MockStream', (), {
            'messages': lambda: [],
            'emit': lambda *args: None
        })(),
        "llm": {"model": "test-model", "temperature": 0.7}
    }

@pytest.fixture
def mock_style_violations():
    """Mock style violations."""
    return [
        type('StyleViolation', (), {
            'violation_type': 'passive_voice',
            'message': 'Passive voice detected: was written',
            'line_number': 1,
            'context': 'The report was written by the team.'
        })(),
        type('StyleViolation', (), {
            'violation_type': 'long_sentence',
            'message': 'Sentence too long: 45 words',
            'line_number': 2,
            'context': 'This is a very long sentence that contains many words and should be flagged as too long for most style guides.'
        })()
    ]

@pytest.fixture
def mock_style_check_response():
    """Mock style check response."""
    return {
        "violations": [
            {"type": "passive_voice", "message": "Passive voice detected", "line": 1},
            {"type": "long_sentence", "message": "Sentence too long", "line": 2}
        ]
    }
