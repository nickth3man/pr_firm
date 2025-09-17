from pocketflow import Node
from typing import Dict, Any, List, Optional, Union
import json
import re
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

from pr_firm.utils.content.format_platform import build_guidelines
from pr_firm.utils.content.rewrite_with_constraints import rewrite_with_constraints
from pr_firm.utils.helpers.check_style_violations import check_style_violations
from pr_firm.utils.content.report_builder import build_report
from pr_firm.utils.llm.call_llm import call_llm
from pr_firm.utils.helpers.progress import progress_for_stage
from pr_firm.core.shared_store import initialize_shared_store


def calculate_section_budgets(guidelines: Dict[str, Any]) -> Dict[str, int]:
    """Calculate character budgets for each content section based on platform guidelines.

    This helper function determines how many characters should be allocated to each
    content section (e.g., introduction, body, conclusion) based on the platform's
    total character limits and section structure.

    Args:
        guidelines: Platform guidelines dictionary containing structure and limits

    Returns:
        Dictionary mapping section names to their character budgets
    """
    structure: List[str] = guidelines.get("structure", [])
    if not structure:
        return {}
    # Prefer explicit section_budgets; else derive from char limits or approx_chars
    explicit = guidelines.get("section_budgets") or {}
    if isinstance(explicit, dict) and explicit:
        return {s: int(explicit.get(s, 120)) for s in structure}
    limits = guidelines.get("limits", {})
    total_chars = (
        limits.get("chars")
        or limits.get("body")
        or limits.get("approx_chars")
        or 800
    )
    per = max(40, int(total_chars / max(1, len(structure))))
    return {s: per for s in structure}


def enforce_hashtag_placements(text: str, g: Dict[str, Any], platform: str) -> str:
    """Enforce platform-specific hashtag placement and count rules.

    This helper function applies different hashtag strategies based on platform:
    - Instagram/LinkedIn: Move all hashtags to end of content
    - Twitter/X: Allow 1-3 hashtags inline, move extras to end
    - Reddit/Email/Blog: Remove all hashtags

    Args:
        text: The content text to process
        g: Platform guidelines dictionary containing hashtag rules
        platform: The target platform name

    Returns:
        Processed text with hashtags positioned according to platform rules
    """
    hashtags = g.get("hashtags")
    # Normalize whitespace first
    out = re.sub(r"[ \t]+\n", "\n", text).strip()
    out = re.sub(r"\n{3,}", "\n\n", out)
    if isinstance(hashtags, dict):
        count = int(hashtags.get("count", 0) or 0)
        placement = hashtags.get("placement")
        tags = re.findall(r"#\w+", out)
        if tags:
            if platform in ("instagram", "linkedin") and placement == "end":
                out_wo = re.sub(r"\s*#\w+", "", out).strip()
                end_tags = " ".join(tags[-count or len(tags):]) if count else " ".join(tags)
                out = out_wo.rstrip() + "\n" + end_tags
            elif platform in ("twitter", "x"):
                # Allow 1–3 inline kept, move extras to end
                keep = min(max(count or 2, 1), 3)
                if len(tags) > keep:
                    out_wo = re.sub(r"\s*#\w+", "", out).strip()
                    inline = " ".join(tags[:keep])
                    end = " ".join(tags[keep:])
                    out = f"{inline} {out_wo}\n{end}".strip()
            else:
                # Reddit/Email/Blog: remove hashtags entirely
                out = re.sub(r"\s*#\w+", "", out).strip()
    return out




class FormatGuidelinesRouter(Node):
    """Router node used inside BatchFlow to dispatch to per-platform nodes via action."""
    def prep(self, shared: Dict[str, Any]) -> None:
        return None

    def post(self, shared: Dict[str, Any], prep_res: None, exec_res: Any) -> str:
        platform = self.params.get("platform", "").lower()
        # Action name equals platform string
        return platform or "default"


class _BaseGuidelinesNode(Node):
    platform_name: str = ""

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        persona = shared.get("brand_bible", {}).get("persona_voice", {})
        intents = shared.get("task_requirements", {}).get("intents_by_platform", {})
        platform_nuance = shared.get("platform_nuance", {}).get(self.platform_name, {})
        reddit_block = shared.get("reddit", {}) if self.platform_name == "reddit" else None
        intent_val = intents.get(self.platform_name, {}).get("value", "general") if isinstance(intents.get(self.platform_name), dict) else intents.get(self.platform_name, "general")
        return {
            "persona": persona,
            "intent": intent_val,
            "nuance": platform_nuance,
            "reddit": reddit_block,
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        return build_guidelines(self.platform_name, prep["persona"], prep["intent"], platform_nuance=prep.get("nuance"), reddit=prep.get("reddit"))

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        shared.setdefault("platform_guidelines", {})
        shared["platform_guidelines"][self.platform_name] = exec_res
        return "default"


class EmailGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "email"


class InstagramGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "instagram"


class TwitterGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "twitter"


class RedditGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "reddit"


class LinkedInGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "linkedin"


class BlogGuidelinesNode(_BaseGuidelinesNode):
    platform_name = "blog"


class ContentCraftsmanNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "guidelines": shared.get("platform_guidelines", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "intents": shared.get("task_requirements", {}).get("intents_by_platform", {}),
            "topic": shared.get("task_requirements", {}).get("topic_or_goal", ""),
            "house_style": shared.get("house_style", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        topic = prep["topic"]
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)

        for platform, g in prep["guidelines"].items():
            sections: Dict[str, str] = {}
            parts: List[str] = []
            budgets = calculate_section_budgets(g)
            for sec in g.get("structure", []):
                budget = budgets.get(sec, 120)
                prompt = (
                    f"Platform: {platform}\n"
                    f"Section: {sec}\n"
                    f"Topic/Goal: {topic}\n"
                    f"Voice: {prep['persona'].get('styles',{}).get('voice','clear')} | Axes: {json.dumps(prep['persona'].get('axes',{}))}\n"
                    f"Guidelines: {json.dumps(g)}\n"
                    f"Constraints: No em dash; no rhetorical contrasts; respect structure; keep within ~{budget} chars."
                )
                messages = [
                    {"role": "system", "content": "You write concise, on-brand marketing copy that strictly follows constraints."},
                    {"role": "user", "content": prompt},
                ]
                sec_text = call_llm(messages, model=model, temperature=temperature)
                sections[sec] = sec_text.strip()
                parts.append(sec_text.strip())

            text = "\n".join(parts)
            text = enforce_hashtag_placements(text, g, platform)
            # Final pass to remove forbidden patterns
            text = rewrite_with_constraints(text, prep["persona"], g)
            out[platform] = {"sections": sections, "text": text}
        return out

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        # Store the generated content pieces in shared store
        shared["content_pieces"].update(exec_res)
        # No streaming here per policy; drafts available in shared when complete
        shared["workflow_state"]["current_stage"] = "style_editor"
        shared["workflow_state"]["completed_stages"].append("content_craftsman")
        return "default"


class StyleEditorNode(Node):
    """Node responsible for editing content to remove AI fingerprints."""

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for style editing.

        Args:
            shared: The shared store containing workflow state

        Returns:
            Dictionary with content, persona, guidelines, and LLM config
        """
        return {
            "content": shared.get("content_pieces", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "guidelines": shared.get("platform_guidelines", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        """Execute style editing on content pieces.

        Args:
            prep: Prepared data from prep method

        Returns:
            Dictionary of edited content pieces
        """
        edited: Dict[str, Any] = {}
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)
        for p, piece in prep["content"].items():
            g = prep["guidelines"].get(p, {})
            base_text = piece.get("text", "")
            attempt = 0
            final_text = base_text
            while attempt < 2:
                prompt = (
                    "Rewrite the text to remove AI fingerprints (stiff transitions, "
                    "predictable lists, tidy wrap-ups, monotone rhythm, platitudes). "
                    "Do not change meaning or structure. Do not introduce em dashes "
                    "or rhetorical contrasts.\n\n"
                    f"Voice: {prep['persona'].get('styles',{}).get('voice','clear')} | "
                    f"Axes: {json.dumps(prep['persona'].get('axes',{}))}\n"
                    f"Guidelines: {json.dumps(g)}\n\n"
                    f"Text:\n{final_text}"
                )
                messages = [
                    {"role": "system", "content": "You are a precise marketing editor."},
                    {"role": "user", "content": prompt},
                ]
                candidate = call_llm(messages, model=model, temperature=temperature).strip()
                candidate = rewrite_with_constraints(candidate, prep["persona"], g)
                res = check_style_violations(candidate)
                if not res.get("violations"):
                    final_text = candidate
                    break
                final_text = candidate
                attempt += 1
            edited[p] = {"sections": piece.get("sections", {}), "text": final_text}
        return edited

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Post-process and update workflow state after style editing.

        Args:
            shared: The shared store
            prep_res: Result from prep method
            exec_res: Result from exec method

        Returns:
            Action string for flow control
        """
        shared["content_pieces"].update(exec_res)
        shared["workflow_state"]["current_stage"] = "style_compliance"
        shared["workflow_state"]["completed_stages"].append("style_editor")
        return "default"


class StyleComplianceNode(Node):
    """Node responsible for checking style compliance and managing revision cycles."""

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for style compliance checking.

        Args:
            shared: The shared store containing workflow state

        Returns:
            Dictionary with content pieces and revision count
        """
        return {
            "content": shared.get("content_pieces", {}),
            "revision_count": shared.get("workflow_state", {}).get("revision_count", 0),
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        """Execute style violation checking on all content pieces.

        Args:
            prep: Prepared data from prep method

        Returns:
            Dictionary with reports, status, and updated revision count
        """
        reports = {}
        any_viol = False
        for p, piece in prep["content"].items():
            res = check_style_violations(piece.get("text", ""))
            reports[p] = res
            if res.get("violations"):
                any_viol = True
        status = "pass"
        new_rev = prep["revision_count"]
        if any_viol:
            new_rev += 1
            status = "revise" if new_rev < 5 else "max_revisions"
        return {"reports": reports, "status": status, "revision_count": new_rev}

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Post-process compliance results and update workflow state.

        Args:
            shared: The shared store
            prep_res: Result from prep method
            exec_res: Result from exec method

        Returns:
            Action string for flow control ("pass", "revise", or "max_revisions")
        """
        shared["style_compliance"] = exec_res["reports"]
        shared["workflow_state"]["revision_count"] = exec_res["revision_count"]
        pct, _msg = progress_for_stage(min(exec_res["revision_count"], 5), 5)
        shared["stream"].emit("milestone",
                              f"Style check {exec_res['revision_count']}/5 ({pct}%): {exec_res['status']}")
        action = exec_res["status"]  # "pass" | "revise" | "max_revisions"
        if action == "max_revisions":
            # Build a concise report for the upcoming EditCycleReportNode
            histories = [{"violations": v.get("violations", [])} for v in exec_res["reports"].values()]
            any_p = next(iter(shared.get("content_pieces", {}).keys()), None)
            last_text = shared.get("content_pieces", {}).get(any_p, {}).get("text", "") if any_p else ""
            shared.setdefault("final_campaign", {})
            shared["final_campaign"]["edit_cycle_report"] = build_report(histories, last_text, any_p or "n/a")
            shared["workflow_state"]["manual_review_required"] = True
            shared["workflow_state"]["current_stage"] = "edit_cycle_report"
        elif action == "revise":
            shared["workflow_state"]["current_stage"] = "style_editor"
        else:
            shared["workflow_state"]["current_stage"] = "fact_validator"
        shared["workflow_state"]["completed_stages"].append("style_compliance")
        return action


class EditCycleReportNode(Node):
    def prep(self, shared):
        return shared.get("final_campaign", {}).get("edit_cycle_report")

    def exec(self, report_text):
        return report_text or "No report available."

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("final_campaign", {})
        shared["final_campaign"]["edit_cycle_report"] = exec_res
        shared["stream"].emit("milestone", "Max revisions reached. Report generated.")
        shared["workflow_state"]["current_stage"] = "fact_validator"
        shared["workflow_state"]["completed_stages"].append("edit_cycle_report")
        return "default"


class FactValidatorNode(Node):
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
        # LLM-based extraction of claims needing sources
        content_pieces = prep.get("content", {})
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)
        results: Dict[str, Any] = {}
        for platform, piece in content_pieces.items():
            text = (piece or {}).get("text", "")
            prompt = (
                "Extract factual claims and whether each needs a source. Respond in YAML with:\n"
                "claims:\n  - text: <claim>\n    needs_source: true|false\n"
            )
            messages = [
                {"role": "system", "content": "You analyze text and identify claims that require citations."},
                {"role": "user", "content": f"Text:\n{text}\n\n{prompt}"},
            ]
            resp = call_llm(messages, model=model, temperature=temperature)
            claims = []
            if yaml:
                try:
                    y = yaml.safe_load(resp)
                    claims = (y or {}).get("claims", []) if isinstance(y, dict) else []
                except Exception:
                    claims = []
            results[platform] = {"claims_needing_source": claims}
        return results

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("final_campaign", {})
        shared["final_campaign"]["fact_validation"] = exec_res
        shared["workflow_state"]["current_stage"] = "brand_guardian"
        shared["workflow_state"]["completed_stages"].append("fact_validator")
        return "default"


class BrandGuardianNode(Node):
    """Node responsible for evaluating brand alignment of content."""

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for brand alignment evaluation.

        Args:
            shared: The shared store containing workflow state

        Returns:
            Dictionary with content, persona, and LLM config
        """
        return {
            "content": shared.get("content_pieces", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep: Dict[str, Any]) -> Dict[str, Any]:
        """Execute brand alignment scoring for all content pieces.

        Args:
            prep: Prepared data from prep method

        Returns:
            Dictionary of alignment scores and suggestions per platform
        """
        content_pieces = prep.get("content", {})
        persona = prep.get("persona", {})
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)
        scores: Dict[str, Any] = {}
        for platform, piece in content_pieces.items():
            text = (piece or {}).get("text", "")
            prompt = (
                "Score brand alignment from 0.0 to 1.0 and provide 2-3 micro-edit suggestions."
                " Respond in YAML as:\nalignment_score: <float>\nsuggestions:\n  - <text>\n"
                f"Persona: {json.dumps(persona)}\nText:\n{text}"
            )
            messages = [
                {"role": "system", "content": "You are a brand guardian evaluating alignment."},
                {"role": "user", "content": prompt},
            ]
            resp = call_llm(messages, model=model, temperature=temperature)
            alignment_score = 0.75
            suggestions: List[str] = []
            if yaml:
                try:
                    y = yaml.safe_load(resp)
                    if isinstance(y, dict):
                        alignment_score = float(y.get("alignment_score", alignment_score))
                        suggestions = y.get("suggestions", suggestions)
                except Exception:
                    pass
            scores[platform] = {"alignment_score": max(0.0, min(1.0, alignment_score)), "suggestions": suggestions}
        return scores

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Post-process alignment results and update workflow state.

        Args:
            shared: The shared store
            prep_res: Result from prep method
            exec_res: Result from exec method

        Returns:
            Action string for flow control
        """
        shared.setdefault("final_campaign", {})
        shared["final_campaign"]["brand_alignment"] = exec_res
        shared["workflow_state"]["current_stage"] = "authenticity_auditor"
        shared["workflow_state"]["completed_stages"].append("brand_guardian")
        return "default"


class AuthenticityAuditorNode(Node):
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
        content_pieces = prep.get("content", {})
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)
        warnings: Dict[str, Any] = {}
        for platform, piece in content_pieces.items():
            text = (piece or {}).get("text", "")
            prompt = (
                "Evaluate authenticity and flag hype/over-claiming. Respond in YAML as:\n"
                "hype_flags:\n  - <term>\nsuggestions:\n  - <actionable suggestion>\n"
                f"Text:\n{text}"
            )
            messages = [
                {"role": "system", "content": "You are an authenticity auditor."},
                {"role": "user", "content": prompt},
            ]
            resp = call_llm(messages, model=model, temperature=temperature)
            hype_flags: List[str] = []
            suggestions: List[str] = []
            if yaml:
                try:
                    y = yaml.safe_load(resp)
                    if isinstance(y, dict):
                        hype_flags = y.get("hype_flags", []) or []
                        suggestions = y.get("suggestions", []) or []
                except Exception:
                    pass
            warnings[platform] = {"hype_flags": hype_flags, "suggestions": suggestions}
        return warnings

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("final_campaign", {})
        shared["final_campaign"]["authenticity"] = exec_res
        shared["workflow_state"]["current_stage"] = "agency_director"
        shared["workflow_state"]["completed_stages"].append("authenticity_auditor")
        return "default"


class AgencyDirectorNode(Node):
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "guidelines": shared.get("platform_guidelines", {}),
            "report": shared.get("final_campaign", {}).get("edit_cycle_report"),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
        # Build publishing schedule and performance predictions via LLM
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)
        plan_prompt = (
            "Given the platform drafts, propose a simple 7-day publishing schedule (date placeholders OK) and predict relative performance."
            " Respond in YAML as:\n"
            "schedule:\n  - platform: <platform>\n    day: <Mon..Sun>\n    time: <HH:MM>\n"
            "predictions:\n  <platform>:\n    expected_engagement: <low|medium|high>\n    notes: <text>\n"
        )
        messages = [
            {"role": "system", "content": "You are an experienced content operations planner."},
            {"role": "user", "content": plan_prompt + "\nPlatforms:" + ", ".join(list(prep.get("content", {}).keys()))},
        ]
        resp = call_llm(messages, model=model, temperature=temperature)
        schedule: List[Dict[str, Any]] = []
        predictions: Dict[str, Any] = {}
        if yaml:
            try:
                y = yaml.safe_load(resp)
                if isinstance(y, dict):
                    schedule = y.get("schedule", []) or []
                    predictions = y.get("predictions", {}) or {}
            except Exception:
                pass
        # Package deliverables
        return {
            "approved_content": prep["content"],
            "guidelines": prep["guidelines"],
            "edit_cycle_report": prep["report"],
            "publishing_schedule": schedule,
            "performance_predictions": predictions,
        }

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("final_campaign", {})
        shared["final_campaign"].update(exec_res)
        shared["stream"].emit("milestone", "Packaging complete")
        shared["workflow_state"]["current_stage"] = "done"
        shared["workflow_state"]["completed_stages"].append("agency_director")
        return "default"