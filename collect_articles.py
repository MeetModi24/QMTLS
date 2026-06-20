#!/usr/bin/env python3
"""
Collect article text for URLs in <cluster>/subtopics/<subtopic>/article_urls.jsonl
and write articles.jsonl (UTF-8) in the same folder.

Install:
    pip install requests trafilatura readability-lxml beautifulsoup4 lxml_html_clean
    pip install curl_cffi    # strongly recommended (bypasses Cloudflare 403s)

Usage:
    python collect_articles_v2.py --cluster c1
    python collect_articles_v2.py --cluster c1 --subtopic c1_a_us_iran
    python collect_articles_v2.py --cluster c1 --no-resume
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, quote

# ------------------------------------------------------------------
# Optional curl_cffi (Chrome TLS impersonation)
# ------------------------------------------------------------------
HAVE_CURL_CFFI = False
try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    HAVE_CURL_CFFI = True
except ImportError:
    pass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------------------------------------------------------
# Extractors
# ------------------------------------------------------------------
try:
    import trafilatura
except ImportError:
    sys.exit("pip install trafilatura lxml_html_clean")

try:
    from readability import Document as ReadabilityDoc
    HAVE_READABILITY = True
except ImportError:
    HAVE_READABILITY = False

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("pip install beautifulsoup4")


# ==================================================================
# Config
# ==================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

MIN_TEXT_LEN     = 150
DEFAULT_TIMEOUT  = 25
LONG_TIMEOUT     = 60
DOMAIN_DELAY     = 0.6
WAYBACK_TIMEOUT  = 30

SLOW_DOMAINS = {
    "sputniknews.com", "themoscowtimes.com", "looptt.com",
    "theboltonnews.co.uk", "dawn.com", "tribune.com.pk",
    "almasdarnews.com", "washingtonpost.com",
}

SKIP_SSL_VERIFY = {"plenglish.com"}

PREFER_BROWSER_IMPERSONATION = {
    "xinhuanet.com", "hltv.org", "syriahr.com", "presstv.com",
    "kurdistan24.net", "arabnews.com", "telegraph.co.uk",
    "france24.com", "rfi.fr", "alarabiya.net", "barrons.com",
    "wsj.com", "marketwatch.com", "bloomberg.com", "thestar.com",
    "investmentwatchblog.com", "thisismoney.co.uk",
    "english.ahram.org.eg", "ahram.org.eg", "usip.org", "centcom.mil",
    "cambridge.org", "panow.com", "pinknews.co.uk", "mb.com.ph",
    "almanar.com.lb", "english.almanar.com.lb",
}

TRY_AMP = {
    "timesofisrael.com", "thetimes.co.uk", "thesun.co.uk",
    "telegraph.co.uk", "ft.com", "wsj.com",
}

WAYBACK_ONLY_DOMAINS = {"reuters.com", "in.reuters.com",
                        "uk.reuters.com", "cn.reuters.com"}


# ==================================================================
# Text cleaning  — strip weird characters but keep human-readable text
# ==================================================================

# Characters to wipe outright: zero-width, BOM, bidi marks, soft hyphen,
# replacement char, line/paragraph separators, etc.
_INVISIBLE_RE = re.compile(
    "["
    "\u200b\u200c\u200d\u200e\u200f"   # zero-width / bidi
    "\u202a-\u202e"                     # bidi overrides
    "\u2060-\u2064"                     # invisible operators
    "\ufeff"                            # BOM
    "\u00ad"                            # soft hyphen
    "\ufffd"                            # replacement char
    "\u2028\u2029"                      # line/paragraph separators
    "]"
)

# Smart-quote / punctuation normalization (safe, keeps meaning)
_PUNCT_MAP = {
    "\u00a0": " ",       # nbsp -> space
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u2026": "...",
    "\u00b7": "*", "\u2022": "*",
}
_PUNCT_RE = re.compile("|".join(re.escape(k) for k in _PUNCT_MAP))


def clean_text(text: str) -> str:
    """Normalize unicode and strip invisible/control characters."""
    if not text:
        return ""
    # Normalize unicode (NFKC folds half/full-width, ligatures, etc.)
    text = unicodedata.normalize("NFKC", text)
    # Drop invisible / formatting characters
    text = _INVISIBLE_RE.sub("", text)
    # Replace smart quotes / dashes / nbsp
    text = _PUNCT_RE.sub(lambda m: _PUNCT_MAP[m.group(0)], text)
    # Strip all remaining control chars except \n and \t
    text = "".join(
        ch for ch in text
        if ch in ("\n", "\t") or not unicodedata.category(ch).startswith("C")
    )
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ==================================================================
# Logging + sessions
# ==================================================================

def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )


def make_requests_session() -> requests.Session:
    sess = requests.Session()
    retry = Retry(
        total=2, connect=2, read=2,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    sess.headers.update({"User-Agent": random.choice(USER_AGENTS), **BROWSER_HEADERS})
    return sess


# ==================================================================
# Per-domain politeness
# ==================================================================

_last_hit: dict = {}
_last_hit_lock = Lock()


def domain_wait(url: str, delay: float = DOMAIN_DELAY) -> None:
    host = urlparse(url).netloc.lower()
    with _last_hit_lock:
        last = _last_hit.get(host, 0.0)
        wait = (last + delay) - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_hit[host] = time.monotonic()


def host_of(url: str) -> str:
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def matches_any(host: str, domains: set) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


# ==================================================================
# HTTP fetching
# ==================================================================

class FetchError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}" if detail else reason)


def fetch_with_requests(session, url, timeout, verify=True):
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True, verify=verify)
    except requests.exceptions.Timeout:
        raise FetchError("timeout", url)
    except requests.exceptions.SSLError as e:
        raise FetchError("ssl", str(e)[:200])
    except requests.exceptions.ConnectionError as e:
        raise FetchError("connection", str(e)[:200])
    except requests.exceptions.RequestException as e:
        raise FetchError("network", str(e)[:200])

    if resp.status_code >= 400:
        raise FetchError(f"http_{resp.status_code}", url)

    ctype = resp.headers.get("Content-Type", "").lower()
    if ctype and "html" not in ctype and "xml" not in ctype:
        raise FetchError("not_html", ctype)

    # Force UTF-8 if the server didn't declare an encoding
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"

    html = resp.text
    if not html or len(html) < 500:
        raise FetchError("empty_body", f"{len(html)} bytes")
    return resp.url, html


def fetch_with_curl_cffi(url, timeout, verify=True):
    if not HAVE_CURL_CFFI:
        raise FetchError("no_curl_cffi", "install curl_cffi")
    headers = {"User-Agent": random.choice(USER_AGENTS), **BROWSER_HEADERS}
    try:
        resp = cffi_requests.get(
            url, headers=headers, timeout=timeout,
            impersonate="chrome124", verify=verify, allow_redirects=True,
        )
    except Exception as e:
        msg = str(e).lower()
        if "timeout" in msg or "timed out" in msg:
            raise FetchError("timeout", str(e)[:200])
        if "ssl" in msg or "certificate" in msg:
            raise FetchError("ssl", str(e)[:200])
        if "resolve" in msg or "connect" in msg:
            raise FetchError("connection", str(e)[:200])
        raise FetchError("network", str(e)[:200])

    if resp.status_code >= 400:
        raise FetchError(f"http_{resp.status_code}", url)
    ctype = resp.headers.get("Content-Type", "").lower()
    if ctype and "html" not in ctype and "xml" not in ctype:
        raise FetchError("not_html", ctype)
    html = resp.text
    if not html or len(html) < 500:
        raise FetchError("empty_body", f"{len(html)} bytes")
    return str(resp.url), html


def fetch_wayback(url, timeout=WAYBACK_TIMEOUT, near=None):
    api = f"https://archive.org/wayback/available?url={quote(url, safe='')}"
    if near:
        api += f"&timestamp={near}"
    r = requests.get(api, timeout=timeout,
                     headers={"User-Agent": random.choice(USER_AGENTS)})
    if r.status_code != 200:
        raise FetchError("wayback_api", f"http_{r.status_code}")
    data = r.json()
    snap = (data.get("archived_snapshots") or {}).get("closest") or {}
    if not snap.get("available") or not snap.get("url"):
        raise FetchError("wayback_no_snapshot", url)
    snap_url = snap["url"].replace("http://web.archive.org",
                                   "https://web.archive.org")
    snap_url = snap_url.replace(f"/{snap['timestamp']}/",
                                f"/{snap['timestamp']}id_/", 1)
    r2 = requests.get(snap_url, timeout=timeout,
                      headers={"User-Agent": random.choice(USER_AGENTS)})
    if r2.status_code >= 400:
        raise FetchError(f"wayback_http_{r2.status_code}", snap_url)
    if not r2.encoding or r2.encoding.lower() == "iso-8859-1":
        r2.encoding = r2.apparent_encoding or "utf-8"
    html = r2.text
    if not html or len(html) < 500:
        raise FetchError("wayback_empty", f"{len(html)} bytes")
    return snap_url, html


def guess_wayback_timestamp(url, record):
    pub = record.get("pub_date") or ""
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", pub)
    if m:
        y, mo, d = m.groups()
        return f"{y}{int(mo):02d}{int(d):02d}"
    m = re.search(r"/(20\d{2})/(\d{1,2})/(\d{1,2})/", url)
    if m:
        y, mo, d = m.groups()
        return f"{y}{int(mo):02d}{int(d):02d}"
    m = re.search(r"/(20\d{2})/", url)
    if m:
        return f"{m.group(1)}0701"
    return None


def amp_variants(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    out = [
        url + ("&" if "?" in url else "?") + "amp=1",
        f"{parsed.scheme}://{parsed.netloc}{path}/amp",
        f"{parsed.scheme}://{parsed.netloc}{path}.amp",
    ]
    if not parsed.netloc.startswith("amp."):
        out.append(f"{parsed.scheme}://amp.{parsed.netloc}{parsed.path}")
    return out


# ==================================================================
# Extraction cascade
# ==================================================================

BOILERPLATE_PATTERNS = [
    r"please enable javascript",
    r"subscribe to continue",
    r"sign in to read",
    r"this site requires javascript",
]


def is_boilerplate(text):
    low = text.lower()
    return any(re.search(p, low) for p in BOILERPLATE_PATTERNS) and len(text) < 400


def _has_lxml():
    try:
        import lxml  # noqa
        return True
    except ImportError:
        return False


def extract_trafilatura(html, url):
    extracted = trafilatura.extract(
        html, url=url,
        include_comments=False, include_tables=False,
        with_metadata=True, output_format="json",
        favor_recall=True,
    )
    if not extracted:
        return None
    data = json.loads(extracted)
    text = (data.get("text") or "").strip()
    if len(text) < MIN_TEXT_LEN or is_boilerplate(text):
        return None
    return {"text": text, "title": data.get("title"), "date": data.get("date")}


def extract_readability(html, url):
    if not HAVE_READABILITY:
        return None
    try:
        doc = ReadabilityDoc(html)
        title = doc.short_title()
        content_html = doc.summary()
    except Exception:
        return None
    soup = BeautifulSoup(content_html, "lxml" if _has_lxml() else "html.parser")
    text = soup.get_text("\n", strip=True)
    if len(text) < MIN_TEXT_LEN or is_boilerplate(text):
        return None
    return {"text": text, "title": title, "date": None}


def extract_soup(html, url):
    soup = BeautifulSoup(html, "lxml" if _has_lxml() else "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header",
                     "footer", "aside", "form", "iframe"]):
        tag.decompose()
    candidates = []
    for sel in ["article", "main",
                "[itemprop='articleBody']",
                "[class*='article-body']", "[class*='article__body']",
                "[class*='story-body']", "[class*='post-content']",
                "[class*='entry-content']", "[id*='article-body']",
                "[id*='story-body']"]:
        for node in soup.select(sel):
            text = node.get_text("\n", strip=True)
            if len(text) >= MIN_TEXT_LEN:
                candidates.append(text)
    if not candidates:
        body = soup.find("body")
        if body:
            text = body.get_text("\n", strip=True)
            if len(text) >= MIN_TEXT_LEN * 2:
                candidates.append(text)
    if not candidates:
        return None
    text = max(candidates, key=len)
    if is_boilerplate(text):
        return None
    title_tag = soup.find(["h1", "title"])
    title = title_tag.get_text(strip=True) if title_tag else None
    return {"text": text, "title": title, "date": None}


def extract_cascade(html, url):
    for fn in (extract_trafilatura, extract_readability, extract_soup):
        try:
            res = fn(html, url)
        except Exception as e:
            logging.debug("extractor %s failed: %s", fn.__name__, e)
            continue
        if res and res.get("text"):
            return res
    return None


# ==================================================================
# Per-URL orchestration
# ==================================================================

def fetch_html(session, url, timeout):
    host = host_of(url)
    verify = not matches_any(host, SKIP_SSL_VERIFY)

    if matches_any(host, WAYBACK_ONLY_DOMAINS):
        raise FetchError("skip_to_wayback", url)

    if matches_any(host, PREFER_BROWSER_IMPERSONATION) and HAVE_CURL_CFFI:
        return fetch_with_curl_cffi(url, timeout, verify=verify)

    try:
        return fetch_with_requests(session, url, timeout, verify=verify)
    except FetchError as e:
        if HAVE_CURL_CFFI and e.reason in (
            "http_401", "http_403", "http_406", "http_429", "http_421",
            "empty_body", "ssl", "not_html",
        ):
            return fetch_with_curl_cffi(url, timeout, verify=verify)
        raise


def collect_one(session, record, timeout, allow_wayback=True):
    url = record["url"]
    host = host_of(url)
    domain_wait(url)
    effective_timeout = LONG_TIMEOUT if matches_any(host, SLOW_DOMAINS) else timeout

    last_err = None
    final_url, html = None, None
    try:
        final_url, html = fetch_html(session, url, effective_timeout)
    except FetchError as e:
        last_err = e

    if html is not None:
        ext = extract_cascade(html, final_url or url)
        if ext:
            return _build_record(record, final_url or url, ext)
        last_err = FetchError("extract_failed", "all extractors failed")

    if matches_any(host, TRY_AMP):
        for amp_url in amp_variants(url):
            try:
                domain_wait(amp_url)
                furl, html = fetch_html(session, amp_url, effective_timeout)
                ext = extract_cascade(html, furl)
                if ext:
                    return _build_record(record, furl, ext)
            except FetchError:
                continue

    if allow_wayback and last_err and last_err.reason != "not_html":
        ts = guess_wayback_timestamp(url, record)
        try:
            domain_wait("https://web.archive.org/")
            wb_url, wb_html = fetch_wayback(url, near=ts)
            ext = extract_cascade(wb_html, url)
            if ext:
                rec = _build_record(record, url, ext)
                rec["wayback_url"] = wb_url
                return rec
        except FetchError:
            pass

    raise last_err or FetchError("unknown")


def _build_record(record, final_url, extracted):
    return {
        "id": record["id"],
        "url": final_url,
        "time": extracted.get("date") or record.get("pub_date"),
        "title": clean_text(extracted.get("title") or record.get("title") or ""),
        "text": clean_text(extracted["text"]),
    }


# ==================================================================
# I/O helpers
# ==================================================================

def read_jsonl(path):
    """Tolerant JSONL reader — UTF-8 with errors ignored."""
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def load_done_ids(path: Path) -> set:
    if not path.exists():
        return set()
    return {rec["id"] for rec in read_jsonl(path) if rec.get("id")}


def find_targets(root, cluster_id, subtopic_id):
    if cluster_id:
        candidates = sorted({*root.glob(f"{cluster_id}_*"), *root.glob(cluster_id)})
        cluster_dirs = [d for d in candidates if d.is_dir()]
    else:
        cluster_dirs = [d for d in root.iterdir()
                        if d.is_dir() and (d / "subtopics").is_dir()]
    targets = []
    for cdir in cluster_dirs:
        st_root = cdir / "subtopics"
        if not st_root.is_dir():
            continue
        for std in sorted(st_root.iterdir()):
            if not std.is_dir():
                continue
            if subtopic_id and not (
                std.name == subtopic_id or std.name.startswith(subtopic_id)
            ):
                continue
            if (std / "article_urls.jsonl").exists():
                targets.append(std)
    return targets


# ==================================================================
# Per-subtopic
# ==================================================================

def process_subtopic(subdir, *, workers, resume, timeout, allow_wayback):
    urls_path = subdir / "article_urls.jsonl"
    out_path  = subdir / "articles.jsonl"

    records = [r for r in read_jsonl(urls_path) if r.get("url") and r.get("id")]
    done    = load_done_ids(out_path) if resume else set()
    pending = [r for r in records if r["id"] not in done]

    logging.info("[%s] %d urls | %d done | %d to fetch",
                 subdir.name, len(records), len(done), len(pending))

    stats = {
        "subtopic": subdir.name,
        "total_urls": len(records),
        "already_done": len(done),
        "attempted": len(pending),
        "succeeded": 0,
        "failed": 0,
        "wayback_rescues": 0,
        "failures_by_reason": Counter(),
        "by_outlet": defaultdict(lambda: {"ok": 0, "fail": 0}),
        "started": time.time(),
        "elapsed": 0.0,
    }
    if not pending:
        return stats

    session = make_requests_session()
    write_lock = Lock()

    # Open in append mode if resuming, write mode otherwise
    mode = "a" if resume else "w"
    with open(out_path, mode, encoding="utf-8") as out_fh:

        def handle(record):
            try:
                result = collect_one(session, record, timeout,
                                     allow_wayback=allow_wayback)
                with write_lock:
                    out_fh.write(json.dumps(result, ensure_ascii=False) + "\n")
                    out_fh.flush()
                return record, result, None
            except FetchError as e:
                return record, None, e
            except Exception as e:
                logging.exception("unexpected for %s", record.get("url"))
                return record, None, FetchError("unexpected", str(e)[:200])

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(handle, r): r for r in pending}
            for i, fut in enumerate(as_completed(futures), 1):
                record, result, err = fut.result()
                outlet = (record.get("outlet")
                          or urlparse(record.get("url", "")).netloc or "?")
                if err is None:
                    stats["succeeded"] += 1
                    stats["by_outlet"][outlet]["ok"] += 1
                    if result and result.get("wayback_url"):
                        stats["wayback_rescues"] += 1
                else:
                    stats["failed"] += 1
                    stats["failures_by_reason"][err.reason] += 1
                    stats["by_outlet"][outlet]["fail"] += 1
                if i % 25 == 0 or i == len(pending):
                    logging.info("[%s] %d/%d  ok=%d fail=%d (wb=%d)",
                                 subdir.name, i, len(pending),
                                 stats["succeeded"], stats["failed"],
                                 stats["wayback_rescues"])

    stats["elapsed"] = time.time() - stats["started"]
    return stats


# ==================================================================
# Reporting
# ==================================================================

def print_report(all_stats):
    if not all_stats:
        return
    tot_urls = sum(s["total_urls"] for s in all_stats)
    tot_skip = sum(s["already_done"] for s in all_stats)
    tot_try  = sum(s["attempted"] for s in all_stats)
    tot_ok   = sum(s["succeeded"] for s in all_stats)
    tot_fail = sum(s["failed"] for s in all_stats)
    tot_wb   = sum(s["wayback_rescues"] for s in all_stats)
    tot_t    = sum(s["elapsed"] for s in all_stats)

    print("\n" + "=" * 64)
    print("COLLECTION REPORT")
    print("=" * 64)
    print(f"curl_cffi available  : {HAVE_CURL_CFFI}")
    print(f"readability available: {HAVE_READABILITY}")
    print(f"Subtopics processed  : {len(all_stats)}")
    print(f"URLs total           : {tot_urls}")
    print(f"  already in output  : {tot_skip}")
    print(f"  attempted now      : {tot_try}")
    print(f"  succeeded          : {tot_ok}")
    print(f"    of which Wayback : {tot_wb}")
    print(f"  failed             : {tot_fail}")
    if tot_try:
        print(f"  success rate       : {100 * tot_ok / tot_try:.1f}%")
        if tot_t:
            print(f"  throughput         : {tot_try / tot_t:.2f} urls/s")
    print(f"Elapsed              : {tot_t:.1f}s")

    fail_reasons = Counter()
    for s in all_stats:
        fail_reasons.update(s["failures_by_reason"])
    if fail_reasons:
        print("\nFailure reasons:")
        for reason, n in fail_reasons.most_common():
            print(f"  {reason:<28} {n}")

    print("\nPer-subtopic:")
    for s in sorted(all_stats, key=lambda x: x["subtopic"]):
        rate = (100 * s["succeeded"] / s["attempted"]) if s["attempted"] else 100.0
        print(f"  {s['subtopic']:<38} ok={s['succeeded']:<5} "
              f"fail={s['failed']:<4} rate={rate:5.1f}%  ({s['elapsed']:.1f}s)")
    print("=" * 64)


# ==================================================================
# Entry point
# ==================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--cluster", type=str)
    ap.add_argument("--subtopic", type=str)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--no-resume", action="store_true",
                    help="don't skip ids already in articles.jsonl (rewrites file)")
    ap.add_argument("--no-wayback", action="store_true",
                    help="disable Wayback Machine fallback")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    setup_logging(args.verbose)

    if not HAVE_CURL_CFFI:
        logging.warning("curl_cffi NOT installed - many 403s will still fail. "
                        "Install with: pip install curl_cffi")
    if not HAVE_READABILITY:
        logging.warning("readability-lxml NOT installed - install with: "
                        "pip install readability-lxml")

    targets = find_targets(args.root, args.cluster, args.subtopic)
    if not targets:
        logging.error("No subtopics matched (root=%s, cluster=%s, subtopic=%s)",
                      args.root, args.cluster, args.subtopic)
        return 2

    logging.info("Found %d subtopic(s) to process", len(targets))
    all_stats = []
    try:
        for sub in targets:
            try:
                stats = process_subtopic(
                    sub,
                    workers=args.workers,
                    resume=not args.no_resume,
                    timeout=args.timeout,
                    allow_wayback=not args.no_wayback,
                )
                all_stats.append(stats)
            except Exception:
                logging.exception("subtopic %s crashed", sub.name)
    except KeyboardInterrupt:
        logging.warning("Interrupted; partial output kept on disk.")

    print_report(all_stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())