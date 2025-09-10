from __future__ import annotations
import hashlib
from typing import Iterable, List

COMMODITY_KEYWORDS_TR = [
    "altın","gümüş","petrol","doğalgaz","bakır","pamuk","buğday","mısır","kahve","şeker","nikel","alüminyum","platin","paladyum"
]
COMMODITY_KEYWORDS_EN = [
    "gold","silver","oil","crude","brent","natural gas","copper","cotton","wheat","corn","coffee","sugar","nickel","aluminum","platinum","palladium"
]

def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def tag_by_keywords(text: str, lang: str) -> List[str]:
    text_l = (text or "").lower()
    bag = []
    pool = COMMODITY_KEYWORDS_TR if (lang or "").startswith("tr") else COMMODITY_KEYWORDS_EN
    for kw in pool:
        if kw in text_l:
            bag.append(kw)
    return sorted(set(bag))

def join_tags(tags: Iterable[str]) -> str:
    return ",".join(sorted(set([t.strip() for t in tags if t and t.strip()])))
