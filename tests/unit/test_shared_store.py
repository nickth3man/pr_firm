"""
Unit tests for core/shared_store.py
"""

import pytest
from unittest.mock import patch, MagicMock
from src.pr_firm.core.shared_store import initialize_shared_store


class TestInitializeSharedStore:
    """Test cases for initialize_shared_store function."""

    def test_initialize_empty_shared_store(self):
        """Test initializing an empty shared store."""
        shared = {}

        initialize_shared_store(shared)

        # Check that all expected keys are present
        expected_keys = [
            "config", "task_requirements", "brand_bible", "house_style",
            "reddit", "platform_nuance", "platform_guidelines",
            "content_pieces", "style_compliance", "workflow_state",
            "final_campaign", "stream", "llm"
        ]

        for key in expected_keys:
            assert key in shared, f"Expected key '{key}' not found in shared store"

    def test_initialize_preserves_existing_data(self):
        """Test that existing data in shared store is preserved."""
        shared = {
            "existing_key": "existing_value",
            "config": {"custom_config": True}
        }

        initialize_shared_store(shared)

        # Existing data should be preserved
        assert shared["existing_key"] == "existing_value"
        assert shared["config"]["custom_config"] is True
        # But new defaults should be added
        assert "task_requirements" in shared

    def test_config_defaults(self):
        """Test that config is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        assert shared["config"]["style_policy"] == "strict"

    def test_task_requirements_defaults(self):
        """Test that task_requirements is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        tr = shared["task_requirements"]
        assert tr["platforms"] == ["email", "linkedin"]
        assert tr["topic_or_goal"] == "Announce our new AI feature"
        assert tr["urgency_level"] == "normal"
        assert "intents_by_platform" in tr

    def test_brand_bible_defaults(self):
        """Test that brand_bible is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        bb = shared["brand_bible"]
        assert "xml_raw" in bb
        assert "<brand>" in bb["xml_raw"]
        assert "<brand_name>Acme</brand_name>" in bb["xml_raw"]

    def test_house_style_defaults(self):
        """Test that house_style is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        hs = shared["house_style"]
        assert "email_signature" in hs
        assert "blog_style" in hs
        assert hs["email_signature"]["content"] == "Best,\nAcme Team"

    def test_reddit_defaults(self):
        """Test that reddit structure is initialized correctly."""
        shared = {}
        initialize_shared_store(shared)

        reddit = shared["reddit"]
        assert reddit["rules_text"] is None
        assert reddit["description_text"] is None

    def test_platform_nuance_defaults(self):
        """Test that platform_nuance is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        pn = shared["platform_nuance"]
        assert "linkedin" in pn
        assert "twitter" in pn
        assert "instagram" in pn
        assert "reddit" in pn
        assert "email" in pn
        assert "blog" in pn

        # Check specific values
        assert pn["linkedin"]["whitespace_density"] == "high"
        assert pn["twitter"]["thread_ok_above_chars"] == 240
        assert isinstance(pn["twitter"]["hashtag_count_range"], list)

    def test_workflow_state_defaults(self):
        """Test that workflow_state is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        ws = shared["workflow_state"]
        assert ws["current_stage"] == "engagement"
        assert ws["completed_stages"] == []
        assert ws["revision_count"] == 0
        assert ws["manual_review_required"] is False

    def test_final_campaign_defaults(self):
        """Test that final_campaign is initialized with correct defaults."""
        shared = {}
        initialize_shared_store(shared)

        fc = shared["final_campaign"]
        assert "approved_content" in fc
        assert "publishing_schedule" in fc
        assert "performance_predictions" in fc
        assert fc["edit_cycle_report"] is None

    def test_stream_initialization(self):
        """Test that stream is properly initialized."""
        shared = {}
        initialize_shared_store(shared)

        # Stream should be initialized
        assert "stream" in shared
        assert shared["stream"] is not None

    def test_llm_defaults(self):
        """Test that llm configuration is initialized correctly."""
        shared = {}
        initialize_shared_store(shared)

        llm = shared["llm"]
        assert llm["model"] == "anthropic/claude-3.5-sonnet"
        assert llm["temperature"] == 0.7

    @patch('src.pr_firm.core.shared_store.get_preset')
    def test_brand_bible_preset_loading(self, mock_get_preset):
        """Test loading brand bible from preset."""
        mock_get_preset.return_value = {"xml_raw": "<preset_brand></preset_brand>"}

        shared = {
            "brand_bible": {
                "preset_name": "test_preset"
            }
        }

        initialize_shared_store(shared)

        # Should have loaded preset
        assert shared["brand_bible"]["xml_raw"] == "<preset_brand></preset_brand>"
        mock_get_preset.assert_called_with("brand_bibles", "test_preset")

    @patch('src.pr_firm.core.shared_store.get_preset')
    def test_brand_bible_preset_save(self, mock_get_preset):
        """Test saving brand bible as preset."""
        shared = {
            "brand_bible": {
                "save_as_preset": True,
                "preset_name": "test_preset",
                "xml_raw": "<brand></brand>"
            }
        }

        with patch('src.pr_firm.core.shared_store.save_preset') as mock_save:
            initialize_shared_store(shared)

            mock_save.assert_called_with("brand_bibles", "test_preset", {"xml_raw": "<brand></brand>"})

    @patch('src.pr_firm.core.shared_store.get_preset')
    def test_email_signature_preset_loading(self, mock_get_preset):
        """Test loading email signature from preset."""
        mock_get_preset.return_value = {"content": "Custom signature"}

        shared = {
            "house_style": {
                "email_signature": {
                    "name": "test_sig"
                }
            }
        }

        initialize_shared_store(shared)

        assert shared["house_style"]["email_signature"]["content"] == "Custom signature"

    @patch('src.pr_firm.core.shared_store.get_preset')
    def test_blog_style_preset_loading(self, mock_get_preset):
        """Test loading blog style from preset."""
        mock_get_preset.return_value = {"content": '{"custom": "style"}'}

        shared = {
            "house_style": {
                "blog_style": {
                    "name": "test_style"
                }
            }
        }

        initialize_shared_store(shared)

        assert shared["house_style"]["blog_style"]["content"] == '{"custom": "style"}'

    @patch('src.pr_firm.core.shared_store.normalize_subreddit')
    def test_subreddit_normalization(self, mock_normalize):
        """Test that subreddit name is normalized."""
        mock_normalize.return_value = "normalized_name"

        shared = {
            "task_requirements": {
                "subreddit_name_or_title": "raw_name"
            }
        }

        initialize_shared_store(shared)

        mock_normalize.assert_called_with("raw_name")
        assert shared["task_requirements"]["subreddit_name_or_title"] == "normalized_name"

    def test_no_subreddit_normalization_when_none(self):
        """Test that subreddit normalization is skipped when None."""
        shared = {
            "task_requirements": {
                "subreddit_name_or_title": None
            }
        }

        with patch('src.pr_firm.core.shared_store.normalize_subreddit') as mock_normalize:
            initialize_shared_store(shared)

            mock_normalize.assert_not_called()

    def test_no_subreddit_normalization_when_missing(self):
        """Test that subreddit normalization is skipped when key is missing."""
        shared = {
            "task_requirements": {}
        }

        with patch('src.pr_firm.core.shared_store.normalize_subreddit') as mock_normalize:
            initialize_shared_store(shared)

            mock_normalize.assert_not_called()


class TestSharedStoreIntegration:
    """Integration tests for shared store functionality."""

    def test_full_initialization_workflow(self):
        """Test the complete shared store initialization workflow."""
        shared = {}

        # This should not raise any exceptions
        initialize_shared_store(shared)

        # Verify all expected structures are present
        assert len(shared) > 10  # Should have many keys

        # Verify nested structures
        assert isinstance(shared["platform_nuance"], dict)
        assert isinstance(shared["workflow_state"], dict)
        assert isinstance(shared["final_campaign"], dict)

    def test_initialization_idempotent(self):
        """Test that multiple initializations don't break anything."""
        shared = {}

        # Initialize multiple times
        initialize_shared_store(shared)
        initialize_shared_store(shared)
        initialize_shared_store(shared)

        # Should still be valid
        assert "config" in shared
        assert "task_requirements" in shared

    def test_partial_existing_data_preservation(self):
        """Test that partial existing data is properly merged."""
        shared = {
            "config": {"existing_setting": True},
            "task_requirements": {"existing_platform": ["custom"]}
        }

        initialize_shared_store(shared)

        # Existing data should be preserved
        assert shared["config"]["existing_setting"] is True
        assert "custom" in shared["task_requirements"]["existing_platform"]

        # Defaults should still be added for missing keys
        assert shared["config"]["style_policy"] == "strict"
        assert "platforms" in shared["task_requirements"]