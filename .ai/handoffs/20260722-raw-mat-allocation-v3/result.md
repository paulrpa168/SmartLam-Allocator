# result.md — 測試與交付紀錄（v3.1.4）

**日期：** 2026-07-23  
**App：** `allocation-web.html` `APP_VERSION = 3.1.4`  
**規格：** `docs/07-allocation-v3-spec.md`  
**Base commit：** `3ccdadd`（工作樹未 commit）  
**Diff：** [allocation-v3.1.4.diff](./allocation-v3.1.4.diff)  
**Brief：** [brief.md](./brief.md)

---

## 變更檔案

| 路徑 | 說明 |
|------|------|
| `allocation-web.html` | 18 欄；母廠內／廠外顯示；outside 聚合恢復 |
| `verify_allocation_v3.py` | 镜像 + 新 fixture + 索引 |
| `docs/07` / `allocation-manual.html` / `README.md` | 規格與手冊同步 |

---

## 測試

```text
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
```

```text
PASS test_find_col_open_quantity
PASS test_expand_plus_direct_and_outside
PASS test_bom_expand_when_vendor_stock_l_is_zero
PASS test_mother_not_double_counted
PASS test_segment_lock_blank
PASS test_mh04_kept_but_ignored_for_y_kit
PASS test_mother_rows_sort_before_direct_within_so
PASS test_flt_mtf_stock_never_mixed
PASS test_mother_outside_clamps_negative_pair
PASS test_available_pool_ignores_outside
New_0722 smoke OK: schedule=733 coois=16325 zrmm=16275 mb52=7019 out_rows=465

All v3 fixture checks passed.
```

---

## 建議 Hermes → Codex prompt

```text
請以 agency-code-reviewer + reality-checker 審查 RAW MAT Allocation v3.1.4（未 commit 工作樹）。

工作目錄：D:/0.AI-Agent-Workspace/03_projects/RAW MAT Project
Diff：.ai/handoffs/20260722-raw-mat-allocation-v3/allocation-v3.1.4.diff
Brief／Result：同目錄
規格：docs/07-allocation-v3-spec.md

重點：18 欄契約、母廠內／廠外僅顯示、MB52 39*、outside max(0,J-P) 加總、不影響子料池、JS↔Python。
Verdict 預設 NEEDS WORK。不要改業務檔。寫入 review-hermes-codex.md。
```
