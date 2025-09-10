from __future__ import annotations
import yaml
from typing import List, Tuple, Dict, Any
from .sources.rss_source import RSSSource
from .sources.base import Source

def load_sources(yaml_path: str) -> List[Source]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # Support both top-level list (legacy) and dict with 'sources' key (new style)
    if isinstance(cfg, list):
        src_list = cfg
        translation_cfg = {}
    else:
        src_list = cfg.get("sources", [])
        translation_cfg = cfg.get("translation", {}) or {}

    sources: List[Source] = []
    for s in src_list:
        if not s.get("rss_url") and not s.get("url"):
            continue
        if not s.get("enabled", True):
            # assume enabled by default
            pass
        t = (s.get("type") or "rss").lower()
        name = s.get("name", "Unnamed")
        lang = s.get("language", "")
        translate_to_tr = bool(s.get("translate_to_tr", False))
        url = s.get("rss_url") or s.get("url")
        if t == "rss":
            sources.append(RSSSource(name=name, url=url, language=lang, translate_to_tr=translate_to_tr, translator_cfg=translation_cfg))
        else:
            # future: implement JSON APIs etc.
            pass
    return sources
