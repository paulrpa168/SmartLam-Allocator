# 決策記錄

## D1 — 產品方向：配發引擎取代 VLOOKUP

- **決定**：`allocation-web.html` 為現行產品；`vlookup-web.html` 保留但標記 deprecated。
- **理由**：舊兩段查找不是核准業務結果；核准規則是庫存貪婪配發。

## D2 — Excel2 數量欄 = Open Quantity (Q)

- **決定**：需求量固定讀取欄 Q（0-based index 16）。
- **理由**：業務已鎖定；不以其他數量欄替代。

## D3 — 初始庫存 = MAX(K)，非 SUM

- **決定**：同子料多列 Unrestricted 取最大值。
- **理由**：K 為倉儲快照重複列，加總會高估庫存。

## D4 — 母：子需求比 = 1:1

- **決定**：每個 child 的 need = 該 (SO, mother) 加總後的 Q。
- **理由**：已核准；不引入 BOM 用量係數。

## D5 — 輸出欄序：demand 緊接 child 之後

- **決定**：`cutting, so, mother, child, demand, provided, remaining`。
- **理由**：方便同一列比對需求 vs 能提供。

## D6 — 新檔而非改寫舊檔

- **決定**：新建 `allocation-web.html`，不直接改寫 `vlookup-web.html` 核心。
- **理由**：降低回歸風險；舊工具仍可作歷史對照。

## D7 — 介面中文採繁體

- **決定**：v2 新字串使用繁體中文（`zh`）。
- **理由**：專案語言規則；舊檔簡體字串不回溯修改。

## D8 — SHT 末碼來源 = Excel3.F（母料全名）

- **決定**：末碼自 **3.F** `Material Full Description(EN)` 擷取，非 3.J。
- **理由**：業務規格鎖定母材料名稱末幾碼；真實檔 SHT→YD 時 F 有末碼、J 常無。
- **衝突處理**：同母料多列 F 末碼不一致 → 事前錯誤停止。

## D9 — 換算表可編輯，引擎不寫死倍率

- **決定**：`DEFAULT_SIZE_CONVERSION_RULES` 僅作首次／Reset 種子；執行時只讀 `localStorage` 內使用者表。
- **理由**：未來料號規格變更由使用者自行新增／修改，不需改程式。

## D10 — 使用者自行管理換算列

- **決定**：換算表支援新增、改倍率、刪除；**不**自動刪列、**不**因刪列排除子料。
- **理由**：Paul 明確要求「讓使用者自己編輯在減少」= 手動維護比例，非程式自動過濾子料。

## D11 — SHT→SHT 一律 1:1

- **決定**：母單位與子單位皆 SHT 時，`conversionRatio` 直接回傳 1，不查末碼表。
- **理由**：與既有單位相同 1:1 規則一致。

## D12 — 子單位 Y 與 YD 等價

- **決定**：查末碼表時 `normalizeChildUnit("Y")` → `"YD"`。
- **理由**：真實檔子單位可能標 Y 或 YD。

## D13 — Y 欄群組判定（v2.2.1）

- **決定**：同 SO + 母料群組內，僅當**全部**子料 demand>0 且 provided≥demand 時，群組每列標 Y。
- **理由**：Paul 要求「同訂單母材料下子料都有庫存且需求不為 0 才 Y」；任一字料短缺則整組不標。

## D14 — 三語系 + 操作手冊（v2.2.2）

- **決定**：新增 `allocation-manual.html`；主程式頂部連結；語系 EN / 繁中 / 緬甸文（my）；`localStorage` key `rawmat.allocation.lang` 兩頁共用。
- **理由**：現場緬甸籍人員需操作說明；語系切換需一致。

## D15 — 錯誤 modal 可關閉（v2.2.2）

- **決定**：錯誤視窗右上角加 ×，與底部 OK 同呼叫 `hideErrorModal()`。
- **理由**：長錯誤訊息時使用者無法關閉視窗（Paul 回報）。

## D16 — Codex W1/W2 暫不修（v2.2.2 後備註）

- **來源**：`cursor-handoff-v2.2.2-quality-review.md`（Codex PASS + 兩項 Warning）
- **決定**：v2.2.2 **不修正** W1／W2；寫入備註，日後再審是否要修。
- **W1**：`normalizeSizeSuffix` 雙重 match（先去空白嚴格 match，再對 raw `SIZE_SUFFIX_RE`）— 可讀性問題，非功能缺陷。
- **W2**：自訂 suffix 缺 `cm`（如 `"220x110"`）會存成非標準值，與 `extractSizeSuffix`（必帶 `cm`）對不上；執行時仍會 `missing-size-rule` 擋下，但 UI 列看起來像有效規則。若日後要修：需同時收緊 `normalizeSizeSuffix` **與** `loadSizeConversionRules`／`sync` 的 `|| raw` fallback，否則無效。
- **理由（Paul, 2026-07-20）**：現場多半用下拉／種子規則（皆標準格式）；踩到 Custom 缺 `cm` 機率低；PASS 已足夠，暫不值得改動。
- **複審觸發**：使用者回報「換算表有列卻一直缺規則」；或下一版整理 size-suffix API 時一併處理。

## Assumptions（低風險）

1. 固定欄位以 **字母索引** 為準（A=0…），表頭名稱僅供對應摘要顯示。
2. 缺少 Excel1 cutting 的 SO：cutting 顯示空白，排序靠後。
3. 真實檔煙測為可選；缺檔或缺 openpyxl 則 SKIP。
4. 末碼 regex 支援 `x` / `×` / `*` 與大小寫 `cm`。
