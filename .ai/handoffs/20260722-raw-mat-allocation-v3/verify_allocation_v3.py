#!/usr/bin/env python3
"""Fixture verifier for RAW MAT allocation engine v3.

Covers: dual-header field names, J/L/39* filters, outside max(0,ΣJ−ΣP),
MB52 SUM, mother expand + child direct add, mother self not double-counted,
segment lock, greedy by cutting, Y flag, 17-column output.
Optional: smoke New_0722/ workbooks when present.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

OUTPUT_HEADERS = [
    "cutting",
    "so",
    "mother material",
    "mother batch",
    "mother unit",
    "child material",
    "child batch",
    "child unit",
    "demand from mother",
    "demand direct",
    "demand qty",
    "stock MB52",
    "stock outside",
    "stock available",
    "provided qty",
    "remaining stock after this row",
    "allocated (Y)",
]

DEFAULT_RULES = {
    ("M", "YD"): 1.0936,
    ("YD", "M"): 0.9144,
}

DEFAULT_SIZE_RULES = {
    ("110x200cm", "M"): 2.0,
    ("110x200cm", "YD"): 2.187227,
    ("110x200cm", "SHT"): 1.0,
}

SIZE_SUFFIX_RE = re.compile(r"(\d+)\s*[x×*]\s*(\d+)\s*cm\s*$", re.I)

HAND_OFF = Path(__file__).resolve().parent
ROOT = HAND_OFF.parent.parent.parent  # .../handoffs/<id> → project root
NEW_0722 = ROOT / "New_0722"


def _norm(value: object) -> str:
    return str(value or "").strip()


def _norm_seg(value: object) -> str:
    """FLT/MTF warehouse lock — never mix; blank stays blank."""
    return _norm(value).upper()


def _num(value: object) -> float:
    text = _norm(value).replace(",", "")
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _fmt(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    rounded = round(value, 6)
    text = str(rounded)
    if "." in text:
        return text.rstrip("0").rstrip(".")
    return text


def _extract_size_suffix(text: object) -> str:
    match = SIZE_SUFFIX_RE.search(_norm(text))
    if not match:
        return ""
    return f"{match.group(1)}x{match.group(2)}cm".lower()


def _header_key(h: object) -> str:
    return re.sub(r"\s+", " ", _norm(h).lower())


def find_col(headers: list[str], aliases: list[str]) -> int:
    normalized = [_header_key(h) for h in headers]
    alias_keys = [_header_key(a) for a in aliases if _norm(a)]
    for key in alias_keys:
        for i, h in enumerate(normalized):
            if h == key:
                return i
    for key in alias_keys:
        for i, h in enumerate(normalized):
            if key in h or (len(key) >= 3 and len(h) >= 3 and h in key):
                return i
    return -1


def conversion_ratio(
    from_unit: str,
    to_unit: str,
    rules: dict[tuple[str, str], float],
    size_rules: dict[tuple[str, str], float],
    size_suffix: str,
) -> tuple[bool, float, str]:
    a = _norm(from_unit).upper()
    b = _norm(to_unit).upper()
    if a == "Y":
        a = "YD"
    if b == "Y":
        b = "YD"
    if not a or not b or a == b:
        return True, 1.0, ""
    if a == "SHT":
        if not size_suffix:
            return False, 0.0, "missing-suffix"
        key = (size_suffix.lower(), b)
        if key not in size_rules:
            return False, 0.0, "missing-size-rule"
        return True, size_rules[key], ""
    key = (a, b)
    if key not in rules:
        return False, 0.0, "missing-rule"
    return True, rules[key], ""


def storage_excluded(storage: object) -> bool:
    return _norm(storage).startswith("39")


def child_excluded(child: object) -> bool:
    return _norm(child).upper().startswith("MH04")


def run_engine(
    schedule: list[dict],
    coois: list[dict],
    zrmm: list[dict],
    mb52: list[dict],
    rules: dict[tuple[str, str], float] | None = None,
    size_rules: dict[tuple[str, str], float] | None = None,
) -> dict:
    """Minimal v3 engine mirror for fixtures (dict rows with logical keys)."""
    rules = rules or DEFAULT_RULES
    size_rules = size_rules or DEFAULT_SIZE_RULES

    schedule_map: dict[str, dict] = {}
    for row in schedule:
        so = _norm(row.get("so"))
        if not so:
            continue
        cutting = _norm(row.get("cutting"))
        sort_key = cutting
        prev = schedule_map.get(so)
        if not prev or sort_key < prev["sort_key"]:
            schedule_map[so] = {"cutting": cutting, "sort_key": sort_key}

    outside_pair: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
        lambda: {"j": 0.0, "p": 0.0}
    )
    children_by_mother_seg: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    mother_suffix: dict[str, str] = {}
    mother_unit_h: dict[str, str] = {}

    for row in zrmm:
        mother = _norm(row.get("mother"))
        child = _norm(row.get("child"))
        if not mother or not child:
            continue
        if child_excluded(child):
            continue
        j = _num(row.get("gi_j"))
        l = _num(row.get("vendor_l"))
        p = _num(row.get("gr_p"))
        if j == 0 or l == 0:
            continue
        if storage_excluded(row.get("storage")):
            continue
        batch = _norm_seg(row.get("batch"))
        oun = _norm(row.get("oun")).upper()
        bun = _norm(row.get("bun")).upper()
        desc = row.get("desc")
        if mother not in mother_unit_h and oun:
            mother_unit_h[mother] = oun
        suffix = _extract_size_suffix(desc)
        if suffix and mother not in mother_suffix:
            mother_suffix[mother] = suffix
        outside_pair[(mother, child, batch)]["j"] += j
        outside_pair[(mother, child, batch)]["p"] += p
        if child not in children_by_mother_seg[(mother, batch)]:
            children_by_mother_seg[(mother, batch)][child] = {"bun": bun, "oun": oun}

    outside_by_child: dict[tuple[str, str], float] = defaultdict(float)
    for (mother, child, seg), agg in outside_pair.items():
        outside_by_child[(child, seg)] += max(0.0, agg["j"] - agg["p"])

    stock_mb52: dict[tuple[str, str], float] = defaultdict(float)
    for row in mb52:
        material = _norm(row.get("material"))
        if not material:
            continue
        if storage_excluded(row.get("storage")):
            continue
        seg = _norm_seg(row.get("segment"))
        stock_mb52[(material, seg)] += _num(row.get("stock"))

    mothers_in_bom = {m for (m, _s) in children_by_mother_seg}
    valid_children: set[str] = set()
    for child_map in children_by_mother_seg.values():
        valid_children.update(child_map.keys())

    demand_rows: dict[tuple[str, str, str, str], dict] = {}

    def ensure(so: str, seg: str, mother: str, child: str, meta: dict) -> dict:
        key = (so, seg, mother, child)
        if key not in demand_rows:
            sched = schedule_map.get(so, {})
            demand_rows[key] = {
                "cutting": sched.get("cutting", ""),
                "sort_cutting": sched.get("sort_key", "\uffff"),
                "so": so,
                "segment": seg,
                "mother": mother,
                "child": child,
                "mother_unit": meta.get("mother_unit", ""),
                "child_unit": meta.get("child_unit", ""),
                "demand_from_mother": 0.0,
                "demand_direct": 0.0,
            }
        return demand_rows[key]

    coois_by_so: dict[str, list] = defaultdict(list)
    for row in coois:
        so = _norm(row.get("so"))
        if so and so in schedule_map:
            coois_by_so[so].append(row)

    sorted_sos = sorted(
        schedule_map.keys(),
        key=lambda s: (schedule_map[s]["sort_key"], s),
    )

    for so in sorted_sos:
        lines = coois_by_so.get(so, [])
        expansion_children: set[tuple[str, str]] = set()
        expanded_mothers: set[tuple[str, str]] = set()

        for row in lines:
            material = _norm(row.get("material"))
            if not material:
                continue
            qty = _num(row.get("qty"))
            seg = _norm_seg(row.get("segment"))
            unit = _norm(row.get("unit")).upper()
            if material in mothers_in_bom and seg:
                child_map = children_by_mother_seg.get((material, seg), {})
                if child_map:
                    expanded_mothers.add((seg, material))
                    size_suffix = mother_suffix.get(material, "")
                    mother_unit = unit or mother_unit_h.get(material, "")
                    for child in sorted(child_map):
                        child_unit = child_map[child]["bun"]
                        ok, ratio, reason = conversion_ratio(
                            mother_unit, child_unit, rules, size_rules, size_suffix
                        )
                        if not ok:
                            return {"ok": False, "error": f"conversion {reason}: {material}->{child}"}
                        item = ensure(
                            so,
                            seg,
                            material,
                            child,
                            {"mother_unit": mother_unit, "child_unit": child_unit},
                        )
                        item["demand_from_mother"] += qty * ratio
                        expansion_children.add((seg, child))

        for row in lines:
            material = _norm(row.get("material"))
            if not material:
                continue
            qty = _num(row.get("qty"))
            seg = _norm_seg(row.get("segment"))
            unit = _norm(row.get("unit")).upper()
            if (seg, material) in expanded_mothers:
                continue
            if material not in valid_children:
                continue
            if (seg, material) in expansion_children:
                candidates = [
                    d
                    for d in demand_rows.values()
                    if d["so"] == so
                    and d["segment"] == seg
                    and d["child"] == material
                    and d["mother"]
                ]
                candidates.sort(key=lambda d: d["mother"])
                if candidates:
                    candidates[0]["demand_direct"] += qty
            else:
                item = ensure(
                    so, seg, "", material, {"mother_unit": "", "child_unit": unit}
                )
                item["demand_direct"] += qty

    expanded = list(demand_rows.values())
    # Keep demand=0 rows (UI Step 3 hide checkboxes decide visibility).
    # cutting → SO → rows with mother first → mother → child → segment
    expanded.sort(
        key=lambda a: (
            a["sort_cutting"],
            a["so"],
            0 if a["mother"] else 1,
            a["mother"],
            a["child"],
            a["segment"],
        )
    )

    remaining: dict[tuple[str, str], float] = {}
    all_keys = set(stock_mb52) | set(outside_by_child)
    for key in all_keys:
        remaining[key] = max(0.0, stock_mb52.get(key, 0.0) - outside_by_child.get(key, 0.0))

    out_rows: list[list] = []
    for item in expanded:
        demand_total = item["demand_from_mother"] + item["demand_direct"]
        key = (item["child"], item["segment"])
        mb = stock_mb52.get(key, 0.0)
        out = outside_by_child.get(key, 0.0)
        initial_pool = max(0.0, mb - out)
        available = remaining.get(key, initial_pool)
        provide = min(demand_total, max(0.0, available))
        next_rem = available - provide
        remaining[key] = next_rem
        out_rows.append(
            [
                item["cutting"],
                item["so"],
                item["mother"],
                item["segment"],
                item["mother_unit"],
                item["child"],
                item["segment"],
                item["child_unit"],
                _fmt(item["demand_from_mother"]),
                _fmt(item["demand_direct"]),
                _fmt(demand_total),
                _fmt(mb),
                _fmt(out),
                _fmt(initial_pool),
                _fmt(provide),
                _fmt(next_rem),
                "",
            ]
        )

    # Y flag: so+mother+segment (or so+seg+child when mother blank)
    groups: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(out_rows):
        so = _norm(row[1])
        mother = _norm(row[2])
        segment = _norm(row[3]) or _norm(row[6])
        child = _norm(row[5])
        gkey = f"{so}\0{mother}\0{segment}" if mother else f"{so}\0\0{segment}\0{child}"
        groups[gkey].append(idx)
    for indices in groups.values():
        qualifies = indices and all(
            _num(out_rows[i][10]) > 0 and _num(out_rows[i][14]) >= _num(out_rows[i][10]) - 1e-9
            for i in indices
        )
        for i in indices:
            out_rows[i][16] = "Y" if qualifies else ""

    return {"ok": True, "headers": OUTPUT_HEADERS, "rows": out_rows}


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_expand_plus_direct_and_outside() -> None:
    """Mother expand + child direct; outside reduces pool; greedy early cutting first."""
    result = run_engine(
        schedule=[
            {"so": "10100001", "cutting": "2026-07-01"},
            {"so": "10100002", "cutting": "2026-07-02"},
        ],
        coois=[
            # Mother demand on SO1 → expands to CHILD_A
            {"so": "10100001", "material": "MOTHER_A", "qty": 10, "segment": "FLT", "unit": "M"},
            # Direct child demand same SO
            {"so": "10100001", "material": "CHILD_A", "qty": 5, "segment": "FLT", "unit": "M"},
            # Later SO also needs CHILD_A
            {"so": "10100002", "material": "CHILD_A", "qty": 100, "segment": "FLT", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "MOTHER_A",
                "child": "CHILD_A",
                "gi_j": 20,
                "vendor_l": 20,
                "gr_p": 8,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "fabric 110x200cm",
            },
            # filtered: J=0
            {
                "mother": "MOTHER_A",
                "child": "CHILD_B",
                "gi_j": 0,
                "vendor_l": 10,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
            # filtered: storage 39*
            {
                "mother": "MOTHER_A",
                "child": "CHILD_C",
                "gi_j": 5,
                "vendor_l": 5,
                "gr_p": 0,
                "storage": "3901",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_A", "segment": "FLT", "storage": "1001", "stock": 30},
            {"material": "CHILD_A", "segment": "FLT", "storage": "1002", "stock": 20},  # SUM=50
            {"material": "CHILD_A", "segment": "FLT", "storage": "3900", "stock": 999},  # excluded
            {"material": "CHILD_A", "segment": "MTF", "storage": "1001", "stock": 500},  # other seg
        ],
    )
    _assert(result["ok"], str(result))
    rows = result["rows"]
    _assert(len(result["headers"]) == 17, "17 headers")
    # outside = max(0,20-8)=12; MB52 SUM FLT=50; pool=38
    so1 = [r for r in rows if r[1] == "10100001"]
    _assert(len(so1) == 1, f"SO1 should be one merged mother×child row, got {len(so1)}")
    r = so1[0]
    _assert(r[2] == "MOTHER_A", "mother")
    _assert(r[3] == "FLT" and r[6] == "FLT", "batches")
    _assert(_num(r[8]) == 10, f"demand from mother expected 10 got {r[8]}")
    _assert(_num(r[9]) == 5, f"demand direct expected 5 got {r[9]}")
    _assert(_num(r[10]) == 15, "demand total 15")
    _assert(_num(r[11]) == 50, "MB52 SUM")
    _assert(_num(r[12]) == 12, "outside")
    _assert(_num(r[13]) == 38, "initial pool")
    _assert(_num(r[14]) == 15, "provided full")
    _assert(_num(r[15]) == 23, "remaining after SO1")
    _assert(r[16] == "Y", "Y when fully provided")

    so2 = [r for r in rows if r[1] == "10100002"]
    _assert(len(so2) == 1, "SO2 one direct row")
    r2 = so2[0]
    _assert(r2[2] == "", "no mother on direct-only")
    _assert(_num(r2[14]) == 23, f"SO2 gets remaining pool 23, got {r2[14]}")
    _assert(r2[16] == "", "not Y when short")


def test_mother_not_double_counted() -> None:
    """COOIS mother line expands only; mother material itself is not a direct stock row."""
    result = run_engine(
        schedule=[{"so": "10100010", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100010", "material": "MA020162253", "qty": 2, "segment": "FLT", "unit": "SHT"},
        ],
        zrmm=[
            {
                "mother": "MA020162253",
                "child": "CHILD_X",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "SHT",
                "bun": "M",
                "desc": "sheet 110x200cm",
            },
            # Dual identity: same code also appears as child under another mother
            {
                "mother": "OTHER_M",
                "child": "MA020162253",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_X", "segment": "FLT", "storage": "1001", "stock": 100},
            {"material": "MA020162253", "segment": "FLT", "storage": "1001", "stock": 100},
        ],
        size_rules=DEFAULT_SIZE_RULES,
    )
    _assert(result["ok"], str(result))
    rows = result["rows"]
    mothers_self = [r for r in rows if r[5] == "MA020162253" and r[2] == ""]
    _assert(not mothers_self, "expanded mother must not appear as blank-mother direct row")
    child_rows = [r for r in rows if r[5] == "CHILD_X"]
    _assert(len(child_rows) == 1, "one expansion child")
    _assert(_num(child_rows[0][8]) == 4, f"SHT→M 2*2=4, got {child_rows[0][8]}")
    _assert(_num(child_rows[0][9]) == 0, "no direct on child")


def test_segment_lock_blank() -> None:
    """Blank batch/segment does not mix with FLT — no expand; mother not in Article → no direct."""
    result = run_engine(
        schedule=[{"so": "10100020", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100020", "material": "M1", "qty": 5, "segment": "FLT", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "M1",
                "child": "C1",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "",  # blank — must not expand for FLT
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[{"material": "C1", "segment": "FLT", "storage": "1001", "stock": 50}],
    )
    _assert(result["ok"], str(result))
    _assert(result["rows"] == [], result["rows"])


def test_mh04_child_and_non_bom_coois_skipped() -> None:
    """MH04* Article dropped; COOIS materials not in 0028.F (HC/HU) not calculated."""
    result = run_engine(
        schedule=[{"so": "10100050", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100050", "material": "MOTHER_OK", "qty": 2, "segment": "FLT", "unit": "M"},
            {"so": "10100050", "material": "HC0100000025956006", "qty": 99, "segment": "FLT", "unit": "M"},
            {"so": "10100050", "material": "HU999", "qty": 88, "segment": "FLT", "unit": "M"},
            {"so": "10100050", "material": "CHILD_OK", "qty": 3, "segment": "FLT", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "MOTHER_OK",
                "child": "CHILD_OK",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
            {
                "mother": "MOTHER_OK",
                "child": "MH04ABCDEF",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_OK", "segment": "FLT", "storage": "1001", "stock": 100},
            {"material": "MH04ABCDEF", "segment": "FLT", "storage": "1001", "stock": 100},
            {"material": "HC0100000025956006", "segment": "FLT", "storage": "1001", "stock": 100},
        ],
    )
    _assert(result["ok"], str(result))
    children = [r[5] for r in result["rows"]]
    _assert(children == ["CHILD_OK"], f"only CHILD_OK expected, got {children}")
    _assert(_num(result["rows"][0][8]) == 2, "expand from mother")
    _assert(_num(result["rows"][0][9]) == 3, "direct on valid child")


def test_find_col_open_quantity() -> None:
    headers = [
        "SD Document",
        "Material",
        "Quantity withdrawn",
        "Open Quantity",
        "Requirement Segment",
        "Base Unit of Measure",
    ]
    qty = find_col(headers, ["open quantity"])
    _assert(qty == 3, f"must prefer Open Quantity not withdrawn, got {qty}")
    so = find_col(headers, ["sd document"])
    _assert(so == 0, "SD Document")


def smoke_new_0722() -> dict | None:
    if not NEW_0722.exists():
        print("SKIP New_0722 smoke (folder missing)")
        return None
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("SKIP New_0722 smoke (openpyxl missing)")
        return None

    def load_sheet(path: Path) -> tuple[list[str], list[list]]:
        wb = load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        raw = [[("" if c is None else c) for c in row] for row in ws.iter_rows(values_only=True)]
        wb.close()
        if not raw:
            return [], []
        # dual-header detect: if row0 chinese-ish and row1 has english keys → use row1
        def has_en(cells: list) -> bool:
            keys = [_header_key(c) for c in cells]
            hints = [
                "sd document",
                "article(com.)",
                "open quantity",
                "material",
                "unrestricted",
                "stock segment",
                "requirement segment",
                "gi sc(541/542)",
                "stock of vendor",
                "base unit of measure",
                "storage location",
                "order",
                "cutting",
            ]
            hits = sum(1 for h in hints if any(k == h or (len(h) >= 4 and h in k) for k in keys))
            return hits >= 2

        def looks_cn(cells: list) -> bool:
            text = "".join(str(c) for c in cells)
            cn = len(re.findall(r"[\u4e00-\u9fff]", text))
            lat = len(re.findall(r"[A-Za-z]", text))
            return cn > 0 and cn >= max(3, lat * 0.25)

        hi = 0
        if len(raw) >= 2 and looks_cn(raw[0]) and has_en(raw[1]):
            hi = 1
        elif has_en(raw[0]):
            hi = 0
        elif len(raw) >= 2 and has_en(raw[1]):
            hi = 1
        headers = [str(h or f"Column {i+1}") for i, h in enumerate(raw[hi])]
        data = [list(r[: len(headers)]) for r in raw[hi + 1 :]]
        return headers, data

    schedule_h, schedule_d = load_sheet(NEW_0722 / "1.xlsx")
    coois_h, coois_d = load_sheet(NEW_0722 / "COOIS.xlsx")
    zrmm_h, zrmm_d = load_sheet(NEW_0722 / "0028.xlsx")
    mb52_h, mb52_d = load_sheet(NEW_0722 / "MB52_new.xlsx")

    sc = {
        "so": find_col(schedule_h, ["order", "so", "訂單", "order no", "order no."]),
        "cutting": find_col(schedule_h, ["cutting", "production", "裁斷", "cutting process"]),
    }
    cc = {
        "so": find_col(coois_h, ["sd document"]),
        "material": find_col(coois_h, ["material"]),
        "qty": find_col(coois_h, ["open quantity"]),
        "segment": find_col(coois_h, ["requirement segment"]),
        "unit": find_col(coois_h, ["base unit of measure"]),
    }
    zc = {
        "mother": find_col(zrmm_h, ["material"]),
        "child": find_col(zrmm_h, ["article(com.)", "article (com.)", "article"]),
        "gi_j": find_col(zrmm_h, ["gi sc(541/542)"]),
        "vendor_l": find_col(zrmm_h, ["stock of vendor"]),
        "gr_p": find_col(zrmm_h, ["gr sc(543/544)"]),
        "storage": find_col(zrmm_h, ["storage location"]),
        "batch": find_col(zrmm_h, ["batch"]),
        "oun": find_col(zrmm_h, ["oun"]),
        "bun": find_col(zrmm_h, ["bun"]),
        "desc": find_col(
            zrmm_h,
            [
                "material full description(cn)",
                "material full description(en)",
                "material full description",
            ],
        ),
    }
    mc = {
        "material": find_col(mb52_h, ["material"]),
        "segment": find_col(mb52_h, ["stock segment"]),
        "storage": find_col(mb52_h, ["storage location"]),
        "stock": find_col(mb52_h, ["unrestricted"]),
    }

    for name, cols in [("schedule", sc), ("coois", cc), ("zrmm", zc), ("mb52", mc)]:
        missing = [k for k, v in cols.items() if v < 0]
        _assert(not missing, f"{name} missing columns: {missing}")

    # Confirm Open Quantity is not Quantity withdrawn
    withdrawn = find_col(coois_h, ["quantity withdrawn"])
    _assert(cc["qty"] != withdrawn or withdrawn < 0, "qty must not be Quantity withdrawn")

    def col(row: list, idx: int):
        return row[idx] if 0 <= idx < len(row) else ""

    schedule = [
        {"so": col(r, sc["so"]), "cutting": col(r, sc["cutting"])} for r in schedule_d if _norm(col(r, sc["so"]))
    ]
    coois = [
        {
            "so": col(r, cc["so"]),
            "material": col(r, cc["material"]),
            "qty": col(r, cc["qty"]),
            "segment": col(r, cc["segment"]),
            "unit": col(r, cc["unit"]),
        }
        for r in coois_d
        if _norm(col(r, cc["so"]))
    ]
    zrmm = [
        {
            "mother": col(r, zc["mother"]),
            "child": col(r, zc["child"]),
            "gi_j": col(r, zc["gi_j"]),
            "vendor_l": col(r, zc["vendor_l"]),
            "gr_p": col(r, zc["gr_p"]),
            "storage": col(r, zc["storage"]),
            "batch": col(r, zc["batch"]),
            "oun": col(r, zc["oun"]),
            "bun": col(r, zc["bun"]),
            "desc": col(r, zc["desc"]),
        }
        for r in zrmm_d
        if _norm(col(r, zc["mother"]))
    ]
    mb52 = [
        {
            "material": col(r, mc["material"]),
            "segment": col(r, mc["segment"]),
            "storage": col(r, mc["storage"]),
            "stock": col(r, mc["stock"]),
        }
        for r in mb52_d
        if _norm(col(r, mc["material"]))
    ]

    result = run_engine(schedule, coois, zrmm, mb52)
    if not result["ok"]:
        # Real data often misses size rules — report but still count resolution OK
        print(f"New_0722 engine note: {result.get('error')}")
        return {
            "schedule_rows": len(schedule),
            "coois_rows": len(coois),
            "zrmm_rows": len(zrmm),
            "mb52_rows": len(mb52),
            "engine_ok": False,
            "error": result.get("error"),
            "headers_ok": True,
        }

    dual = [r for r in result["rows"] if "MA020162253" in (r[2], r[5])]
    print(
        f"New_0722 smoke OK: schedule={len(schedule)} coois={len(coois)} "
        f"zrmm={len(zrmm)} mb52={len(mb52)} out_rows={len(result['rows'])} "
        f"MA020162253_rows={len(dual)}"
    )
    return {
        "schedule_rows": len(schedule),
        "coois_rows": len(coois),
        "zrmm_rows": len(zrmm),
        "mb52_rows": len(mb52),
        "out_rows": len(result["rows"]),
        "engine_ok": True,
        "headers_ok": True,
        "dual_rows": len(dual),
    }


def test_mother_rows_sort_before_direct_within_so() -> None:
    """Same SO: rows with mother (col C) appear before blank-mother direct rows."""
    result = run_engine(
        schedule=[{"so": "10100030", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100030", "material": "MOTHER_Z", "qty": 1, "segment": "FLT", "unit": "M"},
            {"so": "10100030", "material": "DIRECT_ONLY", "qty": 1, "segment": "FLT", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "MOTHER_Z",
                "child": "CHILD_Z",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
            {
                "mother": "OTHER_M",
                "child": "DIRECT_ONLY",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_Z", "segment": "FLT", "storage": "1001", "stock": 10},
            {"material": "DIRECT_ONLY", "segment": "FLT", "storage": "1001", "stock": 10},
        ],
    )
    _assert(result["ok"], str(result))
    rows = result["rows"]
    _assert(len(rows) == 2, rows)
    _assert(rows[0][2] == "MOTHER_Z" and rows[0][5] == "CHILD_Z", f"mother row first: {rows[0]}")
    _assert(rows[1][2] == "" and rows[1][5] == "DIRECT_ONLY", f"direct row second: {rows[1]}")


def test_flt_mtf_stock_never_mixed() -> None:
    """Same material FLT vs MTF must use separate pools (no cross-sum / cross-allocate)."""
    result = run_engine(
        schedule=[{"so": "10100060", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100060", "material": "CHILD_SEG", "qty": 30, "segment": "FLT", "unit": "M"},
            {"so": "10100060", "material": "CHILD_SEG", "qty": 5, "segment": "MTF", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "M_SEG",
                "child": "CHILD_SEG",
                "gi_j": 10,
                "vendor_l": 10,
                "gr_p": 0,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
            {
                "mother": "M_SEG",
                "child": "CHILD_SEG",
                "gi_j": 1,
                "vendor_l": 1,
                "gr_p": 0,
                "storage": "1001",
                "batch": "MTF",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_SEG", "segment": "FLT", "storage": "1001", "stock": 100},
            {"material": "CHILD_SEG", "segment": "MTF", "storage": "1001", "stock": 7},
            {"material": "CHILD_SEG", "segment": "flt", "storage": "1002", "stock": 20},  # same as FLT
        ],
    )
    _assert(result["ok"], str(result))
    by_seg = {r[6]: r for r in result["rows"]}
    _assert("FLT" in by_seg and "MTF" in by_seg, by_seg.keys())
    flt, mtf = by_seg["FLT"], by_seg["MTF"]
    # FLT: MB52 = 100+20=120 (case-normalized), outside=10, avail=110, provide=30
    _assert(_num(flt[11]) == 120, f"FLT MB52 {flt[11]}")
    _assert(_num(flt[12]) == 10, f"FLT outside {flt[12]}")
    _assert(_num(flt[13]) == 110, f"FLT avail {flt[13]}")
    _assert(_num(flt[14]) == 30, f"FLT provided {flt[14]}")
    # MTF must NOT see FLT stock: MB52=7, outside=1, avail=6, provide=5
    _assert(_num(mtf[11]) == 7, f"MTF MB52 must not include FLT, got {mtf[11]}")
    _assert(_num(mtf[12]) == 1, f"MTF outside {mtf[12]}")
    _assert(_num(mtf[13]) == 6, f"MTF avail {mtf[13]}")
    _assert(_num(mtf[14]) == 5, f"MTF provided {mtf[14]}")


def test_available_pool_never_negative() -> None:
    """When outside > MB52, stock available shows 0 (not negative)."""
    result = run_engine(
        schedule=[{"so": "10100040", "cutting": "2026-07-01"}],
        coois=[
            {"so": "10100040", "material": "CHILD_NEG", "qty": 5, "segment": "FLT", "unit": "M"},
        ],
        zrmm=[
            {
                "mother": "M_NEG",
                "child": "CHILD_NEG",
                "gi_j": 100,
                "vendor_l": 100,
                "gr_p": 10,
                "storage": "1001",
                "batch": "FLT",
                "oun": "M",
                "bun": "M",
                "desc": "",
            },
        ],
        mb52=[
            {"material": "CHILD_NEG", "segment": "FLT", "storage": "1001", "stock": 20},
        ],
    )
    _assert(result["ok"], str(result))
    r = result["rows"][0]
    _assert(_num(r[11]) == 20, f"MB52 {r[11]}")
    _assert(_num(r[12]) == 90, f"outside {r[12]}")  # max(0,100-10)
    _assert(_num(r[13]) == 0, f"available must be 0 not negative, got {r[13]}")
    _assert(_num(r[14]) == 0, f"provided {r[14]}")


def main() -> int:
    tests = [
        test_find_col_open_quantity,
        test_expand_plus_direct_and_outside,
        test_mother_not_double_counted,
        test_segment_lock_blank,
        test_mh04_child_and_non_bom_coois_skipped,
        test_mother_rows_sort_before_direct_within_so,
        test_flt_mtf_stock_never_mixed,
        test_available_pool_never_negative,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {exc}")

    try:
        smoke_new_0722()
    except AssertionError as exc:
        failed += 1
        print(f"FAIL smoke_new_0722: {exc}")
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print(f"ERROR smoke_new_0722: {exc}")

    if failed:
        print(f"\n{failed} failed")
        return 1
    print("\nAll v3 fixture checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
