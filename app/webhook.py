from __future__ import annotations
import json
import time
from typing import Iterable, Dict, Any, List
import httpx

from .config import settings
from .logging_util import get_logger

log = get_logger("webhook")

def _parse_endpoints() -> List[str]:
    urls = (settings.WEBHOOK_URLS or "").strip()
    if not urls:
        return []
    return [u.strip() for u in urls.split(",") if u.strip()]

def notify_news(items: Iterable[Dict[str, Any]]):
    endpoints = _parse_endpoints()
    if not endpoints:
        return
    payload = {"event": "news.created", "count": len(list(items))}
    # Send one-by-one to preserve memory, and include record content
    for it in items:
        body = {"event": "news.created", "record": it}
        for url in endpoints:
            _post_with_retry(url, body)

def _post_with_retry(url: str, body: Dict[str, Any], retries: int = 3, backoff: float = 1.0):
    last_err = None
    for i in range(retries):
        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.post(url, json=body, headers={"Content-Type": "application/json"})
                if r.status_code < 300:
                    log.info(f"Webhook OK -> {url}")
                    return
                else:
                    last_err = f"[{r.status_code}] {r.text[:200]}"
        except Exception as e:
            last_err = str(e)
        time.sleep(backoff * (2 ** i))
    log.error(f"Webhook failed -> {url}: {last_err}")
