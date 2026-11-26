"""Apply the evaluated standalone temporal rules to one serialized MIU."""

from bisect import bisect_left
from collections import defaultdict
import re

import ujson

from eis1600._vendor.temporal_entity_recogniser import (
    clean_text,
    normalize_input,
    recognise,
)

REVISION = "3130bb68d06326a4a9e74e29316d4a0ac9efb0a8"
COLUMNS = {
    "Y": "DATE_TAGS",
    "L": "MONTH_TAGS",
    "W": "WEEKDAY_TAGS",
    "C": "CENTURY_TAGS",
}
KINDS = {"Y": "year", "L": "month", "W": "weekday", "C": "century"}
VALUES = {"Y": "year_hijri", "L": "month", "W": "weekday", "C": "century"}
PREFIX = re.compile(r"^(Ü?)([YLWC])(\d+)")
MANUAL = re.compile(r"([YLWC])(\d+?)([A-Za-z])(\d+|None)(I?)([YLWC])(\d+)?$")
FIELDS = {
    "dates",
    "lunar_months",
    "min_date",
    "max_date",
    "dates_headings",
    "temporal_entities",
    "temporal_recogniser",
}


def recognise_segment(
    tokens: list, tags: list, origin: str, offset: int = 0
) -> list[dict]:
    """Return manual and automatic entities with half-open source-token coordinates.

    Origin identifies the body or a heading. Offset is the segment's first row
    in the original frame. Normalization can drop or split words, so keep a
    mapping back to original rows for every word passed to the recogniser.
    """
    words, starts, indices = [], [], []
    manual = defaultdict(list)
    found = []
    pos = 0
    for i, (token, cell) in enumerate(zip(tokens, tags)):
        for tag in cell or ():
            prefix = PREFIX.match(tag)
            if not prefix or prefix[1]:
                continue
            code, width = prefix[2], int(prefix[3])
            spelling = tag
            if tag == "Y10627Y":
                width, spelling = 1, "Y1X0627Y"
            elif tag == "Y1DO491Y":
                spelling = "Y1DNoneY"
            raw = MANUAL.fullmatch(spelling)
            if not raw and code == "Y":
                # Some reviewed sources omit the terminator or repeat the role letter.
                repair = re.fullmatch(
                    r"(Y\d{1,2}[A-Za-z]\d{3,4})(?:[DA]|Y\d+Y|IYO\d+)?", tag
                )
                if repair:
                    raw = MANUAL.fullmatch(repair[1] + "Y")
            end = min(len(tokens), i + width)
            item = {
                "origin": origin,
                "start_token": offset + i,
                "end_token": offset + end,
                "entity_type": KINDS[code],
                "tag": tag,
                "source": "manual",
                "surface": " ".join(t for t in tokens[i:end] if t),
            }
            if raw and raw[1] == raw[6]:
                if tag != "Y10627Y":
                    item["category"] = raw[3].upper()
                if raw[4].isdigit():
                    item[VALUES[code]] = int(raw[4])
                if code == "Y" and raw[7]:
                    item["corrected_year_hijri"] = int(raw[7])
                if raw[5]:
                    item["inexact"] = True
            manual[code].append((i, end, item))
            found.append(item)
        for word in clean_text(normalize_input(token or "")).split():
            starts.append(pos)
            indices.append(i)
            words.append(word)
            pos += len(word) + 1
    if not words:
        return found
    for entity in recognise(" ".join(words), gazetteer=False):
        end_word = bisect_left(starts, entity.end)
        start_word = end_word - entity.length
        if not 0 <= start_word < end_word <= len(words):
            raise ValueError(f"Invalid temporal span for {entity.text!r}")
        i, end = indices[start_word], indices[end_word - 1] + 1
        standalone_tag = entity.to_tag()
        code = standalone_tag[1]
        tag = re.sub(r"^Ü([YLWC])\d+", lambda m: f"Ü{m[1]}{end - i}", standalone_tag)
        item = {
            "origin": origin,
            "start_token": offset + i,
            "end_token": offset + end,
            "entity_type": entity.entity_type,
            "tag": tag,
            "source": "automatic",
            "surface": " ".join(t for t in tokens[i:end] if t),
            "category": entity.category,
            "expression": entity.expression,
        }
        for field in (
            "year_hijri",
            "year_ce",
            "month",
            "day",
            "weekday",
            "century",
            "trigger",
        ):
            value = getattr(entity, field)
            if value is not None:
                item[field] = value
        # A compound year can carry a month/weekday that has its own human annotation.
        first = max(0, bisect_left(starts, entity.expression_start + 1) - 1)
        for component in ("L", "W"):
            for begin, stop, reviewed in manual[component]:
                if indices[first] < stop and begin < end and VALUES[component] in item:
                    item.pop(VALUES[component], None)
                    if VALUES[component] in reviewed:
                        item[VALUES[component]] = reviewed[VALUES[component]]
        overlaps = [m for begin, stop, m in manual[code] if i < stop and begin < end]
        if overlaps:
            # Preserve the literal reviewed tag and its numerical correction. Attach
            # richer automatic components only when the tagged interval agrees.
            for reviewed in overlaps:
                if (reviewed["start_token"], reviewed["end_token"]) == (
                    offset + i,
                    offset + end,
                ):
                    for field in ("day", "month", "weekday", "expression", "trigger"):
                        if field in item and field != VALUES[code]:
                            reviewed.setdefault(field, item[field])
            continue
        found.append(item)
    return sorted(found, key=lambda v: v["start_token"])


def heading_entities(text: str, origin: str) -> list[dict]:
    """Score a raw heading, keeping manual inline tags attached to their words."""
    tokens, tags, pending = [], [], []
    for word in text.split():
        if PREFIX.match(word):
            if not word.startswith("Ü"):
                pending.append(word)
        elif re.fullmatch(r"Ü?[A-Za-z]+[0-9A-Za-z]*", word):
            continue
        else:
            tokens.append(word)
            tags.append(pending)
            pending = []
    return recognise_segment(tokens, tags, origin)


def apply_temporal(row: dict) -> dict:
    """Replace only temporal fields in a package JSON row; repeated application is idempotent."""
    yml = row["yml"]
    df = ujson.loads(row["df"])
    token_map = df["TOKENS"]
    keys = list(token_map)
    tags = df["TAGS_LISTS"]
    for key, cell in tags.items():
        if cell:
            tags[key] = [t for t in cell if not re.match(r"^Ü[YLWC]\d", t)] or None
    for key in FIELDS:
        yml.pop(key, None)
    for col in COLUMNS.values():
        df[col] = dict.fromkeys(keys)
    entities = []
    sections = df["SECTIONS"]
    bounds = [0, *(i for i, k in enumerate(keys) if i and sections[k]), len(keys)]
    for start, end in zip(bounds, bounds[1:]):
        segment = keys[start:end]
        entities.extend(
            recognise_segment(
                [token_map[k] for k in segment],
                [tags[k] for k in segment],
                "body",
                start,
            )
        )
    dates, months = [], []
    for item in entities:
        tag = item["tag"]
        if item["source"] == "automatic":
            key = keys[item["start_token"]]
            col = df[COLUMNS[tag[1]]]
            if col[key] is None:
                col[key] = tag
            elif isinstance(col[key], list):
                col[key].append(tag)
            else:
                col[key] = [col[key], tag]
            tags[key] = (tags[key] or []) + [tag]
        if "year_hijri" in item or "corrected_year_hijri" in item:
            dates.append(
                {
                    "entity": item["surface"],
                    "date": item.get("corrected_year_hijri", item.get("year_hijri")),
                    "cat": item.get("category", "X"),
                }
            )
        if "month" in item:
            months.append(
                {
                    "entity": item.get("expression", item["surface"]),
                    "lunar_month": item["month"],
                    "cat": "X",
                }
            )
    if dates:
        yml["dates"] = dates
        births = [d["date"] for d in dates if d["cat"] == "B"]
        deaths = [d["date"] for d in dates if d["cat"] == "D"]
        ages = [
            a["age"]
            for a in (yml.get("ages") or [])
            if a.get("cat") == "D" and isinstance(a.get("age"), int)
        ]
        interval = max(ages, default=70)
        yml["max_date"] = (
            max(deaths)
            if deaths
            else min(births) + interval
            if births
            else max(d["date"] for d in dates)
        )
        yml["min_date"] = min(births) if births else yml["max_date"] - interval
    if months:
        yml["lunar_months"] = months
    years = []
    for key, text in (yml.get("headings") or {}).items():
        if re.fullmatch(r"h\d+", key) and isinstance(text, str):
            for item in heading_entities(text, key):
                entities.append(item)
                value = item.get("corrected_year_hijri", item.get("year_hijri"))
                if value is not None and value not in years:
                    years.append(value)
    if years:
        yml["dates_headings"] = years
    yml["temporal_recogniser"] = REVISION
    if entities:
        yml["temporal_entities"] = entities
    row["df"] = ujson.dumps(df, ensure_ascii=False)
    return row
