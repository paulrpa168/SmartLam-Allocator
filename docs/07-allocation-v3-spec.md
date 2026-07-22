# 07 — RAW MAT 庫存配發引擎規格（v3）

> 本文件為 **v3** 已確認業務規則。實作入口：`allocation-web.html`（`APP_VERSION` 3.0.0+）。  
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

1. ZRMM0028：`J == 0` **或** `L == 0` → 丟棄  
2. ZRMM0028：`Storage Location` 以 `39` 開頭 → 丟棄  
3. ZRMM0028：子料 `Article`（F）以 **`MH04`** 開頭 → 丟棄（不進 BOM／廠外／需求）  
4. MB52：`Storage Location` 以 `39` 開頭 → 丟棄  
5. COOIS：SO 不在 Schedule → 不參與  
6. COOIS 直接需求：料號必須存在於 ZRMM0028 **子料 Article**（通過上述過濾後）；不在 0028.F 的料（如 HC／HU 開頭且未當子料）→ **不計算**  
7. Segment 鎖定（**不可混倉**）：同一材料的庫存／廠外／BOM／需求加總與扣減，必須 `COOIS.Requirement Segment` = `MB52.Stock Segment` = `ZRMM0028.Batch`（一律正規化大寫）。**FLT 與 MTF 分池，不可互相加總或配發**；空白 Segment 不與 FLT/MTF 混配。

比對順序：先以 0028 有效子料為準 → 再回 COOIS 取 Open Quantity（母料僅做展開至其子料）。

---

## 3. 廠外庫存

對每個 `(mother Material, child Article, Batch seg)`：

```text
outside(mother, child, seg) = max(0, SUM(J) - SUM(P))
```

子料 `X` 的廠外占用：加總所有母料下 `outside(*, X, seg)`。

---

## 4. 廠內可配發池

```text
pool(X, seg) = SUM(MB52.Unrestricted where Material=X, Stock Segment=seg, Storage Location not 39*)
             - outside_total(X, seg)
```

若 `MB52 − outside < 0`，**可配發庫存與配發池皆 clamp 為 0**（報表不顯示負數；廠內／廠外原值仍保留供追查）。

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

### Y 標記（保留 v2 精神）

同 `(SO + 母料 + Segment)` 群組：全部子料列 `demand qty > 0` 且 `provided ≥ demand` → `Y`，否則空白。  
無母料（僅直接需求）時，群組鍵用 `(SO + "" + Segment + child)` 或僅對有母料的列套用 Y——實作：無母料列各自成組（單列滿足則 Y）。

---

## 7. 輸出 17 欄

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
| 9 | demand from mother | 母料展開需求 |
| 10 | demand direct | 子料直接需求 |
| 11 | demand qty | 需求合計 |
| 12 | stock MB52 | 廠內庫存 MB52 |
| 13 | stock outside | 廠外庫存 |
| 14 | stock available | 可配發庫存 |
| 15 | provided qty | 能提供數量 |
| 16 | remaining stock after this row | 扣減後剩餘 |
| 17 | allocated (Y) | 已配發（Y） |

---

## 8. 與 v2 差異摘要

| 項目 | v2 | v3 |
|------|----|----|
| 輸入 | Excel1/2/3 | Schedule + COOIS + ZRMM0028 + MB52 |
| 欄位定位 | 固定字母索引 | 英文表頭名 |
| 庫存 | Excel3 Unrestricted MAX | MB52 SUM − 廠外 |
| 廠外 | 無 | max(0, ΣJ−ΣP) |
| 需求 | 僅母料展開 | 展開 + COOIS 直接加成 |
| Segment | 無 | FLT/MTF 鎖定 |
| 顯示 | — | 雙重身分料號（ZRMM 中既為母又為子）於結果表母／子欄以**藍色**標示（網頁預覽＋匯出 Excel） |
