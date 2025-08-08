from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

REQUIRED_FIELDS = ["brand_name", "voice", "tone", "forbiddens"]


def parse(xml_str: str) -> Tuple[Dict, List[str]]:
    """Parse Brand Bible XML into a dict and return (parsed, missing_fields).

    This is a tolerant minimal parser; real schemas can be added later.
    Expected structure example:
      <brand>
        <brand_name>Acme</brand_name>
        <voice>friendly</voice>
        <tone>warm</tone>
        <forbiddens>
          <item>em_dash</item>
          <item>rhetorical_contrast</item>
        </forbiddens>
      </brand>
    """
    parsed: Dict = {}
    missing: List[str] = []
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        # return empty parsed with all fields missing
        return {}, REQUIRED_FIELDS.copy()

    def _text(tag: str) -> str:
        el = root.find(tag)
        return el.text.strip() if el is not None and el.text else ""

    parsed["brand_name"] = _text("brand_name")
    parsed["voice"] = _text("voice")
    parsed["tone"] = _text("tone")

    forbiddens = []
    forbiddens_root = root.find("forbiddens")
    if forbiddens_root is not None:
        for item in forbiddens_root.findall("item"):
            if item.text:
                forbiddens.append(item.text.strip())
    parsed["forbiddens"] = forbiddens

    for f in REQUIRED_FIELDS:
        if not parsed.get(f):
            missing.append(f)
    return parsed, missing
