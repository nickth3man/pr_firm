"""
Pydantic schemas for structured LLM outputs.

These models provide type-safe, validated outputs from LLM calls
replacing fragile YAML/regex parsing with schema enforcement.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class AlignmentScore(BaseModel):
    """Brand alignment scoring output."""
    alignment_score: float = Field(
        ge=0.0, le=1.0,
        description="Brand alignment score from 0.0 to 1.0"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="2-3 micro-edit suggestions for improvement"
    )


class ClaimItem(BaseModel):
    """Individual claim requiring validation."""
    text: str = Field(description="The claim text")
    needs_source: bool = Field(description="Whether this claim needs a source citation")


class FactValidationOutput(BaseModel):
    """Fact validation results for a content piece."""
    claims: List[ClaimItem] = Field(
        default_factory=list,
        description="List of claims and their source requirements"
    )


class AuthenticityWarning(BaseModel):
    """Authenticity audit warnings for content."""
    hype_flags: List[str] = Field(
        default_factory=list,
        description="Terms or phrases flagged as hype/over-claiming"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable suggestions to improve authenticity"
    )


class ScheduleItem(BaseModel):
    """Single publishing schedule entry."""
    platform: str = Field(description="Target platform")
    day: str = Field(description="Day of week (Mon, Tue, etc.)")
    time: str = Field(description="Time in HH:MM format")


class PerformancePrediction(BaseModel):
    """Performance prediction for a platform."""
    expected_engagement: str = Field(
        pattern="^(low|medium|high)$",
        description="Expected engagement level"
    )
    notes: str = Field(default="", description="Additional notes")


class CampaignPlanOutput(BaseModel):
    """Complete campaign planning output from AgencyDirector."""
    schedule: List[ScheduleItem] = Field(
        default_factory=list,
        description="Publishing schedule"
    )
    predictions: Dict[str, PerformancePrediction] = Field(
        default_factory=dict,
        description="Performance predictions per platform"
    )


class ContentSection(BaseModel):
    """Single section of generated content."""
    section_name: str = Field(description="Name of the section")
    text: str = Field(description="Generated text for this section")
    char_count: int = Field(default=0, description="Character count")


class PlatformContent(BaseModel):
    """Complete content for a single platform."""
    platform: str = Field(description="Platform name")
    sections: List[ContentSection] = Field(default_factory=list)
    full_text: str = Field(description="Complete formatted text")
    hashtags: List[str] = Field(default_factory=list)
    estimated_chars: int = Field(default=0)


class IntentSuggestion(BaseModel):
    """Auto-generated intent suggestion per platform."""
    platform: str = Field(description="Platform name")
    intent: str = Field(description="Suggested posting intent")


class EngagementIntentsOutput(BaseModel):
    """Output from EngagementManager auto-intent generation."""
    intents: List[IntentSuggestion] = Field(default_factory=list)


class StyleEditResult(BaseModel):
    """Result of style editing operation."""
    edited_text: str = Field(description="Edited text with AI fingerprints removed")
    changes_made: List[str] = Field(
        default_factory=list,
        description="List of changes applied"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        default=0.8,
        description="Confidence in the edit quality"
    )


class StyleViolationItem(BaseModel):
    """Individual style violation."""
    violation_type: str = Field(description="Type of violation")
    message: str = Field(description="Human-readable description")
    line_number: int = Field(default=0)
    context: str = Field(default="")


class StyleComplianceReport(BaseModel):
    """Complete style compliance report."""
    platform: str = Field(description="Platform name")
    violations: List[StyleViolationItem] = Field(default_factory=list)
    passed: bool = Field(description="Whether content passed all checks")
    suggestions: List[str] = Field(default_factory=list)


class PlatformGuideline(BaseModel):
    """Generated platform-specific guidelines."""
    platform: str = Field(description="Platform name")
    tone_guidance: str = Field(description="Tone guidance for this platform")
    structure: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    hashtag_strategy: Dict[str, Any] = Field(default_factory=dict)
    emoji_guidance: str = Field(default="")


class EditCycleSummary(BaseModel):
    """Summary of edit cycle results."""
    revision_count: int = Field(description="Number of revisions performed")
    max_revisions_reached: bool = Field(description="Whether max revisions was hit")
    final_violation_count: int = Field(default=0)
    report_summary: str = Field(default="")


# Union type for all LLM outputs
LLMOutput = (
    AlignmentScore | 
    FactValidationOutput | 
    AuthenticityWarning | 
    CampaignPlanOutput | 
    PlatformContent |
    EngagementIntentsOutput |
    StyleEditResult |
    StyleComplianceReport |
    PlatformGuideline |
    EditCycleSummary
)
