# -*- coding: utf-8 -*-
"""One way to read a number typed by a person or found in a file, shared by the suite.

    40000, "40 000", "40 000 FCFA", "5.000" (thousands), "40,000" (thousands), "1.234,56", "1,234.56",
    "0,5", "12,5 %", "0.750"  ->  float
A group of exactly three digits after a single separator is a thousands group ("5.000" = 5000), unless the
number starts with 0 ("0.750" = 0.75). A comma followed by one or two digits is a decimal comma.
"""
import re

_SPACES = "    "


def parse(v):
    """float, or None when there is no number. Never guesses silently: ambiguous forms follow the rule above."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    for ch in _SPACES:
        s = s.replace(ch, "")
    m = re.search(r"-?\d[\d.,]*", s)
    if not m:
        return None
    s = m.group(0).rstrip(".,")
    neg = s.startswith("-")
    s = s.lstrip("-")
    if re.fullmatch(r"\d+", s):
        out = float(s)
    elif re.fullmatch(r"\d{1,3}(,\d{3})+\.\d+", s):        # 1,234.56
        out = float(s.replace(",", ""))
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+,\d+", s):        # 1.234,56
        out = float(s.replace(".", "").replace(",", "."))
    elif re.fullmatch(r"[1-9]\d{0,2}([.,]\d{3})+", s) and len(set(re.findall(r"[.,]", s))) == 1:
        out = float(re.sub(r"[.,]", "", s))                  # 5.000 / 40,000 / 1.234.567
    elif re.fullmatch(r"\d+,\d+", s):                        # 0,5 / 12,75
        out = float(s.replace(",", "."))
    elif re.fullmatch(r"\d+\.\d+", s):
        out = float(s)
    else:
        try:
            out = float(s.replace(",", ""))
        except ValueError:
            return None
    return -out if neg else out


def has_percent(v):
    return isinstance(v, str) and "%" in v
