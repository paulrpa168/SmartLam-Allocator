# result.md — 測試與交付紀錄（v3.1.3）

**日期：** 2026-07-22  
**App：** `allocation-web.html` `APP_VERSION = 3.1.3`  
**規格：** `docs/07-allocation-v3-spec.md`  
**Git：** `ac618e9` on `origin/master`  
**Diff：** [allocation-v3.1.3.diff](./allocation-v3.1.3.diff)  
**審查交辦：** [brief.md](./brief.md)

---

## 變更檔案

| 路徑 | 類型 |
|------|------|
| `allocation-web.html` | 引擎／表頭／tips → 16 欄；pool=MB52 |
| `allocation-manual.html` | 手冊同步 16 欄／v3.1.3 |
| `README.md` | 狀態與資料流改 16 欄 |
| `docs/07-allocation-v3-spec.md` | 規格：16 欄；廠外不輸出 |
| `verify_allocation_v3.py` | Fixture 索引與期望值對齊 |

---

## 測試指令與輸出

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
PASS test_available_pool_ignores_outside
New_0722 smoke OK: schedule=733 coois=16325 zrmm=16275 mb52=7019 out_rows=465 MA020162253_rows=18

All v3 fixture checks passed.
```

### Fixture 涵義

1. **expand + direct** — 母展開＋子直接；16 headers；pool=MB52；cutting 早者先配；Y  
2. **bom expand L=0** — L=0 仍展開子料  
3. **mother not double-counted** — 雙重身分不產生 blank-mother 自身列；SHT→M  
4. **segment lock blank** — Batch 空白不對 FLT 展開  
5. **MH04 / Y** — MH04 保留列但略過配套；非 MH04 齊套則標 Y  
6. **mother rows sort** — 同 SO 有母列排在直接列前  
7. **FLT/MTF never mixed** — 分池庫存  
8. **available pool ignores outside** — 大廠外不影響 pool=MB52  
9. **New_0722 smoke** — 真實四報表可跑（本機，未進 git）；out_rows=465（16 欄契約後）

---

## 已知限制

1. 驗證為 **Python 镜像**，非瀏覽器執行 JS  
2. **尚未**做 UI 四檔上傳端到端  
3. `docs/01`～`05` 未全面改寫為 v3（以 docs/07 為準）

---

## 建議 Hermes 轉交 Codex 的 prompt（可直接貼）

```text
請以 agency-code-reviewer + reality-checker 審查 RAW MAT Allocation v3.1.3。

工作目錄：D:/0.AI-Agent-Workspace/03_projects/RAW MAT Project
Diff：.ai/handoffs/20260722-raw-mat-allocation-v3/allocation-v3.1.3.diff
Brief：.ai/handoffs/20260722-raw-mat-allocation-v3/brief.md
規格：docs/07-allocation-v3-spec.md
測試證據：同目錄 result.md
Commit：ac618e9

請用繁體中文輸出 Findings（Critical/High/Medium/Low）、測試缺口、Verdict（APPROVE / NEEDS WORK / BLOCK）。
重點：16 欄契約、MB52-only pool、child demand 更名、OUT 索引／Y flag、JS↔Python 镜像一致。
預設 NEEDS WORK，除非有壓倒性證據。
不要修改程式，只做審查。最終寫入 review-hermes-codex.md。
```
