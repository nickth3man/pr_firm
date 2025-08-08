from flow import create_pr_flow
from dotenv import load_dotenv

# Optional Gradio UI wrapper
try:
    import gradio as gr  # type: ignore
    HAS_GRADIO = True
except Exception:
    HAS_GRADIO = False

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


def launch_gradio():
    if not HAS_GRADIO:
        raise RuntimeError("Gradio is not installed. pip install gradio")

    # Ensure environment variables from .env are available in the Gradio UI flow
    # This is needed because calling launch_gradio() directly does not execute main().
    load_dotenv()

    def run_flow(platforms, topic, reddit_name, brand_xml):
        shared = {
            "task_requirements": {
                "platforms": [p.strip().lower() for p in (platforms or "").split(",") if p.strip()],
                "topic_or_goal": topic,
                "subreddit_name_or_title": reddit_name,
            },
            "brand_bible": {"xml_raw": brand_xml},
        }
        pr_flow = create_pr_flow()
        pr_flow.run(shared)
        # Collect milestones and final drafts
        stream = shared.get("stream")
        msgs = list(stream.messages()) if stream else []
        drafts = {k: v.get("text", "") for k, v in shared.get("content_pieces", {}).items()}
        return "\n".join([f"[{r}] {t}" for r, t, _ in msgs]), drafts

    with gr.Blocks() as demo:
        gr.Markdown("# PR Firm UI (minimal)")
        with gr.Row():
            platforms = gr.Textbox(label="Platforms (comma-separated)", value="email, linkedin")
            topic = gr.Textbox(label="Topic/Goal", value="Announce our new AI feature")
        with gr.Row():
            reddit = gr.Textbox(label="Subreddit (optional)")
        brand_xml = gr.Textbox(label="Brand Bible XML", lines=8, value="""
<brand>
  <brand_name>Acme</brand_name>
  <voice>clear</voice>
  <tone>warm</tone>
  <forbiddens><item>em_dash</item></forbiddens>
</brand>
""".strip())
        run_btn = gr.Button("Run")
        logs = gr.Textbox(label="Milestones", lines=10)
        drafts = gr.JSON(label="Drafts")
        run_btn.click(run_flow, inputs=[platforms, topic, reddit, brand_xml], outputs=[logs, drafts])

    demo.launch()

if __name__ == "__main__":
    main()
