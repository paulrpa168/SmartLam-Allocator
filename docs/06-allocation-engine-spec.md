# 06 — RAW MAT 庫存配發引擎規格（v2）

> 本文件為**已核准業務規則**的產品規格，**取代**舊兩段式 VLOOKUP（`vlookup-web.html`）作為產品方向。  
> This document is the **approved business-rules** product specification and **supersedes** the old two-stage VLOOKUP (`vlookup-web.html`) as the product direction.

**狀態 / Status：** LOCKED（規則鎖定）＋ v2.2 SHT 末碼換算  
**對應程式 / App：** `allocation-web.html` **v2.2.0**  
**日期 / Date：** 2026-07-20

---

## 產品目的 / Product purpose

### 繁體中文

依排程（Excel1）、需求（Excel2 Open Quantity）與庫存快照（Excel3 Unrestricted），將母材料需求以 **1:1** 展開至子材料，再依生產日優先序對子料庫存做**貪婪配發**，輸出可比對「需求 vs 能提供」與「扣減後剩餘」的結果表。

### English

Using schedule (Excel1), demand (Excel2 Open Quantity), and stock snapshot (Excel3 Unrestricted), expand each mother demand to children at **1:1**, then **greedily allocate** child stock by production-date priority. Export a result table that compares demand vs provided and shows remaining stock after each row.

---

## 輸入對應（固定欄位）/ Fixed column mapping

| 來源 / Source | 欄位 / Column | 語意 / Meaning |
|---|---|---|
| Excel1 | A `so` | 訂單鍵 / Sales order key |
| Excel1 | B `cutting` | 排程生產日 / Production (cutting) date |
| Excel2 | B `SD Document` | 訂單鍵（對應 Excel1.A）/ SO key |
| Excel2 | F `Material` | 母材料 / Mother material |
| Excel2 | Q `Open Quantity` | **需求數量**（加總）/ **Demand qty** (summed) |
| Excel2 | R `Base Unit of Measure` | 母單位（事前檢查＋換算）/ Mother unit |
| Excel3 | E `Material` | 母材料 / Mother material |
| Excel3 | F `Material Full Description(EN)` | 母料全名；SHT 末碼來源 / Mother full name; SHT size-suffix source |
| Excel3 | H `OUn` | 母單位事前檢查（須等於 2.R）/ Mother unit pre-check |
| Excel3 | I `Article(Com.)` | 子材料 / Child material |
| Excel3 | M `BUn` | 子單位（換算）/ Child unit for conversion |
| Excel3 | K `Unrestricted` | 庫存快照欄；同子料取 **MAX(K)** / Stock snapshot; **MAX(K)** per child |

### v2.1 / v2.2 單位規則 / Unit rules

1. **事前檢查**：同母料（2.F=3.E）時 **2.R 必須等於 3.H**；否則彈錯誤並停止。  
2. **換算**：比較 **2.R vs 3.M**。相同 → Demand **1:1**。  
3. **母單位為 SHT**（且子單位不同）：自 Excel3.**F** 母料全名擷取末碼（如 `110x200cm`），查可編輯「SHT 末碼換算」表（預設種子可改；使用者自行新增／改倍率／刪除，存 localStorage；引擎不寫死倍率）。缺末碼或缺規則 → 停止。`Y` 與 `YD` 視為同一子單位鍵。同母若 F 末碼不一致 → 停止。  
4. **其他單位對**：查單位白名單（預設 M→YD=1.0936、YD→M=0.9144）；缺規則 → 停止。  
5. **輸出 10 欄**：cutting, so, mother, mother unit, child, child unit, demand, provided, remaining, Y（同 SO+母料群組：全部子料 demand>0 且 provided≥demand 才標 Y）。  
6. **UI**：頂部可篩 SO／cutting／母料；可勾選隱藏零需求；預覽 SO 灰白斑馬；末碼下拉 = 檔案偵測 ∪ 既有規則 ∪ 自訂。

**重要說明 / Important notes**

1. Excel2 需求量使用 **Q = Open Quantity**，不是其他數量欄。  
   Excel2 demand uses **Q = Open Quantity**, not another quantity column.
2. Excel3 的 K 為倉儲快照，同一子料可能在多列重複出現；初始庫存 = 該子料所有列的 **MAX(K)**，不是 SUM。  
   Excel3 column K is a warehouse snapshot repeated across rows; initial stock = **MAX(K)** for that child, not SUM.
3. 僅保留「母料存在於 Excel3 欄 E」的需求列。  
   Keep only demand rows whose mother exists in Excel3 column E.

---

## 演算法步驟 / Algorithm steps

### 1. Excel1：SO → 最早 cutting

- 對每個 `so`，若有多筆，取 **最早** `cutting`。  
- For each `so`, if duplicates exist, keep the **earliest** `cutting`.

### 2. Excel2：依 (SO, mother) 加總 Q

- `demand[(so, mother)] = SUM(Open Quantity Q)`。  
- 丟棄 mother 不在 Excel3.E 中的鍵。  
- Drop keys whose mother is not present in Excel3.E.

### 3. Excel3：母→子與初始庫存

- 對每個 mother：收集 **distinct** children（欄 I）。  
- 對每個 child：`stock[child] = MAX(K Unrestricted)`。  
- For each mother: collect **distinct** children (column I).  
- For each child: `stock[child] = MAX(K Unrestricted)`.

### 4. 展開（母：子 = 1:1）

- 每個 `(so, mother)` 需求 Q，對該母下每個 child 產生一列，且 **child need = Q**（1:1）。  
- For each `(so, mother)` demand Q, emit one row per child under that mother with **child need = Q** (1:1).

### 5. 排序

輸出列排序鍵（皆升序）：

1. `cutting` ASC  
2. `so` ASC  
3. `mother` ASC  
4. `child` ASC  

### 6. 貪婪配發（依子料由上而下）

對每個 child：

- `remaining[child]` 初始 = `MAX(K)`  
- 對排序後的每一列：  
  - `provide = min(need, remaining)`  
  - `remaining -= provide`  
- 第 9 欄（I）寫入該列配發後的 `remaining`（同 child 由上往下遞減；最後一列 = 最終未派發庫存）。  
- Column I writes post-allocate `remaining` (decreases top-to-bottom per child; last row = final unallocated).

### 7. 輸出欄位順序（鎖定 v2.1）/ Locked output columns (v2.1)

| 序 / # | 欄位 / Column | 來源 / Source |
|---|---|---|
| 1 | cutting | Excel1.B |
| 2 | so | Excel1.A |
| 3 | mother material | Excel2.F |
| 4 | mother unit (2.R) | Excel2.R |
| 5 | child material | Excel3.I |
| 6 | child unit (3.M) | Excel3.M |
| 7 | demand qty | 換算後子料需求 / converted child demand |
| 8 | provided qty | `min(demand, remaining)` |
| 9 | remaining stock after this row | 扣減後剩餘 / post-allocate remaining |
| 10 | allocated (Y) | 同 SO+母料：全部子料 demand>0 且 provided≥demand → `Y` |

比對方式：同一列若第 7 欄 == 第 8 欄 → 該子料需求配平；第 8 < 第 7 → 短缺。  
Compare: on the same row, col7 == col8 means demand met; col8 < col7 means shortage.

---

## 與舊 VLOOKUP 的關係 / Relation to legacy VLOOKUP

| 項目 / Item | 舊產品 / Legacy | 新產品 / v2 |
|---|---|---|
| 入口 / Entry | `vlookup-web.html` | `allocation-web.html` |
| 方向 / Direction | 兩段查找合併欄位 | 庫存配發引擎 |
| 狀態 / Status | **Deprecated**（僅供歷史對照） | **Current product** |
| 業務核准 / Approval | 未核准為最終產品 | 本規格規則已鎖定 |

---

## 資料邊界 / Data boundary

真實業務檔 `1.xlsx` / `2.xlsx` / `3.xlsx` **不得**提交至 git 或寫入 handoff。測試僅使用去識別 fixture；本機真實檔僅可印出彙總計數（列數、匹配數），不得貼出真實料號／SO 樣本。

Real business workbooks must **not** be committed or pasted into handoffs. Tests use sanitized fixtures only; local real-file checks may print aggregate counts only (row/match counts), never real material codes or SO samples.

---

## 驗收要點 / Acceptance points

1. MAX(K) 初始化正確（非 SUM）。  
2. 貪婪扣減：`provide = min(need, remaining)`，剩餘遞減。  
3. 一母多子：1:1 展開。  
4. 短缺案例：`provide < demand`。  
5. 輸出欄序固定為上表 7 欄。  
6. cutting 顯示為可讀日期（非裸 Excel serial）。  
7. CSV：UTF-8 BOM + 公式中和；XLSX：離線 store-method OOXML（無 CDN）。
