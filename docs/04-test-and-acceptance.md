# RAW MAT 配發引擎 v3.3 測試與驗收規格 / RAW MAT Allocation Engine v3.3 Test and Acceptance Specification

**狀態 / Status:** 已更新；核心與全量基準通過，互動式瀏覽器點驗待人工完成。/ Updated; core and full-data baseline passed, interactive browser clicking remains manual.<br>
**日期 / Date:** 2026-07-24<br>
**適用版本 / Applies to:** `allocation-web.html` 3.3.0

## 1. 測試資料政策 / Test-data policy

- 真實 20260723 檔只可在本機唯讀驗收，不提交 Git、不放 prompt／handoff／截圖。/ Real 20260723 files are local read-only acceptance data and must not enter Git, prompts, handoffs, or screenshots.
- Handoff 可記 SHA-256、列數與彙總證據，不包含真實資料列。/ Handoffs may record SHA-256, row counts, and aggregate evidence, but not real rows.
- 自動分享使用去識別 fixtures。/ Shared automated testing uses sanitized fixtures.
- 產生的 CSV／XLSX 測試輸出由 `.gitignore` 排除。/ Generated CSV/XLSX output is excluded by `.gitignore`.

## 2. 必要測試矩陣 / Required test matrix

| ID | 中文案例 | English case | 預期 / Expected |
|---|---|---|---|
| A-001 | 0028 母料 MB* | 0028 mother MB* | 計算前整列排除 / Row excluded before calculation |
| A-002 | 0028 子料 MB* | 0028 child MB* | 計算前整列排除 / Row excluded before calculation |
| A-003 | MB 過濾後自我配對 | Self-link after MB filter | 0 |
| A-004 | COOIS 同鍵多列 | Duplicate COOIS key rows | 依 SO+Material+Segment 加總 / Aggregate all rows |
| A-005 | 母料 F+G 覆蓋 | Mother F+G coverage | 不足才展開 / Expand only shortage |
| A-006 | 廠外 pair 單位 | Outside pair units | 先換回母料 OUn 再加總 / Convert to mother OUn before sum |
| A-007 | Rule D 直接子料需求 | Rule D direct child demand | 先扣母料餘量，未覆蓋量才扣子料 MB52 / Mother balance first; uncovered amount uses child MB52 |
| A-008 | 直接需求可歸多母 | Direct demand maps to multiple mothers | 列出全部衝突並確認；確認後按母料 Open Qty 比例拆分，取消則整批停止 / List conflicts and confirm; on confirm split by mother Open Qty; cancel stops run |
| A-009 | 共享子料 | Shared child | 依核准順序共扣同池 / Consume common pool in order |
| A-010 | 220x110 SHT→YD | 220x110 SHT→YD | 2.187227 |
| A-011 | 缺換算／衝突 | Missing/conflicting conversion | 整批停止，不略過 / Stop; never skip |
| A-012 | 19 欄 | 19 columns | 預覽、CSV、XLSX 同值同序 / Same values/order |
| A-013 | child stock | child stock | 固定原始 MB52 總量 / Fixed original MB52 total |
| A-014 | stock available | stock available | 本列前餘量 / Pre-row balance |
| A-015 | Y 正常群組 | Valid Y group | 有母、有正數非 MH04、全部足量才 Y / Mother + positive non-MH04 + fully supplied |
| A-016 | 零需求／純直接／MH04-only | Zero/direct-only/MH04-only | Y 空白 / Blank Y |
| A-017 | 結果失效 | Result invalidation | 清舊結果並停用 CSV/XLSX / Clear results and disable exports |
| A-018 | 語言切換 | Language switch | en/zh 不改資料與選取 / No data or selection drift |
| A-019 | CSV 安全 | CSV safety | UTF-8 BOM、引號／換行、公式字首防護 / BOM, quoting, multiline, formula safety |
| A-020 | XLSX 可用性 | XLSX usability | Excel 可開啟且與 CSV 一致 / Opens in Excel and matches CSV |
| A-021 | 母料完整覆蓋直接需求 | Full mother coverage | H 正確、Q=0、R 不扣 / Correct H, Q=0, R unchanged |
| A-022 | 母料部分覆蓋直接需求 | Partial mother coverage | Q 只等於未覆蓋量 / Q equals uncovered amount only |
| A-023 | 多直接子料共母料池 | Multiple direct children | 依 0028 列序，H 逐列遞減 / 0028 order; H decreases per row |
| A-024 | 母料池跨 SO | Mother pool across SOs | 母料需求與 Rule D 均延續扣減 / Both mother demand and Rule D persist |
| A-025 | 不同母子單位 | Different mother/child units | 覆蓋量與回扣依相同係數 / Coverage and deduction use the same ratio |

## 3. 排序驗收 / Ordering acceptance

必須依序驗證：cutting 升冪 → 同日 Schedule SO 原始列序 → 同 SO COOIS 母料首次列序 → 同母 0028 子料首次列序。<br>
Verify in this exact order: cutting ascending → original Schedule SO row for equal dates → first COOIS mother row within SO → first 0028 child row within mother.

多個母料共用一個子料時，所有列必須依此順序共扣同一 Material + Segment 池。<br>
When mothers share a child, all rows consume the same Material + Segment pool in this order.

## 4. 錨點與全量基準 / Anchor and full-data baseline

錨點 `10189518 / MN090134761 / MA020147549`：<br>
Anchor `10189518 / MN090134761 / MA020147549`:

| Metric | Expected |
|---|---:|
| F mother plant stock | 0 |
| G mother stock outside | 1.996708 |
| mother Open Quantity | 1.5 |
| H mother stock before row | 0.496708 |
| N demand qty | 0.02 |
| Q provided from child MB52 | 0 |
| R child remaining | 43.046 |
| shortage | false |

20260723 全量：<br>
20260723 full dataset:

| Metric | Expected |
|---|---:|
| Schedule rows | 246 |
| COOIS rows | 129,993 |
| ZRMM0028 rows | 16,307 |
| MB52 rows | 7,050 |
| Output rows | 3,505 |
| Mothers | 499 |
| Shortage rows | 71 |
| MB rows excluded | 389 |
| Relationships removed | 45 |
| Dual identities | 0 |

## 5. 自動驗證 / Automated verification

```powershell
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py `
  --real-data 20260723 `
  --conversion-config config/conversion-rules.v1.json
python .ai/handoffs/20260724-raw-mat-allocation-handoff/verify_ui_contract_v3_3.py
```

13 組 Python fixtures、New_0722 smoke、20260723 全量與 v3.3 靜態 UI／匯出契約於 2026-07-24 通過。<br>
Thirteen Python fixtures, New_0722 smoke, the 20260723 full dataset, and the v3.3 static UI/export contract passed on 2026-07-24.

## 6. 人工 UI 驗收 / Manual UI acceptance

1. 開啟本機 `allocation-web.html`，確認版本 3.3.0 與 English／繁體中文兩種語言。/ Open the local app and confirm version 3.3.0 and the two languages.
2. 用 Sample data 執行，確認預覽 19 欄。/ Run Sample data and confirm 19 preview columns.
3. 切換語言，確認資料、映射、篩選與列數不變。/ Switch language and confirm data, mappings, filters, and row counts remain unchanged.
4. 修改一般換算、尺寸換算與任一輸入，確認結果清除且兩個匯出鍵停用。/ Change conversions and an input; confirm results clear and both exports disable.
5. 匯出 CSV／XLSX，以 Excel 開啟後逐欄比較。/ Export CSV/XLSX, open in Excel, and compare column by column.
6. 用真實 20260723 檔重跑，只記錄彙總，不保存或提交輸出。/ Rerun real 20260723 files, recording only aggregates and committing no output.

本次自動瀏覽器因 `file://` URL 安全政策未執行，狀態為 `NOT TESTED`，不得誤標 PASS。<br>
Automated interactive browser testing was not run because `file://` was blocked by URL policy. Its status is `NOT TESTED`, not PASS.

## 7. 效能記錄 / Performance recording

至少記錄四份輸入列數、總執行時間、瀏覽器記憶體異常、輸出列數與短缺列。未取得重複量測前不設定臆測 SLA。<br>
Record input row counts, total runtime, browser memory failures, output rows, and shortages. Do not invent an SLA before repeat measurements exist.

## 8. 完成判定 / Completion classification

- `PASS`：已執行且有證據符合預期。/ Executed with evidence matching expectations.
- `FAIL`：已執行但不符。/ Executed but did not match.
- `BLOCKED`：外部條件阻擋且已記錄缺口。/ Blocked by an external condition with the gap documented.
- `NOT TESTED`：尚未執行，不得以規格或靜態檢查替代。/ Not executed; specifications or static checks do not substitute.

正式簽核前，A-001 至 A-025、錨點、全量基準與人工 UI 六步都必須有明確狀態。<br>
Before final sign-off, A-001 through A-025, the anchor, full baseline, and six manual UI steps must each have an explicit status.