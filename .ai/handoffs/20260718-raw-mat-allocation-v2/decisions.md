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

## Assumptions（低風險）

1. 固定欄位以 **字母索引** 為準（A=0…），表頭名稱僅供對應摘要顯示。
2. 缺少 Excel1 cutting 的 SO：cutting 顯示空白，排序靠後。
3. 真實檔煙測為可選；缺檔或缺 openpyxl 則 SKIP。
