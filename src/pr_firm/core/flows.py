"""Flow definitions and orchestration for PR Firm."""

from typing import Dict, Any, List

from pocketflow import Flow, BatchFlow

from pr_firm.nodes.engagement.manager import EngagementManagerNode
from pr_firm.nodes.brand.ingest import BrandBibleIngestNode
from pr_firm.nodes.brand.voice import VoiceAlignmentNode
from pr_firm.nodes.__main__ import (
    AgencyDirectorNode,
    AuthenticityAuditorNode,
    BlogGuidelinesNode,
    BrandGuardianNode,
    ContentCraftsmanNode,
    EditCycleReportNode,
    EmailGuidelinesNode,
    FactValidatorNode,
    FormatGuidelinesRouter,
    InstagramGuidelinesNode,
    LinkedInGuidelinesNode,
    RedditGuidelinesNode,
    StyleComplianceNode,
    StyleEditorNode,
    TwitterGuidelinesNode,
)


class FormatGuidelinesBatch(BatchFlow):
    """Batch flow for generating platform guidelines in parallel."""

    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare platform list for batch processing.

        Args:
            shared: The shared store containing workflow state

        Returns:
            List of platform parameter dictionaries
        """
        platforms = shared.get("task_requirements", {}).get("platforms", [])
        return [{"platform": p} for p in platforms]

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res_list: Any) -> str:
        """Post-process after all guidelines are generated.

        Args:
            shared: The shared store
            prep_res: Result from prep method
            exec_res_list: List of execution results

        Returns:
            Action string for flow control
        """
        # Update workflow state after all platform guidelines are produced
        shared.setdefault("workflow_state", {})
        shared["workflow_state"]["current_stage"] = "content_craftsman"
        completed = shared["workflow_state"].setdefault("completed_stages", [])
        completed.append("guidelines")
        return "default"


def create_pr_flow() -> Any:
    """Create and return the PR Firm flow."""
    # Nodes
    m = EngagementManagerNode()
    b = BrandBibleIngestNode()
    v = VoiceAlignmentNode()
    # Build guidelines sub-flow with per-platform router
    router = FormatGuidelinesRouter()
    g_email = EmailGuidelinesNode()
    g_ig = InstagramGuidelinesNode()
    g_tw = TwitterGuidelinesNode()
    g_rd = RedditGuidelinesNode()
    g_li = LinkedInGuidelinesNode()
    g_bg = BlogGuidelinesNode()

    # Route based on action equal to platform param
    router - "email" >> g_email
    router - "instagram" >> g_ig
    router - "twitter" >> g_tw
    router - "x" >> g_tw
    router - "reddit" >> g_rd
    router - "linkedin" >> g_li
    router - "blog" >> g_bg

    guidelines_flow = Flow(start=router)
    g = FormatGuidelinesBatch(start=guidelines_flow)

    # LLM-heavy nodes with retries
    c = ContentCraftsmanNode(max_retries=2, wait=5)
    e = StyleEditorNode(max_retries=2, wait=5)
    s = StyleComplianceNode()
    r = EditCycleReportNode()
    fv = FactValidatorNode()
    bg = BrandGuardianNode()
    aa = AuthenticityAuditorNode()
    d = AgencyDirectorNode()

    # Wire core linear path
    m >> b >> v >> g >> c >> e >> s
    # Style loop and branching
    s - "revise" >> e
    s - "max_revisions" >> r
    s - "pass" >> fv
    # After report, continue to validators
    r >> fv
    # Validation sequence
    fv >> bg >> aa >> d

    # Start
    return Flow(start=m)

pr_flow = create_pr_flow()