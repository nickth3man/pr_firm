from flow import create_qa_flow

# Example main function
# Please replace this with your own main function
from pr_flow import create_pr_flow

# PR Firm main function
def main():
    # Minimal shared store; EngagementManagerNode seeds defaults
    shared = {}

    pr_flow = create_pr_flow()
    pr_flow.run(shared)

    # Print concise summary
    fc = shared.get("final_campaign", {})
    guidelines = shared.get("platform_guidelines", {})
    content = shared.get("content_pieces", {})
    print("=== Platforms ===")
    print(", ".join(guidelines.keys()) or "None")
    print("=== Drafts ===")
    for p, piece in content.items():
        txt = (piece.get("text") or "")[:160]
        print(f"- {p}: {txt}{'...' if len(piece.get('text',''))>160 else ''}")
    if fc.get("edit_cycle_report"):
        print("=== Edit Cycle Report ===")
        print(fc["edit_cycle_report"]) 

if __name__ == "__main__":
    main()
