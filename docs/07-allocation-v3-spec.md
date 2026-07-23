# 07 — RAW MAT 庫存配發引擎規格（v3）

> 本文件為 **v3** 已確認業務規則。實作入口：`allocation-web.html`（`APP_VERSION` 3.1.3）。  
> 欄位對應一律使用**英文欄位名稱**，禁止寫死 Excel 欄位字母（A/B/C）。

**狀態 / Status：** CONFIRMED（2026-07-22）  
**資料樣本 / Sample folder：** `New_0722/`

---

## 1. 輸入四報表

| 槽位 | 典型檔名 | 角色 |
|------|----------|------|
| Schedule | `1.xlsx` | 訂單 + cutting；同 SO 取最早 cutting |
| Demand (COOIS) | `COOIS.xlsx` | 訂單材料需求 |
| BOM / 廠外 (ZRMM0028) | `0028.xlsx` | 母子合貼、廠外庫存、展開關係 |
| Stock (MB52) | `MB52_new.xlsx` | 全材料廠內庫存 |

### 雙表頭

`COOIS` / `ZRMM0028`：第 1 列中文、第 2 列英文、第 3 列起為資料。  
解析時偵測英文表頭列（含 `SD Document`、`Article(Com.)`、`Open Quantity` 等）並以其為 header。

### 欄位契約（英文名；可含常見 alias）

**Schedule**
- Order / `訂單編號` / `Order NO` / `so` → SO
- cutting / `cutting process` → cutting 日期

**COOIS**
- `SD Document` → SO（必須存在於 Schedule）
- `Material` → 需求料號
- `Open Quantity` → 需求量（**不是** Quantity withdrawn）
- `Requirement Segment` → `FLT` / `MTF`
- `Base Unit of Measure` → 需求側單位

**ZRMM0028**
- `Material` → 母料
- `Article(Com.)` → 子料
- `GI SC(541/542)` → 發料 J
- `Stock of Vendor` → 廠商庫存 L
- `GR SC(543/544)` → 領料 P
- `Storage Location`（第一個同名欄）→ 儲位；`39*` 開頭整列排除
- `Batch` → FLT/MTF（須與需求 Segment 一致）
- `OUn` / `BUn` → 母／子單位
- `Material Full Description(CN)`（或 EN）→ SHT 末碼來源

**MB52**
- `Material` → 料號
- `Stock Segment` → FLT/MTF
- `Storage Location` → `39*` 排除
- `Unrestricted` → 廠內庫存；同 Material+Segment 多列 **SUM**
- `Base Unit of Measure` → 庫存單位（可選對帳）

---

## 2. 過濾

1. ZRMM0028：**廠外庫存加總**：`J == 0` **或** `L == 0` → 該列**不計入** outside（仍可當母子合貼）  
2. ZRMM0028：`Storage Location` 以 `39` 開頭 → 丟棄（BOM 與廠外皆不計）  
3. MB52：`Storage Location` 以 `39` 開頭 → 丟棄  
4. COOIS：SO 不在 Schedule → 不參與  
5. COOIS 直接需求：料號必須存在於 ZRMM0028 **子料 Article**（通過儲位過濾後的母子列）；不在 0028.F 的料（如 HC／HU 開頭且未當子料）→ **不計算**  
6. Segment 鎖定（**不可混倉**）：同一材料的庫存／廠外／BOM／需求加總與扣減，必須 `COOIS.Requirement Segment` = `MB52.Stock Segment` = `ZRMM0028.Batch`（一律正規化大寫）。**FLT 與 MTF 分池，不可互相加總或配發**；空白 Segment 不與 FLT/MTF 混配。

> **母子合貼展開**：同一母料 + Batch（Segment）下出現的所有子料 `Article` 皆須展開（含 MH04），**不因**該列 `J=0` 或 `L=0` 而省略。  
> 例：`MN010011097` 在 MTF 下 `MH040007537` 的 Vendor Stock L 全為 0 → 過去會漏展開；現在 MTF 訂單仍應展開 MH04 + MP19。

> 注意：子料 `Article` 以 **MH04** 開頭者仍進 BOM／需求與輸出列；僅 **Y（待配發／配套）** 判定時略過 MH04（見 §6）。

比對順序：先以 0028 有效子料為準 → 再回 COOIS 取 Open Quantity（母料僅做展開至其子料）。

---

## 3. 廠外庫存（輸入規則；目前不輸出）

對每個 `(mother Material, child Article, Batch seg)`（僅計入通過 J≠0 且 L≠0 的列）：

```text
outside(mother, child, seg) = max(0, SUM(J) - SUM(P))
```

廠外**不扣減**可配發池，且 **v3.1.3+ 不再輸出**母／子廠外或母材料廠內顯示欄。

---

## 4. 廠內可配發池

```text
pool(X, seg) = SUM(MB52.Unrestricted where Material=X, Stock Segment=seg, Storage Location not 39*)
```

**不減** 子料廠外。

輸出列上：
- **子材料庫存** = 該子料配發前剩餘廠內（起始 MB52，先前列 `provided` 已扣）  
- **可配發庫存** = 該子料配發前剩餘池（起始 = MB52，先前列已扣）  
- **扣減後剩餘** = 本列配發後的可配發池  

---

## 5. 需求展開（方案 A + 直接加成）

對每個 Schedule SO（依 cutting 早→晚），按 Segment 分開：

1. **母料展開**：COOIS 列 `Material=M` 且 M 在 ZRMM0028 為母料（且該 Batch=Segment 下有子料）→ 對該母下**每一個子料** F：  
   `need(F) += OpenQuantity(M) * conversion(OUn_M, BUn_F, sizeSuffix_M)`  
2. **直接加成**：COOIS 列 `Material=X`：  
   - 若 X 在本 SO+Segment **已成功當母展開** → **不再**對 X 本身建立直接需求列（避免母料庫存再扣一次）  
   - 若 X 已是某母展開出的子料 → `need(X)` 的直接量併入該展開列（`demand direct`）  
   - 否則 → `need(X) += OpenQuantity(X)`（母欄空白）  
3. 同 SO 母+子都出現 = **展開用量 + 子料自身 Open Quantity 兩筆都扣**  
4. 料號在 0028 只當子、COOIS 只有直接需求 → 只扣直接 R（無「當母再扣」）

單位換算：**同 v2**（相同單位 1:1；SHT 末碼表；M↔YD 白名單；缺規則阻擋）。

---

## 6. 配發

- 排序：cutting ASC → SO → **有母料號（C 欄非空）優先** → mother → child → segment  
  （同訂單內：展開／有母列在上，僅直接需求、母欄空白列在下；預覽與匯出 Excel 同序）
- 結果列：含 demand=0（COOIS Open Quantity 為 0 等）；Step 3「隱藏需求=0／整張 SO 需求皆 0」**預設勾選**，取消勾選才會出現在預覽／匯出。
- 列粒度：SO × 母料 × 子料 × Segment  

### Y 標記（配套；略過 MH04）

同 `(SO + 母料 + Segment)` 群組：僅檢查**非 MH04** 且 `demand qty > 0` 的子料列是否皆 `provided ≥ demand` → 全組標 `Y`，否則空白。  
**MH04*** 子料仍出現在輸出／可配發，但**不參與配套判定**（不論其是否有庫存）。  

例：母料 `MN050022618` 下有 `MH040001138`、`MPO80002175`、`MP190000407` → 只要後兩者（非 MH04）皆齊套，整組（含 MH04 列）標 `Y`。

無母料（僅直接需求）時：群組鍵用 `(SO + "" + Segment + child)`；若該列為 MH04，因無其他非 MH04 需求列可檢查 → 不標 `Y`（`toCheck` 為空）。

---

## 7. 輸出 16 欄

| # | 英文表頭 | 中文辨識 |
|---|----------|----------|
| 1 | cutting | 生產日 cutting |
| 2 | so | 訂單 SO |
| 3 | mother material | 母材料 |
| 4 | mother batch | 母材料 BATCH |
| 5 | mother unit | 母單位 |
| 6 | child material | 子材料 |
| 7 | child batch | 子材料 BATCH |
| 8 | child unit | 子單位 |
| 9 | child demand | 子材料需求（母料展開） |
| 10 | demand direct | 子料直接需求 |
| 11 | demand qty | 需求合計 |
| 12 | child stock | 子材料庫存（本列配發前剩餘廠內；依序遞減） |
| 13 | stock available | 可配發庫存（= 廠內剩餘池；依序遞減） |
| 14 | provided qty | 能提供數量 |
| 15 | remaining stock after this row | 扣減後剩餘（可配發池） |
| 16 | pending allocation (Y) | 待配發（Y） |

（已移除：母材料廠內／廠外庫存、子材料廠外庫存顯示欄。）

---

## 8. 與 v2 差異摘要

| 項目 | v2 | v3 |
|------|----|----|
| 輸入 | Excel1/2/3 | Schedule + COOIS + ZRMM0028 + MB52 |
| 欄位定位 | 固定字母索引 | 英文表頭名 |
| 庫存 | Excel3 Unrestricted MAX | MB52 SUM（配發不扣廠外） |
| 廠外 | 無 | max(0, ΣJ−ΣP) |
| 需求 | 僅母料展開 | 展開 + COOIS 直接加成 |
| Segment | 無 | FLT/MTF 鎖定 |
| 顯示 | — | 雙重身分料號（ZRMM 中既為母又為子）於結果表母／子欄以**藍色**標示（網頁預覽＋匯出 Excel） |
