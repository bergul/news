from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional, Dict, Any
from datetime import datetime, timezone

@dataclass
class Item:
    source_name: str
    title: str
    url: str
    published_at: datetime
    summary: str
    content: str
    language: str
    raw: Dict[str, Any]

class Source:
    def __init__(self, name: str, language: str = "", translate_to_tr: bool = False, meta: Dict[str, Any] | None = None, **kwargs):
        self.name = name
        self.language = language or ""
        self.translate_to_tr = bool(translate_to_tr)
        self.meta = meta or {}

    def fetch(self) -> Iterable[Item]:
        raise NotImplementedError
