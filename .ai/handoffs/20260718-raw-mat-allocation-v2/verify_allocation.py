#!/usr/bin/env python3
"""Sanitized fixture verifier for RAW MAT allocation engine v2.2.

Proves: MAX(K), greedy, 1:1 when units match, M→YD conversion,
SHT size-suffix conversion (Excel3.J), R vs H pre-check block,
missing conversion block, Y flag, 10-column order.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

COL_E1_SO = 0
COL_E1_CUTTING = 1
COL_E2_SO = 1
COL_E2_MOTHER = 5
COL_E2_QTY = 16
COL_E2_UNIT_R = 17
COL_E3_MOTHER = 4
COL_E3_UNIT_H = 7
COL_E3_CHILD = 8
COL_E3_DESC_J = 9
COL_E3_STOCK = 10
COL_E3_UNIT_M = 12

OUTPUT_HEADERS = [
    "cutting",
    "so",
    "mother material",
    "mother unit (2.R)",
    "child material",
    "child unit (3.M)",
    "demand qty",
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
    ("220x110cm", "M"): 2.0,
    ("220x110cm", "YD"): 2.187227,
    ("220x110cm", "SHT"): 1.0,
    ("200x110cm", "M"): 2.2,
    ("200x110cm", "YD"): 2.405949,
    ("200x110cm", "SHT"): 1.0,
}

SIZE_SUFFIX_RE = re.compile(r"(\d+)\s*[x×*]\s*(\d+)\s*cm\s*$", re.I)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _norm(value: object) -> str:
    return str(value or "").strip()


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


def _child_unit(unit: str) -> str:
    u = unit.upper()
    if u == "Y":
        return "YD"
    return u


def _extract_size_suffix(text: object) -> str:
    match = SIZE_SUFFIX_RE.search(_norm(text))
    if not match:
        return ""
    return f"{match.group(1)}x{match.group(2)}cm".lower()


def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return [], []
    headers = rows[0]
    width = max(len(headers), max((len(r) for r in rows), default=0))
    headers = headers + [""] * (width - len(headers))
    data = [r + [""] * (width - len(r)) for r in rows[1:]]
    return headers, data


def _ratio(
    mother_unit: str,
    child_unit: str,
    rules: dict[tuple[str, str], float],
    size_rules: dict[tuple[str, str], float],
    size_suffix: str,
) -> tuple[float | None, str]:
    m = mother_unit.upper()
    c = _child_unit(child_unit)
    if not m or not c:
        return None, "blank-unit"
    if m == c:
        return 1.0, "ok"
    if m == "SHT":
        if not size_suffix:
            return None, "missing-suffix"
        hit = size_rules.get((size_suffix, c))
        if hit is None:
            return None, "missing-size-rule"
        return hit, "ok"
    hit = rules.get((m, c))
    if hit is None:
        return None, "missing"
    return hit, "ok"


def allocate(
    excel1_rows: list[list[str]],
    excel2_rows: list[list[str]],
    excel3_rows: list[list[str]],
    rules: dict[tuple[str, str], float] | None = None,
    size_rules: dict[tuple[str, str], float] | None = None,
) -> tuple[list[str], list[list[str]], dict[str, float], list[str]]:
    """Return headers, rows, stock_max, errors (empty if ok)."""
    rules = rules if rules is not None else dict(DEFAULT_RULES)
    size_rules = size_rules if size_rules is not None else dict(DEFAULT_SIZE_RULES)
    errors: list[str] = []

    r_by_mother: dict[str, set[str]] = {}
    for idx, row in enumerate(excel2_rows):
        mother = _norm(row[COL_E2_MOTHER] if len(row) > COL_E2_MOTHER else "")
        if not mother:
            continue
        unit_r = _norm(row[COL_E2_UNIT_R] if len(row) > COL_E2_UNIT_R else "").upper()
        r_by_mother.setdefault(mother, set()).add(unit_r)

    h_by_mother: dict[str, set[str]] = {}
    for row in excel3_rows:
        mother = _norm(row[COL_E3_MOTHER] if len(row) > COL_E3_MOTHER else "")
        if not mother:
            continue
        unit_h = _norm(row[COL_E3_UNIT_H] if len(row) > COL_E3_UNIT_H else "").upper()
        h_by_mother.setdefault(mother, set()).add(unit_h)

    for mother in set(r_by_mother) | set(h_by_mother):
        if mother not in r_by_mother or mother not in h_by_mother:
            continue
        r_units = r_by_mother[mother]
        h_units = h_by_mother[mother]
        if len(r_units) != 1 or len(h_units) != 1 or next(iter(r_units)) != next(iter(h_units)):
            errors.append(f"R/H mismatch for {mother}: R={sorted(r_units)} H={sorted(h_units)}")
    if errors:
        return OUTPUT_HEADERS, [], {}, errors

    schedule: dict[str, str] = {}
    for row in excel1_rows:
        so = _norm(row[COL_E1_SO] if len(row) > COL_E1_SO else "")
        if not so:
            continue
        cutting = _norm(row[COL_E1_CUTTING] if len(row) > COL_E1_CUTTING else "")
        prev = schedule.get(so)
        if prev is None or cutting < prev:
            schedule[so] = cutting

    mothers_in_bom: set[str] = set()
    children_by_mother: dict[str, set[str]] = {}
    stock_max: dict[str, float] = {}
    mother_unit_r: dict[str, str] = {}
    child_unit_m: dict[tuple[str, str], str] = {}
    child_suffix: dict[tuple[str, str], str] = {}

    for mother, units in r_by_mother.items():
        mother_unit_r[mother] = next(iter(units))

    for row in excel3_rows:
        mother = _norm(row[COL_E3_MOTHER] if len(row) > COL_E3_MOTHER else "")
        child = _norm(row[COL_E3_CHILD] if len(row) > COL_E3_CHILD else "")
        if not mother:
            continue
        mothers_in_bom.add(mother)
        if not child:
            continue
        children_by_mother.setdefault(mother, set()).add(child)
        pair = (mother, child)
        suffix = _extract_size_suffix(row[COL_E3_DESC_J] if len(row) > COL_E3_DESC_J else "")
        if suffix:
            prev_suffix = child_suffix.get(pair)
            if prev_suffix and prev_suffix != suffix:
                errors.append(
                    f"Conflicting 3.J size suffix for {mother}/{child}: {prev_suffix} vs {suffix}"
                )
            else:
                child_suffix[pair] = suffix
        unit_m = _norm(row[COL_E3_UNIT_M] if len(row) > COL_E3_UNIT_M else "").upper()
        child_unit_m[pair] = unit_m
        k = _num(row[COL_E3_STOCK] if len(row) > COL_E3_STOCK else 0)
        prev_k = stock_max.get(child)
        if prev_k is None or k > prev_k:
            stock_max[child] = k

    if errors:
        return OUTPUT_HEADERS, [], stock_max, errors

    demand: dict[tuple[str, str], float] = {}
    for row in excel2_rows:
        so = _norm(row[COL_E2_SO] if len(row) > COL_E2_SO else "")
        mother = _norm(row[COL_E2_MOTHER] if len(row) > COL_E2_MOTHER else "")
        if not so or not mother or mother not in mothers_in_bom:
            continue
        qty = _num(row[COL_E2_QTY] if len(row) > COL_E2_QTY else 0)
        key = (so, mother)
        demand[key] = demand.get(key, 0.0) + qty

    expanded: list[dict[str, object]] = []
    for (so, mother), qty in demand.items():
        cutting = schedule.get(so, "")
        m_unit = mother_unit_r.get(mother, "")
        for child in sorted(children_by_mother.get(mother, set())):
            c_unit = child_unit_m.get((mother, child), "")
            suffix = child_suffix.get((mother, child), "")
            ratio, reason = _ratio(m_unit, c_unit, rules, size_rules, suffix)
            if ratio is None:
                if reason == "missing-suffix":
                    errors.append(f"Missing size suffix in Excel3.J for {mother}/{child}")
                elif reason == "missing-size-rule":
                    errors.append(
                        f"Missing size conversion {suffix or '?'}->{c_unit} for {mother}/{child}"
                    )
                else:
                    errors.append(f"Missing conversion {m_unit}->{c_unit} for {mother}/{child}")
                continue
            expanded.append(
                {
                    "cutting": cutting,
                    "so": so,
                    "mother": mother,
                    "mother_unit": m_unit,
                    "child": child,
                    "child_unit": c_unit,
                    "need": qty * ratio,
                }
            )
    if errors:
        return OUTPUT_HEADERS, [], stock_max, errors

    expanded.sort(
        key=lambda item: (
            str(item["cutting"]),
            str(item["so"]),
            str(item["mother"]),
            str(item["child"]),
        )
    )

    remaining = dict(stock_max)
    out_rows: list[list[str]] = []
    for item in expanded:
        child = str(item["child"])
        need = float(item["need"])
        rem = remaining.get(child, 0.0)
        provide = min(need, rem)
        next_rem = rem - provide
        remaining[child] = next_rem
        out_rows.append(
            [
                str(item["cutting"]),
                str(item["so"]),
                str(item["mother"]),
                str(item["mother_unit"]),
                child,
                str(item["child_unit"]),
                _fmt(need),
                _fmt(provide),
                _fmt(next_rem),
                "Y" if provide > 0 else "",
            ]
        )
    return OUTPUT_HEADERS, out_rows, stock_max, []


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _pad_row(cells: list[str], width: int) -> list[str]:
    return cells + [""] * (width - len(cells))


def main() -> int:
    _, e1 = _read_csv(FIXTURE_DIR / "excel1.csv")
    _, e2 = _read_csv(FIXTURE_DIR / "excel2.csv")
    _, e3 = _read_csv(FIXTURE_DIR / "excel3.csv")

    headers, rows, stock_max, errors = allocate(e1, e2, e3)
    print("=== RAW MAT allocation v2.2 fixture verify ===")
    print(f"output_rows={len(rows)}")
    print(f"stock_max={stock_max}")
    for row in rows:
        print(",".join(row))
    _assert(not errors, f"unexpected errors: {errors}")
    _assert(headers == OUTPUT_HEADERS, f"column order mismatch: {headers}")
    _assert(stock_max.get("CHILD-1") == 20.0, "MAX(K) CHILD-1")
    _assert(stock_max.get("CHILD-2") == 12.0, "MAX(K) CHILD-2")

    so_a_rows = [r for r in rows if r[1] == "SO-A"]
    _assert(all(r[0] == "2026-07-01" for r in so_a_rows), "earliest cutting")
    _assert(all(r[2] != "MOTHER-X" for r in rows), "MOTHER-X filtered")

    expected = [
        ["2026-07-01", "SO-A", "MOTHER-1", "M", "CHILD-1", "M", "10", "10", "10", "Y"],
        ["2026-07-01", "SO-A", "MOTHER-1", "M", "CHILD-2", "M", "10", "10", "2", "Y"],
        ["2026-07-03", "SO-B", "MOTHER-1", "M", "CHILD-1", "M", "5", "5", "5", "Y"],
        ["2026-07-03", "SO-B", "MOTHER-1", "M", "CHILD-2", "M", "5", "2", "0", "Y"],
    ]
    _assert(rows == expected, f"row mismatch:\n got={rows}\n exp={expected}")

    # Conversion M→YD
    e3_yd = [row[:] for row in e3]
    for row in e3_yd:
        if len(row) > COL_E3_UNIT_M:
            row[COL_E3_UNIT_M] = "YD"
    _, rows_yd, _, err_yd = allocate(e1, e2, e3_yd)
    _assert(not err_yd, f"conversion errors: {err_yd}")
    so_a_c1 = next(r for r in rows_yd if r[1] == "SO-A" and r[4] == "CHILD-1")
    _assert(so_a_c1[5] == "YD", "child unit YD")
    _assert(abs(float(so_a_c1[6]) - 10 * 1.0936) < 1e-6, f"converted demand expected 10.936 got {so_a_c1[6]}")

    # Missing conversion blocks
    _, _, _, err_missing = allocate(e1, e2, e3_yd, rules={})
    _assert(any("Missing conversion" in e for e in err_missing), "missing conversion should block")

    # R vs H mismatch blocks
    e3_bad = [row[:] for row in e3]
    for row in e3_bad:
        if len(row) > COL_E3_UNIT_H:
            row[COL_E3_UNIT_H] = "YD"
    _, _, _, err_rh = allocate(e1, e2, e3_bad)
    _assert(any("R/H mismatch" in e for e in err_rh), "R/H mismatch should block")

    # SHT size-suffix conversion (Excel3.J)
    e1_sht = [["SO-S", "2026-07-05"]]
    e2_sht = [_pad_row(["", "SO-S", "", "", "", "MOTHER-SHT", "", "", "", "", "", "", "", "", "", "", "3", "SHT"], 18)]
    e3_sht = [
        _pad_row(["", "", "", "", "MOTHER-SHT", "", "", "SHT", "CHILD-Y", "CHILD YD 110x200cm", "10", "", "YD"], 13),
        _pad_row(["", "", "", "", "MOTHER-SHT", "", "", "SHT", "CHILD-S", "CHILD SHT 110x200cm", "5", "", "SHT"], 13),
    ]
    _, rows_sht, _, err_sht = allocate(e1_sht, e2_sht, e3_sht)
    _assert(not err_sht, f"SHT conversion errors: {err_sht}")
    row_y = next(r for r in rows_sht if r[4] == "CHILD-Y")
    row_s = next(r for r in rows_sht if r[4] == "CHILD-S")
    _assert(abs(float(row_y[6]) - 3 * 2.187227) < 1e-6, f"SHT→YD demand got {row_y[6]}")
    _assert(row_s[6] == "3", f"SHT→SHT should stay 1:1 got {row_s[6]}")

    # Missing size rule blocks
    _, _, _, err_size = allocate(e1_sht, e2_sht, e3_sht, size_rules={})
    _assert(any("Missing size conversion" in e for e in err_size), "missing size conversion should block")

    # Conflicting suffixes on same mother+child block
    e3_conflict = [
        _pad_row(["", "", "", "", "MOTHER-SHT", "", "", "SHT", "CHILD-Y", "A 110x200cm", "10", "", "YD"], 13),
        _pad_row(["", "", "", "", "MOTHER-SHT", "", "", "SHT", "CHILD-Y", "B 220x110cm", "5", "", "YD"], 13),
    ]
    _, _, _, err_conflict = allocate(e1_sht, e2_sht, e3_conflict)
    _assert(any("Conflicting 3.J size suffix" in e for e in err_conflict), "suffix conflict should block")

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
