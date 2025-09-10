from __future__ import annotations
from datetime import datetime, timezone
from typing import Iterable, List, Dict, Any

from .base import Source, Item
from ..translation import Translator

def _clean_html(summary: str) -> str:
    try:
        # Lazy import BeautifulSoup
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            return summary or ""
        return BeautifulSoup(summary or "", "html.parser").get_text(" ", strip=True)
    except Exception:
        return summary or ""

class RSSSource(Source):
    def __init__(self, name: str, url: str, language: str = "", translate_to_tr: bool = False, translator_cfg: Dict[str, Any] | None = None, **kwargs):
        super().__init__(name, language, translate_to_tr, meta={"type": "rss", "url": url})
        self.url = url
        self.translator = Translator(translator_cfg or {}) if translate_to_tr else None

    def fetch(self) -> Iterable[Item]:
        # Lazy import feedparser
        try:
            import feedparser  # type: ignore
        except Exception:
            # If feedparser is not available, return empty list so the app continues running
            return []
        feed = feedparser.parse(self.url)
        items: List[Item] = []
        # Only process the first entry (most recent item)
        for e in (getattr(feed, "entries", []) or [])[:1]:
            # published_parsed may be missing -> fallback to now()
            if hasattr(e, "published_parsed") and e.published_parsed:
                dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(e, "updated_parsed") and e.updated_parsed:
                dt = datetime(*e.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                dt = datetime.now(tz=timezone.utc)

            title = getattr(e, "title", "").strip()
            link = getattr(e, "link", "").strip()
            summary = _clean_html(getattr(e, "summary", ""))
            content = summary

            lang = self.language or "en"

            # If the source is English and translate_to_tr is true, translate title/summary
            if self.translator and (lang.lower().startswith("en")):
                try:
                    tr_title = self.translator.translate(title, source_lang="en", target_lang="tr") if title else title
                    tr_summary = self.translator.translate(summary, source_lang="en", target_lang="tr") if summary else summary
                    # Store original in raw
                    raw = dict(original=dict(title=title, summary=summary, language=lang))
                    title, summary, content, lang = tr_title or title, tr_summary or summary, tr_summary or summary, "tr"
                except Exception:
                    raw = {}
            else:
                raw = {}

            base_raw = dict(
                feed=dict(title=getattr(getattr(feed, "feed", {}), "get", lambda *_: "")("title", ""),
                          link=getattr(getattr(feed, "feed", {}), "get", lambda *_: "")("link", ""))
            )
            # add entry raw if available
            try:
                base_raw["e"] = e
            except Exception:
                pass
            raw.update(base_raw)

            items.append(Item(
                source_name=self.name,
                title=title,
                url=link,
                published_at=dt,
                summary=summary,
                content=content,
                language=lang,
                raw=raw,
            ))
        return items
