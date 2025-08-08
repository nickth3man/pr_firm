from pocketflow import Flow
from pr_nodes import EngagementManagerNode, BrandBibleIngestNode, VoiceAlignmentNode, FormatGuidelinesNode


def create_pr_flow():
    # Nodes
    m = EngagementManagerNode()
    b = BrandBibleIngestNode()
    v = VoiceAlignmentNode()
    g = FormatGuidelinesNode()

    # Wire
    m >> b >> v >> g

    return Flow(start=m)
