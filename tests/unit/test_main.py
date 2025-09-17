"""
Unit tests for main.py
"""

import pytest
from unittest.mock import patch, MagicMock, call
from src.pr_firm.main import main, launch_gradio


class TestMainFunction:
    """Test cases for main() function."""

    @patch('src.pr_firm.main.create_pr_flow')
    @patch('src.pr_firm.main.load_dotenv')
    def test_main_executes_flow(self, mock_load_dotenv, mock_create_flow):
        """Test that main() loads environment and runs the PR flow."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        main()

        # Verify environment loading
        mock_load_dotenv.assert_called_once()

        # Verify flow creation and execution
        mock_create_flow.assert_called_once()
        mock_flow.run.assert_called_once_with({})

    @patch('src.pr_firm.main.create_pr_flow')
    @patch('builtins.print')
    def test_main_prints_summary(self, mock_print, mock_create_flow):
        """Test that main() prints a summary of results."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        # Mock shared store with sample data
        mock_flow.run.side_effect = lambda shared: shared.update({
            "final_campaign": {
                "publishing_schedule": [
                    {"platform": "twitter", "day": "Monday", "time": "9:00 AM"}
                ],
                "performance_predictions": {
                    "twitter": {"expected_engagement": "High", "notes": "Good fit"}
                },
                "edit_cycle_report": "Report content"
            },
            "platform_guidelines": {"twitter": {}, "linkedin": {}},
            "content_pieces": {
                "twitter": {"text": "Short tweet content"},
                "linkedin": {"text": "Long linkedin post content that exceeds 160 characters and should be truncated in the summary output"}
            }
        })

        main()

        # Verify print calls were made
        assert mock_print.call_count > 0

        # Check specific print calls
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("=== Platforms ===" in call for call in calls)
        assert any("twitter" in call and "linkedin" in call for call in calls)

    @patch('src.pr_firm.main.create_pr_flow')
    @patch('builtins.print')
    def test_main_handles_empty_results(self, mock_print, mock_create_flow):
        """Test that main() handles empty results gracefully."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        main()

        # Should still make print calls even with empty results
        assert mock_print.call_count > 0


class TestLaunchGradioFunction:
    """Test cases for launch_gradio() function."""

    @patch('src.pr_firm.main.HAS_GRADIO', True)
    @patch('src.pr_firm.main.gr')
    @patch('src.pr_firm.main.load_dotenv')
    def test_launch_gradio_with_gradio_available(self, mock_load_dotenv, mock_gr):
        """Test launch_gradio() when Gradio is available."""
        mock_blocks = MagicMock()
        mock_demo = MagicMock()
        mock_gr.Blocks.return_value.__enter__ = mock_demo
        mock_gr.Blocks.return_value.__exit__ = MagicMock()

        launch_gradio()

        # Verify environment loading
        mock_load_dotenv.assert_called_once()

        # Verify Gradio components were created
        mock_gr.Blocks.assert_called_once()
        mock_gr.Markdown.assert_called()
        mock_gr.Textbox.assert_called()
        mock_gr.Button.assert_called()
        mock_demo.launch.assert_called_once()

    @patch('src.pr_firm.main.HAS_GRADIO', False)
    def test_launch_gradio_without_gradio_raises_error(self):
        """Test launch_gradio() raises error when Gradio is not available."""
        with pytest.raises(RuntimeError) as excinfo:
            launch_gradio()

        assert "Gradio is not installed" in str(excinfo.value)


class TestRunFlowFunction:
    """Test cases for the internal run_flow function."""

    @patch('src.pr_firm.main.create_pr_flow')
    def test_run_flow_creates_correct_shared_store(self, mock_create_flow):
        """Test that run_flow creates the correct shared store structure."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        # Mock stream
        mock_stream = MagicMock()
        mock_stream.messages.return_value = [("INFO", "Test message", None)]
        mock_flow.run.side_effect = lambda shared: shared.update({
            "stream": mock_stream,
            "content_pieces": {
                "twitter": {"text": "Test tweet"},
                "linkedin": {"text": "Test post"}
            }
        })

        logs, drafts = launch_gradio.__wrapped__(
            ["email", "linkedin"],
            "Test topic",
            "test_subreddit",
            "<brand></brand>"
        )

        # Verify the shared store was created correctly
        mock_flow.run.assert_called_once()
        call_args = mock_flow.run.call_args[0][0]  # Get the shared dict

        assert call_args["task_requirements"]["platforms"] == ["email", "linkedin"]
        assert call_args["task_requirements"]["topic_or_goal"] == "Test topic"
        assert call_args["task_requirements"]["subreddit_name_or_title"] == "test_subreddit"
        assert call_args["brand_bible"]["xml_raw"] == "<brand></brand>"

    @patch('src.pr_firm.main.create_pr_flow')
    def test_run_flow_handles_empty_inputs(self, mock_create_flow):
        """Test run_flow handles empty or None inputs."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        logs, drafts = launch_gradio.__wrapped__(
            "",
            "",
            None,
            ""
        )

        # Should handle empty inputs gracefully
        call_args = mock_flow.run.call_args[0][0]
        assert call_args["task_requirements"]["platforms"] == []
        assert call_args["task_requirements"]["topic_or_goal"] == ""
        assert call_args["task_requirements"]["subreddit_name_or_title"] is None
        assert call_args["brand_bible"]["xml_raw"] == ""

    @patch('src.pr_firm.main.create_pr_flow')
    def test_run_flow_returns_formatted_logs_and_drafts(self, mock_create_flow):
        """Test run_flow returns properly formatted logs and drafts."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        # Mock stream with messages
        mock_stream = MagicMock()
        mock_stream.messages.return_value = [
            ("INFO", "First milestone", None),
            ("SUCCESS", "Second milestone", None)
        ]

        mock_flow.run.side_effect = lambda shared: shared.update({
            "stream": mock_stream,
            "content_pieces": {
                "twitter": {"text": "Tweet content"},
                "linkedin": {"text": "LinkedIn post content"}
            }
        })

        logs, drafts = launch_gradio.__wrapped__(
            ["twitter", "linkedin"],
            "Test topic",
            None,
            "<brand></brand>"
        )

        # Verify logs format
        assert "[INFO] First milestone" in logs
        assert "[SUCCESS] Second milestone" in logs

        # Verify drafts format
        expected_drafts = {
            "twitter": "Tweet content",
            "linkedin": "LinkedIn post content"
        }
        assert drafts == expected_drafts

    @patch('src.pr_firm.main.create_pr_flow')
    def test_run_flow_handles_missing_stream(self, mock_create_flow):
        """Test run_flow handles cases where stream is None."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        mock_flow.run.side_effect = lambda shared: shared.update({
            "stream": None,
            "content_pieces": {"twitter": {"text": "Content"}}
        })

        logs, drafts = launch_gradio.__wrapped__(
            ["twitter"],
            "Test",
            None,
            "<brand></brand>"
        )

        # Should handle None stream gracefully
        assert logs == ""
        assert drafts == {"twitter": "Content"}


class TestMainModuleIntegration:
    """Integration tests for the main module."""

    def test_has_gradio_detection(self):
        """Test that HAS_GRADIO is properly set based on import success."""
        # This tests the module-level HAS_GRADIO variable
        from src.pr_firm import main as main_module

        # HAS_GRADIO should be a boolean
        assert isinstance(main_module.HAS_GRADIO, bool)

    @patch('src.pr_firm.main.create_pr_flow')
    def test_main_execution_flow(self, mock_create_flow):
        """Test the complete execution flow of main()."""
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow

        # Execute main
        main()

        # Verify the execution sequence
        mock_create_flow.assert_called_once()
        mock_flow.run.assert_called_once()

        # Verify shared store was passed
        call_args = mock_flow.run.call_args[0][0]
        assert isinstance(call_args, dict)

    def test_module_imports(self):
        """Test that all required modules can be imported."""
        # This is a smoke test for imports
        from src.pr_firm.main import main, launch_gradio

        assert callable(main)
        assert callable(launch_gradio)