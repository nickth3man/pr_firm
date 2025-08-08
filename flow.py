from pocketflow import Flow, BatchFlow
from nodes import (
    EngagementManagerNode,
    BrandBibleIngestNode,
    VoiceAlignmentNode,
    FormatGuidelinesRouter,
    EmailGuidelinesNode,
    InstagramGuidelinesNode,
    TwitterGuidelinesNode,
    RedditGuidelinesNode,
    LinkedInGuidelinesNode,
    BlogGuidelinesNode,
    ContentCraftsmanNode,
    StyleEditorNode,
    StyleComplianceNode,
    EditCycleReportNode,
    FactValidatorNode,
    BrandGuardianNode,
    AuthenticityAuditorNode,
    AgencyDirectorNode,
)

class FormatGuidelinesBatch(BatchFlow):
    def prep(self, shared):
        platforms = shared.get("task_requirements", {}).get("platforms", [])
        return [{"platform": p} for p in platforms]

    def post(self, shared, prep_res, exec_res):
        # Update workflow state after all platform guidelines are produced
        shared.setdefault("workflow_state", {})
        shared["workflow_state"]["current_stage"] = "content_craftsman"
        completed = shared["workflow_state"].setdefault("completed_stages", [])
        completed.append("guidelines")
        return "default"


def create_pr_flow():
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