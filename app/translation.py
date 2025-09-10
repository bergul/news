from __future__ import annotations
import httpx
from typing import Optional, Dict

class Translator:
    def __init__(self, cfg: Dict):
        self.cfg = cfg or {}
        self.primary = (self.cfg.get("provider_primary") or "").lower()
        self.fallback = (self.cfg.get("provider_fallback") or "").lower()

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "tr") -> str:
        if not text:
            return text
        # try primary
        if self.primary == "libretranslate":
            out = self._libretranslate(text, source_lang, target_lang)
            if out:
                return out
        elif self.primary == "mymemory":
            out = self._mymemory(text, source_lang, target_lang)
            if out:
                return out
        # fallback
        if self.fallback == "libretranslate":
            out = self._libretranslate(text, source_lang, target_lang)
            if out:
                return out
        elif self.fallback == "mymemory":
            out = self._mymemory(text, source_lang, target_lang)
            if out:
                return out
        return text  # give up

    def _libretranslate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        try:
            lt = self.cfg.get("libretranslate") or {}
            url = lt.get("endpoint")
            if not url:
                return None
            payload = {"q": text, "source": source_lang, "target": target_lang, "format": "text"}
            with httpx.Client(timeout=10.0) as client:
                r = client.post(url, json=payload)
                if r.status_code == 200:
                    data = r.json()
                    return data.get("translatedText") or data.get("translated_text") or None
        except Exception:
            return None
        return None

    def _mymemory(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        try:
            mm = self.cfg.get("mymemory") or {}
            url = mm.get("endpoint")
            if not url:
                return None
            params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
            with httpx.Client(timeout=10.0) as client:
                r = client.get(url, params=params)
                if r.status_code == 200:
                    data = r.json()
                    return (data.get("responseData") or {}).get("translatedText")
        except Exception:
            return None
        return None
