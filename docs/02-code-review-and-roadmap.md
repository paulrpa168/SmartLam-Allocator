# RAW MAT 程式碼審查與優化 Roadmap

- 審查日期：2026-07-17
- 審查範圍：`vlookup-web.html`、三份 Excel 結構、Word/PDF 操作說明
- 程式碼變更：無；本文件只記錄現況與建議

# RAW MAT Code Review and Optimization Roadmap

- Review date: 2026-07-17
- Review scope: `vlookup-web.html`, the structure of the three workbooks, and the Word/PDF instructions
- Program changes: None; this document records the current state and recommendations only

## 1. 總體結論

程式可重現原始操作說明的 17 筆輸出基準，整體資料流也容易理解。結果表使用 `textContent` 寫入使用者資料，外部 script 帶有 SRI，且未發現把 Excel 內容上傳到外部服務的程式碼，這些都是正向基礎。

但目前不適合宣告 production-ready。至少有一項會造成錯誤匯出的 P0 缺陷、數項資料完整性與安全 P1 缺陷，以及尚未核准的第一筆業務規則。正式使用前應先完成階段二修正與雙人核准。

## 1. Overall conclusion

The program reproduces the documented 17-row baseline, and its high-level data flow is understandable. Result cells use `textContent` for user data, the external script includes SRI, and no code was found that uploads workbook contents to an external service. These are positive foundations.

However, the application is not production-ready. It contains at least one P0 stale-export defect, several P1 data-integrity and security issues, and an unapproved first-match business rule. Phase 2 fixes and joint approval are required before formal use.

## 2. 審查發現

### RM-001 — P0：設定變更後仍可匯出舊結果

- 位置：`clearResult()` 約第 1502–1515 行；查找欄位 change listeners 約第 1978–1983 行；輸出 pill click 約第 1336–1347 行；匯出啟用約第 1712–1713 行。
- 重現路徑：先產生結果，返回步驟二，變更查找欄位、回傳欄位、輸出欄位、大小寫或第一筆模式，再直接返回結果頁匯出。
- 影響：畫面設定與實際匯出資料可能不同，使用者無法判斷結果已過期。
- 建議：建立單一 `markResultDirty()`，所有影響結果的控制項都必須呼叫；清除結果、停用 XLSX/CSV/複製並顯示「需重新執行」。

### RM-001 — P0: Old results remain exportable after configuration changes

- Location: `clearResult()` around lines 1502–1515; lookup-column change listeners around lines 1978–1983; output-pill click handling around lines 1336–1347; export enablement around lines 1712–1713.
- Reproduction: Build a result, return to Step 2, change a lookup, return, output, case, or first-match setting, then export without rebuilding.
- Impact: The visible configuration can differ from the exported data, with no stale-result warning.
- Recommendation: Add one `markResultDirty()` path used by every result-affecting control; clear results, disable XLSX/CSV/copy, and display a rebuild-required state.

### RM-002 — P1：Excel 匯出按鈕永遠不可用

- 位置：按鈕約第 818 行；元素註冊約第 1093 行；`clearResult()` 約第 1512 行；事件註冊約第 2003–2005 行。
- 證據：程式會把 `exportXlsx.disabled` 設為 `true`，但沒有任何設為 `false` 的路徑，也沒有 Excel 匯出 click handler。
- 影響：UI 與需求不一致，使用者只能匯出 CSV。
- 建議：實作型別安全的 XLSX exporter、啟用條件與錯誤處理；CSV 保留為交換格式。

### RM-002 — P1: The Excel export button is permanently unavailable

- Location: button around line 818; element registration around line 1093; `clearResult()` around line 1512; event registration around lines 2003–2005.
- Evidence: The code sets `exportXlsx.disabled` to `true`, but never sets it to `false` and registers no Excel-export click handler.
- Impact: The UI contradicts the intended requirement, and users can export only CSV.
- Recommendation: Implement a type-safe XLSX exporter, enablement rules, and error handling while retaining CSV as an interchange format.

### RM-003 — P1／待業務決策：第一筆結果依賴來源排序

- 位置：`firstOnly` 預設勾選約第 750 行；Excel 2 與 Excel 3 取 `[matches[0]]` 約第 1602、1632 行。
- 資料證據：基準 17 個 SO 在 COIS 各有 135–442 筆；使用到的 ZRMm Material 各有 13–60 筆。
- 影響：來源排序改變即可改變材料與 PO 數量，且程式沒有顯示候選筆數或選取原因。
- 建議：在規則核准前維持現況但顯示重複數警告；Paul 與原開發者共同決定第一筆、排序／篩選或全部展開。

### RM-003 — P1 / business decision required: First-match output depends on source order

- Location: `firstOnly` is checked by default around line 750; Excel 2 and Excel 3 use `[matches[0]]` around lines 1602 and 1632.
- Data evidence: Each of the 17 baseline SO values has 135–442 COIS rows; the selected ZRMm Materials have 13–60 rows.
- Impact: Changing source order can change the selected Material and PO Quantity, while the application shows neither candidate counts nor selection rationale.
- Recommendation: Preserve compatibility until approval but show duplicate warnings; Paul and the original developer must jointly choose first row, approved sort/filter, or full expansion.

### RM-004 — P1：空白查找鍵會彼此匹配

- 位置：Excel 2／3 索引建立約第 1551–1562 行；兩段查找約第 1585–1587、1618–1620 行。
- 重現條件：選定欄位在左右兩側都有空白值。
- 影響：空白不再代表缺少資料，而可能產生假匹配；關閉第一筆模式時可能放大為大量結果。
- 建議：索引與查找都略過空白鍵，並以 `No Match` 與警告數量記錄。

### RM-004 — P1: Blank lookup keys match each other

- Location: Excel 2/3 index construction around lines 1551–1562; lookup execution around lines 1585–1587 and 1618–1620.
- Reproduction condition: The selected key column contains blanks on both sides.
- Impact: Blank values can become false matches and may expand into many rows when first-match mode is disabled.
- Recommendation: Exclude blank keys from indexes and lookups, record them as `No Match`, and report a warning count.

### RM-005 — P1：CSV 公式注入與 Excel 編碼風險

- 位置：`csvEscape()` 約第 1799–1802 行；`downloadCsv()` 約第 1808–1820 行。
- 重現條件：儲存格以 `=`, `+`, `-`, `@` 開頭，或含非 ASCII 文字。
- 影響：CSV 在 Excel 開啟時可能執行公式；缺少 BOM 也可能在部分 Windows/Excel 環境中造成中文亂碼。
- 建議：在 CSV 模式中中和危險公式字首、加入 UTF-8 BOM、完整處理引號／換行，並以 XLSX 作為主要人類使用格式。

### RM-005 — P1: CSV formula injection and Excel encoding risk

- Location: `csvEscape()` around lines 1799–1802; `downloadCsv()` around lines 1808–1820.
- Reproduction condition: A cell begins with `=`, `+`, `-`, or `@`, or contains non-ASCII text.
- Impact: Opening the CSV in Excel may execute formulas, and the missing BOM can cause mojibake in some Windows/Excel environments.
- Recommendation: Neutralize dangerous formula prefixes in CSV mode, add a UTF-8 BOM, handle quoting/newlines fully, and use XLSX as the primary human-facing format.

### RM-006 — P1：日期被輸出為 Excel 序號

- 位置：XLSX cell value 解析約第 1866–1884 行；CSV 產生約第 1804–1806 行。
- 證據：操作說明截圖顯示 `46204.441666...` 等原始值，而不是日期時間。
- 影響：輸出難以閱讀，且 CSV 無法保留日期型別與格式。
- 建議：解析工作表 style/number format，或至少對指定日期欄位做可靠轉換；XLSX 輸出應使用真正日期值與明確格式。

### RM-006 — P1: Dates are exported as Excel serial numbers

- Location: XLSX cell parsing around lines 1866–1884; CSV generation around lines 1804–1806.
- Evidence: The instruction screenshot shows raw values such as `46204.441666...` instead of readable date/time values.
- Impact: The output is difficult to read, and CSV cannot preserve date types or formatting.
- Recommendation: Parse worksheet styles/number formats or reliably convert the configured date column; write true date values with explicit formats in XLSX.

### RM-007 — P2：貼上／CSV parser 無法處理引號內換行

- 位置：`parseTextTable()` 約第 1204–1214 行會先按換行切列；`splitLine()` 約第 1172–1193 行只處理單一實體行。
- 影響：含多行材料說明的合法 CSV 會被拆成多筆，且每個 cell 的 `trim()` 可能改變原始內容。
- 建議：採用符合 RFC 4180 的 parser，並明確定義是否保留欄位前後空白。

### RM-007 — P2: The paste/CSV parser cannot handle quoted newlines

- Location: `parseTextTable()` around lines 1204–1214 splits physical lines before `splitLine()` around lines 1172–1193 processes fields.
- Impact: A valid CSV field containing a multiline material description becomes multiple records, and `trim()` can alter source text.
- Recommendation: Use an RFC 4180-compliant parser and define whether leading/trailing field whitespace is preserved.

### RM-008 — P2：輸出欄位識別與語言切換可能漂移

- 位置：`deselectedColumns` 使用顯示文字作 key，約第 1303–1345 行；語言切換會呼叫 `refreshSelectors()`，約第 1109–1118、1966–1970 行。
- 影響：重複欄名無法獨立管理；Excel 2／3 的翻譯前綴變更後，已取消的欄位可能重新被選取，而舊結果仍保留舊語言狀態。
- 建議：使用穩定 ID（source + column index）保存選取；狀態值使用穩定代碼，顯示文字才翻譯。

### RM-008 — P2: Output-column identity and language switching can drift

- Location: `deselectedColumns` uses display text as its key around lines 1303–1345; language changes call `refreshSelectors()` around lines 1109–1118 and 1966–1970.
- Impact: Duplicate headers cannot be controlled independently. Translated Excel 2/3 prefixes can reselect previously deselected fields, while old results retain old-language statuses.
- Recommendation: Persist selection by stable ID (`source + column index`) and store status as a stable code translated only for display.

### RM-009 — P2：匹配計數單位不一致

- 位置：Excel 2 匹配約第 1587–1590 行按 Excel 1 列計數；Excel 3 匹配約第 1620–1632 行按中間列計數。
- 影響：關閉第一筆模式後，兩個 metric 不再可直接比較，Excel 3 數字可能超過來源列數。
- 建議：分別顯示 source rows matched、intermediate rows matched 與 output rows，並在規格中固定分母。

### RM-009 — P2: Match metrics use inconsistent units

- Location: Excel 2 matches are counted per Excel 1 row around lines 1587–1590; Excel 3 matches are counted per intermediate row around lines 1620–1632.
- Impact: When first-match mode is disabled, the metrics are not directly comparable and the Excel 3 count may exceed the source-row count.
- Recommendation: Report source rows matched, intermediate rows matched, and output rows separately, with fixed denominators in the specification.

### RM-010 — P2：離線性與可維護性不足

- 位置：第 841 行載入 CDN SheetJS，但程式未使用 `XLSX` API；全部程式、樣式、解析器與 UI 均放在單一 2,021 行 HTML。
- 影響：本機工具仍有非必要網路依賴；核心邏輯難以單元測試，parser 與 UI 變更容易互相影響。
- 建議：階段三拆出 lookup core、parser、exporter、UI controller，再建置為自包含單檔；移除未使用 CDN。

### RM-010 — P2: Offline and maintainability weaknesses

- Location: line 841 loads CDN SheetJS, but the application does not use the `XLSX` API; all logic, styles, parsers, and UI live in one 2,021-line HTML file.
- Impact: The local tool retains an unnecessary network dependency, and core logic is difficult to unit test safely.
- Recommendation: In Phase 3, extract lookup core, parsers, exporters, and UI controller, then build a self-contained offline file and remove the unused CDN.

## 3. 優化 Roadmap

| 階段 | 優先級 | 內容 | Owner | 完成閘門 |
|---|---|---|---|---|
| Phase 1 | Now | 雙語規格、review、Git、handoff、驗收基準 | Codex | 文件與雜湊可追溯；無程式變更 |
| Phase 2 | P0/P1 | RM-001 至 RM-006、英文＋繁中 UI、XLSX＋CSV | Cursor；Codex 驗證 | Paul＋原開發者核准；所有回歸測試通過 |
| Phase 3 | P2 | 模組化、自包含 build、sanitized fixtures、自動測試 | Cursor／Codex | 固定 build 可重現；測試與真實基準一致 |
| Phase 4 | Business | 多筆匹配規則、內網部署與進階功能 | Paul＋原開發者＋業務 Owner | 業務與資料邊界書面核准 |

## 3. Optimization roadmap

| Phase | Priority | Work | Owner | Completion gate |
|---|---|---|---|---|
| Phase 1 | Now | Bilingual specification, review, Git, handoff, acceptance baseline | Codex | Traceable documents and hashes; no program change |
| Phase 2 | P0/P1 | RM-001 through RM-006, English/Traditional Chinese UI, XLSX and CSV | Cursor; Codex verifies | Joint approval and all regression tests pass |
| Phase 3 | P2 | Modularization, self-contained build, sanitized fixtures, automation | Cursor/Codex | Reproducible build; tests agree with real baseline |
| Phase 4 | Business | Duplicate-match rule, intranet deployment, advanced capabilities | Paul, original developer, and business owner | Written business-rule and data-boundary approval |

## 4. 必要核准點

1. Paul 與原開發者共同核准現況規格與 Phase 2 範圍。
2. 修改第一筆／全部匹配規則前，必須完成業務決策。
3. 新增任何資料傳輸、遠端記錄或內網服務前，必須核准資料邊界。
4. Phase 2 diff 必須由 Codex 驗證並附測試證據，再由 Paul 與原開發者接受。

## 4. Required approval gates

1. Paul and the original developer jointly approve the current specification and Phase 2 scope.
2. A business decision is required before changing first-match or all-match behavior.
3. The data boundary must be approved before any transmission, remote logging, or intranet service is added.
4. Codex must verify the Phase 2 diff with test evidence before Paul and the original developer accept it.
