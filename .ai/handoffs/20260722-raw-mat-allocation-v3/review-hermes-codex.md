# Codex Review — RAW MAT Allocation v3.1.4

**日期：** 2026-07-23  
**版本：** v3.1.4  
**審查方式：** 真實 Codex CLI（非 Hermes 代審）  
**Model：** gpt-5.5（OpenAI Codex CLI v0.140.0-alpha.2）  
**Tokens：** 55,636  
**Base：** `3ccdadd`（工作樹未 commit）  

---

## Verdict：NEEDS WORK

---

## 測試結果（外部獨立執行）

| Test | Status |
|------|--------|
| test_find_col_open_quantity | PASS |
| test_expand_plus_direct_and_outside | PASS |
| test_bom_expand_when_vendor_stock_l_is_zero | PASS |
| test_mother_not_double_counted | PASS |
| test_segment_lock_blank | PASS |
| test_mh04_kept_but_ignored_for_y_kit | PASS |
| test_mother_rows_sort_before_direct_within_so | PASS |
| test_flt_mtf_stock_never_mixed | PASS |
| test_mother_outside_clamps_negative_pair | PASS |
| test_available_pool_ignores_outside | PASS |
| New_0722 smoke (schedule=733, coois=16325, zrmm=16275, mb52=7019, out_rows=465) | OK |

All 10 fixture checks + 1 smoke test passed.

---

## Codex 審查發現

### Critical：0

### High：1
1. **allocation-web.html ZH/MY 表頭亂碼**（files: `allocation-web.html` @ L1572, L1593）  
   - 中文與緬文表頭陣列（`OUTPUT_HEADERS_ZH`、`OUTPUT_HEADERS_MY`）以及 tooltip 文案在 diff 中顯示為 mojibake。  
   - 違反「18 欄輸出契約 EN／ZH／MY 表頭／tips 一致」的交付要求。EN 18 欄語 OUT 索引正確，但中文／緬文模式使用者看到的是不可驗收的輸出。  
   - **影響路徑：** `allocation-web.html`（OUTPUT_HEADERS_ZH @ L1569-1592、OUTPUT_HEADERS_MY @ L1590-1615、tips @ L1877-1896 及 L2047-2066 + L2217-2236）

### Medium：2
2. **New_0722 smoke 缺乏真實資料抽樣斷言**（files: `verify_allocation_v3.py` @ L857）  
   - smoke 測試確認 engine 可跑、列數與部分欄位解析，但未抽樣 2-3 個 mother+segment 做獨立重算（MB52 SUM vs output col 6；outside per-child clamp → 母料加總 vs output col 7）。
3. **JS ↔ Python 鏡像無獨立 oracle**（files: `allocation-web.html` @ L3708, `verify_allocation_v3.py` @ L170）  
   - 兩端高度同構，若同時對規格誤解，現有測試無法抓出。

### Low：1
4. **工作樹未追蹤資料夾含真實 .xlsx**（`20260723/`、`bk_0722/`）  
   - Diff 內未含 .xlsx 或 secret，但 commit 前寬鬆 `git add .` 有誤入風險。

---

## 測試缺口

1. 無獨立計算的真實資料抽樣 — 例如從 MB52/ZRMM 原表人工重算 2-3 個 mother+segment 的 col 6（廠內母庫存）與 col 7（廠外母庫存）後比對輸出。
2. 無瀏覽器端匯出檔檢查 EN/ZH/MY 三種 header 與 tooltip 實際顯示畫面驗證。

---

## 給 Paul 的結論

v3.1.4 核心公式方向正確：
- 廠內母 MB52 SUM 排除 39* ✓
- 廠外母 J/L gate → per-child clamp → 母料+Batch 加總 ✓
- 不影響子料可配發池、provided、Y ✓
- JS ↔ Python 同構無偏差 ✓

但交付品質尚不過線：
1. **先修中文／緬文表頭與 tips 編碼亂碼**（High — 輸出契約失敗）
2. **補真實 New_0722 抽樣重算證據**（Medium — 降低雙端同誤風險）

完成後可進入下一輪 review → 預期 APPROVE。

---

*本報告由 Codex CLI（gpt-5.5）產出 + Hermes 外部執行測試驗證合併。*
