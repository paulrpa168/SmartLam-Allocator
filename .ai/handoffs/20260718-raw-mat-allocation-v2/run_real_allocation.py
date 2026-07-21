#!/usr/bin/env python3
"""Run RAW MAT allocation v2 on real 1.xlsx / 2.xlsx / 3.xlsx."""

from __future__ import annotations

import csv
import re
import sys
import zipfile
import zlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "allocation-result.csv"

COL_E1_SO = 0
COL_E1_CUTTING = 1
COL_E2_SO = 1
COL_E2_MOTHER = 5
COL_E2_QTY = 16
COL_E2_UNIT_R = 17
COL_E3_MOTHER = 4
COL_E3_DESC_F = 5
COL_E3_UNIT_H = 7
COL_E3_CHILD = 8
COL_E3_STOCK = 10
COL_E3_UNIT_M = 12

OUTPUT_HEADERS = [
    "cutting",
    "so",
    "mother",
    "mother_unit_2R",
    "child",
    "child_unit_3M",
    "demand",
    "provided",
    "remaining_after",
    "allocated_Y",
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

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


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
    return str(value)


def format_cell_date(value: object) -> str:
    text = _norm(value)
    if not text:
        return ""
    try:
        serial = float(text.replace(",", ""))
    except ValueError:
        return text
    if not (20000 <= serial < 100000):
        return text
    whole = int(serial)
    fraction = serial - whole
    base = datetime(1899, 12, 30) + timedelta(days=whole)
    y, m, d = base.year, base.month, base.day
    if fraction < 1e-10:
        return f"{y:04d}-{m:02d}-{d:02d}"
    total_seconds = round(fraction * 86400)
    hh = (total_seconds // 3600) % 24
    mm = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}"


def cutting_sort_key(value: object) -> tuple[int, float | str]:
    text = _norm(value)
    try:
        serial = float(text.replace(",", ""))
    except ValueError:
        return (1, format_cell_date(value) or text)
    if 20000 <= serial < 100000:
        return (0, serial)
    return (1, format_cell_date(value) or text)


def _col_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "A")
    letters = match.group(1) if match else "A"
    number = 0
    for letter in letters:
        number = number * 26 + ord(letter) - 64
    return max(number - 1, 0)


def _inflate_raw_deflate(data: bytes) -> bytes:
    return zlib.decompress(data, -zlib.MAX_WBITS)


def read_xlsx_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            ss_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in ss_root.findall(f"{NS}si"):
                parts = [t.text or "" for t in si.findall(f".//{NS}t")]
                shared.append("".join(parts))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        first_sheet = workbook.find(f"{NS}sheets/{NS}sheet")
        if first_sheet is None:
            raise ValueError(f"No worksheet in {path.name}")
        rel_id = first_sheet.get(f"{REL_NS}id")
        rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target: str | None = None
        for rel in rels_root:
            if rel.get("Id") == rel_id:
                target = rel.get("Target")
                break
        if not target:
            raise ValueError(f"Sheet relationship missing in {path.name}")
        sheet_path = target.lstrip("/")
        if not sheet_path.startswith("xl/"):
            sheet_path = f"xl/{sheet_path}"

        sheet_root = ET.fromstring(archive.read(sheet_path))
        rows_out: list[list[str]] = []
        for row_node in sheet_root.findall(f".//{NS}sheetData/{NS}row"):
            cells: dict[int, str] = {}
            for cell in row_node.findall(f"{NS}c"):
                ref = cell.get("r", "A1")
                idx = _col_index(ref)
                cell_type = cell.get("t")
                v_node = cell.find(f"{NS}v")
                val = v_node.text if v_node is not None and v_node.text else ""
                if cell_type == "s" and val.isdigit():
                    val = shared[int(val)] if int(val) < len(shared) else ""
                elif cell_type == "inlineStr":
                    val = "".join(t.text or "" for t in cell.findall(f".//{NS}t"))
                cells[idx] = val
            if not cells:
                continue
            width = max(cells) + 1
            if not any(_norm(cells.get(i, "")) for i in range(width)):
                continue
            rows_out.append([cells.get(i, "") for i in range(width)])

    if not rows_out:
        return []
    return rows_out[1:]  # skip header row


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


def _ratio(mother_unit: str, child_unit: str, size_suffix: str = "") -> float | None:
    m = mother_unit.upper()
    c = _child_unit(child_unit)
    if not m or not c:
        return None
    if m == c:
        return 1.0
    if m == "SHT":
        if not size_suffix:
            return None
        return DEFAULT_SIZE_RULES.get((size_suffix, c))
    return DEFAULT_RULES.get((m, c))


OUT_DEMAND = 6
OUT_PROVIDED = 7
OUT_FLAG_Y = 9


def _apply_group_y_flag(rows: list[list[str]]) -> list[list[str]]:
    groups: dict[str, list[int]] = {}
    for idx, row in enumerate(rows):
        key = f"{_norm(row[1])}\0{_norm(row[2])}"
        groups.setdefault(key, []).append(idx)
    for indices in groups.values():
        qualifies = bool(indices) and all(
            _num(rows[i][OUT_DEMAND]) > 0 and _num(rows[i][OUT_PROVIDED]) >= _num(rows[i][OUT_DEMAND]) - 1e-9
            for i in indices
        )
        for i in indices:
            rows[i][OUT_FLAG_Y] = "Y" if qualifies else ""
    return rows


def allocate(
    excel1_rows: list[list[str]],
    excel2_rows: list[list[str]],
    excel3_rows: list[list[str]],
) -> tuple[list[str], list[list[str]], dict[str, float], list[str]]:
    errors: list[str] = []
    r_by_mother: dict[str, set[str]] = {}
    for row in excel2_rows:
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
        if r_by_mother[mother] != h_by_mother[mother] or len(r_by_mother[mother]) != 1:
            errors.append(
                f"R/H mismatch {mother}: R={sorted(r_by_mother[mother])} H={sorted(h_by_mother[mother])}"
            )
    if errors:
        return OUTPUT_HEADERS, [], {}, errors

    schedule: dict[str, tuple[str, tuple[int, float | str]]] = {}
    for row in excel1_rows:
        so = _norm(row[COL_E1_SO] if len(row) > COL_E1_SO else "")
        if not so:
            continue
        cutting_raw = row[COL_E1_CUTTING] if len(row) > COL_E1_CUTTING else ""
        sort_key = cutting_sort_key(cutting_raw)
        display = format_cell_date(cutting_raw)
        prev = schedule.get(so)
        if prev is None or sort_key < prev[1]:
            schedule[so] = (display, sort_key)

    mothers_in_bom: set[str] = set()
    children_by_mother: dict[str, set[str]] = {}
    stock_max: dict[str, float] = {}
    mother_unit_r: dict[str, str] = {
        mother: next(iter(units)) for mother, units in r_by_mother.items()
    }
    child_unit_m: dict[tuple[str, str], str] = {}
    mother_suffix: dict[str, str] = {}

    for row in excel3_rows:
        mother = _norm(row[COL_E3_MOTHER] if len(row) > COL_E3_MOTHER else "")
        child = _norm(row[COL_E3_CHILD] if len(row) > COL_E3_CHILD else "")
        if not mother:
            continue
        mothers_in_bom.add(mother)
        suffix = _extract_size_suffix(row[COL_E3_DESC_F] if len(row) > COL_E3_DESC_F else "")
        if suffix:
            prev_suffix = mother_suffix.get(mother)
            if prev_suffix and prev_suffix != suffix:
                errors.append(f"Conflicting 3.F size suffix for {mother}: {prev_suffix} vs {suffix}")
            else:
                mother_suffix[mother] = suffix
        if child:
            children_by_mother.setdefault(mother, set()).add(child)
            unit_m = _norm(row[COL_E3_UNIT_M] if len(row) > COL_E3_UNIT_M else "").upper()
            child_unit_m[(mother, child)] = unit_m
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
        sched = schedule.get(so)
        cutting = sched[0] if sched else ""
        cut_sort = sched[1] if sched else (1, "")
        m_unit = mother_unit_r.get(mother, "")
        suffix = mother_suffix.get(mother, "")
        for child in sorted(children_by_mother.get(mother, set())):
            c_unit = child_unit_m.get((mother, child), "")
            ratio = _ratio(m_unit, c_unit, suffix)
            if ratio is None:
                if m_unit.upper() == "SHT":
                    errors.append(
                        f"Missing size conversion {suffix or '?'}->{_child_unit(c_unit)} for {mother}/{child}"
                    )
                else:
                    errors.append(f"Missing conversion {m_unit}->{c_unit} for {mother}/{child}")
                continue
            expanded.append(
                {
                    "cutting": cutting,
                    "cut_sort": cut_sort,
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
            item["cut_sort"],
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
                "",
            ]
        )
    _apply_group_y_flag(out_rows)
    return OUTPUT_HEADERS, out_rows, stock_max, []


def main() -> int:
    files = [ROOT / "1.xlsx", ROOT / "2.xlsx", ROOT / "3.xlsx"]
    for path in files:
        if not path.is_file():
            print(f"Missing input: {path}", file=sys.stderr)
            return 1

    print("Reading Excel files...")
    e1 = read_xlsx_rows(files[0])
    e2 = read_xlsx_rows(files[1])
    e3 = read_xlsx_rows(files[2])
    print(f"excel1_data_rows={len(e1)} excel2_data_rows={len(e2)} excel3_data_rows={len(e3)}")

    headers, rows, stock_max, errors = allocate(e1, e2, e3)
    if errors:
        print("ALLOCATION BLOCKED:", file=sys.stderr)
        for err in errors[:50]:
            print(err, file=sys.stderr)
        if len(errors) > 50:
            print(f"... (+{len(errors) - 50})", file=sys.stderr)
        return 2

    total_demand = sum(_num(r[6]) for r in rows)
    total_provided = sum(_num(r[7]) for r in rows)
    shortage_rows = sum(1 for r in rows if _num(r[7]) < _num(r[6]))
    zero_provide = sum(1 for r in rows if _num(r[7]) == 0 and _num(r[6]) > 0)

    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"output_path={OUT_PATH}")
    print(f"output_rows={len(rows)}")
    print(f"distinct_children_in_stock={len(stock_max)}")
    print(f"total_demand={total_demand}")
    print(f"total_provided={total_provided}")
    print(f"shortage_rows={shortage_rows}")
    print(f"zero_provide_rows={zero_provide}")
    print("--- first 15 rows ---")
    for row in rows[:15]:
        print(",".join(row))
    print("--- last 10 rows ---")
    for row in rows[-10:]:
        print(",".join(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
