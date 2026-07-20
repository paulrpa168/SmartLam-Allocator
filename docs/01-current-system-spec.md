# RAW MAT 現況系統規格

- 文件狀態：Draft — 等待 Paul 與原開發者共同核准
- 版本：1.0
- 日期：2026-07-17
- 實作基準：`vlookup-web.html` SHA-256 `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3`

# RAW MAT Current System Specification

- Document status: Draft — pending joint approval by Paul and the original developer
- Version: 1.0
- Date: 2026-07-17
- Implementation baseline: `vlookup-web.html` SHA-256 `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3`

## 1. 問題與使用者

主要使用者是需要從排程、COIS 與 ZRMm 資料中取得指定原料資訊的人員。現有人工操作需要跨三份 Excel 做兩段查找並按 cutting 日期縮小範圍，容易產生欄位選錯、排序依賴或匯出錯誤。

## 1. Problem and users

The primary users need to derive selected raw-material information from schedule, COIS, and ZRMm data. The manual workflow requires two lookups across three workbooks plus a cutting-date filter, which creates risks of incorrect column selection, ordering dependence, and export mistakes.

## 2. 目標與非目標

### 目標

- 在瀏覽器中讀取三份本機檔案，不把檔案內容傳送到外部服務。
- 依明確欄位完成兩段查找、日期篩選、結果預覽與匯出。
- 讓查找規則、輸出欄位、匹配狀態與限制可被人員與 Agent 稽核。

### 非目標

- 本規格不核准多筆匹配的最終業務規則。
- 本階段不修改程式、不建立內網服務、不新增資料庫。
- 本階段不承諾目前 Excel 匯出按鈕可用。

## 2. Goals and non-goals

### Goals

- Read three local files in the browser without transmitting file contents to an external service.
- Perform two explicit lookups, date filtering, result preview, and export.
- Make lookup rules, output columns, match status, and limitations auditable by people and agents.

### Non-goals

- This specification does not approve the final business rule for duplicate matches.
- This phase does not modify the program, create an intranet service, or add a database.
- This phase does not claim that the current Excel export button works.

## 3. 輸入契約

| 輸入 | 目前角色 | 資料列數 | 必要欄位 | 現況限制 |
|---|---|---:|---|---|
| `1.xlsx` | Excel 1 / schedule | 43 | `so`, `cutting` | 只讀第一個工作表；日期由 Excel 序號讀取 |
| `2.xlsx` | Excel 2 / COIS | 10,842 | `SD Document`, `Material` | 只讀第一個工作表；同一 SO 有大量重複列 |
| `3.xlsx` | Excel 3 / ZRMm | 25,064 | `Material`, `Material Full Description(EN)`, `PO Quantity` | 只讀第一個工作表；同一 Material 有重複列 |

支援的檔案副檔名為 `.xlsx`、`.csv`、`.tsv`、`.txt`。程式也允許把表格文字貼入文字區。`.xls` 不在目前支援範圍。

## 3. Input contract

| Input | Current role | Data rows | Required columns | Current limitation |
|---|---|---:|---|---|
| `1.xlsx` | Excel 1 / schedule | 43 | `so`, `cutting` | Reads only the first worksheet; dates are read as Excel serial values |
| `2.xlsx` | Excel 2 / COIS | 10,842 | `SD Document`, `Material` | Reads only the first worksheet; each SO can have many duplicate rows |
| `3.xlsx` | Excel 3 / ZRMm | 25,064 | `Material`, `Material Full Description(EN)`, `PO Quantity` | Reads only the first worksheet; each Material can have duplicate rows |

Supported file extensions are `.xlsx`, `.csv`, `.tsv`, and `.txt`. Users may also paste table text into the text areas. Legacy `.xls` is not currently supported.

## 4. 查找與資料流契約

```text
Excel 1 schedule
  so + cutting
       |
       | so = SD Document
       v
Excel 2 COIS
  SD Document + Material
       |
       | Material = Material
       v
Excel 3 ZRMm
  Material + Material Full Description(EN) + PO Quantity
```

1. 第一段以 Excel 1 `so` 對應 Excel 2 `SD Document`。
2. 第一段從 Excel 2 回傳 `SD Document` 與 `Material`。
3. 第二段以第一段結果的 `Excel 2 Material` 對應 Excel 3 `Material`。
4. 第二段從 Excel 3 回傳 `Material Full Description(EN)` 與 `PO Quantity`。
5. 查找值預設會去除前後空白並轉為小寫；勾選大小寫敏感時不轉小寫。

## 4. Lookup and data-flow contract

1. The first lookup matches Excel 1 `so` to Excel 2 `SD Document`.
2. The first lookup returns `SD Document` and `Material` from Excel 2.
3. The second lookup matches the intermediate `Excel 2 Material` to Excel 3 `Material`.
4. The second lookup returns `Material Full Description(EN)` and `PO Quantity` from Excel 3.
5. Lookup values are trimmed and lowercased by default. Lowercasing is skipped when case-sensitive mode is enabled.

## 5. 多筆匹配規則

程式目前預設勾選「只使用第一個匹配」。第一筆是來源檔案中的列順序，不含額外排序、狀態篩選或業務優先權。基準期間內，COIS 每個被選 SO 有 135–442 筆，ZRMm 的被選 Material 有 13–60 筆，因此結果會受來源排序影響。

此規則是現況相容行為，不代表已核准的正確業務規則。Paul 與原開發者必須共同決定以下其中之一後，才可修改：

- 維持來源第一筆；
- 先依指定欄位排序或條件篩選，再取第一筆；
- 展開全部匹配並定義最大筆數與重複資料處理。

## 5. Duplicate-match rule

The program currently enables “Use first match only” by default. “First” means source-row order; no additional sorting, status filter, or business priority is applied. In the baseline period, each selected COIS SO has 135–442 rows and the selected ZRMm Materials have 13–60 rows, so the result depends on input ordering.

This is compatibility behavior, not an approved business rule. Paul and the original developer must jointly approve one of the following before it is changed:

- Keep the first row in source order;
- Sort or filter by approved business fields before selecting the first row;
- Expand all matches and define row limits and duplicate handling.

## 6. 日期篩選契約

- 日期欄位來源為 Excel 1，基準欄位為 `cutting`。
- From 與 To 均為可選；兩者皆空白時不篩選。
- 篩選包含起始日與結束日。
- 無法解析日期的資料列在啟用日期篩選時被排除。
- `From > To` 必須阻擋執行。
- 現有預覽與 CSV 會保留 Excel 原始日期序號；這是已知缺陷，不是目標格式。

## 6. Date-filter contract

- The date column comes from Excel 1; the baseline column is `cutting`.
- From and To are optional; when both are blank, no date filter is applied.
- Both date boundaries are inclusive.
- Rows with unparseable dates are excluded when date filtering is enabled.
- Execution is blocked when `From > To`.
- The current preview and CSV retain raw Excel date serials. This is a known defect, not the target format.

## 7. 輸出契約

基準輸出欄位依序為：

1. `so`
2. `cutting`
3. `Excel 2 SD Document`
4. `Excel 2 Material`
5. `Excel 3 Material Full Description(EN)`
6. `Excel 3 PO Quantity`
7. `Lookup Status`

目前狀態值為：`Matched All`、`Excel 2 Matched, Excel 3 No Match`、`Excel 2 No Match, Excel 3 Matched`、`No Match`。未來正式介面需提供英文與繁體中文顯示，但儲存或交換格式應使用穩定代碼，避免切換語言改變資料語意。

正式需求是同時支援 XLSX 與 CSV。現況只有 CSV 可觸發；Excel 按鈕永久停用，列為 P1 缺陷。

## 7. Output contract

The baseline output columns, in order, are:

1. `so`
2. `cutting`
3. `Excel 2 SD Document`
4. `Excel 2 Material`
5. `Excel 3 Material Full Description(EN)`
6. `Excel 3 PO Quantity`
7. `Lookup Status`

Current status values are `Matched All`, `Excel 2 Matched, Excel 3 No Match`, `Excel 2 No Match, Excel 3 Matched`, and `No Match`. The future UI must display English and Traditional Chinese, while stored or exchanged status values should use stable codes so language changes do not alter data meaning.

The formal requirement is to support both XLSX and CSV. Only CSV is currently actionable; the Excel button is permanently disabled and is tracked as a P1 defect.

## 8. 基準驗收案例

使用現有三份 Excel、上述欄位與 2026-07-01 至 2026-07-31 的日期範圍，且維持第一筆模式時：

- Excel 1 總資料列：43
- 日期內資料列／輸出列：17
- 日期排除：26
- Excel 2 匹配：17
- Excel 3 匹配：17

這些數字只證明程式可重現現有文件畫面，不代表第一筆規則已通過業務正確性驗證。

## 8. Baseline acceptance case

Using the supplied files, the mappings above, the inclusive range 2026-07-01 through 2026-07-31, and first-match mode:

- Excel 1 data rows: 43
- In-range/output rows: 17
- Date-filtered rows: 26
- Excel 2 matches: 17
- Excel 3 matches: 17

These figures prove that the application reproduces the existing instruction screenshots. They do not prove that first-match behavior is the correct business rule.

## 9. 品質屬性與限制

- 正確性優先於速度與 UI 美觀。
- 真實資料僅能在使用者電腦上使用，直到資料邊界另行核准。
- 原始檔、輸出檔與真實資料不得進 Git 或 Agent handoff。
- 現有自製 XLSX/CSV parser、未使用的 CDN 依賴、缺少測試與缺少結果失效機制均需在後續階段處理。
- 本規格的批准狀態在 Paul 與原開發者共同簽核前保持 Draft。

## 9. Quality attributes and limitations

- Correctness takes priority over speed and UI polish.
- Real data must remain on the user’s computer until the data boundary is separately approved.
- Source files, exports, and real data must not enter Git or agent handoffs.
- The custom XLSX/CSV parser, unused CDN dependency, lack of tests, and missing stale-result invalidation must be addressed in later phases.
- This specification remains Draft until jointly approved by Paul and the original developer.
