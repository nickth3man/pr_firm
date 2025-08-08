from pocketflow import Node
from typing import Dict, Any, List
import json
import re
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

from utils.streaming import Stream
from utils.brand_bible_parser import parse as parse_brand_bible
from utils.brand_voice_mapper import brand_bible_to_voice
from utils.format_platform import build_guidelines
from utils.rewrite_with_constraints import rewrite_with_constraints
from utils.check_style_violations import check_style_violations
from utils.report_builder import build_report
from utils.call_llm import call_llm
from utils.presets import get_preset, save_preset
from utils.input_normalize import normalize_subreddit
from utils.progress import progress_for_stage

class EngagementManagerNode(Node):
    def prep(self, shared):
        return {
            "task_requirements": shared.get("task_requirements", {}),
            "brand_bible": shared.get("brand_bible", {}),
            "house_style": shared.get("house_style", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
        # Propose auto-intents if any platform marked as type "auto"
        intents_by_platform = dict(prep.get("task_requirements", {}).get("intents_by_platform", {}))
        platforms = prep.get("task_requirements", {}).get("platforms", [])
        topic = prep.get("task_requirements", {}).get("topic_or_goal", "")
        auto_platforms = [p for p in platforms if (isinstance(intents_by_platform.get(p), dict) and intents_by_platform.get(p, {}).get("type") == "auto")]
        if not auto_platforms:
            return {"auto_intents": {}}
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.3)
        prompt = (
            "Suggest concise posting intents per platform for the given topic."
            " Respond in YAML mapping platform->intent string.\n"
            f"Platforms: {', '.join(auto_platforms)}\nTopic: {topic}"
        )
        messages = [
            {"role": "system", "content": "You are a marketing strategist."},
            {"role": "user", "content": prompt},
        ]
        resp = call_llm(messages, model=model, temperature=temperature)
        auto_map: Dict[str, str] = {}
        if yaml:
            try:
                y = yaml.safe_load(resp)
                if isinstance(y, dict):
                    auto_map = {str(k).lower(): str(v) for k, v in y.items()}
            except Exception:
                auto_map = {}
        return {"auto_intents": auto_map}

    def post(self, shared, prep_res, exec_res):
        # Initialize shared store per design schema
        shared.setdefault("config", {"style_policy": "strict"})
        shared.setdefault("task_requirements", {
            "platforms": ["email", "linkedin"],
            "intents_by_platform": {
                "email": {"type": "preset", "value": "outreach"},
                "linkedin": {"type": "custom", "value": "thought leadership"},
            },
            "topic_or_goal": "Announce our new AI feature",
            "subreddit_name_or_title": None,
            "urgency_level": "normal",
        })
        shared.setdefault("brand_bible", {
            "xml_raw": (
                "<brand>\n"
                "  <brand_name>Acme</brand_name>\n"
                "  <voice>clear</voice>\n"
                "  <tone>warm</tone>\n"
                "  <forbiddens><item>em_dash</item></forbiddens>\n"
                "</brand>"
            )
        })
        # house_style nested structure
        shared.setdefault("house_style", {
            "email_signature": {"name": None, "content": "Best,\nAcme Team"},
            "blog_style": {"name": None, "content": json.dumps({"title_case": True})},
        })
        # top-level reddit structure
        shared.setdefault("reddit", {"rules_text": None, "description_text": None})
        shared.setdefault("platform_nuance", {
            "linkedin": {"whitespace_density": "high", "para_length": "short", "hashtag_placement": "end"},
            "twitter": {"thread_ok_above_chars": 240, "hashtag_count_range": [0, 3]},
            "instagram": {"emoji_freq": "moderate", "line_breaks": "liberal", "hashtag_count_range": [8, 20]},
            "reddit": {"markdown_blocks": ["lists", "bold"], "tl_dr_required": True},
            "email": {"subject_target_chars": 50, "single_cta_required": True},
            "blog": {"h2_h3_depth": "deep", "link_density": "medium"},
        })

        # Initialize other structures
        shared.setdefault("platform_guidelines", {})
        shared.setdefault("content_pieces", {})
        shared.setdefault("style_compliance", {})
        shared.setdefault("workflow_state", {
            "current_stage": "engagement",
            "completed_stages": [],
            "revision_count": 0,
            "manual_review_required": False,
        })
        shared.setdefault("final_campaign", {
            "approved_content": {},
            "publishing_schedule": {},
            "performance_predictions": {},
            "edit_cycle_report": None,
        })
        if "stream" not in shared or shared["stream"] is None:
            shared["stream"] = Stream()
        shared.setdefault("llm", {"model": "anthropic/claude-3.5-sonnet", "temperature": 0.7})

        # Presets integration (load if preset_name provided and content missing)
        bb = shared.get("brand_bible", {})
        preset_name = bb.get("preset_name")
        if preset_name and not bb.get("xml_raw"):
            preset = get_preset("brand_bibles", preset_name)
            if preset and preset.get("xml_raw"):
                shared["brand_bible"]["xml_raw"] = preset["xml_raw"]
        # Optional save brand bible
        if bb.get("save_as_preset") and bb.get("preset_name") and bb.get("xml_raw"):
            save_preset("brand_bibles", bb["preset_name"], {"xml_raw": bb["xml_raw"]})
        # Email signature preset
        es = shared.get("house_style", {}).get("email_signature", {})
        if es.get("name") and not es.get("content"):
            sig = get_preset("email_sigs", es["name"]) or {}
            if sig.get("content"):
                shared["house_style"]["email_signature"]["content"] = sig["content"]
        if es.get("save_as_preset") and es.get("name") and es.get("content"):
            save_preset("email_sigs", es["name"], {"content": es["content"]})
        # Blog style preset
        bs = shared.get("house_style", {}).get("blog_style", {})
        if bs.get("name") and not bs.get("content"):
            st = get_preset("blog_styles", bs["name"]) or {}
            if st.get("content"):
                shared["house_style"]["blog_style"]["content"] = st["content"]
        if bs.get("save_as_preset") and bs.get("name") and bs.get("content"):
            save_preset("blog_styles", bs["name"], {"content": bs["content"]})

        # Normalize subreddit name/title if present
        sr = shared.get("task_requirements", {}).get("subreddit_name_or_title")
        if sr:
            shared["task_requirements"]["subreddit_name_or_title"] = normalize_subreddit(sr)

        # Merge auto-intents if produced
        auto_map = (exec_res or {}).get("auto_intents", {})
        if auto_map:
            intents = shared["task_requirements"].setdefault("intents_by_platform", {})
            for plat, intent in auto_map.items():
                intents[plat] = {"type": "auto", "value": intent}

        # Stream engagement milestone only (per streaming policy)
        shared["stream"].emit("milestone", "Engagement data prepared")
        shared["workflow_state"]["current_stage"] = "brand_bible_ingest"
        shared["workflow_state"]["completed_stages"].append("engagement")
        return "default"

class BrandBibleIngestNode(Node):
    def prep(self, shared):
        return shared.get("brand_bible", {}).get("xml_raw", "")

    def exec(self, xml_raw: str):
        parsed, missing = parse_brand_bible(xml_raw)
        persona = brand_bible_to_voice(parsed)
        return {"parsed": parsed, "missing": missing, "persona": persona}

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("brand_bible", {})
        shared["brand_bible"]["parsed"] = exec_res["parsed"]
        shared["brand_bible"]["missing"] = exec_res["missing"]
        shared["brand_bible"]["persona_voice"] = exec_res["persona"]
        # No streaming here per policy
        shared["workflow_state"]["current_stage"] = "voice_alignment"
        shared["workflow_state"]["completed_stages"].append("brand_bible_ingest")
        return "default"

class VoiceAlignmentNode(Node):
    def prep(self, shared):
        return shared.get("brand_bible", {}).get("persona_voice", {})

    def exec(self, persona_voice):
        # Normalize tone axes/styles; ensure forbiddens include hard bans
        persona_voice = dict(persona_voice or {})
        persona_voice.setdefault("axes", {}).setdefault("formality", "medium")
        persona_voice.setdefault("axes", {}).setdefault("vividness", "balanced")
        persona_voice.setdefault("styles", {}).setdefault("voice", persona_voice.get("styles", {}).get("voice", "clear"))
        forb = persona_voice.setdefault("forbiddens", {})
        forb["em_dash"] = True
        forb["rhetorical_contrast"] = True
        return persona_voice

    def post(self, shared, prep_res, exec_res):
        # Write back to brand_bible.persona_voice per schema
        shared.setdefault("brand_bible", {})
        shared["brand_bible"]["persona_voice"] = exec_res
        # No streaming here per policy
        shared["workflow_state"]["current_stage"] = "guidelines"
        shared["workflow_state"]["completed_stages"].append("voice_alignment")
        return "default"

class FormatGuidelinesRouter(Node):
    """Router node used inside BatchFlow to dispatch to per-platform nodes via action."""
    def prep(self, shared):
        return None

    def post(self, shared, prep_res, exec_res):
        platform = self.params.get("platform", "").lower()
        # Action name equals platform string
        return platform or "default"


class _BaseGuidelinesNode(Node):
    platform_name: str = ""

    def prep(self, shared):
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

    def exec(self, prep):
        return build_guidelines(self.platform_name, prep["persona"], prep["intent"], platform_nuance=prep.get("nuance"), reddit=prep.get("reddit"))

    def post(self, shared, prep_res, exec_res):
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
    def prep(self, shared):
        return {
            "guidelines": shared.get("platform_guidelines", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "intents": shared.get("task_requirements", {}).get("intents_by_platform", {}),
            "topic": shared.get("task_requirements", {}).get("topic_or_goal", ""),
            "house_style": shared.get("house_style", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
        def section_budgets(guidelines: Dict[str, Any]) -> Dict[str, int]:
            structure: List[str] = guidelines.get("structure", [])
            if not structure:
                return {}
            # Use char limit when available; else a small default per section
            total_chars = guidelines.get("limits", {}).get("chars") or guidelines.get("limits", {}).get("body", 800)
            per = max(40, int(total_chars / max(1, len(structure))))
            return {s: per for s in structure}

        def enforce_placements(text: str, g: Dict[str, Any]) -> str:
            # Move hashtags to end if required
            hashtags = g.get("hashtags")
            if isinstance(hashtags, dict) and hashtags.get("placement") == "end":
                tags = re.findall(r"#\w+", text)
                if tags:
                    text_wo_tags = re.sub(r"\s*#\w+", "", text).strip()
                    end_tags = " " + " ".join(tags[-hashtags.get("count", len(tags)):])
                    text = text_wo_tags + "\n" + end_tags
            return text

        out: Dict[str, Any] = {}
        topic = prep["topic"]
        model = prep.get("llm", {}).get("model")
        temperature = prep.get("llm", {}).get("temperature", 0.7)

        for platform, g in prep["guidelines"].items():
            sections: Dict[str, str] = {}
            parts: List[str] = []
            budgets = section_budgets(g)
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
            text = enforce_placements(text, g)
            # Final pass to remove forbidden patterns
            text = rewrite_with_constraints(text, prep["persona"], g)
            out[platform] = {"sections": sections, "text": text}
        return out

    def post(self, shared, prep_res, exec_res):
        shared["content_pieces"].update(exec_res)
        # No streaming here per policy; drafts available in shared when complete
        shared["workflow_state"]["current_stage"] = "style_editor"
        shared["workflow_state"]["completed_stages"].append("content_craftsman")
        return "default"


class StyleEditorNode(Node):
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "guidelines": shared.get("platform_guidelines", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
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
                    "Rewrite the text to remove AI fingerprints (stiff transitions, predictable lists, tidy wrap-ups, monotone rhythm, platitudes). "
                    "Do not change meaning or structure. Do not introduce em dashes or rhetorical contrasts.\n\n"
                    f"Voice: {prep['persona'].get('styles',{}).get('voice','clear')} | Axes: {json.dumps(prep['persona'].get('axes',{}))}\n"
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

    def post(self, shared, prep_res, exec_res):
        shared["content_pieces"].update(exec_res)
        shared["workflow_state"]["current_stage"] = "style_compliance"
        shared["workflow_state"]["completed_stages"].append("style_editor")
        return "default"


class StyleComplianceNode(Node):
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "revision_count": shared.get("workflow_state", {}).get("revision_count", 0),
        }

    def exec(self, prep):
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

    def post(self, shared, prep_res, exec_res):
        shared["style_compliance"] = exec_res["reports"]
        shared["workflow_state"]["revision_count"] = exec_res["revision_count"]
        pct, _msg = progress_for_stage(min(exec_res["revision_count"], 5), 5)
        shared["stream"].emit("milestone", f"Style check {exec_res['revision_count']}/5 ({pct}%): {exec_res['status']}")
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
    def prep(self, shared):
        return {
            "content": shared.get("content_pieces", {}),
            "persona": shared.get("brand_bible", {}).get("persona_voice", {}),
            "llm": shared.get("llm", {}),
        }

    def exec(self, prep):
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

    def post(self, shared, prep_res, exec_res):
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