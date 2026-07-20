# RAW MAT 測試與驗收規格

- 文件狀態：Draft
- 日期：2026-07-17
- 適用版本：`vlookup-web.html` SHA-256 `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3`

# RAW MAT Test and Acceptance Specification

- Document status: Draft
- Date: 2026-07-17
- Applicable version: `vlookup-web.html` SHA-256 `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3`

## 1. 測試資料政策

- 真實 `1.xlsx`、`2.xlsx`、`3.xlsx` 只可在本機以唯讀方式做最終驗收。
- 真實資料、擷取內容與匯出結果不得提交 Git、放進 handoff、prompt、issue 或截圖。
- 自動測試與跨人員協作使用小型去識別 fixture；fixture 必須保留必要資料型別、重複鍵與日期邊界，但不得保留真實料號、供應商或描述。
- 每次驗收以 SHA-256 確認來源版本，避免同名檔案被替換後仍沿用舊結論。

## 1. Test-data policy

- The real `1.xlsx`, `2.xlsx`, and `3.xlsx` files may be used only for read-only local acceptance testing.
- Real data, extracted contents, exports, screenshots, and row samples must not enter Git, handoffs, prompts, or issues.
- Automated and shared testing uses small sanitized fixtures that preserve necessary data types, duplicate-key behavior, and date boundaries without real materials, suppliers, or descriptions.
- Every acceptance run verifies the source SHA-256 values so conclusions are not reused after same-named files are replaced.

## 2. 現況基準測試

### 設定

- Excel 1 lookup：`so`
- Excel 2 lookup：`SD Document`
- Excel 2 return：`SD Document`、`Material`
- Result lookup：`Excel 2 Material`
- Excel 3 lookup：`Material`
- Excel 3 return：`Material Full Description(EN)`、`PO Quantity`
- Date column：`cutting`
- From：`2026-07-01`
- To：`2026-07-31`
- Case sensitive：off
- First match only：on

### 預期結果

| 指標 | 預期值 |
|---|---:|
| Excel 1 資料列 | 43 |
| 輸出列 | 17 |
| Excel 2 matched | 17 |
| Excel 3 matched | 17 |
| Date skipped | 26 |

上述結果已用唯讀 workbook 分析重現。尚未在 Phase 1 完成真實瀏覽器端到端操作，因此 UI journey 狀態為 `not tested`。

## 2. Current baseline test

### Configuration

- Excel 1 lookup: `so`
- Excel 2 lookup: `SD Document`
- Excel 2 return: `SD Document`, `Material`
- Result lookup: `Excel 2 Material`
- Excel 3 lookup: `Material`
- Excel 3 return: `Material Full Description(EN)`, `PO Quantity`
- Date column: `cutting`
- From: `2026-07-01`
- To: `2026-07-31`
- Case sensitive: off
- First match only: on

### Expected result

| Metric | Expected value |
|---|---:|
| Excel 1 data rows | 43 |
| Output rows | 17 |
| Excel 2 matched | 17 |
| Excel 3 matched | 17 |
| Date skipped | 26 |

The result was reproduced through read-only workbook analysis. A real browser end-to-end journey was not completed during Phase 1, so UI journey status is `not tested`.

## 3. 去識別功能案例

| ID | 案例 | 預期行為 |
|---|---|---|
| T-001 | 一對一兩段匹配 | 產生一筆 `Matched All` |
| T-002 | Excel 2 無匹配 | 保留 Excel 1；Excel 2/3 欄位空白；正確狀態 |
| T-003 | Excel 2 匹配、Excel 3 無匹配 | 保留前兩段資料；Excel 3 欄位空白 |
| T-004 | 空白 key 在兩側都存在 | 不得互相匹配；記錄 warning |
| T-005 | 大小寫不同 | insensitive 模式匹配；sensitive 模式不匹配 |
| T-006 | Excel 2 重複 key，first-only on | 依來源順序取一筆並顯示候選數警告 |
| T-007 | Excel 3 重複 key，first-only on | 依來源順序取一筆並顯示候選數警告 |
| T-008 | first-only off | 依核准規則展開，且不得以空白重複欄位破壞平面資料完整性 |
| T-009 | From／To 邊界日 | 起訖日均包含 |
| T-010 | From 大於 To | 阻擋執行並顯示錯誤 |
| T-011 | 無效或空白資料日期 | 啟用日期篩選時排除並計數 |
| T-012 | Excel 日期序號含時間 | 正確比較日期並以可讀日期時間輸出 |
| T-013 | 中文、逗號、雙引號、換行 | XLSX/CSV 開啟後內容完整 |
| T-014 | `=`, `+`, `-`, `@` 開頭 | CSV 不得在 Excel 中執行公式 |
| T-015 | 重複欄名 | 輸出欄位可用 stable ID 獨立選取 |
| T-016 | 英文／繁中切換 | 設定、狀態代碼與結果不漂移 |
| T-017 | 任一設定在結果後變更 | 結果立即失效，所有匯出停用 |
| T-018 | 合法 CSV quoted newline | parser 保留為同一 cell／row |
| T-019 | 多工作表 XLSX | 依公開契約讀第一表，或在新增 selector 後讀使用者指定表 |
| T-020 | 不支援或毀損檔案 | 不產生部分錯誤結果；顯示可行處理方式 |

## 3. Sanitized functional cases

| ID | Case | Expected behavior |
|---|---|---|
| T-001 | One-to-one two-stage match | Produce one `Matched All` row |
| T-002 | No Excel 2 match | Preserve Excel 1; leave Excel 2/3 fields blank; use the correct status |
| T-003 | Excel 2 match, no Excel 3 match | Preserve the first two stages; leave Excel 3 fields blank |
| T-004 | Blank key on both sides | Do not match; record a warning |
| T-005 | Different letter case | Match in insensitive mode and not in sensitive mode |
| T-006 | Duplicate Excel 2 key, first-only on | Select source-order first row and show candidate-count warning |
| T-007 | Duplicate Excel 3 key, first-only on | Select source-order first row and show candidate-count warning |
| T-008 | First-only off | Expand per the approved rule without blanking repeated cells in a way that breaks flat-table integrity |
| T-009 | From/To boundary dates | Include both boundary dates |
| T-010 | From later than To | Block execution and display an error |
| T-011 | Invalid or blank source date | Exclude and count when the date filter is active |
| T-012 | Excel serial date with time | Compare dates correctly and export readable date/time values |
| T-013 | Chinese, comma, quote, and newline | Preserve content after opening XLSX/CSV |
| T-014 | Values beginning with `=`, `+`, `-`, `@` | CSV must not execute a formula in Excel |
| T-015 | Duplicate headers | Stable IDs allow independent output selection |
| T-016 | English/Traditional Chinese switch | Settings, status codes, and results do not drift |
| T-017 | Any result-affecting setting changes | Invalidate results immediately and disable every export action |
| T-018 | Valid CSV quoted newline | Preserve the field and row correctly |
| T-019 | Multi-sheet XLSX | Read the first sheet per current contract, or the selected sheet after a selector is approved |
| T-020 | Unsupported or damaged file | Do not produce a partial incorrect result; show an actionable error |

## 4. Phase 2 UI 驗收 Journey

1. 開啟本機工具，確認不需網路且沒有非必要外部請求。
2. 上傳三份 sanitized fixture，確認列數與欄位。
3. 設定兩段查找、輸出欄位與日期，建立結果。
4. 檢查 metrics、狀態、預覽與第一／最後一筆。
5. 匯出 XLSX 與 CSV，以 Excel 開啟並核對內容、型別、日期與中文。
6. 返回步驟二依序改變每個設定，確認結果失效與匯出停用。
7. 切換英文／繁中，確認選取與結果不變。
8. 重新執行並確認輸出可追溯到相同設定摘要。

## 4. Phase 2 UI acceptance journey

1. Open the local tool and confirm that it works without network access or unnecessary external requests.
2. Upload the three sanitized fixtures and verify row and column counts.
3. Configure both lookups, output columns, and date range, then build the result.
4. Check metrics, statuses, preview rows, and the first/last result.
5. Export XLSX and CSV, open both in Excel, and reconcile content, types, dates, and Chinese text.
6. Return to Step 2 and change every result-affecting setting in turn; verify invalidation and disabled exports.
7. Switch between English and Traditional Chinese; verify that selection and result state do not change.
8. Rebuild and confirm the export is traceable to the same configuration summary.

## 5. 效能與資源基準

以 43／10,842／25,064 資料列記錄匯入時間、查找時間、預覽時間、峰值記憶體、輸出列數與瀏覽器錯誤。Phase 1 只記錄資料量，不虛構 SLA；Phase 2 第一次量測後由 Paul 與原開發者核准可接受門檻。

## 5. Performance and resource baseline

Using 43, 10,842, and 25,064 data rows, record import time, lookup time, preview time, peak memory, output rows, and browser errors. Phase 1 records dataset size only and does not invent an SLA. Paul and the original developer approve acceptable thresholds after the first Phase 2 measurement.

## 6. 完成判定

- `PASS`：有實際執行證據且符合預期。
- `FAIL`：已執行但結果不符。
- `BLOCKED`：外部權限、業務決策或環境阻擋，且已記錄所缺條件。
- `NOT TESTED`：尚未執行，不得用規格或自述替代。

Phase 2 不得在 RM-001 至 RM-006 任一未通過、真實 17/17/26 基準未重現、或第一筆規則被未授權改變時宣告完成。

## 6. Completion classification

- `PASS`: Executed evidence exists and matches the expectation.
- `FAIL`: The check ran but did not meet the expectation.
- `BLOCKED`: Permission, business decision, or environment prevents execution, and the missing condition is recorded.
- `NOT TESTED`: The check was not executed; specifications or self-reported claims do not substitute for evidence.

Phase 2 must not be declared complete if any of RM-001 through RM-006 fails, the real 17/17/26 baseline is not reproduced, or first-match behavior changes without authorization.
