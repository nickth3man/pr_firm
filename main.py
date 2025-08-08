from flow import create_pr_flow
from dotenv import load_dotenv

# Example main function
# Please replace this with your own main function
# PR Firm main function
def main():
    # Load environment variables from .env
    load_dotenv()

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
    if fc.get("publishing_schedule"):
        print("=== Schedule ===")
        for item in fc.get("publishing_schedule", []):
            print(f"- {item.get('platform')}: {item.get('day')} {item.get('time')}")
    if fc.get("performance_predictions"):
        print("=== Predictions ===")
        for plat, pred in fc.get("performance_predictions", {}).items():
            print(f"- {plat}: {pred.get('expected_engagement')} - {pred.get('notes','')}")
    if fc.get("edit_cycle_report"):
        print("=== Edit Cycle Report ===")
        print(fc["edit_cycle_report"]) 

if __name__ == "__main__":
    main()
