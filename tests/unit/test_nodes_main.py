"""
Unit tests for nodes/__main__.py
"""

import pytest
from unittest.mock import patch, MagicMock
from src.pr_firm.nodes.engagement.manager import EngagementManagerNode
from src.pr_firm.nodes.brand.ingest import BrandBibleIngestNode
from src.pr_firm.nodes.brand.voice import VoiceAlignmentNode
from src.pr_firm.nodes.__main__ import (
    calculate_section_budgets,
    enforce_hashtag_placements,
    FormatGuidelinesRouter,
    _BaseGuidelinesNode,
    ContentCraftsmanNode,
    StyleEditorNode,
    StyleComplianceNode,
    EditCycleReportNode,
    FactValidatorNode
)


class TestCalculateSectionBudgets:
    """Test cases for calculate_section_budgets function."""

    def test_calculate_with_explicit_budgets(self):
        """Test calculation with explicit section budgets."""
        guidelines = {
            "structure": ["intro", "body", "conclusion"],
            "section_budgets": {"intro": 100, "body": 200, "conclusion": 50}
        }

        result = calculate_section_budgets(guidelines)

        assert result == {"intro": 100, "body": 200, "conclusion": 50}

    def test_calculate_with_partial_explicit_budgets(self):
        """Test calculation with partial explicit budgets."""
        guidelines = {
            "structure": ["intro", "body", "conclusion"],
            "section_budgets": {"intro": 100}
        }

        result = calculate_section_budgets(guidelines)

        assert result == {"intro": 100, "body": 120, "conclusion": 120}

    def test_calculate_with_char_limits(self):
        """Test calculation with character limits."""
        guidelines = {
            "structure": ["intro", "body"],
            "limits": {"chars": 600}
        }

        result = calculate_section_budgets(guidelines)

        assert result == {"intro": 300, "body": 300}

    def test_calculate_with_empty_structure(self):
        """Test calculation with empty structure."""
        guidelines = {"structure": []}

        result = calculate_section_budgets(guidelines)

        assert result == {}

    def test_calculate_with_no_limits(self):
        """Test calculation with no limits specified."""
        guidelines = {
            "structure": ["intro", "body"],
            "limits": {}
        }

        result = calculate_section_budgets(guidelines)

        assert result == {"intro": 400, "body": 400}  # Uses default 800 / 2


class TestEnforceHashtagPlacements:
    """Test cases for enforce_hashtag_placements function."""

    def test_instagram_end_placement(self):
        """Test hashtag placement for Instagram."""
        text = "Check out our new product #awesome #amazing"
        guidelines = {"hashtags": {"count": 2, "placement": "end"}}
        platform = "instagram"

        result = enforce_hashtag_placements(text, guidelines, platform)

        assert result == "Check out our new product\n#awesome #amazing"

    def test_twitter_inline_and_end(self):
        """Test hashtag placement for Twitter with inline and end."""
        text = "Exciting news #tech #innovation #future #ai"
        guidelines = {"hashtags": {"count": 2}}
        platform = "twitter"

        result = enforce_hashtag_placements(text, guidelines, platform)

        # Should keep 2 inline and move extras to end
        assert "#tech #innovation" in result
        assert "#future #ai" in result

    def test_reddit_remove_hashtags(self):
        """Test hashtag removal for Reddit."""
        text = "Interesting discussion #reddit #discussion"
        guidelines = {"hashtags": {"count": 0}}
        platform = "reddit"

        result = enforce_hashtag_placements(text, guidelines, platform)

        assert "#" not in result
        assert result == "Interesting discussion"

    def test_no_hashtags_config(self):
        """Test with no hashtags configuration."""
        text = "Regular text without hashtags"
        guidelines = {}
        platform = "instagram"

        result = enforce_hashtag_placements(text, guidelines, platform)

        assert result == text

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Line 1  \t\n\n\n\nLine 2"
        guidelines = {}
        platform = "instagram"

        result = enforce_hashtag_placements(text, guidelines, platform)

        assert result == "Line 1\n\nLine 2"


class TestEngagementManagerNode:
    """Test cases for EngagementManagerNode."""

    def test_prep_method(self):
        """Test prep method extracts required data."""
        shared = {
            "task_requirements": {"platforms": ["email", "linkedin"]},
            "brand_bible": {"xml_raw": "<xml></xml>"},
            "house_style": {"signature": "Best"},
            "llm": {"model": "test-model"}
        }

        node = EngagementManagerNode()
        result = node.prep(shared)

        expected = {
            "task_requirements": {"platforms": ["email", "linkedin"]},
            "brand_bible": {"xml_raw": "<xml></xml>"},
            "house_style": {"signature": "Best"},
            "llm": {"model": "test-model"}
        }
        assert result == expected

    @patch('src.pr_firm.nodes.engagement.manager.call_llm')
    def test_exec_with_auto_platforms(self, mock_call_llm):
        """Test exec method with auto platforms."""
        mock_call_llm.return_value = "email:\n  - announcement\nlinkedin:\n  - thought leadership"

        prep = {
            "task_requirements": {
                "platforms": ["email", "linkedin"],
                "intents_by_platform": {
                    "email": {"type": "auto"},
                    "linkedin": {"type": "auto"}
                },
                "topic_or_goal": "Test topic"
            },
            "llm": {"model": "test-model", "temperature": 0.7}
        }

        node = EngagementManagerNode()
        result = node.exec(prep)

        assert "auto_intents" in result
        mock_call_llm.assert_called_once()

    def test_exec_no_auto_platforms(self):
        """Test exec method with no auto platforms."""
        prep = {
            "task_requirements": {
                "platforms": ["email"],
                "intents_by_platform": {
                    "email": {"type": "preset", "value": "outreach"}
                }
            }
        }

        node = EngagementManagerNode()
        result = node.exec(prep)

        assert result == {"auto_intents": {}}

    @patch('src.pr_firm.nodes.engagement.manager.initialize_shared_store')
    def test_post_updates_workflow_state(self, mock_init_store):
        """Test post method updates workflow state."""
        shared = {
            "stream": MagicMock(),
            "task_requirements": {"intents_by_platform": {}},
            "workflow_state": {"completed_stages": []}
        }

        prep_res = {}
        exec_res = {"auto_intents": {"email": "test intent"}}

        node = EngagementManagerNode()
        result = node.post(shared, prep_res, exec_res)

        assert shared["workflow_state"]["current_stage"] == "brand_bible_ingest"
        assert "engagement" in shared["workflow_state"]["completed_stages"]
        assert result == "default"
        shared["stream"].emit.assert_called_once()


class TestBrandBibleIngestNode:
    """Test cases for BrandBibleIngestNode."""

    @patch('src.pr_firm.nodes.brand.ingest.parse_brand_bible')
    @patch('src.pr_firm.nodes.brand.ingest.brand_bible_to_voice')
    def test_exec_processes_brand_bible(self, mock_brand_to_voice, mock_parse):
        """Test exec method processes brand bible correctly."""
        mock_parse.return_value = ({"parsed": "data"}, ["missing"])
        mock_brand_to_voice.return_value = {"voice": "persona"}

        node = BrandBibleIngestNode()
        result = node.exec("<xml></xml>")

        expected = {
            "parsed": {"parsed": "data"},
            "missing": ["missing"],
            "persona": {"voice": "persona"}
        }
        assert result == expected

    def test_post_updates_shared_store(self):
        """Test post method updates shared store."""
        shared = {}

        node = BrandBibleIngestNode()
        exec_res = {
            "parsed": {"test": "data"},
            "missing": ["field1"],
            "persona": {"voice": "test"}
        }

        result = node.post(shared, "<xml>", exec_res)

        assert shared["brand_bible"]["parsed"] == {"test": "data"}
        assert shared["brand_bible"]["missing"] == ["field1"]
        assert shared["brand_bible"]["persona_voice"] == {"voice": "test"}
        assert shared["workflow_state"]["current_stage"] == "voice_alignment"
        assert result == "default"


class TestVoiceAlignmentNode:
    """Test cases for VoiceAlignmentNode."""

    def test_exec_normalizes_persona_voice(self):
        """Test exec method normalizes persona voice."""
        persona_voice = {
            "axes": {"formality": "high"},
            "styles": {"voice": "professional"}
        }

        node = VoiceAlignmentNode()
        result = node.exec(persona_voice)

        assert result["axes"]["formality"] == "high"
        assert result["axes"]["vividness"] == "balanced"
        assert result["styles"]["voice"] == "professional"
        assert result["forbiddens"]["em_dash"] is True
        assert result["forbiddens"]["rhetorical_contrast"] is True

    def test_post_updates_brand_bible(self):
        """Test post method updates brand bible."""
        shared = {"brand_bible": {}}

        node = VoiceAlignmentNode()
        exec_res = {"normalized": "voice"}

        result = node.post(shared, {}, exec_res)

        assert shared["brand_bible"]["persona_voice"] == {"normalized": "voice"}
        assert shared["workflow_state"]["current_stage"] == "guidelines"
        assert result == "default"


class TestFormatGuidelinesRouter:
    """Test cases for FormatGuidelinesRouter."""

    def test_post_returns_platform_action(self):
        """Test post method returns platform as action."""
        shared = {}

        node = FormatGuidelinesRouter()
        node.set_params({"platform": "twitter"})

        result = node.post(shared, None, None)

        assert result == "twitter"

    def test_post_returns_default_for_empty_platform(self):
        """Test post method returns default for empty platform."""
        shared = {}

        node = FormatGuidelinesRouter()
        node.set_params({"platform": ""})

        result = node.post(shared, None, None)

        assert result == "default"


class TestBaseGuidelinesNode:
    """Test cases for _BaseGuidelinesNode base class."""

    @patch('src.pr_firm.nodes.__main__.build_guidelines')
    def test_exec_calls_build_guidelines(self, mock_build):
        """Test exec method calls build_guidelines."""
        mock_build.return_value = {"guidelines": "test"}

        # Create a concrete subclass for testing
        class TestGuidelinesNode(_BaseGuidelinesNode):
            platform_name = "test"

        node = TestGuidelinesNode()
        prep = {
            "persona": {"voice": "test"},
            "intent": "test_intent",
            "nuance": {"test": "setting"},
            "reddit": None
        }

        result = node.exec(prep)

        mock_build.assert_called_once_with(
            "test",
            {"voice": "test"},
            "test_intent",
            platform_nuance={"test": "setting"},
            reddit=None
        )
        assert result == {"guidelines": "test"}

    def test_post_updates_platform_guidelines(self):
        """Test post method updates platform guidelines."""
        shared = {}

        # Create a concrete subclass for testing
        class TestGuidelinesNode(_BaseGuidelinesNode):
            platform_name = "test"

        node = TestGuidelinesNode()
        exec_res = {"test": "guidelines"}

        result = node.post(shared, {}, exec_res)

        assert shared["platform_guidelines"]["test"] == {"test": "guidelines"}
        assert result == "default"


class TestContentCraftsmanNode:
    """Test cases for ContentCraftsmanNode."""

    @patch('src.pr_firm.nodes.__main__.call_llm')
    @patch('src.pr_firm.nodes.__main__.enforce_hashtag_placements')
    @patch('src.pr_firm.nodes.__main__.rewrite_with_constraints')
    def test_exec_generates_content_for_platforms(self, mock_rewrite, mock_hashtags, mock_call_llm):
        """Test exec method generates content for multiple platforms."""
        mock_call_llm.return_value = "Generated content"
        mock_hashtags.return_value = "Content with hashtags"
        mock_rewrite.return_value = "Rewritten content"

        prep = {
            "guidelines": {
                "twitter": {
                    "structure": ["intro", "body"],
                    "section_budgets": {"intro": 50, "body": 100}
                }
            },
            "persona": {"styles": {"voice": "clear"}, "axes": {}},
            "intents": {},
            "topic": "Test topic",
            "house_style": {},
            "llm": {"model": "test-model", "temperature": 0.7}
        }

        node = ContentCraftsmanNode()
        result = node.exec(prep)

        assert "twitter" in result
        assert "sections" in result["twitter"]
        assert "text" in result["twitter"]
        mock_call_llm.assert_called()

    def test_post_updates_content_pieces(self):
        """Test post method updates content pieces."""
        shared = {
            "content_pieces": {},
            "workflow_state": {"completed_stages": []}
        }

        node = ContentCraftsmanNode()
        exec_res = {"twitter": {"text": "Test content"}}

        result = node.post(shared, {}, exec_res)

        assert shared["content_pieces"]["twitter"]["text"] == "Test content"
        assert shared["workflow_state"]["current_stage"] == "style_editor"
        assert "content_craftsman" in shared["workflow_state"]["completed_stages"]
        assert result == "default"


class TestStyleComplianceNode:
    """Test cases for StyleComplianceNode."""

    @patch('src.pr_firm.nodes.__main__.check_style_violations')
    def test_exec_checks_violations(self, mock_check):
        """Test exec method checks for style violations."""
        mock_check.return_value = {"violations": ["error1"]}

        prep = {
            "content": {
                "twitter": {"text": "Test content"},
                "linkedin": {"text": "More content"}
            },
            "revision_count": 0
        }

        node = StyleComplianceNode()
        result = node.exec(prep)

        assert result["status"] == "revise"
        assert result["revision_count"] == 1
        assert "reports" in result

    @patch('src.pr_firm.nodes.__main__.check_style_violations')
    def test_exec_max_revisions(self, mock_check):
        """Test exec method handles max revisions."""
        mock_check.return_value = {"violations": ["error"]}

        prep = {
            "content": {"twitter": {"text": "Test"}},
            "revision_count": 4  # One less than max
        }

        node = StyleComplianceNode()
        result = node.exec(prep)

        assert result["status"] == "max_revisions"
        assert result["revision_count"] == 5

    def test_post_updates_workflow_state(self):
        """Test post method updates workflow state."""
        shared = {
            "style_compliance": {},
            "workflow_state": {},
            "stream": MagicMock()
        }

        node = StyleComplianceNode()
        exec_res = {
            "reports": {"twitter": {"violations": []}},
            "status": "pass",
            "revision_count": 1
        }

        result = node.post(shared, {}, exec_res)

        assert shared["workflow_state"]["revision_count"] == 1
        assert shared["workflow_state"]["current_stage"] == "fact_validator"
        assert result == "pass"


class TestEditCycleReportNode:
    """Test cases for EditCycleReportNode."""

    def test_exec_returns_report_text(self):
        """Test exec method returns report text."""
        node = EditCycleReportNode()
        result = node.exec("Test report")

        assert result == "Test report"

    def test_exec_returns_default_when_none(self):
        """Test exec method returns default when report is None."""
        node = EditCycleReportNode()
        result = node.exec(None)

        assert result == "No report available."

    def test_post_updates_final_campaign(self):
        """Test post method updates final campaign."""
        shared = {
            "final_campaign": {},
            "stream": MagicMock(),
            "workflow_state": {"completed_stages": []}
        }

        node = EditCycleReportNode()
        result = node.post(shared, None, "Final report")

        assert shared["final_campaign"]["edit_cycle_report"] == "Final report"
        assert shared["workflow_state"]["current_stage"] == "fact_validator"
        assert "edit_cycle_report" in shared["workflow_state"]["completed_stages"]
        assert result == "default"


class TestFactValidatorNode:
    """Test cases for FactValidatorNode."""

    @patch('src.pr_firm.nodes.__main__.call_llm')
    def test_exec_extracts_claims(self, mock_call_llm):
        """Test exec method extracts factual claims."""
        mock_call_llm.return_value = """
claims:
  - text: "Test claim"
    needs_source: true
"""

        prep = {
            "content": {
                "twitter": {"text": "This is a factual claim."}
            },
            "llm": {"model": "test-model", "temperature": 0.7}
        }

        node = FactValidatorNode()
        result = node.exec(prep)

        assert "twitter" in result
        mock_call_llm.assert_called_once()

    def test_post_updates_shared_store(self):
        """Test post method updates shared store."""
        shared = {
            "workflow_state": {"completed_stages": []}
        }

        node = FactValidatorNode()
        exec_res = {"validation": "results"}

        result = node.post(shared, {}, exec_res)

        assert shared["fact_validation"] == {"validation": "results"}
        assert shared["workflow_state"]["current_stage"] == "brand_guardian"
        assert "fact_validator" in shared["workflow_state"]["completed_stages"]
        assert result == "default"