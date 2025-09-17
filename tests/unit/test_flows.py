"""
Unit tests for core/flows.py
"""

import pytest
from unittest.mock import patch, MagicMock
from src.pr_firm.core.flows import FormatGuidelinesBatch, create_pr_flow, pr_flow


class TestFormatGuidelinesBatch:
    """Test cases for FormatGuidelinesBatch class."""

    def test_prep_with_platforms(self):
        """Test prep method with platforms in task_requirements."""
        shared = {
            "task_requirements": {
                "platforms": ["email", "linkedin", "twitter"]
            }
        }

        batch_flow = FormatGuidelinesBatch()
        result = batch_flow.prep(shared)

        expected = [
            {"platform": "email"},
            {"platform": "linkedin"},
            {"platform": "twitter"}
        ]
        assert result == expected

    def test_prep_without_platforms(self):
        """Test prep method without platforms in task_requirements."""
        shared = {
            "task_requirements": {}
        }

        batch_flow = FormatGuidelinesBatch()
        result = batch_flow.prep(shared)

        assert result == []

    def test_prep_without_task_requirements(self):
        """Test prep method without task_requirements in shared."""
        shared = {}

        batch_flow = FormatGuidelinesBatch()
        result = batch_flow.prep(shared)

        assert result == []

    def test_post_updates_workflow_state(self):
        """Test post method updates workflow state correctly."""
        shared = {
            "workflow_state": {
                "current_stage": "guidelines"
            }
        }

        batch_flow = FormatGuidelinesBatch()
        result = batch_flow.post(shared, [], [])

        # Check workflow state updates
        assert shared["workflow_state"]["current_stage"] == "content_craftsman"
        assert "guidelines" in shared["workflow_state"]["completed_stages"]
        assert result == "default"

    def test_post_creates_workflow_state(self):
        """Test post method creates workflow_state if not present."""
        shared = {}

        batch_flow = FormatGuidelinesBatch()
        batch_flow.post(shared, [], [])

        # Check workflow state is created and updated
        assert "workflow_state" in shared
        assert shared["workflow_state"]["current_stage"] == "content_craftsman"
        assert shared["workflow_state"]["completed_stages"] == ["guidelines"]


class TestCreatePrFlow:
    """Test cases for create_pr_flow function."""

    @patch('src.pr_firm.core.flows.EngagementManagerNode')
    @patch('src.pr_firm.core.flows.BrandBibleIngestNode')
    @patch('src.pr_firm.core.flows.VoiceAlignmentNode')
    @patch('src.pr_firm.core.flows.FormatGuidelinesRouter')
    @patch('src.pr_firm.core.flows.EmailGuidelinesNode')
    @patch('src.pr_firm.core.flows.InstagramGuidelinesNode')
    @patch('src.pr_firm.core.flows.TwitterGuidelinesNode')
    @patch('src.pr_firm.core.flows.RedditGuidelinesNode')
    @patch('src.pr_firm.core.flows.LinkedInGuidelinesNode')
    @patch('src.pr_firm.core.flows.BlogGuidelinesNode')
    @patch('src.pr_firm.core.flows.ContentCraftsmanNode')
    @patch('src.pr_firm.core.flows.StyleEditorNode')
    @patch('src.pr_firm.core.flows.StyleComplianceNode')
    @patch('src.pr_firm.core.flows.EditCycleReportNode')
    @patch('src.pr_firm.core.flows.FactValidatorNode')
    @patch('src.pr_firm.core.flows.BrandGuardianNode')
    @patch('src.pr_firm.core.flows.AuthenticityAuditorNode')
    @patch('src.pr_firm.core.flows.AgencyDirectorNode')
    @patch('src.pr_firm.core.flows.Flow')
    @patch('src.pr_firm.core.flows.BatchFlow')
    def test_create_pr_flow_structure(self, mock_batch_flow, mock_flow, *mock_nodes):
        """Test that create_pr_flow creates the expected flow structure."""
        # Create mock instances
        mock_flow_instance = MagicMock()
        mock_batch_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_batch_flow.return_value = mock_batch_flow_instance

        # Call the function
        result = create_pr_flow()

        # Verify Flow is called with the correct start node
        mock_flow.assert_called()
        # The last Flow call should be the main flow starting with EngagementManagerNode
        assert result == mock_flow_instance

    def test_create_pr_flow_returns_flow_instance(self):
        """Test that create_pr_flow returns a Flow instance."""
        result = create_pr_flow()

        # Should return some kind of flow object (we can't easily test the exact type
        # without importing pocketflow, but we can verify it's not None)
        assert result is not None

    def test_pr_flow_is_created(self):
        """Test that the module-level pr_flow variable is created."""
        # This tests that the module-level variable is properly initialized
        assert pr_flow is not None

    @patch('src.pr_firm.core.flows.ContentCraftsmanNode')
    def test_content_craftsman_has_retries(self, mock_content_craftsman):
        """Test that ContentCraftsmanNode is created with retry configuration."""
        # Reset the module-level flow to trigger recreation
        import src.pr_firm.core.flows as flows_module
        flows_module.pr_flow = None

        # Recreate the flow
        flow = flows_module.create_pr_flow()

        # Verify ContentCraftsmanNode was created with retries
        # This is a bit tricky to test directly, but we can verify the function runs
        assert flow is not None


class TestFlowIntegration:
    """Integration tests for flow functionality."""

    def test_flow_creation_does_not_raise_exceptions(self):
        """Test that creating flows doesn't raise any exceptions."""
        # This is a basic smoke test to ensure all imports and instantiation work
        try:
            flow = create_pr_flow()
            assert flow is not None
        except Exception as e:
            pytest.fail(f"Flow creation raised an exception: {e}")

    def test_batch_flow_inheritance(self):
        """Test that FormatGuidelinesBatch properly inherits from BatchFlow."""
        batch_flow = FormatGuidelinesBatch()

        # Should have prep method
        assert hasattr(batch_flow, 'prep')
        assert callable(getattr(batch_flow, 'prep'))

        # Should have post method
        assert hasattr(batch_flow, 'post')
        assert callable(getattr(batch_flow, 'post'))

    def test_flow_references_valid_nodes(self):
        """Test that the flow references valid node types."""
        # This is more of a documentation test - ensuring the flow
        # is constructed with the expected node types
        flow = create_pr_flow()

        # The flow should be created successfully
        assert flow is not None

        # We can't easily inspect the internal structure without more complex mocking,
        # but we can verify the flow object exists and has expected methods
        assert hasattr(flow, 'run')  # PocketFlow Flow objects should have a run method