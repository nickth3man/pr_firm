"""
PlatformRegistry - Centralized configuration for all supported platforms.

This module provides a single source of truth for platform constraints,
guidelines, and behaviors. New platforms can be added via JSON config files
without code changes.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class PlatformLimits:
    """Character and content limits for a platform."""
    chars: Optional[int] = None
    body: Optional[int] = None
    approx_chars: int = 800
    hashtag_min: int = 0
    hashtag_max: int = 0
    thread_ok_above_chars: Optional[int] = None


@dataclass
class PlatformStyle:
    """Style and formatting rules for a platform."""
    whitespace_density: str = "normal"  # high, normal, low
    para_length: str = "medium"  # short, medium, long
    hashtag_placement: str = "inline"  # end, inline, none
    emoji_freq: str = "none"  # none, minimal, moderate, liberal
    line_breaks: str = "normal"  # conservative, normal, liberal
    markdown_blocks: List[str] = field(default_factory=list)
    tl_dr_required: bool = False
    subject_target_chars: Optional[int] = None
    single_cta_required: bool = False
    h2_h3_depth: str = "normal"  # shallow, normal, deep
    link_density: str = "low"  # low, medium, high


@dataclass
class PlatformConfig:
    """Complete configuration for a platform."""
    name: str
    display_name: str
    limits: PlatformLimits = field(default_factory=PlatformLimits)
    style: PlatformStyle = field(default_factory=PlatformStyle)
    content_types: Dict[str, Any] = field(default_factory=dict)
    structure: List[str] = field(default_factory=list)
    section_budgets: Dict[str, int] = field(default_factory=dict)
    default_intent: str = "general"
    supports_media: bool = False
    supported_media_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "limits": {
                "chars": self.limits.chars,
                "body": self.limits.body,
                "approx_chars": self.limits.approx_chars,
                "hashtag_min": self.limits.hashtag_min,
                "hashtag_max": self.limits.hashtag_max,
                "thread_ok_above_chars": self.limits.thread_ok_above_chars,
            },
            "style": {
                "whitespace_density": self.style.whitespace_density,
                "para_length": self.style.para_length,
                "hashtag_placement": self.style.hashtag_placement,
                "emoji_freq": self.style.emoji_freq,
                "line_breaks": self.style.line_breaks,
                "markdown_blocks": self.style.markdown_blocks,
                "tl_dr_required": self.style.tl_dr_required,
                "subject_target_chars": self.style.subject_target_chars,
                "single_cta_required": self.style.single_cta_required,
                "h2_h3_depth": self.style.h2_h3_depth,
                "link_density": self.style.link_density,
            },
            "content_types": self.content_types,
            "structure": self.structure,
            "section_budgets": self.section_budgets,
            "default_intent": self.default_intent,
            "supports_media": self.supports_media,
            "supported_media_types": self.supported_media_types,
        }


class PlatformRegistry:
    """
    Centralized registry for all platform configurations.
    
    Provides singleton access to platform configs with support for
    loading from JSON files and runtime registration.
    """
    
    _instance: Optional["PlatformRegistry"] = None
    _platforms: Dict[str, PlatformConfig]
    _config_dir: Optional[Path]
    
    def __new__(cls, config_dir: Optional[Path] = None) -> "PlatformRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._platforms = {}
            cls._instance._config_dir = config_dir
            cls._instance._initialize_defaults()
            if config_dir:
                cls._instance._load_from_directory(config_dir)
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
    
    def _initialize_defaults(self) -> None:
        """Initialize default platform configurations."""
        # Twitter/X
        self.register(PlatformConfig(
            name="twitter",
            display_name="Twitter/X",
            limits=PlatformLimits(
                chars=280,
                approx_chars=280,
                hashtag_max=3,
                thread_ok_above_chars=240,
            ),
            style=PlatformStyle(
                whitespace_density="low",
                para_length="short",
                hashtag_placement="inline",
                emoji_freq="minimal",
                line_breaks="conservative",
            ),
            structure=["hook", "body", "cta"],
            section_budgets={"hook": 60, "body": 180, "cta": 40},
            default_intent="engagement",
        ))
        
        # LinkedIn
        self.register(PlatformConfig(
            name="linkedin",
            display_name="LinkedIn",
            limits=PlatformLimits(
                chars=3000,
                approx_chars=1200,
                hashtag_max=3,
            ),
            style=PlatformStyle(
                whitespace_density="high",
                para_length="short",
                hashtag_placement="end",
                emoji_freq="minimal",
                line_breaks="liberal",
            ),
            structure=["hook", "story", "insight", "cta"],
            section_budgets={"hook": 150, "story": 400, "insight": 300, "cta": 100},
            default_intent="thought leadership",
        ))
        
        # Instagram
        self.register(PlatformConfig(
            name="instagram",
            display_name="Instagram",
            limits=PlatformLimits(
                chars=2200,
                approx_chars=800,
                hashtag_min=8,
                hashtag_max=20,
            ),
            style=PlatformStyle(
                whitespace_density="high",
                para_length="short",
                hashtag_placement="end",
                emoji_freq="moderate",
                line_breaks="liberal",
            ),
            structure=["hook", "body", "hashtags"],
            section_budgets={"hook": 100, "body": 500, "hashtags": 200},
            default_intent="engagement",
            supports_media=True,
            supported_media_types=["image", "video", "carousel"],
        ))
        
        # Reddit
        self.register(PlatformConfig(
            name="reddit",
            display_name="Reddit",
            limits=PlatformLimits(
                approx_chars=2000,
                hashtag_max=0,
            ),
            style=PlatformStyle(
                whitespace_density="normal",
                para_length="medium",
                hashtag_placement="none",
                emoji_freq="none",
                line_breaks="normal",
                markdown_blocks=["lists", "bold", "italic", "links"],
                tl_dr_required=True,
            ),
            structure=["tl_dr", "body", "context"],
            section_budgets={"tl_dr": 100, "body": 1500, "context": 400},
            default_intent="discussion",
        ))
        
        # Email
        self.register(PlatformConfig(
            name="email",
            display_name="Email",
            limits=PlatformLimits(
                approx_chars=1500,
                hashtag_max=0,
            ),
            style=PlatformStyle(
                whitespace_density="normal",
                para_length="medium",
                hashtag_placement="none",
                emoji_freq="none",
                line_breaks="normal",
                subject_target_chars=50,
                single_cta_required=True,
            ),
            structure=["subject", "greeting", "body", "cta", "signature"],
            section_budgets={"subject": 50, "greeting": 50, "body": 1000, "cta": 100, "signature": 100},
            default_intent="outreach",
        ))
        
        # Blog
        self.register(PlatformConfig(
            name="blog",
            display_name="Blog",
            limits=PlatformLimits(
                chars=50000,
                approx_chars=2000,
                hashtag_max=0,
            ),
            style=PlatformStyle(
                whitespace_density="normal",
                para_length="long",
                hashtag_placement="none",
                emoji_freq="none",
                line_breaks="normal",
                h2_h3_depth="deep",
                link_density="medium",
            ),
            structure=["title", "intro", "h2_section", "h3_section", "conclusion"],
            section_budgets={"title": 60, "intro": 200, "h2_section": 500, "h3_section": 300, "conclusion": 200},
            default_intent="education",
        ))
    
    def _load_from_directory(self, config_dir: Path) -> None:
        """Load platform configurations from JSON files in directory."""
        if not config_dir.exists():
            return
        
        for config_file in config_dir.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                config = self._config_from_dict(data)
                self.register(config)
            except Exception as e:
                print(f"Warning: Failed to load platform config from {config_file}: {e}")
    
    def _config_from_dict(self, data: Dict[str, Any]) -> PlatformConfig:
        """Create PlatformConfig from dictionary."""
        limits_data = data.get("limits", {})
        limits = PlatformLimits(
            chars=limits_data.get("chars"),
            body=limits_data.get("body"),
            approx_chars=limits_data.get("approx_chars", 800),
            hashtag_min=limits_data.get("hashtag_min", 0),
            hashtag_max=limits_data.get("hashtag_max", 0),
            thread_ok_above_chars=limits_data.get("thread_ok_above_chars"),
        )
        
        style_data = data.get("style", {})
        style = PlatformStyle(
            whitespace_density=style_data.get("whitespace_density", "normal"),
            para_length=style_data.get("para_length", "medium"),
            hashtag_placement=style_data.get("hashtag_placement", "inline"),
            emoji_freq=style_data.get("emoji_freq", "none"),
            line_breaks=style_data.get("line_breaks", "normal"),
            markdown_blocks=style_data.get("markdown_blocks", []),
            tl_dr_required=style_data.get("tl_dr_required", False),
            subject_target_chars=style_data.get("subject_target_chars"),
            single_cta_required=style_data.get("single_cta_required", False),
            h2_h3_depth=style_data.get("h2_h3_depth", "normal"),
            link_density=style_data.get("link_density", "low"),
        )
        
        return PlatformConfig(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            limits=limits,
            style=style,
            content_types=data.get("content_types", {}),
            structure=data.get("structure", []),
            section_budgets=data.get("section_budgets", {}),
            default_intent=data.get("default_intent", "general"),
            supports_media=data.get("supports_media", False),
            supported_media_types=data.get("supported_media_types", []),
        )
    
    def register(self, config: PlatformConfig) -> None:
        """Register a new platform configuration."""
        self._platforms[config.name.lower()] = config
    
    def get(self, name: str) -> Optional[PlatformConfig]:
        """Get platform configuration by name."""
        return self._platforms.get(name.lower())
    
    def get_all(self) -> Dict[str, PlatformConfig]:
        """Get all registered platforms."""
        return dict(self._platforms)
    
    def list_platforms(self) -> List[str]:
        """List all registered platform names."""
        return list(self._platforms.keys())
    
    def validate_platforms(self, platforms: List[str]) -> tuple:
        """
        Validate a list of platform names.
        
        Returns:
            Tuple of (valid_platforms, invalid_platforms)
        """
        valid = []
        invalid = []
        for p in platforms:
            if p.lower() in self._platforms:
                valid.append(p.lower())
            else:
                invalid.append(p)
        return valid, invalid
    
    def get_limits(self, name: str) -> Optional[PlatformLimits]:
        """Get limits for a platform."""
        config = self.get(name)
        return config.limits if config else None
    
    def get_style(self, name: str) -> Optional[PlatformStyle]:
        """Get style for a platform."""
        config = self.get(name)
        return config.style if config else None
    
    def calculate_section_budgets(self, name: str) -> Dict[str, int]:
        """Calculate character budgets for each section."""
        config = self.get(name)
        if not config:
            return {}
        
        if config.section_budgets:
            return config.section_budgets
        
        structure = config.structure or ["body"]
        limits = config.limits
        total = limits.approx_chars if limits else 800
        per = max(40, int(total / len(structure)))
        return {s: per for s in structure}


# Global accessor function
def get_platform_registry(config_dir: Optional[Path] = None) -> PlatformRegistry:
    """Get the global PlatformRegistry instance."""
    return PlatformRegistry(config_dir)


def get_platform_config(name: str) -> Optional[PlatformConfig]:
    """Convenience function to get a platform config by name."""
    return get_platform_registry().get(name)
